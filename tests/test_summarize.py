"""Tests for the summarize_article MCP tool."""

import json
from unittest.mock import MagicMock, patch

from local_first_mcp.tools.summarize import summarize_article


SAMPLE_ARTICLE = "Python is a programming language. " * 50  # > 200 words
SAMPLE_NOTE_RESPONSE = json.dumps({
    "title": "Understanding Python",
    "citation": "Smith, J. (2024). Understanding Python. Blog.",
    "summary": "A brief overview of Python as a language.",
    "key_concept": "Dynamic typing",
    "key_quotes": ["Python is readable.", "Python is popular.", "Python is versatile."],
})


class TestSummarizeArticle:
    def test_returns_markdown_note(self):
        mock_llm = MagicMock()
        mock_llm.complete.return_value = SAMPLE_NOTE_RESPONSE

        with patch("local_first_common.providers.PROVIDERS", {"ollama": MagicMock(return_value=mock_llm)}):
            with patch("resource_summarizer.fetch_url", return_value=(SAMPLE_ARTICLE, "Understanding Python")):
                result = summarize_article(url="https://example.com/article")

        assert "---" in result          # has YAML frontmatter
        assert "Citation" in result
        assert "Summary" in result
        assert "Key Concept" in result
        assert "Key Quotes" in result

    def test_includes_url_in_frontmatter(self):
        mock_llm = MagicMock()
        mock_llm.complete.return_value = SAMPLE_NOTE_RESPONSE

        with patch("local_first_common.providers.PROVIDERS", {"ollama": MagicMock(return_value=mock_llm)}):
            with patch("resource_summarizer.fetch_url", return_value=(SAMPLE_ARTICLE, None)):
                result = summarize_article(url="https://example.com/article")

        assert "https://example.com/article" in result

    def test_passes_provider_and_model(self):
        mock_provider_cls = MagicMock()
        mock_llm = MagicMock()
        mock_llm.complete.return_value = SAMPLE_NOTE_RESPONSE
        mock_provider_cls.return_value = mock_llm

        with patch("local_first_common.providers.PROVIDERS", {"anthropic": mock_provider_cls}):
            with patch("resource_summarizer.fetch_url", return_value=(SAMPLE_ARTICLE, "Title")):
                summarize_article(url="https://example.com", provider="anthropic", model="claude-haiku-4-5-20251001")

        mock_provider_cls.assert_called_once_with(model="claude-haiku-4-5-20251001")
