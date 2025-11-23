"""FastAPI application for RAG system."""

import uuid
import logging
from typing import Dict, Optional
from pathlib import Path
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import Config

from src import GrokLLM, VectorStoreManager, DocumentProcessor, RAGChain
from api.models import (
    QueryRequest,
    QueryResponse,
    IngestRequest,
    IngestResponse,
    HistoryResponse,
    HistoryItem,
    StatusResponse,
    Source
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="RAG API with GROQ",
    description="Retrieval Augmented Generation API using GROQ and LangChain",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session storage for multiple users
sessions: Dict[str, RAGChain] = {}

# Shared components
llm: Optional[GrokLLM] = None
vectorstore_manager: Optional[VectorStoreManager] = None
document_processor: Optional[DocumentProcessor] = None


@app.on_event("startup")
async def startup_event():
    """Initialize components on startup."""
    global llm, vectorstore_manager, document_processor
    
    try:
        logger.info("Initializing RAG components...")
        
        llm = GrokLLM(
            api_key=Config.GROQ_API_KEY,
            base_url=Config.GROQ_BASE_URL,
            model_name=Config.MODEL_NAME,
            temperature=Config.TEMPERATURE,
            max_tokens=Config.MAX_TOKENS
        )
        
        vectorstore_manager = VectorStoreManager(
            vectorstore_path=Config.VECTORSTORE_PATH,
            embedding_model=Config.EMBEDDING_MODEL
        )
        
        document_processor = DocumentProcessor(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP
        )
        
        logger.info("RAG components initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize components: {e}")
        raise


def get_or_create_session(session_id: Optional[str] = None) -> tuple[str, RAGChain]:
    """Get existing session or create new one."""
    if session_id and session_id in sessions:
        return session_id, sessions[session_id]
    
    if llm is None or vectorstore_manager is None:
        raise RuntimeError("Components not initialized")
    
    new_session_id = str(uuid.uuid4())
    sessions[new_session_id] = RAGChain(
        llm=llm,
        vectorstore_manager=vectorstore_manager,
        top_k=Config.TOP_K_RESULTS
    )
    
    logger.info(f"Created new session: {new_session_id}")
    return new_session_id, sessions[new_session_id]


@app.get("/", response_class=FileResponse)
async def root():
    """Serve the frontend."""
    return FileResponse("frontend/index.html")


@app.get("/api/status", response_model=StatusResponse)
async def get_status():
    """Get API status and configuration."""
    if vectorstore_manager is None:
        raise HTTPException(status_code=500, detail="Server not initialized")
    
    return StatusResponse(
        status="online",
        vectorstore_initialized=vectorstore_manager.is_initialized(),
        model_name=Config.MODEL_NAME
    )


@app.post("/api/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """
    Query the RAG system.
    
    - **question**: The user's question
    - **session_id**: Optional session ID for conversation continuity
    - **maintain_history**: Whether to save this exchange in conversation history
    """
    try:
        session_id, rag_chain = get_or_create_session(request.session_id)
        
        # Query the system
        result = rag_chain.query(
            question=request.question,
            maintain_history=request.maintain_history
        )
        
        # Convert sources to proper format
        sources = [
            Source(
                content=src["content"],
                metadata=src["metadata"]
            )
            for src in result["sources"]
        ]
        
        return QueryResponse(
            answer=result["answer"],
            sources=sources,
            session_id=session_id
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ingest", response_model=IngestResponse)
async def ingest_documents(request: IngestRequest):
    """
    Ingest documents from a file or directory path.
    
    - **path**: Path to file or directory containing documents
    """
    try:
        if document_processor is None or vectorstore_manager is None:
            raise HTTPException(status_code=500, detail="Server not initialized")
        
        file_path = Path(request.path)
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"Path not found: {request.path}")
        
        # Load and process documents
        documents = document_processor.load_and_process(file_path)
        
        if not documents:
            return IngestResponse(
                success=False,
                message="No documents found or processed",
                documents_processed=0
            )
        
        # Add to vectorstore
        vectorstore_manager.add_documents(documents)
        
        return IngestResponse(
            success=True,
            message=f"Successfully ingested {len(documents)} document chunks",
            documents_processed=len(documents)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ingesting documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload and ingest a document file.
    
    - **file**: Document file to upload and process
    """
    try:
        if document_processor is None or vectorstore_manager is None:
            raise HTTPException(status_code=500, detail="Server not initialized")
        
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        # Save uploaded file
        upload_dir = Config.DATA_DIR / "uploads"
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = upload_dir / file.filename
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Process the uploaded file
        documents = document_processor.load_and_process(file_path)
        
        if not documents:
            return IngestResponse(
                success=False,
                message="Failed to process uploaded file",
                documents_processed=0
            )
        
        # Add to vectorstore
        vectorstore_manager.add_documents(documents)
        
        return IngestResponse(
            success=True,
            message=f"Successfully uploaded and ingested {len(documents)} chunks from {file.filename}",
            documents_processed=len(documents)
        )
        
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/history/{session_id}", response_model=HistoryResponse)
async def get_history(session_id: str):
    """
    Get conversation history for a session.
    
    - **session_id**: Session identifier
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    rag_chain = sessions[session_id]
    history = [
        HistoryItem(question=q, answer=a)
        for q, a in rag_chain.chat_history
    ]
    
    return HistoryResponse(
        history=history,
        session_id=session_id
    )


@app.delete("/api/history/{session_id}")
async def clear_history(session_id: str):
    """
    Clear conversation history for a session.
    
    - **session_id**: Session identifier
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    sessions[session_id].clear_history()
    
    return {"message": "History cleared", "session_id": session_id}


@app.delete("/api/session/{session_id}")
async def delete_session(session_id: str):
    """
    Delete a session.
    
    - **session_id**: Session identifier
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    del sessions[session_id]
    
    return {"message": "Session deleted", "session_id": session_id}


# Mount static files for frontend assets (CSS, JS, etc.)
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
