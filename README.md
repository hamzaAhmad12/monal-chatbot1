# Monal RAG Prototype

A portfolio-ready restaurant AI concierge for Monal Peshawar. It uses a PDF knowledge base, HuggingFace embeddings, ChromaDB vector search, MMR retrieval, and a Groq chat model to produce grounded answers with retrieved evidence.

## Setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Add your `GROQ_API_KEY` to `.env`, then build the local vector database:

```powershell
python -m rag ingest
streamlit run app.py
```

## Refresh from the Monal website

Run the crawler whenever you want to check for new website information:

```powershell
python -m rag crawl
python -m rag ingest
```

The crawler renders the JavaScript-driven site in headless Chromium, follows same-domain HTML pages, extracts visible content and contact links, records page hashes in `data/website_snapshot.json`, and appends the live website information to `data/The_Monal_Restaurant_Knowledge_Base_Updated.pdf`. It reports added, changed, and removed pages. After installing requirements, install the browser once with `python -m playwright install chromium`. Review the generated PDF before using it as a production source.

## Terminal chat

After the vector database has been created, you can use the RAG assistant directly in a terminal:

```powershell
python -m rag chat
```

Type a question at `You:` and enter `exit` or `quit` to stop. Use the same virtual environment and `.env` file as the Streamlit app.

The PDF is a prototype knowledge source. Confirm current prices, timings, availability, and contact details with Monal before using this in production.

## Example questions

- What is the address of Monal Peshawar?
- What is included in the buffet?
- Show me vegetarian options.
- What are the cheapest chicken dishes?
