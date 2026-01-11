"""
Hyukebox MCP Server
Last.fm API를 활용한 음악 메타데이터 검색 서버
"""
import os
import sys
from pathlib import Path

import httpx
from fastmcp import FastMCP
from mcp.types import TextContent

# 환경변수 로드
from dotenv import load_dotenv

# 프로젝트 루트의 .env 파일 로드
project_root = Path(__file__).parent.parent
env_path = project_root / ".env"
load_dotenv(env_path)

# API 설정
LASTFM_API_KEY = os.getenv("LASTFM_API_KEY")
LASTFM_API_URL = "https://ws.audioscrobbler.com/2.0/"
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 서사 생성용 프롬프트 템플릿
NARRATIVE_SYSTEM_PROMPT = """당신은 음악 감정 분석 전문가입니다.
곡의 가사와 배경 정보를 바탕으로 곡의 주제를 요약하고,
감정/스토리/무드를 복합적으로 고려한 서사 흐름을 분석합니다."""

NARRATIVE_USER_TEMPLATE = """다음은 '{artist} - {title}' 곡에 대한 가사 정보입니다:

{search_content}

이 곡에 대해 다음을 분석해주세요:

1. 요약: 곡의 주제와 내용을 1-2문장으로 요약
2. 서사 흐름: 곡의 감정적 여정을 3-7단계로 나누어 분석
   - 각 단계는 감정(기쁨/슬픔/분노 등) + 스토리(이별/회복/시작 등) + 무드(우울/희망/담담 등)를 복합적으로 표현
   - 곡의 복잡도에 따라 3-7단계 중 적절한 개수를 선택
3. 키워드: 각 단계를 대표하는 핵심 키워드 3-5개

출력 형식 (JSON):
{{{{
  "summary": "곡의 주제 요약 (1-2문장)",
  "narrative": {{{{
    "stage_count": 5,
    "stages": [
      {{{{
        "step": 1,
        "title": "이별 → 미련과 자책",
        "description": "이별 직후 상대방에 대한 미련과 자책감이 교차하는 복잡한 감정 상태",
        "keywords": ["이별 노래", "후회", "자책", "미련"]
      }}}},
      ...
    ]
  }}}}
}}}}

예시 출력 (화사 - Good Goodbye):
{{{{
  "summary": "사랑의 상처를 딛고 상대방과의 이별을 담담하게 받아들이며, 자신을 위한 새로운 시작을 다짐하는 내용",
  "narrative": {{{{
    "stage_count": 5,
    "stages": [
      {{{{
        "step": 1,
        "title": "이별 → 미련과 자책",
        "description": "이별 직후 상대방에 대한 미련과 자책감이 교차하는 복잡한 감정",
        "keywords": ["이별 노래", "후회", "자책"]
      }}}},
      {{{{
        "step": 2,
        "title": "감정 바닥",
        "description": "슬픔과 우울이 극에 달하는 감정의 최저점",
        "keywords": ["눈물", "우울", "슬픔"]
      }}}},
      {{{{
        "step": 3,
        "title": "자존 회복",
        "description": "자존감을 되찾고 스스로를 다시 사랑하기 시작",
        "keywords": ["회복", "자존감", "성장"]
      }}}},
      {{{{
        "step": 4,
        "title": "이별 직후의 감정 정리",
        "description": "지난 관계를 담담하게 정리하고 받아들임",
        "keywords": ["정리", "담담함", "수용"]
      }}}},
      {{{{
        "step": 5,
        "title": "새로운 시작",
        "description": "앞으로 나아갈 희망과 새로운 시작에 대한 다짐",
        "keywords": ["시작", "희망", "다짐"]
      }}}}
    ]
  }}}}
}}}}

위 형식으로 '{artist} - {title}' 곡을 분석해주세요."""

# ============================================================
# 추천 시스템용 평가 프롬프트 (비활성화됨 - 존재하지 않는 곡 추천 문제)
# ============================================================

# EVALUATION_SYSTEM_PROMPT = """당신은 음악 큐레이션 전문가입니다.
# 주어진 서사 흐름의 특정 단계에 대해 후보곡들이 얼마나 적합한지 평가합니다.
#
# 평가 기준:
# 1. 곡의 감정/분위기가 서사 단계와 일치하는가?
# 2. 가사 테마가 서사 내용과 연결되는가?
# 3. 음악적 분위기(템포, 멜로디, 장르)가 적합한가?
# 4. 키워드가 곡의 특성과 매칭되는가?
#
# 점수 기준 (0-100):
# - 90-100: 완벽히 일치, 서사 단계를 매우 잘 표현
# - 70-89: 잘 일치, 서사 단계와 명확한 연관성
# - 50-69: 부분적 일치, 일부 요소만 연결됨
# - 30-49: 약한 연관성, 분위기만 비슷함
# - 0-29: 불일치, 서사 단계와 맞지 않음
#
# 각 곡에 대해 점수와 간단한 이유를 제공해주세요."""
#
# EVALUATION_USER_TEMPLATE = """원곡 서사 요약: {summary}
#
# 현재 평가할 서사 단계:
# [{step}단계] {stage_title}
# 설명: {stage_description}
# 키워드: {keywords}
#
# 후보곡 리스트:
# {candidates_list}
#
# 위 후보곡들이 이 서사 단계에 얼마나 적합한지 평가해주세요.
#
# 출력 형식 (JSON):
# {{
#   "evaluations": [
#     {{"artist": "아티스트1", "title": "곡제목1", "score": 85, "reason": "평가 이유"}},
#     {{"artist": "아티스트2", "title": "곡제목2", "score": 72, "reason": "평가 이유"}},
#     ...
#   ]
# }}"""

# FastMCP 서버 생성
mcp = FastMCP("Hyukebox")


@mcp.tool()
async def search_song(artist: str, title: str) -> TextContent:
    """곡의 기본 정보, 태그, 비슷한 곡을 검색합니다.

    "화사의 good goodbye 정보 알려줘", "비슷한 곡 추천해줘" 같은 요청에 사용합니다.

    Args:
        artist: 아티스트 이름
        title: 곡 제목

    Returns:
        곡 기본 정보 + 태그 + 유사곡 리스트
    """
    # API 키 확인
    if not LASTFM_API_KEY:
        return TextContent(
            type="text",
            text="Error: LASTFM_API_KEY가 .env 파일에 설정되지 않았습니다."
        )

    try:
        import json
        import asyncio

        async with httpx.AsyncClient(timeout=30.0) as client:
            # 여러 API 병렬 호출
            base_params = {
                "api_key": LASTFM_API_KEY,
                "artist": artist,
                "track": title,
                "format": "json"
            }

            # 1. track.getInfo - 기본 곡 정보
            info_params = {**base_params, "method": "track.getInfo"}

            # 2. track.getSimilar - 유사곡
            similar_params = {**base_params, "method": "track.getSimilar", "limit": 10}

            # 3. track.getTopTags - 태그
            tags_params = {**base_params, "method": "track.getTopTags"}

            # 병렬 호출
            info_task = client.get(LASTFM_API_URL, params=info_params)
            similar_task = client.get(LASTFM_API_URL, params=similar_params)
            tags_task = client.get(LASTFM_API_URL, params=tags_params)

            info_res, similar_res, tags_res = await asyncio.gather(
                info_task, similar_task, tags_task,
                return_exceptions=True
            )

            # 응답 수집
            all_data = {}

            # track.getInfo
            if not isinstance(info_res, Exception):
                info_res.raise_for_status()
                info_data = info_res.json()
                if "error" not in info_data:
                    all_data["track_info"] = info_data

            # track.getSimilar
            if not isinstance(similar_res, Exception):
                similar_res.raise_for_status()
                similar_data = similar_res.json()
                if "error" not in similar_data:
                    all_data["similar_tracks"] = similar_data

            # track.getTopTags
            if not isinstance(tags_res, Exception):
                tags_res.raise_for_status()
                tags_data = tags_res.json()
                if "error" not in tags_data:
                    all_data["top_tags"] = tags_data

            # 결과 포맷팅
            result_parts = []

            # 기본 정보
            if "track_info" in all_data:
                track = all_data["track_info"].get("track", {})
                result_parts.append("=== 곡 정보 ===")
                result_parts.append(f"곡명: {track.get('name', 'N/A')}")
                result_parts.append(f"아티스트: {track.get('artist', {}).get('name', 'N/A')}")

                album = track.get("album", {})
                if album:
                    result_parts.append(f"앨범: {album.get('title', 'N/A')}")

                playcount = track.get("playcount", "0")
                listeners = track.get("listeners", "0")
                try:
                    result_parts.append(f"재생 횟수: {int(playcount):,} 회")
                    result_parts.append(f"청취자: {int(listeners):,} 명")
                except:
                    result_parts.append(f"재생 횟수: {playcount} 회")
                    result_parts.append(f"청취자: {listeners} 명")

            # 태그
            if "top_tags" in all_data:
                tags = all_data["top_tags"].get("toptags", {}).get("tag", [])
                if tags:
                    tag_names = [t.get("name") for t in tags[:10]]
                    result_parts.append(f"\n태그: {', '.join(tag_names)}")

            # 유사곡
            if "similar_tracks" in all_data:
                similar = all_data["similar_tracks"].get("similartracks", {}).get("track", [])
                if similar:
                    result_parts.append("\n=== 비슷한 곡 ===")
                    for i, sim in enumerate(similar[:10], 1):
                        sim_name = sim.get("name", "")
                        sim_artist = sim.get("artist", {}).get("name", "")
                        match = sim.get("match", "0")
                        result_parts.append(f"{i}. {sim_artist} - {sim_name} (유사도: {float(match)*100:.0f}%)")

            return TextContent(type="text", text="\n".join(result_parts))

    except httpx.HTTPStatusError as e:
        return TextContent(
            type="text",
            text=f"HTTP Error: {e.response.status_code} - {e.response.text}"
        )
    except Exception as e:
        return TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )


def extract_json_from_response(text: str) -> dict:
    """OpenAI 응답에서 JSON 추출 및 파싱"""
    import json
    import re

    # 1. JSON 코드 블록 찾기 (```json ... ```)
    json_match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
    if json_match:
        return json.loads(json_match.group(1))

    # 2. 일반 JSON 블록 찾기 ({ ... })
    brace_start = text.find('{')
    brace_end = text.rfind('}') + 1
    if brace_start != -1 and brace_end > brace_start:
        json_str = text[brace_start:brace_end]
        return json.loads(json_str)

    # 3. 파싱 실패
    raise ValueError("No valid JSON found in response")


def format_narrative_output(artist: str, title: str, data: dict) -> str:
    """JSON 데이터를 사람이 읽기 좋은 텍스트로 변환"""
    lines = [
        f"=== {artist} - {title} ===",
        "",
        f"요약: {data['summary']}",
        "",
        f"서사 흐름 ({data['narrative']['stage_count']}단계):",
    ]

    # 서사 단계 제목
    for stage in data['narrative']['stages']:
        lines.append(f"{stage['step']}. {stage['title']}")

    lines.append("")
    lines.append("각 단계별 키워드:")

    # 키워드
    for stage in data['narrative']['stages']:
        keywords = ", ".join(stage['keywords'])
        lines.append(f"{stage['step']}. {keywords}")

    return "\n".join(lines)


@mcp.tool()
async def describe_song(artist: str, title: str) -> TextContent:
    """곡의 주제를 요약하고 감정/스토리/무드 복합 서사를 생성합니다.

    "이 곡은 어떤 노래야?", "이 곡 서사 알려줘" 같은 요청에 사용합니다.

    Args:
        artist: 아티스트 이름
        title: 곡 제목

    Returns:
        요약 + 서사 흐름 (3-7단계) + 각 단계별 키워드
    """
    # API 키 확인
    if not TAVILY_API_KEY:
        return TextContent(
            type="text",
            text="Error: TAVILY_API_KEY가 .env 파일에 설정되지 않았습니다."
        )

    if not OPENAI_API_KEY:
        return TextContent(
            type="text",
            text="Error: OPENAI_API_KEY가 .env 파일에 설정되지 않았습니다."
        )

    try:
        import json

        async with httpx.AsyncClient(timeout=30.0) as client:
            # 1. Tavily API로 가사 웹 검색
            search_query = f"{artist} {title} 가사"

            tavily_payload = {
                "api_key": TAVILY_API_KEY,
                "query": search_query,
                "max_results": 3
            }

            try:
                tavily_response = await client.post(
                    "https://api.tavily.com/search",
                    json=tavily_payload
                )
                tavily_response.raise_for_status()
                tavily_data = tavily_response.json()
            except httpx.HTTPStatusError as e:
                return TextContent(
                    type="text",
                    text=f"Tavily API Error (status {e.response.status_code}): {e.response.text}"
                )

            # 검색 결과 추출
            results = tavily_data.get("results", [])
            if not results:
                return TextContent(
                    type="text",
                    text=f"웹에서 '{artist} - {title}' 가사 정보를 찾지 못했습니다."
                )

            # 검색 결과 텍스트 합치기
            search_content = "\n\n".join([
                f"제목: {r.get('title', '')}\n내용: {r.get('content', '')}"
                for r in results[:3]
            ])

            # 2. OpenAI API로 서사 생성
            openai_payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {
                        "role": "system",
                        "content": NARRATIVE_SYSTEM_PROMPT
                    },
                    {
                        "role": "user",
                        "content": NARRATIVE_USER_TEMPLATE.format(
                            artist=artist,
                            title=title,
                            search_content=search_content
                        )
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 2000
            }

            try:
                openai_response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    json=openai_payload,
                    headers={
                        "Authorization": f"Bearer {OPENAI_API_KEY}",
                        "Content-Type": "application/json"
                    }
                )
                openai_response.raise_for_status()
                openai_data = openai_response.json()
            except httpx.HTTPStatusError as e:
                error_detail = e.response.text
                return TextContent(
                    type="text",
                    text=f"OpenAI API Error (status {e.response.status_code}): {error_detail}"
                )

            # 응답 파싱
            response_text = openai_data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()

            if not response_text:
                return TextContent(
                    type="text",
                    text="서사 생성에 실패했습니다."
                )

            try:
                # JSON 추출 및 파싱
                narrative_data = extract_json_from_response(response_text)

                # 사람이 읽기 좋은 형식으로 변환
                result = format_narrative_output(artist, title, narrative_data)

            except (ValueError, json.JSONDecodeError, KeyError) as e:
                # 파싱 실패 시 원본 텍스트 반환 (fallback)
                result = f"=== {artist} - {title} ===\n\n{response_text}"

            return TextContent(type="text", text=result)

    except httpx.HTTPStatusError as e:
        return TextContent(
            type="text",
            text=f"HTTP Error: {e.response.status_code} - {e.response.text}"
        )
    except Exception as e:
        return TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )


# ============================================================
# 추천 시스템 헬퍼 함수들 (비활성화됨 - 존재하지 않는 곡 추천 문제)
# ============================================================

def score_to_weight(score: float, temperature: float = 1.0) -> float:
    """점수를 가중치로 변환 (지수 스케일)

    Args:
        score: 0-100 사이의 점수
        temperature: 온도 파라미터
            - 낮을수록 (0.5) 상위곡에 집중
            - 높을수록 (2.0) 다양성 증가

    Returns:
        변환된 가중치 값
    """
    import math
    normalized = score / 100.0
    weight = math.exp(normalized / temperature)
    return weight


async def _get_narrative_json(artist: str, title: str) -> dict:
    """describe_song 로직을 재사용하여 서사 JSON 반환

    Args:
        artist: 아티스트 이름
        title: 곡 제목

    Returns:
        서사 데이터 (dict with summary, narrative.stages)

    Raises:
        Exception: API 호출 실패 또는 파싱 실패
    """
    import json

    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. Tavily API로 가사 웹 검색
        search_query = f"{artist} {title} 가사"

        tavily_payload = {
            "api_key": TAVILY_API_KEY,
            "query": search_query,
            "max_results": 3
        }

        tavily_response = await client.post(
            "https://api.tavily.com/search",
            json=tavily_payload
        )
        tavily_response.raise_for_status()
        tavily_data = tavily_response.json()

        # 검색 결과 추출
        results = tavily_data.get("results", [])
        if not results:
            raise ValueError(f"웹에서 '{artist} - {title}' 가사 정보를 찾지 못했습니다.")

        # 검색 결과 텍스트 합치기
        search_content = "\n\n".join([
            f"제목: {r.get('title', '')}\n내용: {r.get('content', '')}"
            for r in results[:3]
        ])

        # 2. OpenAI API로 서사 생성
        openai_payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "system",
                    "content": NARRATIVE_SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": NARRATIVE_USER_TEMPLATE.format(
                        artist=artist,
                        title=title,
                        search_content=search_content
                    )
                }
            ],
            "temperature": 0.7,
            "max_tokens": 2000
        }

        openai_response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            json=openai_payload,
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
        )
        openai_response.raise_for_status()
        openai_data = openai_response.json()

        # 응답 파싱
        response_text = openai_data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()

        if not response_text:
            raise ValueError("서사 생성에 실패했습니다.")

        # JSON 추출 및 파싱
        narrative_data = extract_json_from_response(response_text)
        return narrative_data


async def search_candidates_for_keyword(keyword: str, limit: int = 15) -> list[dict]:
    """키워드로 Last.fm 검색 (tag.getTopTracks + track.search fallback)

    Args:
        keyword: 검색할 키워드
        limit: 반환할 곡 수

    Returns:
        후보곡 리스트 [{"artist": "...", "title": "..."}, ...]
    """
    candidates = []

    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1차: tag.getTopTracks
        tag_params = {
            "method": "tag.getTopTracks",
            "tag": keyword,
            "api_key": LASTFM_API_KEY,
            "format": "json",
            "limit": limit
        }

        try:
            tag_response = await client.get(LASTFM_API_URL, params=tag_params)
            tag_response.raise_for_status()
            tag_data = tag_response.json()

            if "tracks" in tag_data and "track" in tag_data["tracks"]:
                for track in tag_data["tracks"]["track"][:limit]:
                    candidates.append({
                        "artist": track.get("artist", {}).get("name", "") if isinstance(track.get("artist"), dict) else track.get("artist", ""),
                        "title": track.get("name", "")
                    })
        except Exception:
            pass  # 실패해도 계속 진행

        # 2차: track.search (부족할 경우)
        if len(candidates) < 10:
            search_params = {
                "method": "track.search",
                "track": keyword,
                "api_key": LASTFM_API_KEY,
                "format": "json",
                "limit": 10
            }

            try:
                search_response = await client.get(LASTFM_API_URL, params=search_params)
                search_response.raise_for_status()
                search_data = search_response.json()

                if "results" in search_data and "trackmatches" in search_data["results"]:
                    tracks = search_data["results"]["trackmatches"].get("track", [])
                    for track in tracks:
                        candidate = {
                            "artist": track.get("artist", ""),
                            "title": track.get("name", "")
                        }
                        # 중복 체크
                        key = f"{candidate['artist']}||{candidate['title']}"
                        existing_keys = [f"{c['artist']}||{c['title']}" for c in candidates]
                        if key not in existing_keys:
                            candidates.append(candidate)
            except Exception:
                pass

    return candidates[:limit]


async def _search_candidates_for_narrative(narrative: dict) -> list[dict]:
    """모든 서사 단계의 키워드를 병렬로 검색하여 후보곡 수집

    Args:
        narrative: 서사 JSON 데이터

    Returns:
        중복 제거된 후보곡 리스트
    """
    import asyncio

    stages = narrative.get("narrative", {}).get("stages", [])

    # 모든 키워드 추출
    all_keywords = []
    for stage in stages:
        keywords = stage.get("keywords", [])
        all_keywords.extend(keywords)

    # 병렬 검색
    search_tasks = [search_candidates_for_keyword(kw, limit=15) for kw in all_keywords]
    results = await asyncio.gather(*search_tasks, return_exceptions=True)

    # 결과 합치기 및 중복 제거
    all_candidates = []
    seen_keys = set()

    for result in results:
        if isinstance(result, Exception):
            continue
        for candidate in result:
            key = f"{candidate['artist']}||{candidate['title']}"
            if key not in seen_keys:
                all_candidates.append(candidate)
                seen_keys.add(key)

    return all_candidates


async def _llm_evaluate_stage(
    stage: dict,
    candidates: list[dict],
    summary: str
) -> list[dict]:
    """특정 서사 단계에 대해 후보곡 LLM 평가

    Args:
        stage: 서사 단계 정보
        candidates: 후보곡 리스트
        summary: 원곡 서사 요약

    Returns:
        평가된 후보곡 리스트 [{"artist": ..., "title": ..., "score": ..., "reason": ...}, ...]
    """
    import json

    if not candidates:
        return []

    # 후보곡 리스트 포맷팅
    candidates_text = "\n".join([
        f"{i+1}. {c['artist']} - {c['title']}"
        for i, c in enumerate(candidates)
    ])

    keywords_text = ", ".join(stage.get("keywords", []))

    # OpenAI API 호출
    async with httpx.AsyncClient(timeout=60.0) as client:
        openai_payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "system",
                    "content": EVALUATION_SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": EVALUATION_USER_TEMPLATE.format(
                        summary=summary,
                        step=stage.get("step", 1),
                        stage_title=stage.get("title", ""),
                        stage_description=stage.get("description", ""),
                        keywords=keywords_text,
                        candidates_list=candidates_text
                    )
                }
            ],
            "temperature": 0.5,
            "max_tokens": 3000
        }

        try:
            openai_response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                json=openai_payload,
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                }
            )
            openai_response.raise_for_status()
            openai_data = openai_response.json()

            response_text = openai_data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()

            # JSON 파싱
            eval_data = extract_json_from_response(response_text)
            evaluations = eval_data.get("evaluations", [])

            return evaluations

        except Exception as e:
            # 평가 실패 시 빈 리스트 반환
            return []


async def _evaluate_candidates_with_llm(
    narrative: dict,
    candidates: list[dict]
) -> list[dict]:
    """모든 후보곡에 대해 단계별 LLM 평가 수행

    Args:
        narrative: 서사 JSON 데이터
        candidates: 후보곡 리스트

    Returns:
        점수가 부여된 후보곡 리스트
        [{"artist": ..., "title": ..., "score": ..., "reason": ..., "best_stage": ...}, ...]
    """
    import asyncio

    stages = narrative.get("narrative", {}).get("stages", [])
    summary = narrative.get("summary", "")

    # 각 단계별로 평가
    evaluation_tasks = [
        _llm_evaluate_stage(stage, candidates, summary)
        for stage in stages
    ]

    stage_evaluations = await asyncio.gather(*evaluation_tasks, return_exceptions=True)

    # 결과 통합: 각 곡마다 최고 점수 단계 선택
    song_scores = {}  # key: "artist||title", value: {"score": ..., "reason": ..., "stage": ...}

    for stage_idx, evals in enumerate(stage_evaluations):
        if isinstance(evals, Exception) or not evals:
            continue

        stage_number = stages[stage_idx].get("step", stage_idx + 1)

        for eval_item in evals:
            artist = eval_item.get("artist", "")
            title = eval_item.get("title", "")
            score = eval_item.get("score", 0)
            reason = eval_item.get("reason", "")

            key = f"{artist}||{title}"

            # 최고 점수 업데이트
            if key not in song_scores or score > song_scores[key]["score"]:
                song_scores[key] = {
                    "artist": artist,
                    "title": title,
                    "score": score,
                    "reason": reason,
                    "best_stage": stage_number
                }

    # 리스트로 변환
    scored_candidates = list(song_scores.values())

    # 점수순 정렬
    scored_candidates.sort(key=lambda x: x["score"], reverse=True)

    return scored_candidates


def _weighted_random_sampling(
    narrative: dict,
    scored_candidates: list[dict],
    songs_per_stage: int = 2,
    temperature: float = 1.0
) -> list[dict]:
    """가중치 기반 랜덤 샘플링으로 최종 추천곡 선택

    Args:
        narrative: 서사 JSON 데이터
        scored_candidates: 점수가 부여된 후보곡 리스트
        songs_per_stage: 각 단계별 추천곡 수
        temperature: 샘플링 온도 (높을수록 다양성 증가)

    Returns:
        최종 추천곡 리스트
    """
    import random

    recommendations = []
    stages = narrative.get("narrative", {}).get("stages", [])

    for stage in stages:
        stage_number = stage.get("step", 0)

        # 이 단계에 해당하는 후보곡만 필터링
        stage_candidates = [
            c for c in scored_candidates
            if c.get("best_stage") == stage_number
        ]

        if not stage_candidates:
            continue

        # 점수순 정렬 후 상위 10곡만 샘플링 대상
        stage_candidates.sort(key=lambda x: x.get("score", 0), reverse=True)
        stage_candidates = stage_candidates[:10]

        # 가중치 계산
        weights = [
            score_to_weight(c.get("score", 0), temperature)
            for c in stage_candidates
        ]

        # 가중치 기반 랜덤 샘플링
        num_to_sample = min(songs_per_stage, len(stage_candidates))
        selected = random.choices(
            stage_candidates,
            weights=weights,
            k=num_to_sample
        )

        # 중복 제거
        seen = set()
        for song in selected:
            key = f"{song['artist']}||{song['title']}"
            if key not in seen:
                recommendations.append({
                    **song,
                    "stage_number": stage_number,
                    "stage_title": stage.get("title", "")
                })
                seen.add(key)

    return recommendations


def _format_recommendations(
    narrative: dict,
    recommendations: list[dict]
) -> TextContent:
    """추천 결과를 텍스트로 포맷팅

    Args:
        narrative: 서사 JSON 데이터
        recommendations: 추천곡 리스트

    Returns:
        포맷된 텍스트 결과
    """
    summary = narrative.get("summary", "")
    stages = narrative.get("narrative", {}).get("stages", [])

    lines = [
        "=" * 60,
        f"서사 기반 추천곡: {summary}",
        "=" * 60,
        "",
        f"총 {len(recommendations)}곡 추천",
        ""
    ]

    # 단계별로 그룹화
    stage_map = {}
    for rec in recommendations:
        stage_num = rec.get("stage_number", 0)
        if stage_num not in stage_map:
            stage_map[stage_num] = []
        stage_map[stage_num].append(rec)

    # 단계 순서대로 출력
    for stage in stages:
        stage_number = stage.get("step", 0)

        if stage_number not in stage_map:
            continue

        stage_recs = stage_map[stage_number]
        keywords = ", ".join(stage.get("keywords", []))

        lines.append(f"[{stage_number}단계] {stage.get('title', '')}")
        lines.append(f"키워드: {keywords}")
        lines.append("")

        for i, rec in enumerate(stage_recs, 1):
            lines.append(f"  {i}. {rec['artist']} - {rec['title']} (점수: {rec.get('score', 0)}/100)")
            lines.append(f"     이유: {rec.get('reason', '')}")
            lines.append("")

    lines.append("=" * 60)
    lines.append("실행할 때마다 다른 추천곡이 선정됩니다.")

    return TextContent(type="text", text="\n".join(lines))


# @mcp.tool()  # 비활성화: 존재하지 않는 곡 추천 문제
async def recommend_songs(artist: str, title: str) -> TextContent:
    """서사/키워드 기반으로 곡을 추천합니다 (10-20곡) - 현재 비활성화됨.

    "{artist}의 {title} 같은 곡 추천해줘" 요청에 사용합니다.
    매 실행마다 랜덤 가중치 기반으로 다른 곡들이 선정됩니다.

    Args:
        artist: 아티스트 이름
        title: 곡 제목

    Returns:
        서사 기반 추천곡 10-20개 (단계별 2-3곡)
    """
    # API 키 확인
    if not TAVILY_API_KEY:
        return TextContent(
            type="text",
            text="Error: TAVILY_API_KEY가 .env 파일에 설정되지 않았습니다."
        )

    if not OPENAI_API_KEY:
        return TextContent(
            type="text",
            text="Error: OPENAI_API_KEY가 .env 파일에 설정되지 않았습니다."
        )

    if not LASTFM_API_KEY:
        return TextContent(
            type="text",
            text="Error: LASTFM_API_KEY가 .env 파일에 설정되지 않았습니다."
        )

    try:
        # 1. 서사 생성
        try:
            narrative_json = await _get_narrative_json(artist, title)
        except ValueError as e:
            return TextContent(
                type="text",
                text=f"서사 생성 실패: {str(e)}"
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                return TextContent(
                    type="text",
                    text="OpenAI API 요청 한도 초과. 잠시 후 다시 시도해주세요."
                )
            elif e.response.status_code == 401:
                return TextContent(
                    type="text",
                    text="OpenAI API 키가 유효하지 않습니다. .env 파일을 확인해주세요."
                )
            else:
                return TextContent(
                    type="text",
                    text=f"서사 생성 API 오류 ({e.response.status_code}): {e.response.text}"
                )

        # 2. 후보곡 검색 (Last.fm)
        try:
            candidates = await _search_candidates_for_narrative(narrative_json)
        except Exception as e:
            return TextContent(
                type="text",
                text=f"후보곡 검색 오류: {str(e)}"
            )

        if len(candidates) < 5:
            return TextContent(
                type="text",
                text=f"검색된 후보곡이 너무 적습니다 ({len(candidates)}곡). 다른 곡으로 시도해주세요."
            )

        # 3. LLM 평가
        try:
            scored_candidates = await _evaluate_candidates_with_llm(
                narrative_json, candidates
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                return TextContent(
                    type="text",
                    text="OpenAI API 요청 한도 초과. 잠시 후 다시 시도해주세요."
                )
            elif e.response.status_code == 401:
                return TextContent(
                    type="text",
                    text="OpenAI API 키가 유효하지 않습니다. .env 파일을 확인해주세요."
                )
            else:
                return TextContent(
                    type="text",
                    text=f"LLM 평가 API 오류 ({e.response.status_code}): {e.response.text}"
                )
        except Exception as e:
            return TextContent(
                type="text",
                text=f"LLM 평가 오류: {str(e)}"
            )

        if not scored_candidates:
            return TextContent(
                type="text",
                text="평가된 후보곡이 없습니다. 다른 곡으로 시도해주세요."
            )

        # 4. 가중치 랜덤 샘플링
        try:
            recommendations = _weighted_random_sampling(
                narrative_json,
                scored_candidates,
                songs_per_stage=2,
                temperature=1.0
            )
        except Exception as e:
            return TextContent(
                type="text",
                text=f"추천곡 샘플링 오류: {str(e)}"
            )

        if len(recommendations) < 3:
            return TextContent(
                type="text",
                text=f"추천곡이 충분하지 않습니다 ({len(recommendations)}곡). 다른 곡으로 시도해주세요."
            )

        # 5. 포맷팅 & 반환
        return _format_recommendations(narrative_json, recommendations)

    except Exception as e:
        return TextContent(
            type="text",
            text=f"추천 시스템 오류: {str(e)}"
        )


# 서버 시작 시 API 키 확인 (Last.fm만 필수, 나머지는 선택)
if not LASTFM_API_KEY:
    print("ERROR: LASTFM_API_KEY가 .env 파일에 설정되지 않았습니다.", file=sys.stderr)
    print(".env 파일에 다음을 추가하세요: LASTFM_API_KEY=your_api_key", file=sys.stderr)
    sys.exit(1)

print("Hyukebox MCP Server 초기화 완료", file=sys.stderr)
print(f".env 경로: {env_path}", file=sys.stderr)
