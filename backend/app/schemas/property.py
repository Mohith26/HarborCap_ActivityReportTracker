from datetime import datetime

from pydantic import BaseModel


class PropertyCreate(BaseModel):
    name: str
    address: str | None = None
    city: str | None = None
    state: str | None = None
    property_type: str | None = None
    total_sf: int | None = None
    num_buildings: int | None = None
    description: str | None = None


class PropertyUpdate(BaseModel):
    name: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    property_type: str | None = None
    total_sf: int | None = None
    num_buildings: int | None = None
    description: str | None = None


class PropertyResponse(BaseModel):
    id: str
    name: str
    address: str | None
    city: str | None
    state: str | None
    property_type: str | None
    total_sf: int | None
    num_buildings: int | None
    description: str | None
    created_by: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PropertyListItem(PropertyResponse):
    report_count: int = 0
    active_deal_count: int = 0
    last_report_date: str | None = None
