"""Metadata API service integrating Spotify and Last.fm."""

import asyncio
import logging
from typing import Optional

import httpx
import pylast
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from ..config import settings
from ..models import LastFmMetadata, Song, SpotifyMetadata
from ..utils.cache import MetadataCache
from ..utils.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)


class MetadataAPIService:
    """Service for fetching song metadata from Spotify and Last.fm.

    Combines data from both APIs to provide comprehensive song information.
    """

    def __init__(self):
        """Initialize API clients and rate limiters."""
        # Spotify client
        auth_manager = SpotifyClientCredentials(
            client_id=settings.spotify_client_id,
            client_secret=settings.spotify_client_secret
        )
        self.spotify = spotipy.Spotify(auth_manager=auth_manager)

        # Last.fm client
        self.lastfm = pylast.LastFMNetwork(
            api_key=settings.lastfm_api_key
        )

        # Rate limiters
        self.spotify_limiter = RateLimiter(settings.spotify_rate_limit)
        self.lastfm_limiter = RateLimiter(settings.lastfm_rate_limit)

        # Cache
        self.cache = MetadataCache(settings.cache_dir)

    async def search_song(
        self,
        artist: str,
        title: str,
        use_cache: bool = True
    ) -> Optional[Song]:
        """Search for a song using both Spotify and Last.fm.

        Args:
            artist: Artist name
            title: Song title
            use_cache: Whether to use cached results (default: True)

        Returns:
            Song object with combined metadata, or None if not found
        """
        # Check cache first
        cache_key = f"song:{artist.lower()}:{title.lower()}"
        if use_cache:
            cached = self.cache.get(cache_key)
            if cached:
                logger.info(f"Cache hit for {artist} - {title}")
                return Song(**cached)

        # Fetch from both APIs in parallel
        spotify_task = self._search_spotify(artist, title)
        lastfm_task = self._search_lastfm(artist, title)

        spotify_meta, lastfm_meta = await asyncio.gather(
            spotify_task,
            lastfm_task,
            return_exceptions=True
        )

        # Handle exceptions
        if isinstance(spotify_meta, Exception):
            logger.error(f"Spotify search failed: {spotify_meta}")
            spotify_meta = None

        if isinstance(lastfm_meta, Exception):
            logger.error(f"Last.fm search failed: {lastfm_meta}")
            lastfm_meta = None

        # If both failed, return None
        if not spotify_meta and not lastfm_meta:
            logger.warning(f"No metadata found for {artist} - {title}")
            return None

        # Create Song object
        song = Song(
            artist=artist,
            title=title,
            spotify=spotify_meta,
            lastfm=lastfm_meta
        )

        # Cache result
        self.cache.set(cache_key, song.to_dict(), ttl=settings.cache_ttl)

        return song

    async def _search_spotify(self, artist: str, title: str) -> Optional[SpotifyMetadata]:
        """Search Spotify for track metadata.

        Args:
            artist: Artist name
            title: Track title

        Returns:
            SpotifyMetadata or None if not found
        """
        await self.spotify_limiter.acquire()

        try:
            # Search for track
            query = f"artist:{artist} track:{title}"
            results = self.spotify.search(q=query, type="track", limit=1)

            if not results or not results.get("tracks", {}).get("items"):
                return None

            track = results["tracks"]["items"][0]

            # Get audio features
            audio_features = None
            try:
                features = self.spotify.audio_features([track["id"]])[0]
                audio_features = features if features else {}
            except Exception as e:
                logger.warning(f"Failed to get audio features: {e}")
                audio_features = {}

            # Parse metadata
            return SpotifyMetadata(
                track_id=track["id"],
                artist=track["artists"][0]["name"],
                title=track["name"],
                album=track["album"]["name"] if track.get("album") else None,
                release_date=track["album"].get("release_date"),
                duration_ms=track["duration_ms"],
                popularity=track["popularity"],
                preview_url=track.get("preview_url"),
                external_url=track["external_urls"]["spotify"],
                tempo=audio_features.get("tempo"),
                energy=audio_features.get("energy"),
                danceability=audio_features.get("danceability"),
                valence=audio_features.get("valence"),
                acousticness=audio_features.get("acousticness"),
            )

        except Exception as e:
            logger.error(f"Spotify API error: {e}")
            raise

    async def _search_lastfm(self, artist: str, title: str) -> Optional[LastFmMetadata]:
        """Search Last.fm for track metadata.

        Args:
            artist: Artist name
            title: Track title

        Returns:
            LastFmMetadata or None if not found
        """
        await self.lastfm_limiter.acquire()

        try:
            # Get track info (blocking call, run in executor)
            loop = asyncio.get_event_loop()
            track = await loop.run_in_executor(
                None,
                self.lastfm.get_track,
                artist,
                title
            )

            # Get track info
            info = await loop.run_in_executor(None, track.get_info)

            # Parse tags
            tags = []
            try:
                top_tags = await loop.run_in_executor(None, track.get_top_tags, 5)
                tags = [tag.item.name for tag in top_tags]
            except Exception as e:
                logger.warning(f"Failed to get Last.fm tags: {e}")

            # Parse wiki
            wiki_summary = None
            try:
                wiki = track.get_wiki_summary()
                if wiki:
                    wiki_summary = wiki
            except Exception:
                pass

            return LastFmMetadata(
                artist=artist,
                title=title,
                play_count=int(info.get("playcount", 0)),
                listeners=int(info.get("listeners", 0)),
                tags=tags,
                wiki_summary=wiki_summary
            )

        except pylast.WSError as e:
            if "Track not found" in str(e):
                logger.info(f"Track not found on Last.fm: {artist} - {title}")
                return None
            logger.error(f"Last.fm API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Last.fm error: {e}")
            raise

    async def search_youtube_url(self, artist: str, title: str) -> Optional[str]:
        """Search YouTube for song video URL.

        Args:
            artist: Artist name
            title: Song title

        Returns:
            YouTube video ID or None if not found
        """
        try:
            # Use YouTube search via httpx
            query = f"{artist} {title} official audio"

            async with httpx.AsyncClient(timeout=10.0) as client:
                # Simple YouTube search URL (this would need YouTube Data API in production)
                # For now, we'll construct a search URL
                # In production, use google-api-python-client
                search_url = f"https://www.youtube.com/results?search_query={query}"

                logger.info(f"YouTube search: {query}")
                # TODO: Implement proper YouTube Data API search
                # This is a placeholder - actual implementation needs YouTube API key

                return None

        except Exception as e:
            logger.error(f"YouTube search error: {e}")
            return None

    async def enrich_song_with_youtube(self, song: Song) -> Song:
        """Add YouTube URL to song metadata.

        Args:
            song: Song object to enrich

        Returns:
            Enriched song object
        """
        if song.youtube_id or song.youtube_url:
            return song  # Already has YouTube data

        youtube_id = await self.search_youtube_url(song.artist, song.title)
        if youtube_id:
            song.youtube_id = youtube_id
            song.youtube_url = f"https://www.youtube.com/watch?v={youtube_id}"

        return song
