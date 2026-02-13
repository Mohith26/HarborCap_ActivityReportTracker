import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Property(Base):
    __tablename__ = "properties"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str | None] = mapped_column(Text)
    city: Mapped[str | None] = mapped_column(String(100))
    state: Mapped[str | None] = mapped_column(String(50))
    property_type: Mapped[str | None] = mapped_column(String(50))
    total_sf: Mapped[int | None] = mapped_column(Integer)
    num_buildings: Mapped[int | None] = mapped_column(Integer)
    description: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    reports = relationship("ActivityReport", back_populates="property", cascade="all, delete-orphan")
    deals = relationship("Deal", back_populates="property", cascade="all, delete-orphan")
    availabilities = relationship("PropertyAvailability", back_populates="property", cascade="all, delete-orphan")
    metrics = relationship("PropertyMetric", back_populates="property", cascade="all, delete-orphan")
    insights = relationship("AIInsight", back_populates="related_property", cascade="all, delete-orphan")
