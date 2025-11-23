"""Document loader and processor for RAG application."""

import logging
from pathlib import Path
from typing import List
from langchain_core.documents import Document
from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
    UnstructuredMarkdownLoader,
    CSVLoader,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Handles document loading and processing."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize DocumentProcessor.
        
        Args:
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )
    
    def load_document(self, file_path: Path) -> List[Document]:
        """
        Load a single document based on file type.
        
        Args:
            file_path: Path to document
            
        Returns:
            List of Document objects
        """
        suffix = file_path.suffix.lower()
        
        try:
            if suffix == ".txt":
                loader = TextLoader(str(file_path), encoding="utf-8")
            elif suffix == ".pdf":
                loader = PyPDFLoader(str(file_path))
            elif suffix in [".md", ".markdown"]:
                loader = UnstructuredMarkdownLoader(str(file_path))
            elif suffix == ".csv":
                loader = CSVLoader(str(file_path))
            else:
                logger.warning(f"Unsupported file type: {suffix}")
                return []
            
            documents = loader.load()
            logger.info(f"Loaded {len(documents)} document(s) from {file_path.name}")
            return documents
            
        except Exception as e:
            logger.error(f"Error loading {file_path}: {e}")
            return []
    
    def load_directory(self, directory_path: Path) -> List[Document]:
        """
        Load all supported documents from a directory.
        
        Args:
            directory_path: Path to directory
            
        Returns:
            List of Document objects
        """
        supported_extensions = [".txt", ".pdf", ".md", ".markdown", ".csv"]
        all_documents = []
        
        if not directory_path.exists():
            logger.error(f"Directory not found: {directory_path}")
            return []
        
        for file_path in directory_path.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                documents = self.load_document(file_path)
                all_documents.extend(documents)
        
        logger.info(f"Loaded {len(all_documents)} total documents from {directory_path}")
        return all_documents
    
    def process_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into chunks.
        
        Args:
            documents: List of Document objects
            
        Returns:
            List of chunked Document objects
        """
        if not documents:
            logger.warning("No documents to process")
            return []
        
        logger.info(f"Processing {len(documents)} documents...")
        chunks = self.text_splitter.split_documents(documents)
        logger.info(f"Created {len(chunks)} chunks")
        return chunks
    
    def load_and_process(self, path: Path) -> List[Document]:
        """
        Load and process documents from file or directory.
        
        Args:
            path: Path to file or directory
            
        Returns:
            List of processed Document chunks
        """
        if path.is_file():
            documents = self.load_document(path)
        elif path.is_dir():
            documents = self.load_directory(path)
        else:
            logger.error(f"Path not found: {path}")
            return []
        
        return self.process_documents(documents)
