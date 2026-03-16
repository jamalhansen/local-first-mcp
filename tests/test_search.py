"""Tests for the search_vault MCP tool."""

import json
from unittest.mock import MagicMock, patch

from local_first_mcp.tools.search import search_vault
from vsearch.search import SearchResult


SAMPLE_RESULTS = [
    SearchResult(
        rank=1,
        score=0.92,
        source_file="Notes/Python.md",
        breadcrumb="Notes / Python",
        snippet="Python is a programming language...",
        metadata={},
    ),
    SearchResult(
        rank=2,
        score=0.85,
        source_file="Notes/Coding.md",
        breadcrumb="Notes / Coding",
        snippet="Coding is a skill...",
        metadata={},
    ),
]


class TestSearchVault:
    def test_returns_json_results(self, monkeypatch):
        monkeypatch.setenv("OBSIDIAN_VAULT", "/fake/vault")
        mock_collection = MagicMock()
        mock_collection.count.return_value = 10

        with patch("vsearch.store.get_client", return_value=MagicMock()):
            with patch("vsearch.store.get_collection", return_value=mock_collection):
                with patch("vsearch.search.search", return_value=SAMPLE_RESULTS):
                    result = search_vault("python programming")

        data = json.loads(result)
        assert len(data) == 2
        assert data[0]["rank"] == 1
        assert data[0]["score"] == 0.92
        assert "Python.md" in data[0]["source_file"]

    def test_empty_index_returns_message(self, monkeypatch):
        monkeypatch.setenv("OBSIDIAN_VAULT", "/fake/vault")
        mock_collection = MagicMock()
        mock_collection.count.return_value = 0

        with patch("vsearch.store.get_client", return_value=MagicMock()):
            with patch("vsearch.store.get_collection", return_value=mock_collection):
                result = search_vault("anything")

        assert "empty" in result.lower() or "vsearch index" in result

    def test_missing_vault_env_returns_error(self, monkeypatch):
        monkeypatch.delenv("OBSIDIAN_VAULT", raising=False)
        result = search_vault("anything")
        assert "OBSIDIAN_VAULT" in result

    def test_top_k_capped_at_20(self, monkeypatch):
        monkeypatch.setenv("OBSIDIAN_VAULT", "/fake/vault")
        mock_collection = MagicMock()
        mock_collection.count.return_value = 100
        mock_search = MagicMock(return_value=SAMPLE_RESULTS)

        with patch("vsearch.store.get_client", return_value=MagicMock()):
            with patch("vsearch.store.get_collection", return_value=mock_collection):
                with patch("vsearch.search.search", mock_search):
                    search_vault("query", top_k=50)

        call_kwargs = mock_search.call_args
        assert call_kwargs.kwargs.get("top_k", call_kwargs.args[2] if len(call_kwargs.args) > 2 else 50) <= 20

    def test_no_results_returns_message(self, monkeypatch):
        monkeypatch.setenv("OBSIDIAN_VAULT", "/fake/vault")
        mock_collection = MagicMock()
        mock_collection.count.return_value = 10

        with patch("vsearch.store.get_client", return_value=MagicMock()):
            with patch("vsearch.store.get_collection", return_value=mock_collection):
                with patch("vsearch.search.search", return_value=[]):
                    result = search_vault("obscure query with no matches")

        assert "no results" in result.lower()
