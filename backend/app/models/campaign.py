from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Campaign(Base):
    __tablename__ = "campaigns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    segment_id: Mapped[int] = mapped_column(Integer, ForeignKey("segments.id"), nullable=False, index=True)
    channel: Mapped[str] = mapped_column(String(50), nullable=False)
    message_template: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="draft")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    launched_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    segment: Mapped["Segment"] = relationship("Segment", back_populates="campaigns", lazy="selectin")
    communication_logs: Mapped[list["CommunicationLog"]] = relationship(
        "CommunicationLog", back_populates="campaign", lazy="selectin"
    )
