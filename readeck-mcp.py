# Reference: https://benanderson.work/blog/agentic-search-for-dummies/

from typing import TypedDict
from urllib.parse import quote_plus
import requests
from markdownify import markdownify as md
from zeromcp import McpServer, McpToolError
import os

# Environment variables are automatically loaded from .env by pyauto-dotenv
READECK_URL = os.environ.get("READECK_URL", "").strip().rstrip("/")
if not READECK_URL:
    raise ValueError("READECK_URL is not set in environment or .env file")

READECK_TOKEN = os.environ.get("READECK_TOKEN", "").strip()
if not READECK_TOKEN:
    raise ValueError("READECK_TOKEN is not set in environment or .env file")

mcp = McpServer(name="readeck-mcp", version="0.1.0")


class Bookmark(TypedDict):
    id: str
    title: str
    description: str
    url: str


def list_bookmarks(search: str, offset: int, limit: int) -> list[Bookmark]:
    url = f"{READECK_URL}/api/bookmarks?search={quote_plus(search)}&has_errors=false&offset={offset}&limit={limit}"
    response = requests.get(url, headers={"Authorization": f"Bearer {READECK_TOKEN}"})
    response.raise_for_status()
    return response.json()


class SearchResult(TypedDict):
    title: str
    description: str
    document_id: str


def search(query: str, limit: int = 10) -> list[SearchResult]:
    """
    Search the knowledge base for articles that match the query.
    """
    bookmarks = list_bookmarks(query, 0, limit)
    return [
        SearchResult(
            title=bookmark["title"],
            description=bookmark.get("description", ""),
            document_id=bookmark["id"],
        )
        for bookmark in bookmarks
    ]


@mcp.tool
def initial_search(
    keywords: list[str], limit: int = 10
) -> dict[str, list[SearchResult]]:
    """
    Search the knowledge base for articles that match single keywords.
    After completing this initial search you can perform an adjacent_search to find related articles.
    """
    for keyword in keywords:
        if " " in keyword:
            raise McpToolError("Keywords cannot contain spaces")
    return {keyword: search(keyword, limit) for keyword in keywords}


@mcp.tool
def adjacent_search(
    keywords: list[str], limit: int = 10
) -> dict[str, list[SearchResult]]:
    """
    Search the knowledge base for articles that match the keywords.
    The queries should be derived from the initial search result descriptions.
    """
    return {keyword: search(keyword, limit) for keyword in keywords}


class Document(TypedDict):
    content: str
    citation_url: str


@mcp.tool
def read(document_ids: list[str]) -> dict[str, Document]:
    """
    Read an article from the knowledge base. Make sure to use the citation_url to cite the article in your response.
    """
    results = {}
    for document_id in document_ids:
        url = f"{READECK_URL}/api/bookmarks/{document_id}/article"
        response = requests.get(
            url, headers={"Authorization": f"Bearer {READECK_TOKEN}"}
        )
        try:
            response.raise_for_status()
        except requests.HTTPError as x:
            raise McpToolError(x.args[0])
        markdown = md(response.text, strip=["a", "img"])
        results[document_id] = Document(
            content=markdown, citation_url=f"{READECK_URL}/bookmarks/{document_id}"
        )
    return results


if __name__ == "__main__":
    import sys

    # Run in stdio mode by default (for MCP clients)
    # Or use: python readeck-mcp.py serve <host> <port> for HTTP mode
    if len(sys.argv) > 1 and sys.argv[1] == "serve":
        host = sys.argv[2] if len(sys.argv) > 2 else "127.0.0.1"
        port = int(sys.argv[3]) if len(sys.argv) > 3 else 5001
        mcp.serve(host, port)
    else:
        mcp.stdio()
