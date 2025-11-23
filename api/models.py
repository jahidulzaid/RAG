"""Pydantic models for API requests and responses."""

from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class Source(BaseModel):
    """Source document reference."""
    content: str = Field(..., description="Content snippet from the source")
    metadata: Dict = Field(default_factory=dict, description="Metadata about the source")


class QueryRequest(BaseModel):
    """Request model for query endpoint."""
    question: str = Field(..., description="The user's question")
    session_id: Optional[str] = Field(None, description="Optional session ID for conversation continuity")
    maintain_history: bool = Field(True, description="Whether to save this exchange in conversation history")


class QueryResponse(BaseModel):
    """Response model for query endpoint."""
    answer: str = Field(..., description="The generated answer")
    sources: List[Source] = Field(default_factory=list, description="Source documents used")
    session_id: str = Field(..., description="Session ID for future requests")


class IngestRequest(BaseModel):
    """Request model for ingest endpoint."""
    path: str = Field(..., description="Path to file or directory containing documents")


class IngestResponse(BaseModel):
    """Response model for ingest endpoint."""
    success: bool = Field(..., description="Whether ingestion was successful")
    message: str = Field(..., description="Details about the ingestion")
    documents_processed: int = Field(..., description="Number of document chunks processed")


class HistoryItem(BaseModel):
    """Single item in conversation history."""
    question: str = Field(..., description="The user's question")
    answer: str = Field(..., description="The assistant's answer")


class HistoryResponse(BaseModel):
    """Response model for history endpoint."""
    history: List[HistoryItem] = Field(default_factory=list, description="Conversation history items")
    session_id: str = Field(..., description="Session ID")


class StatusResponse(BaseModel):
    """Response model for status endpoint."""
    status: str = Field(..., description="Server status")
    vectorstore_initialized: bool = Field(..., description="Whether vectorstore is initialized")
    model_name: str = Field(..., description="Current model name")
