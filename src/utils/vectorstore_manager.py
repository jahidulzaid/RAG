"""Vector store manager for RAG application."""

import logging
from pathlib import Path
from typing import List, Optional
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document

logger = logging.getLogger(__name__)


class VectorStoreManager:
    """Manages vector store operations for document retrieval."""
    
    def __init__(
        self,
        vectorstore_path: Path,
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    ):
        """
        Initialize VectorStoreManager.
        
        Args:
            vectorstore_path: Path to store/load vector database
            embedding_model: HuggingFace embedding model name
        """
        self.vectorstore_path = vectorstore_path
        self.embedding_model = embedding_model
        self.embeddings = HuggingFaceEmbeddings(model_name=embedding_model)
        self.vectorstore: Optional[FAISS] = None
        
        # Try to load existing vectorstore
        self._load_vectorstore()
    
    def _load_vectorstore(self) -> None:
        """Load existing vectorstore from disk."""
        index_path = self.vectorstore_path / "index.faiss"
        if index_path.exists():
            try:
                self.vectorstore = FAISS.load_local(
                    str(self.vectorstore_path),
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                logger.info(f"Loaded existing vectorstore from {self.vectorstore_path}")
            except Exception as e:
                logger.warning(f"Failed to load vectorstore: {e}")
                self.vectorstore = None
    
    def create_vectorstore(self, documents: List[Document]) -> None:
        """
        Create new vectorstore from documents.
        
        Args:
            documents: List of LangChain Document objects
        """
        if not documents:
            raise ValueError("Cannot create vectorstore from empty documents list")
        
        logger.info(f"Creating vectorstore with {len(documents)} documents...")
        self.vectorstore = FAISS.from_documents(documents, self.embeddings)
        self.save_vectorstore()
        logger.info("Vectorstore created successfully")
    
    def add_documents(self, documents: List[Document]) -> None:
        """
        Add documents to existing vectorstore.
        
        Args:
            documents: List of LangChain Document objects
        """
        if not documents:
            logger.warning("No documents to add")
            return
        
        if self.vectorstore is None:
            self.create_vectorstore(documents)
        else:
            logger.info(f"Adding {len(documents)} documents to vectorstore...")
            self.vectorstore.add_documents(documents)
            self.save_vectorstore()
            logger.info("Documents added successfully")
    
    def save_vectorstore(self) -> None:
        """Save vectorstore to disk."""
        if self.vectorstore is None:
            logger.warning("No vectorstore to save")
            return
        
        self.vectorstore_path.mkdir(parents=True, exist_ok=True)
        self.vectorstore.save_local(str(self.vectorstore_path))
        logger.info(f"Vectorstore saved to {self.vectorstore_path}")
    
    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        """
        Perform similarity search on vectorstore.
        
        Args:
            query: Search query
            k: Number of results to return
            
        Returns:
            List of relevant documents
        """
        if self.vectorstore is None:
            logger.error("Vectorstore not initialized")
            return []
        
        results = self.vectorstore.similarity_search(query, k=k)
        logger.info(f"Found {len(results)} relevant documents for query")
        return results
    
    def is_initialized(self) -> bool:
        """Check if vectorstore is initialized."""
        return self.vectorstore is not None



