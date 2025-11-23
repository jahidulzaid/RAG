# RAG Application - Quick Start Guide

## 🚀 Getting Started in 3 Steps

### Step 1: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 2: Set Your API Key
Edit `.env` file and add your GROQ API key:
```
GROQ_API_KEY=your_key_here
```

### Step 3: Start the Server
```powershell
.\start_server.ps1
```

Then open: **http://localhost:8000**

---

## 🎯 What Can You Do?

### Web Interface
1. **Upload Documents** - Click "📤 Upload Document"
2. **Ask Questions** - Type in the chat box
3. **Follow-up Questions** - It remembers context!
4. **View Sources** - See where answers come from

### CLI (Alternative)
```powershell
# Ingest documents
python rag_app.py ingest ./data

# Ask a question
python rag_app.py query "What is this about?"

# Interactive mode
python rag_app.py interactive
```

---

## 📝 Example Conversation

```
You: What is RAG?
AI: RAG (Retrieval Augmented Generation) is a technique that combines...
    📚 Sources: sample.txt

You: What are its benefits?
AI: The benefits of RAG include... [understands "its" = RAG]
    📚 Sources: sample.txt

You: How does it work?
AI: RAG works by... [understands "it" = RAG]
```

---

## 🔧 Troubleshooting

**Server won't start?**
- Check if port 8000 is free
- Verify GROQ_API_KEY is set in `.env`

**No documents to query?**
- Click "Ingest Data Folder" in the web UI
- Or run: `python rag_app.py ingest ./data`

**API errors?**
- Check logs in terminal
- Visit http://localhost:8000/docs for API status

---

## 📚 Learn More

- **Full README**: See [README.md](README.md)
- **API Guide**: See [API_GUIDE.md](API_GUIDE.md)
- **Test API**: Run `python test_api.py`

---

## 🎉 That's It!

You now have a fully functional RAG system with:
- ✅ Web chat interface
- ✅ Document upload
- ✅ Conversation memory
- ✅ Source citations
- ✅ REST API

Enjoy! 🚀
