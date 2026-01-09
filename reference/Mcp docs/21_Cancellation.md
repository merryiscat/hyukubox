# MCP 취소 (Cancellation)

## 프로토콜 개정판

**현재 버전**: 2025-11-25

---

## 개요

Model Context Protocol (MCP)은 알림 메시지를 통해 진행 중인 요청의 선택적 취소를 지원합니다.

**기능:**

- ✅ 양쪽 모두 취소 알림을 보낼 수 있음
- ✅ 이전에 발행된 요청이 종료되어야 함을 나타냄
- ✅ 선택적 이유 문자열 제공

**사용 사례:**

- 사용자가 장기 실행 작업 취소
- 타임아웃 또는 오류로 인한 요청 중단
- 리소스 정리 및 최적화

---

## Cancellation Flow (취소 흐름)

### 취소 알림 전송

당사자가 진행 중인 요청을 취소하려는 경우, `notifications/cancelled` 알림을 전송합니다.

**알림 내용:**

- 취소할 요청의 ID
- 로깅 또는 표시할 수 있는 선택적 이유 문자열

---

### 알림 형식

```json
{
  "jsonrpc": "2.0",
  "method": "notifications/cancelled",
  "params": {
    "requestId": "123",
    "reason": "User requested cancellation"
  }
}
```

**필드 설명:**

|필드|타입|필수|설명|
|---|---|---|---|
|`jsonrpc`|string|✅|JSON-RPC 버전 ("2.0")|
|`method`|string|✅|"notifications/cancelled"|
|`params`|object|✅|취소 매개변수|
|`params.requestId`|string|✅|취소할 요청의 ID|
|`params.reason`|string|❌|취소 이유 (선택)|

---

### 취소 흐름 다이어그램

```
클라이언트                        서버
   │                               │
   │  1. Request                   │
   │     id: 123                   │
   │     method: tools/call        │
   ├──────────────────────────────►│
   │                               │
   │                               │  2. Processing...
   │                               │     (장기 실행)
   │                               │
   │  3. Cancel Notification       │
   │     requestId: 123            │
   │     reason: "User cancelled"  │
   ├──────────────────────────────►│
   │                               │
   │                               │  4. Stop Processing
   │                               │     Free Resources
   │                               │     (응답 전송 안 함)
   │                               │
```

---

## Behavior Requirements (동작 요구사항)

### 1. 취소할 수 있는 요청

**필수 조건:** 취소 알림은 **반드시(MUST)** 다음 조건을 충족하는 요청만 참조해야 합니다:

**조건 A: 동일한 방향으로 이전에 발행됨**

- 클라이언트가 보낸 요청은 클라이언트가 취소
- 서버가 보낸 요청은 서버가 취소

**조건 B: 여전히 진행 중인 것으로 믿어짐**

- 응답이 아직 수신되지 않음
- 요청이 완료되지 않은 것으로 보임

**예시:**

```typescript
// ✅ 올바른 취소
const requestId = await client.sendRequest({
  method: "tools/call",
  params: { name: "long_running_tool", arguments: {} }
});

// 요청이 진행 중인 동안
client.sendNotification({
  method: "notifications/cancelled",
  params: {
    requestId: requestId,
    reason: "User cancelled"
  }
});

// ❌ 잘못된 취소 - 이미 완료된 요청
const response = await client.sendRequest(...);
// 응답 수신 후
client.sendNotification({
  method: "notifications/cancelled",
  params: { requestId: response.id }  // 너무 늦음!
});
```

---

### 2. initialize 요청 취소 금지

**필수:**

- ✅ `initialize` 요청은 **절대(MUST NOT)** 클라이언트가 취소해서는 안 됨

**이유:**

- `initialize`는 연결 설정의 중요한 부분
- 취소하면 프로토콜 상태가 불확실해짐

**예시:**

```typescript
// ❌ 금지됨
const initRequestId = await client.sendRequest({
  method: "initialize",
  params: { ... }
});

// 절대 하지 마세요!
client.sendNotification({
  method: "notifications/cancelled",
  params: { requestId: initRequestId }
});
```

---

### 3. Task 취소는 별도 메커니즘 사용

**필수:** [task-augmented requests](https://claude.ai/chat/tasks)의 경우:

- ✅ `tasks/cancel` 요청을 **반드시(MUST)** 사용해야 함
- ❌ `notifications/cancelled` 알림을 사용해서는 안 됨

**이유:**

- Task는 자체 전용 취소 메커니즘을 가짐
- 최종 task 상태를 반환함

**예시:**

```typescript
// ✅ Task 취소 - 올바른 방법
await client.sendRequest({
  method: "tasks/cancel",
  params: {
    taskId: "task-123"
  }
});
// 응답: { status: "cancelled", ... }

// ❌ Task 취소 - 잘못된 방법
client.sendNotification({
  method: "notifications/cancelled",
  params: { requestId: "task-123" }  // Task에는 사용 안 됨!
});
```

---

### 4. 수신자의 권장 동작

취소 알림을 받은 수신자는 **권장(SHOULD)**:

**A. 취소된 요청 처리 중지**

```typescript
const activeRequests = new Map();

// 요청 처리 시작
async function handleRequest(id, request) {
  const abortController = new AbortController();
  activeRequests.set(id, abortController);
  
  try {
    await processRequest(request, abortController.signal);
  } finally {
    activeRequests.delete(id);
  }
}

// 취소 알림 처리
function handleCancellation(requestId, reason) {
  const controller = activeRequests.get(requestId);
  
  if (controller) {
    console.log(`Cancelling request ${requestId}: ${reason}`);
    controller.abort();  // 처리 중지
  }
}
```

---

**B. 관련 리소스 해제**

```typescript
function handleCancellation(requestId, reason) {
  const request = activeRequests.get(requestId);
  
  if (request) {
    // 처리 중지
    request.abort();
    
    // 리소스 해제
    if (request.fileHandle) {
      request.fileHandle.close();
    }
    
    if (request.databaseConnection) {
      request.databaseConnection.release();
    }
    
    if (request.networkStream) {
      request.networkStream.destroy();
    }
    
    // 정리
    activeRequests.delete(requestId);
    
    console.log(`Freed resources for request ${requestId}`);
  }
}
```

---

**C. 취소된 요청에 대한 응답 전송 안 함**

```typescript
async function handleRequest(id, request) {
  try {
    const result = await processRequest(request);
    
    // 취소되었는지 확인
    if (activeRequests.has(id)) {
      // 취소되지 않았으면 응답 전송
      sendResponse(id, result);
    } else {
      // 취소되었으면 응답 전송 안 함
      console.log(`Request ${id} was cancelled, not sending response`);
    }
  } catch (error) {
    if (!activeRequests.has(id)) {
      // 취소됨 - 오류 응답도 전송 안 함
      return;
    }
    
    sendError(id, error);
  }
}
```

---

### 5. 수신자가 취소 알림을 무시할 수 있는 경우

수신자는 **가능(MAY)** 다음 경우 취소 알림을 무시할 수 있습니다:

**경우 A: 참조된 요청을 알 수 없음**

```typescript
function handleCancellation(requestId, reason) {
  if (!activeRequests.has(requestId)) {
    console.warn(`Unknown request ${requestId}, ignoring cancellation`);
    return;  // 무시
  }
  
  // 처리...
}
```

---

**경우 B: 처리가 이미 완료됨**

```typescript
function handleCancellation(requestId, reason) {
  const request = activeRequests.get(requestId);
  
  if (!request) {
    console.log(`Request ${requestId} already completed, ignoring cancellation`);
    return;  // 무시
  }
  
  if (request.completed) {
    console.log(`Request ${requestId} completed, ignoring cancellation`);
    return;  // 무시
  }
  
  // 처리...
}
```

---

**경우 C: 요청을 취소할 수 없음**

```typescript
function handleCancellation(requestId, reason) {
  const request = activeRequests.get(requestId);
  
  if (request && request.nonCancellable) {
    console.warn(`Request ${requestId} cannot be cancelled (critical operation)`);
    return;  // 무시
  }
  
  // 처리...
}
```

**취소 불가능한 작업 예시:**

- 중요한 데이터베이스 트랜잭션
- 돌이킬 수 없는 외부 API 호출
- 보안 관련 작업

---

### 6. 발신자의 권장 동작

취소 알림의 발신자는 **권장(SHOULD)** 이후 도착하는 요청에 대한 응답을 무시해야 합니다.

**구현:**

```typescript
const cancelledRequests = new Set();

function cancelRequest(requestId, reason) {
  // 취소 표시
  cancelledRequests.add(requestId);
  
  // 취소 알림 전송
  sendNotification({
    method: "notifications/cancelled",
    params: { requestId, reason }
  });
  
  // 타임아웃 후 취소 표시 제거
  setTimeout(() => {
    cancelledRequests.delete(requestId);
  }, 5000);
}

function handleResponse(id, response) {
  if (cancelledRequests.has(id)) {
    console.log(`Ignoring response for cancelled request ${id}`);
    return;  // 무시
  }
  
  // 정상 응답 처리
  processResponse(response);
}
```

---

## Timing Considerations (타이밍 고려사항)

### 경쟁 조건 (Race Conditions)

**문제:** 네트워크 대기 시간으로 인해 취소 알림이 요청 처리가 완료된 후 도착할 수 있으며, 잠재적으로 응답이 이미 전송된 후에 도착할 수 있습니다.

**필수:** 양쪽 모두 **반드시(MUST)** 이러한 경쟁 조건을 우아하게 처리해야 합니다.

---

### 경쟁 조건 시나리오

#### 시나리오 1: 취소가 응답 전에 도착

```
클라이언트                        서버
   │                               │
   │  1. Request (id: 123)         │
   ├──────────────────────────────►│
   │                               │
   │                               │  2. Processing...
   │                               │
   │  3. Cancel (id: 123)          │
   ├──────────────────────────────►│
   │                               │
   │                               │  4. Abort Processing
   │                               │     (응답 전송 안 함)
   │                               │
```

**결과:** ✅ 정상적인 취소

---

#### 시나리오 2: 취소와 응답이 교차

```
클라이언트                        서버
   │                               │
   │  1. Request (id: 123)         │
   ├──────────────────────────────►│
   │                               │
   │                               │  2. Processing...
   │                               │  3. Complete
   │                               │
   │  4. Cancel (id: 123)          │  5. Send Response
   ├──────────────────────────────►├────────┐
   │                               │        │
   │  ◄──────────────────────────────────────┘
   │  6. Receive Response          │
   │     (취소 후)                 │
   │                               │
   │                               │  7. Receive Cancel
   │                               │     (응답 후)
```

**결과:**

- 클라이언트: 응답 무시 ✅
- 서버: 취소 알림 무시 ✅

---

#### 시나리오 3: 응답이 취소보다 먼저 도착

```
클라이언트                        서버
   │                               │
   │  1. Request (id: 123)         │
   ├──────────────────────────────►│
   │                               │
   │                               │  2. Fast Processing
   │  3. Response (id: 123)        │  3. Complete
   │◄────────────────────────────────────────┤
   │                               │
   │  4. Cancel (id: 123)          │
   │     (너무 늦음!)              │
   ├──────────────────────────────►│
   │                               │
   │                               │  5. Ignore Cancel
   │                               │     (이미 완료됨)
```

**결과:**

- 클라이언트: 응답 이미 처리됨 ✅
- 서버: 취소 알림 무시 ✅

---

### 경쟁 조건 처리 구현

```typescript
class RequestManager {
  private activeRequests = new Map();
  private cancelledRequests = new Set();
  private completedRequests = new Set();
  
  async sendRequest(request) {
    const id = generateId();
    
    this.activeRequests.set(id, {
      request,
      abortController: new AbortController()
    });
    
    try {
      const response = await this.transport.send(id, request);
      
      // 응답 수신 시
      this.completedRequests.add(id);
      
      // 취소되었는지 확인
      if (this.cancelledRequests.has(id)) {
        console.log(`Ignoring response for cancelled request ${id}`);
        return null;
      }
      
      return response;
      
    } finally {
      this.activeRequests.delete(id);
      
      // 정리 (타임아웃 후)
      setTimeout(() => {
        this.cancelledRequests.delete(id);
        this.completedRequests.delete(id);
      }, 5000);
    }
  }
  
  cancelRequest(id, reason) {
    const request = this.activeRequests.get(id);
    
    if (!request) {
      // 이미 완료되었거나 알 수 없는 요청
      console.log(`Cannot cancel request ${id}: not active`);
      return;
    }
    
    // 취소 표시
    this.cancelledRequests.add(id);
    
    // 취소 알림 전송
    this.transport.sendNotification({
      method: "notifications/cancelled",
      params: { requestId: id, reason }
    });
    
    // 로컬 처리 중단 (있는 경우)
    request.abortController.abort();
  }
  
  handleCancellation(requestId, reason) {
    // 이미 완료되었는지 확인
    if (this.completedRequests.has(requestId)) {
      console.log(`Request ${requestId} already completed, ignoring cancellation`);
      return;
    }
    
    const request = this.activeRequests.get(requestId);
    
    if (!request) {
      console.log(`Unknown request ${requestId}, ignoring cancellation`);
      return;
    }
    
    console.log(`Cancelling request ${requestId}: ${reason}`);
    
    // 처리 중단
    request.abortController.abort();
    
    // 정리
    this.activeRequests.delete(requestId);
  }
}
```

---

## Implementation Notes (구현 참고사항)

### 1. 로깅

**권장:** 양쪽 모두 **권장(SHOULD)** 디버깅을 위해 취소 이유를 로깅해야 합니다.

**구현:**

```typescript
function handleCancellation(requestId, reason) {
  logger.info('Request cancelled', {
    requestId,
    reason,
    timestamp: new Date().toISOString(),
    activeRequests: activeRequests.size
  });
  
  // 처리...
}

function cancelRequest(requestId, reason) {
  logger.info('Cancelling request', {
    requestId,
    reason,
    initiator: 'client',
    timestamp: new Date().toISOString()
  });
  
  // 취소 알림 전송...
}
```

---

### 2. UI 표시

**권장:** 애플리케이션 UI는 **권장(SHOULD)** 취소가 요청되었음을 나타내야 합니다.

**예시:**

```typescript
// React 예시
function RequestStatus({ requestId }) {
  const [status, setStatus] = useState('pending');
  
  const handleCancel = () => {
    setStatus('cancelling');
    
    client.cancelRequest(requestId, 'User requested cancellation');
    
    // UI 업데이트
    toast.info('Cancelling request...');
  };
  
  return (
    <div className="request-status">
      {status === 'pending' && (
        <>
          <Spinner />
          <span>Processing...</span>
          <button onClick={handleCancel}>Cancel</button>
        </>
      )}
      
      {status === 'cancelling' && (
        <>
          <Icon name="cancel" />
          <span>Cancelling...</span>
        </>
      )}
      
      {status === 'cancelled' && (
        <span className="cancelled">Cancelled</span>
      )}
    </div>
  );
}
```

---

## Error Handling (오류 처리)

### 유효하지 않은 취소 알림

유효하지 않은 취소 알림은 **권장(SHOULD)** 무시되어야 합니다:

**무시할 경우:**

#### 1. 알 수 없는 요청 ID

```typescript
function handleCancellation(requestId, reason) {
  if (!activeRequests.has(requestId)) {
    logger.warn('Unknown request ID in cancellation', {
      requestId,
      reason
    });
    return;  // 무시
  }
  
  // 처리...
}
```

---

#### 2. 이미 완료된 요청

```typescript
function handleCancellation(requestId, reason) {
  if (completedRequests.has(requestId)) {
    logger.debug('Cancellation for completed request', {
      requestId,
      reason
    });
    return;  // 무시
  }
  
  // 처리...
}
```

---

#### 3. 잘못된 형식의 알림

```typescript
function handleNotification(notification) {
  if (notification.method !== 'notifications/cancelled') {
    return;
  }
  
  const { requestId, reason } = notification.params || {};
  
  // 검증
  if (!requestId || typeof requestId !== 'string') {
    logger.error('Invalid cancellation notification: missing or invalid requestId', {
      notification
    });
    return;  // 무시
  }
  
  // 처리...
  handleCancellation(requestId, reason);
}
```

---

### "Fire and Forget" 특성 유지

**이유:** 이는 비동기 통신에서 경쟁 조건을 허용하면서 알림의 "fire and forget" 특성을 유지합니다.

**설명:**

- 취소 알림은 응답을 기대하지 않음
- 오류가 발생해도 발신자에게 알리지 않음
- 수신자는 최선의 노력으로 처리

**구현:**

```typescript
// 취소 알림 전송 - 응답 없음
function sendCancellation(requestId, reason) {
  try {
    transport.sendNotification({
      method: "notifications/cancelled",
      params: { requestId, reason }
    });
    
    // 성공 여부와 관계없이 계속 진행
    console.log(`Sent cancellation for ${requestId}`);
    
  } catch (error) {
    // 오류 로깅만, 예외 던지지 않음
    logger.error('Failed to send cancellation', {
      requestId,
      reason,
      error: error.message
    });
  }
}
```

---

## 요약

### MCP 취소 메커니즘

**핵심 개념:**

- 선택적 취소 지원
- 알림 기반 (응답 없음)
- 경쟁 조건 처리 필수
- "Fire and forget" 특성

**취소 알림 형식:**

```json
{
  "jsonrpc": "2.0",
  "method": "notifications/cancelled",
  "params": {
    "requestId": "123",
    "reason": "User requested cancellation"
  }
}
```

**필수 규칙:**

- ✅ 진행 중인 요청만 취소
- ❌ `initialize` 요청 취소 금지
- ✅ Task는 `tasks/cancel` 사용
- ✅ 경쟁 조건 우아하게 처리

**수신자 권장사항:**

- 처리 중지
- 리소스 해제
- 응답 전송 안 함
- 무효한 알림 무시

**발신자 권장사항:**

- 취소 이유 로깅
- 지연된 응답 무시
- UI에 취소 상태 표시

**경쟁 조건 처리:**

- 취소와 응답이 교차할 수 있음
- 양쪽 모두 우아하게 처리해야 함
- 완료된 요청에 대한 취소는 무시

MCP의 취소 메커니즘은 장기 실행 작업을 효율적으로 관리하고 리소스를 최적화하는 데 필수적입니다!

---

_이 문서는 Model Context Protocol 공식 Cancellation 사양에서 가져온 내용입니다._