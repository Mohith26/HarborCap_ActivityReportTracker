from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.availability import PropertyAvailability
from app.models.report import ActivityReport
from app.schemas.availability import AvailabilityResponse

router = APIRouter()


@router.get("/properties/{property_id}/availabilities", response_model=list[AvailabilityResponse])
def list_availabilities(
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

    avails = (
        db.query(PropertyAvailability)
        .filter(PropertyAvailability.report_id == latest_report.id)
        .order_by(PropertyAvailability.building)
        .all()
    )
    return [AvailabilityResponse.model_validate(a) for a in avails]


@router.get("/properties/{property_id}/availabilities/history", response_model=list[AvailabilityResponse])
def list_availability_history(
    property_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    avails = (
        db.query(PropertyAvailability)
        .filter(PropertyAvailability.property_id == property_id)
        .order_by(PropertyAvailability.snapshot_date, PropertyAvailability.building)
        .all()
    )
    return [AvailabilityResponse.model_validate(a) for a in avails]
