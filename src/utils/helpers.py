"""Utility helper functions for RAG application."""

import logging
import sys
from pathlib import Path
from typing import List, Dict, Optional

# Setup logging
def setup_logging(log_level: str = "INFO"):
    """Configure logging for the application."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("rag_app.log")
        ]
    )


def validate_file_path(path: str) -> Optional[Path]:
    """
    Validate and return a Path object.
    
    Args:
        path: Path string to validate
        
    Returns:
        Path object if valid, None otherwise
    """
    try:
        file_path = Path(path)
        if not file_path.exists():
            print(f"❌ Path does not exist: {path}")
            return None
        return file_path
    except Exception as e:
        print(f"❌ Invalid path: {path} - {e}")
        return None


def format_sources(sources: List[Dict]) -> str:
    """
    Format source documents for display.
    
    Args:
        sources: List of source dictionaries
        
    Returns:
        Formatted string representation
    """
    if not sources:
        return "No sources found"
    
    formatted = []
    for i, source in enumerate(sources, 1):
        content = source.get("content", "")[:150]
        metadata = source.get("metadata", {})
        filename = metadata.get("source", "Unknown")
        formatted.append(f"\n{i}. **{filename}**\n   {content}...")
    
    return "".join(formatted)


def print_separator(char: str = "=", length: int = 80) -> None:
    """
    Print a separator line.
    
    Args:
        char: Character to use for separator
        length: Length of separator line
    """
    print(char * length)
