"""LLM service for AI-powered playlist generation using Claude API."""

import json
import logging
from typing import Optional

from anthropic import Anthropic

from ..config import settings
from ..models import AlbumPlaylist, MoodType, NarrativeArc, PlaylistMetadata, Song

logger = logging.getLogger(__name__)


class LLMService:
    """Service for generating playlists using Claude AI.

    Uses Claude to analyze title track and generate thematically coherent
    playlist recommendations with narrative structure.
    """

    def __init__(self):
        """Initialize Claude API client."""
        self.client = Anthropic(api_key=settings.anthropic_api_key)
        self.model = settings.llm_model
        self.max_tokens = settings.llm_max_tokens
        self.temperature = settings.llm_temperature

    async def generate_narrative_arc(
        self,
        title_track: Song,
        playlist_size: int,
        user_prompt: Optional[str] = None
    ) -> NarrativeArc:
        """Generate narrative arc for playlist based on title track.

        Args:
            title_track: The seed/title track for the playlist
            playlist_size: Desired number of songs in playlist
            user_prompt: Optional user guidance for the narrative

        Returns:
            Generated narrative arc
        """
        # Build prompt
        prompt = self._build_narrative_prompt(title_track, playlist_size, user_prompt)

        try:
            # Call Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # Parse response
            response_text = response.content[0].text
            logger.info(f"Claude narrative response: {response_text[:200]}...")

            # Extract JSON from response
            narrative_data = self._parse_narrative_response(response_text)

            # Convert to NarrativeArc
            stages = [
                (MoodType(stage["mood"]), stage["description"])
                for stage in narrative_data["stages"]
            ]

            return NarrativeArc(
                theme=narrative_data["theme"],
                description=narrative_data["description"],
                stages=stages,
                preferred_genres=narrative_data.get("preferred_genres", []),
                tempo_progression=narrative_data.get("tempo_progression"),
                energy_progression=narrative_data.get("energy_progression")
            )

        except Exception as e:
            logger.error(f"Failed to generate narrative: {e}")
            raise

    async def generate_song_recommendations(
        self,
        title_track: Song,
        narrative: NarrativeArc,
        song_count: int,
        context_language: str = "korean"
    ) -> list[dict[str, str]]:
        """Generate song recommendations following narrative arc.

        Args:
            title_track: The seed/title track
            narrative: The narrative arc to follow
            song_count: Number of songs to recommend
            context_language: Language for recommendations (default: korean)

        Returns:
            List of song recommendations as {"artist": "...", "title": "..."}
        """
        # Build prompt
        prompt = self._build_recommendation_prompt(
            title_track,
            narrative,
            song_count,
            context_language
        )

        try:
            # Call Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # Parse response
            response_text = response.content[0].text
            logger.info(f"Claude recommendations: {response_text[:200]}...")

            # Extract JSON from response
            recommendations = self._parse_recommendations_response(response_text)

            return recommendations[:song_count]

        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
            raise

    def _build_narrative_prompt(
        self,
        title_track: Song,
        playlist_size: int,
        user_prompt: Optional[str]
    ) -> str:
        """Build prompt for narrative arc generation."""
        # Gather song info
        genres = ", ".join(title_track.genres) if title_track.genres else "Unknown"

        spotify_info = ""
        if title_track.spotify:
            spotify_info = f"""
Spotify Metadata:
- Popularity: {title_track.spotify.popularity}/100
- Energy: {title_track.spotify.energy}
- Valence (mood): {title_track.spotify.valence}
- Tempo: {title_track.spotify.tempo} BPM
- Danceability: {title_track.spotify.danceability}
"""

        prompt = f"""You are a music curator creating a {playlist_size}-song album-style playlist.

Title Track: "{title_track.artist} - {title_track.title}"
Genres: {genres}
{spotify_info}

Task: Create a narrative arc (emotional journey) for this playlist.

{f'User guidance: {user_prompt}' if user_prompt else ''}

Requirements:
1. Analyze the title track's mood, theme, and emotional content
2. Design a 5-7 stage emotional journey that flows naturally
3. Each stage should have a clear mood and description
4. The journey should feel cohesive and intentional

Available moods: joy, excitement, hope, peace, love, confidence, sadness, anger,
fear, regret, loneliness, despair, nostalgia, melancholy, ambivalence, reflection, determination

Output Format (JSON):
{{
    "theme": "Brief theme description (Korean or English)",
    "description": "Detailed narrative description",
    "stages": [
        {{"mood": "sadness", "description": "Stage description"}},
        ...
    ],
    "preferred_genres": ["genre1", "genre2"],
    "tempo_progression": "slow → moderate → upbeat",
    "energy_progression": "low → medium → high"
}}

Generate the narrative arc now:"""

        return prompt

    def _build_recommendation_prompt(
        self,
        title_track: Song,
        narrative: NarrativeArc,
        song_count: int,
        context_language: str
    ) -> str:
        """Build prompt for song recommendations."""
        # Format narrative stages
        stages_text = "\n".join([
            f"{i+1}. {mood.value}: {desc}"
            for i, (mood, desc) in enumerate(narrative.stages)
        ])

        prompt = f"""You are a music curator creating a {song_count}-song playlist.

Title Track: "{title_track.artist} - {title_track.title}"

Narrative Arc:
Theme: {narrative.theme}
{stages_text}

Preferred Genres: {", ".join(narrative.preferred_genres)}

Task: Recommend {song_count} songs that follow this narrative arc.

Requirements:
1. Include the title track as the first song
2. Each song should match the emotional stage it represents
3. Maintain musical coherence (genre, style, era)
4. Prefer {context_language} artists when appropriate, but include international artists for diversity
5. Songs should be real, well-known tracks

Output Format (JSON):
[
    {{"artist": "Artist Name", "title": "Song Title"}},
    ...
]

Generate {song_count} song recommendations now:"""

        return prompt

    def _parse_narrative_response(self, response_text: str) -> dict:
        """Parse narrative arc from Claude response."""
        try:
            # Try to extract JSON from response
            # Look for JSON block
            start_idx = response_text.find("{")
            end_idx = response_text.rfind("}") + 1

            if start_idx == -1 or end_idx == 0:
                raise ValueError("No JSON found in response")

            json_text = response_text[start_idx:end_idx]
            return json.loads(json_text)

        except Exception as e:
            logger.error(f"Failed to parse narrative response: {e}")
            logger.error(f"Response text: {response_text}")
            raise

    def _parse_recommendations_response(self, response_text: str) -> list[dict[str, str]]:
        """Parse song recommendations from Claude response."""
        try:
            # Try to extract JSON array from response
            start_idx = response_text.find("[")
            end_idx = response_text.rfind("]") + 1

            if start_idx == -1 or end_idx == 0:
                raise ValueError("No JSON array found in response")

            json_text = response_text[start_idx:end_idx]
            return json.loads(json_text)

        except Exception as e:
            logger.error(f"Failed to parse recommendations response: {e}")
            logger.error(f"Response text: {response_text}")
            raise
