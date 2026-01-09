# MCP Progress (진행 상황)

## 프로토콜 개정판

**현재 버전**: 2025-11-25

---

## 개요

Model Context Protocol (MCP)은 알림 메시지를 통해 장기 실행 작업에 대한 선택적 진행 상황 추적을 지원합니다.

**기능:**

- ✅ 장기 실행 작업의 진행 상황 모니터링
- ✅ 양방향 진행 상황 알림 지원
- ✅ 선택적 진행 상황 추적
- ✅ 유연한 진행 상황 보고

**사용 사례:**

- 대용량 파일 처리
- 데이터베이스 쿼리 실행
- 외부 API 호출
- 복잡한 계산 작업
- 배치 처리

---

## Progress Flow (진행 상황 흐름)

### 1. 진행 상황 요청

당사자가 요청에 대한 진행 상황 업데이트를 _받기_ 원하는 경우, 요청 메타데이터에 `progressToken`을 포함합니다.

**Progress Token 요구사항:**

- ✅ 문자열 또는 정수 값이어야 함 (**MUST**)
- ✅ 발신자가 어떤 수단으로든 선택할 수 있음
- ✅ 모든 활성 요청에서 고유해야 함 (**MUST**)

---

### 요청 형식

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "some_method",
  "params": {
    "_meta": {
      "progressToken": "abc123"
    }
  }
}
```

**필드 설명:**

|필드|타입|필수|설명|
|---|---|---|---|
|`jsonrpc`|string|✅|JSON-RPC 버전 ("2.0")|
|`id`|string/number|✅|요청 식별자|
|`method`|string|✅|호출할 메서드|
|`params`|object|✅|메서드 매개변수|
|`params._meta`|object|✅|메타데이터|
|`params._meta.progressToken`|string/number|✅|진행 상황 토큰 (고유)|

---

### Progress Token 생성 예시

```typescript
// 방법 1: UUID 사용
import { v4 as uuidv4 } from 'uuid';
const progressToken = uuidv4(); // "550e8400-e29b-41d4-a716-446655440000"

// 방법 2: 타임스탬프 + 랜덤
const progressToken = `progress-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
// "progress-1704672000000-k3j4h5g6f"

// 방법 3: 순차 카운터
let progressCounter = 0;
const progressToken = `progress-${++progressCounter}`; // "progress-1"

// 방법 4: 요청 ID 기반
const progressToken = `progress-${requestId}`; // "progress-req-123"
```

---

### 2. 진행 상황 알림

수신자는 **가능(MAY)** 다음을 포함하는 진행 상황 알림을 전송할 수 있습니다:

**알림 내용:**

- 원래의 progress token
- 현재까지의 진행 값
- 선택적 "total" 값
- 선택적 "message" 값

---

### 알림 형식

```json
{
  "jsonrpc": "2.0",
  "method": "notifications/progress",
  "params": {
    "progressToken": "abc123",
    "progress": 50,
    "total": 100,
    "message": "Reticulating splines..."
  }
}
```

**필드 설명:**

|필드|타입|필수|설명|
|---|---|---|---|
|`jsonrpc`|string|✅|JSON-RPC 버전 ("2.0")|
|`method`|string|✅|"notifications/progress"|
|`params`|object|✅|알림 매개변수|
|`params.progressToken`|string/number|✅|원래 요청의 토큰|
|`params.progress`|number|✅|현재 진행 값|
|`params.total`|number|❌|전체 값 (선택, 알 수 없으면 생략)|
|`params.message`|string|❌|사람이 읽을 수 있는 메시지 (선택)|

---

### 진행 상황 값 요구사항

**1. progress 값은 증가해야 함 (필수):**

- ✅ `progress` 값은 **반드시(MUST)** 각 알림마다 증가해야 함
- ✅ total이 알 수 없는 경우에도 증가해야 함

```typescript
// ✅ 올바른 예시
sendProgress({ progress: 0, total: 100 });
sendProgress({ progress: 25, total: 100 });
sendProgress({ progress: 50, total: 100 });
sendProgress({ progress: 100, total: 100 });

// ❌ 잘못된 예시 - progress가 감소
sendProgress({ progress: 50, total: 100 });
sendProgress({ progress: 25, total: 100 }); // 잘못됨!
```

---

**2. 부동 소수점 값 허용 (가능):**

- ✅ `progress` 및 `total` 값은 **가능(MAY)** 부동 소수점일 수 있음

```json
{
  "progressToken": "abc123",
  "progress": 42.5,
  "total": 100.0,
  "message": "Processing item 42.5/100"
}
```

---

**3. message 필드 권장사항:**

- ✅ `message` 필드는 **권장(SHOULD)** 관련 있는 사람이 읽을 수 있는 진행 정보를 제공해야 함

```json
// 좋은 메시지 예시
"Processing file 5 of 10"
"Downloading data: 2.5 MB of 10 MB"
"Analyzing records: 1,234 processed"
"Connecting to database..."
"Finalizing results..."

// 나쁜 메시지 예시
"Working..." (너무 모호함)
"50%" (progress 값과 중복)
"" (빈 문자열)
```

---

## 진행 상황 흐름 다이어그램

### 완전한 진행 상황 추적 흐름

```
클라이언트                        서버
   │                               │
   │  1. Request + progressToken   │
   │     {                         │
   │       method: "tools/call",   │
   │       _meta: {                │
   │         progressToken: "abc"  │
   │       }                       │
   │     }                         │
   ├──────────────────────────────►│
   │                               │
   │                               │  2. Start Processing
   │                               │
   │  3. Progress: 0%              │
   │     { progress: 0, total: 100 }
   │◄────────────────────────────────┤
   │                               │
   │                               │  4. Continue...
   │                               │
   │  5. Progress: 25%             │
   │     { progress: 25,           │
   │       total: 100,             │
   │       message: "Step 1/4" }   │
   │◄────────────────────────────────┤
   │                               │
   │                               │  6. Continue...
   │                               │
   │  7. Progress: 50%             │
   │     { progress: 50,           │
   │       total: 100,             │
   │       message: "Step 2/4" }   │
   │◄────────────────────────────────┤
   │                               │
   │                               │  8. Continue...
   │                               │
   │  9. Progress: 75%             │
   │     { progress: 75,           │
   │       total: 100,             │
   │       message: "Step 3/4" }   │
   │◄────────────────────────────────┤
   │                               │
   │                               │  10. Finish
   │                               │
   │  11. Progress: 100%           │
   │      { progress: 100,         │
   │        total: 100,            │
   │        message: "Complete" }  │
   │◄────────────────────────────────┤
   │                               │
   │  12. Final Response           │
   │      { result: { ... } }      │
   │◄────────────────────────────────┤
```

---

## Behavior Requirements (동작 요구사항)

### 1. 진행 상황 알림 제약

진행 상황 알림은 **반드시(MUST)** 다음 조건을 충족하는 토큰만 참조해야 합니다:

**조건 A: 활성 요청에 제공됨**

- 현재 진행 중인 요청의 토큰이어야 함

**조건 B: 진행 중인 작업과 연결됨**

- 아직 완료되지 않은 작업이어야 함

**구현:**

```typescript
class ProgressTracker {
  private activeTokens = new Map<string, RequestInfo>();
  
  registerToken(token: string, requestId: string) {
    this.activeTokens.set(token, {
      requestId,
      startTime: Date.now(),
      lastProgress: 0
    });
  }
  
  sendProgress(token: string, progress: number, total?: number, message?: string) {
    // 토큰이 활성 상태인지 확인
    if (!this.activeTokens.has(token)) {
      console.warn(`Ignoring progress for inactive token: ${token}`);
      return;
    }
    
    const info = this.activeTokens.get(token)!;
    
    // progress가 증가하는지 확인
    if (progress < info.lastProgress) {
      throw new Error('Progress value must increase');
    }
    
    info.lastProgress = progress;
    
    // 알림 전송
    this.transport.sendNotification({
      method: 'notifications/progress',
      params: { progressToken: token, progress, total, message }
    });
  }
  
  completeToken(token: string) {
    this.activeTokens.delete(token);
  }
}
```

---

### 2. 수신자의 선택권

진행 상황 요청의 수신자는 **가능(MAY)**:

**옵션 A: 진행 상황 알림을 전송하지 않음**

```typescript
// 진행 상황 토큰을 무시하고 바로 결과 반환
async function handleRequest(request) {
  // progressToken이 있어도 무시
  const result = await processRequest(request);
  return result;
}
```

---

**옵션 B: 적절하다고 판단되는 빈도로 알림 전송**

```typescript
// 빈번한 업데이트
async function frequentUpdates(progressToken: string) {
  for (let i = 0; i <= 100; i++) {
    await processChunk(i);
    sendProgress(progressToken, i, 100); // 매 1%마다
  }
}

// 드문 업데이트
async function infrequentUpdates(progressToken: string) {
  sendProgress(progressToken, 0, 100, 'Starting...');
  await processPhase1();
  
  sendProgress(progressToken, 50, 100, 'Halfway...');
  await processPhase2();
  
  sendProgress(progressToken, 100, 100, 'Complete');
}
```

---

**옵션 C: total이 알 수 없으면 생략**

```typescript
// total 알 수 없는 경우
async function unknownTotal(progressToken: string) {
  let itemsProcessed = 0;
  
  while (hasMoreItems()) {
    await processNextItem();
    itemsProcessed++;
    
    // total 없이 progress만
    sendProgress(progressToken, itemsProcessed, undefined, 
                `Processed ${itemsProcessed} items`);
  }
}
```

---

### 3. Task와 함께 사용

[task-augmented requests](https://claude.ai/chat/tasks)의 경우, 원래 요청에 제공된 `progressToken`은 **반드시(MUST)** `CreateTaskResult`가 반환된 후에도 작업의 수명 동안 계속 진행 상황 알림에 사용되어야 합니다.

**규칙:**

- ✅ progress token은 작업이 종료 상태에 도달할 때까지 유효하고 작업과 연결됨
- ✅ 작업에 대한 진행 상황 알림은 **반드시(MUST)** 초기 task-augmented 요청에 제공된 동일한 `progressToken`을 사용해야 함
- ✅ 작업에 대한 진행 상황 알림은 **반드시(MUST)** 작업이 종료 상태(`completed`, `failed`, 또는 `cancelled`)에 도달한 후 중지되어야 함

---

**Task 진행 상황 흐름:**

```
클라이언트                        서버
   │                               │
   │  1. Task Request              │
   │     progressToken: "task-1"   │
   ├──────────────────────────────►│
   │                               │
   │  2. CreateTaskResult          │
   │     taskId: "t-123"           │
   │◄────────────────────────────────┤
   │                               │
   │                               │  3. Task Running
   │                               │
   │  4. Progress: 20%             │
   │     progressToken: "task-1"   │
   │◄────────────────────────────────┤
   │                               │
   │  5. Progress: 50%             │
   │     progressToken: "task-1"   │
   │◄────────────────────────────────┤
   │                               │
   │  6. Progress: 80%             │
   │     progressToken: "task-1"   │
   │◄────────────────────────────────┤
   │                               │
   │                               │  7. Task Completed
   │                               │
   │  8. Progress: 100%            │
   │     progressToken: "task-1"   │
   │◄────────────────────────────────┤
   │                               │
   │  (No more progress after this) │
```

**구현:**

```typescript
class TaskProgressManager {
  private taskTokens = new Map<string, string>(); // taskId -> progressToken
  
  async createTask(request: any): Promise<CreateTaskResult> {
    const taskId = generateTaskId();
    const progressToken = request.params._meta?.progressToken;
    
    if (progressToken) {
      // progressToken을 작업과 연결
      this.taskTokens.set(taskId, progressToken);
    }
    
    // 작업 시작
    this.startTask(taskId);
    
    return { taskId };
  }
  
  private async startTask(taskId: string) {
    const progressToken = this.taskTokens.get(taskId);
    
    try {
      // 작업 실행
      for (let i = 0; i <= 100; i += 20) {
        await processTaskStep(taskId);
        
        if (progressToken) {
          this.sendProgress(progressToken, i, 100);
        }
      }
      
      // 작업 완료
      this.completeTask(taskId);
      
    } catch (error) {
      this.failTask(taskId);
    }
  }
  
  private completeTask(taskId: string) {
    const progressToken = this.taskTokens.get(taskId);
    
    if (progressToken) {
      // 최종 진행 상황
      this.sendProgress(progressToken, 100, 100, 'Completed');
      
      // 더 이상 진행 상황 알림 전송 안 함
      this.taskTokens.delete(taskId);
    }
  }
  
  private failTask(taskId: string) {
    // 실패 시에도 정리
    this.taskTokens.delete(taskId);
  }
}
```

---

## Implementation Notes (구현 참고사항)

### 1. 활성 진행 상황 토큰 추적 (권장)

**권장사항:**

- ✅ 발신자와 수신자 모두 **권장(SHOULD)** 활성 진행 상황 토큰을 추적해야 함

**발신자 (클라이언트) 측:**

```typescript
class ProgressTokenManager {
  private activeTokens = new Set<string>();
  private tokenCallbacks = new Map<string, ProgressCallback>();
  
  createToken(callback: ProgressCallback): string {
    const token = `progress-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    
    this.activeTokens.add(token);
    this.tokenCallbacks.set(token, callback);
    
    return token;
  }
  
  handleProgressNotification(notification: any) {
    const { progressToken, progress, total, message } = notification.params;
    
    // 활성 토큰인지 확인
    if (!this.activeTokens.has(progressToken)) {
      console.warn(`Received progress for unknown token: ${progressToken}`);
      return;
    }
    
    // 콜백 호출
    const callback = this.tokenCallbacks.get(progressToken);
    if (callback) {
      callback(progress, total, message);
    }
  }
  
  completeToken(token: string) {
    this.activeTokens.delete(token);
    this.tokenCallbacks.delete(token);
  }
  
  getActiveTokens(): string[] {
    return Array.from(this.activeTokens);
  }
}
```

---

**수신자 (서버) 측:**

```typescript
class ServerProgressTracker {
  private activeRequests = new Map<string, {
    requestId: string;
    progressToken: string;
    startTime: number;
    lastProgress: number;
  }>();
  
  registerRequest(requestId: string, progressToken?: string) {
    if (progressToken) {
      this.activeRequests.set(progressToken, {
        requestId,
        progressToken,
        startTime: Date.now(),
        lastProgress: 0
      });
    }
  }
  
  sendProgress(
    progressToken: string, 
    progress: number, 
    total?: number, 
    message?: string
  ) {
    const request = this.activeRequests.get(progressToken);
    
    if (!request) {
      console.warn(`No active request for token: ${progressToken}`);
      return;
    }
    
    // progress 증가 확인
    if (progress < request.lastProgress) {
      console.error(`Progress decreased for ${progressToken}: ${request.lastProgress} -> ${progress}`);
      return;
    }
    
    request.lastProgress = progress;
    
    // 알림 전송
    this.transport.sendNotification({
      method: 'notifications/progress',
      params: { progressToken, progress, total, message }
    });
  }
  
  completeRequest(progressToken: string) {
    this.activeRequests.delete(progressToken);
  }
  
  getActiveTokens(): string[] {
    return Array.from(this.activeRequests.keys());
  }
}
```

---

### 2. 속도 제한 (권장)

**권장사항:**

- ✅ 양쪽 모두 **권장(SHOULD)** 플러딩을 방지하기 위해 속도 제한을 구현해야 함

**구현:**

```typescript
class RateLimitedProgressSender {
  private lastSendTime = new Map<string, number>();
  private readonly MIN_INTERVAL = 100; // 최소 100ms 간격
  
  sendProgress(
    token: string,
    progress: number,
    total?: number,
    message?: string
  ) {
    const now = Date.now();
    const lastTime = this.lastSendTime.get(token) || 0;
    const timeSinceLastSend = now - lastTime;
    
    // 최소 간격 확인 (100% 또는 시작/종료는 항상 전송)
    if (timeSinceLastSend < this.MIN_INTERVAL && 
        progress !== 0 && 
        progress !== total) {
      // 스킵
      return;
    }
    
    this.lastSendTime.set(token, now);
    
    // 알림 전송
    this.transport.sendNotification({
      method: 'notifications/progress',
      params: { progressToken: token, progress, total, message }
    });
  }
}
```

**디바운싱 사용:**

```typescript
import { debounce } from 'lodash';

class DebouncedProgressSender {
  private debouncedSenders = new Map<string, Function>();
  
  constructor(private delay: number = 100) {}
  
  sendProgress(
    token: string,
    progress: number,
    total?: number,
    message?: string
  ) {
    // 0%, 100%는 즉시 전송
    if (progress === 0 || progress === total) {
      this.sendImmediately(token, progress, total, message);
      return;
    }
    
    // 디바운스된 sender 가져오기 또는 생성
    if (!this.debouncedSenders.has(token)) {
      const sender = debounce(
        (p: number, t?: number, m?: string) => {
          this.sendImmediately(token, p, t, m);
        },
        this.delay
      );
      this.debouncedSenders.set(token, sender);
    }
    
    // 디바운스된 전송
    const sender = this.debouncedSenders.get(token)!;
    sender(progress, total, message);
  }
  
  private sendImmediately(
    token: string,
    progress: number,
    total?: number,
    message?: string
  ) {
    this.transport.sendNotification({
      method: 'notifications/progress',
      params: { progressToken: token, progress, total, message }
    });
  }
  
  cleanup(token: string) {
    const sender = this.debouncedSenders.get(token);
    if (sender) {
      // @ts-ignore
      sender.flush(); // 대기 중인 호출 즉시 실행
      this.debouncedSenders.delete(token);
    }
  }
}
```

---

### 3. 완료 후 진행 상황 알림 중지 (필수)

**요구사항:**

- ✅ 진행 상황 알림은 **반드시(MUST)** 완료 후 중지되어야 함

**구현:**

```typescript
class ProgressManager {
  private activeTokens = new Set<string>();
  
  async executeWithProgress<T>(
    progressToken: string,
    operation: (sendProgress: ProgressSender) => Promise<T>
  ): Promise<T> {
    // 토큰 등록
    this.activeTokens.add(progressToken);
    
    const sendProgress: ProgressSender = (progress, total, message) => {
      // 활성 토큰인지 확인
      if (!this.activeTokens.has(progressToken)) {
        console.warn('Attempting to send progress for completed operation');
        return;
      }
      
      this.transport.sendNotification({
        method: 'notifications/progress',
        params: { progressToken, progress, total, message }
      });
    };
    
    try {
      // 작업 실행
      const result = await operation(sendProgress);
      
      return result;
      
    } finally {
      // 완료 - 더 이상 진행 상황 알림 전송 안 함
      this.activeTokens.delete(progressToken);
    }
  }
}

// 사용 예시
await progressManager.executeWithProgress('token-123', async (sendProgress) => {
  sendProgress(0, 100, 'Starting...');
  
  for (let i = 1; i <= 100; i++) {
    await processItem(i);
    sendProgress(i, 100, `Processing item ${i}/100`);
  }
  
  return result;
});

// executeWithProgress가 반환되면 더 이상 진행 상황 알림 전송 안 됨
```

---

## 완전한 구현 예시

### 클라이언트 측

```typescript
class ProgressTrackingClient {
  private progressCallbacks = new Map<string, ProgressCallback>();
  
  constructor(private transport: Transport) {
    // 진행 상황 알림 수신 처리
    this.transport.on('notification', (notification) => {
      if (notification.method === 'notifications/progress') {
        this.handleProgressNotification(notification);
      }
    });
  }
  
  async sendRequestWithProgress(
    method: string,
    params: any,
    onProgress: ProgressCallback
  ): Promise<any> {
    // 고유 progress token 생성
    const progressToken = `progress-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    
    // 콜백 등록
    this.progressCallbacks.set(progressToken, onProgress);
    
    try {
      // 요청 전송
      const response = await this.transport.sendRequest({
        method,
        params: {
          ...params,
          _meta: {
            progressToken
          }
        }
      });
      
      return response;
      
    } finally {
      // 정리
      this.progressCallbacks.delete(progressToken);
    }
  }
  
  private handleProgressNotification(notification: any) {
    const { progressToken, progress, total, message } = notification.params;
    
    const callback = this.progressCallbacks.get(progressToken);
    if (callback) {
      callback({
        progress,
        total,
        message,
        percentage: total ? (progress / total) * 100 : undefined
      });
    }
  }
}

// 사용 예시
const client = new ProgressTrackingClient(transport);

await client.sendRequestWithProgress(
  'tools/call',
  { name: 'process_large_file', arguments: { file: 'data.csv' } },
  ({ progress, total, message, percentage }) => {
    console.log(`Progress: ${progress}/${total} (${percentage?.toFixed(1)}%) - ${message}`);
    
    // UI 업데이트
    updateProgressBar(percentage);
  }
);
```

---

### 서버 측

```typescript
class ProgressReportingServer {
  private activeProgress = new Map<string, {
    lastSent: number;
    lastProgress: number;
  }>();
  
  async handleRequest(request: any): Promise<any> {
    const progressToken = request.params?._meta?.progressToken;
    
    if (progressToken) {
      return this.handleWithProgress(progressToken, request);
    } else {
      return this.handleWithoutProgress(request);
    }
  }
  
  private async handleWithProgress(
    progressToken: string,
    request: any
  ): Promise<any> {
    // 진행 상황 추적 초기화
    this.activeProgress.set(progressToken, {
      lastSent: Date.now(),
      lastProgress: 0
    });
    
    const sendProgress = (progress: number, total?: number, message?: string) => {
      this.sendProgressNotification(progressToken, progress, total, message);
    };
    
    try {
      // 시작
      sendProgress(0, 100, 'Starting...');
      
      // 작업 실행
      const result = await this.processRequest(request, sendProgress);
      
      // 완료
      sendProgress(100, 100, 'Completed');
      
      return result;
      
    } finally {
      // 정리
      this.activeProgress.delete(progressToken);
    }
  }
  
  private sendProgressNotification(
    progressToken: string,
    progress: number,
    total?: number,
    message?: string
  ) {
    const info = this.activeProgress.get(progressToken);
    if (!info) return;
    
    // 속도 제한 (최소 100ms 간격, 0%와 100%는 제외)
    const now = Date.now();
    const timeSinceLastSend = now - info.lastSent;
    
    if (timeSinceLastSend < 100 && progress !== 0 && progress !== total) {
      return;
    }
    
    // progress 증가 확인
    if (progress < info.lastProgress) {
      console.error('Progress must increase');
      return;
    }
    
    info.lastSent = now;
    info.lastProgress = progress;
    
    // 알림 전송
    this.transport.sendNotification({
      method: 'notifications/progress',
      params: { progressToken, progress, total, message }
    });
  }
  
  private async processRequest(
    request: any,
    sendProgress: ProgressSender
  ): Promise<any> {
    // 예시: 100개 항목 처리
    const items = Array.from({ length: 100 }, (_, i) => i);
    
    for (let i = 0; i < items.length; i++) {
      await processItem(items[i]);
      
      // 진행 상황 보고 (10%마다)
      if ((i + 1) % 10 === 0) {
        sendProgress(
          i + 1,
          items.length,
          `Processed ${i + 1}/${items.length} items`
        );
      }
    }
    
    return { processed: items.length };
  }
  
  private async handleWithoutProgress(request: any): Promise<any> {
    // 진행 상황 없이 처리
    return this.processRequest(request, () => {});
  }
}
```

---

## 요약

### MCP Progress 메커니즘

**핵심 개념:**

- 장기 실행 작업의 진행 상황 추적
- 선택적 기능
- progressToken 기반
- 유연한 보고

**메시지 형식:**

```json
// 요청
{
  "params": {
    "_meta": {
      "progressToken": "abc123"
    }
  }
}

// 알림
{
  "method": "notifications/progress",
  "params": {
    "progressToken": "abc123",
    "progress": 50,
    "total": 100,
    "message": "Halfway done"
  }
}
```

**필수 규칙:**

- ✅ progressToken은 고유해야 함
- ✅ progress 값은 증가해야 함
- ✅ 활성 토큰만 참조
- ✅ 완료 후 알림 중지

**선택 사항:**

- 진행 상황 알림 전송 안 함 가능
- 적절한 빈도로 알림 전송
- total 알 수 없으면 생략 가능
- 부동 소수점 값 사용 가능

**권장 사항:**

- 활성 토큰 추적
- 속도 제한 구현
- 사람이 읽을 수 있는 메시지
- Task와 함께 사용 시 동일 토큰 유지

MCP Progress는 사용자에게 장기 실행 작업의 투명성과 피드백을 제공하는 필수 메커니즘입니다!

---

_이 문서는 Model Context Protocol 공식 Progress 사양에서 가져온 내용입니다._