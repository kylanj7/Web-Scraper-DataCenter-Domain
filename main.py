import os
import re
import csv
import time
import json
import math
import queue
import hashlib
import logging
import pathlib
import urllib.parse
import urllib.robotparser as robotparser
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

import requests
from PyPDF2 import PdfReader

# ------------ Config ------------
USER_AGENT = "PublicPDFScraper/1.0 (+compatible; contact=webmaster@example.com)"
OUT_DIR = "public_pdfs"
MANIFEST_CSV = "manifest.csv"
LOG_FILE = "scrape.log"

# Global rate limit (requests per minute)
REQUESTS_PER_MIN = 10
SECONDS_PER_REQUEST = max(6.0, 60.0 / max(1, REQUESTS_PER_MIN))

# Per-domain politeness delay
PER_DOMAIN_DELAY = 10.0  # seconds between hits to the same domain

# Bing Web Search API (recommended) – set env var BING_API_KEY
BING_ENDPOINT = "https://api.bing.microsoft.com/v7.0/search"

# Conservative license allow/deny patterns
PERMISSIVE_LICENSE_PATTERNS = re.compile(
    r"(creative\s+commons|cc[-\s]?by|cc[-\s]?by[-\s]?sa|public\s+domain|"
    r"open\s+government\s+licen[cs]e|u\.?s\.?\s+government\s+work|17\s*usc\s*105)",
    re.IGNORECASE,
)
RESTRICTIVE_PATTERNS = re.compile(
    r"(all\s+rights\s+reserved|no\s+reproduction|no\s+redistribution|©|copyright\s+\d{4})",
    re.IGNORECASE,
)

# Optional safe allowlist behavior: treat these TLDs as "likely public" unless headers prohibit
LIKELY_PUBLIC_TLDS = (".gov", ".mil", ".eu", ".int")

# ------------ Setup ------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ],
)

os.makedirs(OUT_DIR, exist_ok=True)

# ------------ Utilities ------------
def domain_of(url: str) -> str:
    return urllib.parse.urlparse(url).netloc.lower()

def tld_is_likely_public(netloc: str) -> bool:
    return any(netloc.endswith(tld) for tld in LIKELY_PUBLIC_TLDS)

def sha256_of_bytes(data: bytes) -> str:
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()

def sanitize_filename(name: str) -> str:
    name = re.sub(r"[^\w\-.]+", "_", name)
    return name[:150]

# ------------ Robots handling ------------
class RobotsCache:
    def __init__(self, user_agent: str):
        self.user_agent = user_agent
        self.cache: Dict[str, robotparser.RobotFileParser] = {}

    def can_fetch(self, url: str) -> bool:
        parsed = urllib.parse.urlparse(url)
        base = f"{parsed.scheme}://{parsed.netloc}"
        if base not in self.cache:
            rp = robotparser.RobotFileParser()
            robots_url = urllib.parse.urljoin(base, "/robots.txt")
            try:
                rp.set_url(robots_url)
                rp.read()
                self.cache[base] = rp
            except Exception as e:
                logging.warning(f"robots.txt fetch failed for {base}: {e}")
                # Fail closed: if robots can't be read, be conservative and block
                return False
        rp = self.cache[base]
        return rp.can_fetch(self.user_agent, url)

# ------------ Rate limiting ------------
class RateLimiter:
    def __init__(self, min_interval: float):
        self.min_interval = float(min_interval)
        self.last_time = 0.0

    def wait(self):
        now = time.time()
        delta = now - self.last_time
        if delta < self.min_interval:
            time.sleep(self.min_interval - delta)
        self.last_time = time.time()

class PerDomainLimiter:
    def __init__(self, delay: float):
        self.delay = float(delay)
        self.last_hit: Dict[str, float] = defaultdict(lambda: 0.0)

    def wait(self, netloc: str):
        now = time.time()
        delta = now - self.last_hit[netloc]
        if delta < self.delay:
            time.sleep(self.delay - delta)
        self.last_hit[netloc] = time.time()

# ------------ HTTP ------------
session = requests.Session()
session.headers.update({"User-Agent": USER_AGENT, "Accept": "*/*"})

global_rl = RateLimiter(SECONDS_PER_REQUEST)
domain_rl = PerDomainLimiter(PER_DOMAIN_DELAY)
robots_cache = RobotsCache(USER_AGENT)

def safe_get(url: str, stream: bool = False, allow_redirects: bool = True) -> Optional[requests.Response]:
    if not robots_cache.can_fetch(url):
        logging.info(f"Robots disallow: {url}")
        return None
    netloc = domain_of(url)
    domain_rl.wait(netloc)
    global_rl.wait()
    try:
        resp = session.get(url, timeout=30, stream=stream, allow_redirects=allow_redirects)
        return resp
    except Exception as e:
        logging.warning(f"GET failed {url}: {e}")
        return None

# ------------ Licensing checks ------------
def headers_forbid_use(resp: requests.Response) -> bool:
    # Respect X-Robots-Tag = noindex/noarchive/noai etc.
    xr = resp.headers.get("X-Robots-Tag", "") + "," + resp.headers.get("x-robots-tag", "")
    if xr:
        tags = xr.lower()
        if any(tag in tags for tag in ["noindex", "noarchive", "noai", "nofollow", "none"]):
            return True
    # Also respect standard robots meta via header (rare for PDFs, but be cautious)
    return False

def text_looks_permissive(text: str) -> bool:
    return bool(PERMISSIVE_LICENSE_PATTERNS.search(text))

def text_looks_restrictive(text: str) -> bool:
    return bool(RESTRICTIVE_PATTERNS.search(text))

def pdf_text_preview(pdf_bytes: bytes, max_pages: int = 2) -> str:
    # Extract minimal text to check licensing cues
    try:
        reader = PdfReader(io_bytes := pdf_bytes)
    except Exception:
        # Fallback: write to temp for PyPDF2
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=True) as tmp:
            tmp.write(pdf_bytes)
            tmp.flush()
            reader = PdfReader(tmp.name)
    pages = []
    for i, page in enumerate(reader.pages[:max_pages]):
        try:
            pages.append(page.extract_text() or "")
        except Exception:
            pages.append("")
    return "\n".join(pages)

def is_public_enough(url: str, resp: requests.Response, pdf_bytes: bytes, netloc: str) -> Tuple[bool, str]:
    """
    Very conservative policy:
    - Reject if headers include restrictive X-Robots-Tag (noindex/noarchive/noai)
    - Prefer allow if page text mentions permissive license (CC/Public Domain/etc.)
    - If domain is likely public (.gov/.mil/.eu/.int) and text is NOT explicitly restrictive, allow
    - Otherwise, reject if we see restrictive language (©/All rights reserved)
    - If no signal either way, default to REJECT (conservative)
    """
    if headers_forbid_use(resp):
        return (False, "Rejected: X-Robots-Tag forbids indexing/AI")

    preview = pdf_text_preview(pdf_bytes, max_pages=2)
    if text_looks_permissive(preview):
        return (True, "Accepted: permissive license detected in text")

    if tld_is_likely_public(netloc):
        if text_looks_restrictive(preview):
            return (False, "Rejected: restrictive language on likely-public domain")
        return (True, "Accepted: likely public TLD and no restrictive language found")

    # If explicit restrictive phrasing is present, reject
    if text_looks_restrictive(preview):
        return (False, "Rejected: restrictive licensing language found")

    return (False, "Rejected: no permissive license signal (conservative default)")

# ------------ Discovery ------------
def discover_via_bing(query: str) -> List[str]:
    key = os.environ.get("BING_API_KEY", "").strip()
    if not key:
        logging.warning("BING_API_KEY not set; skipping Bing discovery for query: %s", query)
        return []
    params = {
        "q": f'filetype:pdf "{query}"',
        "count": 30,
        "textDecorations": False,
        "textFormat": "Raw",
        "responseFilter": "Webpages",
        "mkt": "en-US",
        "safeSearch": "Moderate",
    }
    headers = {"Ocp-Apim-Subscription-Key": key}
    global_rl.wait()
    try:
        r = session.get(BING_ENDPOINT, params=params, headers=headers, timeout=30)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        logging.warning(f"Bing search failed for '{query}': {e}")
        return []

    urls = []
    for w in (data.get("webPages") or {}).get("value", []):
        url = w.get("url", "")
        if url.lower().endswith(".pdf"):
            urls.append(url)
    return urls

def crawl_for_pdfs(seed_url: str) -> List[str]:
    # Fetch HTML and extract direct .pdf links on the page
    resp = safe_get(seed_url, stream=False)
    if not resp or not (200 <= resp.status_code < 300):
        return []
    ctype = resp.headers.get("Content-Type", "").lower()
    if "text/html" not in ctype:
        return []
    try:
        html = resp.text
    except Exception:
        return []
    pdf_links = set()
    for m in re.finditer(r'href=["\']([^"\']+\.pdf)(\?[^"\']*)?["\']', html, flags=re.IGNORECASE):
        href = m.group(0)  # full match
        url = m.group(1)
        full = urllib.parse.urljoin(resp.url, url)
        pdf_links.add(full)
    return list(pdf_links)

# ------------ Download & Save ------------
def save_pdf(url: str, content: bytes) -> str:
    # Name by hash + slug of file
    hash_prefix = sha256_of_bytes(content)[:12]
    slug = sanitize_filename(pathlib.Path(urllib.parse.urlparse(url).path).name or "document.pdf")
    fname = f"{hash_prefix}__{slug}"
    path = os.path.join(OUT_DIR, fname)
    with open(path, "wb") as f:
        f.write(content)
    return path

def record_manifest(row: Dict[str, str]):
    file_exists = os.path.exists(MANIFEST_CSV)
    with open(MANIFEST_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "timestamp",
                "source_url",
                "status",
                "reason",
                "http_status",
                "content_type",
                "saved_path",
                "sha256",
            ],
        )
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

# ------------ Main ------------
def main():
    try:
        import SearchTerms  # your list lives here
        SEARCH_TERMS = getattr(SearchTerms, "SEARCH_TERMS", [])
        ALLOWED_DOMAINS = [d.lower() for d in getattr(SearchTerms, "ALLOWED_DOMAINS", [])]
        SEED_URLS = getattr(SearchTerms, "SEED_URLS", [])
    except Exception as e:
        logging.error("Could not import SearchTerms.py: %s", e)
        return

    if not SEARCH_TERMS and not SEED_URLS:
        logging.error("No SEARCH_TERMS and no SEED_URLS provided. Nothing to do.")
        return

    seen_urls = set()

    # 1) Query via Bing API (if configured)
    for term in SEARCH_TERMS:
        for url in discover_via_bing(term):
            seen_urls.add(url)

    # 2) Crawl provided seed pages for .pdf links
    for seed in SEED_URLS:
        for url in crawl_for_pdfs(seed):
            seen_urls.add(url)

    if not seen_urls:
        logging.info("No candidate PDF URLs discovered. Exiting.")
        return

    logging.info("Discovered %d candidate PDF URLs.", len(seen_urls))

    # Filter by allowed domains, if specified
    if ALLOWED_DOMAINS:
        filtered = set()
        for u in seen_urls:
            net = domain_of(u)
            if any(net.endswith(x) or net == x.lstrip(".") for x in ALLOWED_DOMAINS):
                filtered.add(u)
        seen_urls = filtered
        logging.info("After domain filter, %d URLs remain.", len(seen_urls))

    for url in sorted(seen_urls):
        ts = datetime.utcnow().isoformat()
        try:
            # HEAD first (if allowed) to check content type and robots
            head_resp = safe_get(url, stream=False, allow_redirects=True)
            if not head_resp:
                record_manifest({
                    "timestamp": ts,
                    "source_url": url,
                    "status": "skipped",
                    "reason": "robots_disallow_or_request_failed",
                    "http_status": "",
                    "content_type": "",
                    "saved_path": "",
                    "sha256": "",
                })
                continue

            status = head_resp.status_code
            ctype = head_resp.headers.get("Content-Type", "").lower()

            if not (200 <= status < 400):
                record_manifest({
                    "timestamp": ts, "source_url": url, "status": "skipped",
                    "reason": f"http_{status}", "http_status": str(status),
                    "content_type": ctype, "saved_path": "", "sha256": "",
                })
                continue

            if "pdf" not in ctype and not url.lower().endswith(".pdf"):
                record_manifest({
                    "timestamp": ts, "source_url": url, "status": "skipped",
                    "reason": "not_pdf", "http_status": str(status),
                    "content_type": ctype, "saved_path": "", "sha256": "",
                })
                continue

            if headers_forbid_use(head_resp):
                record_manifest({
                    "timestamp": ts, "source_url": url, "status": "skipped",
                    "reason": "x-robots-tag_forbids", "http_status": str(status),
                    "content_type": ctype, "saved_path": "", "sha256": "",
                })
                continue

            # GET the PDF
            get_resp = safe_get(url, stream=True, allow_redirects=True)
            if not get_resp or not (200 <= get_resp.status_code < 300):
                record_manifest({
                    "timestamp": ts, "source_url": url, "status": "skipped",
                    "reason": "get_failed", "http_status": str(get_resp.status_code if get_resp else ""),
                    "content_type": get_resp.headers.get("Content-Type", "") if get_resp else "",
                    "saved_path": "", "sha256": "",
                })
                continue

            if "application/pdf" not in get_resp.headers.get("Content-Type", "").lower() and not url.lower().endswith(".pdf"):
                record_manifest({
                    "timestamp": ts, "source_url": url, "status": "skipped",
                    "reason": "not_pdf_after_get", "http_status": str(get_resp.status_code),
                    "content_type": get_resp.headers.get("Content-Type", ""),
                    "saved_path": "", "sha256": "",
                })
                continue

            # Read bytes (streamed)
            content = b""
            try:
                for chunk in get_resp.iter_content(chunk_size=1024 * 64):
                    if chunk:
                        content += chunk
                        # soft limit: avoid huge files (e.g., > 40 MB)
                        if len(content) > 40 * 1024 * 1024:
                            raise RuntimeError("file_too_large")
            except Exception as e:
                record_manifest({
                    "timestamp": ts, "source_url": url, "status": "skipped",
                    "reason": f"stream_error:{e}", "http_status": str(get_resp.status_code),
                    "content_type": get_resp.headers.get("Content-Type", ""),
                    "saved_path": "", "sha256": "",
                })
                continue

            netloc = domain_of(url)
            allowed, reason = is_public_enough(url, get_resp, content, netloc)
            if not allowed:
                record_manifest({
                    "timestamp": ts, "source_url": url, "status": "rejected",
                    "reason": reason, "http_status": str(get_resp.status_code),
                    "content_type": get_resp.headers.get("Content-Type", ""),
                    "saved_path": "", "sha256": sha256_of_bytes(content),
                })
                continue

            saved = save_pdf(url, content)
            record_manifest({
                "timestamp": ts, "source_url": url, "status": "saved",
                "reason": reason, "http_status": str(get_resp.status_code),
                "content_type": get_resp.headers.get("Content-Type", ""),
                "saved_path": saved, "sha256": sha256_of_bytes(content),
            })
            logging.info(f"Saved: {saved}  ({reason})")

        except Exception as e:
            logging.exception(f"Unhandled error for {url}: {e}")
            record_manifest({
                "timestamp": ts, "source_url": url, "status": "error",
                "reason": str(e), "http_status": "", "content_type": "",
                "saved_path": "", "sha256": "",
            })

if __name__ == "__main__":
    main()
