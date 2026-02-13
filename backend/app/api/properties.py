from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.property import Property
from app.models.report import ActivityReport
from app.models.deal import Deal
from app.schemas.property import PropertyCreate, PropertyUpdate, PropertyResponse, PropertyListItem

router = APIRouter()


@router.get("/", response_model=list[PropertyListItem])
def list_properties(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    properties = db.query(Property).order_by(Property.updated_at.desc()).all()
    result = []
    for prop in properties:
        report_count = db.query(func.count(ActivityReport.id)).filter(ActivityReport.property_id == prop.id).scalar()
        active_deal_count = db.query(func.count(Deal.id)).filter(
            Deal.property_id == prop.id,
            Deal.stage_numeric.in_([1, 2, 3, 4]),
        ).scalar()
        last_report = (
            db.query(ActivityReport.report_date)
            .filter(ActivityReport.property_id == prop.id)
            .order_by(ActivityReport.report_date.desc())
            .first()
        )
        item = PropertyListItem(
            **PropertyResponse.model_validate(prop).model_dump(),
            report_count=report_count or 0,
            active_deal_count=active_deal_count or 0,
            last_report_date=str(last_report[0]) if last_report and last_report[0] else None,
        )
        result.append(item)
    return result


@router.post("/", response_model=PropertyResponse, status_code=201)
def create_property(
    data: PropertyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    prop = Property(**data.model_dump(), created_by=current_user.id)
    db.add(prop)
    db.commit()
    db.refresh(prop)
    return PropertyResponse.model_validate(prop)


@router.get("/{property_id}", response_model=PropertyResponse)
def get_property(
    property_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    prop = db.query(Property).filter(Property.id == property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    return PropertyResponse.model_validate(prop)


@router.put("/{property_id}", response_model=PropertyResponse)
def update_property(
    property_id: str,
    data: PropertyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    prop = db.query(Property).filter(Property.id == property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(prop, key, value)

    db.commit()
    db.refresh(prop)
    return PropertyResponse.model_validate(prop)


@router.delete("/{property_id}", status_code=204)
def delete_property(
    property_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    prop = db.query(Property).filter(Property.id == property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    db.delete(prop)
    db.commit()


@router.get("/{property_id}/summary")
def get_property_summary(
    property_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    prop = db.query(Property).filter(Property.id == property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")

    # Get latest report
    latest_report = (
        db.query(ActivityReport)
        .filter(ActivityReport.property_id == property_id, ActivityReport.extraction_status == "completed")
        .order_by(ActivityReport.report_date.desc())
        .first()
    )

    # Deal counts by stage from latest report
    stage_counts = {}
    if latest_report:
        rows = (
            db.query(Deal.stage, Deal.stage_numeric, func.count(Deal.id))
            .filter(Deal.report_id == latest_report.id)
            .group_by(Deal.stage, Deal.stage_numeric)
            .all()
        )
        stage_counts = {row[0]: {"count": row[2], "stage_numeric": row[1]} for row in rows}

    total_reports = db.query(func.count(ActivityReport.id)).filter(ActivityReport.property_id == property_id).scalar()

    return {
        "property": PropertyResponse.model_validate(prop),
        "total_reports": total_reports,
        "latest_report_date": str(latest_report.report_date) if latest_report and latest_report.report_date else None,
        "deal_pipeline": stage_counts,
    }
