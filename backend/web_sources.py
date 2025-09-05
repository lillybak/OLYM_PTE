import os, time, json, hashlib, requests
from typing import Optional, Dict, Any, List

CACHE_BASE = os.path.join("data", "cache")
SNIPPET_DIR = os.path.join(CACHE_BASE, "web_snippets")
os.makedirs(SNIPPET_DIR, exist_ok=True)

def _h(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def _snippet_path(key: str) -> str:
    return os.path.join(SNIPPET_DIR, f"{_h(key)}.json")

def cache_get(key: str, ttl_seconds: int = 86400) -> Optional[Dict[str, Any]]:
    p = _snippet_path(key)
    if not os.path.exists(p):
        return None
    try:
        obj = json.load(open(p, "r"))
        if time.time() - obj.get("fetched_at", 0) < ttl_seconds:
            return obj
    except Exception:
        return None
    return None

def cache_set(key: str, data: Dict[str, Any]) -> None:
    data = dict(data)
    data["fetched_at"] = time.time()
    os.makedirs(SNIPPET_DIR, exist_ok=True)
    with open(_snippet_path(key), "w") as f:
        json.dump(data, f)

def _safe_get(url: str, timeout: float = 2.5, headers: Optional[Dict[str, str]] = None):
    return requests.get(url, timeout=timeout, headers=headers or {"User-Agent": "NPTE-Agent/1.0"})

def _is_relevant_content(content: str, search_query: str, min_relevance_score: int = 2) -> bool:
    """
    Check if the content is relevant to the search query by counting keyword matches.
    Returns True if the content contains enough relevant keywords.
    """
    if not content or not search_query:
        return False
    
    content_lower = content.lower()
    query_words = [word.lower() for word in search_query.split() if len(word) > 3]
    
    # Count how many query words appear in the content
    matches = sum(1 for word in query_words if word in content_lower)
    
    # Consider it relevant if at least min_relevance_score words match
    return matches >= min_relevance_score

def fetch_pubmed_abstract(topic_or_query: str, max_chars: int = 1200, ttl: int = 86400) -> Optional[Dict[str, Any]]:
    cache_key = f"pubmed|{topic_or_query.strip().lower()}"
    hit = cache_get(cache_key, ttl)
    if hit:
        return hit

    # Enhance the search query to be more specific for physical therapy
    enhanced_query = f"{topic_or_query}[Title/Abstract] AND (physical therapy[MeSH Terms] OR rehabilitation[MeSH Terms] OR physiotherapy[Title/Abstract])"
    q = requests.utils.quote(enhanced_query)
    esearch = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmode=json&retmax=3&term={q}&sort=relevance"
    r = _safe_get(esearch)
    if r.status_code != 200:
        return None
    ids = (r.json().get("esearchresult", {}).get("idlist") or [])[:3]
    if not ids:
        return None

    id_str = ",".join(ids)
    esum = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&retmode=json&id={id_str}"
    s = _safe_get(esum)
    if s.status_code != 200:
        return None
    data = s.json().get("result", {})
    docs: List[Dict[str, Any]] = [data[i] for i in ids if i in data]

    for d in docs:
        uid = d.get("uid")
        title = (d.get("title") or "").strip()
        journal = (d.get("fulljournalname") or d.get("source") or "").strip()
        abstract = (d.get("abstract") or d.get("snippet") or "").strip()
        if not abstract:
            efetch = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
            params = {"db": "pubmed", "retmode": "xml", "id": uid}
            try:
                xf = requests.get(efetch, params=params, timeout=2.5)
                if xf.status_code == 200:
                    text = xf.text
                    start = text.find("<AbstractText")
                    if start != -1:
                        close = text.find("</AbstractText>", start)
                        if close != -1:
                            abstract = text[start:close]
                            abstract = abstract.split(">", 1)[-1].replace("</AbstractText", "")
            except Exception:
                pass

        snippet_text = (f"{title}\n\n{journal}\n\n{abstract}".strip() or title)[:max_chars]
        if snippet_text:
            # Check if the content is relevant to the original search query
            if _is_relevant_content(snippet_text, topic_or_query):
                url = f"https://pubmed.ncbi.nlm.nih.gov/{uid}/"
                result = {"url": url, "title": title, "journal": journal, "snippet_text": snippet_text, "source_domain": "pubmed.ncbi.nlm.nih.gov"}
                cache_set(cache_key, result)
                return result
            else:
                print(f"⚠️ PubMed result not relevant enough: {title[:50]}...")

    return None

def fetch_pmc_snippet(pt_query: str, max_chars: int = 1200, ttl: int = 86400, max_results: int = 5) -> Optional[Dict[str, Any]]:
    cache_key = f"pmc|{pt_query.strip().lower()}|{max_results}|all_years"
    hit = cache_get(cache_key, ttl)
    if hit:
        return hit
    base_url = "https://pmc.ncbi.nlm.nih.gov/search/"
    collected: List[Dict[str, str]] = []
    try:
        # Search all years without date filter
        params = {"term": pt_query, "sort": "relevance"}
        r = requests.get(base_url, params=params, timeout=2.5, headers={"User-Agent": "NPTE-Agent/1.0"})
        if r.status_code != 200:
            return None
        text = r.text
        # Crude extraction of multiple titles and links
        idx = 0
        while len(collected) < max_results:
            tpos = text.find('<div class="title">', idx)
            if tpos == -1:
                break
            # find anchor href after title block
            ahref = text.find('href="', tpos, tpos + 600)
            if ahref == -1:
                idx = tpos + 1
                continue
            ahref_start = ahref + 6
            ahref_end = text.find('"', ahref_start)
            if ahref_end == -1:
                idx = tpos + 1
                continue
            url = text[ahref_start:ahref_end]
            # Extract title text
            title_segment = text[tpos:tpos + 600]
            title = title_segment.split('>', 1)[-1].split('<', 1)[0].strip()
            if url and title:
                if url.startswith('/'):
                    full_url = "https://pmc.ncbi.nlm.nih.gov" + url
                else:
                    full_url = url
                # Deduplicate by URL
                if not any(item.get("url") == full_url for item in collected):
                    collected.append({"url": full_url, "title": title})
            idx = tpos + 1
    except Exception:
        pass

    if collected:
        # Build a concise snippet of top titles
        titles = "\n".join([f"- {item['title']}" for item in collected[:max_results]])
        snippet_text = (f"PMC results for: {pt_query}\n\n{titles}")[:max_chars]
        result = {
            "url": collected[0]["url"],
            "title": collected[0]["title"],
            "journal": "PMC (OA subset)",
            "snippet_text": snippet_text,
            "source_domain": "pmc.ncbi.nlm.nih.gov",
        }
        cache_set(cache_key, result)
        return result
    return None

def fetch_ijspt_snippet(query: str, max_chars: int = 1200, ttl: int = 86400) -> Optional[Dict[str, Any]]:
    """
    Fast IJSPT snippet via DuckDuckGo site search, then fetch first result's meta/paragraph.
    Keeps strict timeouts and caches result. For demo use only.
    """
    cache_key = f"ijspt|{query.strip().lower()}"
    hit = cache_get(cache_key, ttl)
    if hit:
        return hit

    try:
        # Step 1: site search
        dq = requests.utils.quote(f"site:ijspt.org {query}")
        search_url = f"https://duckduckgo.com/html/?q={dq}"
        sr = requests.get(search_url, timeout=2.5, headers={"User-Agent": "NPTE-Agent/1.0"})
        if sr.status_code != 200:
            return None
        html = sr.text
        # crude extract first result link
        href_marker = 'class="result__a" href="'
        idx = html.find(href_marker)
        if idx == -1:
            return None
        start = idx + len(href_marker)
        end = html.find('"', start)
        if end == -1:
            return None
        first_url = html[start:end]
        if not first_url.startswith("http"):
            return None

        # Step 2: fetch the page and grab meta description or first paragraph
        pr = requests.get(first_url, timeout=2.5, headers={"User-Agent": "NPTE-Agent/1.0"})
        if pr.status_code != 200:
            return None
        page = pr.text
        title = ""
        t1 = page.find("<title>")
        if t1 != -1:
            t2 = page.find("</title>", t1)
            if t2 != -1:
                title = page[t1+7:t2].strip()
        desc = ""
        # meta description
        md = 'name="description" content="'
        m1 = page.find(md)
        if m1 != -1:
            m2 = page.find('"', m1 + len(md))
            if m2 != -1:
                desc = page[m1+len(md):m2].strip()
        # fallback: first paragraph
        if not desc:
            p1 = page.find("<p>")
            if p1 != -1:
                p2 = page.find("</p>", p1)
                if p2 != -1:
                    desc = page[p1+3:p2].strip()

        snippet = (f"{title}\n\nIJSPT\n\n{desc}".strip() or title)[:max_chars]
        if snippet:
            result = {
                "url": first_url,
                "title": title,
                "journal": "International Journal of Sports Physical Therapy (IJSPT)",
                "snippet_text": snippet,
                "source_domain": "ijspt.org",
            }
            cache_set(cache_key, result)
            return result
    except Exception:
        return None
    return None

def fetch_doaj_snippet(query: str, max_chars: int = 1200, ttl: int = 86400) -> Optional[Dict[str, Any]]:
    api_key = os.getenv("DOAJ_API_KEY")
    if not api_key:
        return None
    cache_key = f"doaj|{query.strip().lower()}"
    hit = cache_get(cache_key, ttl)
    if hit:
        return hit
    try:
        url = "https://doaj.org/api/v2/search/articles/"
        headers = {"Accept": "application/json", "X-API-Key": api_key}
        params = {"q": query, "pageSize": 3}
        r = requests.get(url, params=params, headers=headers, timeout=2.5)
        if r.status_code != 200:
            return None
        js = r.json()
        results = js.get("results") or []
        if not results:
            return None
        first = results[0]
        bib = first.get("bibjson", {})
        title = (bib.get("title") or "").strip()
        journal = (bib.get("journal", {}).get("title") or "").strip()
        abstract = (bib.get("abstract") or "").strip()
        link = ""
        for l in bib.get("link", []):
            if l.get("type") == "fulltext" and l.get("url"):
                link = l["url"]
                break
        snippet = (f"{title}\n\n{journal}\n\n{abstract}".strip() or title)[:max_chars]
        if snippet:
            result = {"url": link or "https://doaj.org", "title": title, "journal": journal or "DOAJ", "snippet_text": snippet, "source_domain": "doaj.org"}
            cache_set(cache_key, result)
            return result
    except Exception:
        return None
    return None

def get_fast_web_snippet(topic: str, mesh_style_query: Optional[str] = None, max_attempts: int = 3) -> Optional[Dict[str, Any]]:
    """
    Try to get web content from APIs with retry limits.
    First attempts to get full article content, falls back to abstracts.
    Returns the first successful result or None if all attempts fail.
    """
    q = mesh_style_query or topic
    print(f"🔍 Searching for: '{q}' (max {max_attempts} attempts)")
    
    # Try PubMed first (most reliable)
    print("📚 Attempt 1/3: PubMed...")
    hit = fetch_pubmed_abstract(q)
    if hit and hit.get("snippet_text"):
        # Double-check relevance before proceeding
        if _is_relevant_content(hit.get("snippet_text", ""), q):
            # Try to get full article content if URL is available
            if hit.get("url"):
                print("📖 Attempting to get full article content...")
                full_content = get_full_article_content(hit["url"])
                if full_content:
                    hit["full_content"] = full_content
                    hit["content_type"] = "full_article"
                    print(f"✅ Found relevant full article in PubMed: {hit.get('title', 'No title')[:50]}...")
                else:
                    hit["content_type"] = "abstract"
                    print(f"✅ Found relevant abstract in PubMed: {hit.get('title', 'No title')[:50]}...")
            else:
                hit["content_type"] = "abstract"
                print(f"✅ Found relevant abstract in PubMed: {hit.get('title', 'No title')[:50]}...")
            return hit
        else:
            print(f"⚠️ PubMed result not relevant enough, trying next source...")
    
    # Try IJSPT second
    print("📚 Attempt 2/3: IJSPT...")
    hit = fetch_ijspt_snippet(q)
    if hit and hit.get("snippet_text"):
        # Try to get full article content if URL is available
        if hit.get("url"):
            print("📖 Attempting to get full article content...")
            full_content = get_full_article_content(hit["url"])
            if full_content:
                hit["full_content"] = full_content
                hit["content_type"] = "full_article"
                print(f"✅ Found full article in IJSPT: {hit.get('title', 'No title')[:50]}...")
            else:
                hit["content_type"] = "abstract"
                print(f"✅ Found abstract in IJSPT: {hit.get('title', 'No title')[:50]}...")
        else:
            hit["content_type"] = "abstract"
            print(f"✅ Found abstract in IJSPT: {hit.get('title', 'No title')[:50]}...")
        return hit
    
    # Try DOAJ third
    print("📚 Attempt 3/3: DOAJ...")
    hit = fetch_doaj_snippet(q)
    if hit and hit.get("snippet_text"):
        # Try to get full article content if URL is available
        if hit.get("url"):
            print("📖 Attempting to get full article content...")
            full_content = get_full_article_content(hit["url"])
            if full_content:
                hit["full_content"] = full_content
                hit["content_type"] = "full_article"
                print(f"✅ Found full article in DOAJ: {hit.get('title', 'No title')[:50]}...")
            else:
                hit["content_type"] = "abstract"
                print(f"✅ Found abstract in DOAJ: {hit.get('title', 'No title')[:50]}...")
        else:
            hit["content_type"] = "abstract"
            print(f"✅ Found abstract in DOAJ: {hit.get('title', 'No title')[:50]}...")
        return hit
    
    # Try PMC as final fallback
    print("📚 Final attempt: PMC...")
    hit = fetch_pmc_snippet(q, max_results=5)
    if hit and hit.get("snippet_text"):
        # Try to get full article content if URL is available
        if hit.get("url"):
            print("📖 Attempting to get full article content...")
            full_content = get_full_article_content(hit["url"])
            if full_content:
                hit["full_content"] = full_content
                hit["content_type"] = "full_article"
                print(f"✅ Found full article in PMC: {hit.get('title', 'No title')[:50]}...")
            else:
                hit["content_type"] = "abstract"
                print(f"✅ Found abstract in PMC: {hit.get('title', 'No title')[:50]}...")
        else:
            hit["content_type"] = "abstract"
            print(f"✅ Found abstract in PMC: {hit.get('title', 'No title')[:50]}...")
        return hit
    
    print("❌ Tried 4 journals and found nothing")
    return None

def get_full_article_content(url: str, max_chars: int = 3000) -> Optional[str]:
    """
    Attempt to fetch full article content from URL for detailed explanations.
    Returns the full text content if available.
    """
    try:
        import requests
        from bs4 import BeautifulSoup
        
        # Try to get the full article content
        response = requests.get(url, timeout=5.0, headers={"User-Agent": "NPTE-Agent/1.0"})
        if response.status_code != 200:
            return None
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Try different selectors for article content
        content_selectors = [
            'article', '.article-content', '.content', '.main-content',
            '.abstract', '.full-text', '.article-body', '.entry-content',
            '[role="main"]', '.post-content', '.article-text'
        ]
        
        article_text = ""
        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                for element in elements:
                    # Get text content, clean it up
                    text = element.get_text(separator=' ', strip=True)
                    if len(text) > 200:  # Only use substantial content
                        article_text += text + "\n\n"
                        break
                if article_text:
                    break
        
        # If no specific selectors worked, try to get all paragraph text
        if not article_text:
            paragraphs = soup.find_all('p')
            for p in paragraphs:
                text = p.get_text(strip=True)
                if len(text) > 50:  # Only substantial paragraphs
                    article_text += text + "\n\n"
        
        # Clean and truncate
        if article_text:
            # Remove excessive whitespace
            article_text = ' '.join(article_text.split())
            # Truncate to max_chars
            if len(article_text) > max_chars:
                article_text = article_text[:max_chars] + "..."
            return article_text
            
    except Exception as e:
        print(f"⚠️ Failed to fetch full article content from {url}: {e}")
        return None
    
    return None



