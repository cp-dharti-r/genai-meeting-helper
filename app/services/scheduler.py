from __future__ import annotations

from datetime import datetime, timedelta
from typing import List

from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import select

from app.db.session import db_session
from app.models.meeting import Meeting, MeetingStatus, MeetingSummary, Participant
from app.models.event import MeetingEvent
from app.services.summarizer import summarize_text
from app.services.emailer import send_email


scheduler = BackgroundScheduler()


def summarize_active_meetings() -> None:
    now = datetime.utcnow()
    window_start = now - timedelta(minutes=5)
    with db_session() as session:
        stmt = select(Meeting).where(Meeting.status == MeetingStatus.LIVE)
        live_meetings: List[Meeting] = list(session.scalars(stmt).all())
        for meeting in live_meetings:
            events_stmt = select(MeetingEvent).where(
                MeetingEvent.meeting_id == meeting.id,
                MeetingEvent.created_at >= window_start,
                MeetingEvent.created_at < now,
            )
            events = list(session.scalars(events_stmt).all())
            if not events:
                continue
            content_chunks = [e.content for e in events]
            summary = summarize_text(content_chunks, max_sentences=5)
            if not summary:
                continue
            ms = MeetingSummary(
                meeting_id=meeting.id,
                window_start=window_start,
                window_end=now,
                summary_text=summary,
                kind="rolling",
            )
            session.add(ms)


def check_absentees() -> None:
    """Check for participants who haven't joined and notify them"""
    now = datetime.utcnow()
    # Check meetings that started 2-5 minutes ago (give grace period)
    grace_period_start = now - timedelta(minutes=5)
    grace_period_end = now - timedelta(minutes=2)
    
    with db_session() as session:
        stmt = select(Meeting).where(
            Meeting.status == MeetingStatus.LIVE,
            Meeting.actual_start >= grace_period_start,
            Meeting.actual_start <= grace_period_end,
        )
        live_meetings: List[Meeting] = list(session.scalars(stmt).all())
        
        for meeting in live_meetings:
            # Get participants who haven't joined
            participants_stmt = select(Participant).where(
                Participant.meeting_id == meeting.id,
                Participant.joined_at.is_(None),
            )
            absentees = list(session.scalars(participants_stmt).all())
            
            if absentees:
                absentee_emails = [p.email for p in absentees]
                absentee_names = [p.name for p in absentees]
                subject = f"Reminder: Join {meeting.title}"
                body = f"""
                <p>Hello,</p>
                <p>This is a reminder that the meeting <strong>{meeting.title}</strong> has started and you haven't joined yet.</p>
                <p>Please join the meeting as soon as possible.</p>
                <p>Meeting started at: {meeting.actual_start.strftime('%Y-%m-%d %H:%M:%S UTC') if meeting.actual_start else 'N/A'}</p>
                """
                send_email(absentee_emails, subject, body)


def start_scheduler() -> None:
    if scheduler.state == 1:  # already running
        return
    scheduler.add_job(summarize_active_meetings, "interval", minutes=5, id="rolling_summaries", replace_existing=True)
    scheduler.add_job(check_absentees, "interval", minutes=3, id="check_absentees", replace_existing=True)
    scheduler.start()
