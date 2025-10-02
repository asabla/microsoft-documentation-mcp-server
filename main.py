"""
Sample MCP Server for ChatGPT Integration

This server implements the Model Context Protocol (MCP) with search and fetch
capabilities designed to work with ChatGPT's chat and deep research features.
"""

import logging
import os
from typing import Any, Dict, List

import html2text
import requests
from fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

server_instructions = """
This MCP server provides search and document retrieval capabilities
for chat and deep research connectors. Use the search tool to find relevant documents
based on keywords, then use the fetch tool to retrieve complete
document content with citations.
"""


def create_server() -> FastMCP[Any]:
    mcp = FastMCP(
        name="Microsoft Documentation MCP Server", instructions=server_instructions
    )

    @mcp.tool()
    async def search(
        query: str, locale: str = "en-us", top: int = 10
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search for documents using OpenAI Vector Store search.

        This tool searches through the vector store to find semantically relevant matches.
        Returns a list of search results with basic information. Use the fetch tool to get
        complete document content.

        Args:
            query: Search query string. Natural language queries work best for semantic search.

        Returns:
            Dictionary with 'results' key containing list of matching documents.
            Each result includes title, url, description and category.
        """

        if not query or not query.strip():
            return {"results": []}

        base_url = "https://learn.microsoft.com/api/search"
        params = {
            "search": query,
            "locale": locale,
            "facet": ["category", "products", "tags"],
            "$top": top,
            "expandScope": "true",
            "includeQuestion": "false",
            "partnerId": "LearnSite",
        }

        logger.info(f"Searching for query: {query} with params: {params}")

        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()

        logger.info(f"Search returned {len(data.get('results', []))} results")

        return {"results": data.get("results", [])}

    @mcp.tool()
    async def fetch(url: str) -> str:
        """
        Retrieve complete document content by ID for detailed
        analysis and citation. This tool fetches the full document
        content from Microsoft Learn platform. Use this after finding
        relevant documents with the search tool to get complete
        information for analysis and proper citation.

        Args:
            url: The URL of the document to fetch.

        Returns:
            Complete document in markdown format.

        Raises:
            ValueError: If the specified url is not found
        """

        if not url or not url.strip():
            raise ValueError("The 'url' parameter is required.")

        logger.info(f"Fetching document from URL: {url}")

        response = requests.get(url)
        if response.status_code == 404:
            raise ValueError(f"Document not found at URL: {url}")
        response.raise_for_status()

        logger.info(f"Successfully fetched document from URL: {url}")

        markdown = html2text.HTML2Text()
        markdown.ignore_links = False
        markdown.ignore_images = True
        markdown.bypass_tables = False
        markdown.ignore_emphasis = False
        markdown.body_width = 0  # Prevent wrapping

        return markdown.handle(response.text)

    return mcp


def main():
    logger.info("Starting MCP server...")

    server = create_server()

    # Configure and start the server
    logger.info("Start MCP server on 0.0.0.0:8000")
    logger.info("Server will be accessible via SSE transport")

    try:
        server.run(transport="sse", host="0.0.0.0", port=8000)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Error running server: {e}")
        raise


if __name__ == "__main__":
    main()
