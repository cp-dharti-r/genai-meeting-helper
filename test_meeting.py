#!/usr/bin/env python3
"""
Quick test script for the Meeting Helper API
Run this after starting the server: uvicorn app.main:app --reload
"""
import requests
import time
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

def test_meeting_flow():
    print("=" * 60)
    print("Testing Meeting Helper API")
    print("=" * 60)
    
    # 1. Create meeting
    print("\n1. Creating meeting...")
    response = requests.post(f"{BASE_URL}/meetings/", json={
        "title": "Python Test Meeting",
        "description": "Testing the meeting helper via Python script",
        "participants": [
            {"name": "Alice", "email": "alice@example.com"},
            {"name": "Bob", "email": "bob@example.com"}
        ]
    })
    if response.status_code != 200:
        print(f"ERROR: {response.status_code} - {response.text}")
        return
    meeting = response.json()
    meeting_id = meeting["id"]
    print(f"✅ Created meeting ID: {meeting_id}")
    print(f"   Title: {meeting['title']}")
    print(f"   Status: {meeting['status']}")

    # 2. Start meeting
    print("\n2. Starting meeting...")
    response = requests.post(f"{BASE_URL}/meetings/{meeting_id}/start", json={})
    if response.status_code != 200:
        print(f"ERROR: {response.status_code} - {response.text}")
        return
    print("✅ Meeting started (notification email sent to participants)")

    # 3. Join as participant
    print("\n3. Participant joining...")
    response = requests.post(f"{BASE_URL}/meetings/{meeting_id}/join", json={
        "email": "alice@example.com"
    })
    if response.status_code != 200:
        print(f"ERROR: {response.status_code} - {response.text}")
        return
    print("✅ Alice joined the meeting")

    # 4. Ingest events (simulate discussion)
    print("\n4. Ingesting meeting events...")
    events = [
        "We need to improve our deployment process and make it more automated.",
        "The team agreed on using Docker containers for better consistency.",
        "We should also set up automated testing to catch bugs earlier.",
        "Alice suggested implementing a CI/CD pipeline for faster releases.",
        "Bob mentioned we need better monitoring and alerting systems."
    ]

    for i, event_text in enumerate(events, 1):
        response = requests.post(f"{BASE_URL}/events/", json={
            "meeting_id": meeting_id,
            "content": event_text,
            "author": "Alice" if i % 2 == 1 else "Bob"
        })
        if response.status_code == 200:
            print(f"✅ Event {i} ingested: {event_text[:50]}...")
        else:
            print(f"ERROR ingesting event {i}: {response.status_code}")

    # 5. Heartbeat
    print("\n5. Sending heartbeat...")
    response = requests.post(f"{BASE_URL}/meetings/{meeting_id}/heartbeat", json={
        "email": "alice@example.com"
    })
    if response.status_code == 200:
        print("✅ Heartbeat sent")

    # 6. Wait a bit (simulate meeting time)
    print("\n6. Simulating meeting time (waiting 3 seconds)...")
    time.sleep(3)

    # 7. End meeting (generates final notes, emails, persists to vector store)
    print("\n7. Ending meeting (generating final notes)...")
    response = requests.post(f"{BASE_URL}/meetings/{meeting_id}/end")
    if response.status_code != 200:
        print(f"ERROR: {response.status_code} - {response.text}")
        return
    meeting_ended = response.json()
    print("✅ Meeting ended")
    print(f"   Final status: {meeting_ended['status']}")
    print("   Final notes generated and emailed to participants")
    print("   Notes persisted to vector store")

    # 8. Test RAG query
    print("\n8. Testing RAG query...")
    response = requests.post(f"{BASE_URL}/meetings/{meeting_id}/rag", json={
        "question": "What did we discuss about deployment and automation?"
    })
    if response.status_code == 200:
        results = response.json()
        print("✅ RAG query successful")
        print(f"   Found {len(results.get('answers', []))} relevant answers:")
        for i, answer in enumerate(results.get('answers', [])[:3], 1):
            print(f"   {i}. Score: {answer['score']:.3f}")
            print(f"      {answer['text'][:100]}...")
    else:
        print(f"ERROR: {response.status_code} - {response.text}")

    # 9. Send calendar invite
    print("\n9. Sending calendar invite...")
    future_start = (datetime.utcnow() + timedelta(days=1)).isoformat() + "Z"
    future_end = (datetime.utcnow() + timedelta(days=1, hours=1)).isoformat() + "Z"
    response = requests.post(f"{BASE_URL}/meetings/{meeting_id}/invite", json={
        "start": future_start,
        "end": future_end
    })
    if response.status_code == 200:
        print("✅ Calendar invite sent to participants")
    else:
        print(f"ERROR: {response.status_code} - {response.text}")

    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)
    print(f"\nNote: Check server logs for email notifications and rolling summaries.")
    print(f"      Rolling summaries are generated every 5 minutes during live meetings.")

if __name__ == "__main__":
    try:
        # Check if server is running
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        if response.status_code == 200:
            test_meeting_flow()
        else:
            print(f"Server not healthy: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to server.")
        print("Please start the server first:")
        print("  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    except Exception as e:
        print(f"ERROR: {e}")

