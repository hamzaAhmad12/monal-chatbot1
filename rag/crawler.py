from __future__ import annotations

import hashlib
import io
import json
import re
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urldefrag, urljoin, urlparse
from xml.sax.saxutils import escape

from bs4 import BeautifulSoup
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright
from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
SOURCE_PDF = DATA_DIR / "The_Monal_Restaurant_Knowledge_Base.pdf"
UPDATED_PDF = DATA_DIR / "The_Monal_Restaurant_Knowledge_Base_Updated.pdf"
SNAPSHOT_PATH = DATA_DIR / "website_snapshot.json"
TEXT_PATH = DATA_DIR / "website_knowledge.txt"
START_URL = "https://themonal.com/"
SEED_URLS = [START_URL, f"{START_URL}menu", f"{START_URL}reservation", f"{START_URL}mobile-app", f"{START_URL}feedback"]
USER_AGENT = "MonalKnowledgeCrawler/1.0 (+local portfolio project)"


def normalize_url(url: str) -> str | None:
    url, _ = urldefrag(url)
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or parsed.netloc != "themonal.com":
        return None
    path = parsed.path or "/"
    if path.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp", ".css", ".js", ".pdf")):
        return None
    return f"https://themonal.com{path.rstrip('/') or '/'}"


def clean_text(soup: BeautifulSoup) -> str:
    for element in soup(["script", "style", "noscript", "svg"]):
        element.decompose()
    lines = []
    for line in soup.get_text("\n").splitlines():
        line = re.sub(r"\s+", " ", line).strip()
        if line and (not lines or line != lines[-1]):
            lines.append(line)
    return "\n".join(lines)


def extract_contacts(soup: BeautifulSoup, text: str) -> dict[str, list[str]]:
    phones, whatsapp = set(), set()
    emails = set(re.findall(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", text, re.I))
    for anchor in soup.select("a[href]"):
        href = anchor["href"].strip()
        label = re.sub(r"\s+", " ", anchor.get_text(" ", strip=True))
        if href.startswith("tel:"):
            phones.add(label or href.removeprefix("tel:"))
        if "wa.me" in href or "whatsapp" in href.lower():
            whatsapp.add(label or href)
    return {"phones": sorted(phones), "whatsapp": sorted(whatsapp), "emails": sorted(emails)}


def crawl(max_pages: int = 20) -> list[dict[str, object]]:
    queue, visited, pages = deque(SEED_URLS), set(), []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(user_agent=USER_AGENT)
        while queue and len(pages) < max_pages:
            url = normalize_url(queue.popleft())
            if not url or url in visited:
                continue
            visited.add(url)
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                try:
                    page.wait_for_load_state("networkidle", timeout=10000)
                except PlaywrightTimeoutError:
                    pass
            except PlaywrightTimeoutError:
                continue
            soup = BeautifulSoup(page.content(), "html.parser")
            text = clean_text(soup)
            if not text:
                continue
            pages.append({"url": url, "title": soup.title.get_text(strip=True) if soup.title else url, "text": text, "contacts": extract_contacts(soup, text), "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest()})
            for anchor in soup.select("a[href]"):
                next_url = normalize_url(urljoin(url, anchor["href"]))
                if next_url and next_url not in visited:
                    queue.append(next_url)
        browser.close()
    return pages


def crawl_and_update(max_pages: int = 20) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    pages = crawl(max_pages)
    if not pages:
        raise SystemExit("No pages were crawled; the existing knowledge base was not changed.")
    previous = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8")).get("pages", {}) if SNAPSHOT_PATH.exists() else {}
    current = {page["url"]: page["sha256"] for page in pages}
    added = set(current) - set(previous)
    changed = {url for url in set(current) & set(previous) if current[url] != previous[url]}
    removed = set(previous) - set(current)
    SNAPSHOT_PATH.write_text(json.dumps({"crawled_at": datetime.now(timezone.utc).isoformat(), "pages": current}, indent=2), encoding="utf-8")
    TEXT_PATH.write_text("\n\n".join(f"SOURCE: {page['url']}\n{page['text']}" for page in pages), encoding="utf-8")
    styles = getSampleStyleSheet()
    story = [Paragraph("Monal Website Knowledge Update", styles["Title"]), Spacer(1, 0.2 * inch), Paragraph(f"Crawled: {datetime.now(timezone.utc).isoformat()}", styles["Normal"]), PageBreak()]
    for page in pages:
        story.extend([Paragraph(str(page["title"]), styles["Heading1"]), Paragraph(f"Source URL: {page['url']}", styles["Normal"])])
        contacts = page["contacts"]
        story.append(Paragraph("Phones: " + ", ".join(contacts["phones"]) + " | WhatsApp: " + ", ".join(contacts["whatsapp"]) + " | Emails: " + ", ".join(contacts["emails"]), styles["Normal"]))
        for paragraph in str(page["text"]).split("\n"):
            story.append(Paragraph(escape(paragraph), styles["BodyText"]))
        story.append(PageBreak())
    website_pdf = io.BytesIO()
    SimpleDocTemplate(website_pdf, pagesize=A4, rightMargin=0.6 * inch, leftMargin=0.6 * inch, topMargin=0.6 * inch, bottomMargin=0.6 * inch).build(story)
    writer = PdfWriter()
    if SOURCE_PDF.exists():
        for page in PdfReader(str(SOURCE_PDF)).pages:
            writer.add_page(page)
    for page in PdfReader(io.BytesIO(website_pdf.getvalue())).pages:
        writer.add_page(page)
    with UPDATED_PDF.open("wb") as output:
        writer.write(output)
    print(f"Crawled {len(pages)} pages. Added: {len(added)}, changed: {len(changed)}, removed: {len(removed)}")
    print(f"Updated PDF: {UPDATED_PDF}")