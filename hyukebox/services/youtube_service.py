"""YouTube API service for playlist creation."""

import logging
import pickle
from pathlib import Path
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from ..config import settings

logger = logging.getLogger(__name__)

# YouTube API scopes
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]


class YouTubeService:
    """Service for creating and managing YouTube playlists.

    Handles OAuth authentication and playlist operations.
    """

    def __init__(self):
        """Initialize YouTube API client."""
        self.credentials = None
        self.youtube = None

    def authenticate(self) -> None:
        """Authenticate with YouTube API using OAuth 2.0.

        Loads credentials from token file or initiates OAuth flow.
        """
        token_path = settings.youtube_token_path
        credentials_path = settings.youtube_credentials_path

        # Load existing credentials
        if token_path.exists():
            with open(token_path, "rb") as token:
                self.credentials = pickle.load(token)

        # Refresh or get new credentials
        if not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                logger.info("Refreshing YouTube credentials")
                self.credentials.refresh(Request())
            else:
                logger.info("Starting OAuth flow for YouTube")
                if not credentials_path.exists():
                    raise FileNotFoundError(
                        f"YouTube credentials file not found: {credentials_path}\n"
                        "Please download OAuth 2.0 credentials from Google Cloud Console"
                    )

                flow = InstalledAppFlow.from_client_secrets_file(
                    str(credentials_path),
                    SCOPES
                )
                self.credentials = flow.run_local_server(port=0)

            # Save credentials
            token_path.parent.mkdir(parents=True, exist_ok=True)
            with open(token_path, "wb") as token:
                pickle.dump(self.credentials, token)

        # Build YouTube client
        self.youtube = build("youtube", "v3", credentials=self.credentials)
        logger.info("YouTube API client initialized")

    def create_playlist(
        self,
        title: str,
        description: str,
        privacy_status: str = "private"
    ) -> tuple[str, str]:
        """Create a new YouTube playlist.

        Args:
            title: Playlist title
            description: Playlist description
            privacy_status: Privacy setting (public, unlisted, private)

        Returns:
            Tuple of (playlist_id, playlist_url)
        """
        if not self.youtube:
            self.authenticate()

        try:
            # Create playlist
            request = self.youtube.playlists().insert(
                part="snippet,status",
                body={
                    "snippet": {
                        "title": title,
                        "description": description,
                        "defaultLanguage": "ko"
                    },
                    "status": {
                        "privacyStatus": privacy_status
                    }
                }
            )
            response = request.execute()

            playlist_id = response["id"]
            playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"

            logger.info(f"Created playlist: {title} ({playlist_id})")

            return playlist_id, playlist_url

        except Exception as e:
            logger.error(f"Failed to create playlist: {e}")
            raise

    def add_videos_to_playlist(
        self,
        playlist_id: str,
        video_ids: list[str]
    ) -> int:
        """Add videos to a playlist.

        Args:
            playlist_id: YouTube playlist ID
            video_ids: List of YouTube video IDs to add

        Returns:
            Number of videos successfully added
        """
        if not self.youtube:
            self.authenticate()

        added_count = 0

        for video_id in video_ids:
            try:
                request = self.youtube.playlistItems().insert(
                    part="snippet",
                    body={
                        "snippet": {
                            "playlistId": playlist_id,
                            "resourceId": {
                                "kind": "youtube#video",
                                "videoId": video_id
                            }
                        }
                    }
                )
                request.execute()
                added_count += 1
                logger.info(f"Added video {video_id} to playlist {playlist_id}")

            except Exception as e:
                logger.error(f"Failed to add video {video_id}: {e}")
                # Continue with next video

        return added_count

    def search_video(self, query: str, max_results: int = 1) -> Optional[str]:
        """Search for a video on YouTube.

        Args:
            query: Search query (e.g., "Artist - Song Title")
            max_results: Maximum number of results to return

        Returns:
            Video ID of first result, or None if not found
        """
        if not self.youtube:
            self.authenticate()

        try:
            request = self.youtube.search().list(
                part="snippet",
                q=query,
                type="video",
                videoCategoryId="10",  # Music category
                maxResults=max_results
            )
            response = request.execute()

            if response["items"]:
                video_id = response["items"][0]["id"]["videoId"]
                logger.info(f"Found video for '{query}': {video_id}")
                return video_id

            logger.warning(f"No video found for '{query}'")
            return None

        except Exception as e:
            logger.error(f"YouTube search error: {e}")
            return None

    def create_playlist_with_search(
        self,
        title: str,
        description: str,
        song_queries: list[str],
        privacy_status: str = "private"
    ) -> tuple[str, str, int]:
        """Create playlist and add songs by searching for them.

        Args:
            title: Playlist title
            description: Playlist description
            song_queries: List of search queries (e.g., ["Artist - Song"])
            privacy_status: Privacy setting

        Returns:
            Tuple of (playlist_id, playlist_url, songs_added_count)
        """
        # Create playlist
        playlist_id, playlist_url = self.create_playlist(
            title=title,
            description=description,
            privacy_status=privacy_status
        )

        # Search for videos and collect IDs
        video_ids = []
        for query in song_queries:
            video_id = self.search_video(query)
            if video_id:
                video_ids.append(video_id)

        # Add videos to playlist
        added_count = self.add_videos_to_playlist(playlist_id, video_ids)

        logger.info(
            f"Playlist created: {title} ({added_count}/{len(song_queries)} songs added)"
        )

        return playlist_id, playlist_url, added_count
