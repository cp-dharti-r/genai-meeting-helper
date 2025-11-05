# Setup Notes

## Python Version Compatibility

**Important**: This application works best with **Python 3.11 or 3.12**.

If you're using **Python 3.13**, the vector store dependencies (faiss-cpu and sentence-transformers) are not yet available. The application will still run, but:
- RAG queries will return empty results
- Vector storage will be disabled (summaries won't be stored in vector DB)
- All other features (meetings, summaries, emails, calendar invites) will work normally

The application gracefully handles missing vector store dependencies.

## Installing Vector Store Dependencies (Python 3.11/3.12)

If you're using Python 3.11 or 3.12 and want full vector store functionality:

```bash
pip install sentence-transformers faiss-cpu
```

## Current Status

✅ Server is running successfully
✅ Core features working (meetings, summaries, emails, calendar)
⚠️ Vector store disabled (due to Python 3.13 compatibility)

## Running the Server

```bash
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The server will be available at `http://localhost:8000`

