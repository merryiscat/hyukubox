## mcp 구현 설계

- 가수와 곡을 input으로 받아 api 검색 후 추천곡 리스트를 만드는 일종의 도메인 특화 딥서치 mcp 서버
- 동작 예시
```
input :
"화사의 good goodbye를 타이틀 곡으로 한 앨범 만들어 줘" 
output : 
Album: Good Goodbye
Artist: 화사, 헤이즈 ... 프롬
Genre: R&B / Soul / Alternative Pop
Mood:  이별 → 미련과 자책 → 감정 바닥 → 자존 회복 → 이별 직후의 감정 정리
playlist: https://youtube.com/playlist?list=예시
```

## tool 구성
3가지 요청을 대응할 수 있는 3가지 툴을 구성할 것이다.
첫번째로 검색 요청에 대한 서치 툴이다. meta 검색과 웹검색 api를 하나로 묶어 곡 정보에 대한 검색을 대응할 것이다.
두번째로 추천 요청에 대한 딥서치 툴이다. 메타 검색과 웹검색된 내용을 기반으로 주제를 추출하고 서사를 생성하여 관련 주제와 서사에 맞는 노래, 음악을 추천해준다.
세번째로 생성 요청에 대한 유튜브 api 툴이다. 플레이리스트를 만들고 곡을 추가해준다.

---

## Reference 구현체 분석

### 1. llm-jukebox (YouTube 음악 검색 & 재생)

**위치**: `reference/llm-jukebox/server.py`

**기술 스택**:
- FastMCP 2.11.3+
- yt-dlp (YouTube 검색/다운로드)
- pygame (오디오 재생)
- TinyDB (로컬 DB 캐싱)

**구현된 3가지 Tool**:

#### Tool 1: `download_and_play`
```python
@mcp.tool()
def download_and_play(query: str) -> str:
    """Search for and play a song. If the song is already in the library
    it will play the existing version, otherwise it will download it first.

    Args:
        query: Search query for music (artist, song, album, etc.)

    Returns:
        Success message with file info, or error message
    """
```

**동작**:
1. YouTube에서 곡 검색 (yt-dlp)
2. 컴필레이션/앨범 필터링 (is_single_song 체크)
3. 로컬 라이브러리에서 기존 곡 확인
4. 없으면 다운로드 후 DB 저장
5. pygame으로 재생

**핵심 패턴**:
- yt_dlp로 메타데이터 조회 → 다운로드 → TinyDB 저장 → 재생
- `@suppress_output` 데코레이터로 stdout/stderr 억제

#### Tool 2: `stop_playback`
```python
@mcp.tool()
async def stop_playback() -> str:
    """Stop any currently playing song."""
```

**동작**: pygame.mixer.music.stop() 호출

#### Tool 3: `list_library`
```python
@mcp.tool()
async def list_library() -> str:
    """List all songs in the music library."""
```

**동작**:
1. 파일 존재 여부 체크 (cleanup_missing_files)
2. TinyDB에서 모든 곡 조회
3. 포맷팅된 리스트 반환

**주요 구현 특징**:
```python
# 1. FastMCP 초기화 (매우 간단)
mcp = FastMCP("LLM Jukebox")

# 2. 환경 변수 사용
download_path = Path(os.environ.get("DOWNLOAD_PATH", "./"))

# 3. TinyDB 초기화
db = TinyDB(db_path)
Track = Query()

# 4. 로깅 억제 (CRITICAL!)
logging.getLogger().setLevel(logging.CRITICAL)
logging.getLogger("yt_dlp").setLevel(logging.CRITICAL)

# 5. Tool 등록
@mcp.tool()  # 이 데코레이터만으로 자동 등록

# 6. 서버 실행
if __name__ == "__main__":
    mcp.run(transport="stdio")
```

---

### 2. aimusic-mcp-tool (AI 음악 생성)

**위치**: `reference/aimusic-mcp-tool/musicmcp_ai_mcp/api.py`

**기술 스택**:
- FastMCP (from mcp.server.fastmcp)
- httpx (async HTTP 클라이언트)
- Polling 패턴 (장시간 작업 처리)

**구현된 4가지 Tool**:

#### Tool 1: `generate_prompt_song`
```python
@mcp.tool(
    description="""🎼 Inspiration Mode: Generate songs based on simple
    text descriptions (AI automatically generates title, lyrics, style, etc.)

    ⚠️ COST WARNING: This tool makes an API call which may incur costs
    (5 credits per generation). Each generation creates 2 songs. Only use
    when explicitly requested by the user.

    Args:
        prompt (str): Song theme or emotional description, 1-1200 characters
        instrumental (bool): Whether instrumental only (no lyrics)
        style (str, optional): Music style (e.g., "ambient", "pop", "rock")

    Returns:
        Song information including download URLs
    """
)
async def generate_prompt_song(
    prompt: str,
    instrumental: bool,
    style: str | None = None
) -> list[TextContent]:
```

**동작**:
1. API 키 검증
2. httpx로 POST 요청 (음악 생성 태스크 생성)
3. **Polling 패턴**: 2초마다 query_song_task() 호출하여 완료 대기
4. 완료되면 곡 정보 반환 (URL, 메타데이터 등)

**Polling 패턴 코드**:
```python
# Poll for task completion
current_timestamp = datetime.now().timestamp()
while True:
    if (datetime.now().timestamp() - current_timestamp) > default_time_out:
        raise Exception(f"Song generation timed out after {default_time_out} seconds")

    songs, status = await query_song_task(song_ids)

    if status == "error":
        raise Exception("Song generation failed with error status")
    elif status == "completed" or status == "success":
        break
    else:
        time.sleep(2)  # 2초 대기 후 재확인
```

#### Tool 2: `generate_custom_song`
```python
@mcp.tool(description="""🎵 Custom Mode: Generate songs based on detailed
song information (user specifies song name, lyrics, style, etc.)""")
async def generate_custom_song(
    title: str,
    instrumental: bool,
    lyric: str | None = None,
    tags: str | None = None
) -> list[TextContent]:
```

**동작**: Tool 1과 유사하지만 사용자가 제목, 가사, 태그 직접 지정

#### Tool 3: `check_credit_balance`
```python
@mcp.tool(description="Check your credit balance.")
async def check_credit_balance() -> TextContent:
```

#### Tool 4: `check_api_health`
```python
@mcp.tool(description="Check the health status of the MusicMCP.AI API service.")
async def check_api_health() -> TextContent:
```

**주요 구현 특징**:
```python
# 1. 환경 변수로 설정 관리
api_key = os.getenv('MUSICMCP_API_KEY')
api_url = os.getenv('MUSICMCP_API_URL', "https://www.musicmcp.ai/api")
default_time_out = float(os.getenv('TIME_OUT_SECONDS', '600'))

# 2. stderr로 디버그 출력 (stdout 절대 사용 금지!)
print(f"✅ Song generation task created. Song IDs: {song_ids}", file=sys.stderr)

# 3. httpx로 async HTTP 요청
async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
    response = await client.post(url, json=params, headers=headers)
    response.raise_for_status()
    result = response.json()

# 4. HTTP 에러 처리
except httpx.HTTPStatusError as e:
    if e.response.status_code == 402:
        error_detail = "Insufficient credits. Please recharge your account."
    elif e.response.status_code == 401:
        error_detail = "Invalid API key. Please check your MUSICMCP_API_KEY."

# 5. 반환 타입: list[TextContent] 또는 TextContent
return [TextContent(type="text", text=formatted_text)]

# 6. 서버 실행
def main():
    mcp.run()  # transport는 기본값 stdio
```

---

## MCP Tool 구현 패턴 정리

### 기본 구조
```python
from fastmcp import FastMCP
from mcp.types import TextContent

# 1. FastMCP 인스턴스 생성
mcp = FastMCP("Server Name")

# 2. Tool 정의 (데코레이터 방식)
@mcp.tool()
async def tool_name(param1: str, param2: int = 10) -> TextContent:
    """Tool description for LLM.

    Args:
        param1: Description of param1
        param2: Description of param2 (default: 10)

    Returns:
        Success or error message
    """
    try:
        # 로직 구현
        result = do_something(param1, param2)

        # 성공 응답
        return TextContent(type="text", text=f"✅ Success: {result}")

    except Exception as e:
        # 에러 응답
        return TextContent(type="text", text=f"❌ Error: {str(e)}")

# 3. 서버 실행
if __name__ == "__main__":
    mcp.run(transport="stdio")
```

### Tool 파라미터 정의
```python
# 타입 힌팅 필수 (MCP가 자동으로 inputSchema 생성)
async def search_song(
    artist: str,              # 필수 파라미터
    title: str,               # 필수 파라미터
    include_similar: bool = False  # 선택 파라미터 (기본값)
) -> TextContent:
```

### 반환 타입
```python
# 1. 단일 텍스트 응답
return TextContent(type="text", text="response text")

# 2. 여러 응답 (리스트)
return [
    TextContent(type="text", text="First response"),
    TextContent(type="text", text="Second response")
]
```

---

## MCP Docs 핵심 참고 가이드

### 📚 언제 어떤 문서를 참고할지

| 구현 단계 | 참고 문서 | 위치 | 핵심 내용 |
|----------|---------|------|---------|
| **서버 기본 구조** | Build an MCP Server | `reference/Mcp docs/08_Build an MCP Server.md` | - FastMCP 초기화<br>- Tool/Resource/Prompt 개념<br>- ⚠️ **로깅 주의사항 (필독!)** |
| **Tool 정의** | Tools | `reference/Mcp docs/32_Tools.md` | - Tool 스키마 정의<br>- inputSchema (JSON Schema)<br>- tools/list, tools/call 프로토콜<br>- 사용자 승인 필요성 |
| **전송 방식** | Transports | `reference/Mcp docs/18_Transports.md` | - stdio vs HTTP<br>- JSON-RPC 인코딩<br>- UTF-8 필수 |
| **아키텍처 이해** | Architecture | `reference/Mcp docs/02_Architecture.md` | - Client-Server 모델<br>- 양방향 통신<br>- 프로토콜 계층 |
| **리소스 제공** | Resources | `reference/Mcp docs/30_Resources.md` | - 파일/데이터 노출 방법<br>- URI 스킴<br>- resources/list |
| **프롬프트 템플릿** | Prompts | `reference/Mcp docs/29_Prompts.md` | - 사전 작성 템플릿<br>- 변수 바인딩<br>- prompts/list |
| **진행 상황 추적** | Progress | `reference/Mcp docs/23_Progress.md` | - 장시간 작업 진행률 표시<br>- Progress tokens |
| **페이지네이션** | Pagination | `reference/Mcp docs/34_Pagination.md` | - Cursor 기반 페이징<br>- 대량 데이터 처리 |
| **보안** | Security Best Practices | `reference/Mcp docs/20_Security Best Practices_part1-2.md` | - API 키 보호<br>- 입력 검증<br>- Rate limiting |
| **인증** | Authorization | `reference/Mcp docs/11_Understanding Authorization in MCP.md`<br>`19_Authorization_part1-4.md` | - OAuth 2.0<br>- Token 관리<br>- 권한 부여 플로우 |

### 🔥 필독 문서 (우선순위)

1. **08_Build an MCP Server.md** - 로깅 주의사항 (stdout 절대 금지!)
2. **32_Tools.md** - Tool 정의 방법
3. **18_Transports.md** - stdio 전송 이해

### ⚠️ 로깅 주의사항 (매우 중요!)

**출처**: `reference/Mcp docs/08_Build an MCP Server.md:49-80`

#### STDIO 기반 서버의 경우

**절대 표준 출력(stdout)에 쓰지 마세요:**
- Python: `print()` ❌
- JavaScript: `console.log()` ❌
- 이유: stdout에 쓰면 JSON-RPC 메시지가 손상되고 서버가 중단됨

**올바른 방법:**
```python
# ❌ 잘못됨 (STDIO)
print("Processing request")

# ✅ 올바름 (STDIO)
import sys
print("Processing request", file=sys.stderr)

# ✅ 올바름 (파일 로깅)
logging.basicConfig(filename='server.log', level=logging.INFO)
logging.info("Processing request")
```

#### HTTP 기반 서버의 경우
stdout 로깅 가능 (HTTP 응답을 방해하지 않음)

---

## 구현 시 주의사항

### 1. 로깅 (Critical!)
```python
# reference/llm-jukebox/server.py:19-25 참고
import logging
import sys

# 모든 로깅을 stderr로 리다이렉트
logging.getLogger().setLevel(logging.CRITICAL)
logging.getLogger("yt_dlp").setLevel(logging.CRITICAL)

# 디버그 출력은 반드시 stderr 사용
print(f"Debug info: {data}", file=sys.stderr)
```

### 2. 환경 변수 관리
```python
# reference/aimusic-mcp-tool/api.py:13-15 참고
import os

api_key = os.getenv('MUSICMCP_API_KEY')
api_url = os.getenv('MUSICMCP_API_URL', "https://default.url")  # 기본값 제공
timeout = float(os.getenv('TIME_OUT_SECONDS', '600'))
```

### 3. Async 패턴
```python
# Async HTTP 요청
async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
    response = await client.post(url, json=params, headers=headers)
    response.raise_for_status()

# Async 병렬 실행
spotify_task = spotify_client.search_track(artist, title)
lastfm_task = lastfm_client.get_track_info(artist, title)

spotify_data, lastfm_data = await asyncio.gather(
    spotify_task, lastfm_task,
    return_exceptions=True  # 예외를 결과로 반환
)
```

### 4. 장시간 작업 처리 (Polling)
```python
# reference/aimusic-mcp-tool/api.py:90-106 참고
current_timestamp = datetime.now().timestamp()
while True:
    if (datetime.now().timestamp() - current_timestamp) > timeout:
        raise Exception(f"Timed out after {timeout} seconds")

    result, status = await check_status(task_id)

    if status == "completed":
        break
    elif status == "error":
        raise Exception("Task failed")
    else:
        time.sleep(2)  # 2초 대기 후 재시도
```

### 5. TinyDB 캐싱
```python
# reference/llm-jukebox/server.py:31-33 참고
from tinydb import TinyDB, Query

db = TinyDB("cache.json")
Track = Query()

# 데이터 저장
db.insert({'key': 'value'})

# 데이터 조회
results = db.search(Track.key == 'value')

# 데이터 삭제
db.remove(doc_ids=[item.doc_id])
```

### 6. 에러 처리
```python
# HTTP 상태 코드별 처리
try:
    response = await client.post(url, json=params)
    response.raise_for_status()
except httpx.HTTPStatusError as e:
    if e.response.status_code == 402:
        return "Insufficient credits"
    elif e.response.status_code == 401:
        return "Invalid API key"
    else:
        raise
```

### 7. Tool Description 작성
```python
@mcp.tool(
    description="""명확한 설명 작성 (LLM이 언제 사용할지 판단)

    Use case: 구체적인 사용 사례

    Example inputs:
    - "예시 1"
    - "예시 2"

    ⚠️ COST WARNING: API 비용 발생 시 경고 표시

    Args:
        param: 파라미터 설명

    Returns:
        반환값 설명
    """
)
```

---

## Reference 활용 전략

### Hyukebox 구현 시 참고 매핑

| Hyukebox 기능 | Reference 파일 | 참고 항목 |
|--------------|---------------|---------|
| **FastMCP 서버 초기화** | `llm-jukebox/server.py:27-33` | `mcp = FastMCP("name")`<br>환경 변수 로딩<br>TinyDB 초기화 |
| **Tool 1: search_song** | `aimusic-mcp/api.py:18-163` | Tool 파라미터 정의<br>상세한 docstring<br>에러 처리 패턴 |
| **Tool 2: create_album_playlist** | `aimusic-mcp/api.py:90-106` | Polling 패턴 (LLM 호출 대기용)<br>asyncio.gather() 병렬 실행 |
| **Tool 3: create_youtube_playlist** | `llm-jukebox/server.py:392-438` | 외부 API 통합 패턴<br>DB 저장 후 반환 |
| **Spotify/Last.fm API** | `aimusic-mcp/api.py:70-73` | httpx async 클라이언트<br>timeout 설정 |
| **Claude API (LLM)** | `aimusic-mcp/api.py:90-106` | Polling 패턴 응용<br>JSON 응답 파싱 |
| **캐싱 (TinyDB)** | `llm-jukebox/server.py:242-276` | 메타데이터 캐싱<br>중복 체크 |
| **에러 메시지 포맷** | `aimusic-mcp/api.py:131-146` | 이모지 활용<br>구조화된 응답 |

---

## 다음 단계

1. ✅ Reference 분석 완료
2. ⏭️ 프로젝트 구조 생성 (pyproject.toml 등)
3. ⏭️ Utils & Models 구현
4. ⏭️ Service Layer 구현
5. ⏭️ MCP Tools 구현
