from datetime import datetime, date

from pydantic import BaseModel


class InsightResponse(BaseModel):
    id: str
    property_id: str | None
    insight_type: str
    title: str
    content: str
    model_used: str | None
    date_range_start: date | None
    date_range_end: date | None
    created_at: datetime

    model_config = {"from_attributes": True}


class InsightGenerateRequest(BaseModel):
    insight_types: list[str] | None = None
