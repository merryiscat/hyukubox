"""MCP server entry point for Hyukebox."""

import sys
from fastmcp import FastMCP

from .config import settings
from .utils.logging_config import setup_logging

# Initialize logging (STDERR ONLY - NEVER stdout!)
logger = setup_logging(settings.log_level)

# Initialize FastMCP server
mcp = FastMCP("Hyukebox")


def main() -> None:
    """Run the MCP server.

    This is the main entry point for the Hyukebox MCP server.
    """
    try:
        # Validate required API keys
        try:
            settings.validate_required_keys()
        except ValueError as e:
            print(f"❌ Configuration error: {e}", file=sys.stderr)
            print("\nPlease ensure all required API keys are set in .env file.", file=sys.stderr)
            print("See .env.example for required variables.", file=sys.stderr)
            sys.exit(1)

        print("🎵 Starting Hyukebox MCP Server...", file=sys.stderr)
        print(f"Log level: {settings.log_level}", file=sys.stderr)

        # Import tools to register them with MCP
        from .tools import deep_search, search, youtube
        print(f"✅ Loaded {len(mcp._tools)} MCP tools", file=sys.stderr)

        # Run server (STDIO transport by default)
        mcp.run(transport="stdio")

    except KeyboardInterrupt:
        print("\n👋 Shutting down Hyukebox MCP Server...", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        print(f"❌ Fatal error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
