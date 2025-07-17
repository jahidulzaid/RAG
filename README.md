# 🚀 Simple RAG from Scratch

This implements a minimalist Retrieval-Augmented Generation (RAG) pipeline in Python using Ollama, compatible with open-source LLMs and embeddings.

---

## ✨ Key Concepts

- **RAG** combines:
  1. **Retrieval** – using embeddings to find relevant text chunks.
  2. **Generation** – feeding retrieved chunks to a language model to answer queries. 

- Components:
  - Embedding model (e.g. `bge-base-en-v1.5`)
  - Simple in-memory vector store
  - LLM for generation (e.g. `Llama-3.2-1B-Instruct`)

---

## 📚 Prerequisites

- [Ollama CLI & Python SDK](https://ollama.com)
- Pretrained models:
  ```bash
  ollama pull hf.co/CompendiumLabs/bge-base-en-v1.5-gguf
  ollama pull hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF

  ```bash
  pip install ollama


  ```bash
  python Basic_RAG.py

### You need to run those in an env ( Conda Suggested)
