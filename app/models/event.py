from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

class MeetingEvent(Base):
    meeting_id: Mapped[int] = mapped_column(ForeignKey("meeting.id", ondelete="CASCADE"), index=True)
    author: Mapped[Optional[str]] = mapped_column(default=None)
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    meeting: Mapped["Meeting"] = relationship(back_populates="events")
