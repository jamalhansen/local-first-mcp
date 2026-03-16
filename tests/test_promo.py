"""Tests for the generate_promo MCP tool."""

from pathlib import Path
from unittest.mock import MagicMock, patch


from local_first_mcp.tools.promo import generate_promo


SAMPLE_FRONTMATTER = "---\ntitle: My Post\nslug: my-post\ndate: 2024-01-15\n---\n\n"
SAMPLE_CONTENT = "This is a great post about Python. " * 50
SAMPLE_POST = SAMPLE_FRONTMATTER + SAMPLE_CONTENT

SAMPLE_PLATFORMS = {
    "twitter": {"label": "Twitter / X", "char_limit": 280},
    "linkedin": {"label": "LinkedIn", "char_limit": 3000},
}

SAMPLE_CONFIG = {
    "blog": {"base_url": "https://example.com/blog"},
    "subscribe": {"cta": "Subscribe here"},
}


def _make_post_file(tmp_path: Path, content: str = SAMPLE_POST) -> Path:
    p = tmp_path / "my-post.md"
    p.write_text(content, encoding="utf-8")
    return p


def _mock_promo_module(
    hook_text: str = "Great hook",
    twitter_text: str = "Twitter promo text",
    linkedin_text: str = "LinkedIn promo text",
):
    mod = MagicMock()
    mod.load_config.return_value = SAMPLE_CONFIG
    mod.load_platforms.return_value = SAMPLE_PLATFORMS
    mod.load_post.return_value = ({"title": "My Post", "slug": "my-post", "date": "2024-01-15"}, SAMPLE_CONTENT)
    mod.extract_slug.return_value = "my-post"
    mod.build_canonical_url.return_value = "https://example.com/blog/my-post"
    mod.extract_hook.return_value = MagicMock(hook=hook_text, key_insight="insight", hashtags=["#python"])
    mod.format_context.return_value = f"Hook: {hook_text}"
    mod.generate_platform.side_effect = lambda key, *args, **kwargs: (
        twitter_text if key == "twitter" else linkedin_text
    )
    mod.assemble_promo.return_value = "# Promo\n\n## Twitter / X\n\nTwitter promo text\n\n## LinkedIn\n\nLinkedIn promo text"
    return mod


class TestGeneratePromo:
    def test_returns_assembled_promo_for_all_platforms(self, tmp_path):
        post_file = _make_post_file(tmp_path)
        mock_llm = MagicMock()
        mock_promo = _mock_promo_module()

        with patch("local_first_common.providers.PROVIDERS", {"ollama": MagicMock(return_value=mock_llm)}):
            with patch.dict("sys.modules", {"promo": mock_promo}):
                result = generate_promo(post_path=str(post_file))

        assert "Promo" in result or "Twitter" in result or "LinkedIn" in result

    def test_single_platform_returns_section_only(self, tmp_path):
        post_file = _make_post_file(tmp_path)
        mock_llm = MagicMock()
        mock_promo = _mock_promo_module()

        with patch("local_first_common.providers.PROVIDERS", {"ollama": MagicMock(return_value=mock_llm)}):
            with patch.dict("sys.modules", {"promo": mock_promo}):
                result = generate_promo(post_path=str(post_file), platform="twitter")

        assert "Twitter / X" in result
        assert "LinkedIn" not in result

    def test_passes_provider_and_model(self, tmp_path):
        post_file = _make_post_file(tmp_path)
        mock_provider_cls = MagicMock()
        mock_llm = MagicMock()
        mock_provider_cls.return_value = mock_llm
        mock_promo = _mock_promo_module()

        with patch("local_first_common.providers.PROVIDERS", {"anthropic": mock_provider_cls}):
            with patch.dict("sys.modules", {"promo": mock_promo}):
                generate_promo(post_path=str(post_file), provider="anthropic", model="claude-haiku-4-5-20251001")

        mock_provider_cls.assert_called_once_with(model="claude-haiku-4-5-20251001")

    def test_calls_extract_hook_with_content(self, tmp_path):
        post_file = _make_post_file(tmp_path)
        mock_llm = MagicMock()
        mock_promo = _mock_promo_module()

        with patch("local_first_common.providers.PROVIDERS", {"ollama": MagicMock(return_value=mock_llm)}):
            with patch.dict("sys.modules", {"promo": mock_promo}):
                generate_promo(post_path=str(post_file))

        mock_promo.extract_hook.assert_called_once()
        call_args = mock_promo.extract_hook.call_args
        assert mock_llm == call_args.args[0] or mock_llm == call_args.kwargs.get("provider")

    def test_generate_platform_called_for_each_platform(self, tmp_path):
        post_file = _make_post_file(tmp_path)
        mock_llm = MagicMock()
        mock_promo = _mock_promo_module()

        with patch("local_first_common.providers.PROVIDERS", {"ollama": MagicMock(return_value=mock_llm)}):
            with patch.dict("sys.modules", {"promo": mock_promo}):
                generate_promo(post_path=str(post_file))

        assert mock_promo.generate_platform.call_count == len(SAMPLE_PLATFORMS)
