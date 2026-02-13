from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.deal import Deal
from app.models.report import ActivityReport
from app.schemas.deal import DealResponse, DealUpdate, PipelineSummary

router = APIRouter()


@router.get("/properties/{property_id}/deals", response_model=list[DealResponse])
def list_deals(
    property_id: str,
    stage: str | None = None,
    deal_type: str | None = None,
    snapshot: str | None = Query(None, description="Filter by snapshot date or 'latest'"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Deal).filter(Deal.property_id == property_id)

    if snapshot == "latest" or snapshot is None:
        # Get deals from the latest report
        latest_report = (
            db.query(ActivityReport)
            .filter(ActivityReport.property_id == property_id, ActivityReport.extraction_status == "completed")
            .order_by(ActivityReport.report_date.desc())
            .first()
        )
        if latest_report:
            query = query.filter(Deal.report_id == latest_report.id)
        else:
            return []
    elif snapshot:
        query = query.filter(Deal.snapshot_date == snapshot)

    if stage:
        query = query.filter(Deal.stage == stage)
    if deal_type:
        query = query.filter(Deal.deal_type == deal_type)

    deals = query.order_by(Deal.stage_numeric, Deal.tenant_name).all()
    return [DealResponse.model_validate(d) for d in deals]


@router.get("/properties/{property_id}/deals/pipeline", response_model=list[PipelineSummary])
def get_pipeline(
    property_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    latest_report = (
        db.query(ActivityReport)
        .filter(ActivityReport.property_id == property_id, ActivityReport.extraction_status == "completed")
        .order_by(ActivityReport.report_date.desc())
        .first()
    )
    if not latest_report:
        return []

    rows = (
        db.query(
            Deal.stage,
            Deal.stage_numeric,
            func.count(Deal.id),
            func.sum(Deal.size_min_sf),
            func.sum(Deal.size_max_sf),
        )
        .filter(Deal.report_id == latest_report.id)
        .group_by(Deal.stage, Deal.stage_numeric)
        .order_by(Deal.stage_numeric)
        .all()
    )
    return [
        PipelineSummary(
            stage=row[0],
            stage_numeric=row[1] or 0,
            count=row[2],
            total_min_sf=row[3],
            total_max_sf=row[4],
        )
        for row in rows
    ]


@router.get("/properties/{property_id}/deals/history/{tenant_name}", response_model=list[DealResponse])
def get_deal_history(
    property_id: str,
    tenant_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    deals = (
        db.query(Deal)
        .filter(Deal.property_id == property_id, Deal.tenant_name.ilike(f"%{tenant_name}%"))
        .order_by(Deal.snapshot_date)
        .all()
    )
    return [DealResponse.model_validate(d) for d in deals]


@router.get("/deals/{deal_id}", response_model=DealResponse)
def get_deal(
    deal_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    return DealResponse.model_validate(deal)


@router.put("/deals/{deal_id}", response_model=DealResponse)
def update_deal(
    deal_id: str,
    data: DealUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(deal, key, value)

    db.commit()
    db.refresh(deal)
    return DealResponse.model_validate(deal)
