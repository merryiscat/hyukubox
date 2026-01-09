"""MCP Tools for music search, playlist generation, and YouTube integration."""

# Import tools to register them with FastMCP server
# These imports MUST happen after server.py imports, so we do them lazily
from . import deep_search, search, youtube

__all__ = [
    "search",
    "deep_search",
    "youtube",
]
