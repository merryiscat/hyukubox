# MCP 아키텍처 개요

## 개요

이 문서는 Model Context Protocol (MCP)의 **범위(scope)**와 **핵심 개념(core concepts)**을 다루며, 각 핵심 개념을 보여주는 **예제**를 제공합니다.

MCP SDK는 많은 부분을 추상화하므로, 대부분의 개발자는 **데이터 레이어 프로토콜** 섹션이 가장 유용할 것입니다. 이 섹션에서는 MCP 서버가 AI 애플리케이션에 컨텍스트를 제공하는 방법을 설명합니다.

구체적인 구현 세부 사항은 [언어별 SDK 문서](https://claude.ai/docs/sdk)를 참조하세요.

---

## 범위 (Scope)

Model Context Protocol은 다음 프로젝트들을 포함합니다:

- **[MCP 사양](https://modelcontextprotocol.io/specification/latest)**: 클라이언트와 서버의 구현 요구사항을 명시하는 MCP 사양
- **[MCP SDK](https://claude.ai/docs/sdk)**: MCP를 구현하는 다양한 프로그래밍 언어용 SDK
- **MCP 개발 도구**: [MCP Inspector](https://github.com/modelcontextprotocol/inspector)를 포함한 MCP 서버 및 클라이언트 개발 도구
- **[MCP 참조 서버 구현](https://github.com/modelcontextprotocol/servers)**: MCP 서버의 참조 구현

> **중요**: MCP는 컨텍스트 교환을 위한 프로토콜에만 초점을 맞춥니다. AI 애플리케이션이 LLM을 사용하거나 제공된 컨텍스트를 관리하는 방법은 규정하지 않습니다.

---

## MCP의 핵심 개념

### 참여자 (Participants)

MCP는 클라이언트-서버 아키텍처를 따릅니다. **MCP 호스트**(Claude Code, Claude Desktop 같은 AI 애플리케이션)가 하나 이상의 MCP 서버에 연결을 설정합니다. MCP 호스트는 각 MCP 서버마다 하나의 MCP 클라이언트를 생성하여 이를 수행합니다.

- **로컬 MCP 서버**: STDIO 전송을 사용하며 일반적으로 단일 MCP 클라이언트를 제공
- **원격 MCP 서버**: Streamable HTTP 전송을 사용하며 일반적으로 여러 MCP 클라이언트를 제공

#### MCP 아키텍처의 주요 참여자:

1. **MCP 호스트 (MCP Host)**
    - 하나 또는 여러 MCP 클라이언트를 조정하고 관리하는 AI 애플리케이션
2. **MCP 클라이언트 (MCP Client)**
    - MCP 서버와의 연결을 유지하고 MCP 호스트가 사용할 컨텍스트를 MCP 서버로부터 가져오는 컴포넌트
3. **MCP 서버 (MCP Server)**
    - MCP 클라이언트에 컨텍스트를 제공하는 프로그램

#### 예시

Visual Studio Code가 MCP 호스트로 작동하는 경우:

- **Sentry MCP 서버**에 연결 → VS Code 런타임이 MCP 클라이언트 객체를 인스턴스화
- **로컬 파일시스템 서버**에 연결 → VS Code 런타임이 추가 MCP 클라이언트 객체를 인스턴스화

> **참고**: "MCP 서버"는 실행 위치와 관계없이 컨텍스트 데이터를 제공하는 프로그램을 의미합니다.
> 
> - **로컬 서버**: STDIO 전송 사용 (예: filesystem 서버)
> - **원격 서버**: Streamable HTTP 전송 사용 (예: Sentry MCP 서버)

---

### 레이어 (Layers)

MCP는 두 개의 레이어로 구성됩니다:

#### 1. 데이터 레이어 (Data Layer)

클라이언트-서버 통신을 위한 JSON-RPC 기반 프로토콜을 정의합니다.

포함 내용:

- 라이프사이클 관리
- 핵심 프리미티브 (tools, resources, prompts, notifications)

#### 2. 전송 레이어 (Transport Layer)

클라이언트와 서버 간의 데이터 교환을 가능하게 하는 통신 메커니즘을 정의합니다.

포함 내용:

- 전송별 연결 설정
- 메시지 프레이밍
- 인증

개념적으로 데이터 레이어는 내부 레이어이고, 전송 레이어는 외부 레이어입니다.

---

### 데이터 레이어 세부사항

데이터 레이어는 메시지 구조와 의미를 정의하는 [JSON-RPC 2.0](https://www.jsonrpc.org/) 기반 교환 프로토콜을 구현합니다.

#### 주요 기능:

**라이프사이클 관리**

- 연결 초기화
- 기능 협상
- 연결 종료

**서버 기능**

- **Tools**: AI 작업을 위한 도구
- **Resources**: 컨텍스트 데이터를 위한 리소스
- **Prompts**: 상호작용 템플릿을 위한 프롬프트

**클라이언트 기능**

- **Sampling**: 호스트 LLM에서 샘플링
- **Elicitation**: 사용자로부터 입력 유도
- **Logging**: 클라이언트에 메시지 로깅

**유틸리티 기능**

- **Notifications**: 실시간 업데이트를 위한 알림
- **Progress tracking**: 장기 실행 작업을 위한 진행 상황 추적

---

### 전송 레이어 세부사항

전송 레이어는 클라이언트와 서버 간의 통신 채널과 인증을 관리합니다.

#### MCP가 지원하는 두 가지 전송 메커니즘:

**1. STDIO 전송**

- 표준 입력/출력 스트림 사용
- 동일 머신의 로컬 프로세스 간 직접 통신
- 네트워크 오버헤드 없이 최적의 성능 제공

**2. Streamable HTTP 전송**

- 클라이언트-서버 메시지에 HTTP POST 사용
- 스트리밍 기능을 위한 선택적 Server-Sent Events
- 원격 서버 통신 가능
- 표준 HTTP 인증 방법 지원:
    - Bearer 토큰
    - API 키
    - 커스텀 헤더
    - OAuth (권장)

> 전송 레이어는 프로토콜 레이어에서 통신 세부사항을 추상화하여 모든 전송 메커니즘에서 동일한 JSON-RPC 2.0 메시지 형식을 사용할 수 있게 합니다.

---

## 데이터 레이어 프로토콜

MCP의 핵심은 MCP 클라이언트와 MCP 서버 간의 스키마와 의미를 정의하는 것입니다. 개발자는 데이터 레이어, 특히 **프리미티브(primitives)** 세트가 MCP에서 가장 흥미로운 부분일 것입니다.

MCP는 기본 RPC 프로토콜로 **JSON-RPC 2.0**을 사용합니다.

---

### 라이프사이클 관리

MCP는 라이프사이클 관리가 필요한 상태 유지 프로토콜입니다.

**목적**: 클라이언트와 서버가 지원하는 기능을 협상

자세한 정보는 [사양 문서](https://claude.ai/specification/latest/basic/lifecycle)를 참조하세요.

---

### 프리미티브 (Primitives)

MCP 프리미티브는 MCP에서 가장 중요한 개념입니다. 클라이언트와 서버가 서로에게 제공할 수 있는 것을 정의합니다.

#### 서버가 노출할 수 있는 세 가지 핵심 프리미티브:

**1. Tools (도구)**

- AI 애플리케이션이 호출하여 작업을 수행할 수 있는 실행 가능한 함수
- 예: 파일 작업, API 호출, 데이터베이스 쿼리

**2. Resources (리소스)**

- AI 애플리케이션에 컨텍스트 정보를 제공하는 데이터 소스
- 예: 파일 내용, 데이터베이스 레코드, API 응답

**3. Prompts (프롬프트)**

- 언어 모델과의 상호작용을 구조화하는 재사용 가능한 템플릿
- 예: 시스템 프롬프트, few-shot 예제

각 프리미티브 타입에는 다음과 같은 연관 메서드가 있습니다:

- **발견 (Discovery)**: `*/list`
- **검색 (Retrieval)**: `*/get`
- **실행 (Execution)**: `tools/call` (일부 경우)

#### 구체적인 예시

데이터베이스에 대한 컨텍스트를 제공하는 MCP 서버:

- **Tools**: 데이터베이스 쿼리용 도구
- **Resource**: 데이터베이스 스키마를 포함하는 리소스
- **Prompt**: 도구와 상호작용하기 위한 few-shot 예제를 포함하는 프롬프트

더 자세한 내용은 [서버 개념](https://claude.ai/chat/server-concepts) 참조.

---

#### 클라이언트가 노출할 수 있는 프리미티브:

**1. Sampling (샘플링)**

- 서버가 클라이언트의 AI 애플리케이션에서 언어 모델 완성을 요청할 수 있게 함
- 모델 독립적으로 유지하면서 언어 모델 액세스가 필요한 경우 유용
- 메서드: `sampling/complete`

**2. Elicitation (유도)**

- 서버가 사용자로부터 추가 정보를 요청할 수 있게 함
- 사용자 확인이나 추가 정보가 필요한 경우 유용
- 메서드: `elicitation/request`

**3. Logging (로깅)**

- 서버가 디버깅 및 모니터링 목적으로 클라이언트에 로그 메시지를 보낼 수 있게 함

더 자세한 내용은 [클라이언트 개념](https://claude.ai/chat/client-concepts) 참조.

---

#### 범용 유틸리티 프리미티브:

**Tasks (실험적)**

- 지연된 결과 검색과 상태 추적을 가능하게 하는 지속 가능한 실행 래퍼
- 사용 사례: 비용이 많이 드는 계산, 워크플로우 자동화, 배치 처리, 다단계 작업

---

### 알림 (Notifications)

프로토콜은 서버와 클라이언트 간의 동적 업데이트를 가능하게 하는 실시간 알림을 지원합니다.

**예시**: 서버의 사용 가능한 도구가 변경되면(새 기능 추가, 기존 도구 수정 등) 서버가 연결된 클라이언트에 도구 업데이트 알림을 보낼 수 있습니다.

알림은 JSON-RPC 2.0 알림 메시지로 전송되며(응답을 기대하지 않음) MCP 서버가 연결된 클라이언트에 실시간 업데이트를 제공할 수 있게 합니다.

---

## 예제: MCP 클라이언트-서버 상호작용

### 데이터 레이어 동작 흐름

이 섹션에서는 MCP 클라이언트-서버 상호작용을 단계별로 살펴봅니다.

---

### 1단계: 초기화 (라이프사이클 관리)

MCP는 기능 협상 핸드셰이크를 통한 라이프사이클 관리로 시작합니다.

#### 초기화 요청

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2025-06-18",
    "capabilities": {
      "elicitation": {}
    },
    "clientInfo": {
      "name": "example-client",
      "version": "1.0.0"
    }
  }
}
```

#### 초기화 응답

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2025-06-18",
    "capabilities": {
      "tools": {
        "listChanged": true
      },
      "resources": {}
    },
    "serverInfo": {
      "name": "example-server",
      "version": "1.0.0"
    }
  }
}
```

#### 초기화 교환 이해하기

초기화 프로세스는 여러 중요한 목적을 수행합니다:

**1. 프로토콜 버전 협상**

- `protocolVersion` 필드로 호환 가능한 프로토콜 버전 사용 보장
- 호환되지 않는 버전 간 통신 오류 방지
- 상호 호환 버전 협상 실패 시 연결 종료

**2. 기능 발견**

- `capabilities` 객체로 각 참여자가 지원하는 기능 선언
- 지원하는 프리미티브 (tools, resources, prompts) 및 알림 기능 포함
- 지원되지 않는 작업을 피하여 효율적인 통신 가능

**3. 신원 교환**

- `clientInfo`와 `serverInfo` 객체로 디버깅 및 호환성을 위한 식별 정보 제공

#### 예제의 기능 협상

**클라이언트 기능**:

- `"elicitation": {}` - 사용자 상호작용 요청 처리 가능 (`elicitation/create` 메서드 수신 가능)

**서버 기능**:

- `"tools": {"listChanged": true}` - 도구 프리미티브 지원 AND 도구 목록 변경 시 `tools/list_changed` 알림 전송 가능
- `"resources": {}` - 리소스 프리미티브 지원 (`resources/list` 및 `resources/read` 메서드 처리 가능)

#### 초기화 완료 알림

초기화 성공 후, 클라이언트가 준비되었음을 알리는 알림을 보냅니다:

```json
{
  "jsonrpc": "2.0",
  "method": "notifications/initialized"
}
```

#### AI 애플리케이션에서의 동작

초기화 중 AI 애플리케이션의 MCP 클라이언트 관리자는 구성된 서버에 연결을 설정하고 나중에 사용할 수 있도록 해당 기능을 저장합니다.

```python
# 의사 코드
async with stdio_client(server_config) as (read, write):
    async with ClientSession(read, write) as session:
        init_response = await session.initialize()
        if init_response.capabilities.tools:
            app.register_mcp_server(session, supports_tools=True)
        app.set_server_ready(session)
```

---

### 2단계: 도구 발견 (프리미티브)

연결이 설정되면 클라이언트는 `tools/list` 요청을 보내 사용 가능한 도구를 발견할 수 있습니다.

#### 도구 목록 요청

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/list"
}
```

이 요청은 매개변수가 없는 간단한 형태입니다.

#### 도구 목록 응답

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "tools": [
      {
        "name": "weather_current",
        "title": "Get Current Weather",
        "description": "Retrieves current weather data for a location",
        "inputSchema": {
          "type": "object",
          "properties": {
            "location": {
              "type": "string",
              "description": "City name or coordinates"
            },
            "units": {
              "type": "string",
              "enum": ["metric", "imperial"],
              "default": "metric"
            }
          },
          "required": ["location"]
        }
      }
    ]
  }
}
```

#### 도구 발견 응답 이해하기

응답의 `tools` 배열은 각 도구에 대한 포괄적인 메타데이터를 제공합니다.

각 도구 객체의 주요 필드:

- **`name`**: 서버 네임스페이스 내에서 도구의 고유 식별자 (예: `weather_current`)
- **`title`**: 사용자에게 표시할 수 있는 사람이 읽을 수 있는 도구 이름
- **`description`**: 도구의 기능과 사용 시기에 대한 상세 설명
- **`inputSchema`**: 예상 입력 매개변수를 정의하는 JSON Schema
    - 타입 검증 가능
    - 필수 및 선택적 매개변수에 대한 명확한 문서 제공

#### AI 애플리케이션에서의 동작

AI 애플리케이션은 모든 연결된 MCP 서버에서 사용 가능한 도구를 가져와 언어 모델이 액세스할 수 있는 통합 도구 레지스트리로 결합합니다.

```python
# 의사 코드
available_tools = []
for session in app.mcp_server_sessions():
    tools_response = await session.list_tools()
    available_tools.extend(tools_response.tools)
conversation.register_available_tools(available_tools)
```

---

### 3단계: 도구 실행 (프리미티브)

클라이언트는 이제 `tools/call` 메서드를 사용하여 도구를 실행할 수 있습니다.

#### 도구 호출 요청

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "weather_current",
    "arguments": {
      "location": "San Francisco",
      "units": "imperial"
    }
  }
}
```

#### 도구 실행 요청 이해하기

요청 구조의 중요한 구성 요소:

1. **`name`**: 발견 응답의 도구 이름과 정확히 일치해야 함 (`weather_current`)
2. **`arguments`**: 도구의 `inputSchema`에 정의된 입력 매개변수 포함
    - `location`: "San Francisco" (필수 매개변수)
    - `units`: "imperial" (선택적 매개변수, 미지정 시 "metric"으로 기본 설정)
3. **JSON-RPC 구조**: 요청-응답 상관관계를 위한 고유 `id`를 가진 표준 JSON-RPC 2.0 형식

#### 도구 호출 응답

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Current weather in San Francisco:\nTemperature: 72°F\nConditions: Partly cloudy\nHumidity: 65%"
      }
    ]
  }
}
```

#### 도구 실행 응답 이해하기

응답은 MCP의 유연한 콘텐츠 시스템을 보여줍니다:

1. **`content` 배열**: 풍부한 다중 형식 응답(텍스트, 이미지, 리소스 등)을 위한 콘텐츠 객체 배열 반환
2. **콘텐츠 타입**: 각 콘텐츠 객체는 `type` 필드를 가짐 (예: `"type": "text"`)
3. **구조화된 출력**: AI 애플리케이션이 언어 모델 상호작용에 사용할 수 있는 실행 가능한 정보 제공

#### AI 애플리케이션에서의 동작

언어 모델이 대화 중 도구 사용을 결정하면, AI 애플리케이션이 도구 호출을 가로채고 적절한 MCP 서버로 라우팅하여 실행하고, 결과를 대화 흐름의 일부로 LLM에 반환합니다.

```python
# 의사 코드
async def handle_tool_call(conversation, tool_name, arguments):
    session = app.find_mcp_session_for_tool(tool_name)
    result = await session.call_tool(tool_name, arguments)
    conversation.add_tool_result(result.content)
```

---

### 4단계: 실시간 업데이트 (알림)

MCP는 서버가 명시적 요청 없이 클라이언트에 변경 사항을 알릴 수 있는 실시간 알림을 지원합니다.

#### 도구 목록 변경 알림

서버의 사용 가능한 도구가 변경되면 서버가 연결된 클라이언트에 알림을 보낼 수 있습니다:

```json
{
  "jsonrpc": "2.0",
  "method": "notifications/tools/list_changed"
}
```

#### MCP 알림의 주요 특징

1. **응답 불필요**: `id` 필드가 없음 → JSON-RPC 2.0 알림 의미론 따름
2. **기능 기반**: 초기화 시 `"listChanged": true`를 선언한 서버만 이 알림 전송 가능
3. **이벤트 기반**: 서버가 내부 상태 변경에 따라 알림 전송 시기 결정

#### 알림에 대한 클라이언트 응답

클라이언트는 이 알림을 받으면 일반적으로 업데이트된 도구 목록을 요청합니다:

```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "method": "tools/list"
}
```

#### 알림이 중요한 이유

1. **동적 환경**: 서버 상태, 외부 종속성, 사용자 권한에 따라 도구가 추가/제거될 수 있음
2. **효율성**: 클라이언트가 변경 사항을 폴링할 필요 없음 - 업데이트 발생 시 알림 받음
3. **일관성**: 클라이언트가 항상 사용 가능한 서버 기능에 대한 정확한 정보를 가짐
4. **실시간 협업**: 변화하는 컨텍스트에 적응할 수 있는 반응형 AI 애플리케이션 가능

#### AI 애플리케이션에서의 동작

AI 애플리케이션이 도구 변경 알림을 받으면 즉시 도구 레지스트리를 새로 고침하고 LLM의 사용 가능한 기능을 업데이트합니다.

```python
# 의사 코드
async def handle_tools_changed_notification(session):
    tools_response = await session.list_tools()
    app.update_available_tools(session, tools_response.tools)
    if app.conversation.is_active():
        app.conversation.notify_llm_of_new_capabilities()
```

---

## 추가 리소스

- **공식 사양**: [MCP Specification](https://modelcontextprotocol.io/specification/latest)
- **서버 개념**: [Server Concepts](https://claude.ai/docs/learn/server-concepts)
- **클라이언트 개념**: [Client Concepts](https://claude.ai/docs/learn/client-concepts)
- **SDK 문서**: [SDKs](https://claude.ai/docs/sdk)
- **GitHub**: https://github.com/modelcontextprotocol

---

_이 문서는 Model Context Protocol 공식 문서에서 가져온 내용입니다._