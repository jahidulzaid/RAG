"""RAG Chain implementation."""

import logging
from typing import List, Dict, Any, Tuple
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from src.utils.grok_llm import GrokLLM
from src.utils.vectorstore_manager import VectorStoreManager

logger = logging.getLogger(__name__)


class RAGChain:
    """Retrieval Augmented Generation chain with conversation memory."""
    
    def __init__(
        self,
        llm: GrokLLM,
        vectorstore_manager: VectorStoreManager,
        top_k: int = 4
    ):
        """
        Initialize RAG chain.
        
        Args:
            llm: Grok LLM instance
            vectorstore_manager: Vector store manager
            top_k: Number of documents to retrieve
        """
        self.llm = llm
        self.vectorstore_manager = vectorstore_manager
        self.top_k = top_k
        self.chat_history: List[Tuple[str, str]] = []
        self.chain = self._create_chain()
    
    def _create_chain(self):
        """Create the RAG chain."""
        # Define the prompt template
        template = """You are an AI assistant that answers questions based on the provided context.
Use the following pieces of context to answer the question at the end.
If you don't know the answer based on the context, just say that you don't know, don't try to make up an answer.

For follow-up questions, use the conversation history to understand the full context of what the user is asking.

Conversation History:
{chat_history}

Context:
{context}

Question: {question}

Answer: """
        
        prompt = ChatPromptTemplate.from_template(template)
        
        # Create the chain
        chain = (
            {
                "context": lambda x: self._format_docs(
                    self.vectorstore_manager.similarity_search(
                        self._get_contextualized_question(x["question"]), 
                        k=self.top_k
                    )
                ),
                "question": RunnablePassthrough(),
                "chat_history": lambda x: self._format_chat_history()
            }
            | RunnablePassthrough.assign(
                context=lambda x: x["context"],
                question=lambda x: x["question"],
                chat_history=lambda x: x["chat_history"]
            )
            | prompt
            | self.llm
            | StrOutputParser()
        )
        
        return chain
    
    def _format_docs(self, docs: List[Document]) -> str:
        """Format documents for context."""
        if not docs:
            return "No relevant context found."
        
        formatted = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get("source", "Unknown")
            content = doc.page_content
            formatted.append(f"[Source {i}: {source}]\n{content}")
        
        return "\n\n---\n\n".join(formatted)
    
    def _format_chat_history(self) -> str:
        """Format chat history for the prompt."""
        if not self.chat_history:
            return "No previous conversation."
        
        formatted = []
        for i, (question, answer) in enumerate(self.chat_history[-3:], 1):  # Last 3 exchanges
            formatted.append(f"Q{i}: {question}\nA{i}: {answer}")
        
        return "\n\n".join(formatted)
    
    def _get_contextualized_question(self, question: str) -> str:
        """Get contextualized question based on chat history for better retrieval."""
        if not self.chat_history:
            return question
        
        # For follow-up questions, combine with context from previous question
        # This helps with pronouns like "it", "that", "this", etc.
        last_q, last_a = self.chat_history[-1]
        
        # Check if question seems like a follow-up (contains pronouns or is very short)
        follow_up_indicators = ["it", "this", "that", "they", "them", "what about", "how about", "and"]
        is_follow_up = any(indicator in question.lower() for indicator in follow_up_indicators) or len(question.split()) < 5
        
        if is_follow_up:
            # Combine context for better retrieval
            return f"{last_q} {question}"
        
        return question
    
    def clear_history(self) -> None:
        """Clear conversation history."""
        self.chat_history.clear()
        logger.info("Chat history cleared")
    
    def query(self, question: str, maintain_history: bool = True) -> Dict[str, Any]:
        """
        Query the RAG system.
        
        Args:
            question: User question
            maintain_history: Whether to add this exchange to chat history
            
        Returns:
            Dictionary with answer and retrieved documents
        """
        if not self.vectorstore_manager.is_initialized():
            return {
                "answer": "Error: Vector store not initialized. Please ingest documents first.",
                "sources": []
            }
        
        try:
            # Retrieve relevant documents using contextualized question
            contextualized_q = self._get_contextualized_question(question)
            relevant_docs = self.vectorstore_manager.similarity_search(
                contextualized_q, k=self.top_k
            )
            
            # Generate answer
            answer = self.chain.invoke({"question": question})
            
            # Add to history if requested
            if maintain_history:
                self.chat_history.append((question, answer))
                # Keep only last 5 exchanges to manage context size
                if len(self.chat_history) > 5:
                    self.chat_history = self.chat_history[-5:]
            
            # Extract sources
            sources = [
                {
                    "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                    "metadata": doc.metadata
                }
                for doc in relevant_docs
            ]
            
            return {
                "answer": answer,
                "sources": sources
            }
            
        except Exception as e:
            logger.error(f"Error during query: {e}")
            return {
                "answer": f"Error processing query: {str(e)}",
                "sources": []
            }
    
    def batch_query(self, questions: List[str]) -> List[Dict[str, Any]]:
        """
        Process multiple queries.
        
        Args:
            questions: List of questions
            
        Returns:
            List of results
        """
        return [self.query(q) for q in questions]
