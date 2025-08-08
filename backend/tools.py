# -*- coding: utf-8 -*-
import os
import re
import html
import textwrap
from typing import Any, List, Optional
from dotenv import load_dotenv
import requests

from qdrant_client import QdrantClient
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import Qdrant
from pydantic import BaseModel

load_dotenv()



# ⚡ Embedding + Qdrant setup
_qdrant_url = os.getenv("QDRANT_URL")
_qdrant_key = os.getenv("QDRANT_API_KEY")
_qdrant_coll = os.getenv("QDRANT_COLLECTION", "my_knowledge")

emb = OpenAIEmbeddings(model="text-embedding-3-small")

_qdrant_client = QdrantClient(
    url=_qdrant_url,
    api_key=_qdrant_key,
)

_qdrant_store = Qdrant.from_existing_collection(
    client=_qdrant_client,
    collection_name=_qdrant_coll,
    embeddings=emb,
)

def strip_html_tags(text: str) -> str:
    """
    Removes any HTML tags from a snippet and decodes HTML entities.
    Uses a lightweight regex (RFC‑compatible) — suitable for cleaning snippets, not for sanitizing untrusted inputs.
    """
    clean = re.sub(r'<[^<]+?>', '', text)  # Regex strips all <...> tags 💡
    return html.unescape(clean).strip()     # Decode & trim whitespace

def limit_chars(text: str, max_chars: int = 200) -> str:
    """
    Truncates text to the nearest word before max_chars, appending '…' if truncated.
    """
    if len(text) <= max_chars:
        return text
    snippet = textwrap.shorten(text, width=max_chars, placeholder="…")
    return snippet


class RetrieverTool:
    """
    ReAct tool for semantic retrieval from your subject-based Qdrant vector DB.
    Returns the top-N matching snippet(s) as a single string.
    """

    name = "Retriever"
    description = (
        "Returns Q&A snippet from embedding index based on student question"
    )

    def __init__(self, k: int = 3):
        self._retriever = _qdrant_store.as_retriever(
            search_kwargs={"k": k}
        )

    def call(self, question: str) -> str:
        docs = self._retriever.get_relevant_documents(question)
        lines = []
        for idx, doc in enumerate(docs, start=1):
            content = getattr(doc, "page_content", None) or doc.content
            md = getattr(doc, "metadata", {})
            src = md.get("source", "")
            lines.append(f"[{idx}] {content} (← {src})")
        return "\n".join(lines) or "No relevant info found."


class SearchTool:
    """
    ReAct Tool: calls a web search API (e.g. Serper, Tavily).
    Applies best practices:
      1. Limit output to top 2 snippets
      2. Clean HTML
      3. Truncate to ~200 chars
      4. Always include source URL for traceability

    Lightweight fallback that uses a third-party search API.
    Useful when RetrieverTool fails or you need Web-based span-backed reasoning.
    """

    name = "WebSearch"
    description = "Search the web and return top 2 snippet(s) with URLs for factual backup."

    def __init__(self, api_key: str = None):
        self._api_key = api_key or os.getenv("SEARCH_API_KEY")
        if not self._api_key:
            raise RuntimeError("SEARCH_API_KEY not set in .env or environment")
        self.endpoint = "https://api.serper.dev/search"  # Or Tavily

    def call(self, query: str) -> str:
        resp = requests.get(
            self.endpoint,
            params={"q": query, "num": 2},
            headers={"X-API-KEY": self._api_key} # or tavily key
        )
        if not resp.ok:
            return f"Search error: {resp.status_code}"
        data = resp.json().get("queryExpanded")
        return (
            "\n".join([item.get("snippet", "") for item in resp.json().get("items", [])])
            or f"No snippet from query '{query}'"
        )


class ToolCall(BaseModel):
    tool: str
    input: Any

