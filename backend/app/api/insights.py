from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.property import Property
from app.models.insight import AIInsight
from app.schemas.insight import InsightResponse, InsightGenerateRequest

router = APIRouter()


@router.post("/properties/{property_id}/insights/generate", response_model=list[InsightResponse])
def generate_insights(
    property_id: str,
    request: InsightGenerateRequest | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    prop = db.query(Property).filter(Property.id == property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")

    from app.services.insight_service import InsightService
    service = InsightService(db)
    insight_types = request.insight_types if request and request.insight_types else None
    insights = service.generate_property_insights(property_id, insight_types=insight_types)
    return [InsightResponse.model_validate(i) for i in insights]


@router.get("/properties/{property_id}/insights", response_model=list[InsightResponse])
def list_property_insights(
    property_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    insights = (
        db.query(AIInsight)
        .filter(AIInsight.property_id == property_id)
        .order_by(AIInsight.created_at.desc())
        .all()
    )
    return [InsightResponse.model_validate(i) for i in insights]


@router.post("/insights/portfolio/generate", response_model=list[InsightResponse])
def generate_portfolio_insights(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate unprompted portfolio-level insights across all properties."""
    from app.services.portfolio_insight_service import PortfolioInsightService
    service = PortfolioInsightService(db)
    try:
        insights = service.generate_all_portfolio_insights()
    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e))
    return [InsightResponse.model_validate(i) for i in insights]


@router.get("/insights/portfolio", response_model=list[InsightResponse])
def list_portfolio_insights(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List portfolio-level insights (scope='portfolio')."""
    insights = (
        db.query(AIInsight)
        .filter(AIInsight.scope == "portfolio")
        .order_by(AIInsight.created_at.desc())
        .limit(50)
        .all()
    )
    return [InsightResponse.model_validate(i) for i in insights]


@router.get("/insights/latest", response_model=list[InsightResponse])
def list_latest_insights(
    limit: int = Query(default=10, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get the most recent insights of any scope, for the dashboard."""
    insights = (
        db.query(AIInsight)
        .order_by(AIInsight.created_at.desc())
        .limit(limit)
        .all()
    )
    return [InsightResponse.model_validate(i) for i in insights]


@router.get("/insights", response_model=list[InsightResponse])
def list_all_insights(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    insights = db.query(AIInsight).order_by(AIInsight.created_at.desc()).limit(50).all()
    return [InsightResponse.model_validate(i) for i in insights]
