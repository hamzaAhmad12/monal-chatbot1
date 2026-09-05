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
python -m rag ingest
```

## Run the frontend

The frontend is a plain HTML page served by FastAPI. It does not need a separate frontend server, build step, or npm installation.

Start the backend from the project root:

```powershell
python -m uvicorn api:app --reload
```

Open the chatbot in your browser:

```text
http://127.0.0.1:8000/
```

The interface includes the animated matrix background, suggested questions, and a chat composer connected to the `/chat` endpoint. The API documentation is available at `/docs`.

### GitHub Pages

GitHub Pages is static hosting, so it can display the frontend but cannot run the FastAPI chatbot backend. In the repository settings, open **Pages**, choose **Deploy from a branch**, select the `frontend` branch and the `/ (root)` folder, then save. The root `index.html` opens the matrix interface from `frontend/index.html`.

For the chat requests to work on GitHub Pages, the frontend must call the deployed Railway API and that API must allow the GitHub Pages origin through CORS. Opening the Railway URL directly serves both the UI and API without this cross-origin setup.

To call the API directly:

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/chat -Method Post -ContentType "application/json" -Body '{"question":"What is included in the buffet?"}'
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
