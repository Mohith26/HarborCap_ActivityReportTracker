import uuid
import json
from datetime import datetime, date, timezone
from decimal import Decimal

from sqlalchemy import String, Integer, Date, DateTime, Numeric, Text, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class PropertyMetric(Base):
    __tablename__ = "property_metrics"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    property_id: Mapped[str] = mapped_column(String(36), ForeignKey("properties.id", ondelete="CASCADE"), nullable=False, index=True)
    report_id: Mapped[str] = mapped_column(String(36), ForeignKey("activity_reports.id", ondelete="CASCADE"), nullable=False)

    report_date: Mapped[date | None] = mapped_column(Date, index=True)
    total_property_sf: Mapped[int | None] = mapped_column(Integer)
    vacant_sf: Mapped[int | None] = mapped_column(Integer)
    vacancy_pct: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    occupancy_pct: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    shadow_vacancy_sf: Mapped[int | None] = mapped_column(Integer)

    inquiries_sent: Mapped[int | None] = mapped_column(Integer)
    tours_conducted: Mapped[int | None] = mapped_column(Integer)
    proposals_sent: Mapped[int | None] = mapped_column(Integer)

    quoted_rate_psf: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    additional_metrics: Mapped[dict | None] = mapped_column(JSON)

    snapshot_date: Mapped[date | None] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    property = relationship("Property", back_populates="metrics")
    report = relationship("ActivityReport", back_populates="metrics")
