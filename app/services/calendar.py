from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from icalendar import Calendar, Event


def build_ics_invite(
    summary: str,
    description: str,
    start: datetime,
    end: datetime,
    attendees_emails: Optional[List[str]] = None,
) -> bytes:
    cal = Calendar()
    cal.add("prodid", "-//GenAI Meeting Helper//")
    cal.add("version", "2.0")

    event = Event()
    event.add("summary", summary)
    event.add("description", description)
    event.add("dtstart", start)
    event.add("dtend", end)

    if attendees_emails:
        for email in attendees_emails:
            event.add("attendee", f"MAILTO:{email}")

    cal.add_component(event)
    return cal.to_ical()
