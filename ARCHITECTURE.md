# Architecture

```mermaid
flowchart TD
    PDF[Monal knowledge base PDF] --> LOAD[PDF loader]
    LOAD --> SPLIT[Text chunking]
    SPLIT --> EMBED[Sentence Transformer embeddings]
    EMBED --> DB[(ChromaDB)]
    USER[User] --> UI[Streamlit UI]
    UI --> RETRIEVE[MMR retriever]
    DB --> RETRIEVE
    RETRIEVE --> CONTEXT[Relevant chunks]
    CONTEXT --> LLM[Groq LLM]
    LLM --> ANSWER[Grounded answer + evidence]
```

## Components

- `scripts/ingest.py` loads the PDF, splits it into overlapping chunks, embeds those chunks, and writes `data/chroma/`.
- `rag/retriever.py` opens Chroma, retrieves diverse relevant chunks with MMR, and asks Groq to answer strictly from that context.
- `app.py` provides the Streamlit interface and displays the source pages returned by retrieval.

The vector database is generated locally and ignored by Git. Re-run ingestion when the source PDF changes.
