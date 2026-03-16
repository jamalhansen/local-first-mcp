"""MCP tool: generate_promo — create multi-platform promotional copy for a blog post."""

import os
from typing import Optional

from local_first_mcp.server import mcp

_DEFAULT_PROVIDER = os.environ.get("PROMO_PROVIDER") or os.environ.get("MODEL_PROVIDER", "ollama")
_DEFAULT_MODEL = os.environ.get("PROMO_MODEL") or os.environ.get("MODEL") or None


@mcp.tool()
def generate_promo(
    post_path: str,
    provider: str = _DEFAULT_PROVIDER,
    model: Optional[str] = _DEFAULT_MODEL,
    platform: Optional[str] = None,
) -> str:
    """Generate platform-specific promotional copy for a blog post.

    Runs a two-pass generation: first extracts a hook, key insight, and hashtags
    from the post; then generates formatted copy per platform.

    Args:
        post_path: Absolute path to the blog post markdown file.
        provider: LLM provider (ollama, anthropic, groq, deepseek, gemini).
                  Defaults: PROMO_PROVIDER → MODEL_PROVIDER → "ollama".
        model: Override the provider's default model.
               Defaults: PROMO_MODEL → MODEL → provider default.
        platform: Generate for one platform only (e.g. "twitter", "linkedin").
                  If omitted, generates for all configured platforms.
    """
    from datetime import date
    from pathlib import Path

    import promo as promo_module
    from local_first_common.providers import PROVIDERS
    from local_first_common.cli import resolve_provider

    config = promo_module.load_config()
    platforms = promo_module.load_platforms()
    llm = resolve_provider(PROVIDERS, provider, model)

    post_file = Path(post_path).resolve()
    metadata, content = promo_module.load_post(post_file)
    slug = promo_module.extract_slug(post_file, metadata)
    canonical_url = promo_module.build_canonical_url(slug, config)
    published_date = str(metadata.get("date", date.today().isoformat()))

    post_context = promo_module.extract_hook(llm, content[:4000], verbose=False, dry_run=False)
    context_str = promo_module.format_context(post_context)

    active_keys = [platform] if platform else list(platforms.keys())
    sections: dict = {}
    for key in active_keys:
        plat = platforms[key]
        text = promo_module.generate_platform(
            key, plat, llm, canonical_url, context_str, config, verbose=False, dry_run=False
        )
        sections[key] = (plat["label"], text)

    if platform and platform in sections:
        label, text = sections[platform]
        return f"## {label}\n\n{text}"

    return promo_module.assemble_promo(slug, canonical_url, published_date, sections)
