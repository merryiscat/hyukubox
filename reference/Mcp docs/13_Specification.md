# MCP 사양 (Specification)

## 버전 정보

**현재 버전**: 2025-11-25 (최신)

---

## 개요

[Model Context Protocol](https://modelcontextprotocol.io/) (MCP)은 LLM 애플리케이션과 외부 데이터 소스 및 도구 간의 원활한 통합을 가능하게 하는 오픈 프로토콜입니다. AI 기반 IDE를 구축하든, 채팅 인터페이스를 개선하든, 사용자 정의 AI 워크플로우를 만들든, MCP는 LLM을 필요한 컨텍스트와 연결하는 표준화된 방법을 제공합니다.

**이 사양의 목적:**

- 권위 있는 프로토콜 요구사항 정의
- [schema.ts](https://github.com/modelcontextprotocol/specification/blob/main/schema/2025-11-25/schema.ts)의 TypeScript 스키마 기반

**추가 자료:**

- 구현 가이드 및 예제: [modelcontextprotocol.io](https://modelcontextprotocol.io/)

---

## RFC 키워드 정의

이 문서의 키워드는 [BCP 14](https://datatracker.ietf.org/doc/html/bcp14) [[RFC2119](https://datatracker.ietf.org/doc/html/rfc2119)] [[RFC8174](https://datatracker.ietf.org/doc/html/rfc8174)]에 설명된 대로 해석되며, 대문자로 표시된 경우에만 적용됩니다:

- **MUST** (반드시): 절대적인 요구사항
- **MUST NOT** (절대 금지): 절대적인 금지사항
- **REQUIRED** (필수): 필수 요구사항
- **SHALL** (해야 함): 강제 요구사항
- **SHALL NOT** (해서는 안 됨): 강제 금지사항
- **SHOULD** (권장): 권장사항
- **SHOULD NOT** (비권장): 비권장사항
- **RECOMMENDED** (추천): 추천사항
- **NOT RECOMMENDED** (비추천): 비추천사항
- **MAY** (가능): 선택사항
- **OPTIONAL** (옵션): 선택적 기능

---

## MCP가 제공하는 것

MCP는 애플리케이션이 다음을 수행할 수 있는 표준화된 방법을 제공합니다:

### 1. 컨텍스트 정보 공유

**목적:**

- 언어 모델과 컨텍스트 정보 공유
- 관련 데이터 제공
- 작업 수행에 필요한 배경 정보 전달

**사용 사례:**

- 문서 및 파일 내용
- 데이터베이스 쿼리 결과
- API 응답 데이터
- 사용자별 컨텍스트

---

### 2. 도구 및 기능 노출

**목적:**

- AI 시스템에 도구 및 기능 노출
- 실행 가능한 작업 제공
- 외부 시스템과의 상호작용 지원

**사용 사례:**

- 파일 시스템 작업
- API 호출
- 데이터베이스 쿼리
- 외부 서비스 통합

---

### 3. 구성 가능한 통합 및 워크플로우 구축

**목적:**

- 모듈식 통합 구축
- 재사용 가능한 구성 요소
- 확장 가능한 아키텍처

**이점:**

- 컴포저블 디자인
- 유연한 워크플로우
- 쉬운 확장성

---

## 프로토콜 기반

### JSON-RPC 2.0

**프로토콜:**

- [JSON-RPC](https://www.jsonrpc.org/) 2.0 메시지 형식 사용
- 요청-응답 패턴
- 구조화된 통신

**메시지 구성 요소 간 통신:**

```
┌─────────┐         ┌─────────┐         ┌─────────┐
│  Host   │◄───────►│ Client  │◄───────►│ Server  │
└─────────┘         └─────────┘         └─────────┘
```

---

## 핵심 구성 요소

### 1. Hosts (호스트)

**정의:**

- 연결을 시작하는 LLM 애플리케이션

**역할:**

- 클라이언트 관리
- 사용자 인터페이스 제공
- LLM과 상호작용

**예시:**

- Claude Desktop
- IDE (VS Code, IntelliJ)
- 챗봇 애플리케이션

---

### 2. Clients (클라이언트)

**정의:**

- 호스트 애플리케이션 내의 커넥터

**역할:**

- 서버와 통신
- 프로토콜 메시지 처리
- 데이터 변환 및 전달

**특징:**

- 호스트 내부에 포함됨
- 여러 서버와 연결 가능
- 기능 협상 수행

---

### 3. Servers (서버)

**정의:**

- 컨텍스트와 기능을 제공하는 서비스

**역할:**

- 리소스 노출
- 도구 제공
- 프롬프트 관리

**예시:**

- 파일 시스템 서버
- 데이터베이스 서버
- API 통합 서버

---

## LSP와의 관계

**영감:** MCP는 [Language Server Protocol](https://microsoft.github.io/language-server-protocol/) (LSP)에서 영감을 받았습니다.

### LSP와의 유사점

**LSP:**

- 프로그래밍 언어 지원 표준화
- 개발 도구 생태계 전반에 걸쳐 통합
- 단일 언어 서버 → 여러 IDE

**MCP:**

- 컨텍스트 및 도구 통합 표준화
- AI 애플리케이션 생태계 전반에 걸쳐 통합
- 단일 MCP 서버 → 여러 AI 앱

### 차이점

|측면|LSP|MCP|
|---|---|---|
|목적|언어 지원|컨텍스트 및 도구|
|대상|개발 도구|AI 애플리케이션|
|주요 기능|자동완성, 진단, 정의 이동|리소스, 프롬프트, 도구|
|사용 사례|코드 편집|AI 워크플로우|

---

## 주요 세부 사항

### 기본 프로토콜 (Base Protocol)

#### 1. JSON-RPC 메시지 형식

**구조:**

```json
{
  "jsonrpc": "2.0",
  "method": "method_name",
  "params": { ... },
  "id": 1
}
```

**특징:**

- 요청-응답 패턴
- 알림 지원
- 배치 요청 가능

---

#### 2. 상태 유지 연결 (Stateful Connections)

**특성:**

- 연결이 세션 동안 유지됨
- 상태 정보 보존
- 효율적인 통신

**이점:**

- 재연결 오버헤드 감소
- 컨텍스트 유지
- 성능 향상

---

#### 3. 기능 협상 (Capability Negotiation)

**프로세스:**

1. 클라이언트가 지원 기능 전송
2. 서버가 지원 기능 응답
3. 공통 기능 집합 결정

**협상 항목:**

- 지원되는 기능
- 프로토콜 버전
- 전송 방식

---

## 기능 (Features)

### 서버가 제공하는 기능

서버는 클라이언트에 다음 기능 중 하나 이상을 제공합니다:

#### 1. Resources (리소스)

**정의:**

- 사용자 또는 AI 모델이 사용할 컨텍스트 및 데이터

**특징:**

- 읽기 가능한 데이터
- 구조화된 정보
- 메타데이터 포함

**예시:**

```json
{
  "uri": "file:///path/to/document.txt",
  "name": "Project Documentation",
  "mimeType": "text/plain",
  "description": "Main project documentation"
}
```

**사용 사례:**

- 파일 내용
- API 응답
- 데이터베이스 레코드
- 구성 정보

---

#### 2. Prompts (프롬프트)

**정의:**

- 사용자를 위한 템플릿화된 메시지 및 워크플로우

**특징:**

- 재사용 가능한 템플릿
- 매개변수화된 메시지
- 워크플로우 정의

**예시:**

```json
{
  "name": "code_review",
  "description": "Review code for quality",
  "arguments": [
    {
      "name": "file_path",
      "description": "Path to file",
      "required": true
    }
  ]
}
```

**사용 사례:**

- 코드 리뷰 템플릿
- 문서 생성 워크플로우
- 표준 질문 세트

---

#### 3. Tools (도구)

**정의:**

- AI 모델이 실행할 함수

**특징:**

- 실행 가능한 작업
- 입력/출력 스키마
- 부작용 가능

**예시:**

```json
{
  "name": "search_files",
  "description": "Search for files by pattern",
  "inputSchema": {
    "type": "object",
    "properties": {
      "pattern": {
        "type": "string",
        "description": "Search pattern"
      }
    },
    "required": ["pattern"]
  }
}
```

**사용 사례:**

- 파일 시스템 작업
- API 호출
- 계산 수행
- 데이터 변환

---

### 클라이언트가 제공하는 기능

클라이언트는 서버에 다음 기능을 제공할 수 있습니다:

#### 1. Sampling (샘플링)

**정의:**

- 서버가 시작하는 에이전틱 동작 및 재귀적 LLM 상호작용

**특징:**

- 서버가 LLM 완성 요청
- 모델 응답 생성
- 컨텍스트 내 추론

**사용 사례:**

- 복잡한 작업 분해
- 멀티 스텝 추론
- 자율적 의사 결정

---

#### 2. Roots (루트)

**정의:**

- URI 또는 파일시스템 경계에 대한 서버 시작 문의

**특징:**

- 작업 경계 정의
- 파일 시스템 범위
- 권한 관리

**사용 사례:**

- 프로젝트 루트 정의
- 작업 디렉토리 설정
- 접근 범위 제한

---

#### 3. Elicitation (유도)

**정의:**

- 사용자로부터 추가 정보를 요청하는 서버 시작 요청

**특징:**

- 동적 정보 수집
- 사용자 입력 요청
- 대화형 워크플로우

**사용 사례:**

- 누락된 매개변수 요청
- 확인 요청
- 추가 컨텍스트 수집

---

## 추가 유틸리티

MCP는 다양한 유틸리티 기능을 제공합니다:

### 1. Configuration (구성)

**기능:**

- 서버 설정 관리
- 클라이언트 구성
- 환경 변수

**예시:**

```json
{
  "config": {
    "api_key": "...",
    "base_url": "https://api.example.com",
    "timeout": 30
  }
}
```

---

### 2. Progress Tracking (진행 상황 추적)

**기능:**

- 장기 실행 작업 모니터링
- 진행률 업데이트
- 상태 보고

**예시:**

```json
{
  "progress": {
    "total": 100,
    "completed": 45,
    "message": "Processing files..."
  }
}
```

---

### 3. Cancellation (취소)

**기능:**

- 실행 중인 작업 취소
- 리소스 정리
- 우아한 종료

**사용 사례:**

- 사용자가 작업 중단
- 타임아웃 처리
- 오류 복구

---

### 4. Error Reporting (오류 보고)

**기능:**

- 구조화된 오류 메시지
- 오류 코드
- 세부 정보 제공

**예시:**

```json
{
  "error": {
    "code": -32602,
    "message": "Invalid params",
    "data": {
      "field": "file_path",
      "reason": "File not found"
    }
  }
}
```

---

### 5. Logging (로깅)

**기능:**

- 진단 메시지
- 디버그 정보
- 성능 메트릭

**로그 레벨:**

- ERROR
- WARN
- INFO
- DEBUG

---

## 보안 및 신뢰와 안전

Model Context Protocol은 임의의 데이터 접근 및 코드 실행 경로를 통해 강력한 기능을 제공합니다. 이러한 능력에는 모든 구현자가 신중하게 다뤄야 할 중요한 보안 및 신뢰 고려사항이 따릅니다.

---

### 핵심 원칙

#### 1. 사용자 동의 및 제어 (User Consent and Control)

**요구사항:**

✅ **명시적 동의**

- 사용자는 모든 데이터 접근 및 작업에 대해 명시적으로 동의해야 함
- 무엇이 공유되고 실행되는지 이해해야 함

✅ **사용자 제어**

- 사용자가 데이터 공유 대상 제어
- 수행되는 작업에 대한 통제권 유지

✅ **명확한 UI**

- 구현자는 활동을 검토하고 승인하기 위한 명확한 UI를 제공해야 함
- 투명한 권한 관리

**예시:**

```
┌─────────────────────────────────────┐
│ 권한 요청                            │
├─────────────────────────────────────┤
│ 서버가 다음을 요청합니다:             │
│ ✓ /project/src 디렉토리 읽기         │
│ ✓ 파일 검색 도구 실행                │
│                                      │
│ [승인]  [거부]  [자세히 보기]        │
└─────────────────────────────────────┘
```

---

#### 2. 데이터 프라이버시 (Data Privacy)

**요구사항:**

✅ **명시적 사용자 동의**

- 호스트는 서버에 사용자 데이터를 노출하기 전에 명시적 동의를 얻어야 함

✅ **데이터 전송 제한**

- 호스트는 사용자 동의 없이 리소스 데이터를 다른 곳으로 전송해서는 안 됨

✅ **접근 제어**

- 사용자 데이터는 적절한 접근 제어로 보호되어야 함

**보호 대상:**

- 개인 정보
- 민감한 문서
- 인증 정보
- 비즈니스 데이터

**구현 예시:**

```typescript
async function shareResource(resource: Resource) {
  const consent = await getUserConsent({
    action: "share_resource",
    resource: resource.uri,
    destination: server.name
  });
  
  if (!consent.approved) {
    throw new Error("User denied consent");
  }
  
  return sendToServer(resource);
}
```

---

#### 3. 도구 안전 (Tool Safety)

**경고:** 도구는 임의의 코드 실행을 나타내므로 적절한 주의를 기울여야 합니다.

**중요 고려사항:**

⚠️ **신뢰할 수 없는 설명**

- 주석과 같은 도구 동작 설명은 신뢰할 수 없는 것으로 간주해야 함
- 신뢰할 수 있는 서버에서 얻은 경우는 예외

✅ **명시적 동의 필요**

- 호스트는 도구를 호출하기 전에 명시적 사용자 동의를 얻어야 함

✅ **도구 이해**

- 사용자는 승인하기 전에 각 도구가 무엇을 하는지 이해해야 함

**안전 체크리스트:**

- [ ] 도구가 수행하는 작업 확인
- [ ] 필요한 권한 검토
- [ ] 잠재적 부작용 평가
- [ ] 신뢰할 수 있는 출처 확인

**UI 예시:**

```
┌─────────────────────────────────────┐
│ 도구 실행 승인                       │
├─────────────────────────────────────┤
│ 도구: delete_file                    │
│ 설명: 파일 삭제                      │
│                                      │
│ 매개변수:                            │
│ - path: /important/data.txt          │
│                                      │
│ ⚠️ 이 작업은 되돌릴 수 없습니다      │
│                                      │
│ [실행]  [취소]                       │
└─────────────────────────────────────┘
```

---

#### 4. LLM 샘플링 제어 (LLM Sampling Controls)

**요구사항:**

✅ **명시적 승인**

- 사용자는 모든 LLM 샘플링 요청을 명시적으로 승인해야 함

✅ **사용자 제어 항목**

**제어 범위:**

1. **샘플링 발생 여부**
    
    - 샘플링을 허용할지 결정
2. **실제 프롬프트**
    
    - 전송될 실제 프롬프트 내용 제어
3. **결과 가시성**
    
    - 서버가 볼 수 있는 결과 범위

**프로토콜 설계:**

- 의도적으로 서버의 프롬프트 가시성 제한
- 사용자 프라이버시 보호

**구현 예시:**

```typescript
async function handleSamplingRequest(request: SamplingRequest) {
  const approval = await getUserApproval({
    prompt: request.prompt,
    server: request.serverId,
    maxTokens: request.maxTokens
  });
  
  if (!approval.granted) {
    return { error: "User denied sampling request" };
  }
  
  const result = await llm.complete(approval.modifiedPrompt);
  
  return {
    completion: result.text,
    // 서버에 제한된 정보만 반환
    tokensUsed: result.tokens
  };
}
```

---

### 구현 가이드라인

프로토콜 자체는 프로토콜 수준에서 이러한 보안 원칙을 강제할 수 없지만, 구현자는 **반드시(SHOULD)** 다음을 수행해야 합니다:

#### 1. 강력한 동의 및 권한 흐름 구축

**구현 항목:**

- 명확한 권한 요청 UI
- 세분화된 권한 제어
- 권한 취소 메커니즘

**예시:**

```typescript
class ConsentManager {
  async requestConsent(action: Action): Promise<ConsentResult> {
    return await showConsentDialog({
      action: action.type,
      details: action.details,
      risks: action.risks,
      benefits: action.benefits
    });
  }
  
  async revokeConsent(actionType: string) {
    // 권한 취소 처리
  }
}
```

---

#### 2. 보안 영향에 대한 명확한 문서 제공

**문서화 항목:**

- 데이터 접근 범위
- 실행 가능한 작업
- 보안 위험
- 완화 방법

**예시 문서:**

```markdown
## 보안 고려사항

### 데이터 접근
이 서버는 다음에 접근합니다:
- 프로젝트 디렉토리 내 모든 파일
- Git 저장소 메타데이터

### 실행 가능한 작업
- 파일 읽기/쓰기
- Git 명령 실행

### 권장 사항
- 민감한 파일이 포함된 디렉토리에서 사용하지 마세요
- 프로덕션 저장소에 사용 전 테스트하세요
```

---

#### 3. 적절한 접근 제어 및 데이터 보호 구현

**보안 메커니즘:**

- 역할 기반 접근 제어 (RBAC)
- 데이터 암호화
- 감사 로깅
- 세션 관리

**구현 예시:**

```typescript
class AccessControl {
  private permissions: Map<string, Set<string>>;
  
  canAccess(user: User, resource: Resource): boolean {
    const userPerms = this.permissions.get(user.id);
    return userPerms?.has(resource.uri) ?? false;
  }
  
  grantAccess(user: User, resource: Resource) {
    // 접근 권한 부여 및 로깅
    this.auditLog.record({
      action: "grant_access",
      user: user.id,
      resource: resource.uri,
      timestamp: Date.now()
    });
  }
}
```

---

#### 4. 통합에서 보안 모범 사례 따르기

**모범 사례:**

- 최소 권한 원칙
- 입력 검증
- 출력 인코딩
- 안전한 기본값

**체크리스트:**

- [ ] 모든 입력 검증
- [ ] SQL 인젝션 방지
- [ ] XSS 공격 방지
- [ ] CSRF 토큰 사용
- [ ] HTTPS 강제

---

#### 5. 기능 설계에서 프라이버시 영향 고려

**프라이버시 원칙:**

- 데이터 최소화
- 목적 제한
- 저장 제한
- 투명성

**설계 질문:**

- 이 데이터가 정말 필요한가?
- 얼마나 오래 보관해야 하는가?
- 누가 접근할 수 있는가?
- 사용자가 통제할 수 있는가?

---

## 학습 자료

각 프로토콜 구성 요소에 대한 자세한 사양을 탐색하세요:

### 1. Architecture (아키텍처)

**내용:**

- 전체 시스템 구조
- 구성 요소 간 상호작용
- 데이터 흐름

**링크:** [Architecture](https://claude.ai/specification/2025-11-25/architecture)

---

### 2. Base Protocol (기본 프로토콜)

**내용:**

- JSON-RPC 메시지 형식
- 연결 수명 주기
- 전송 메커니즘
- 인증 및 권한 부여

**링크:** [Base Protocol](https://claude.ai/specification/2025-11-25/basic)

---

### 3. Server Features (서버 기능)

**내용:**

- Resources (리소스)
- Prompts (프롬프트)
- Tools (도구)
- 구현 가이드

**링크:** [Server Features](https://claude.ai/specification/2025-11-25/server)

---

### 4. Client Features (클라이언트 기능)

**내용:**

- Sampling (샘플링)
- Roots (루트)
- Elicitation (유도)
- 구현 가이드

**링크:** [Client Features](https://claude.ai/specification/2025-11-25/client)

---

### 5. Contributing (기여하기)

**내용:**

- 기여 방법
- 개발 가이드라인
- 코드 리뷰 프로세스

**링크:** [Contributing](https://claude.ai/development/contributing)

---

## 요약

Model Context Protocol은 LLM 애플리케이션과 외부 리소스 간의 표준화된 통합을 제공합니다.

### 핵심 특징

**프로토콜 기반:**

- ✅ JSON-RPC 2.0 메시지
- ✅ 상태 유지 연결
- ✅ 기능 협상

**서버 기능:**

- ✅ Resources: 컨텍스트 및 데이터
- ✅ Prompts: 템플릿 및 워크플로우
- ✅ Tools: 실행 가능한 함수

**클라이언트 기능:**

- ✅ Sampling: LLM 상호작용
- ✅ Roots: 경계 정의
- ✅ Elicitation: 정보 요청

**보안 원칙:**

- ✅ 사용자 동의 및 제어
- ✅ 데이터 프라이버시
- ✅ 도구 안전
- ✅ LLM 샘플링 제어

**추가 유틸리티:**

- ✅ Configuration (구성)
- ✅ Progress Tracking (진행 추적)
- ✅ Cancellation (취소)
- ✅ Error Reporting (오류 보고)
- ✅ Logging (로깅)

### LSP에서 영감

MCP는 Language Server Protocol의 성공을 AI 생태계로 가져옵니다:

- 표준화된 통합
- 모듈식 아키텍처
- 광범위한 호환성

MCP를 사용하여 강력하고 안전하며 상호 운용 가능한 AI 애플리케이션을 구축하세요!

---

## 추가 리소스

- **공식 사이트**: https://modelcontextprotocol.io
- **GitHub**: https://github.com/modelcontextprotocol
- **스키마**: [schema.ts](https://github.com/modelcontextprotocol/specification/blob/main/schema/2025-11-25/schema.ts)
- **커뮤니티**: [Communication](https://claude.ai/community/communication)

---

_이 문서는 Model Context Protocol 공식 사양에서 가져온 내용입니다._