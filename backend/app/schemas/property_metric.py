from datetime import datetime, date
from decimal import Decimal

from pydantic import BaseModel


class PropertyMetricResponse(BaseModel):
    id: str
    property_id: str
    report_date: date | None
    total_property_sf: int | None
    vacant_sf: int | None
    vacancy_pct: Decimal | None
    occupancy_pct: Decimal | None
    shadow_vacancy_sf: int | None
    inquiries_sent: int | None
    tours_conducted: int | None
    proposals_sent: int | None
    quoted_rate_psf: Decimal | None
    additional_metrics: dict | None
    snapshot_date: date | None
    created_at: datetime

    model_config = {"from_attributes": True}
