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

### Deploy the frontend on Vercel

Import the `frontend` branch into Vercel. This is a plain static HTML/CSS/JavaScript frontend, not a Vite, React, or Next.js project. No build command, package installation, or environment variable is required. Set the project Root Directory to `frontend`.

Use these Vercel settings:

```text
Framework Preset: Other
Build Command: leave empty
Output Directory: leave empty
Install Command: leave empty
Root Directory: frontend
```

If deploying with the Vercel CLI, run it from the frontend directory or pass the directory explicitly:

```powershell
vercel --cwd frontend --prod
```

Run the Vercel command from the `frontend` directory so Vercel only sees the static frontend files.

After deployment, open the Vercel project URL. To connect it to a separately hosted backend, define `window.MONAL_API_URL` before the frontend script runs, or replace the empty API base in `frontend/index.html` with that backend URL.

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
