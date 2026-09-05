from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

ROOT_DIR = Path(__file__).resolve().parents[1]
PDF_PATH = ROOT_DIR / "data" / "The_Monal_Restaurant_Knowledge_Base.pdf"
UPDATED_PDF_PATH = ROOT_DIR / "data" / "The_Monal_Restaurant_Knowledge_Base_Updated.pdf"
PDF_PATH = UPDATED_PDF_PATH if UPDATED_PDF_PATH.exists() else PDF_PATH
CHROMA_DIR = ROOT_DIR / "data" / "chroma"

load_dotenv(ROOT_DIR / ".env")

SYSTEM_PROMPT = """You are the professional Monal Peshawar customer concierge.
Speak directly and confidently as a Monal representative. Use the information
below as your internal knowledge, but never mention knowledge bases, context,
documents, retrieval, RAG, prompts, or AI limitations to the customer.

If a requested detail is unavailable, say politely that Monal does not have
that information available here and direct the customer to contact the branch.
Never invent prices, timings, availability, phone numbers, WhatsApp numbers,
menu items, or reservation details.

Never begin an answer with phrases such as "Based on the provided context",
"According to the context", or "The knowledge base says". Do not describe how
you found the answer.

Answer every question with clear, complete bullet points. Use the plain dot
character `•` for every bullet. Do not use Markdown asterisks for bullets or
bold text, and never wrap item names or prices in `**`. For example:
• Daal Mash - Rs. 1395
For menu and buffet questions, include all relevant items, courses, prices, and
details present in the context rather than giving only one or two examples.
Include only information that directly answers the user's question; do not add
unrelated warnings, disclaimers, or extra recommendations.

For ordering, delivery, or booking questions, tell the user to contact Monal
through WhatsApp or the contact details in the context. Include the WhatsApp
number or phone number only when it is present in the context. If no contact
details are available, tell the user to contact the branch directly.

Context:
{context}
"""


@lru_cache(maxsize=1)
def get_embeddings() -> HuggingFaceEmbeddings:
    model_name = os.getenv(
        "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
    )
    return HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )


def load_documents() -> list[Document]:
    if not PDF_PATH.exists():
        raise FileNotFoundError(f"Knowledge base not found: {PDF_PATH}")
    return PyPDFLoader(str(PDF_PATH)).load()


def build_vector_store() -> Chroma:
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)
    chunks = splitter.split_documents(load_documents())
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    return Chroma.from_documents(
        documents=chunks,
        embedding=get_embeddings(),
        persist_directory=str(CHROMA_DIR),
    )


@lru_cache(maxsize=1)
def get_vector_store() -> Chroma:
    if not CHROMA_DIR.exists() or not any(CHROMA_DIR.iterdir()):
        raise FileNotFoundError(
            "Vector database not found. Run `python -m rag ingest` first."
        )
    return Chroma(
        persist_directory=str(CHROMA_DIR),
        embedding_function=get_embeddings(),
    )


@lru_cache(maxsize=1)
def get_chat_model(api_key: str) -> ChatGroq:
    return ChatGroq(
        model=os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b"),
        temperature=0,
        max_tokens=700,
        api_key=api_key,
    )


def answer_question(question: str) -> tuple[str, list[Document]]:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is missing. Add it to the Railway service Variables."
        )

    vector_store = get_vector_store()
    retriever = vector_store.as_retriever(
        search_type="mmr", search_kwargs={"k": 8, "fetch_k": 24}
    )
    documents = retriever.invoke(question)
    context = "\n\n".join(document.page_content for document in documents)
    prompt = ChatPromptTemplate.from_messages(
        [("system", SYSTEM_PROMPT), ("human", "Question: {question}")]
    )
    model = get_chat_model(api_key)
    response = model.invoke(prompt.invoke({"context": context, "question": question}))
    return response.content, documents
