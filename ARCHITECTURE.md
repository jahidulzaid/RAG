# RAG Application Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACES                          │
├─────────────────────────────────┬───────────────────────────────┤
│   Web Browser (Port 8000)       │   Command Line Interface      │
│   - Modern Chat UI              │   - rag_app.py ingest         │
│   - File Upload                 │   - rag_app.py query          │
│   - Real-time Chat              │   - rag_app.py interactive    │
└────────────┬────────────────────┴───────────────┬───────────────┘
             │                                    │
             │ HTTP/REST API                      │ Direct
             │                                    │
             ▼                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                     APPLICATION LAYER                           │
├─────────────────────────────────┬───────────────────────────────┤
│   FastAPI Backend               │   CLI Application             │
│   (api/main.py)                 │   (rag_app.py)                │
│   - Session Management          │   - Direct Component Access   │
│   - Multi-user Support          │   - Single User               │
│   - API Endpoints               │                               │
└────────────┬────────────────────┴───────────────┬───────────────┘
             │                                    │
             │ Both use same core components      │
             │                                    │
             ▼                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                      CORE RAG COMPONENTS                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌────────────────┐        ┌─────────────────┐                  │
│  │   RAGChain     │◄───────┤   GrokLLM       │                  │
│  │                │        │   (OpenAI SDK)  │                  │
│  │ - Query Logic  │        │                 │                  │
│  │ - History Mgmt │        └─────────────────┘                  │
│  │ - Context Fmt  │                 │                           │
│  └────────┬───────┘                 │                           │
│           │                         │                           │
│           │                         ▼                           │
│           │              ┌──────────────────┐                   │
│           │              │   GROQ API       │                   │
│           │              │   (Cloud)        │                   │
│           │              └──────────────────┘                   │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────────┐       ┌────────────────────┐           │
│  │ VectorStoreManager  │◄──────┤ DocumentProcessor  │           │
│  │                     │       │                    │           │
│  │ - FAISS Index       │       │ - Load Files       │           │
│  │ - Embeddings        │       │ - Text Splitting   │           │
│  │ - Similarity Search │       │ - Metadata         │           │
│  └─────────────────────┘       └────────────────────┘           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
             │                                    │
             │ Reads/Writes                       │ Reads
             │                                    │
             ▼                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATA LAYER                                 │
├─────────────────────────────────┬───────────────────────────────┤
│   Vector Database               │   Source Documents            │
│   (vectorstore/)                │   (data/)                     │
│   - FAISS index files           │   - PDFs                      │
│   - Embeddings cache            │   - Text files                │
│   - Persisted on disk           │   - Markdown                  │
│                                 │   - CSV files                 │
└─────────────────────────────────┴───────────────────────────────┘
```

## Data Flow - Query Processing

```
1. USER QUERY
   │
   ├─► Web: User types in chat
   │   "What is RAG?"
   │
   └─► CLI: python rag_app.py query "What is RAG?"
   
2. SESSION MANAGEMENT (Web only)
   │
   └─► Get or create session
       Store session_id for conversation continuity
   
3. RAG CHAIN PROCESSING
   │
   ├─► Check chat history
   │   Is this a follow-up question?
   │
   ├─► Contextualize query
   │   "What is RAG?" + history context
   │
   └─► Format with conversation history
   
4. VECTOR RETRIEVAL
   │
   ├─► Embed query using HuggingFace
   │   Query → [0.23, -0.45, 0.67, ...] (384 dims)
   │
   ├─► Search FAISS index
   │   Find top-K similar documents
   │
   └─► Retrieve document chunks
       4 most relevant pieces
   
5. LLM GENERATION
   │
   ├─► Build prompt with:
   │   - Conversation history (last 3 exchanges)
   │   - Retrieved context (4 documents)
   │   - User question
   │
   ├─► Send to GROQ API
   │   Model: llama-3.3-70b-versatile
   │
   └─► Get response
       "RAG (Retrieval Augmented Generation) is..."
   
6. POST-PROCESSING
   │
   ├─► Add to conversation history
   │   (question, answer) → chat_history
   │
   ├─► Format sources
   │   Extract metadata, truncate content
   │
   └─► Return to user
       - Answer text
       - Source citations
       - Session ID
```


## Document Ingestion Flow

```
1. DOCUMENT INPUT
   │
   ├─► Web UI Upload
   │   User drags PDF → /api/upload
   │
   ├─► API Ingest
   │   POST /api/ingest {"path": "./data"}
   │
   └─► CLI Ingest
       python rag_app.py ingest ./data
   
2. DOCUMENT LOADING
   │
   ├─► Detect file type (.pdf, .txt, .md, .csv)
   │
   ├─► Load with appropriate loader
   │   - PyPDFLoader for PDFs
   │   - TextLoader for TXT
   │   - UnstructuredMarkdownLoader for MD
   │   - CSVLoader for CSV
   │
   └─► Extract text + metadata
       Store source file path
   
3. TEXT SPLITTING
   │
   ├─► RecursiveCharacterTextSplitter
   │   chunk_size=1000, overlap=200
   │
   ├─► Create document chunks
   │   Long doc → [chunk1, chunk2, chunk3...]
   │
   └─► Preserve metadata
       Each chunk knows its source
   
4. EMBEDDING
   │
   ├─► Generate embeddings
   │   HuggingFace: all-MiniLM-L6-v2
   │   Text → Vector (384 dimensions)
   │
   ├─► Create vector representations
   │   "RAG is..." → [0.12, -0.34, 0.56, ...]
   │
   └─► Batch processing
       Efficient for multiple chunks
   
5. VECTOR STORE
   │
   ├─► Add to FAISS index
   │   Store vectors + metadata
   │
   ├─► Save to disk
   │   Persist in vectorstore/
   │
   └─► Ready for retrieval
       Can now search documents
```
