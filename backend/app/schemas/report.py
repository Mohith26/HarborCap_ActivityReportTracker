from datetime import datetime, date

from pydantic import BaseModel


class ReportResponse(BaseModel):
    id: str
    property_id: str
    file_name: str
    file_type: str
    file_size_bytes: int | None
    report_date: date | None
    extraction_status: str
    extraction_errors: list | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ReportDetailResponse(ReportResponse):
    sheet_names: list | None
    raw_extraction: dict | None
    deal_count: int = 0
    availability_count: int = 0
