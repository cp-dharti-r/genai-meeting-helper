from __future__ import annotations

from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.db.session import db_session
from app.models.event import MeetingEvent
from app.models.meeting import Meeting

router = APIRouter(prefix="/events", tags=["events"])

class EventIn(BaseModel):
    meeting_id: int
    content: str
    author: str | None = None

@router.post("/")
def ingest_event(payload: EventIn):
    with db_session() as session:
        meeting = session.get(Meeting, payload.meeting_id)
        if not meeting:
            raise HTTPException(status_code=404, detail="Meeting not found")
        event = MeetingEvent(meeting_id=payload.meeting_id, content=payload.content, author=payload.author)
        session.add(event)
        session.flush()
        return {"id": event.id}
