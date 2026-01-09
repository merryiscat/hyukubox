"""MCP Tool: create_youtube_playlist - Create YouTube playlists."""

import sys
from typing import Optional

from mcp.types import TextContent

from ..server import mcp
from ..services import YouTubeService


# Initialize service (lazy loading)
_youtube_service: YouTubeService | None = None


def get_youtube_service() -> YouTubeService:
    """Get or create YouTube service instance."""
    global _youtube_service
    if _youtube_service is None:
        _youtube_service = YouTubeService()
    return _youtube_service


@mcp.tool()
async def create_youtube_playlist(
    title: str,
    songs: list[str],
    description: Optional[str] = None,
    privacy: str = "private"
) -> TextContent:
    """Create a YouTube playlist and add songs to it.

    This tool creates a new YouTube playlist in your account and adds songs
    by searching for them on YouTube. Requires YouTube API authentication.

    ⚠️ AUTHENTICATION REQUIRED: This tool requires YouTube OAuth authentication.
    On first use, you'll be prompted to authorize access to your YouTube account.

    Use this when:
    - User wants to create a YouTube playlist
    - User has a list of songs they want to save to YouTube
    - User wants to export a generated playlist to YouTube

    Args:
        title: Playlist title (required)
        songs: List of songs in "Artist - Title" format (required)
        description: Optional playlist description
        privacy: Privacy setting - "public", "unlisted", or "private" (default: "private")

    Returns:
        Playlist URL and creation status

    Examples:
        - create_youtube_playlist(
            title="My Playlist",
            songs=["화사 - Good Goodbye", "Adele - Someone Like You"]
          )
        - create_youtube_playlist(
            title="Workout Mix",
            songs=["BTS - Dynamite", "BlackPink - How You Like That"],
            description="High energy K-pop workout playlist",
            privacy="public"
          )
    """
    try:
        # Validate inputs
        if not songs:
            return TextContent(
                type="text",
                text="❌ No songs provided. Please provide a list of songs."
            )

        if privacy not in ["public", "unlisted", "private"]:
            return TextContent(
                type="text",
                text=f"❌ Invalid privacy setting: {privacy}\n"
                     "Must be one of: public, unlisted, private"
            )

        print(f"🎬 Creating YouTube playlist: {title}", file=sys.stderr)
        print(f"   Songs: {len(songs)}", file=sys.stderr)
        print(f"   Privacy: {privacy}", file=sys.stderr)

        # Get service
        service = get_youtube_service()

        # Ensure authenticated
        try:
            service.authenticate()
        except FileNotFoundError as e:
            return TextContent(
                type="text",
                text=f"❌ YouTube authentication failed: {str(e)}\n\n"
                     "Please configure YouTube API credentials:\n"
                     "1. Go to Google Cloud Console\n"
                     "2. Enable YouTube Data API v3\n"
                     "3. Create OAuth 2.0 credentials\n"
                     "4. Download credentials.json\n"
                     f"5. Place at: {service.credentials_path}"
            )

        # Create playlist with search
        playlist_description = description or f"Created by Hyukebox - {len(songs)} songs"

        print("📀 Creating playlist...", file=sys.stderr)
        playlist_id, playlist_url, added_count = service.create_playlist_with_search(
            title=title,
            description=playlist_description,
            song_queries=songs,
            privacy_status=privacy
        )

        print(f"✅ Playlist created: {playlist_url}", file=sys.stderr)

        # Format response
        response_lines = [
            f"✅ YouTube Playlist Created!",
            "",
            f"📀 Title: {title}",
            f"🔗 URL: {playlist_url}",
            f"🎵 Songs: {added_count}/{len(songs)} added successfully",
            f"🔒 Privacy: {privacy}",
            ""
        ]

        if added_count < len(songs):
            missing_count = len(songs) - added_count
            response_lines.extend([
                f"⚠️ Warning: {missing_count} song(s) could not be found on YouTube",
                "   These songs were skipped.",
                ""
            ])

        response_lines.append("✨ You can now view and edit your playlist on YouTube!")

        return TextContent(
            type="text",
            text="\n".join(response_lines)
        )

    except Exception as e:
        print(f"❌ Error in create_youtube_playlist: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)

        return TextContent(
            type="text",
            text=f"❌ Failed to create YouTube playlist: {str(e)}\n\n"
                 "Please check your YouTube API credentials and try again."
        )


@mcp.tool()
async def search_youtube_video(
    query: str
) -> TextContent:
    """Search for a video on YouTube and return its ID.

    This is a helper tool for finding YouTube video IDs for specific songs.

    Args:
        query: Search query (e.g., "Artist - Song Title")

    Returns:
        Video ID and URL if found

    Example:
        - search_youtube_video(query="화사 - Good Goodbye")
    """
    try:
        print(f"🔍 Searching YouTube: {query}", file=sys.stderr)

        # Get service
        service = get_youtube_service()

        # Ensure authenticated
        service.authenticate()

        # Search
        video_id = service.search_video(query)

        if not video_id:
            return TextContent(
                type="text",
                text=f"❌ No video found for: {query}"
            )

        video_url = f"https://www.youtube.com/watch?v={video_id}"

        return TextContent(
            type="text",
            text=f"✅ Found video!\n\n"
                 f"Query: {query}\n"
                 f"Video ID: {video_id}\n"
                 f"URL: {video_url}"
        )

    except Exception as e:
        print(f"❌ Error in search_youtube_video: {e}", file=sys.stderr)
        return TextContent(
            type="text",
            text=f"❌ Search failed: {str(e)}"
        )
