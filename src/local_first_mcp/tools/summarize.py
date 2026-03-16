"""MCP tool: summarize_article — fetch a URL and write an Obsidian resource note."""

from typing import Optional

from local_first_mcp.server import mcp


@mcp.tool()
def summarize_article(
    url: str,
    provider: str = "ollama",
    model: Optional[str] = None,
) -> str:
    """Fetch an article URL and generate a structured Obsidian resource note.

    Returns markdown with YAML frontmatter, APA 7 citation, summary,
    key concept, and three verbatim quotes.

    The note is returned as a string. To save it, paste or write it to your
    vault — or use the --vault + --class flags via the CLI.

    Args:
        url: The article URL to fetch and summarize.
        provider: LLM provider to use (ollama, anthropic, groq, deepseek, gemini).
        model: Override the provider's default model.
    """
    from resource_summarizer import fetch_url, extract_note, build_note
    from local_first_common.providers import PROVIDERS
    from local_first_common.cli import resolve_provider

    llm = resolve_provider(PROVIDERS, provider, model)
    article_text, page_title = fetch_url(url)
    note = extract_note(llm, article_text, url, page_title, verbose=False)
    return build_note(note, url)
