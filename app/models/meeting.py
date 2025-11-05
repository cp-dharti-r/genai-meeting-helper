from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import String, Text, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

class MeetingStatus:
    SCHEDULED = "scheduled"
    LIVE = "live"
    ENDED = "ended"

class Meeting(Base):
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text, default=None)
    scheduled_start: Mapped[Optional[datetime]] = mapped_column(default=None)
    scheduled_end: Mapped[Optional[datetime]] = mapped_column(default=None)
    actual_start: Mapped[Optional[datetime]] = mapped_column(default=None)
    actual_end: Mapped[Optional[datetime]] = mapped_column(default=None)
    status: Mapped[str] = mapped_column(String(32), default=MeetingStatus.SCHEDULED, index=True)

    participants: Mapped[List["Participant"]] = relationship(back_populates="meeting", cascade="all, delete-orphan")
    summaries: Mapped[List["MeetingSummary"]] = relationship(back_populates="meeting", cascade="all, delete-orphan")
    events: Mapped[List["MeetingEvent"]] = relationship(back_populates="meeting", cascade="all, delete-orphan")

class Participant(Base):
    meeting_id: Mapped[int] = mapped_column(ForeignKey("meeting.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255))
    joined_at: Mapped[Optional[datetime]] = mapped_column(default=None)
    last_seen_at: Mapped[Optional[datetime]] = mapped_column(default=None)

    meeting: Mapped[Meeting] = relationship(back_populates="participants")

    __table_args__ = (
        UniqueConstraint("meeting_id", "email", name="uq_participant_meeting_email"),
        Index("ix_participant_meeting_last_seen", "meeting_id", "last_seen_at"),
    )

class MeetingSummary(Base):
    meeting_id: Mapped[int] = mapped_column(ForeignKey("meeting.id", ondelete="CASCADE"), index=True)
    window_start: Mapped[datetime]
    window_end: Mapped[datetime]
    summary_text: Mapped[str] = mapped_column(Text)
    kind: Mapped[str] = mapped_column(String(32), default="rolling")  # rolling or final

    meeting: Mapped[Meeting] = relationship(back_populates="summaries")

