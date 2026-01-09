# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Hyukebox**: MCP server for AI-powered music discovery and playlist generation

- **Purpose**: Search music metadata, generate thematically coherent playlists using AI, create YouTube playlists
- **3 MCP Tools**:
  1. `search_song` - Search music metadata via Spotify + Last.fm APIs
  2. `create_album_playlist` - Generate AI-curated playlists with narrative arcs using Claude API
  3. `create_youtube_playlist` - Create YouTube playlists via YouTube Data API v3
- **Tech Stack**: Python 3.13+ | FastMCP 2.11.3+ | Spotify API | Last.fm API | Claude API | YouTube Data API v3
- **Architecture**: 3-layer (MCP Tools → Services → Utils/Models)

## Development Setup

### Prerequisites

- Python 3.13+
- API Keys:
  - Spotify (Client ID + Secret)
  - Last.fm API Key
  - Anthropic API Key (Claude)
  - YouTube Data API v3 credentials

### Installation (Planned)

```bash
# Install dependencies
pip install -e .

# Copy environment template
cp .env.example .env
# Then edit .env with your API keys
```

### Running the Server (Planned)

```bash
# Run MCP server
python -m hyukebox

# Test with MCP Inspector
mcp dev hyukebox
```

### Testing (Planned)

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_search.py

# Run with coverage
pytest --cov=hyukebox
```

## Architecture

### High-Level Structure

```
┌─────────────────────────────────────┐
│        MCP Tools (3개)              │
│  - search_song                      │
│  - create_album_playlist            │
│  - create_youtube_playlist          │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│        Service Layer                │
│  - MetadataAPIService               │
│    (Spotify + Last.fm)              │
│  - LLMService (Claude API)          │
│  - YouTubeService (YouTube API)     │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│        Utils & Models               │
│  - TinyDB Cache                     │
│  - RateLimiter                      │
│  - Pydantic Models                  │
└─────────────────────────────────────┘
```

### Planned Directory Structure

```
hyukebox/
├── hyukebox/
│   ├── __init__.py
│   ├── __main__.py             # Entry point
│   ├── server.py               # FastMCP server initialization
│   ├── config.py               # Environment variable management
│   │
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── search.py           # Tool 1: search_song
│   │   ├── deep_search.py      # Tool 2: create_album_playlist
│   │   └── youtube.py          # Tool 3: create_youtube_playlist
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── metadata_api.py     # Spotify + Last.fm integration
│   │   ├── llm_service.py      # Claude API integration
│   │   └── youtube_service.py  # YouTube API client
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── song.py             # Song data model
│   │   ├── album.py            # Album/Playlist model
│   │   └── narrative.py        # Narrative arc model
│   │
│   └── utils/
│       ├── __init__.py
│       ├── cache.py            # TinyDB caching
│       ├── rate_limiter.py     # API rate limiting
│       └── logging_config.py   # Logging setup (stderr only!)
│
├── tests/
│   ├── conftest.py
│   ├── test_search.py
│   ├── test_deep_search.py
│   ├── test_youtube.py
│   └── fixtures/
│       └── mock_responses.json
│
├── pyproject.toml
├── .env.example
├── .gitignore
├── CLAUDE.md                   # This file
└── quick_reference.md          # Detailed reference analysis
```

## MCP Implementation Rules

### ⚠️ CRITICAL: STDIO Logging

**NEVER use stdout in STDIO mode** - it breaks JSON-RPC communication!

❌ **Wrong** (breaks MCP):
```python
print("Debug message")
console.log("Info")
```

✅ **Correct**:
```python
import sys
print("Debug message", file=sys.stderr)

# Or use file logging
import logging
logging.basicConfig(filename='server.log', level=logging.INFO)
logging.info("Debug message")
```

### FastMCP Tool Definition Pattern

```python
from fastmcp import FastMCP
from mcp.types import TextContent

# Initialize server
mcp = FastMCP("Hyukebox")

# Define tool with decorator
@mcp.tool()
async def tool_name(
    param1: str,              # Required parameter
    param2: int = 10          # Optional parameter with default
) -> TextContent:
    """Tool description that LLM will see.

    Args:
        param1: Description of param1
        param2: Description of param2 (default: 10)

    Returns:
        Success or error message
    """
    try:
        # Implementation
        result = await do_something(param1, param2)
        return TextContent(type="text", text=f"✅ Success: {result}")
    except Exception as e:
        return TextContent(type="text", text=f"❌ Error: {str(e)}")

# Run server
if __name__ == "__main__":
    mcp.run(transport="stdio")
```

**Key Points**:
- Type hints are **required** - MCP auto-generates `inputSchema` from them
- Docstring format matters - LLM uses it to understand when to call the tool
- Use `async def` for tools that make API calls
- Always return `TextContent` or `list[TextContent]`

## Reference Implementation Guide

When implementing specific features, reference these files from the `reference/` directory:

| Feature | Reference File | Lines | Notes |
|---------|---------------|-------|-------|
| **FastMCP initialization** | `llm-jukebox/server.py` | 27-33 | Server setup, env vars, TinyDB init |
| **Tool parameters & docstrings** | `aimusic-mcp-tool/api.py` | 18-163 | Detailed tool descriptions, parameter validation |
| **Async HTTP (httpx)** | `aimusic-mcp-tool/api.py` | 70-73 | HTTP client setup, timeout handling |
| **TinyDB caching** | `llm-jukebox/server.py` | 31-33 | DB initialization, Query patterns |
| **Polling pattern (long tasks)** | `aimusic-mcp-tool/api.py` | 90-106 | Async polling for LLM API calls |
| **Async parallel execution** | N/A | - | Use `asyncio.gather()` for Spotify + Last.fm |
| **Error handling** | `aimusic-mcp-tool/api.py` | 155-161 | HTTP status codes (401, 402, etc.) |

### MCP Documentation (Must Read)

Located in `reference/Mcp docs/`:

1. **`08_Build an MCP Server.md`** - STDIO logging rules (CRITICAL!)
2. **`32_Tools.md`** - Tool schema definition, JSON-RPC protocol
3. **`18_Transports.md`** - STDIO transport mechanism

For comprehensive reference analysis with code examples, see `quick_reference.md`.

## Key Implementation Notes

### Environment Variables
- **Storage**: Use `.env` file (never commit!)
- **Loading**: Use `python-dotenv` or `pydantic-settings`
- **Required keys**:
  ```
  SPOTIFY_CLIENT_ID=...
  SPOTIFY_CLIENT_SECRET=...
  LASTFM_API_KEY=...
  ANTHROPIC_API_KEY=...
  YOUTUBE_CREDENTIALS_PATH=./config/youtube_credentials.json
  YOUTUBE_TOKEN_PATH=./config/youtube_token.pickle
  ```

### Async Patterns
```python
# Parallel API calls
spotify_task = spotify_client.search_track(artist, title)
lastfm_task = lastfm_client.get_track_info(artist, title)

# Wait for both (with exception handling)
spotify_data, lastfm_data = await asyncio.gather(
    spotify_task,
    lastfm_task,
    return_exceptions=True  # Returns exceptions as results
)
```

### Error Handling
```python
# HTTP status code handling
try:
    response = await client.post(url, json=params)
    response.raise_for_status()
except httpx.HTTPStatusError as e:
    if e.response.status_code == 401:
        return "Invalid API key"
    elif e.response.status_code == 402:
        return "Insufficient credits"
    elif e.response.status_code == 404:
        return "Resource not found"
    else:
        raise
```

### Type Hints
**Required** for MCP to auto-generate tool schemas:
```python
# ✅ Correct - MCP can generate schema
async def search_song(artist: str, title: str) -> TextContent:
    ...

# ❌ Wrong - MCP cannot infer parameter types
async def search_song(artist, title):
    ...
```

### API Rate Limiting
- **Spotify**: ~180 requests/minute
- **Last.fm**: Generous (no strict limit)
- **Claude API**: Token-based billing
- **YouTube**: 10,000 quota units/day

Implement rate limiting in `utils/rate_limiter.py` using token bucket algorithm.

## API Key Setup Instructions

### 1. Spotify API
1. Go to https://developer.spotify.com/dashboard
2. Create an app
3. Copy Client ID and Client Secret
4. Add to `.env`:
   ```
   SPOTIFY_CLIENT_ID=your_client_id
   SPOTIFY_CLIENT_SECRET=your_client_secret
   ```

### 2. Last.fm API
1. Go to https://www.last.fm/api/account/create
2. Create API account (free)
3. Copy API Key
4. Add to `.env`:
   ```
   LASTFM_API_KEY=your_api_key
   ```

### 3. Claude API (Anthropic)
1. Go to https://console.anthropic.com/
2. Create API key
3. Add to `.env`:
   ```
   ANTHROPIC_API_KEY=your_api_key
   ```

### 4. YouTube Data API v3
1. Go to Google Cloud Console
2. Create project and enable YouTube Data API v3
3. Create OAuth 2.0 credentials
4. Download `credentials.json`
5. Add to `.env`:
   ```
   YOUTUBE_CREDENTIALS_PATH=./config/youtube_credentials.json
   ```

## Current Status

This project is in **initial planning phase**. See `quick_reference.md` for:
- Detailed reference implementation analysis
- MCP documentation guide
- Implementation patterns and code examples
