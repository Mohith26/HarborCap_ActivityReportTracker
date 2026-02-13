from datetime import datetime, date
from decimal import Decimal

from pydantic import BaseModel


class AvailabilityResponse(BaseModel):
    id: str
    property_id: str
    building: str | None
    total_size_sf: int | None
    status: str | None
    office_sf: int | None
    lease_rate_psf: Decimal | None
    opex: Decimal | None
    sale_price_psf: Decimal | None
    power_amps: int | None
    loading_doors: str | None
    eave_height: str | None
    crane_ready: str | None
    land_acreage: Decimal | None
    additional_info: str | None
    snapshot_date: date | None
    created_at: datetime

    model_config = {"from_attributes": True}
