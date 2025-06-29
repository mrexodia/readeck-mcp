# Reference: https://benanderson.work/blog/agentic-search-for-dummies/

from fastmcp import FastMCP
from pydantic import BaseModel
import argparse
from urllib.parse import urlparse, quote_plus
import requests
from markdownify import markdownify as md
import sys, os

READECK_URL = os.environ.get("READECK_URL", "").strip().rstrip("/")
if not READECK_URL:
    sys.stderr.write("READECK_URL is not set\n")
    sys.exit(1)

READECK_TOKEN = os.environ.get("READECK_TOKEN", "").strip()
if not READECK_TOKEN:
    sys.stderr.write("READECK_TOKEN is not set\n")
    sys.exit(1)

mcp = FastMCP(name="readeck-mcp")

def Bookmark(TypedDict):
    id: str
    title: str
    description: str
    url: str

def list_bookmarks(search: str, offset: int, limit: int) -> list[Bookmark]:
    url = f"{READECK_URL}/api/bookmarks?search={quote_plus(search)}&has_errors=false&offset={offset}&limit={limit}"
    response = requests.get(url, headers={"Authorization": f"Bearer {READECK_TOKEN}"})
    response.raise_for_status()
    return response.json()

class SearchResult(BaseModel):
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
            document_id=bookmark["id"]
        )
        for bookmark in bookmarks
    ]

@mcp.tool()
def initial_search(keywords: list[str], limit: int = 10) -> dict[str, list[SearchResult]]:
    """
    Search the knowledge base for articles that match single keywords.
    After completing this initial search you can perform an adjacent_search to find related articles.
    """
    for keyword in keywords:
        if " " in keyword:
            raise ValueError("Keywords cannot contain spaces")
    return {
        keyword: search(keyword, limit)
        for keyword in keywords
    }

@mcp.tool()
def adjacent_search(keywords: list[str], limit: int = 10) -> dict[str, list[SearchResult]]:
    """
    Search the knowledge base for articles that match the keywords.
    The queries should be derived from the initial search result descriptions.
    """
    return {
        keyword: search(keyword, limit)
        for keyword in keywords
    }

class Document(BaseModel):
    content: str
    citation_url: str

@mcp.tool()
def read(document_ids: list[str]) -> dict[str, Document]:
    """
    Read an article from the knowledge base. Make sure to use the citation_url to cite the article in your response.
    """
    results = {}
    for document_id in document_ids:
        url = f"{READECK_URL}/api/bookmarks/{document_id}/article"
        response = requests.get(url, headers={"Authorization": f"Bearer {READECK_TOKEN}"})
        response.raise_for_status()
        markdown = md(response.text, strip=["a", "img"])
        results[document_id] = Document(
            content=markdown,
            citation_url=f"{READECK_URL}/bookmarks/{document_id}"
        )
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=mcp.name)
    parser.add_argument("--transport", type=str, default="stdio", help="Transport protocol to use (stdio or http://127.0.0.1:5001)")
    args = parser.parse_args()
    try:
        if args.transport == "stdio":
            mcp.run(transport="stdio")
        else:
            url = urlparse(args.transport)
            mcp.settings.host = url.hostname
            mcp.settings.port = url.port
            # NOTE: npx @modelcontextprotocol/inspector for debugging
            print(f"{mcp.name} availabile at http://{mcp.settings.host}:{mcp.settings.port}/sse")
            mcp.settings.log_level = "INFO"
            mcp.run(transport="sse")
    except KeyboardInterrupt:
        pass
