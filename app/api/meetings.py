from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy import select

from app.db.session import db_session
from app.models.meeting import Meeting, Participant, MeetingStatus, MeetingSummary
from app.models.base import Base
from app.db.session import engine
from app.services.calendar import build_ics_invite
from app.services.emailer import send_email
from app.services.summarizer import summarize_text
from app.services.vector_store import VectorStore
from app.models.event import MeetingEvent

# Create tables on first import
Base.metadata.create_all(bind=engine)

router = APIRouter(prefix="/meetings", tags=["meetings"])

class ParticipantIn(BaseModel):
    name: str
    email: EmailStr

class MeetingCreateIn(BaseModel):
    title: str
    description: Optional[str] = None
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    participants: List[ParticipantIn] = []

class MeetingOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: str
    scheduled_start: Optional[datetime]
    scheduled_end: Optional[datetime]
    actual_start: Optional[datetime]
    actual_end: Optional[datetime]

    class Config:
        from_attributes = True

@router.get("/", response_model=List[MeetingOut])
def list_meetings():
    """Get all meetings"""
    try:
        with db_session() as session:
            stmt = select(Meeting).order_by(Meeting.created_at.desc())
            meetings = list(session.scalars(stmt).all())
            # Convert to dicts while session is still open to avoid DetachedInstanceError
            meetings_data = []
            for meeting in meetings:
                meetings_data.append({
                    "id": meeting.id,
                    "title": meeting.title,
                    "description": meeting.description,
                    "status": meeting.status,
                    "scheduled_start": meeting.scheduled_start,
                    "scheduled_end": meeting.scheduled_end,
                    "actual_start": meeting.actual_start,
                    "actual_end": meeting.actual_end,
                })
            return meetings_data
    except Exception as e:
        from loguru import logger
        logger.error(f"Error listing meetings: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing meetings: {str(e)}")

@router.get("/{meeting_id}", response_model=MeetingOut)
def get_meeting(meeting_id: int):
    """Get a specific meeting"""
    with db_session() as session:
        meeting = session.get(Meeting, meeting_id)
        if not meeting:
            raise HTTPException(status_code=404, detail="Meeting not found")
        # Convert to dict while session is still open
        return {
            "id": meeting.id,
            "title": meeting.title,
            "description": meeting.description,
            "status": meeting.status,
            "scheduled_start": meeting.scheduled_start,
            "scheduled_end": meeting.scheduled_end,
            "actual_start": meeting.actual_start,
            "actual_end": meeting.actual_end,
        }

@router.post("/", response_model=MeetingOut)
def create_meeting(payload: MeetingCreateIn):
    with db_session() as session:
        meeting = Meeting(
            title=payload.title,
            description=payload.description,
            scheduled_start=payload.scheduled_start,
            scheduled_end=payload.scheduled_end,
        )
        session.add(meeting)
        session.flush()
        for p in payload.participants:
            session.add(Participant(meeting_id=meeting.id, name=p.name, email=str(p.email)))
        session.flush()
        # Convert to dict while session is still open
        return {
            "id": meeting.id,
            "title": meeting.title,
            "description": meeting.description,
            "status": meeting.status,
            "scheduled_start": meeting.scheduled_start,
            "scheduled_end": meeting.scheduled_end,
            "actual_start": meeting.actual_start,
            "actual_end": meeting.actual_end,
        }

class MeetingStartIn(BaseModel):
    start_time: Optional[datetime] = None

@router.post("/{meeting_id}/start", response_model=MeetingOut)
def start_meeting(meeting_id: int, payload: MeetingStartIn = MeetingStartIn()):
    with db_session() as session:
        db_meeting = session.get(Meeting, meeting_id)
        if not db_meeting:
            raise HTTPException(status_code=404, detail="Meeting not found")
        db_meeting.status = MeetingStatus.LIVE
        db_meeting.actual_start = payload.start_time or datetime.utcnow()
        session.add(db_meeting)
        session.flush()
        # Notify all participants that meeting has started
        recipients = [p.email for p in db_meeting.participants]
        if recipients:
            try:
                send_email(recipients, f"Meeting started: {db_meeting.title}", f"<p>Meeting {db_meeting.title} has started. Please join soon.</p>")
            except Exception as e:
                # Don't fail the request if email fails
                from loguru import logger
                logger.warning(f"Failed to send email notification: {e}")
        # Convert to dict while session is still open
        return {
            "id": db_meeting.id,
            "title": db_meeting.title,
            "description": db_meeting.description,
            "status": db_meeting.status,
            "scheduled_start": db_meeting.scheduled_start,
            "scheduled_end": db_meeting.scheduled_end,
            "actual_start": db_meeting.actual_start,
            "actual_end": db_meeting.actual_end,
        }

class JoinIn(BaseModel):
    email: EmailStr

@router.post("/{meeting_id}/join")
def join_meeting(meeting_id: int, payload: JoinIn):
    with db_session() as session:
        stmt = select(Participant).where(Participant.meeting_id == meeting_id, Participant.email == str(payload.email))
        participant = session.scalar(stmt)
        if not participant:
            raise HTTPException(status_code=404, detail="Participant not found for meeting")
        participant.joined_at = datetime.utcnow()
        participant.last_seen_at = participant.joined_at
        session.add(participant)
        return {"ok": True}

@router.post("/{meeting_id}/heartbeat")
def heartbeat(meeting_id: int, payload: JoinIn):
    with db_session() as session:
        stmt = select(Participant).where(Participant.meeting_id == meeting_id, Participant.email == str(payload.email))
        participant = session.scalar(stmt)
        if not participant:
            raise HTTPException(status_code=404, detail="Participant not found for meeting")
        participant.last_seen_at = datetime.utcnow()
        session.add(participant)
        return {"ok": True}

@router.post("/{meeting_id}/end", response_model=MeetingOut)
def end_meeting(meeting_id: int):
    with db_session() as session:
        db_meeting = session.get(Meeting, meeting_id)
        if not db_meeting:
            raise HTTPException(status_code=404, detail="Meeting not found")
        db_meeting.status = MeetingStatus.ENDED
        db_meeting.actual_end = datetime.utcnow()
        session.add(db_meeting)
        session.flush()
        # build final notes from all events
        events_stmt = select(MeetingEvent).where(MeetingEvent.meeting_id == db_meeting.id).order_by(MeetingEvent.created_at.asc())
        all_events = [e.content for e in session.scalars(events_stmt).all()]
        final_notes = summarize_text(all_events, max_sentences=12) if all_events else ""
        if final_notes:
            final_summary = MeetingSummary(
                meeting_id=db_meeting.id,
                window_start=db_meeting.actual_start or db_meeting.created_at,
                window_end=db_meeting.actual_end or datetime.utcnow(),
                summary_text=final_notes,
                kind="final",
            )
            session.add(final_summary)
            # persist to vector store
            vs = VectorStore()
            vs.add_texts([final_notes])
            # email notes to participants
            recipients = [p.email for p in db_meeting.participants]
            if recipients:
                try:
                    send_email(recipients, f"Notes: {db_meeting.title}", f"<p>{final_notes}</p>")
                except Exception as e:
                    # Don't fail the request if email fails
                    from loguru import logger
                    logger.warning(f"Failed to send email notification: {e}")
        # Convert to dict while session is still open
        return {
            "id": db_meeting.id,
            "title": db_meeting.title,
            "description": db_meeting.description,
            "status": db_meeting.status,
            "scheduled_start": db_meeting.scheduled_start,
            "scheduled_end": db_meeting.scheduled_end,
            "actual_start": db_meeting.actual_start,
            "actual_end": db_meeting.actual_end,
        }

class InviteIn(BaseModel):
    start: datetime
    end: datetime

@router.post("/{meeting_id}/invite")
def send_invites(meeting_id: int, payload: InviteIn):
    with db_session() as session:
        meeting = session.get(Meeting, meeting_id)
        if not meeting:
            raise HTTPException(status_code=404, detail="Meeting not found")
        recipients = [p.email for p in meeting.participants]
        ics_bytes = build_ics_invite(meeting.title, meeting.description or "", payload.start, payload.end, recipients)
        subject = f"Invitation: {meeting.title}"
        body = f"""
        <p>You are invited to <strong>{meeting.title}</strong></p>
        <p><strong>Time:</strong> {payload.start.strftime('%Y-%m-%d %H:%M:%S UTC')} - {payload.end.strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
        """
        if meeting.description:
            body += f"<p><strong>Description:</strong> {meeting.description}</p>"
        body += "<p>Please find the calendar invite attached to this email.</p>"
        if recipients:
            try:
                send_email(
                    recipients, 
                    subject, 
                    body,
                    attachment_data=ics_bytes,
                    attachment_filename="meeting.ics",
                    attachment_content_type="text/calendar; charset=utf-8; method=REQUEST"
                )
            except Exception as e:
                # Don't fail the request if email fails
                from loguru import logger
                logger.warning(f"Failed to send calendar invite email: {e}")
        return {"ok": True}

class RagIn(BaseModel):
    question: str

@router.get("/{meeting_id}/summaries")
def get_summaries(meeting_id: int):
    with db_session() as session:
        db_meeting = session.get(Meeting, meeting_id)
        if not db_meeting:
            raise HTTPException(status_code=404, detail="Meeting not found")
        stmt = select(MeetingSummary).where(MeetingSummary.meeting_id == meeting_id).order_by(MeetingSummary.window_end.desc())
        summaries = list(session.scalars(stmt).all())
        return {
            "summaries": [
                {
                    "id": s.id,
                    "kind": s.kind,
                    "window_start": s.window_start.isoformat(),
                    "window_end": s.window_end.isoformat(),
                    "summary_text": s.summary_text,
                }
                for s in summaries
            ]
        }

@router.post("/{meeting_id}/rag")
def rag_query(meeting_id: int, payload: RagIn):
    with db_session() as session:
        db_meeting = session.get(Meeting, meeting_id)
        if not db_meeting:
            raise HTTPException(status_code=404, detail="Meeting not found")
    
    # simple global index; in prod, partition per meeting
    vs = VectorStore()
    hits = vs.query(payload.question, k=5)
    
    # If no hits and vector store is not available, provide helpful message
    if not hits:
        from loguru import logger
        if not hasattr(vs, 'model') or vs.model is None:
            logger.warning("Vector store not available for RAG query")
    
    return {"answers": [{"text": h.text, "score": h.score} for h in hits]}

