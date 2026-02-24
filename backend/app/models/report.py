import uuid
from datetime import datetime, date, timezone

from sqlalchemy import String, Integer, Text, Date, DateTime, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ActivityReport(Base):
    __tablename__ = "activity_reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    property_id: Mapped[str] = mapped_column(String(36), ForeignKey("properties.id", ondelete="CASCADE"), nullable=False, index=True)
    file_name: Mapped[str] = mapped_column(String(500), nullable=False)
    file_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    file_type: Mapped[str] = mapped_column(String(10), nullable=False)
    file_size_bytes: Mapped[int | None] = mapped_column(Integer)
    report_date: Mapped[date | None] = mapped_column(Date, index=True)
    sheet_names: Mapped[dict | None] = mapped_column(JSON)
    extraction_status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    extraction_errors: Mapped[dict | None] = mapped_column(JSON)
    raw_extraction: Mapped[dict | None] = mapped_column(JSON)
    uploaded_by: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    property = relationship("Property", back_populates="reports")
    deals = relationship("Deal", back_populates="report", cascade="all, delete-orphan")
    availabilities = relationship("PropertyAvailability", back_populates="report", cascade="all, delete-orphan")
    metrics = relationship("PropertyMetric", back_populates="report", cascade="all, delete-orphan")
