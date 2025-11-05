# Quick Testing Guide

## 🚀 Server Status
✅ Server is running at `http://localhost:8000`

## Testing Options

### Option 1: Web UI (Easiest - Recommended)

1. **Open the Web Interface**
   ```bash
   open web/index.html
   ```
   Or navigate to `web/index.html` in your browser

2. **View All Meetings**
   - At the top, you'll see "All Meetings" section
   - Click "Refresh List" to see all meetings
   - Or click "Auto-refresh (every 10s)" for live updates

3. **Create a Meeting**
   - Fill in the form:
     - **Title**: "Team Standup"
     - **Description**: "Daily standup meeting"
     - **Participants**: (one per line, format: `name,email`)
       ```
       Alice,alice@example.com
       Bob,bob@example.com
       ```
   - Click "Create"
   - The meeting will appear in the "All Meetings" list above

4. **Select a Meeting**
   - Click on any meeting card in the "All Meetings" list
   - The Meeting ID will auto-fill in the "Controls" section

5. **Start the Meeting**
   - Make sure Meeting ID is filled (or select from list)
   - Click "Start" button
   - Check server logs - you'll see email notification (if SMTP not configured, it's logged)

6. **Join as Participant**
   - Enter email: `alice@example.com`
   - Click "Join"
   - This marks Alice as joined

7. **Add Meeting Content (Events)**
   - In "Ingest Event" section:
     - Enter some discussion content: "We discussed the quarterly goals and decided to focus on user engagement."
     - Optional: Add author name "Alice"
     - Click "Submit Event"
   - Add more events to simulate discussion:
     - "Bob suggested implementing a new analytics dashboard."
     - "The team agreed to start next week."

8. **View Rolling Summaries**
   - After 5 minutes, rolling summaries are generated automatically
   - In "Rolling Summaries" section, click "Refresh Now"
   - Or enable "Auto-refresh" to see summaries appear every 30 seconds
   - Summaries will show every 5 minutes of discussion

9. **End the Meeting**
   - Click "End" button
   - Final notes will be generated and emailed to all participants
   - Summary will be stored in vector DB (if available)

10. **Test RAG Query**
    - Enter a question like: "What did we discuss about analytics?"
    - Click "Ask"
    - See relevant meeting content (if vector store is enabled)

11. **Send Calendar Invite**
    - In "Invite / Follow-up" section:
      - Start: `2025-11-06T10:00:00Z`
      - End: `2025-11-06T11:00:00Z`
    - Click "Send Invite"
    - Calendar invite will be emailed with ICS attachment

---

### Option 2: Python Test Script (Automated)

```bash
cd /Users/dharti/Projects/python/genai-meeting-helper
source .venv/bin/activate
python test_meeting.py
```

This will:
- Create a meeting
- Start it
- Add participants
- Ingest events
- End the meeting
- Test RAG queries

---

### Option 3: API via curl (Command Line)

#### 1. Create a Meeting
```bash
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
```

Save the meeting ID from the response (e.g., `{"id": 1, ...}`)

#### 2. List All Meetings
```bash
curl http://localhost:8000/meetings/
```

#### 3. Start Meeting (replace `1` with your meeting ID)
```bash
curl -X POST "http://localhost:8000/meetings/1/start" \
  -H "Content-Type: application/json" \
  -d '{}'
```

#### 4. Join Meeting
```bash
curl -X POST "http://localhost:8000/meetings/1/join" \
  -H "Content-Type: application/json" \
  -d '{"email": "alice@example.com"}'
```

#### 5. Add Event (simulate discussion)
```bash
curl -X POST "http://localhost:8000/events/" \
  -H "Content-Type: application/json" \
  -d '{
    "meeting_id": 1,
    "content": "We discussed quarterly goals and user engagement strategies.",
    "author": "Alice"
  }'
```

#### 6. Get Summaries
```bash
curl http://localhost:8000/meetings/1/summaries
```

#### 7. End Meeting
```bash
curl -X POST "http://localhost:8000/meetings/1/end"
```

#### 8. Test RAG Query
```bash
curl -X POST "http://localhost:8000/meetings/1/rag" \
  -H "Content-Type: application/json" \
  -d '{"question": "What were the main topics discussed?"}'
```

---

### Option 4: Interactive API Docs

1. Open browser: `http://localhost:8000/docs`
2. Use Swagger UI to test all endpoints interactively
3. Click "Try it out" on any endpoint
4. Fill in parameters and execute

---

## 🎯 Quick Test Flow (5 minutes)

1. **Open** `web/index.html` in browser
2. **Create** a meeting with 2-3 participants
3. **Click** the meeting in the list to select it
4. **Start** the meeting
5. **Add** 3-4 events (simulate discussion)
6. **Wait** 5 minutes OR manually check server logs for rolling summaries
7. **Refresh** summaries view to see rolling summaries
8. **End** the meeting
9. **Check** summaries again for final summary

---

## 📊 What to Check

### Server Logs
- Email notifications (logged if SMTP not configured)
- Rolling summaries generated every 5 minutes
- Absentee notifications (sent 2-5 minutes after meeting starts)

### Web UI
- Meetings list updates
- Meeting selection works
- Summaries appear in real-time
- Status badges show correctly

### Database
- Check `meeting_helper.db` SQLite file
- Meetings, participants, events, summaries stored

### Vector Store
- If vector store dependencies installed: summaries stored in `.vector_index/`
- If not: warnings in logs, but app still works

---

## 🐛 Troubleshooting

**Can't see meetings?**
- Click "Refresh List" button
- Check browser console for errors
- Verify server is running: `curl http://localhost:8000/health`

**Summaries not showing?**
- Wait at least 5 minutes after starting meeting
- Make sure you've added events (no events = no summaries)
- Check server logs for scheduler activity

**Email not working?**
- Check `.env` file for SMTP settings
- If not configured, emails are logged to console
- Check server logs for email output

---

## ✅ Expected Behavior

1. ✅ Meetings appear in list immediately after creation
2. ✅ Status badges update (Scheduled → Live → Ended)
3. ✅ Rolling summaries appear every 5 minutes (if events exist)
4. ✅ Final summary generated on meeting end
5. ✅ Email notifications sent (logged if SMTP not configured)
6. ✅ RAG queries work (if vector store enabled)

---

**Ready to test! Start with the Web UI for the best experience.** 🎉

