"""Main RAG Application with CLI interface."""

import sys
import argparse
from pathlib import Path
from typing import Optional

from config import Config
from src import GrokLLM, VectorStoreManager, DocumentProcessor, RAGChain
from src.utils.helpers import (
    setup_logging,
    validate_file_path,
    format_sources,
    print_separator
)


class RAGApplication:
    """Main RAG Application class."""
    
    def __init__(self):
        """Initialize RAG application."""
        setup_logging()
        
        # Initialize components
        self.llm = GrokLLM(
            api_key=Config.GROQ_API_KEY,
            base_url=Config.GROQ_BASE_URL,
            model_name=Config.MODEL_NAME,
            temperature=Config.TEMPERATURE,
            max_tokens=Config.MAX_TOKENS
        )
        
        self.vectorstore_manager = VectorStoreManager(
            vectorstore_path=Config.VECTORSTORE_PATH,
            embedding_model=Config.EMBEDDING_MODEL
        )
        
        self.document_processor = DocumentProcessor(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP
        )
        
        self.rag_chain = RAGChain(
            llm=self.llm,
            vectorstore_manager=self.vectorstore_manager,
            top_k=Config.TOP_K_RESULTS
        )
    
    def ingest_documents(self, path: str) -> bool:
        """
        Ingest documents from file or directory.
        
        Args:
            path: Path to file or directory
            
        Returns:
            True if successful, False otherwise
        """
        file_path = validate_file_path(path)
        if file_path is None:
            return False
        
        print(f"\n📁 Ingesting documents from: {file_path}")
        print_separator("-")
        
        # Load and process documents
        documents = self.document_processor.load_and_process(file_path)
        
        if not documents:
            print("❌ No documents found or processed.")
            return False
        
        # Add to vectorstore
        self.vectorstore_manager.add_documents(documents)
        
        print(f"✅ Successfully ingested {len(documents)} document chunks.")
        return True
    
    def query(self, question: str, show_sources: bool = True) -> None:
        """
        Query the RAG system.
        
        Args:
            question: User question
            show_sources: Whether to show source documents
        """
        print(f"\n❓ Question: {question}")
        print_separator("-")
        
        result = self.rag_chain.query(question)
        
        print(f"\n💡 Answer:\n{result['answer']}")
        
        if show_sources and result['sources']:
            print_separator("-")
            # print("\n📚 Sources:")
            # print(format_sources(result['sources']))
        
        print_separator("=")
    
    def interactive_mode(self) -> None:
        """Run interactive Q&A session."""
        print("\n🤖 RAG Interactive Mode")
        print("Commands: 'exit/quit' to end, 'clear' to reset conversation, 'history' to view chat history")
        print_separator("=")
        
        if not self.vectorstore_manager.is_initialized():
            print("⚠️  Warning: No documents in vectorstore.")
            print("Use 'python rag_app.py ingest <path>' to add documents first.\n")
        
        while True:
            try:
                question = input("\n🔍 Your question: ").strip()
                
                if question.lower() in ["exit", "quit", "q"]:
                    print("\n👋 Goodbye!")
                    break
                
                if question.lower() == "clear":
                    self.rag_chain.clear_history()
                    print("✅ Conversation history cleared!")
                    continue
                
                if question.lower() == "history":
                    self._show_history()
                    continue
                
                if not question:
                    continue
                
                self.query(question, show_sources=True)
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
    
    def _show_history(self) -> None:
        """Display conversation history."""
        if not self.rag_chain.chat_history:
            print("\n📝 No conversation history yet.")
            return
        
        print("\n📝 Conversation History:")
        print_separator("-")
        for i, (q, a) in enumerate(self.rag_chain.chat_history, 1):
            print(f"\n{i}. Q: {q}")
            print(f"   A: {a[:150]}..." if len(a) > 150 else f"   A: {a}")
        print_separator("-")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="RAG Application using Grok API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Ingest documents from data directory
  python rag_app.py ingest ./data
  
  # Ingest a single file
  python rag_app.py ingest ./data/document.pdf
  
  # Ask a question
  python rag_app.py query "What is this document about?"
  
  # Interactive mode
  python rag_app.py interactive
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Ingest command
    ingest_parser = subparsers.add_parser(
        "ingest",
        help="Ingest documents from file or directory"
    )
    ingest_parser.add_argument(
        "path",
        type=str,
        help="Path to file or directory containing documents"
    )
    
    # Query command
    query_parser = subparsers.add_parser(
        "query",
        help="Query the RAG system"
    )
    query_parser.add_argument(
        "question",
        type=str,
        help="Question to ask"
    )
    query_parser.add_argument(
        "--no-sources",
        action="store_true",
        help="Don't show source documents"
    )
    
    # Interactive command
    subparsers.add_parser(
        "interactive",
        help="Start interactive Q&A session"
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize application
    try:
        app = RAGApplication()
    except Exception as e:
        print(f"❌ Failed to initialize application: {e}")
        print("\nMake sure you have:")
        print("1. Created a .env file with GROQ_API_KEY")
        print("2. Installed all required packages")
        sys.exit(1)
    
    # Handle commands
    if args.command == "ingest":
        success = app.ingest_documents(args.path)
        sys.exit(0 if success else 1)
    
    elif args.command == "query":
        app.query(args.question, show_sources=not args.no_sources)
    
    elif args.command == "interactive":
        app.interactive_mode()


if __name__ == "__main__":
    main()
