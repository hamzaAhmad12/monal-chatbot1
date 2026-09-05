from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from rag.retriever import CHROMA_DIR, answer_question

app = FastAPI(title="Monal Peshawar Chatbot", version="1.0.0")
FRONTEND_PATH = Path(__file__).resolve().parent / "frontend" / "index.html"


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)


class ChatResponse(BaseModel):
    answer: str


@app.get("/")
def root() -> FileResponse:
    return FileResponse(FRONTEND_PATH, media_type="text/html")


@app.get("/health")
def health() -> dict[str, object]:
    vector_store_ready = CHROMA_DIR.exists() and any(CHROMA_DIR.iterdir())
    return {
        "status": "ok",
        "groq_api_key_configured": bool(os.getenv("GROQ_API_KEY")),
        "vector_store_ready": vector_store_ready,
    }


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    try:
        answer, _ = answer_question(request.question.strip())
    except (FileNotFoundError, RuntimeError) as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail="The AI service could not answer right now.",
        ) from error
    return ChatResponse(answer=answer)