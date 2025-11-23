# 🎉 RAG Application - Complete Implementation


## 🚀 Quick Start

### 1. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 2. Configure API Key
Your `.env` already has the GROQ_API_KEY set ✅

### 3. Start the Server
```powershell
.\start_server.ps1
```

### 4. Access the App
Open browser: **http://localhost:8000**


```

## 🎯 Available Endpoints

### Web UI
- `GET /` - Chat interface
- `GET /docs` - Interactive API documentation
- `GET /redoc` - Alternative API docs

### API
- `GET /api/status` - Check system status
- `POST /api/query` - Ask questions (with history)
- `POST /api/upload` - Upload documents
- `POST /api/ingest` - Ingest from directory
- `GET /api/history/{session_id}` - View history
- `DELETE /api/history/{session_id}` - Clear history
- `DELETE /api/session/{session_id}` - Delete session



## 🔧 Configuration

Edit `.env`:
```env
GROQ_API_KEY=your_actual_groq_api_key_here
MODEL_NAME=llama-3.3-70b-versatile
TEMPERATURE=0.7
CHUNK_SIZE=1000
TOP_K_RESULTS=4
```


## 🔄 CLI Still Works!

```powershell
# Ingest documents
python rag_app.py ingest ./data

# Ask a question
python rag_app.py query "What is RAG?"

# Interactive mode
python rag_app.py interactive
```


**Questions?** Check the documentation or API docs at http://localhost:8000/docs
