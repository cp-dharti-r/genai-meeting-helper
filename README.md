# GenAI Meeting Helper

A FastAPI-based meeting assistant that provides real-time summaries, scheduling, notifications, and RAG-based retrieval of meeting information.

## Features

- **Meeting Lifecycle Management**: Create, start, join, and end meetings
- **Real-time Summaries**: Automatic 5-minute rolling summaries during live meetings (displayed in UI)
- **Email Notifications**: Notify participants when meetings start, send reminders to absentees, and send final notes
- **Absentee Tracking**: Automatically detect and notify participants who haven't joined after meeting starts
- **Calendar Integration**: Generate and email ICS calendar invites for follow-up meetings (with proper attachments)
- **Vector Storage**: Store meeting summaries in a vector database for semantic search
- **RAG (Retrieval-Augmented Generation)**: Query past meeting notes using natural language
- **Web UI**: Interactive interface with real-time summary display and auto-refresh

## Quick Start

### 1. Setup

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Optional: Configure email (defaults work for testing)
cp .env.example .env
# Edit .env with your SMTP settings if you want real emails
```

### 2. Run the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### 3. Test the Application

See [TESTING.md](TESTING.md) for detailed testing instructions.

**Quick test options:**

1. **Web UI**: Open `web/index.html` in your browser
2. **Python script**: Run `python test_meeting.py` (server must be running)
3. **Interactive docs**: Visit `http://localhost:8000/docs`
4. **curl commands**: See TESTING.md for examples

## API Endpoints

- `POST /meetings/` - Create a new meeting
- `POST /meetings/{id}/start` - Start a meeting (sends notifications)
- `POST /meetings/{id}/join` - Join a meeting as participant
- `POST /meetings/{id}/heartbeat` - Update participant presence
- `POST /meetings/{id}/end` - End meeting (generates final notes, emails, stores in vector DB)
- `POST /meetings/{id}/invite` - Send calendar invites (with ICS attachment)
- `GET /meetings/{id}/summaries` - Get all meeting summaries (rolling and final)
- `POST /events/` - Ingest meeting content/events
- `POST /meetings/{id}/rag` - Query meeting notes using RAG

## Project Structure

```
genai-meeting-helper/
├── app/
│   ├── api/          # API routes
│   ├── db/           # Database session
│   ├── models/       # SQLAlchemy models
│   ├── services/     # Business logic (email, calendar, vector store, scheduler)
│   ├── utils/        # Configuration
│   └── main.py       # FastAPI app
├── web/
│   └── index.html    # Simple web UI
├── test_meeting.py   # Test script
└── requirements.txt  # Dependencies
```

## Configuration

Create a `.env` file (see `.env.example`):

- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD` - Email configuration
- `VECTOR_INDEX_PATH` - Path for vector index storage (default: `.vector_index`)
- `PORT`, `HOST` - Server configuration

**Note**: If SMTP is not configured, emails are logged to console instead.

## How It Works

1. **Create Meeting**: Define participants and meeting details
2. **Start Meeting**: Meeting goes live, all participants notified
3. **Absentee Detection**: Background scheduler checks every 3 minutes for participants who haven't joined (2-5 min after start) and sends reminders
4. **Ingest Events**: During meeting, send discussion content via `/events/` endpoint
5. **Rolling Summaries**: Every 5 minutes, summaries are generated automatically and can be viewed in the UI
6. **End Meeting**: Final notes generated (highlighting main points), emailed to all participants, stored in vector DB
7. **Query**: Use RAG endpoint to search past meeting notes

## Technologies

- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: ORM for database operations
- **FAISS**: Vector similarity search
- **Sentence Transformers**: Text embeddings
- **APScheduler**: Background task scheduling
- **iCalendar**: Calendar invite generation

## Development

See [TESTING.md](TESTING.md) for comprehensive testing guide.