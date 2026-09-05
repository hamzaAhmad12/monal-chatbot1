# Monal RAG API

A restaurant AI concierge API for Monal Peshawar. It uses a PDF knowledge base, HuggingFace embeddings, ChromaDB vector search, MMR retrieval, and a Groq chat model to produce grounded answers.

## Setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Add your `GROQ_API_KEY` to `.env`, then build the local vector database:

```powershell
python -m uvicorn api:app --reload
```

The browser chatbot is available at `http://127.0.0.1:8000`. The API documentation is at `/docs`, and clients can send questions directly to `/chat`:

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/chat -Method Post -ContentType "application/json" -Body '{"question":"What is included in the buffet?"}'
```

Railway uses the following start command:

```text
uvicorn api:app --host 0.0.0.0 --port $PORT
```

## Refresh from the Monal website

Run the crawler whenever you want to check for new website information:

```powershell
python -m rag crawl
python -m rag ingest
```

The crawler renders the JavaScript-driven site in headless Chromium, follows same-domain HTML pages, extracts visible content and contact links, records page hashes in `data/website_snapshot.json`, and appends the live website information to `data/The_Monal_Restaurant_Knowledge_Base_Updated.pdf`. It reports added, changed, and removed pages. After installing requirements, install the browser once with `python -m playwright install chromium`. Review the generated PDF before using it as a production source.

The PDF is a prototype knowledge source. Confirm current prices, timings, availability, and contact details with Monal before using this in production.

## Example questions

- What is the address of Monal Peshawar?
- What is included in the buffet?
- Show me vegetarian options.
- What are the cheapest chicken dishes?
