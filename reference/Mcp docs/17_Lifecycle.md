# MCP 수명 주기 (Lifecycle)

## 프로토콜 개정판

**현재 버전**: 2025-11-25

---

## 개요

Model Context Protocol (MCP)은 적절한 기능 협상과 상태 관리를 보장하는 엄격한 클라이언트-서버 연결 수명 주기를 정의합니다.

### 수명 주기 3단계

```
┌─────────────────────────────────────┐
│  1. Initialization (초기화)        │
│     - 프로토콜 버전 합의            │
│     - 기능 협상                     │
│     - 구현 정보 교환                │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  2. Operation (작동)                │
│     - 정상적인 프로토콜 통신        │
│     - 협상된 기능 사용              │
│     - 메시지 교환                   │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  3. Shutdown (종료)                 │
│     - 연결의 우아한 종료            │
│     - 리소스 정리                   │
│     - 세션 종료                     │
└─────────────────────────────────────┘
```

---

## 수명 주기 단계 (Lifecycle Phases)

### 1단계: Initialization (초기화)

**정의:** 초기화 단계는 **반드시(MUST)** 클라이언트와 서버 간의 첫 번째 상호작용이어야 합니다.

**목적:** 이 단계에서 클라이언트와 서버는:

- ✅ 프로토콜 버전 호환성 확립
- ✅ 기능 교환 및 협상
- ✅ 구현 세부 정보 공유

---

#### 초기화 흐름

```
클라이언트                      서버
    │                            │
    │  initialize 요청           │
    ├──────────────────────────►│
    │  - protocolVersion         │
    │  - capabilities            │
    │  - clientInfo              │
    │                            │
    │  initialize 응답           │
    │◄──────────────────────────┤
    │  - protocolVersion         │
    │  - capabilities            │
    │  - serverInfo              │
    │                            │
    │  initialized 알림          │
    ├──────────────────────────►│
    │                            │
    ▼                            ▼
  준비 완료                   준비 완료
```

---

#### A. Initialize 요청

**클라이언트 책임:** 클라이언트는 **반드시(MUST)** `initialize` 요청을 전송하여 이 단계를 시작해야 합니다.

**요청 구조:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "roots": {
        "listChanged": true
      },
      "sampling": {},
      "elicitation": {
        "form": {},
        "url": {}
      },
      "tasks": {
        "requests": {
          "elicitation": {
            "create": {}
          },
          "sampling": {
            "createMessage": {}
          }
        }
      }
    },
    "clientInfo": {
      "name": "ExampleClient",
      "title": "Example Client Display Name",
      "version": "1.0.0",
      "description": "An example MCP client application",
      "icons": [
        {
          "src": "https://example.com/icon.png",
          "mimeType": "image/png",
          "sizes": ["48x48"]
        }
      ],
      "websiteUrl": "https://example.com"
    }
  }
}
```

---

**필드 설명:**

|필드|타입|필수|설명|
|---|---|---|---|
|`protocolVersion`|string|✅|지원되는 프로토콜 버전|
|`capabilities`|object|✅|클라이언트 기능|
|`clientInfo`|object|✅|클라이언트 구현 정보|

---

**clientInfo 필드:**

|필드|타입|필수|설명|
|---|---|---|---|
|`name`|string|✅|클라이언트 이름|
|`title`|string|❌|표시 이름|
|`version`|string|✅|클라이언트 버전|
|`description`|string|❌|클라이언트 설명|
|`icons`|array|❌|아이콘 배열|
|`websiteUrl`|string|❌|웹사이트 URL|

---

**클라이언트 기능 예시:**

```json
{
  "capabilities": {
    "roots": {
      "listChanged": true
    },
    "sampling": {},
    "elicitation": {
      "form": {},
      "url": {}
    },
    "tasks": {
      "requests": {
        "elicitation": {
          "create": {}
        },
        "sampling": {
          "createMessage": {}
        }
      }
    }
  }
}
```

---

#### B. Initialize 응답

**서버 책임:** 서버는 **반드시(MUST)** 자체 기능 및 정보로 응답해야 합니다.

**응답 구조:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "logging": {},
      "prompts": {
        "listChanged": true
      },
      "resources": {
        "subscribe": true,
        "listChanged": true
      },
      "tools": {
        "listChanged": true
      },
      "tasks": {
        "list": {},
        "cancel": {},
        "requests": {
          "tools": {
            "call": {}
          }
        }
      }
    },
    "serverInfo": {
      "name": "ExampleServer",
      "title": "Example Server Display Name",
      "version": "1.0.0",
      "description": "An example MCP server providing tools and resources",
      "icons": [
        {
          "src": "https://example.com/server-icon.svg",
          "mimeType": "image/svg+xml",
          "sizes": ["any"]
        }
      ],
      "websiteUrl": "https://example.com/server"
    },
    "instructions": "Optional instructions for the client"
  }
}
```

---

**필드 설명:**

|필드|타입|필수|설명|
|---|---|---|---|
|`protocolVersion`|string|✅|합의된 프로토콜 버전|
|`capabilities`|object|✅|서버 기능|
|`serverInfo`|object|✅|서버 구현 정보|
|`instructions`|string|❌|클라이언트를 위한 선택적 지침|

---

**serverInfo 필드:**

|필드|타입|필수|설명|
|---|---|---|---|
|`name`|string|✅|서버 이름|
|`title`|string|❌|표시 이름|
|`version`|string|✅|서버 버전|
|`description`|string|❌|서버 설명|
|`icons`|array|❌|아이콘 배열|
|`websiteUrl`|string|❌|웹사이트 URL|

---

**서버 기능 예시:**

```json
{
  "capabilities": {
    "logging": {},
    "prompts": {
      "listChanged": true
    },
    "resources": {
      "subscribe": true,
      "listChanged": true
    },
    "tools": {
      "listChanged": true
    }
  }
}
```

---

#### C. Initialized 알림

**클라이언트 책임:** 성공적인 초기화 후, 클라이언트는 **반드시(MUST)** `initialized` 알림을 전송하여 정상 작동을 시작할 준비가 되었음을 나타내야 합니다.

**알림 구조:**

```json
{
  "jsonrpc": "2.0",
  "method": "notifications/initialized"
}
```

**목적:**

- 클라이언트가 준비되었음을 서버에 알림
- 정상 작동 단계 시작 신호
- 양방향 통신 시작 가능

---

#### 초기화 전 제약사항

**클라이언트 제약:**

- ❌ 클라이언트는 서버가 `initialize` 요청에 응답하기 전에 [ping](https://claude.ai/specification/2025-11-25/basic/utilities/ping) 이외의 요청을 **권장하지 않음(SHOULD NOT)** 전송해야 합니다.

**서버 제약:**

- ❌ 서버는 `initialized` 알림을 받기 전에 [ping](https://claude.ai/specification/2025-11-25/basic/utilities/ping) 및 [logging](https://claude.ai/specification/2025-11-25/server/utilities/logging) 이외의 요청을 **권장하지 않음(SHOULD NOT)** 전송해야 합니다.

**예외:**

- ✅ Ping: 연결 확인용
- ✅ Logging (서버만): 초기화 로그

---

### 버전 협상 (Version Negotiation)

#### 협상 프로세스

```
클라이언트                      서버
    │                            │
    │  지원 버전: 2024-11-05     │
    ├──────────────────────────►│
    │                            │
    │                            │  ✅ 지원함
    │  합의 버전: 2024-11-05     │  → 동일 버전 반환
    │◄──────────────────────────┤
    │                            │
```

또는

```
클라이언트                      서버
    │                            │
    │  지원 버전: 2025-01-01     │
    ├──────────────────────────►│
    │                            │
    │                            │  ❌ 지원 안 함
    │  대체 버전: 2024-11-05     │  → 다른 버전 반환
    │◄──────────────────────────┤
    │                            │
    │  ❌ 지원 안 함              │
    │  → 연결 종료 권장          │
```

---

#### 클라이언트 규칙

**요청:**

- ✅ 클라이언트는 `initialize` 요청에서 지원하는 프로토콜 버전을 **반드시(MUST)** 전송해야 함

**버전 선택:**

- ✅ 클라이언트가 지원하는 _최신_ 버전이어야 **권장(SHOULD)** 함

**응답 처리:**

- ✅ 응답의 버전을 지원하지 않으면 **권장(SHOULD)** 연결을 끊어야 함

---

#### 서버 규칙

**응답:**

- ✅ 요청된 버전을 지원하면 **반드시(MUST)** 동일한 버전으로 응답해야 함
- ✅ 요청된 버전을 지원하지 않으면 **반드시(MUST)** 지원하는 다른 버전으로 응답해야 함

**버전 선택:**

- ✅ 서버가 지원하는 _최신_ 버전이어야 **권장(SHOULD)** 함

---

#### HTTP 전송의 추가 요구사항

**HTTP 헤더:**

- ✅ HTTP를 사용하는 경우, 클라이언트는 **반드시(MUST)** MCP 서버에 대한 모든 후속 요청에 다음 헤더를 포함해야 함:

```http
MCP-Protocol-Version: <protocol-version>
```

**예시:**

```http
GET /mcp HTTP/1.1
Host: api.example.com
MCP-Protocol-Version: 2024-11-05
Authorization: Bearer ...
```

**자세한 내용:** [Transports의 Protocol Version Header 섹션](https://claude.ai/specification/2025-11-25/basic/transports#protocol-version-header) 참조

---

#### 버전 협상 예시

**시나리오 1: 성공적인 협상**

```json
// 클라이언트 요청
{
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05"
  }
}

// 서버 응답 (동일 버전 지원)
{
  "id": 1,
  "result": {
    "protocolVersion": "2024-11-05"
  }
}

// ✅ 협상 성공
```

---

**시나리오 2: 버전 불일치 (서버가 대체 버전 제안)**

```json
// 클라이언트 요청
{
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2025-01-01"
  }
}

// 서버 응답 (다른 버전 제안)
{
  "id": 1,
  "result": {
    "protocolVersion": "2024-11-05"
  }
}

// 클라이언트 결정:
// - 2024-11-05 지원 → 계속 진행
// - 2024-11-05 미지원 → 연결 종료
```

---

**시나리오 3: 호환 불가능 (오류 응답)**

```json
// 클라이언트 요청
{
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "1.0.0"
  }
}

// 서버 오류 응답
{
  "id": 1,
  "error": {
    "code": -32602,
    "message": "Unsupported protocol version",
    "data": {
      "supported": ["2024-11-05"],
      "requested": "1.0.0"
    }
  }
}

// ❌ 협상 실패, 연결 종료
```

---

### 기능 협상 (Capability Negotiation)

**정의:** 클라이언트와 서버 기능은 세션 중에 사용할 수 있는 선택적 프로토콜 기능을 설정합니다.

---

#### 주요 기능 (Key Capabilities)

**클라이언트 기능:**

|기능|설명|하위 기능|
|---|---|---|
|`roots`|파일시스템 [루트](https://claude.ai/specification/2025-11-25/client/roots) 제공 능력|`listChanged`|
|`sampling`|LLM [샘플링](https://claude.ai/specification/2025-11-25/client/sampling) 요청 지원|-|
|`elicitation`|서버 [유도](https://claude.ai/specification/2025-11-25/client/elicitation) 요청 지원|`form`, `url`|
|`tasks`|[작업 보강](https://claude.ai/specification/2025-11-25/basic/utilities/tasks) 클라이언트 요청 지원|`requests.*`|
|`experimental`|비표준 실험적 기능 지원 설명|-|

---

**서버 기능:**

|기능|설명|하위 기능|
|---|---|---|
|`prompts`|[프롬프트 템플릿](https://claude.ai/specification/2025-11-25/server/prompts) 제공|`listChanged`|
|`resources`|읽기 가능한 [리소스](https://claude.ai/specification/2025-11-25/server/resources) 제공|`subscribe`, `listChanged`|
|`tools`|호출 가능한 [도구](https://claude.ai/specification/2025-11-25/server/tools) 노출|`listChanged`|
|`logging`|구조화된 [로그 메시지](https://claude.ai/specification/2025-11-25/server/utilities/logging) 전송|-|
|`completions`|인수 [자동완성](https://claude.ai/specification/2025-11-25/server/utilities/completion) 지원|-|
|`tasks`|[작업 보강](https://claude.ai/specification/2025-11-25/basic/utilities/tasks) 서버 요청 지원|`list`, `cancel`, `requests.*`|
|`experimental`|비표준 실험적 기능 지원 설명|-|

---

#### 하위 기능 (Sub-Capabilities)

**`listChanged` (목록 변경 알림):**

- prompts, resources, tools에 대한 목록 변경 알림 지원

**예시:**

```json
{
  "resources": {
    "listChanged": true
  }
}
```

**사용:**

```json
// 서버가 리소스 목록 변경 알림 전송
{
  "method": "notifications/resources/list_changed"
}
```

---

**`subscribe` (구독):**

- 개별 항목의 변경 사항 구독 지원 (리소스 전용)

**예시:**

```json
{
  "resources": {
    "subscribe": true,
    "listChanged": true
  }
}
```

**사용:**

```json
// 클라이언트가 특정 리소스 구독
{
  "method": "resources/subscribe",
  "params": {
    "uri": "file:///project/config.json"
  }
}
```

---

#### 기능 협상 예시

**예시 1: 기본 클라이언트**

```json
{
  "capabilities": {
    "roots": {
      "listChanged": true
    }
  }
}
```

**의미:**

- 파일시스템 루트 제공 가능
- 루트 목록 변경 알림 지원

---

**예시 2: 고급 클라이언트**

```json
{
  "capabilities": {
    "roots": {
      "listChanged": true
    },
    "sampling": {},
    "elicitation": {
      "form": {},
      "url": {}
    }
  }
}
```

**의미:**

- 루트 제공 + 변경 알림
- LLM 샘플링 지원
- 양식 및 URL 유도 지원

---

**예시 3: 완전한 기능 서버**

```json
{
  "capabilities": {
    "logging": {},
    "prompts": {
      "listChanged": true
    },
    "resources": {
      "subscribe": true,
      "listChanged": true
    },
    "tools": {
      "listChanged": true
    },
    "completions": {}
  }
}
```

**의미:**

- 로깅 지원
- 프롬프트 제공 + 변경 알림
- 리소스 제공 + 구독 + 변경 알림
- 도구 제공 + 변경 알림
- 자동완성 지원

---

### 2단계: Operation (작동)

**정의:** 작동 단계 중에 클라이언트와 서버는 협상된 기능에 따라 메시지를 교환합니다.

---

#### 필수 사항

**양측 모두 반드시(MUST):**

**1. 협상된 프로토콜 버전 준수:**

```typescript
// 초기화에서 합의된 버전 사용
const agreedVersion = initializeResponse.protocolVersion;

// 모든 요청에서 이 버전 사용
```

**2. 성공적으로 협상된 기능만 사용:**

```typescript
// 클라이언트가 기능 확인
if (serverCapabilities.resources?.subscribe) {
  // 구독 기능 사용
  await client.subscribe("file:///...");
} else {
  // 대체 방법 사용
  console.log("Subscription not supported");
}
```

---

#### 작동 중 메시지 유형

**클라이언트 → 서버:**

- 리소스 읽기 요청
- 도구 호출 요청
- 프롬프트 가져오기 요청
- 구독 요청 (지원되는 경우)

**서버 → 클라이언트:**

- 샘플링 요청 (지원되는 경우)
- 유도 요청 (지원되는 경우)
- 알림 (로그, 변경 사항 등)

**양방향:**

- Ping (연결 확인)
- 진행 상황 알림
- 취소 알림

---

#### 작동 예시

**리소스 읽기:**

```json
// 요청
{
  "method": "resources/read",
  "params": {
    "uri": "file:///project/readme.md"
  }
}

// 응답
{
  "result": {
    "contents": [
      {
        "uri": "file:///project/readme.md",
        "mimeType": "text/markdown",
        "text": "# Project README..."
      }
    ]
  }
}
```

**도구 호출:**

```json
// 요청
{
  "method": "tools/call",
  "params": {
    "name": "search_files",
    "arguments": {
      "pattern": "*.ts"
    }
  }
}

// 응답
{
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Found 42 files matching *.ts"
      }
    ]
  }
}
```

---

### 3단계: Shutdown (종료)

**정의:** 종료 단계 중에 한쪽 (일반적으로 클라이언트)이 프로토콜 연결을 깔끔하게 종료합니다.

**중요:**

- 특정 종료 메시지가 정의되어 있지 않음
- 대신 기본 전송 메커니즘을 사용하여 연결 종료 신호 전송

---

#### stdio 전송 종료

**클라이언트 시작 종료:**

클라이언트는 **권장(SHOULD)** 다음과 같이 종료를 시작해야 합니다:

**1단계: 입력 스트림 닫기**

```bash
# 자식 프로세스(서버)로의 입력 스트림 닫기
close(stdin)
```

**2단계: 정상 종료 대기**

```bash
# 서버가 종료되기를 기다림
# 합리적인 시간 내에 종료되지 않으면 SIGTERM 전송
```

**3단계: SIGTERM 전송 (필요시)**

```bash
# 서버가 여전히 실행 중이면
kill -TERM <server_pid>
```

**4단계: SIGKILL 전송 (최후의 수단)**

```bash
# SIGTERM 후에도 종료되지 않으면
kill -KILL <server_pid>
```

---

**종료 타임라인:**

```
시간 0초: stdin 닫기
    ↓
시간 0-5초: 서버 종료 대기
    ↓
    서버 종료됨 → ✅ 완료
    서버 실행 중 → 계속
    ↓
시간 5초: SIGTERM 전송
    ↓
시간 5-10초: 서버 종료 대기
    ↓
    서버 종료됨 → ✅ 완료
    서버 실행 중 → 계속
    ↓
시간 10초: SIGKILL 전송
    ↓
    강제 종료 → ✅ 완료
```

---

**서버 시작 종료:**

서버는 **가능(MAY)** 다음과 같이 종료를 시작할 수 있습니다:

```bash
# 1. 클라이언트로의 출력 스트림 닫기
close(stdout)

# 2. 프로세스 종료
exit(0)
```

---

#### HTTP 전송 종료

**종료 메커니즘:** HTTP [전송](https://claude.ai/specification/2025-11-25/basic/transports)의 경우, 종료는 관련 HTTP 연결을 닫음으로써 표시됩니다.

**클라이언트 시작:**

```http
# HTTP 연결 닫기
Connection: close
```

**서버 시작:**

```http
# HTTP 응답 후 연결 닫기
Connection: close
```

**SSE (Server-Sent Events):**

```
# 스트림 종료
# 연결 닫기
```

---

#### 종료 예시

**stdio 클라이언트 종료:**

```typescript
async function shutdown() {
  // 1. stdin 닫기
  server.stdin.end();
  
  // 2. 5초 대기
  await waitForExit(server, 5000);
  
  // 3. 여전히 실행 중이면 SIGTERM
  if (server.isRunning()) {
    server.kill('SIGTERM');
    await waitForExit(server, 5000);
  }
  
  // 4. 여전히 실행 중이면 SIGKILL
  if (server.isRunning()) {
    server.kill('SIGKILL');
  }
}
```

**HTTP 클라이언트 종료:**

```typescript
async function shutdown() {
  // HTTP 연결 닫기
  await httpClient.close();
}
```

---

## 타임아웃 (Timeouts)

### 목적

**방지:**

- 중단된 연결
- 리소스 소진
- 무한 대기

---

### 타임아웃 요구사항

**구현은 권장(SHOULD):**

**1. 모든 전송된 요청에 대한 타임아웃 설정:**

```typescript
const response = await client.request(
  'resources/read',
  params,
  { timeout: 30000 } // 30초
);
```

**2. 타임아웃 시 취소 알림 전송:**

```json
{
  "method": "notifications/cancelled",
  "params": {
    "requestId": "req-123",
    "reason": "Timeout after 30 seconds"
  }
}
```

**3. 응답 대기 중지:**

```typescript
if (elapsedTime > timeout) {
  sendCancellation(requestId);
  stopWaiting();
  throw new TimeoutError();
}
```

---

### SDK 및 미들웨어 권장사항

**요청별 타임아웃 구성 허용:**

```typescript
// SDK 예시
class MCPClient {
  async request(
    method: string,
    params: any,
    options?: {
      timeout?: number;
      retries?: number;
    }
  ) {
    const timeout = options?.timeout || this.defaultTimeout;
    // ...
  }
}
```

**사용 예시:**

```typescript
// 짧은 타임아웃
await client.request('ping', {}, { timeout: 5000 });

// 긴 타임아웃
await client.request('tools/call', params, { timeout: 60000 });
```

---

### 진행 상황 알림 처리

**구현은 가능(MAY):**

**진행 상황 알림 수신 시 타임아웃 시계 재설정:**

```typescript
let timeoutClock = Date.now();

client.on('progress', (notification) => {
  if (notification.requestId === currentRequestId) {
    // 진행 중이므로 시계 재설정
    timeoutClock = Date.now();
  }
});
```

**이유:**

- 작업이 실제로 진행 중임을 의미
- 장기 실행 작업 지원

---

### 최대 타임아웃

**구현은 권장(SHOULD):**

**진행 상황에 관계없이 최대 타임아웃 항상 적용:**

```typescript
const maxTimeout = 300000; // 5분
const progressTimeout = 30000; // 30초

let elapsed = 0;
let lastProgress = Date.now();

setInterval(() => {
  elapsed += 1000;
  
  // 최대 타임아웃 확인
  if (elapsed > maxTimeout) {
    cancelRequest('Maximum timeout exceeded');
  }
  
  // 진행 상황 타임아웃 확인
  if (Date.now() - lastProgress > progressTimeout) {
    cancelRequest('No progress for 30 seconds');
  }
}, 1000);
```

**목적:**

- 오작동하는 클라이언트/서버의 영향 제한
- 리소스 보호

---

### 타임아웃 모범 사례

**권장 타임아웃 값:**

|작업 유형|권장 타임아웃|이유|
|---|---|---|
|Ping|5초|빠른 연결 확인|
|리소스 읽기|30초|파일 I/O|
|도구 호출|60초|복잡한 작업|
|샘플링|120초|LLM 생성|
|초기화|10초|빠른 협상|

**구성 가능:**

```typescript
const timeouts = {
  ping: 5000,
  resourceRead: 30000,
  toolCall: 60000,
  sampling: 120000,
  initialize: 10000,
  default: 30000
};
```

---

## 오류 처리 (Error Handling)

### 처리해야 할 오류 사례

**구현은 준비(SHOULD)해야 합니다:**

---

#### 1. 프로토콜 버전 불일치

**오류 예시:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32602,
    "message": "Unsupported protocol version",
    "data": {
      "supported": ["2024-11-05"],
      "requested": "1.0.0"
    }
  }
}
```

**처리:**

```typescript
try {
  const response = await client.initialize({
    protocolVersion: "1.0.0"
  });
} catch (error) {
  if (error.code === -32602) {
    const supported = error.data.supported;
    console.error(`Server only supports: ${supported.join(', ')}`);
    // 지원되는 버전으로 재시도 또는 종료
  }
}
```

---

#### 2. 필수 기능 협상 실패

**시나리오:** 클라이언트가 필수 기능을 요구하지만 서버가 지원하지 않음

**확인:**

```typescript
const response = await client.initialize(clientCapabilities);

// 필수 기능 확인
if (!response.capabilities.tools) {
  throw new Error("Server does not support required 'tools' capability");
}

if (!response.capabilities.resources?.subscribe) {
  console.warn("Server does not support resource subscriptions");
  // 대체 방법 사용
}
```

---

#### 3. 요청 타임아웃

**오류 처리:**

```typescript
async function requestWithTimeout(
  method: string,
  params: any,
  timeout: number = 30000
): Promise<any> {
  const timeoutPromise = new Promise((_, reject) => {
    setTimeout(() => {
      reject(new TimeoutError(`Request timed out after ${timeout}ms`));
    }, timeout);
  });
  
  const requestPromise = client.request(method, params);
  
  try {
    return await Promise.race([requestPromise, timeoutPromise]);
  } catch (error) {
    if (error instanceof TimeoutError) {
      // 취소 알림 전송
      await client.notify('notifications/cancelled', {
        requestId: getCurrentRequestId(),
        reason: error.message
      });
    }
    throw error;
  }
}
```

---

### 추가 오류 시나리오

**4. 초기화 중 연결 실패:**

```typescript
try {
  await client.connect();
  await client.initialize(capabilities);
} catch (error) {
  console.error("Failed to initialize:", error);
  await client.disconnect();
}
```

**5. 초기화 후 기능 불일치:**

```typescript
// 서버가 선언한 기능과 실제 동작 불일치
if (serverCapabilities.resources?.listChanged) {
  // 변경 알림 구독
  client.on('resources/list_changed', handler);
} else {
  // 폴링 사용
  setInterval(() => client.listResources(), 5000);
}
```

---

### 오류 처리 모범 사례

**1. 우아한 저하:**

```typescript
async function getResource(uri: string) {
  if (serverCapabilities.resources) {
    return await client.readResource(uri);
  } else {
    console.warn("Resources not supported");
    return null;
  }
}
```

**2. 재시도 로직:**

```typescript
async function retryRequest(
  fn: () => Promise<any>,
  maxRetries: number = 3
): Promise<any> {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await sleep(1000 * Math.pow(2, i)); // 지수 백오프
    }
  }
}
```

**3. 명확한 오류 메시지:**

```typescript
class MCPError extends Error {
  constructor(
    public code: number,
    message: string,
    public data?: any
  ) {
    super(message);
    this.name = 'MCPError';
  }
}

// 사용
throw new MCPError(
  -32602,
  "Invalid parameter: 'uri' must be absolute",
  { field: 'uri', value: uri }
);
```

---

## 요약

### 수명 주기 단계

**1. Initialization (초기화):**

- ✅ `initialize` 요청 (클라이언트)
- ✅ `initialize` 응답 (서버)
- ✅ `initialized` 알림 (클라이언트)
- ✅ 버전 협상
- ✅ 기능 협상

**2. Operation (작동):**

- ✅ 협상된 버전 준수
- ✅ 협상된 기능만 사용
- ✅ 정상적인 메시지 교환

**3. Shutdown (종료):**

- ✅ stdio: stdin 닫기 → SIGTERM → SIGKILL
- ✅ HTTP: 연결 닫기

### 중요 개념

**버전 협상:**

- 클라이언트가 최신 버전 제안
- 서버가 지원 여부 응답
- 불일치 시 대체 버전 또는 오류

**기능 협상:**

- 선택적 기능 명시적 선언
- 양측이 기능 확인 후 사용
- 미지원 기능에 대한 우아한 저하

**타임아웃:**

- 모든 요청에 타임아웃 설정
- 진행 상황 알림으로 재설정 가능
- 최대 타임아웃 항상 적용

**오류 처리:**

- 버전 불일치
- 기능 협상 실패
- 요청 타임아웃

MCP 수명 주기는 안정적이고 예측 가능한 클라이언트-서버 상호작용을 보장합니다!

---

## 다음 단계

### 학습 경로

1. **전송**
    
    - [Transports](https://claude.ai/specification/2025-11-25/basic/transports)
    - STDIO vs HTTP
2. **인증**
    
    - [Authorization](https://claude.ai/specification/2025-11-25/basic/authorization)
    - OAuth 2.1
3. **유틸리티**
    
    - Ping, Progress, Cancellation
    - Logging

### 추가 리소스

- **기본 프로토콜**: [Overview](https://claude.ai/specification/2025-11-25/basic)
- **아키텍처**: [Architecture](https://claude.ai/specification/2025-11-25/architecture)
- **GitHub**: https://github.com/modelcontextprotocol

---

_이 문서는 Model Context Protocol 공식 수명 주기 사양에서 가져온 내용입니다._