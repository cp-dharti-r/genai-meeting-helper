# Troubleshooting Guide

## API Endpoints Not Showing

### Check if server is running:
```bash
curl http://localhost:8000/health
```
Should return: `{"healthy":true}`

### Check all endpoints:
```bash
curl http://localhost:8000/openapi.json | python3 -m json.tool | grep '"\/meetings'
```

### View API documentation:
Open in browser: `http://localhost:8000/docs`

You should see:
- `GET /meetings/` - List all meetings
- `GET /meetings/{meeting_id}` - Get a meeting
- `POST /meetings/` - Create a meeting
- `POST /meetings/{meeting_id}/start` - Start meeting
- `POST /meetings/{meeting_id}/end` - End meeting
- `GET /meetings/{meeting_id}/summaries` - Get summaries
- `POST /meetings/{meeting_id}/rag` - RAG query
- And more...

## "Failed to fetch" Error

### Solution 1: Use HTTP server (Recommended)
Don't open HTML file directly. Use a local server:

```bash
cd /Users/dharti/Projects/python/genai-meeting-helper
python3 -m http.server 8080
```

Then open: `http://localhost:8080/web/index.html`

### Solution 2: Check server is running
```bash
# Check server
curl http://localhost:8000/health

# If not running, start it:
cd /Users/dharti/Projects/python/genai-meeting-helper
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Solution 3: Check browser console
Open browser DevTools (F12) → Console tab
Look for CORS or network errors

## Internal Server Error (500)

### Check server logs
The server terminal should show the error details.

### Common fixes:
1. **Database not initialized:**
   ```bash
   cd /Users/dharti/Projects/python/genai-meeting-helper
   source .venv/bin/activate
   python3 -c "from app.db.session import engine; from app.models.base import Base; Base.metadata.create_all(bind=engine)"
   ```

2. **Restart server:**
   - Stop the server (Ctrl+C)
   - Start again: `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`

3. **Check database:**
   ```bash
   ls -la meeting_helper.db
   ```

## Test Endpoints Manually

### 1. List meetings:
```bash
curl http://localhost:8000/meetings/
```

### 2. Create meeting:
```bash
curl -X POST "http://localhost:8000/meetings/" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Meeting","participants":[]}'
```

### 3. Check health:
```bash
curl http://localhost:8000/health
```

## Still Having Issues?

1. **Check server logs** - Look at the terminal where uvicorn is running
2. **Check browser console** - F12 → Console tab
3. **Verify ports** - Make sure port 8000 is not blocked
4. **Restart everything:**
   ```bash
   # Stop server (Ctrl+C)
   # Then restart:
   source .venv/bin/activate
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

