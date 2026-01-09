# 🎵 Hyukebox

MCP server for AI-powered music discovery and playlist generation

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![FastMCP](https://img.shields.io/badge/FastMCP-2.11.3+-green.svg)](https://github.com/jlowin/fastmcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🎯 Features

- **🔍 Song Search**: Search music metadata via Spotify + Last.fm APIs
- **🎭 AI Playlists**: Generate thematically coherent playlists with narrative arcs using Claude AI
- **▶️ YouTube Integration**: Automatically create YouTube playlists from recommendations

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│        MCP Tools (4 tools)          │
│  - search_song                      │
│  - create_album_playlist            │
│  - create_youtube_playlist          │
│  - search_youtube_video             │
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

## 📦 Installation

### Prerequisites

- Python 3.13+
- API Keys:
  - [Spotify API](https://developer.spotify.com/dashboard) (Client ID + Secret)
  - [Last.fm API](https://www.last.fm/api/account/create) (API Key)
  - [Anthropic API](https://console.anthropic.com/) (Claude API Key)
  - [YouTube Data API v3](https://console.cloud.google.com/) (OAuth credentials)

### Setup

```bash
# Clone repository
git clone https://github.com/merryiscat/hyukubox.git
cd hyukubox

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .

# Configure environment variables
cp .env.example .env
# Edit .env with your API keys
```

## 🚀 Usage

### Running the MCP Server

```bash
# Start server
python -m hyukebox

# Or use MCP Inspector for testing
mcp dev hyukebox
```

### Using with Claude Desktop

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "hyukebox": {
      "command": "python",
      "args": ["-m", "hyukebox"],
      "cwd": "/path/to/hyukebox"
    }
  }
}
```

### Example Requests

**Search for a song:**
```
Search for "화사 - Good Goodbye"
```

**Create AI playlist:**
```
Create a playlist based on "Adele - Someone Like You" with 15 songs focusing on healing and hope
```

**Create YouTube playlist:**
```
Create a YouTube playlist called "My K-pop Mix" with these songs:
- BTS - Dynamite
- BlackPink - How You Like That
- NewJeans - Ditto
```

## 🛠️ Development

### Project Structure

```
hyukebox/
├── hyukebox/
│   ├── __init__.py
│   ├── __main__.py             # Entry point
│   ├── server.py               # FastMCP server initialization
│   ├── config.py               # Environment variable management
│   │
│   ├── tools/                  # MCP tool definitions
│   │   ├── search.py           # search_song
│   │   ├── deep_search.py      # create_album_playlist
│   │   └── youtube.py          # create_youtube_playlist
│   │
│   ├── services/               # API integration layer
│   │   ├── metadata_api.py     # Spotify + Last.fm
│   │   ├── llm_service.py      # Claude API
│   │   └── youtube_service.py  # YouTube API
│   │
│   ├── models/                 # Pydantic data models
│   │   ├── song.py             # Song data model
│   │   ├── album.py            # Album/Playlist model
│   │   └── narrative.py        # Narrative arc model
│   │
│   └── utils/                  # Utilities
│       ├── cache.py            # TinyDB caching
│       ├── rate_limiter.py     # API rate limiting
│       └── logging_config.py   # Logging setup
│
├── tests/                      # Test suite
├── pyproject.toml             # Project configuration
└── .env.example               # Environment template
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=hyukebox

# Run specific test file
pytest tests/test_search.py
```

## 📝 Environment Variables

Create a `.env` file with the following variables:

```bash
# Spotify API
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret

# Last.fm API
LASTFM_API_KEY=your_lastfm_api_key

# Anthropic API (Claude)
ANTHROPIC_API_KEY=your_anthropic_api_key

# YouTube API
YOUTUBE_CREDENTIALS_PATH=./config/youtube_credentials.json
YOUTUBE_TOKEN_PATH=./config/youtube_token.pickle

# Optional Configuration
CACHE_DIR=./cache
CACHE_TTL=86400
LOG_LEVEL=INFO
MAX_PLAYLIST_SIZE=20
```

## 🎵 How It Works

### 1. Search Song Metadata

The `search_song` tool fetches comprehensive metadata from multiple sources:

- **Spotify**: Audio features (energy, tempo, valence, etc.), popularity, album info
- **Last.fm**: Tags, play count, listeners, wiki summary

### 2. AI Playlist Generation

The `create_album_playlist` tool:

1. Analyzes the title track's mood and characteristics
2. Uses Claude AI to generate an emotional narrative arc
3. Recommends songs that follow the narrative progression
4. Fetches metadata for all recommended songs
5. Returns a cohesive playlist with thematic flow

### 3. YouTube Playlist Creation

The `create_youtube_playlist` tool:

1. Authenticates with YouTube OAuth
2. Searches for each song on YouTube
3. Creates a new playlist
4. Adds all found videos to the playlist

## 🔒 Security Notes

- Never commit `.env` file or API credentials to git
- YouTube credentials stored in `config/` directory (gitignored)
- All logging goes to stderr (STDIO mode compatibility)
- Rate limiting prevents API quota exhaustion

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- Built with [FastMCP](https://github.com/jlowin/fastmcp)
- Powered by [Claude AI](https://www.anthropic.com/)
- Music data from [Spotify](https://spotify.com) and [Last.fm](https://last.fm)
- Playlist creation via [YouTube Data API](https://developers.google.com/youtube)

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---

**Note**: This is an MCP (Model Context Protocol) server designed to work with Claude Desktop and other MCP-compatible clients.
