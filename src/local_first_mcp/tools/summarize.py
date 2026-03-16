"""MCP tool: summarize_article — fetch a URL and write an Obsidian resource note."""

import os
from typing import Optional

from local_first_mcp.server import mcp

_DEFAULT_PROVIDER = os.environ.get("SUMMARIZE_PROVIDER") or os.environ.get("MODEL_PROVIDER", "ollama")
_DEFAULT_MODEL = os.environ.get("SUMMARIZE_MODEL") or os.environ.get("MODEL") or None


@mcp.tool()
def summarize_article(
    url: str,
    provider: str = _DEFAULT_PROVIDER,
    model: Optional[str] = _DEFAULT_MODEL,
) -> str:
    """Fetch an article URL and generate a structured Obsidian resource note.

    Returns markdown with YAML frontmatter, APA 7 citation, summary,
    key concept, and three verbatim quotes.

    The note is returned as a string. To save it, paste or write it to your
    vault — or use the --vault + --class flags via the CLI.

    Args:
        url: The article URL to fetch and summarize.
        provider: LLM provider (ollama, anthropic, groq, deepseek, gemini).
                  Defaults: SUMMARIZE_PROVIDER → MODEL_PROVIDER → "ollama".
        model: Override the provider's default model.
               Defaults: SUMMARIZE_MODEL → MODEL → provider default.
    """
    from resource_summarizer import fetch_url, extract_note, build_note
    from local_first_common.providers import PROVIDERS
    from local_first_common.cli import resolve_provider

    llm = resolve_provider(PROVIDERS, provider, model)
    article_text, page_title = fetch_url(url)
    note = extract_note(llm, article_text, url, page_title, verbose=False)
    return build_note(note, url)
