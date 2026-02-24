import uuid
import json
from datetime import datetime, date, timezone

from sqlalchemy import String, Text, Date, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AIInsight(Base):
    __tablename__ = "ai_insights"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    property_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("properties.id", ondelete="CASCADE"), index=True)

    insight_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    scope: Mapped[str] = mapped_column(String(20), default="property")  # "property" or "portfolio"
    severity: Mapped[str | None] = mapped_column(String(20))  # "info", "warning", "critical", "positive"
    is_auto_generated: Mapped[bool] = mapped_column(Boolean, default=False)
    tags: Mapped[dict | None] = mapped_column(JSON)

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    data_context: Mapped[dict | None] = mapped_column(JSON)
    model_used: Mapped[str | None] = mapped_column(String(100))

    report_ids_json: Mapped[str | None] = mapped_column(Text)
    date_range_start: Mapped[date | None] = mapped_column(Date)
    date_range_end: Mapped[date | None] = mapped_column(Date)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    related_property = relationship("Property", back_populates="insights")

    def get_report_ids(self) -> list[str] | None:
        if self.report_ids_json:
            return json.loads(self.report_ids_json)
        return None

    def set_report_ids(self, value: list | None):
        if value is not None:
            self.report_ids_json = json.dumps([str(v) for v in value])
        else:
            self.report_ids_json = None
