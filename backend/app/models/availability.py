import uuid
from datetime import datetime, date, timezone
from decimal import Decimal

from sqlalchemy import String, Integer, Text, Date, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class PropertyAvailability(Base):
    __tablename__ = "property_availabilities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    property_id: Mapped[str] = mapped_column(String(36), ForeignKey("properties.id", ondelete="CASCADE"), nullable=False, index=True)
    report_id: Mapped[str] = mapped_column(String(36), ForeignKey("activity_reports.id", ondelete="CASCADE"), nullable=False)

    building: Mapped[str | None] = mapped_column(String(255))
    total_size_sf: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str | None] = mapped_column(String(50))
    office_sf: Mapped[int | None] = mapped_column(Integer)
    lease_rate_psf: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    opex: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    sale_price_psf: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    power_amps: Mapped[int | None] = mapped_column(Integer)
    loading_doors: Mapped[str | None] = mapped_column(String(100))
    eave_height: Mapped[str | None] = mapped_column(String(50))
    crane_ready: Mapped[str | None] = mapped_column(String(100))
    land_acreage: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    additional_info: Mapped[str | None] = mapped_column(Text)

    snapshot_date: Mapped[date | None] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    property = relationship("Property", back_populates="availabilities")
    report = relationship("ActivityReport", back_populates="availabilities")
