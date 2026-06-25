"""
Sprint 1: Web Crawler using crawl4ai
Target: rst.edu.eg

Extracts content and saves it as clean Markdown in data/raw_web/
Maintains a crawl_manifest.json with metadata.
"""

import asyncio
import json
import logging
from datetime import datetime
from urllib.parse import urljoin, urlparse
from pathlib import Path
from crawl4ai import AsyncWebCrawler

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import RAW_WEB_DIR, DATA_DIR
from app.logger import get_logger

# ─── Configuration ──────────────────────────────────────────
SEED_URL = "https://rst.edu.eg"
ALLOWED_DOMAIN = "rst.edu.eg"

MANIFEST_PATH = DATA_DIR / "crawl_manifest.json"
MAX_PAGES = 500  # Deep scrape all pages
POLITE_DELAY = 1.5  # Seconds between requests

logger = get_logger(__name__, str(DATA_DIR.parent / "logs" / "crawler.log"))

# ─── Helpers ────────────────────────────────────────────────

def get_filename_from_url(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path.strip("/").replace("/", "_")
    if not path:
        return "index.md"
    return f"{path}.md"

def load_manifest() -> dict:
    if MANIFEST_PATH.exists():
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_manifest(manifest: dict):
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

# ─── Crawler Core ───────────────────────────────────────────

async def crawl_site():
    logger.info(f"Starting crawl for {SEED_URL}")
    RAW_WEB_DIR.mkdir(parents=True, exist_ok=True)
    
    manifest = load_manifest()
    visited = set(manifest.keys())
    to_visit = {SEED_URL}
    crawled_count = 0

    async with AsyncWebCrawler(verbose=True) as crawler:
        while to_visit and crawled_count < MAX_PAGES:
            url = to_visit.pop()
            if url in visited:
                continue

            logger.info(f"Crawling: {url}")
            try:
                # crawl4ai automatically handles extraction and conversion to markdown
                result = await crawler.arun(url=url)
                
                if result.success and result.markdown:
                    # Save markdown content
                    filename = get_filename_from_url(url)
                    filepath = RAW_WEB_DIR / filename
                    
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(result.markdown)
                    
                    # Update manifest
                    manifest[url] = {
                        "file": filename,
                        "title": result.title if hasattr(result, 'title') else "",
                        "crawl_date": datetime.now().isoformat(),
                        "success": True
                    }
                    save_manifest(manifest)
                    visited.add(url)
                    crawled_count += 1
                    
                    # Basic link extraction to find more pages (simplified)
                    if hasattr(result, 'links') and result.links:
                        for link_obj in result.links.get("internal", []):
                            next_url = link_obj.get("href")
                            if next_url and ALLOWED_DOMAIN in next_url and next_url not in visited:
                                to_visit.add(next_url)
                else:
                    logger.warning(f"Failed to extract content from {url}")
                    manifest[url] = {"success": False, "error": result.error_message}
                
            except Exception as e:
                logger.error(f"Error crawling {url}: {str(e)}")
            
            # Polite delay
            await asyncio.sleep(POLITE_DELAY)
            
    logger.info(f"Crawl finished. Processed {crawled_count} pages.")

if __name__ == "__main__":
    asyncio.run(crawl_site())
