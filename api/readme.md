# FastAPI + Frontend Integration Guide

## 🚀 Quick Start

### 1. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 2. Start the Server

**Windows (PowerShell):**
```powershell
.\start_server.ps1
```

**Or manually:**
```powershell
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

**Linux/Mac:**
```bash
chmod +x start_server.sh
./start_server.sh
```

### 3. Access the Application

- **Frontend UI**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **Alternative Docs**: http://localhost:8000/redoc


## 🌐 API Endpoints

### Status

**GET** `/api/status`

Check API status and configuration.

**Response:**
```json
{
  "status": "online",
  "vectorstore_initialized": true,
  "model_name": "llama-3.3-70b-versatile"
}
```

### Query

**POST** `/api/query`

Query the RAG system with conversation history support.

**Request:**
```json
{
  "question": "What is RAG?",
  "session_id": "optional-session-id",
  "maintain_history": true
}
```

**Response:**
```json
{
  "answer": "RAG stands for...",
  "sources": [
    {
      "content": "Document excerpt...",
      "metadata": {
        "source": "data/sample.txt"
      }
    }
  ],
  "session_id": "uuid-session-id"
}
```

### Ingest Documents

**POST** `/api/ingest`

Ingest documents from a file or directory path.

**Request:**
```json
{
  "path": "./data"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Successfully ingested 15 document chunks",
  "documents_processed": 15
}
```

### Upload File

**POST** `/api/upload`

Upload and process a document file.

**Request:** `multipart/form-data` with file

**Response:**
```json
{
  "success": true,
  "message": "Successfully uploaded and ingested 8 chunks from document.pdf",
  "documents_processed": 8
}
```

### Get History

**GET** `/api/history/{session_id}`

Get conversation history for a session.

**Response:**
```json
{
  "history": [
    {
      "question": "What is RAG?",
      "answer": "RAG is..."
    }
  ],
  "session_id": "uuid-session-id"
}
```

### Clear History

**DELETE** `/api/history/{session_id}`

Clear conversation history for a session.

**Response:**
```json
{
  "message": "History cleared",
  "session_id": "uuid-session-id"
}
```

### Delete Session

**DELETE** `/api/session/{session_id}`

Delete a session entirely.

**Response:**
```json
{
  "message": "Session deleted",
  "session_id": "uuid-session-id"
}
```

## 🎨 Frontend Features

### Main Interface

1. **Chat Area**: Interactive conversation with the AI
2. **Source Citations**: View document sources for each answer
3. **File Upload**: Drag and drop or click to upload documents
4. **Conversation History**: View and clear chat history
5. **Real-time Status**: See connection and vectorstore status



## 🔧 Configuration

Edit `.env` file:

```env
# GROQ API Configuration
GROQ_API_KEY=your_groq_api_key_here

# Model Configuration
MODEL_NAME=llama-3.3-70b-versatile
TEMPERATURE=0.7
MAX_TOKENS=2048

# Vector Store Configuration
VECTORSTORE_PATH=./vectorstore
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# Data Directory
DATA_DIR=./data
```

### Vectorstore Not Initialized

```powershell
# Ingest documents first
python rag_app.py ingest ./data

```

## 🚀 Deployment

### Docker Deployment

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:

```powershell
docker build -t rag-app .
docker run -p 8000:8000 -v ${PWD}/data:/app/data rag-app
```

For issues or questions, check the API documentation at http://localhost:8000/docs
