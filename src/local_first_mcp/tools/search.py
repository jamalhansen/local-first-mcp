"""MCP tool: search_vault — semantic search over the Obsidian vault."""

import json
import os

from local_first_mcp.server import mcp


@mcp.tool()
def search_vault(
    query: str,
    top_k: int = 5,
) -> str:
    """Search the Obsidian vault by meaning using semantic search.

    Requires the vault to be indexed first (run `vsearch index` from the
    vault-semantic-search CLI). Returns ranked results with file paths,
    similarity scores, and content snippets.

    Args:
        query: Natural language search query.
        top_k: Number of results to return (default 5, max 20).
    """
    from vsearch.search import search
    from vsearch.store import get_client, get_collection
    from vsearch.config import DEFAULT_EMBEDDING_MODEL

    vault_path = os.environ.get("OBSIDIAN_VAULT")
    if not vault_path:
        return "Error: OBSIDIAN_VAULT environment variable not set."

    client = get_client()
    collection = get_collection(client, model=DEFAULT_EMBEDDING_MODEL)

    if collection.count() == 0:
        return (
            "The semantic index is empty. "
            "Run `vsearch index --vault <path>` first to build the index."
        )

    top_k = min(top_k, 20)
    results = search(query_text=query, collection=collection, top_k=top_k)

    if not results:
        return "No results found."

    return json.dumps([r.to_dict() for r in results], indent=2)
