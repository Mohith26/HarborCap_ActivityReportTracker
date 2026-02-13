import os
import uuid as _uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import settings
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.property import Property
from app.models.report import ActivityReport
from app.models.deal import Deal
from app.models.availability import PropertyAvailability
from app.schemas.report import ReportResponse, ReportDetailResponse

router = APIRouter()


def _extract_report_date_from_filename(filename: str) -> date | None:
    """Try to parse a date from the filename."""
    import re
    # Pattern: M.D.YY or M.D.YYYY
    match = re.search(r'(\d{1,2})\.(\d{1,2})\.(\d{2,4})', filename)
    if match:
        month, day, year = int(match.group(1)), int(match.group(2)), int(match.group(3))
        if year < 100:
            year += 2000
        # Handle ambiguous cases: if first number > 12, it might be year.month.day
        if month > 12 and day <= 12:
            year_val = month + 2000 if month < 100 else month
            month, day = day, 1
            return date(year_val, month, day)
        try:
            return date(year, month, day)
        except ValueError:
            pass
    # Pattern: (M.D.YY) or (M/D/YY) in parens
    match = re.search(r'\((\d{1,2})[./](\d{1,2})[./](\d{2,4})\)', filename)
    if match:
        month, day, year = int(match.group(1)), int(match.group(2)), int(match.group(3))
        if year < 100:
            year += 2000
        try:
            return date(year, month, day)
        except ValueError:
            pass
    return None


@router.post("/properties/{property_id}/reports/upload", response_model=ReportResponse, status_code=201)
async def upload_report(
    property_id: str,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    prop = db.query(Property).filter(Property.id == property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")

    # Validate file type
    ext = file.filename.rsplit(".", 1)[-1].lower() if file.filename else ""
    if ext not in ("xlsx", "xlsm", "pdf"):
        raise HTTPException(status_code=400, detail="Unsupported file type. Upload .xlsx, .xlsm, or .pdf files.")

    # Save file
    upload_dir = os.path.join(settings.UPLOAD_DIR, str(property_id))
    os.makedirs(upload_dir, exist_ok=True)
    file_id = _uuid.uuid4()
    file_path = os.path.join(upload_dir, f"{file_id}.{ext}")

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    # Extract report date from filename
    report_date = _extract_report_date_from_filename(file.filename or "")

    report = ActivityReport(
        property_id=property_id,
        file_name=file.filename or "unknown",
        file_path=file_path,
        file_type=ext,
        file_size_bytes=len(content),
        report_date=report_date,
        extraction_status="pending",
        uploaded_by=current_user.id,
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    # Trigger background extraction
    from app.services.extraction_service import process_report
    background_tasks.add_task(process_report, str(report.id))

    return ReportResponse.model_validate(report)


@router.get("/properties/{property_id}/reports", response_model=list[ReportResponse])
def list_reports(
    property_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    reports = (
        db.query(ActivityReport)
        .filter(ActivityReport.property_id == property_id)
        .order_by(ActivityReport.created_at.desc())
        .all()
    )
    return [ReportResponse.model_validate(r) for r in reports]


@router.get("/reports/{report_id}", response_model=ReportDetailResponse)
def get_report(
    report_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = db.query(ActivityReport).filter(ActivityReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    deal_count = db.query(func.count(Deal.id)).filter(Deal.report_id == report_id).scalar()
    avail_count = db.query(func.count(PropertyAvailability.id)).filter(PropertyAvailability.report_id == report_id).scalar()

    resp = ReportDetailResponse(
        **ReportResponse.model_validate(report).model_dump(),
        sheet_names=report.sheet_names,
        raw_extraction=report.raw_extraction,
        deal_count=deal_count or 0,
        availability_count=avail_count or 0,
    )
    return resp


@router.post("/reports/{report_id}/reprocess", response_model=ReportResponse)
async def reprocess_report(
    report_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = db.query(ActivityReport).filter(ActivityReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    # Delete existing extracted data
    db.query(Deal).filter(Deal.report_id == report_id).delete()
    db.query(PropertyAvailability).filter(PropertyAvailability.report_id == report_id).delete()

    report.extraction_status = "pending"
    report.extraction_errors = None
    report.raw_extraction = None
    db.commit()
    db.refresh(report)

    from app.services.extraction_service import process_report
    background_tasks.add_task(process_report, str(report.id))

    return ReportResponse.model_validate(report)


@router.delete("/reports/{report_id}", status_code=204)
def delete_report(
    report_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = db.query(ActivityReport).filter(ActivityReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    # Delete the file
    if os.path.exists(report.file_path):
        os.remove(report.file_path)

    db.delete(report)
    db.commit()
