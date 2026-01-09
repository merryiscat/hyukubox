# MCP Ping (핑)

## 프로토콜 개정판

**현재 버전**: 2025-11-25

---

## 개요 (Overview)

Model Context Protocol에는 양쪽 당사자가 상대방이 여전히 응답하고 연결이 활성 상태인지 확인할 수 있는 선택적 ping 메커니즘이 포함되어 있습니다.

**기능:**

- ✅ 연결 상태 확인
- ✅ 양방향 ping 지원 (클라이언트 ↔ 서버)
- ✅ 간단한 요청/응답 패턴
- ✅ 연결 건강 모니터링

**사용 목적:**

- 연결 활성 상태 확인
- 네트워크 연결 유효성 검증
- 타임아웃 탐지
- 연결 품질 모니터링

---

## 구현 방식

ping 기능은 간단한 요청/응답 패턴을 통해 구현됩니다.

**특징:**

- 클라이언트 또는 서버 모두 ping 시작 가능
- 매개변수 없는 간단한 요청
- 빈 객체 응답

---

## Message Format (메시지 형식)

### Ping 요청

ping 요청은 매개변수가 없는 표준 JSON-RPC 요청입니다:

```json
{
  "jsonrpc": "2.0",
  "id": "123",
  "method": "ping"
}
```

**필드 설명:**

|필드|타입|필수|설명|
|---|---|---|---|
|`jsonrpc`|string|✅|JSON-RPC 버전 ("2.0")|
|`id`|string/number|✅|요청 식별자|
|`method`|string|✅|"ping"|
|`params`|-|❌|없음 (매개변수 불필요)|

---

### Ping 응답

수신자는 빈 응답으로 **반드시(MUST)** 신속하게 응답해야 합니다:

```json
{
  "jsonrpc": "2.0",
  "id": "123",
  "result": {}
}
```

**필드 설명:**

|필드|타입|필수|설명|
|---|---|---|---|
|`jsonrpc`|string|✅|JSON-RPC 버전 ("2.0")|
|`id`|string/number|✅|원래 요청의 ID|
|`result`|object|✅|빈 객체 `{}`|

---

## Ping 흐름 다이어그램

### 정상적인 Ping

```
클라이언트                        서버
   │                               │
   │  1. Ping Request              │
   │     id: 123                   │
   │     method: "ping"            │
   ├──────────────────────────────►│
   │                               │
   │                               │  2. Process
   │                               │     (즉시)
   │                               │
   │  3. Ping Response             │
   │     id: 123                   │
   │     result: {}                │
   │◄────────────────────────────────┤
   │                               │
   │  4. Connection OK ✅          │
```

---

### 타임아웃된 Ping

```
클라이언트                        서버
   │                               │
   │  1. Ping Request              │
   │     id: 123                   │
   ├──────────────────────────────►│
   │                               │
   │                               X  (응답 없음)
   │                               
   │  2. Wait...                   
   │                               
   │  3. Timeout! ❌               
   │                               
   │  4. Consider connection       
   │     stale/dead                
   │                               
   │  5. (Optional) Reconnect      
```

---

## Behavior Requirements (동작 요구사항)

### 1. 신속한 응답 (필수)

**요구사항:**

- ✅ 수신자는 **반드시(MUST)** 빈 응답으로 신속하게 응답해야 함

**구현:**

```typescript
// 서버 측
server.on('ping', (request) => {
  // 즉시 응답
  return {};
});

// 클라이언트 측
client.on('ping', (request) => {
  // 즉시 응답
  return {};
});
```

---

### 2. 타임아웃 처리

**요구사항:** 합리적인 타임아웃 기간 내에 응답을 받지 못하면 발신자는 **가능(MAY)**:

**옵션 A: 연결을 부실한 것으로 간주**

```typescript
async function ping(timeout = 5000) {
  try {
    const response = await sendPing(timeout);
    return { alive: true };
  } catch (error) {
    if (error.name === 'TimeoutError') {
      console.warn('Connection appears stale');
      return { alive: false, reason: 'timeout' };
    }
    throw error;
  }
}
```

---

**옵션 B: 연결 종료**

```typescript
async function monitorConnection() {
  try {
    await sendPing({ timeout: 5000 });
  } catch (error) {
    if (error.name === 'TimeoutError') {
      console.error('Ping timeout - terminating connection');
      connection.terminate();
    }
  }
}
```

---

**옵션 C: 재연결 절차 시도**

```typescript
async function maintainConnection() {
  try {
    await sendPing({ timeout: 5000 });
  } catch (error) {
    if (error.name === 'TimeoutError') {
      console.log('Ping timeout - attempting reconnection');
      await reconnect();
    }
  }
}
```

---

## Usage Patterns (사용 패턴)

### 패턴 1: 주기적인 연결 확인

```typescript
class MCPConnection {
  private pingInterval: NodeJS.Timeout | null = null;
  private readonly PING_INTERVAL = 30000; // 30초
  
  startHealthCheck() {
    this.pingInterval = setInterval(async () => {
      try {
        await this.ping();
        console.log('Connection healthy');
      } catch (error) {
        console.error('Ping failed:', error);
        this.handleConnectionFailure();
      }
    }, this.PING_INTERVAL);
  }
  
  stopHealthCheck() {
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
      this.pingInterval = null;
    }
  }
  
  async ping(timeout = 5000): Promise<void> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);
    
    try {
      await this.sendRequest({
        method: 'ping'
      }, { signal: controller.signal });
    } finally {
      clearTimeout(timeoutId);
    }
  }
  
  private handleConnectionFailure() {
    this.stopHealthCheck();
    this.reconnect();
  }
}
```

---

### 패턴 2: 유휴 시간 후 확인

```typescript
class IdleConnectionMonitor {
  private lastActivity: number = Date.now();
  private readonly IDLE_THRESHOLD = 60000; // 1분
  private checkTimer: NodeJS.Timeout | null = null;
  
  constructor(private connection: MCPConnection) {
    this.startMonitoring();
  }
  
  recordActivity() {
    this.lastActivity = Date.now();
  }
  
  private startMonitoring() {
    this.checkTimer = setInterval(async () => {
      const idleTime = Date.now() - this.lastActivity;
      
      if (idleTime > this.IDLE_THRESHOLD) {
        console.log('Connection idle, sending ping...');
        
        try {
          await this.connection.ping();
          this.recordActivity(); // 성공적인 ping도 활동으로 간주
        } catch (error) {
          console.error('Idle ping failed:', error);
        }
      }
    }, this.IDLE_THRESHOLD / 2); // IDLE_THRESHOLD의 절반마다 확인
  }
  
  stop() {
    if (this.checkTimer) {
      clearInterval(this.checkTimer);
      this.checkTimer = null;
    }
  }
}
```

---

### 패턴 3: 적응형 Ping

```typescript
class AdaptivePinger {
  private failureCount = 0;
  private baseInterval = 30000; // 30초
  private currentInterval = this.baseInterval;
  private pingTimer: NodeJS.Timeout | null = null;
  
  start() {
    this.schedulePing();
  }
  
  private schedulePing() {
    this.pingTimer = setTimeout(async () => {
      try {
        await this.sendPing();
        
        // 성공 - 간격을 기본값으로 재설정
        this.failureCount = 0;
        this.currentInterval = this.baseInterval;
        console.log('Ping successful');
        
      } catch (error) {
        // 실패 - 간격 단축
        this.failureCount++;
        this.currentInterval = Math.max(
          5000, // 최소 5초
          this.baseInterval / (this.failureCount + 1)
        );
        
        console.warn(`Ping failed (${this.failureCount}), reducing interval to ${this.currentInterval}ms`);
        
        if (this.failureCount >= 3) {
          console.error('Multiple ping failures - connection may be lost');
          this.handleConnectionLoss();
          return;
        }
      }
      
      // 다음 ping 예약
      this.schedulePing();
      
    }, this.currentInterval);
  }
  
  stop() {
    if (this.pingTimer) {
      clearTimeout(this.pingTimer);
      this.pingTimer = null;
    }
  }
  
  private async sendPing() {
    // ping 구현
  }
  
  private handleConnectionLoss() {
    this.stop();
    // 재연결 로직
  }
}
```

---

### 패턴 4: 요청 전 연결 확인

```typescript
class SafeMCPClient {
  private lastPingTime = 0;
  private readonly PING_CACHE_DURATION = 10000; // 10초
  
  async sendRequest(request: any) {
    // 최근에 ping했는지 확인
    const timeSinceLastPing = Date.now() - this.lastPingTime;
    
    if (timeSinceLastPing > this.PING_CACHE_DURATION) {
      console.log('Verifying connection before request...');
      
      try {
        await this.ping();
        this.lastPingTime = Date.now();
      } catch (error) {
        throw new Error('Connection verification failed - cannot send request');
      }
    }
    
    // 연결이 활성 상태 - 요청 전송
    return this.transport.send(request);
  }
  
  async ping(timeout = 5000): Promise<void> {
    // ping 구현
  }
}
```

---

## Implementation Considerations (구현 고려사항)

### 1. 주기적인 Ping (권장)

**권장사항:**

- ✅ 구현은 **권장(SHOULD)** 연결 상태를 감지하기 위해 주기적으로 ping을 발행해야 함

**예시:**

```typescript
const PING_INTERVAL = 30000; // 30초

setInterval(async () => {
  try {
    await connection.ping();
  } catch (error) {
    console.error('Ping failed:', error);
  }
}, PING_INTERVAL);
```

---

### 2. 구성 가능한 빈도 (권장)

**권장사항:**

- ✅ ping의 빈도는 **권장(SHOULD)** 구성 가능해야 함

**구현:**

```typescript
interface PingConfig {
  enabled: boolean;
  interval: number;      // 밀리초
  timeout: number;       // 밀리초
  maxFailures: number;   // 재연결 전 최대 실패 횟수
}

const defaultConfig: PingConfig = {
  enabled: true,
  interval: 30000,       // 30초
  timeout: 5000,         // 5초
  maxFailures: 3
};

class ConfigurablePinger {
  constructor(
    private connection: MCPConnection,
    private config: PingConfig = defaultConfig
  ) {
    if (this.config.enabled) {
      this.start();
    }
  }
  
  updateConfig(newConfig: Partial<PingConfig>) {
    this.config = { ...this.config, ...newConfig };
    
    // 활성화 상태 변경 시
    if (this.config.enabled) {
      this.start();
    } else {
      this.stop();
    }
  }
  
  // start, stop 메서드...
}
```

---

### 3. 적절한 타임아웃 (권장)

**권장사항:**

- ✅ 타임아웃은 **권장(SHOULD)** 네트워크 환경에 적합해야 함

**네트워크 환경별 권장 타임아웃:**

|환경|권장 타임아웃|이유|
|---|---|---|
|로컬 (localhost)|1-2초|매우 낮은 지연 시간|
|LAN|3-5초|낮은 지연 시간|
|WAN/인터넷|5-10초|중간 지연 시간|
|모바일/불안정|10-15초|높은 지연 시간, 패킷 손실|
|위성/원격|15-30초|매우 높은 지연 시간|

**적응형 타임아웃:**

```typescript
class AdaptiveTimeoutPinger {
  private baseTimeout = 5000;
  private currentTimeout = this.baseTimeout;
  private recentLatencies: number[] = [];
  
  async ping(): Promise<void> {
    const startTime = Date.now();
    
    try {
      await this.sendPing(this.currentTimeout);
      
      const latency = Date.now() - startTime;
      this.recordLatency(latency);
      this.adjustTimeout();
      
    } catch (error) {
      // 타임아웃 증가
      this.currentTimeout = Math.min(
        this.currentTimeout * 1.5,
        30000 // 최대 30초
      );
      throw error;
    }
  }
  
  private recordLatency(latency: number) {
    this.recentLatencies.push(latency);
    
    // 최근 10개만 유지
    if (this.recentLatencies.length > 10) {
      this.recentLatencies.shift();
    }
  }
  
  private adjustTimeout() {
    // 평균 지연 시간 계산
    const avgLatency = this.recentLatencies.reduce((a, b) => a + b, 0) 
                      / this.recentLatencies.length;
    
    // 타임아웃 = 평균 지연 시간 * 3 + 버퍼
    this.currentTimeout = Math.max(
      this.baseTimeout,
      avgLatency * 3 + 1000
    );
    
    console.log(`Adjusted timeout to ${this.currentTimeout}ms (avg latency: ${avgLatency.toFixed(0)}ms)`);
  }
  
  private async sendPing(timeout: number): Promise<void> {
    // ping 구현
  }
}
```

---

### 4. 과도한 Ping 방지 (권장)

**권장사항:**

- ✅ 과도한 ping은 **권장(SHOULD)** 네트워크 오버헤드를 줄이기 위해 피해야 함

**제한 구현:**

```typescript
class ThrottledPinger {
  private readonly MIN_INTERVAL = 5000; // 최소 5초
  private lastPingTime = 0;
  
  async ping(): Promise<void> {
    const now = Date.now();
    const timeSinceLastPing = now - this.lastPingTime;
    
    if (timeSinceLastPing < this.MIN_INTERVAL) {
      console.warn(`Ping throttled - ${this.MIN_INTERVAL - timeSinceLastPing}ms remaining`);
      throw new Error('Ping rate limit exceeded');
    }
    
    this.lastPingTime = now;
    
    // ping 전송
    await this.sendPing();
  }
  
  private async sendPing(): Promise<void> {
    // ping 구현
  }
}
```

---

## Error Handling (오류 처리)

### 1. 타임아웃 처리 (권장)

**권장사항:**

- ✅ 타임아웃은 **권장(SHOULD)** 연결 실패로 처리되어야 함

**구현:**

```typescript
async function handlePing() {
  try {
    await connection.ping({ timeout: 5000 });
    console.log('Ping successful');
    
  } catch (error) {
    if (error.name === 'TimeoutError') {
      console.error('Ping timeout - connection failed');
      
      // 연결 실패로 처리
      await handleConnectionFailure();
      
    } else {
      console.error('Ping error:', error);
      throw error;
    }
  }
}
```

---

### 2. 여러 번 실패한 Ping (권장)

**권장사항:**

- ✅ 여러 번 실패한 ping은 **가능(MAY)** 연결 재설정을 트리거할 수 있음

**구현:**

```typescript
class FailureTracker {
  private failureCount = 0;
  private readonly MAX_FAILURES = 3;
  
  async ping() {
    try {
      await this.sendPing();
      
      // 성공 - 실패 카운트 재설정
      this.failureCount = 0;
      console.log('Ping successful');
      
    } catch (error) {
      this.failureCount++;
      
      console.error(`Ping failed (${this.failureCount}/${this.MAX_FAILURES})`);
      
      if (this.failureCount >= this.MAX_FAILURES) {
        console.error('Maximum ping failures reached - resetting connection');
        await this.resetConnection();
      }
    }
  }
  
  private async sendPing(): Promise<void> {
    // ping 구현
  }
  
  private async resetConnection(): Promise<void> {
    this.failureCount = 0;
    
    // 기존 연결 종료
    await this.connection.close();
    
    // 재연결
    await this.connection.reconnect();
  }
}
```

---

### 3. 진단을 위한 로깅 (권장)

**권장사항:**

- ✅ 구현은 **권장(SHOULD)** 진단을 위해 ping 실패를 로깅해야 함

**구현:**

```typescript
interface PingLogEntry {
  timestamp: string;
  success: boolean;
  latency?: number;
  error?: string;
  consecutiveFailures: number;
}

class PingLogger {
  private logs: PingLogEntry[] = [];
  private consecutiveFailures = 0;
  
  async ping() {
    const startTime = Date.now();
    const timestamp = new Date().toISOString();
    
    try {
      await this.sendPing();
      
      const latency = Date.now() - startTime;
      
      // 성공 로그
      this.log({
        timestamp,
        success: true,
        latency,
        consecutiveFailures: 0
      });
      
      this.consecutiveFailures = 0;
      
    } catch (error) {
      this.consecutiveFailures++;
      
      // 실패 로그
      this.log({
        timestamp,
        success: false,
        error: error.message,
        consecutiveFailures: this.consecutiveFailures
      });
      
      throw error;
    }
  }
  
  private log(entry: PingLogEntry) {
    this.logs.push(entry);
    
    // 최근 100개만 유지
    if (this.logs.length > 100) {
      this.logs.shift();
    }
    
    // 콘솔 출력
    if (entry.success) {
      console.log(`[PING] Success - ${entry.latency}ms`);
    } else {
      console.error(`[PING] Failed (${entry.consecutiveFailures} consecutive) - ${entry.error}`);
    }
  }
  
  getStats() {
    const total = this.logs.length;
    const successful = this.logs.filter(l => l.success).length;
    const failed = total - successful;
    
    const successRate = total > 0 ? (successful / total) * 100 : 0;
    
    const latencies = this.logs
      .filter(l => l.success && l.latency)
      .map(l => l.latency!);
    
    const avgLatency = latencies.length > 0
      ? latencies.reduce((a, b) => a + b, 0) / latencies.length
      : 0;
    
    return {
      total,
      successful,
      failed,
      successRate: successRate.toFixed(2) + '%',
      avgLatency: avgLatency.toFixed(2) + 'ms',
      consecutiveFailures: this.consecutiveFailures
    };
  }
  
  private async sendPing(): Promise<void> {
    // ping 구현
  }
}
```

---

## 완전한 구현 예시

```typescript
import EventEmitter from 'events';

interface PingOptions {
  timeout?: number;
  interval?: number;
  maxFailures?: number;
  enabled?: boolean;
}

class MCPPingManager extends EventEmitter {
  private pingTimer: NodeJS.Timeout | null = null;
  private failureCount = 0;
  private lastPingTime = 0;
  private isRunning = false;
  
  private readonly config: Required<PingOptions>;
  
  constructor(
    private connection: MCPConnection,
    options: PingOptions = {}
  ) {
    super();
    
    this.config = {
      timeout: options.timeout ?? 5000,
      interval: options.interval ?? 30000,
      maxFailures: options.maxFailures ?? 3,
      enabled: options.enabled ?? true
    };
    
    if (this.config.enabled) {
      this.start();
    }
  }
  
  start() {
    if (this.isRunning) {
      return;
    }
    
    this.isRunning = true;
    this.schedulePing();
    this.emit('started');
  }
  
  stop() {
    if (!this.isRunning) {
      return;
    }
    
    this.isRunning = false;
    
    if (this.pingTimer) {
      clearTimeout(this.pingTimer);
      this.pingTimer = null;
    }
    
    this.emit('stopped');
  }
  
  private schedulePing() {
    if (!this.isRunning) {
      return;
    }
    
    this.pingTimer = setTimeout(async () => {
      await this.performPing();
      this.schedulePing(); // 다음 ping 예약
    }, this.config.interval);
  }
  
  private async performPing() {
    const startTime = Date.now();
    
    try {
      await this.connection.ping(this.config.timeout);
      
      const latency = Date.now() - startTime;
      this.lastPingTime = Date.now();
      this.failureCount = 0;
      
      this.emit('success', { latency });
      
    } catch (error) {
      this.failureCount++;
      
      this.emit('failure', {
        error,
        consecutiveFailures: this.failureCount
      });
      
      if (this.failureCount >= this.config.maxFailures) {
        this.emit('connectionLost', {
          consecutiveFailures: this.failureCount
        });
        
        this.stop();
        await this.handleConnectionLost();
      }
    }
  }
  
  private async handleConnectionLost() {
    try {
      await this.connection.reconnect();
      this.failureCount = 0;
      this.start(); // 재시작
    } catch (error) {
      this.emit('reconnectFailed', { error });
    }
  }
  
  getStatus() {
    return {
      isRunning: this.isRunning,
      failureCount: this.failureCount,
      lastPingTime: this.lastPingTime,
      config: this.config
    };
  }
}

// 사용 예시
const pingManager = new MCPPingManager(connection, {
  timeout: 5000,
  interval: 30000,
  maxFailures: 3
});

pingManager.on('success', ({ latency }) => {
  console.log(`Ping successful - ${latency}ms`);
});

pingManager.on('failure', ({ error, consecutiveFailures }) => {
  console.error(`Ping failed (${consecutiveFailures}):`, error);
});

pingManager.on('connectionLost', () => {
  console.error('Connection lost - attempting to reconnect...');
});

pingManager.on('reconnectFailed', ({ error }) => {
  console.error('Reconnection failed:', error);
});
```

---

## 요약

### MCP Ping 메커니즘

**핵심 개념:**

- 연결 상태 확인
- 간단한 요청/응답
- 양방향 지원
- 선택적 기능

**메시지 형식:**

```json
// 요청
{ "jsonrpc": "2.0", "id": "123", "method": "ping" }

// 응답
{ "jsonrpc": "2.0", "id": "123", "result": {} }
```

**동작 요구사항:**

- ✅ 신속한 응답 필수
- ✅ 타임아웃 시 연결 실패 처리
- ✅ 재연결 옵션

**권장 사항:**

- 주기적인 ping 발행
- 구성 가능한 빈도
- 네트워크 환경에 적합한 타임아웃
- 과도한 ping 방지
- 실패 로깅

**구현 패턴:**

- 주기적인 연결 확인
- 유휴 시간 후 확인
- 적응형 ping
- 요청 전 연결 확인

MCP Ping은 연결 상태를 모니터링하고 안정적인 통신을 보장하는 핵심 메커니즘입니다!

---

_이 문서는 Model Context Protocol 공식 Ping 사양에서 가져온 내용입니다._