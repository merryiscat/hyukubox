"""Narrative arc models for playlist generation."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class MoodType(str, Enum):
    """Emotional mood types for narrative progression."""

    # Positive emotions
    JOY = "joy"
    EXCITEMENT = "excitement"
    HOPE = "hope"
    PEACE = "peace"
    LOVE = "love"
    CONFIDENCE = "confidence"

    # Negative emotions
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    REGRET = "regret"
    LONELINESS = "loneliness"
    DESPAIR = "despair"

    # Neutral/Complex
    NOSTALGIA = "nostalgia"
    MELANCHOLY = "melancholy"
    AMBIVALENCE = "ambivalence"
    REFLECTION = "reflection"
    DETERMINATION = "determination"


class NarrativeArc(BaseModel):
    """Emotional narrative arc for a playlist.

    Defines the emotional journey of a playlist from start to finish.
    """

    # Narrative structure
    theme: str = Field(..., description="Main theme of the playlist (e.g., '이별 극복')")
    description: str = Field(..., description="Detailed narrative description")

    # Emotional progression (5-7 stages typical)
    stages: list[tuple[MoodType, str]] = Field(
        ...,
        description="List of (mood, description) tuples for each stage",
        min_length=3,
        max_length=10
    )

    # Genre/Style preferences
    preferred_genres: list[str] = Field(
        default_factory=list,
        description="Preferred music genres for this narrative"
    )

    # Musical characteristics
    tempo_progression: Optional[str] = Field(
        None,
        description="Tempo flow (e.g., 'slow → moderate → upbeat')"
    )

    energy_progression: Optional[str] = Field(
        None,
        description="Energy flow (e.g., 'low → building → high')"
    )

    @property
    def stage_count(self) -> int:
        """Number of emotional stages in this arc."""
        return len(self.stages)

    def get_stage_mood(self, index: int) -> Optional[MoodType]:
        """Get mood for a specific stage."""
        if 0 <= index < len(self.stages):
            return self.stages[index][0]
        return None

    def get_stage_description(self, index: int) -> Optional[str]:
        """Get description for a specific stage."""
        if 0 <= index < len(self.stages):
            return self.stages[index][1]
        return None

    def format_stages(self) -> str:
        """Format stages as human-readable text."""
        lines = []
        for i, (mood, desc) in enumerate(self.stages, 1):
            lines.append(f"{i}. {mood.value.title()}: {desc}")
        return "\n".join(lines)


# Predefined narrative templates
NARRATIVE_TEMPLATES = {
    "breakup_recovery": NarrativeArc(
        theme="이별 극복",
        description="이별의 아픔에서 시작해 회복과 성장으로 나아가는 감정 여정",
        stages=[
            (MoodType.SADNESS, "이별 직후의 상실감과 슬픔"),
            (MoodType.REGRET, "미련과 자책, 되돌아보기"),
            (MoodType.DESPAIR, "감정의 바닥, 가장 힘든 순간"),
            (MoodType.REFLECTION, "자기 성찰과 받아들이기"),
            (MoodType.DETERMINATION, "다시 일어서기, 앞으로 나아가기"),
            (MoodType.HOPE, "새로운 시작에 대한 희망"),
        ],
        preferred_genres=["ballad", "r&b", "soul", "indie"],
        tempo_progression="slow → slow → moderate → moderate → upbeat",
        energy_progression="low → low → building → building → high"
    ),

    "night_drive": NarrativeArc(
        theme="야간 드라이브",
        description="밤의 고요함 속에서 펼쳐지는 몽환적이고 감성적인 음악 여행",
        stages=[
            (MoodType.PEACE, "고요한 밤의 시작"),
            (MoodType.NOSTALGIA, "지나간 추억을 떠올리며"),
            (MoodType.MELANCHOLY, "감성적이고 몽환적인 분위기"),
            (MoodType.REFLECTION, "생각에 잠기는 순간"),
            (MoodType.PEACE, "평온한 마무리"),
        ],
        preferred_genres=["electronic", "indie", "alternative", "ambient"],
        tempo_progression="moderate → slow → slow → moderate",
        energy_progression="medium → low → low → medium"
    ),

    "workout_motivation": NarrativeArc(
        theme="운동 동기부여",
        description="점점 고조되는 에너지로 운동 의욕을 끌어올리는 플레이리스트",
        stages=[
            (MoodType.DETERMINATION, "시작을 위한 마음 다지기"),
            (MoodType.CONFIDENCE, "자신감 상승, 몸 풀기"),
            (MoodType.EXCITEMENT, "본격적인 운동, 에너지 폭발"),
            (MoodType.CONFIDENCE, "마지막 스퍼트, 끝까지 밀어붙이기"),
        ],
        preferred_genres=["hip-hop", "electronic", "rock", "pop"],
        tempo_progression="moderate → upbeat → very upbeat → upbeat",
        energy_progression="medium → high → very high → high"
    ),
}
