"""local-first MCP server — exposes local-first AI tools to Claude."""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("local-first-tools")

# Import tool modules so their @mcp.tool() decorators fire during startup.
from local_first_mcp.tools import summarize, promo, search  # noqa: E402, F401


def main() -> None:
    mcp.run()
