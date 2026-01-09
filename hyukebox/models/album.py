"""Album/Playlist models."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl

from .narrative import NarrativeArc
from .song import Song


class PlaylistMetadata(BaseModel):
    """Metadata for a generated playlist."""

    title: str = Field(..., description="Playlist title")
    description: str = Field(..., description="Playlist description")

    # Categorization
    primary_genre: Optional[str] = Field(None, description="Primary music genre")
    genres: list[str] = Field(default_factory=list, description="All genres in playlist")
    moods: list[str] = Field(default_factory=list, description="Emotional moods")

    # Creator info
    created_by: str = Field(default="Hyukebox", description="Creator name")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")

    # YouTube playlist (if created)
    youtube_playlist_id: Optional[str] = Field(None, description="YouTube playlist ID")
    youtube_playlist_url: Optional[HttpUrl] = Field(None, description="YouTube playlist URL")


class AlbumPlaylist(BaseModel):
    """Generated album-style playlist with narrative structure.

    This is the main output of the create_album_playlist tool.
    """

    # Playlist metadata
    metadata: PlaylistMetadata = Field(..., description="Playlist metadata")

    # Narrative structure
    narrative: NarrativeArc = Field(..., description="Emotional narrative arc")

    # Songs in the playlist
    songs: list[Song] = Field(..., description="Songs in playlist order", min_length=1)

    # Title track (seed song)
    title_track: Song = Field(..., description="The seed/title track")

    @property
    def song_count(self) -> int:
        """Number of songs in the playlist."""
        return len(self.songs)

    @property
    def total_duration_ms(self) -> int:
        """Total duration of all songs in milliseconds."""
        total = 0
        for song in self.songs:
            if song.spotify and song.spotify.duration_ms:
                total += song.spotify.duration_ms
        return total

    @property
    def total_duration_str(self) -> str:
        """Human-readable total duration."""
        total_seconds = self.total_duration_ms // 1000
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60

        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"

    def format_summary(self) -> str:
        """Format a human-readable summary of the playlist."""
        lines = [
            f"📀 Album: {self.metadata.title}",
            f"🎤 Title Track: {self.title_track.display_name}",
            f"🎵 Genre: {self.metadata.primary_genre or 'Various'}",
            f"🎭 Mood: {' → '.join(self.narrative.stages[0][0].value for _ in range(min(3, len(self.narrative.stages))))}...",
            f"⏱️  Duration: {self.total_duration_str} ({self.song_count} songs)",
            "",
            "📝 Narrative Arc:",
            self.narrative.format_stages(),
            "",
            "🎵 Tracklist:",
        ]

        for i, song in enumerate(self.songs, 1):
            lines.append(f"  {i}. {song.display_name}")

        if self.metadata.youtube_playlist_url:
            lines.append("")
            lines.append(f"▶️  Playlist: {self.metadata.youtube_playlist_url}")

        return "\n".join(lines)

    def to_cache_key(self) -> str:
        """Generate cache key for this playlist."""
        return f"playlist:{self.title_track.to_cache_key()}:{self.metadata.created_at.isoformat()}"

    def get_youtube_video_ids(self) -> list[str]:
        """Extract YouTube video IDs from all songs."""
        video_ids = []
        for song in self.songs:
            if song.youtube_id:
                video_ids.append(song.youtube_id)
        return video_ids
