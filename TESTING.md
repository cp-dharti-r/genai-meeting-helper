# Testing Guide

## Quick Start Testing

### 1. Setup Environment

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (optional - will use defaults if not present)
cp .env.example .env
```

### 2. Start the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The server will start on `http://localhost:8000`

### 3. Test Methods

#### Option A: Using the Web UI (Easiest)

1. Open `web/index.html` in your browser (double-click or `open web/index.html`)
2. Use the UI forms to:
   - Create a meeting
   - Start/join meetings
   - Ingest events
   - Test RAG queries

#### Option B: Using curl (Command Line)

```bash
# 1. Create a meeting
curl -X POST "http://localhost:8000/meetings/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Meeting",
    "description": "Testing the meeting helper",
    "participants": [
      {"name": "Alice", "email": "alice@example.com"},
      {"name": "Bob", "email": "bob@example.com"}
    ]
  }'

# Save the meeting ID from response (e.g., {"id": 1, ...})

# 2. Start the meeting
curl -X POST "http://localhost:8000/meetings/1/start" \
  -H "Content-Type: application/json" \
  -d '{}'

# 3. Join as a participant
curl -X POST "http://localhost:8000/meetings/1/join" \
  -H "Content-Type: application/json" \
  -d '{"email": "alice@example.com"}'

# 4. Ingest some meeting events (simulate discussion)
curl -X POST "http://localhost:8000/events/" \
  -H "Content-Type: application/json" \
  -d '{
    "meeting_id": 1,
    "content": "We discussed the quarterly goals and decided to focus on improving user engagement.",
    "author": "Alice"
  }'

curl -X POST "http://localhost:8000/events/" \
  -H "Content-Type: application/json" \
  -d '{
    "meeting_id": 1,
    "content": "Bob suggested implementing a new feature for better analytics tracking.",
    "author": "Bob"
  }'

# 5. Wait 5+ minutes or manually trigger (the scheduler runs every 5 min)
# Check logs for rolling summaries

# 6. End the meeting (this generates final notes and emails)
curl -X POST "http://localhost:8000/meetings/1/end"

# 7. Test RAG query
curl -X POST "http://localhost:8000/meetings/1/rag" \
  -H "Content-Type: application/json" \
  -d '{"question": "What were the main topics discussed?"}'

# 8. Send calendar invite
curl -X POST "http://localhost:8000/meetings/1/invite" \
  -H "Content-Type: application/json" \
  -d '{
    "start": "2025-10-06T10:00:00Z",
    "end": "2025-10-06T11:00:00Z"
  }'
```

#### Option C: Using Python Script

Create a test script `test_meeting.py`:

```python
import requests
import time
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

# 1. Create meeting
response = requests.post(f"{BASE_URL}/meetings/", json={
    "title": "Python Test Meeting",
    "description": "Testing via Python",
    "participants": [
        {"name": "Alice", "email": "alice@example.com"},
        {"name": "Bob", "email": "bob@example.com"}
    ]
})
meeting = response.json()
meeting_id = meeting["id"]
print(f"Created meeting {meeting_id}")

# 2. Start meeting
response = requests.post(f"{BASE_URL}/meetings/{meeting_id}/start", json={})
print("Started meeting")

# 3. Join as participant
response = requests.post(f"{BASE_URL}/meetings/{meeting_id}/join", json={
    "email": "alice@example.com"
})
print("Alice joined")

# 4. Ingest events
events = [
    "We need to improve our deployment process.",
    "The team agreed on using Docker containers.",
    "We should also set up automated testing."
]

for event_text in events:
    response = requests.post(f"{BASE_URL}/events/", json={
        "meeting_id": meeting_id,
        "content": event_text,
        "author": "Alice"
    })
    print(f"Ingested event: {event_text[:50]}...")

# 5. Wait a bit (simulate meeting time)
print("Waiting 10 seconds...")
time.sleep(10)

# 6. End meeting
response = requests.post(f"{BASE_URL}/meetings/{meeting_id}/end")
print("Ended meeting - final notes generated")

# 7. Test RAG
response = requests.post(f"{BASE_URL}/meetings/{meeting_id}/rag", json={
    "question": "What did we discuss about deployment?"
})
print("RAG Results:", response.json())
```

Run it:
```bash
python test_meeting.py
```

#### Option D: Using FastAPI's Interactive Docs

1. Start the server
2. Visit `http://localhost:8000/docs` in your browser
3. Use the Swagger UI to test all endpoints interactively

### 4. Verify Features

- **Rolling Summaries**: Check server logs every 5 minutes for summary generation
- **Email Notifications**: Without SMTP configured, emails are logged to console
- **Vector Store**: Check `.vector_index/` directory for persisted embeddings
- **Database**: Check `meeting_helper.db` SQLite file

### 5. Check Logs

The server will log:
- Email attempts (when SMTP not configured)
- Scheduler activity
- Any errors

### 6. Expected Behavior

- ✅ Meeting creation returns meeting ID
- ✅ Starting meeting sends notification email (logged if SMTP not configured)
- ✅ Events can be ingested during live meetings
- ✅ Every 5 minutes, rolling summaries are generated (if events exist)
- ✅ Ending meeting generates final notes, emails them, and persists to vector store
- ✅ RAG queries return relevant snippets from past meeting notes

### Troubleshooting

**Import errors**: Make sure you're in the virtual environment and all dependencies are installed

**Database errors**: Delete `meeting_helper.db` to reset

**Vector store errors**: Delete `.vector_index/` directory to reset

**CORS errors**: Make sure the server is running and CORS is configured correctly

**Scheduler not running**: Check logs - scheduler starts automatically with the app

