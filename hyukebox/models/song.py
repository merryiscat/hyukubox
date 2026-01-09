"""Song metadata models."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


class SpotifyMetadata(BaseModel):
    """Spotify-specific metadata."""

    track_id: str = Field(..., description="Spotify track ID")
    artist: str = Field(..., description="Primary artist name")
    title: str = Field(..., description="Track title")
    album: Optional[str] = Field(None, description="Album name")
    release_date: Optional[str] = Field(None, description="Release date (YYYY-MM-DD)")
    duration_ms: int = Field(..., description="Track duration in milliseconds")
    popularity: int = Field(..., ge=0, le=100, description="Popularity score 0-100")
    preview_url: Optional[HttpUrl] = Field(None, description="30-second preview URL")
    external_url: HttpUrl = Field(..., description="Spotify web URL")

    # Audio features
    tempo: Optional[float] = Field(None, description="Tempo in BPM")
    energy: Optional[float] = Field(None, ge=0, le=1, description="Energy 0-1")
    danceability: Optional[float] = Field(None, ge=0, le=1, description="Danceability 0-1")
    valence: Optional[float] = Field(None, ge=0, le=1, description="Valence (mood) 0-1")
    acousticness: Optional[float] = Field(None, ge=0, le=1, description="Acousticness 0-1")


class LastFmMetadata(BaseModel):
    """Last.fm-specific metadata."""

    artist: str = Field(..., description="Artist name")
    title: str = Field(..., description="Track title")
    play_count: Optional[int] = Field(None, description="Global play count")
    listeners: Optional[int] = Field(None, description="Unique listener count")
    tags: list[str] = Field(default_factory=list, description="Genre/mood tags")
    wiki_summary: Optional[str] = Field(None, description="Wikipedia summary")


class Song(BaseModel):
    """Complete song metadata combining Spotify and Last.fm data."""

    # Core identification
    artist: str = Field(..., description="Primary artist name")
    title: str = Field(..., description="Track title")

    # Metadata from APIs
    spotify: Optional[SpotifyMetadata] = Field(None, description="Spotify metadata")
    lastfm: Optional[LastFmMetadata] = Field(None, description="Last.fm metadata")

    # YouTube link (for playlist creation)
    youtube_url: Optional[HttpUrl] = Field(None, description="YouTube video URL")
    youtube_id: Optional[str] = Field(None, description="YouTube video ID")

    # Cache metadata
    cached_at: datetime = Field(default_factory=datetime.now, description="Cache timestamp")

    @property
    def display_name(self) -> str:
        """Human-readable song name."""
        return f"{self.artist} - {self.title}"

    @property
    def genres(self) -> list[str]:
        """Get genre tags from Last.fm."""
        if self.lastfm and self.lastfm.tags:
            return self.lastfm.tags
        return []

    @property
    def popularity_score(self) -> Optional[int]:
        """Get popularity from Spotify."""
        if self.spotify:
            return self.spotify.popularity
        return None

    def to_cache_key(self) -> str:
        """Generate cache key for this song."""
        return f"song:{self.artist.lower()}:{self.title.lower()}"

    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return self.model_dump(mode='json')


class SongSearchResult(BaseModel):
    """Result of a song search operation."""

    query: str = Field(..., description="Original search query")
    found: bool = Field(..., description="Whether song was found")
    song: Optional[Song] = Field(None, description="Found song metadata")
    error: Optional[str] = Field(None, description="Error message if search failed")
    searched_at: datetime = Field(default_factory=datetime.now, description="Search timestamp")
