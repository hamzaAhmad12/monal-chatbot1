# Architecture

```mermaid
flowchart TD
    PDF[Monal knowledge base PDF] --> LOAD[PDF loader]
    LOAD --> SPLIT[Text chunking]
    SPLIT --> EMBED[Sentence Transformer embeddings]
    EMBED --> DB[(ChromaDB)]
    USER[API client] --> API[FastAPI API]
    API --> RETRIEVE[MMR retriever]
    DB --> RETRIEVE
    RETRIEVE --> CONTEXT[Relevant chunks]
    CONTEXT --> LLM[Groq LLM]
    LLM --> ANSWER[Grounded answer + evidence]
```

## Components

- `scripts/ingest.py` loads the PDF, splits it into overlapping chunks, embeds those chunks, and writes `data/chroma/`.
- `rag/retriever.py` opens Chroma, retrieves diverse relevant chunks with MMR, and asks Groq to answer strictly from that context.
- `api.py` exposes the `/chat` endpoint and delegates questions to the retriever.

The vector database is generated locally and ignored by Git. Re-run ingestion when the source PDF changes.
