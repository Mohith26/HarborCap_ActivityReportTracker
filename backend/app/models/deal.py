import uuid
from datetime import datetime, date, timezone

from sqlalchemy import String, Integer, SmallInteger, Text, Date, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Deal(Base):
    __tablename__ = "deals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    property_id: Mapped[str] = mapped_column(String(36), ForeignKey("properties.id", ondelete="CASCADE"), nullable=False, index=True)
    report_id: Mapped[str] = mapped_column(String(36), ForeignKey("activity_reports.id", ondelete="CASCADE"), nullable=False, index=True)

    stage: Mapped[str] = mapped_column(String(20), nullable=False)
    stage_numeric: Mapped[int | None] = mapped_column(SmallInteger, index=True)
    deal_type: Mapped[str | None] = mapped_column(String(50))

    tenant_name: Mapped[str | None] = mapped_column(String(500), index=True)
    tenant_industry: Mapped[str | None] = mapped_column(String(500))
    is_undisclosed: Mapped[bool] = mapped_column(Boolean, default=False)

    broker_name: Mapped[str | None] = mapped_column(String(500))
    broker_firm: Mapped[str | None] = mapped_column(String(255))
    broker_phone: Mapped[str | None] = mapped_column(String(50))
    broker_email: Mapped[str | None] = mapped_column(String(255))

    initial_inquiry: Mapped[date | None] = mapped_column(Date)
    size_min_sf: Mapped[int | None] = mapped_column(Integer)
    size_max_sf: Mapped[int | None] = mapped_column(Integer)
    size_raw: Mapped[str | None] = mapped_column(String(255))
    commencement: Mapped[str | None] = mapped_column(String(255))
    transaction_type: Mapped[str | None] = mapped_column(String(20))

    comments: Mapped[str | None] = mapped_column(Text)

    last_updated: Mapped[date | None] = mapped_column(Date)
    last_updated_by: Mapped[str | None] = mapped_column(String(255))
    lead_contact: Mapped[str | None] = mapped_column(String(255))

    building_id: Mapped[str | None] = mapped_column(String(100))

    snapshot_date: Mapped[date | None] = mapped_column(Date, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    property = relationship("Property", back_populates="deals")
    report = relationship("ActivityReport", back_populates="deals")
