"""Data models for Hyukebox."""

from .album import AlbumPlaylist, PlaylistMetadata
from .narrative import MoodType, NarrativeArc, NARRATIVE_TEMPLATES
from .song import (
    LastFmMetadata,
    Song,
    SongSearchResult,
    SpotifyMetadata,
)

__all__ = [
    # Song models
    "Song",
    "SongSearchResult",
    "SpotifyMetadata",
    "LastFmMetadata",
    # Narrative models
    "NarrativeArc",
    "MoodType",
    "NARRATIVE_TEMPLATES",
    # Album/Playlist models
    "AlbumPlaylist",
    "PlaylistMetadata",
]
