"""MCP Tool: search_song - Search for song metadata."""

import sys

from mcp.types import TextContent

from ..server import mcp
from ..services import MetadataAPIService


# Initialize service (lazy loading)
_metadata_service: MetadataAPIService | None = None


def get_metadata_service() -> MetadataAPIService:
    """Get or create metadata service instance."""
    global _metadata_service
    if _metadata_service is None:
        _metadata_service = MetadataAPIService()
    return _metadata_service


@mcp.tool()
async def search_song(
    artist: str,
    title: str
) -> TextContent:
    """Search for detailed song metadata using Spotify and Last.fm APIs.

    This tool searches for a song across multiple music databases to gather
    comprehensive metadata including genres, mood, popularity, and audio features.

    Use this when:
    - User asks for information about a specific song
    - You need metadata before creating a playlist
    - You want to verify a song exists in music databases

    Args:
        artist: Artist or band name (required)
        title: Song title (required)

    Returns:
        Detailed song metadata or error message

    Examples:
        - search_song(artist="화사", title="Good Goodbye")
        - search_song(artist="The Beatles", title="Hey Jude")
    """
    try:
        print(f"🔍 Searching for: {artist} - {title}", file=sys.stderr)

        # Get service
        service = get_metadata_service()

        # Search for song
        song = await service.search_song(artist=artist, title=title)

        if not song:
            return TextContent(
                type="text",
                text=f"❌ Song not found: {artist} - {title}\n\n"
                     "Please check the spelling and try again."
            )

        # Format response
        response_lines = [
            f"✅ Found: {song.display_name}",
            ""
        ]

        # Spotify metadata
        if song.spotify:
            spotify = song.spotify
            response_lines.extend([
                "📊 Spotify Metadata:",
                f"  Album: {spotify.album or 'N/A'}",
                f"  Release Date: {spotify.release_date or 'N/A'}",
                f"  Popularity: {spotify.popularity}/100",
                f"  Duration: {spotify.duration_ms // 1000 // 60}:{(spotify.duration_ms // 1000) % 60:02d}",
                ""
            ])

            # Audio features
            if spotify.energy is not None:
                response_lines.extend([
                    "🎵 Audio Features:",
                    f"  Energy: {spotify.energy:.2f}",
                    f"  Danceability: {spotify.danceability:.2f}",
                    f"  Valence (mood): {spotify.valence:.2f}",
                    f"  Acousticness: {spotify.acousticness:.2f}",
                    f"  Tempo: {spotify.tempo:.0f} BPM",
                    ""
                ])

            response_lines.append(f"🔗 Spotify: {spotify.external_url}")
            response_lines.append("")

        # Last.fm metadata
        if song.lastfm:
            lastfm = song.lastfm
            response_lines.extend([
                "📻 Last.fm Metadata:",
                f"  Play Count: {lastfm.play_count:,}" if lastfm.play_count else "  Play Count: N/A",
                f"  Listeners: {lastfm.listeners:,}" if lastfm.listeners else "  Listeners: N/A",
                ""
            ])

            if lastfm.tags:
                response_lines.append(f"  Tags: {', '.join(lastfm.tags)}")
                response_lines.append("")

            if lastfm.wiki_summary:
                summary = lastfm.wiki_summary[:200] + "..." if len(lastfm.wiki_summary) > 200 else lastfm.wiki_summary
                response_lines.append(f"  About: {summary}")
                response_lines.append("")

        return TextContent(
            type="text",
            text="\n".join(response_lines)
        )

    except Exception as e:
        print(f"❌ Error in search_song: {e}", file=sys.stderr)
        return TextContent(
            type="text",
            text=f"❌ Search failed: {str(e)}\n\n"
                 "Please try again or check your API credentials."
        )
