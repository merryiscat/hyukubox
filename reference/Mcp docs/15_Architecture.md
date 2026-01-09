# MCP 아키텍처 (Architecture)

## 개요

Model Context Protocol (MCP)은 클라이언트-호스트-서버 아키텍처를 따르며, 각 호스트는 여러 클라이언트 인스턴스를 실행할 수 있습니다. 이 아키텍처는 사용자가 명확한 보안 경계를 유지하고 관심사를 분리하면서 애플리케이션 전반에 걸쳐 AI 기능을 통합할 수 있게 합니다. JSON-RPC를 기반으로 구축된 MCP는 클라이언트와 서버 간의 컨텍스트 교환 및 샘플링 조정에 중점을 둔 상태 유지 세션 프로토콜을 제공합니다.

---

## 핵심 구성 요소 (Core Components)

MCP 아키텍처는 세 가지 핵심 구성 요소로 이루어져 있습니다:

```
┌─────────────────────────────────────────┐
│              Host Process                │
│  ┌─────────────────────────────────┐   │
│  │     AI/LLM Integration          │   │
│  │     Context Aggregation         │   │
│  │     Security & Authorization    │   │
│  └─────────────────────────────────┘   │
│                                          │
│  ┌────────┐  ┌────────┐  ┌────────┐   │
│  │Client 1│  │Client 2│  │Client 3│   │
│  └───┬────┘  └───┬────┘  └───┬────┘   │
└──────┼──────────┼──────────┼──────────┘
       │          │          │
       ▼          ▼          ▼
   ┌───────┐  ┌───────┐  ┌───────┐
   │Server1│  │Server2│  │Server3│
   └───────┘  └───────┘  └───────┘
```

---

### 1. Host (호스트)

**정의:** 호스트 프로세스는 컨테이너이자 조정자 역할을 수행합니다.

#### 주요 책임

**클라이언트 관리:**

- ✅ 여러 클라이언트 인스턴스 생성 및 관리
- ✅ 클라이언트 연결 권한 제어
- ✅ 클라이언트 수명 주기 관리

**보안 및 권한:**

- ✅ 보안 정책 및 동의 요구사항 시행
- ✅ 사용자 승인 결정 처리
- ✅ 서버 간 보안 경계 유지

**AI/LLM 통합:**

- ✅ AI/LLM 통합 및 샘플링 조정
- ✅ 클라이언트 간 컨텍스트 집계 관리
- ✅ 모델 응답 조정

#### 호스트 예시

**애플리케이션:**

- Claude Desktop
- IDE (VS Code, IntelliJ)
- 챗봇 플랫폼
- AI 어시스턴트

**역할 예시:**

```
사용자가 "프로젝트 파일 분석" 요청
    ↓
호스트가 요청 받음
    ↓
관련 서버 확인 (파일 시스템 서버, 코드 분석 서버)
    ↓
각 서버에 대한 클라이언트 생성/활성화
    ↓
컨텍스트 수집 및 집계
    ↓
LLM에 전달 및 응답 생성
    ↓
사용자에게 결과 표시
```

---

### 2. Clients (클라이언트)

**정의:** 각 클라이언트는 호스트에 의해 생성되며 격리된 서버 연결을 유지합니다.

#### 주요 책임

**연결 관리:**

- ✅ 서버당 하나의 상태 유지 세션 설정
- ✅ 1:1 서버 관계 유지
- ✅ 프로토콜 협상 및 기능 교환 처리

**메시지 라우팅:**

- ✅ 프로토콜 메시지 양방향 라우팅
- ✅ 구독 및 알림 관리
- ✅ 요청-응답 조정

**보안:**

- ✅ 서버 간 보안 경계 유지
- ✅ 격리된 컨텍스트 관리
- ✅ 권한 검증

#### 클라이언트-서버 관계

**1:1 관계:**

```
Host
├── Client A ──► Server A (파일 시스템)
├── Client B ──► Server B (Git)
└── Client C ──► Server C (데이터베이스)
```

**특징:**

- 각 클라이언트는 정확히 하나의 서버에 연결
- 서버는 여러 클라이언트에서 연결 가능 (다른 호스트)
- 클라이언트 간 직접 통신 없음

#### 클라이언트 워크플로우

```typescript
// 클라이언트 생성 및 연결
const client = host.createClient();
await client.connect(serverConfig);

// 기능 협상
const capabilities = await client.negotiateCapabilities();

// 서버와 통신
const resources = await client.listResources();
const result = await client.callTool("search", { query: "test" });

// 구독 관리
await client.subscribe("resource://files");
client.on("notification", handleNotification);
```

---

### 3. Servers (서버)

**정의:** 서버는 특화된 컨텍스트와 기능을 제공합니다.

#### 주요 책임

**기능 노출:**

- ✅ MCP 프리미티브를 통한 리소스, 도구, 프롬프트 노출
- ✅ 집중된 책임으로 독립적 운영
- ✅ 명확한 인터페이스 제공

**통합:**

- ✅ 클라이언트 인터페이스를 통한 샘플링 요청
- ✅ 보안 제약 준수
- ✅ 로컬 프로세스 또는 원격 서비스로 실행 가능

#### 서버 유형

**로컬 서버:**

```bash
# STDIO 전송 사용
node ./filesystem-server/index.js /home/user/projects
```

**원격 서버:**

```
https://api.example.com/mcp
```

**서버 카테고리:**

|카테고리|예시|주요 기능|
|---|---|---|
|파일 시스템|filesystem, git|파일 읽기/쓰기, 검색|
|데이터베이스|postgresql, mongodb|쿼리, CRUD|
|API 통합|github, slack|외부 서비스 접근|
|도구|calculator, compiler|계산, 변환|
|컨텍스트|documentation, knowledge-base|정보 제공|

#### 서버 구현 예시

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("filesystem-server")

@mcp.resource("file://{path}")
async def read_file(path: str) -> str:
    """파일 내용 읽기"""
    with open(path, 'r') as f:
        return f.read()

@mcp.tool()
async def search_files(pattern: str, directory: str) -> list[str]:
    """파일 검색"""
    # 검색 로직
    return matching_files

@mcp.prompt()
async def code_review(file_path: str) -> str:
    """코드 리뷰 프롬프트"""
    return f"Review the code in {file_path}"
```

---

## 설계 원칙 (Design Principles)

MCP는 아키텍처와 구현을 안내하는 몇 가지 핵심 설계 원칙을 기반으로 합니다:

### 원칙 1: 서버는 구축하기 매우 쉬워야 함

**철학:** 복잡성은 호스트에, 단순성은 서버에

**구현:**

**호스트 책임 (복잡):**

- 🔧 복잡한 오케스트레이션 처리
- 🔧 여러 서버 조정
- 🔧 보안 및 권한 관리
- 🔧 LLM 통합 및 컨텍스트 집계

**서버 책임 (단순):**

- ✅ 특정하고 명확한 기능에 집중
- ✅ 단순한 인터페이스
- ✅ 최소한의 구현 오버헤드
- ✅ 명확한 분리로 유지 관리 가능한 코드

**예시:**

**간단한 날씨 서버:**

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("weather")

@mcp.tool()
async def get_weather(location: str) -> dict:
    """특정 위치의 날씨 가져오기"""
    # 간단한 API 호출
    weather_data = await fetch_weather(location)
    return weather_data
```

**이점:**

- 빠른 개발
- 쉬운 디버깅
- 낮은 진입 장벽
- 광범위한 채택

---

### 원칙 2: 서버는 높은 조합 가능성을 가져야 함

**철학:** 각 서버는 독립적이지만 함께 작동함

**구현:**

**격리된 기능:**

- 🔹 각 서버는 격리된 집중 기능 제공
- 🔹 명확한 책임 경계
- 🔹 최소한의 의존성

**원활한 조합:**

- 🔹 여러 서버를 원활하게 결합 가능
- 🔹 공유 프로토콜로 상호 운용성 보장
- 🔹 모듈식 설계로 확장성 지원

**예시:**

**단일 서버:**

```
파일 시스템 서버
└── 파일 읽기/쓰기
```

**조합된 서버:**

```
프로젝트 분석 워크플로우
├── 파일 시스템 서버 → 파일 읽기
├── Git 서버 → 버전 기록
├── 코드 분석 서버 → 코드 품질
└── 문서 서버 → 컨텍스트
```

**호스트의 조정:**

```typescript
// 호스트가 여러 서버 조정
const fileContent = await filesystemClient.readFile("main.ts");
const gitHistory = await gitClient.getHistory("main.ts");
const analysis = await codeAnalysisClient.analyze(fileContent);
const docs = await docsClient.search("TypeScript best practices");

// 모든 컨텍스트를 LLM에 제공
const response = await llm.complete({
  context: [fileContent, gitHistory, analysis, docs],
  prompt: "Improve this code"
});
```

**이점:**

- 재사용 가능한 구성 요소
- 유연한 워크플로우
- 점진적 기능 추가
- 에코시스템 성장

---

### 원칙 3: 서버는 전체 대화를 읽거나 다른 서버를 "들여다볼" 수 없어야 함

**철학:** 최소 권한 및 격리

**구현:**

**제한된 가시성:**

- 🔒 서버는 필요한 컨텍스트 정보만 수신
- 🔒 전체 대화 기록은 호스트와 함께 유지
- 🔒 각 서버 연결은 격리 유지

**호스트 제어:**

- 🔒 서버 간 상호작용은 호스트에 의해 제어됨
- 🔒 호스트 프로세스가 보안 경계 시행
- 🔒 명시적 권한 부여 필요

**예시:**

**서버 관점 (제한됨):**

```
파일 시스템 서버가 보는 것:
├── 요청: "read file.txt"
├── 응답: [파일 내용]
└── 볼 수 없음:
    ├── 전체 사용자 대화
    ├── 다른 서버의 응답
    └── LLM의 내부 추론
```

**호스트 관점 (전체):**

```
호스트가 보는 것:
├── 전체 대화 기록
├── 모든 서버 응답
│   ├── 파일 시스템 서버: [파일 내용]
│   ├── Git 서버: [커밋 기록]
│   └── 코드 분석 서버: [분석 결과]
├── LLM 컨텍스트 및 응답
└── 사용자 권한 및 선호도
```

**보안 예시:**

```typescript
// 호스트가 컨텍스트 필터링
async function callServer(server, request, fullContext) {
  // 서버에 필요한 최소 컨텍스트만 추출
  const filteredContext = filterContext(fullContext, server.permissions);
  
  // 필터링된 컨텍스트로 서버 호출
  return await server.handle(request, filteredContext);
}
```

**이점:**

- 프라이버시 보호
- 보안 격리
- 최소 권한 원칙
- 신뢰 경계 명확

---

### 원칙 4: 기능을 서버와 클라이언트에 점진적으로 추가할 수 있어야 함

**철학:** 확장성과 하위 호환성

**구현:**

**핵심 프로토콜:**

- 🔄 최소 필수 기능 제공
- 🔄 안정적인 기본 제공

**선택적 기능:**

- 🔄 필요에 따라 추가 기능 협상 가능
- 🔄 서버와 클라이언트가 독립적으로 발전
- 🔄 미래 확장성을 위한 프로토콜 설계

**버전 관리:**

- 🔄 하위 호환성 유지
- 🔄 점진적 업그레이드 가능
- 🔄 우아한 기능 저하

**예시:**

**기본 서버 (핵심 기능만):**

```python
# 버전 1.0 - 기본 리소스만
mcp = FastMCP("basic-server")

@mcp.resource("file://{path}")
async def read_file(path: str) -> str:
    return read_file_content(path)
```

**확장된 서버 (추가 기능):**

```python
# 버전 2.0 - 도구 및 구독 추가
mcp = FastMCP("extended-server")

# 기존 기능 유지
@mcp.resource("file://{path}")
async def read_file(path: str) -> str:
    return read_file_content(path)

# 새 기능 추가
@mcp.tool()
async def search_files(pattern: str) -> list[str]:
    return search(pattern)

# 구독 지원
@mcp.subscribe("file://")
async def watch_files(uri: str):
    # 파일 변경 감시
    pass
```

**기능 협상:**

```typescript
// 클라이언트가 서버 기능 확인
const capabilities = await client.initialize();

if (capabilities.resources?.subscribe) {
  // 구독 사용
  await client.subscribe("file://");
} else {
  // 폴링으로 대체
  setInterval(() => client.listResources(), 5000);
}
```

**이점:**

- 부드러운 업그레이드 경로
- 이전 클라이언트와 호환
- 혁신 가능
- 생태계 성장

---

## 기능 협상 (Capability Negotiation)

Model Context Protocol은 초기화 중에 클라이언트와 서버가 지원하는 기능을 명시적으로 선언하는 기능 기반 협상 시스템을 사용합니다.

### 협상 프로세스

```
클라이언트 연결
    ↓
초기화 요청
    ↓
┌──────────────────────────────────┐
│   기능 교환                       │
│                                  │
│  서버 → 클라이언트               │
│  - resources (구독 포함?)        │
│  - tools                         │
│  - prompts                       │
│                                  │
│  클라이언트 → 서버               │
│  - sampling                      │
│  - roots                         │
│  - notifications                 │
└──────────────────────────────────┘
    ↓
기능 확정
    ↓
세션 시작
```

---

### 서버 기능 선언

**서버가 선언하는 기능:**

**리소스 관련:**

- ✅ 리소스 제공 여부
- ✅ 리소스 구독 지원 여부
- ✅ 리소스 템플릿 지원 여부

**도구 관련:**

- ✅ 도구 제공 여부
- ✅ 도구 목록

**프롬프트 관련:**

- ✅ 프롬프트 템플릿 제공 여부
- ✅ 프롬프트 목록

**서버 기능 예시:**

```json
{
  "capabilities": {
    "resources": {
      "subscribe": true,
      "listChanged": true
    },
    "tools": {
      "listChanged": false
    },
    "prompts": {
      "listChanged": true
    }
  }
}
```

---

### 클라이언트 기능 선언

**클라이언트가 선언하는 기능:**

**샘플링 관련:**

- ✅ LLM 샘플링 지원 여부
- ✅ 지원되는 모델

**루트 관련:**

- ✅ 파일 시스템 루트 제공 여부
- ✅ 루트 변경 알림

**알림 관련:**

- ✅ 서버 알림 처리 여부
- ✅ 진행 상황 추적

**클라이언트 기능 예시:**

```json
{
  "capabilities": {
    "sampling": {
      "models": ["claude-3-opus", "claude-3-sonnet"]
    },
    "roots": {
      "listChanged": true
    }
  }
}
```

---

### 기능과 프로토콜 기능의 관계

각 기능은 세션 중 사용할 수 있는 특정 프로토콜 기능을 잠금 해제합니다.

**예시:**

#### 1. 서버 기능 → 프로토콜 기능

**리소스 구독:**

```json
// 서버 기능
{
  "capabilities": {
    "resources": {
      "subscribe": true
    }
  }
}
```

**사용 가능한 기능:**

```typescript
// 클라이언트가 사용 가능
await client.subscribe("file:///project");

// 서버가 알림 전송 가능
server.notify("resources/updated", { uri: "file:///project/file.txt" });
```

---

#### 2. 도구 호출

**서버 기능:**

```json
{
  "capabilities": {
    "tools": {}
  }
}
```

**사용 가능한 기능:**

```typescript
// 도구 목록 가져오기
const tools = await client.listTools();

// 도구 호출
const result = await client.callTool("search_files", {
  pattern: "*.ts"
});
```

---

#### 3. 샘플링

**클라이언트 기능:**

```json
{
  "capabilities": {
    "sampling": {}
  }
}
```

**사용 가능한 기능:**

```typescript
// 서버가 샘플링 요청 가능
const response = await server.requestSampling({
  messages: [
    { role: "user", content: "Analyze this code" }
  ]
});
```

---

### 기능 검증

**규칙:**

1. **선언된 기능만 사용:**
    
    - ❌ 선언되지 않은 기능 사용 불가
    - ✅ 기능 확인 후 사용
2. **세션 내내 존중:**
    
    - 기능은 세션 중 변경되지 않음
    - 일관된 동작 보장
3. **우아한 저하:**
    
    - 기능이 없으면 대체 방법 사용
    - 명확한 오류 메시지

**검증 예시:**

```typescript
async function useResource(client, uri) {
  const caps = client.getCapabilities();
  
  if (caps.resources?.subscribe) {
    // 구독 사용
    await client.subscribe(uri);
  } else {
    // 폴링으로 대체
    console.warn("Subscription not supported, using polling");
    setInterval(() => client.getResource(uri), 5000);
  }
}
```

---

### 프로토콜 확장성

**설계 목표:**

- 새 기능 추가 가능
- 하위 호환성 유지
- 명확한 협상 메커니즘

**확장 메커니즘:**

1. **새 기능 추가:**
    
    ```json
    {
      "capabilities": {
        "experimental": {
          "tasks": true,
          "streaming": true
        }
      }
    }
    ```
    
2. **기능 버전:**
    
    ```json
    {
      "capabilities": {
        "resources": {
          "version": "2.0",
          "subscribe": true,
          "pagination": true
        }
      }
    }
    ```
    

---

## 요약

### 아키텍처 핵심

**3계층 구조:**

- 🏛️ **Host**: 조정자 및 관리자
- 🔌 **Clients**: 1:1 서버 커넥터
- 🔧 **Servers**: 특화된 기능 제공자

**설계 원칙:**

1. ✅ 서버는 구축하기 쉬워야 함
2. ✅ 서버는 높은 조합 가능성을 가져야 함
3. ✅ 격리 및 프라이버시 유지
4. ✅ 점진적 기능 추가 가능

**기능 협상:**

- 명시적 기능 선언
- 양방향 협상
- 프로토콜 기능 잠금 해제
- 확장 가능한 설계

### 이점

**개발자:**

- 간단한 서버 구현
- 명확한 책임 분리
- 재사용 가능한 구성 요소

**사용자:**

- 안전한 격리
- 모듈식 기능
- 투명한 권한

**생태계:**

- 상호 운용 가능한 서버
- 확장 가능한 프로토콜
- 광범위한 채택

MCP 아키텍처는 단순성, 보안, 확장성의 균형을 맞추어 강력한 AI 통합을 가능하게 합니다!

---

## 다음 단계

### 학습 경로

1. **기본 프로토콜**
    
    - [Overview](https://claude.ai/specification/2025-11-25/basic)
    - JSON-RPC 메시지
    - 연결 수명 주기
2. **서버 기능**
    
    - [Server Features](https://claude.ai/specification/2025-11-25/server)
    - Resources, Tools, Prompts
3. **클라이언트 기능**
    
    - [Client Features](https://claude.ai/specification/2025-11-25/client)
    - Sampling, Roots, Elicitation

### 추가 리소스

- **사양**: [Specification](https://claude.ai/specification/2025-11-25)
- **변경 로그**: [Key Changes](https://claude.ai/specification/2025-11-25/changelog)
- **GitHub**: https://github.com/modelcontextprotocol

---

_이 문서는 Model Context Protocol 공식 아키텍처 사양에서 가져온 내용입니다._