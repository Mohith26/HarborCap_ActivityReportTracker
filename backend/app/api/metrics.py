from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.property_metric import PropertyMetric
from app.schemas.property_metric import PropertyMetricResponse

router = APIRouter()


@router.get("/properties/{property_id}/metrics", response_model=list[PropertyMetricResponse])
def list_metrics(
    property_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    metrics = (
        db.query(PropertyMetric)
        .filter(PropertyMetric.property_id == property_id)
        .order_by(PropertyMetric.report_date.desc())
        .all()
    )
    return [PropertyMetricResponse.model_validate(m) for m in metrics]
