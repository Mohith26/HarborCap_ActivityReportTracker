from datetime import datetime, date

from pydantic import BaseModel


class DealResponse(BaseModel):
    id: str
    property_id: str
    report_id: str
    stage: str
    stage_numeric: int | None
    deal_type: str | None
    probability_score: int | None
    deal_priority: str | None
    tenant_name: str | None
    tenant_industry: str | None
    is_undisclosed: bool
    broker_name: str | None
    broker_firm: str | None
    broker_phone: str | None
    broker_email: str | None
    initial_inquiry: date | None
    size_min_sf: int | None
    size_max_sf: int | None
    size_raw: str | None
    commencement: str | None
    transaction_type: str | None
    comments: str | None
    last_updated: date | None
    last_updated_by: str | None
    lead_contact: str | None
    building_id: str | None
    snapshot_date: date | None
    created_at: datetime
    report_file_name: str | None = None
    report_date: date | None = None

    model_config = {"from_attributes": True}


class DealUpdate(BaseModel):
    stage: str | None = None
    stage_numeric: int | None = None
    deal_type: str | None = None
    tenant_name: str | None = None
    comments: str | None = None
    probability_score: int | None = None
    deal_priority: str | None = None


class PipelineSummary(BaseModel):
    stage: str
    stage_numeric: int
    count: int
    total_min_sf: int | None
    total_max_sf: int | None


class PortfolioPipelineSummary(BaseModel):
    property_id: str
    property_name: str
    stage_counts: dict[str, int]
    total_active_deals: int
    total_sf_in_pipeline: int | None
