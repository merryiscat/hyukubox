"""Pytest configuration and fixtures."""

import json
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest


@pytest.fixture
def mock_responses() -> dict[str, Any]:
    """Load mock API responses from fixtures.

    Returns:
        Dictionary of mock responses for testing
    """
    fixtures_path = Path(__file__).parent / "fixtures" / "mock_responses.json"

    if not fixtures_path.exists():
        # Return empty dict if file doesn't exist yet
        return {}

    with open(fixtures_path) as f:
        return json.load(f)


@pytest.fixture
def temp_cache_dir(tmp_path: Path) -> Path:
    """Temporary cache directory for tests.

    Args:
        tmp_path: Pytest's temporary path fixture

    Returns:
        Path to temporary cache directory
    """
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    return cache_dir


@pytest.fixture(autouse=True)
def reset_env_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    """Reset environment variables for each test.

    Args:
        monkeypatch: Pytest's monkeypatch fixture
    """
    # Set test environment variables
    monkeypatch.setenv("SPOTIFY_CLIENT_ID", "test_spotify_id")
    monkeypatch.setenv("SPOTIFY_CLIENT_SECRET", "test_spotify_secret")
    monkeypatch.setenv("LASTFM_API_KEY", "test_lastfm_key")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test_anthropic_key")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")


# Model fixtures


@pytest.fixture
def mock_spotify_metadata():
    """Mock Spotify metadata for testing."""
    from hyukebox.models import SpotifyMetadata

    return SpotifyMetadata(
        track_id="test_track_id",
        artist="Test Artist",
        title="Test Song",
        album="Test Album",
        release_date="2024-01-01",
        duration_ms=180000,  # 3 minutes
        popularity=85,
        preview_url="https://spotify.com/preview",
        external_url="https://spotify.com/track/test",
        tempo=120.0,
        energy=0.8,
        danceability=0.7,
        valence=0.6,
        acousticness=0.3
    )


@pytest.fixture
def mock_lastfm_metadata():
    """Mock Last.fm metadata for testing."""
    from hyukebox.models import LastFmMetadata

    return LastFmMetadata(
        artist="Test Artist",
        title="Test Song",
        play_count=1000000,
        listeners=500000,
        tags=["pop", "dance", "electronic"],
        wiki_summary="A test song for testing purposes."
    )


@pytest.fixture
def mock_song(mock_spotify_metadata, mock_lastfm_metadata):
    """Mock complete Song object for testing."""
    from hyukebox.models import Song

    return Song(
        artist="Test Artist",
        title="Test Song",
        spotify=mock_spotify_metadata,
        lastfm=mock_lastfm_metadata,
        youtube_url="https://youtube.com/watch?v=test123",
        youtube_id="test123"
    )


@pytest.fixture
def mock_narrative_arc():
    """Mock narrative arc for testing."""
    from hyukebox.models import MoodType, NarrativeArc

    return NarrativeArc(
        theme="Test Journey",
        description="A test emotional journey",
        stages=[
            (MoodType.SADNESS, "Starting with sadness"),
            (MoodType.REFLECTION, "Moving to reflection"),
            (MoodType.HOPE, "Ending with hope")
        ],
        preferred_genres=["pop", "ballad"],
        tempo_progression="slow → moderate → upbeat",
        energy_progression="low → medium → high"
    )


# Service fixtures


@pytest.fixture
def mock_metadata_service(mock_song):
    """Mock MetadataAPIService for testing."""
    from hyukebox.services import MetadataAPIService

    service = MagicMock(spec=MetadataAPIService)

    # Mock search_song method
    async def mock_search(*args, **kwargs):
        return mock_song

    service.search_song = AsyncMock(side_effect=mock_search)

    return service


@pytest.fixture
def mock_llm_service(mock_narrative_arc):
    """Mock LLMService for testing."""
    from hyukebox.services import LLMService

    service = MagicMock(spec=LLMService)

    # Mock generate_narrative_arc
    async def mock_narrative(*args, **kwargs):
        return mock_narrative_arc

    # Mock generate_song_recommendations
    async def mock_recommendations(*args, **kwargs):
        return [
            {"artist": "Artist 1", "title": "Song 1"},
            {"artist": "Artist 2", "title": "Song 2"},
            {"artist": "Artist 3", "title": "Song 3"}
        ]

    service.generate_narrative_arc = AsyncMock(side_effect=mock_narrative)
    service.generate_song_recommendations = AsyncMock(side_effect=mock_recommendations)

    return service


@pytest.fixture
def mock_youtube_service():
    """Mock YouTubeService for testing."""
    from hyukebox.services import YouTubeService

    service = MagicMock(spec=YouTubeService)

    # Mock methods
    service.authenticate = MagicMock()
    service.create_playlist = MagicMock(
        return_value=("test_playlist_id", "https://youtube.com/playlist?list=test")
    )
    service.add_videos_to_playlist = MagicMock(return_value=3)
    service.search_video = MagicMock(return_value="test_video_id")
    service.create_playlist_with_search = MagicMock(
        return_value=("test_playlist_id", "https://youtube.com/playlist?list=test", 3)
    )

    return service
