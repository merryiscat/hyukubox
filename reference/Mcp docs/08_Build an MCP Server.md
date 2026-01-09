# MCP 서버 구축하기

## 개요

Claude for Desktop 및 기타 클라이언트에서 사용할 자체 서버를 구축하기 시작합니다.

이 튜토리얼에서는 간단한 MCP 날씨 서버를 구축하고 호스트(Claude for Desktop)에 연결합니다.

---

## 구축할 내용

두 가지 도구를 노출하는 서버를 구축합니다:

- **`get_alerts`**: 미국 주별 날씨 경보 가져오기
- **`get_forecast`**: 특정 위치의 일기 예보 가져오기

그런 다음 서버를 MCP 호스트(Claude for Desktop)에 연결합니다.

> **참고**: 서버는 모든 클라이언트에 연결할 수 있습니다. 여기서는 단순성을 위해 Claude for Desktop을 선택했지만, [자체 클라이언트 구축](https://claude.ai/docs/develop/build-client) 가이드와 [다른 클라이언트 목록](https://claude.ai/clients)도 있습니다.

---

## MCP 핵심 개념

MCP 서버는 세 가지 주요 기능을 제공할 수 있습니다:

1. **[Resources](https://claude.ai/docs/learn/server-concepts#resources)**: 클라이언트가 읽을 수 있는 파일 같은 데이터 (API 응답 또는 파일 내용 등)
2. **[Tools](https://claude.ai/docs/learn/server-concepts#tools)**: LLM이 호출할 수 있는 함수 (사용자 승인 필요)
3. **[Prompts](https://claude.ai/docs/learn/server-concepts#prompts)**: 사용자가 특정 작업을 수행하는 데 도움이 되는 사전 작성된 템플릿

이 튜토리얼은 주로 **도구(Tools)**에 초점을 맞춥니다.

---

## 지원 언어

이 가이드는 다음 언어로 서버를 구축하는 방법을 제공합니다:

- [Python](https://claude.ai/chat/d1892e31-8053-4913-8394-fadb47edcd3a#python-%EA%B5%AC%ED%98%84)
- [TypeScript](https://claude.ai/chat/d1892e31-8053-4913-8394-fadb47edcd3a#typescript-%EA%B5%AC%ED%98%84)
- [Java](https://claude.ai/chat/d1892e31-8053-4913-8394-fadb47edcd3a#java-%EA%B5%AC%ED%98%84)
- [Kotlin](https://claude.ai/chat/d1892e31-8053-4913-8394-fadb47edcd3a#kotlin-%EA%B5%AC%ED%98%84)
- [C#](https://claude.ai/chat/d1892e31-8053-4913-8394-fadb47edcd3a#c-%EA%B5%AC%ED%98%84)
- [Rust](https://claude.ai/chat/d1892e31-8053-4913-8394-fadb47edcd3a#rust-%EA%B5%AC%ED%98%84)

---

## 🚨 중요: MCP 서버의 로깅

MCP 서버를 구현할 때 로깅 처리 방법에 주의하세요:

### STDIO 기반 서버의 경우

**절대 표준 출력(stdout)에 쓰지 마세요.** 여기에는 다음이 포함됩니다:

- Python의 `print()` 문
- JavaScript의 `console.log()`
- Go의 `fmt.Println()`
- Rust의 `println!()`
- 다른 언어의 유사한 stdout 함수

> **경고**: stdout에 쓰면 JSON-RPC 메시지가 손상되고 서버가 중단됩니다.

### HTTP 기반 서버의 경우

표준 출력 로깅은 HTTP 응답을 방해하지 않으므로 괜찮습니다.

### 모범 사례

1. **stderr 또는 파일에 쓰는 로깅 라이브러리 사용**
2. **Python의 경우**: `print()`는 기본적으로 stdout에 쓰므로 특히 주의

### 올바른/잘못된 예제

```python
# ❌ 잘못됨 (STDIO)
print("Processing request")

# ✅ 올바름 (STDIO)
import logging
logging.info("Processing request")
```

```javascript
// ❌ 잘못됨 (STDIO)
console.log("Server started");

// ✅ 올바름 (STDIO)
console.error("Server started"); // stderr는 안전
```

```rust
// ❌ 잘못됨 (STDIO)
println!("Processing request");

// ✅ 올바름 (STDIO)
use tracing::info;
info!("Processing request"); // stderr에 쓰기
```

---

## Python 구현

### 완성된 코드

[GitHub에서 완성된 코드 보기](https://github.com/modelcontextprotocol/quickstart-resources/tree/main/weather-server-python)

### 사전 요구사항

- Python 3.10 이상
- Python MCP SDK 1.2.0 이상
- Python 및 LLM(Claude 등)에 대한 기본 지식

### 환경 설정

#### 1. uv 설치 및 프로젝트 설정

**macOS/Linux:**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

> **중요**: 터미널을 재시작하여 `uv` 명령이 인식되도록 합니다.

#### 2. 프로젝트 생성

**macOS/Linux:**

```bash
# 프로젝트를 위한 새 디렉토리 생성
uv init weather
cd weather

# 가상 환경 생성 및 활성화
uv venv
source .venv/bin/activate

# 의존성 설치
uv add "mcp[cli]" httpx

# 서버 파일 생성
touch weather.py
```

**Windows:**

```bash
uv init weather
cd weather
uv venv
.venv\Scripts\activate
uv add "mcp[cli]" httpx
New-Item weather.py
```

### 서버 구축

#### 1. 패키지 가져오기 및 인스턴스 설정

`weather.py` 파일 상단에 추가:

```python
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

# FastMCP 서버 초기화
mcp = FastMCP("weather")

# 상수
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"
```

`FastMCP` 클래스는 Python 타입 힌트와 docstring을 사용하여 도구 정의를 자동으로 생성하므로 MCP 도구를 쉽게 만들고 유지 관리할 수 있습니다.

#### 2. 헬퍼 함수

National Weather Service API에서 데이터를 쿼리하고 형식화하는 헬퍼 함수를 추가합니다:

```python
async def make_nws_request(url: str) -> dict[str, Any] | None:
    """NWS API에 적절한 오류 처리로 요청을 보냅니다."""
    headers = {"User-Agent": USER_AGENT, "Accept": "application/geo+json"}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None


def format_alert(feature: dict) -> str:
    """경보 기능을 읽을 수 있는 문자열로 형식화합니다."""
    props = feature["properties"]
    return f"""
Event: {props.get("event", "Unknown")}
Area: {props.get("areaDesc", "Unknown")}
Severity: {props.get("severity", "Unknown")}
Description: {props.get("description", "No description available")}
Instructions: {props.get("instruction", "No specific instructions provided")}
"""
```

#### 3. 도구 실행 구현

도구 실행 핸들러는 각 도구의 로직을 실제로 실행합니다:

```python
@mcp.tool()
async def get_alerts(state: str) -> str:
    """미국 주의 날씨 경보를 가져옵니다.

    Args:
        state: 두 글자 미국 주 코드 (예: CA, NY)
    """
    url = f"{NWS_API_BASE}/alerts/active/area/{state}"
    data = await make_nws_request(url)

    if not data or "features" not in data:
        return "Unable to fetch alerts or no alerts found."

    if not data["features"]:
        return "No active alerts for this state."

    alerts = [format_alert(feature) for feature in data["features"]]
    return "\n---\n".join(alerts)


@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """위치의 일기 예보를 가져옵니다.

    Args:
        latitude: 위치의 위도
        longitude: 위치의 경도
    """
    # 먼저 예보 그리드 엔드포인트 가져오기
    points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    points_data = await make_nws_request(points_url)

    if not points_data:
        return "Unable to fetch forecast data for this location."

    # 포인트 응답에서 예보 URL 가져오기
    forecast_url = points_data["properties"]["forecast"]
    forecast_data = await make_nws_request(forecast_url)

    if not forecast_data:
        return "Unable to fetch detailed forecast."

    # 기간을 읽을 수 있는 예보로 형식화
    periods = forecast_data["properties"]["periods"]
    forecasts = []
    for period in periods[:5]:  # 다음 5개 기간만 표시
        forecast = f"""
{period["name"]}:
Temperature: {period["temperature"]}°{period["temperatureUnit"]}
Wind: {period["windSpeed"]} {period["windDirection"]}
Forecast: {period["detailedForecast"]}
"""
        forecasts.append(forecast)

    return "\n---\n".join(forecasts)
```

#### 4. 서버 실행

서버를 초기화하고 실행합니다:

```python
def main():
    # 서버 초기화 및 실행
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
```

#### 5. 서버 시작

```bash
uv run weather.py
```

서버가 완성되었습니다! MCP 호스트의 메시지를 수신합니다.

---

## TypeScript 구현

### 완성된 코드

[GitHub에서 완성된 코드 보기](https://github.com/modelcontextprotocol/quickstart-resources/tree/main/weather-server-typescript)

### 사전 요구사항

- Node.js 16 이상
- TypeScript 및 LLM(Claude 등)에 대한 기본 지식

### 환경 설정

#### 1. Node.js 설치 확인

```bash
node --version
npm --version
```

Node.js가 설치되어 있지 않으면 [nodejs.org](https://nodejs.org/)에서 다운로드합니다.

#### 2. 프로젝트 생성

**macOS/Linux:**

```bash
# 프로젝트를 위한 새 디렉토리 생성
mkdir weather
cd weather

# npm 프로젝트 초기화
npm init -y

# 의존성 설치
npm install @modelcontextprotocol/sdk zod@3
npm install -D @types/node typescript

# 파일 생성
mkdir src
touch src/index.ts
```

**Windows:**

```bash
mkdir weather
cd weather
npm init -y
npm install @modelcontextprotocol/sdk zod@3
npm install -D @types/node typescript
mkdir src
New-Item src/index.ts
```

#### 3. package.json 업데이트

`type: "module"` 및 빌드 스크립트 추가:

```json
{
  "type": "module",
  "bin": {
    "weather": "./build/index.js"
  },
  "scripts": {
    "build": "tsc && chmod 755 build/index.js"
  },
  "files": ["build"]
}
```

#### 4. tsconfig.json 생성

프로젝트 루트에 생성:

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "Node16",
    "moduleResolution": "Node16",
    "outDir": "./build",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules"]
}
```

### 서버 구축

#### 1. 패키지 가져오기

`src/index.ts` 상단에 추가:

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const NWS_API_BASE = "https://api.weather.gov";
const USER_AGENT = "weather-app/1.0";

// 서버 인스턴스 생성
const server = new McpServer({
  name: "weather",
  version: "1.0.0",
});
```

#### 2. 헬퍼 함수

```typescript
// NWS API 요청을 위한 헬퍼 함수
async function makeNWSRequest<T>(url: string): Promise<T | null> {
  const headers = {
    "User-Agent": USER_AGENT,
    Accept: "application/geo+json",
  };

  try {
    const response = await fetch(url, { headers });
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return (await response.json()) as T;
  } catch (error) {
    console.error("Error making NWS request:", error);
    return null;
  }
}

interface AlertFeature {
  properties: {
    event?: string;
    areaDesc?: string;
    severity?: string;
    status?: string;
    headline?: string;
  };
}

// 경보 데이터 형식화
function formatAlert(feature: AlertFeature): string {
  const props = feature.properties;
  return [
    `Event: ${props.event || "Unknown"}`,
    `Area: ${props.areaDesc || "Unknown"}`,
    `Severity: ${props.severity || "Unknown"}`,
    `Status: ${props.status || "Unknown"}`,
    `Headline: ${props.headline || "No headline"}`,
    "---",
  ].join("\n");
}
```

#### 3. 도구 등록

```typescript
server.registerTool(
  "get_alerts",
  {
    description: "Get weather alerts for a state",
    inputSchema: {
      state: z
        .string()
        .length(2)
        .describe("Two-letter state code (e.g. CA, NY)"),
    },
  },
  async ({ state }) => {
    const stateCode = state.toUpperCase();
    const alertsUrl = `${NWS_API_BASE}/alerts?area=${stateCode}`;
    const alertsData = await makeNWSRequest<AlertsResponse>(alertsUrl);

    if (!alertsData) {
      return {
        content: [
          {
            type: "text",
            text: "Failed to retrieve alerts data",
          },
        ],
      };
    }

    const features = alertsData.features || [];
    if (features.length === 0) {
      return {
        content: [
          {
            type: "text",
            text: `No active alerts for ${stateCode}`,
          },
        ],
      };
    }

    const formattedAlerts = features.map(formatAlert);
    const alertsText = `Active alerts for ${stateCode}:\n\n${formattedAlerts.join("\n")}`;

    return {
      content: [
        {
          type: "text",
          text: alertsText,
        },
      ],
    };
  },
);

server.registerTool(
  "get_forecast",
  {
    description: "Get weather forecast for a location",
    inputSchema: {
      latitude: z
        .number()
        .min(-90)
        .max(90)
        .describe("Latitude of the location"),
      longitude: z
        .number()
        .min(-180)
        .max(180)
        .describe("Longitude of the location"),
    },
  },
  async ({ latitude, longitude }) => {
    const pointsUrl = `${NWS_API_BASE}/points/${latitude.toFixed(4)},${longitude.toFixed(4)}`;
    const pointsData = await makeNWSRequest<PointsResponse>(pointsUrl);

    if (!pointsData) {
      return {
        content: [
          {
            type: "text",
            text: `Failed to retrieve grid point data`,
          },
        ],
      };
    }

    const forecastUrl = pointsData.properties?.forecast;
    if (!forecastUrl) {
      return {
        content: [
          {
            type: "text",
            text: "Failed to get forecast URL from grid point data",
          },
        ],
      };
    }

    const forecastData = await makeNWSRequest<ForecastResponse>(forecastUrl);
    if (!forecastData) {
      return {
        content: [
          {
            type: "text",
            text: "Failed to retrieve forecast data",
          },
        ],
      };
    }

    const periods = forecastData.properties?.periods || [];
    const formattedForecast = periods.map((period: ForecastPeriod) =>
      [
        `${period.name || "Unknown"}:`,
        `Temperature: ${period.temperature || "Unknown"}°${period.temperatureUnit || "F"}`,
        `Wind: ${period.windSpeed || "Unknown"} ${period.windDirection || ""}`,
        `${period.shortForecast || "No forecast available"}`,
        "---",
      ].join("\n"),
    );

    const forecastText = `Forecast:\n\n${formattedForecast.join("\n")}`;

    return {
      content: [
        {
          type: "text",
          text: forecastText,
        },
      ],
    };
  },
);
```

#### 4. 서버 실행

```typescript
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Weather MCP Server running on stdio");
}

main().catch((error) => {
  console.error("Fatal error in main():", error);
  process.exit(1);
});
```

#### 5. 빌드 및 실행

```bash
npm run build
```

---

## Claude Desktop에서 테스트하기

> **Linux 사용자 참고**: Claude for Desktop은 아직 Linux에서 사용할 수 없습니다. Linux 사용자는 [클라이언트 구축](https://claude.ai/docs/develop/build-client) 튜토리얼로 진행하여 방금 구축한 서버에 연결하는 MCP 클라이언트를 구축할 수 있습니다.

### 1. Claude for Desktop 설치

[최신 버전 다운로드](https://claude.ai/download)

이미 설치되어 있다면 **최신 버전으로 업데이트**했는지 확인하세요.

### 2. 구성 파일 열기

Claude for Desktop 구성 파일을 텍스트 편집기로 엽니다:

**파일 위치:**

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

**VS Code로 열기 (예시):**

**macOS/Linux:**

```bash
code ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**Windows:**

```bash
code %APPDATA%\Claude\claude_desktop_config.json
```

### 3. 서버 구성 추가

`mcpServers` 키에 서버를 추가합니다. 최소한 하나의 서버가 올바르게 구성된 경우에만 MCP UI 요소가 Claude for Desktop에 표시됩니다.

#### Python 서버 구성

**macOS/Linux:**

```json
{
  "mcpServers": {
    "weather": {
      "command": "uv",
      "args": [
        "--directory",
        "/ABSOLUTE/PATH/TO/PARENT/FOLDER/weather",
        "run",
        "weather.py"
      ]
    }
  }
}
```

**Windows:**

```json
{
  "mcpServers": {
    "weather": {
      "command": "uv",
      "args": [
        "--directory",
        "C:\\ABSOLUTE\\PATH\\TO\\PARENT\\FOLDER\\weather",
        "run",
        "weather.py"
      ]
    }
  }
}
```

#### TypeScript 서버 구성

**macOS/Linux:**

```json
{
  "mcpServers": {
    "weather": {
      "command": "node",
      "args": ["/ABSOLUTE/PATH/TO/PARENT/FOLDER/weather/build/index.js"]
    }
  }
}
```

**Windows:**

```json
{
  "mcpServers": {
    "weather": {
      "command": "node",
      "args": ["C:\\ABSOLUTE\\PATH\\TO\\PARENT\\FOLDER\\weather\\build\\index.js"]
    }
  }
}
```

> **중요**:
> 
> - 서버에 대한 **절대 경로**를 전달해야 합니다
> - macOS/Linux에서는 `pwd` 명령으로 절대 경로를 얻을 수 있습니다
> - Windows에서는 `cd` 명령 사용
> - Windows JSON 경로에서는 이중 백슬래시(`\\`) 또는 슬래시(`/`) 사용

### 4. Claude Desktop 재시작

파일을 저장하고 **Claude for Desktop을 완전히 종료한 후** 재시작합니다.

**완전히 종료하는 방법:**

- **Windows**: 시스템 트레이의 Claude 아이콘을 마우스 오른쪽 버튼으로 클릭하고 "종료" 또는 "나가기" 선택
- **macOS**: Cmd+Q 사용 또는 메뉴 바에서 "Claude 종료" 선택

> **주의**: 단순히 창을 닫는 것만으로는 애플리케이션이 완전히 종료되지 않으며 MCP 서버 구성 변경 사항이 적용되지 않습니다.

### 5. 테스트

성공적으로 재시작하면 대화 입력 상자의 오른쪽 하단에 MCP 서버 표시기가 나타납니다.

표시기를 클릭하여 Filesystem Server가 제공하는 사용 가능한 도구를 확인하세요.

#### 테스트 명령

- "Sacramento의 날씨는 어때?"
- "텍사스의 활성 날씨 경보는 뭐야?"

> **참고**: 미국 국립 기상청을 사용하므로 쿼리는 미국 위치에만 작동합니다.

---

## 내부 작동 원리

질문을 하면:

1. **클라이언트**가 질문을 Claude에 보냄
2. **Claude**가 사용 가능한 도구를 분석하고 사용할 도구를 결정
3. **클라이언트**가 MCP 서버를 통해 선택한 도구를 실행
4. **결과**가 Claude로 다시 전송됨
5. **Claude**가 자연어 응답을 작성
6. **응답**이 표시됨!

---

## 문제 해결

### Claude Desktop 통합 문제

#### Claude Desktop에서 로그 가져오기

MCP 관련 Claude.app 로깅은 다음 위치의 로그 파일에 기록됩니다:

- **macOS**: `~/Library/Logs/Claude`
- **Windows**: `%APPDATA%\Claude\logs`

**로그 파일:**

- `mcp.log`: MCP 연결 및 연결 실패에 대한 일반 로깅
- `mcp-server-SERVERNAME.log`: 명명된 서버의 오류(stderr) 로깅

**로그 확인 명령:**

```bash
# 최근 로그 확인 및 새 로그 팔로우
tail -n 20 -f ~/Library/Logs/Claude/mcp*.log
```

#### 서버가 Claude에 표시되지 않음

1. `claude_desktop_config.json` 파일 문법 확인
2. 프로젝트 경로가 상대 경로가 아닌 절대 경로인지 확인
3. Claude for Desktop 완전히 재시작

#### 도구 호출이 자동으로 실패함

Claude가 도구를 사용하려고 시도하지만 실패하는 경우:

1. Claude의 로그에서 오류 확인
2. 서버가 오류 없이 빌드되고 실행되는지 확인
3. Claude for Desktop 재시작 시도

#### 아무것도 작동하지 않는 경우

더 나은 디버깅 도구와 자세한 지침은 [디버깅 가이드](https://claude.ai/legacy/tools/debugging)를 참조하세요.

---

### Weather API 문제

#### 오류: 그리드 포인트 데이터 검색 실패

일반적으로 다음을 의미합니다:

1. 좌표가 미국 외부에 있음
2. NWS API에 문제가 있음
3. 속도 제한이 적용됨

**해결 방법:**

- 미국 좌표를 사용하는지 확인
- 요청 간에 작은 지연 추가
- NWS API 상태 페이지 확인

#### 오류: [STATE]에 대한 활성 경보 없음

이것은 오류가 아닙니다. 해당 주에 현재 날씨 경보가 없다는 의미입니다. 다른 주를 시도하거나 악천후 중에 확인하세요.

---

## 다음 단계

### 1. 클라이언트 구축

**서버에 연결할 수 있는 자체 MCP 클라이언트를 구축하는 방법 학습**

- [클라이언트 구축 가이드](https://claude.ai/docs/develop/build-client)

### 2. 예제 서버

**공식 MCP 서버 및 구현 갤러리 확인**

- [Examples](https://claude.ai/examples)

### 3. 디버깅 가이드

**MCP 서버 및 통합을 효과적으로 디버그하는 방법 학습**

- [디버깅 가이드](https://claude.ai/legacy/tools/debugging)

### 4. LLM으로 MCP 구축

**Claude와 같은 LLM을 사용하여 MCP 개발을 가속화하는 방법 학습**

- [LLM으로 MCP 구축](https://claude.ai/tutorials/building-mcp-with-llms)

---

## 다른 언어 구현

이 문서에서는 Python과 TypeScript 구현을 자세히 다뤘습니다. 다른 언어의 구현은 다음을 참조하세요:

- **Java**: [Spring AI MCP 예제](https://github.com/spring-projects/spring-ai-examples/tree/main/model-context-protocol/weather/starter-stdio-server)
- **Kotlin**: [Kotlin SDK 샘플](https://github.com/modelcontextprotocol/kotlin-sdk/tree/main/samples/weather-stdio-server)
- **C#**: [C# SDK 샘플](https://github.com/modelcontextprotocol/csharp-sdk/tree/main/samples/QuickstartWeatherServer)
- **Rust**: [Rust 빠른 시작](https://github.com/modelcontextprotocol/quickstart-resources/tree/main/weather-server-rust)

각 구현은 유사한 패턴을 따르지만 언어별 관용구와 모범 사례를 사용합니다.

---

## 요약

이 가이드를 통해:

✅ MCP 서버의 핵심 개념 이해 ✅ 날씨 API를 사용하는 기본 MCP 서버 구축 ✅ 도구 정의 및 구현 방법 학습 ✅ Claude Desktop과 서버 통합 ✅ 일반적인 문제 해결 방법 이해

이제 사용자 정의 MCP 서버를 구축하여 AI 애플리케이션의 기능을 확장할 수 있습니다!

---

## 추가 리소스

- **공식 문서**: https://modelcontextprotocol.io/docs
- **GitHub 저장소**: https://github.com/modelcontextprotocol
- **예제 서버**: https://github.com/modelcontextprotocol/servers
- **SDK 문서**: [SDKs](https://claude.ai/docs/sdk)

---

_이 문서는 Model Context Protocol 공식 문서에서 가져온 내용입니다._