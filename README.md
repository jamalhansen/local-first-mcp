# local-first-mcp

MCP server that exposes local-first AI tools to Claude.

This server allows Claude to use your locally-built tools (like `resource-summarizer`, `promo-generator`, etc.) directly via the [Model Context Protocol](https://modelcontextprotocol.io).

## Tools Exposed

- `summarize_article`: Fetch and summarize a URL (via `resource-summarizer`)
- `generate_promo`: Create promotional copy for a blog post (via `promo-generator`)
- `semantic_search`: Search your Obsidian vault by meaning (via `vault-semantic-search`)

## Installation

```bash
cd local-first-mcp
uv sync
```

## Configuration for Claude Desktop

Add this to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "local-first": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/jamalhansen/projects/local-first/local-first-mcp",
        "run",
        "local-first-mcp"
      ]
    }
  }
}
```

## Project Structure

```
local-first-mcp/
├── src/
│   └── local_first_mcp/
│       ├── server.py    # FastMCP server definition
│       └── tools/       # Tool-specific wrappers
│           ├── promo.py
│           ├── search.py
│           └── summarize.py
├── pyproject.toml       # Managed by uv
└── tests/               # Server integration tests
```
