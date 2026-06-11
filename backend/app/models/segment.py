from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Segment(Base):
    __tablename__ = "segments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    rules: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    customer_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    ai_generated: Mapped[bool] = mapped_column(Boolean, default=False)

    campaigns: Mapped[list["Campaign"]] = relationship("Campaign", back_populates="segment", lazy="selectin")
