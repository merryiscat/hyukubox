# MCP 전송 (Transports)

## 프로토콜 개정판

**현재 버전**: 2025-11-25

---

## 개요

MCP는 JSON-RPC를 사용하여 메시지를 인코딩합니다.

**필수 요구사항:**

- ✅ JSON-RPC 메시지는 **반드시(MUST)** UTF-8로 인코딩되어야 함

### 표준 전송 메커니즘

프로토콜은 현재 클라이언트-서버 통신을 위한 두 가지 표준 전송 메커니즘을 정의합니다:

```
┌─────────────────────────────────────┐
│     1. stdio                        │
│     표준 입출력 통신                │
│     (권장)                          │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│     2. Streamable HTTP              │
│     HTTP + SSE 기반 통신            │
│     (원격 서버용)                   │
└─────────────────────────────────────┘
```

**권장사항:**

- ✅ 클라이언트는 **권장(SHOULD)** 가능한 한 stdio를 지원해야 함

**확장성:**

- ✅ 클라이언트와 서버는 플러그인 방식으로 [사용자 정의 전송](https://claude.ai/chat/d1892e31-8053-4913-8394-fadb47edcd3a#custom-transports)을 구현할 수 있음

---

## 1. stdio 전송

### 개요

**stdio** 전송에서:

```
┌──────────────┐              ┌──────────────┐
│   Client     │              │   Server     │
│  (Parent)    │              │  (Child)     │
├──────────────┤              ├──────────────┤
│              │              │              │
│   stdout ◄───┼──────────────┼─── stdout    │
│              │              │              │
│   stdin  ───►┼──────────────┼───► stdin    │
│              │              │              │
│   stderr ◄───┼──────────────┼─── stderr    │
│              │              │              │
└──────────────┘              └──────────────┘
```

---

### 프로세스 모델

**클라이언트 역할:**

- ✅ MCP 서버를 하위 프로세스로 실행

**서버 역할:**

- ✅ 표준 입력(`stdin`)에서 JSON-RPC 메시지 읽기
- ✅ 표준 출력(`stdout`)으로 메시지 전송

---

### 메시지 형식

**메시지 타입:**

- 개별 JSON-RPC 요청
- 개별 JSON-RPC 알림
- 개별 JSON-RPC 응답

**구분자:**

- ✅ 메시지는 줄바꿈으로 구분됨
- ❌ 메시지는 **절대(MUST NOT)** 내장 줄바꿈을 포함해서는 안 됨

**예시:**

```json
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{...}}
{"jsonrpc":"2.0","id":1,"result":{...}}
{"jsonrpc":"2.0","method":"notifications/initialized"}
```

---

### stderr 사용

**서버 로깅:**

- ✅ 서버는 **가능(MAY)** 모든 로깅 목적으로 표준 오류(`stderr`)에 UTF-8 문자열을 작성할 수 있음

**로그 타입:**

- 정보 메시지 (informational)
- 디버그 메시지 (debug)
- 오류 메시지 (error)

**클라이언트 처리:**

- ✅ 클라이언트는 **가능(MAY)** 서버의 `stderr` 출력을 캡처, 전달 또는 무시할 수 있음
- ❌ 클라이언트는 **권장하지 않음(SHOULD NOT)** `stderr` 출력이 오류 조건을 나타낸다고 가정해서는 안 됨

**예시:**

```bash
# 서버 stderr 출력
[INFO] Server starting...
[DEBUG] Loading configuration from /etc/server.conf
[ERROR] Failed to connect to database, retrying...
```

---

### stdout/stdin 제약

**서버 제약:**

- ✅ 서버는 **절대(MUST NOT)** 유효한 MCP 메시지가 아닌 것을 `stdout`에 작성해서는 안 됨

**클라이언트 제약:**

- ✅ 클라이언트는 **절대(MUST NOT)** 유효한 MCP 메시지가 아닌 것을 서버의 `stdin`에 작성해서는 안 됨

**위반 예시 (금지됨):**

```bash
# ❌ 잘못된 예시 - stdout에 디버그 메시지
echo "Debug: Processing request..." > /dev/stdout
{"jsonrpc":"2.0","id":1,"result":{...}}

# ✅ 올바른 예시 - stderr에 디버그 메시지
echo "Debug: Processing request..." > /dev/stderr
{"jsonrpc":"2.0","id":1,"result":{...}}
```

---

### stdio 전송 구현 예시

**서버 (Node.js):**

```javascript
const readline = require('readline');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
  terminal: false
});

rl.on('line', (line) => {
  try {
    const message = JSON.parse(line);
    
    // 메시지 처리
    const response = handleMessage(message);
    
    // stdout에 응답 (줄바꿈 포함)
    console.log(JSON.stringify(response));
  } catch (error) {
    // stderr에 오류 로깅
    console.error('Error processing message:', error);
  }
});
```

**클라이언트 (Python):**

```python
import subprocess
import json

# 서버 프로세스 시작
server = subprocess.Popen(
    ['node', 'server.js'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

# 메시지 전송
request = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {...}
}
server.stdin.write(json.dumps(request) + '\n')
server.stdin.flush()

# 응답 읽기
response_line = server.stdout.readline()
response = json.loads(response_line)

# stderr 로그 처리 (별도 스레드에서)
for log_line in server.stderr:
    print(f"[Server Log] {log_line.strip()}")
```

---

### stdio 장점 및 단점

**장점:**

- ✅ 간단한 구현
- ✅ 추가 네트워크 설정 불필요
- ✅ 로컬 프로세스 간 통신에 적합
- ✅ 자동 프로세스 수명 주기 관리

**단점:**

- ❌ 원격 서버 지원 불가
- ❌ 단일 클라이언트만 연결 가능
- ❌ 서버 프로세스가 클라이언트에 종속

**사용 사례:**

- 로컬 도구 통합
- IDE 플러그인
- 명령줄 애플리케이션
- 개발 및 테스트

---

## 2. Streamable HTTP 전송

### 개요

**이전 버전과의 차이:** 이 전송은 프로토콜 버전 2024-11-05의 [HTTP+SSE 전송](https://claude.ai/specification/2024-11-05/basic/transports#http-with-sse)을 대체합니다.

**특징:**

- 서버는 여러 클라이언트 연결을 처리할 수 있는 독립 프로세스로 작동
- HTTP POST 및 GET 요청 사용
- 선택적으로 Server-Sent Events (SSE)를 사용하여 여러 서버 메시지 스트리밍

**아키텍처:**

```
┌──────────────┐
│  Client 1    │──┐
└──────────────┘  │
                  │   HTTP POST/GET
┌──────────────┐  │   + SSE
│  Client 2    │──┼──────────────► ┌──────────────┐
└──────────────┘  │                │  MCP Server  │
                  │                │  (HTTP)      │
┌──────────────┐  │                └──────────────┘
│  Client 3    │──┘
└──────────────┘
```

---

### MCP 엔드포인트

**필수 요구사항:**

- ✅ 서버는 **반드시(MUST)** POST 및 GET 메서드를 모두 지원하는 단일 HTTP 엔드포인트 경로를 제공해야 함

**예시:**

```
https://example.com/mcp
https://api.myservice.com/v1/mcp
http://localhost:3000/mcp
```

**지원 메서드:**

```http
POST /mcp    # 클라이언트 → 서버 메시지
GET  /mcp    # 서버 → 클라이언트 스트림
DELETE /mcp  # 세션 종료 (선택사항)
```

---

### 보안 경고 (Security Warning)

**중요:** Streamable HTTP 전송을 구현할 때 다음 보안 조치를 **반드시** 취해야 합니다:

#### 1. Origin 헤더 검증

**필수:**

- ✅ 서버는 **반드시(MUST)** 모든 수신 연결에서 `Origin` 헤더를 검증하여 DNS 리바인딩 공격을 방지해야 함

**처리:**

- ✅ `Origin` 헤더가 있고 유효하지 않으면, 서버는 **반드시(MUST)** HTTP 403 Forbidden으로 응답해야 함
- ✅ HTTP 응답 본문은 **가능(MAY)** `id`가 없는 JSON-RPC _오류 응답_을 포함할 수 있음

**구현 예시:**

```javascript
app.use((req, res, next) => {
  const origin = req.headers.origin;
  const allowedOrigins = [
    'https://example.com',
    'https://app.example.com'
  ];
  
  if (origin && !allowedOrigins.includes(origin)) {
    return res.status(403).json({
      jsonrpc: "2.0",
      error: {
        code: -32600,
        message: "Forbidden: Invalid origin",
        data: { origin }
      }
    });
  }
  
  next();
});
```

---

#### 2. 로컬 바인딩

**권장:**

- ✅ 로컬에서 실행할 때, 서버는 **권장(SHOULD)** 모든 네트워크 인터페이스(0.0.0.0)가 아닌 localhost (127.0.0.1)에만 바인딩해야 함

**구현 예시:**

```javascript
// ✅ 올바름
app.listen(3000, '127.0.0.1', () => {
  console.log('Server listening on localhost:3000');
});

// ❌ 위험함 (로컬 서버의 경우)
app.listen(3000, '0.0.0.0', () => {
  console.log('Server listening on all interfaces');
});
```

---

#### 3. 인증 구현

**권장:**

- ✅ 서버는 **권장(SHOULD)** 모든 연결에 대해 적절한 인증을 구현해야 함

**인증 방법:**

- Bearer 토큰
- OAuth 2.1
- API 키
- 세션 쿠키

**구현 예시:**

```javascript
app.use((req, res, next) => {
  const auth = req.headers.authorization;
  
  if (!auth || !auth.startsWith('Bearer ')) {
    return res.status(401).json({
      jsonrpc: "2.0",
      error: {
        code: -32600,
        message: "Unauthorized: Missing or invalid token"
      }
    });
  }
  
  const token = auth.substring(7);
  if (!verifyToken(token)) {
    return res.status(401).json({
      jsonrpc: "2.0",
      error: {
        code: -32600,
        message: "Unauthorized: Invalid token"
      }
    });
  }
  
  next();
});
```

---

**보안 위험:** 이러한 보호 조치가 없으면 공격자가 DNS 리바인딩을 사용하여 원격 웹사이트에서 로컬 MCP 서버와 상호작용할 수 있습니다.

**DNS 리바인딩 공격 예시:**

```
1. 사용자가 악성 웹사이트 방문
2. 웹사이트의 DNS가 localhost로 변경됨
3. 웹사이트 JavaScript가 http://localhost:3000/mcp에 요청 전송
4. Origin 검증이 없으면 요청이 성공
5. 공격자가 로컬 MCP 서버에 접근
```

---

### 서버로 메시지 전송 (Sending Messages to the Server)

#### 기본 규칙

**클라이언트 요구사항:** 클라이언트에서 서버로 전송되는 모든 JSON-RPC 메시지는 **반드시(MUST)** MCP 엔드포인트에 대한 새 HTTP POST 요청이어야 합니다.

---

#### POST 요청 규칙

**1. HTTP 메서드:**

- ✅ 클라이언트는 **반드시(MUST)** HTTP POST를 사용하여 JSON-RPC 메시지를 MCP 엔드포인트로 전송해야 함

**2. Accept 헤더:**

- ✅ 클라이언트는 **반드시(MUST)** `Accept` 헤더를 포함해야 함
- ✅ `application/json` 및 `text/event-stream`을 모두 지원되는 콘텐츠 타입으로 나열

**헤더 예시:**

```http
POST /mcp HTTP/1.1
Host: example.com
Accept: application/json, text/event-stream
Content-Type: application/json
MCP-Protocol-Version: 2025-11-25
MCP-Session-Id: session-abc-123
```

**3. 요청 본문:**

- ✅ POST 요청의 본문은 **반드시(MUST)** 단일 JSON-RPC _요청_, _알림_ 또는 _응답_이어야 함

**본문 예시:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list",
  "params": {}
}
```

---

#### 응답 처리

**4. 알림 또는 응답 입력:**

입력이 JSON-RPC _응답_ 또는 _알림_인 경우:

**서버 수락:**

- ✅ 서버가 입력을 수락하면 **반드시(MUST)** 본문 없이 HTTP 상태 코드 202 Accepted를 반환해야 함

**서버 거부:**

- ✅ 서버가 입력을 수락할 수 없으면 **반드시(MUST)** HTTP 오류 상태 코드(예: 400 Bad Request)를 반환해야 함
- ✅ HTTP 응답 본문은 **가능(MAY)** `id`가 없는 JSON-RPC _오류 응답_을 포함할 수 있음

**예시:**

```http
# 알림 전송
POST /mcp HTTP/1.1
Content-Type: application/json

{"jsonrpc":"2.0","method":"notifications/progress","params":{...}}

# 서버 응답
HTTP/1.1 202 Accepted
```

---

**5. 요청 입력:**

입력이 JSON-RPC _요청_인 경우, 서버는 **반드시(MUST)** 다음 중 하나를 반환해야 함:

**옵션 A: SSE 스트림:**

- `Content-Type: text/event-stream`으로 SSE 스트림 시작

**옵션 B: 단일 JSON 객체:**

- `Content-Type: application/json`으로 하나의 JSON 객체 반환

**클라이언트 요구사항:**

- ✅ 클라이언트는 **반드시(MUST)** 두 경우를 모두 지원해야 함

---

#### SSE 스트림 동작

**6. SSE 스트림이 시작되면:**

**A. 초기 이벤트 전송:**

- ✅ 서버는 **권장(SHOULD)** 즉시 이벤트 ID와 빈 `data` 필드로 구성된 SSE 이벤트를 전송하여 클라이언트가 재연결할 수 있도록 준비해야 함

**예시:**

```
id: stream-123:event-0
data: 

```

---

**B. 연결 폴링:**

- ✅ 서버가 이벤트 ID가 있는 SSE 이벤트를 클라이언트에 전송한 후, 서버는 **가능(MAY)** 장기 연결을 피하기 위해 언제든지 _연결_을 닫을 수 있음 (_SSE 스트림_ 종료는 아님)
- ✅ 클라이언트는 **권장(SHOULD)** 그런 다음 재연결을 시도하여 SSE 스트림을 "폴링"해야 함

**폴링 메커니즘:**

```
1. 서버가 이벤트 전송
2. 서버가 연결 닫기 (스트림은 활성 상태)
3. 클라이언트가 Last-Event-ID로 재연결
4. 서버가 스트림 계속 전송
5. 반복...
```

---

**C. retry 필드:**

- ✅ 서버가 _SSE 스트림_을 종료하기 전에 _연결_을 닫는 경우, 연결을 닫기 전에 표준 [`retry`](https://html.spec.whatwg.org/multipage/server-sent-events.html#:~:text=field%20name%20is%20%22retry%22) 필드가 있는 SSE 이벤트를 **권장(SHOULD)** 전송해야 함
- ✅ 클라이언트는 **반드시(MUST)** `retry` 필드를 준수하여 재연결을 시도하기 전에 지정된 밀리초 수를 기다려야 함

**retry 예시:**

```
id: stream-123:event-5
retry: 3000
data: 

```

클라이언트는 3초 후 재연결해야 합니다.

---

**D. 응답 포함:**

- ✅ SSE 스트림은 **권장(SHOULD)** 최종적으로 POST 본문에서 전송된 JSON-RPC _요청_에 대한 JSON-RPC _응답_을 포함해야 함

**예시:**

```
id: stream-123:event-6
data: {"jsonrpc":"2.0","id":1,"result":{...}}

```

---

**E. 중간 메시지:**

- ✅ 서버는 **가능(MAY)** JSON-RPC _응답_을 전송하기 전에 JSON-RPC _요청_ 및 _알림_을 전송할 수 있음
- ✅ 이러한 메시지는 **권장(SHOULD)** 원래 클라이언트 _요청_과 관련되어야 함

**예시:**

```
# 클라이언트 요청
POST /mcp
{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{...}}

# 서버 SSE 응답
id: stream-123:event-1
data: {"jsonrpc":"2.0","method":"notifications/progress","params":{...}}

id: stream-123:event-2
data: {"jsonrpc":"2.0","id":10,"method":"sampling/createMessage","params":{...}}

id: stream-123:event-3
data: {"jsonrpc":"2.0","id":1,"result":{...}}

```

---

**F. 스트림 종료:**

- ✅ 서버는 **가능(MAY)** [세션](https://claude.ai/chat/d1892e31-8053-4913-8394-fadb47edcd3a#session-management)이 만료되면 SSE 스트림을 종료할 수 있음
- ✅ JSON-RPC _응답_이 전송된 후, 서버는 **권장(SHOULD)** SSE 스트림을 종료해야 함

---

**G. 연결 끊김 처리:**

- 연결 끊김은 언제든지 발생할 수 있음 (예: 네트워크 상태로 인해)

**중요 규칙:**

- ❌ 연결 끊김은 **권장하지 않음(SHOULD NOT)** 클라이언트가 요청을 취소하는 것으로 해석되어서는 안 됨
- ✅ 취소하려면 클라이언트는 **권장(SHOULD)** 명시적으로 MCP `CancelledNotification`을 전송해야 함
- ✅ 연결 끊김으로 인한 메시지 손실을 방지하기 위해 서버는 **가능(MAY)** 스트림을 [재개 가능](https://claude.ai/chat/d1892e31-8053-4913-8394-fadb47edcd3a#resumability-and-redelivery)하게 만들 수 있음

---

### 서버로부터 메시지 수신 (Listening for Messages from the Server)

#### GET 요청으로 스트림 열기

**1. GET 요청:**

- ✅ 클라이언트는 **가능(MAY)** MCP 엔드포인트에 HTTP GET을 발행할 수 있음
- 용도: 클라이언트가 먼저 HTTP POST를 통해 데이터를 전송하지 않고도 서버가 클라이언트와 통신할 수 있도록 SSE 스트림 열기

**2. Accept 헤더:**

- ✅ 클라이언트는 **반드시(MUST)** `text/event-stream`을 지원되는 콘텐츠 타입으로 나열하는 `Accept` 헤더를 포함해야 함

**요청 예시:**

```http
GET /mcp HTTP/1.1
Host: example.com
Accept: text/event-stream
MCP-Protocol-Version: 2025-11-25
MCP-Session-Id: session-abc-123
```

---

**3. 서버 응답:** 서버는 **반드시(MUST)** 다음 중 하나를 수행해야 함:

**옵션 A: SSE 스트림 시작:**

- `Content-Type: text/event-stream` 반환

**옵션 B: 메서드 거부:**

- HTTP 405 Method Not Allowed 반환
- 의미: 서버가 이 엔드포인트에서 SSE 스트림을 제공하지 않음

---

**4. SSE 스트림이 시작되면:**

**A. 메시지 전송:**

- ✅ 서버는 **가능(MAY)** 스트림에서 JSON-RPC _요청_ 및 _알림_을 전송할 수 있음
- ✅ 이러한 메시지는 **권장(SHOULD)** 동시 실행 중인 클라이언트 _요청_과 무관해야 함

**B. 응답 전송 제한:**

- ✅ 서버는 **절대(MUST NOT)** 이전 클라이언트 요청과 관련된 스트림을 [재개](https://claude.ai/chat/d1892e31-8053-4913-8394-fadb47edcd3a#resumability-and-redelivery)하는 경우를 **제외하고는** 스트림에서 JSON-RPC _응답_을 전송해서는 안 됨

**C. 스트림 종료:**

- ✅ 서버는 **가능(MAY)** 언제든지 SSE 스트림을 닫을 수 있음
- ✅ 서버가 _스트림_을 종료하지 않고 _연결_을 닫는 경우, POST 요청에 대해 설명된 것과 동일한 폴링 동작을 **권장(SHOULD)** 따라야 함: `retry` 필드를 전송하고 클라이언트가 재연결할 수 있도록 허용

**D. 클라이언트 종료:**

- ✅ 클라이언트는 **가능(MAY)** 언제든지 SSE 스트림을 닫을 수 있음

---

### 여러 연결 (Multiple Connections)

**1. 동시 스트림:**

- ✅ 클라이언트는 **가능(MAY)** 여러 SSE 스트림에 동시에 연결된 상태로 유지할 수 있음

**예시:**

```
클라이언트
├── SSE Stream 1 (POST 요청에서 시작)
├── SSE Stream 2 (GET 요청에서 시작)
└── SSE Stream 3 (POST 요청에서 시작)
```

---

**2. 메시지 브로드캐스팅 금지:**

- ✅ 서버는 **반드시(MUST)** 각 JSON-RPC 메시지를 연결된 스트림 중 하나에만 전송해야 함
- ❌ 즉, 여러 스트림에 걸쳐 동일한 메시지를 **절대(MUST NOT)** 브로드캐스트해서는 안 됨

**올바른 예시:**

```
Stream 1: message-a
Stream 2: message-b
Stream 3: message-c
```

**잘못된 예시:**

```
Stream 1: message-a
Stream 2: message-a  ❌ 중복 브로드캐스트
Stream 3: message-a  ❌ 중복 브로드캐스트
```

---

**3. 메시지 손실 완화:**

- ✅ 메시지 손실의 위험은 **가능(MAY)** 스트림을 [재개 가능](https://claude.ai/chat/d1892e31-8053-4913-8394-fadb47edcd3a#resumability-and-redelivery)하게 만들어 완화할 수 있음

---

### 재개 가능성 및 재전달 (Resumability and Redelivery)

끊어진 연결 재개 및 손실될 수 있는 메시지 재전달을 지원하기 위해:

#### 이벤트 ID

**1. 서버 이벤트 ID:**

- ✅ 서버는 **가능(MAY)** [SSE 표준](https://html.spec.whatwg.org/multipage/server-sent-events.html#event-stream-interpretation)에 설명된 대로 SSE 이벤트에 `id` 필드를 첨부할 수 있음

**ID 고유성:**

- ✅ ID가 있는 경우, ID는 **반드시(MUST)** 해당 [세션](https://claude.ai/chat/d1892e31-8053-4913-8394-fadb47edcd3a#session-management) 내의 모든 스트림에 걸쳐 전역적으로 고유해야 함
- 또는 세션 관리가 사용되지 않는 경우, 해당 특정 클라이언트와의 모든 스트림에 걸쳐 고유해야 함

**ID 인코딩:**

- ✅ 이벤트 ID는 **권장(SHOULD)** 원래 스트림을 식별하기에 충분한 정보를 인코딩하여 서버가 `Last-Event-ID`를 올바른 스트림과 연관시킬 수 있도록 해야 함

**ID 예시:**

```
id: stream-abc:event-1
id: stream-abc:event-2
id: stream-def:event-1
id: stream-def:event-2
```

형식: `{stream-id}:{event-number}`

---

#### 재개 메커니즘

**2. 재개 요청:**

클라이언트가 연결 끊김 후 재개하려는 경우 (네트워크 장애 또는 서버 시작 종료로 인해):

**절차:**

- ✅ 클라이언트는 **권장(SHOULD)** MCP 엔드포인트에 HTTP GET을 발행해야 함
- ✅ 클라이언트는 **권장(SHOULD)** 마지막으로 수신한 이벤트 ID를 나타내기 위해 [`Last-Event-ID`](https://html.spec.whatwg.org/multipage/server-sent-events.html#the-last-event-id-header) 헤더를 포함해야 함

**재개 요청 예시:**

```http
GET /mcp HTTP/1.1
Host: example.com
Accept: text/event-stream
Last-Event-ID: stream-abc:event-5
MCP-Session-Id: session-123
```

---

**서버 재개 처리:**

- ✅ 서버는 **가능(MAY)** 이 헤더를 사용하여 마지막 이벤트 ID 이후 _연결이 끊긴 스트림_에서 전송되었을 메시지를 재생하고 그 지점부터 스트림을 재개할 수 있음
- ✅ 서버는 **절대(MUST NOT)** 다른 스트림에서 전달되었을 메시지를 재생해서는 안 됨

**재개 응답 예시:**

```
# 서버가 이벤트 6부터 재생
id: stream-abc:event-6
data: {"jsonrpc":"2.0","method":"notifications/progress","params":{...}}

id: stream-abc:event-7
data: {"jsonrpc":"2.0","id":1,"result":{...}}

```

---

**재개 규칙:**

- ✅ 이 메커니즘은 원래 스트림이 시작된 방식(POST 또는 GET)에 관계없이 적용됨
- ✅ 재개는 항상 `Last-Event-ID`가 있는 HTTP GET을 통해 수행됨

**요약:** 이러한 이벤트 ID는 서버가 _스트림별_ 기준으로 할당하여 특정 스트림 내에서 커서 역할을 해야 합니다.

---

### 세션 관리 (Session Management)

#### 세션 개념

**MCP "세션":**

- [초기화 단계](https://claude.ai/specification/2025-11-25/basic/lifecycle)로 시작하는 클라이언트와 서버 간의 논리적으로 관련된 상호작용

**목적:** 상태 저장 세션을 설정하려는 서버를 지원하기 위해

---

#### 세션 ID 할당

**1. 서버가 세션 ID 할당:**

Streamable HTTP 전송을 사용하는 서버는:

- ✅ **가능(MAY)** 초기화 시 `InitializeResult`를 포함하는 HTTP 응답의 `MCP-Session-Id` 헤더에 세션 ID를 포함하여 할당할 수 있음

**할당 예시:**

```http
HTTP/1.1 200 OK
Content-Type: application/json
MCP-Session-Id: session-abc-123-def-456

{"jsonrpc":"2.0","id":1,"result":{...}}
```

---

**세션 ID 요구사항:**

**보안:**

- ✅ 세션 ID는 **권장(SHOULD)** 전역적으로 고유하고 암호학적으로 안전해야 함
    - 예: 안전하게 생성된 UUID, JWT 또는 암호화 해시

**형식:**

- ✅ 세션 ID는 **반드시(MUST)** 가시적인 ASCII 문자(0x21에서 0x7E까지)만 포함해야 함

**클라이언트 처리:**

- ✅ 클라이언트는 **반드시(MUST)** 세션 ID를 안전한 방식으로 처리해야 함
- 자세한 내용은 [Session Hijacking 완화](https://claude.ai/specification/2025-11-25/basic/security_best_practices#session-hijacking) 참조

---

#### 세션 ID 사용

**2. 클라이언트가 세션 ID 포함:**

초기화 중에 서버가 `MCP-Session-Id`를 반환하는 경우:

- ✅ Streamable HTTP 전송을 사용하는 클라이언트는 **반드시(MUST)** 모든 후속 HTTP 요청의 `MCP-Session-Id` 헤더에 이를 포함해야 함

**요청 예시:**

```http
POST /mcp HTTP/1.1
Host: example.com
Content-Type: application/json
MCP-Session-Id: session-abc-123-def-456
MCP-Protocol-Version: 2025-11-25

{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}
```

---

**세션 ID 필수화:**

- ✅ 세션 ID가 필요한 서버는 **권장(SHOULD)** (초기화 이외의) `MCP-Session-Id` 헤더가 없는 요청에 HTTP 400 Bad Request로 응답해야 함

**오류 응답 예시:**

```http
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
  "jsonrpc": "2.0",
  "error": {
    "code": -32600,
    "message": "Missing required MCP-Session-Id header"
  }
}
```

---

#### 세션 종료

**3. 서버 시작 종료:**

- ✅ 서버는 **가능(MAY)** 언제든지 세션을 종료할 수 있음
- ✅ 종료 후, 해당 세션 ID를 포함하는 요청에 **반드시(MUST)** HTTP 404 Not Found로 응답해야 함

**종료 응답 예시:**

```http
HTTP/1.1 404 Not Found
Content-Type: application/json

{
  "jsonrpc": "2.0",
  "error": {
    "code": -32600,
    "message": "Session not found or expired",
    "data": {
      "sessionId": "session-abc-123-def-456"
    }
  }
}
```

---

**4. 클라이언트 새 세션 시작:**

`MCP-Session-Id`를 포함하는 요청에 대한 응답으로 HTTP 404를 받으면:

- ✅ 클라이언트는 **반드시(MUST)** 세션 ID가 첨부되지 않은 새 `InitializeRequest`를 전송하여 새 세션을 시작해야 함

**새 세션 시작:**

```http
POST /mcp HTTP/1.1
Host: example.com
Content-Type: application/json
MCP-Protocol-Version: 2025-11-25
# MCP-Session-Id 없음 (새 세션)

{"jsonrpc":"2.0","id":1,"method":"initialize","params":{...}}
```

---

**5. 클라이언트 시작 종료:**

더 이상 특정 세션이 필요하지 않은 클라이언트 (예: 사용자가 클라이언트 애플리케이션을 떠나는 경우):

- ✅ **권장(SHOULD)** 세션을 명시적으로 종료하기 위해 `MCP-Session-Id` 헤더와 함께 MCP 엔드포인트에 HTTP DELETE를 전송해야 함

**종료 요청:**

```http
DELETE /mcp HTTP/1.1
Host: example.com
MCP-Session-Id: session-abc-123-def-456
```

**서버 응답:**

- ✅ 서버는 **가능(MAY)** HTTP 405 Method Not Allowed로 응답할 수 있음
- 의미: 서버가 클라이언트가 세션을 종료하는 것을 허용하지 않음

---

### 시퀀스 다이어그램 (Sequence Diagram)

**기본 Streamable HTTP 흐름:**

```
클라이언트                                서버
   │                                      │
   │  POST /mcp (initialize)              │
   ├─────────────────────────────────────►│
   │                                      │
   │  ◄─ SSE Stream Start                │
   │◄─────────────────────────────────────┤
   │  id: stream-1:0                      │
   │  data:                               │
   │                                      │
   │  ◄─ InitializeResult                │
   │◄─────────────────────────────────────┤
   │  id: stream-1:1                      │
   │  data: {"result":{...}}              │
   │                                      │
   │  POST /mcp (initialized)             │
   ├─────────────────────────────────────►│
   │                                      │
   │  ◄─ 202 Accepted                    │
   │◄─────────────────────────────────────┤
   │                                      │
   │  GET /mcp                            │
   ├─────────────────────────────────────►│
   │                                      │
   │  ◄─ SSE Stream Start                │
   │◄─────────────────────────────────────┤
   │  id: stream-2:0                      │
   │  data:                               │
   │                                      │
   │  POST /mcp (tools/call)              │
   ├─────────────────────────────────────►│
   │                                      │
   │  ◄─ SSE Stream (stream-3)           │
   │◄─────────────────────────────────────┤
   │  id: stream-3:0                      │
   │  data:                               │
   │                                      │
   │  ◄─ Progress notification           │
   │◄─────────────────────────────────────┤
   │  id: stream-3:1                      │
   │  data: {"method":"notifications/..."}│
   │                                      │
   │  ◄─ Tool result                     │
   │◄─────────────────────────────────────┤
   │  id: stream-3:2                      │
   │  data: {"result":{...}}              │
   │                                      │
   │  DELETE /mcp (종료)                  │
   ├─────────────────────────────────────►│
   │                                      │
   │  ◄─ 200 OK                          │
   │◄─────────────────────────────────────┤
```

---

### 프로토콜 버전 헤더 (Protocol Version Header)

**필수 요구사항:** HTTP를 사용하는 경우:

- ✅ 클라이언트는 **반드시(MUST)** MCP 서버에 대한 모든 후속 요청에 `MCP-Protocol-Version: <protocol-version>` HTTP 헤더를 포함해야 함

**목적:** MCP 서버가 MCP 프로토콜 버전에 따라 응답할 수 있도록 허용

**예시:**

```http
POST /mcp HTTP/1.1
Host: example.com
MCP-Protocol-Version: 2025-11-25
Content-Type: application/json

{...}
```

---

**버전 선택:**

- ✅ 클라이언트가 전송하는 프로토콜 버전은 **권장(SHOULD)** [초기화 중에 협상된](https://claude.ai/specification/2025-11-25/basic/lifecycle#version-negotiation) 버전이어야 함

---

**하위 호환성:**

서버가 `MCP-Protocol-Version` 헤더를 받지 **못하고** 버전을 식별할 다른 방법이 없는 경우 (예: 초기화 중에 협상된 프로토콜 버전에 의존):

- ✅ 서버는 **권장(SHOULD)** 프로토콜 버전 `2025-03-26`을 가정해야 함

---

**잘못된 버전 처리:**

서버가 유효하지 않거나 지원되지 않는 `MCP-Protocol-Version`을 받으면:

- ✅ **반드시(MUST)** `400 Bad Request`로 응답해야 함

**오류 응답 예시:**

```http
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
  "jsonrpc": "2.0",
  "error": {
    "code": -32600,
    "message": "Unsupported protocol version",
    "data": {
      "requested": "2025-99-99",
      "supported": ["2025-11-25", "2024-11-05"]
    }
  }
}
```

---

### 하위 호환성 (Backwards Compatibility)

클라이언트와 서버는 다음과 같이 더 이상 사용되지 않는 [HTTP+SSE 전송](https://claude.ai/specification/2024-11-05/basic/transports#http-with-sse) (프로토콜 버전 2024-11-05)과의 하위 호환성을 유지할 수 있습니다:

#### 서버 하위 호환성

**이전 클라이언트를 지원하려는 서버:**

**방법:**

- ✅ 새로운 Streamable HTTP 전송을 위해 정의된 새로운 "MCP 엔드포인트"와 함께 이전 전송의 SSE 및 POST 엔드포인트를 모두 계속 호스팅해야 함

**옵션:**

- 이전 POST 엔드포인트와 새 MCP 엔드포인트를 결합하는 것도 가능하지만 불필요한 복잡성을 초래할 수 있음

**엔드포인트 구조:**

```
# 이전 전송 (2024-11-05)
GET  /sse     # SSE 스트림
POST /message # 메시지 POST

# 새 전송 (2025-11-25)
GET  /mcp     # SSE 스트림 + 메시지
POST /mcp     # 메시지 POST + SSE 스트림
```

---

#### 클라이언트 하위 호환성

**이전 서버를 지원하려는 클라이언트:**

**절차:**

**1. 사용자로부터 URL 수락:**

- 이전 전송 또는 새 전송을 사용하는 서버를 가리킬 수 있음

**2. 새 전송 시도:**

- 위에서 정의한 대로 `Accept` 헤더와 함께 서버 URL에 `InitializeRequest`를 POST하려고 시도

**3. 응답 확인:**

**성공 시:**

- 클라이언트는 새로운 Streamable HTTP 전송을 지원하는 서버라고 가정할 수 있음

**실패 시 (다음 HTTP 상태 코드):**

- "400 Bad Request"
- "404 Not Found"
- "405 Method Not Allowed"

**실패 시 처리:**

- 서버 URL에 GET 요청을 발행하여 SSE 스트림을 열고 첫 번째 이벤트로 `endpoint` 이벤트를 반환할 것으로 예상
- `endpoint` 이벤트가 도착하면, 클라이언트는 이것이 이전 HTTP+SSE 전송을 실행하는 서버라고 가정하고 모든 후속 통신에 해당 전송을 사용해야 함

---

**하위 호환성 흐름:**

```
사용자 → MCP 서버 URL 제공
    ↓
POST /url (InitializeRequest)
    ↓
    ├─ 성공 → 새 Streamable HTTP 전송 사용
    │
    └─ 실패 (400/404/405)
        ↓
        GET /url (SSE 스트림 열기)
        ↓
        endpoint 이벤트 수신?
        ↓
        ├─ 예 → 이전 HTTP+SSE 전송 사용
        │
        └─ 아니오 → 오류 처리
```

---

## 사용자 정의 전송 (Custom Transports)

### 개요

**유연성:**

- ✅ 클라이언트와 서버는 **가능(MAY)** 특정 요구사항에 맞게 추가 사용자 정의 전송 메커니즘을 구현할 수 있음

**전송 불가지론:** 프로토콜은 전송 불가지론적이며 양방향 메시지 교환을 지원하는 모든 통신 채널을 통해 구현될 수 있습니다.

---

### 요구사항

**필수 보존사항:** 사용자 정의 전송을 지원하기로 선택한 구현자는:

- ✅ **반드시(MUST)** MCP에서 정의한 JSON-RPC 메시지 형식 및 수명 주기 요구사항을 보존해야 함

**문서화:** 사용자 정의 전송은:

- ✅ **권장(SHOULD)** 상호 운용성을 돕기 위해 특정 연결 설정 및 메시지 교환 패턴을 문서화해야 함

---

### 사용자 정의 전송 예시

**1. WebSocket:**

```javascript
// 양방향 실시간 통신
const ws = new WebSocket('wss://example.com/mcp');

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  handleMessage(message);
};

ws.send(JSON.stringify({
  jsonrpc: "2.0",
  id: 1,
  method: "initialize",
  params: {...}
}));
```

**2. gRPC:**

```protobuf
service MCP {
  rpc SendMessage(JsonRpcMessage) returns (JsonRpcMessage);
  rpc StreamMessages(stream JsonRpcMessage) returns (stream JsonRpcMessage);
}
```

**3. Unix 소켓:**

```python
import socket
import json

sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
sock.connect('/tmp/mcp.sock')

message = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {...}
}

sock.sendall(json.dumps(message).encode() + b'\n')
response = sock.recv(4096)
```

**4. MQTT:**

```javascript
// Pub/Sub 패턴
const mqtt = require('mqtt');
const client = mqtt.connect('mqtt://localhost:1883');

// 요청 발행
client.publish('mcp/client/requests', JSON.stringify({
  jsonrpc: "2.0",
  id: 1,
  method: "tools/list",
  params: {}
}));

// 응답 구독
client.subscribe('mcp/server/responses');
client.on('message', (topic, message) => {
  const response = JSON.parse(message.toString());
  handleResponse(response);
});
```

---

### 사용자 정의 전송 설계 지침

**1. JSON-RPC 준수:**

- 메시지 형식 유지
- ID 고유성 보장
- 요청-응답 매칭

**2. 수명 주기 준수:**

- 초기화 → 작동 → 종료
- 기능 협상
- 버전 협상

**3. 오류 처리:**

- 전송 수준 오류 처리
- 재연결 로직
- 타임아웃 관리

**4. 보안:**

- 인증 및 권한 부여
- 암호화 (TLS 등)
- 입력 검증

---

## 요약

### 전송 메커니즘 비교

|측면|stdio|Streamable HTTP|사용자 정의|
|---|---|---|---|
|**사용 사례**|로컬 프로세스|원격 서버|특수 요구사항|
|**복잡성**|낮음|중간|다양함|
|**다중 클라이언트**|❌|✅|구현에 따라|
|**네트워크 필요**|❌|✅|구현에 따라|
|**재개 가능성**|❌|✅|구현에 따라|
|**세션 관리**|❌|✅|구현에 따라|

---

### 핵심 개념

**stdio:**

- stdin/stdout 통신
- 줄바꿈 구분 메시지
- stderr 로깅

**Streamable HTTP:**

- POST: 클라이언트 → 서버
- GET: SSE 스트림 열기
- 폴링 및 재개 지원
- 세션 관리

**보안:**

- Origin 헤더 검증 필수
- localhost 바인딩 권장
- 인증 구현 권장

**프로토콜 버전 헤더:**

- HTTP에서 필수
- 협상된 버전 사용
- 하위 호환성 지원

**사용자 정의 전송:**

- JSON-RPC 형식 보존
- 수명 주기 요구사항 준수
- 문서화 권장

MCP 전송은 다양한 배포 시나리오를 지원하는 유연한 통신 계층을 제공합니다!

---

## 다음 단계

### 학습 경로

1. **인증**
    
    - [Authorization](https://claude.ai/specification/2025-11-25/basic/authorization)
    - OAuth 2.1
2. **보안**
    
    - [Security Best Practices](https://claude.ai/specification/2025-11-25/basic/security_best_practices)
    - DNS 리바인딩 방어
3. **유틸리티**
    
    - Ping, Progress, Cancellation
    - Logging

### 추가 리소스

- **수명 주기**: [Lifecycle](https://claude.ai/specification/2025-11-25/basic/lifecycle)
- **기본 프로토콜**: [Overview](https://claude.ai/specification/2025-11-25/basic)
- **GitHub**: https://github.com/modelcontextprotocol

---

_이 문서는 Model Context Protocol 공식 전송 사양에서 가져온 내용입니다._