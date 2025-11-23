"""Custom GROQ LLM wrapper for LangChain."""

from langchain_groq import ChatGroq


class GrokLLM(ChatGroq):
    """Custom LangChain LLM wrapper for GROQ API."""
    
    def __init__(self, api_key: str, base_url: str = "", model_name: str = "llama-3.3-70b-versatile", 
                 temperature: float = 0.7, max_tokens: int = 2048, **kwargs):
        """Initialize GROQ LLM."""
        super().__init__(
            api_key=api_key,
            model=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
