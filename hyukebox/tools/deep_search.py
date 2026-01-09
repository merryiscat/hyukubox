"""MCP Tool: create_album_playlist - AI-powered playlist generation."""

import asyncio
import sys
from typing import Optional

from mcp.types import TextContent

from ..config import settings
from ..models import AlbumPlaylist, PlaylistMetadata, Song
from ..server import mcp
from ..services import LLMService, MetadataAPIService


# Initialize services (lazy loading)
_metadata_service: MetadataAPIService | None = None
_llm_service: LLMService | None = None


def get_services() -> tuple[MetadataAPIService, LLMService]:
    """Get or create service instances."""
    global _metadata_service, _llm_service

    if _metadata_service is None:
        _metadata_service = MetadataAPIService()

    if _llm_service is None:
        _llm_service = LLMService()

    return _metadata_service, _llm_service


@mcp.tool()
async def create_album_playlist(
    artist: str,
    title: str,
    playlist_size: int = 10,
    user_prompt: Optional[str] = None
) -> list[TextContent]:
    """Create an AI-curated playlist with narrative arc based on a title track.

    This tool analyzes a title track and generates a thematically coherent playlist
    following an emotional narrative arc. Uses Claude AI to understand the song's
    mood and create a journey through related songs.

    ⚠️ COST WARNING: This tool makes Claude API calls which may incur costs.
    Only use when explicitly requested by the user.

    Use this when:
    - User wants a playlist around a specific song
    - User requests an "album" based on a song
    - User wants music recommendations with a story/theme

    Args:
        artist: Artist name of the title track (required)
        title: Song title of the title track (required)
        playlist_size: Number of songs in playlist (default: 10, max: 20)
        user_prompt: Optional guidance for playlist theme/mood

    Returns:
        Generated playlist with narrative arc and song list

    Examples:
        - create_album_playlist(artist="화사", title="Good Goodbye")
        - create_album_playlist(artist="Adele", title="Someone Like You", playlist_size=15)
        - create_album_playlist(artist="BTS", title="Spring Day", user_prompt="Focus on healing and hope")
    """
    try:
        # Validate playlist size
        if playlist_size < 3:
            return [TextContent(
                type="text",
                text="❌ Playlist size must be at least 3 songs."
            )]

        if playlist_size > settings.max_playlist_size:
            return [TextContent(
                type="text",
                text=f"❌ Playlist size cannot exceed {settings.max_playlist_size} songs."
            )]

        print(f"🎵 Creating playlist for: {artist} - {title}", file=sys.stderr)

        # Get services
        metadata_service, llm_service = get_services()

        # Step 1: Search for title track
        print(f"📀 Step 1/4: Searching for title track...", file=sys.stderr)
        title_track = await metadata_service.search_song(artist=artist, title=title)

        if not title_track:
            return [TextContent(
                type="text",
                text=f"❌ Title track not found: {artist} - {title}\n\n"
                     "Please check the spelling and try again."
            )]

        print(f"✅ Found title track: {title_track.display_name}", file=sys.stderr)

        # Step 2: Generate narrative arc using LLM
        print(f"🎭 Step 2/4: Generating narrative arc using AI...", file=sys.stderr)
        narrative = await llm_service.generate_narrative_arc(
            title_track=title_track,
            playlist_size=playlist_size,
            user_prompt=user_prompt
        )

        print(f"✅ Narrative theme: {narrative.theme}", file=sys.stderr)

        # Step 3: Get song recommendations from LLM
        print(f"🔍 Step 3/4: Generating song recommendations...", file=sys.stderr)
        recommendations = await llm_service.generate_song_recommendations(
            title_track=title_track,
            narrative=narrative,
            song_count=playlist_size,
            context_language=settings.default_language_context
        )

        print(f"✅ Got {len(recommendations)} recommendations", file=sys.stderr)

        # Step 4: Fetch metadata for all recommended songs
        print(f"📊 Step 4/4: Fetching metadata for recommended songs...", file=sys.stderr)

        # Fetch in parallel (but with rate limiting handled by service)
        async def fetch_song(rec: dict) -> Optional[Song]:
            """Fetch a single song's metadata."""
            try:
                song = await metadata_service.search_song(
                    artist=rec["artist"],
                    title=rec["title"]
                )
                if song:
                    print(f"  ✓ {song.display_name}", file=sys.stderr)
                else:
                    print(f"  ✗ Not found: {rec['artist']} - {rec['title']}", file=sys.stderr)
                return song
            except Exception as e:
                print(f"  ✗ Error fetching {rec['artist']} - {rec['title']}: {e}", file=sys.stderr)
                return None

        # Fetch all songs (with some concurrency but respect rate limits)
        songs = await asyncio.gather(
            *[fetch_song(rec) for rec in recommendations],
            return_exceptions=False
        )

        # Filter out None results
        valid_songs = [s for s in songs if s is not None]

        if len(valid_songs) < 3:
            return [TextContent(
                type="text",
                text=f"❌ Could only find {len(valid_songs)} songs from recommendations.\n\n"
                     "Not enough songs to create a meaningful playlist. Please try again."
            )]

        print(f"✅ Found metadata for {len(valid_songs)}/{len(recommendations)} songs", file=sys.stderr)

        # Step 5: Create playlist object
        # Determine primary genre
        all_genres = []
        for song in valid_songs:
            all_genres.extend(song.genres)

        primary_genre = None
        if all_genres:
            # Most common genre
            from collections import Counter
            genre_counts = Counter(all_genres)
            primary_genre = genre_counts.most_common(1)[0][0]

        metadata = PlaylistMetadata(
            title=f"{title_track.title} - Album Playlist",
            description=f"AI-curated playlist based on '{title_track.display_name}'\n\n"
                       f"Theme: {narrative.theme}\n"
                       f"{narrative.description}",
            primary_genre=primary_genre,
            genres=list(set(all_genres))[:5],  # Top 5 unique genres
            moods=[stage[0].value for stage in narrative.stages]
        )

        playlist = AlbumPlaylist(
            metadata=metadata,
            narrative=narrative,
            songs=valid_songs,
            title_track=title_track
        )

        # Format output
        return [TextContent(
            type="text",
            text=playlist.format_summary()
        )]

    except Exception as e:
        print(f"❌ Error in create_album_playlist: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)

        return [TextContent(
            type="text",
            text=f"❌ Playlist generation failed: {str(e)}\n\n"
                 "Please try again or check your API credentials."
        )]
