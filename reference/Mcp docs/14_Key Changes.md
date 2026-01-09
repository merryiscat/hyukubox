# MCP 주요 변경사항 (Key Changes)

## 버전 정보

**현재 버전**: 2025-11-25 (최신)  
**이전 버전**: 2025-06-18

이 문서는 이전 개정판 [2025-06-18](https://claude.ai/specification/2025-06-18) 이후 Model Context Protocol (MCP) 사양에 적용된 변경사항을 나열합니다.

---

## 주요 변경사항 (Major Changes)

### 1. OpenID Connect Discovery 지원으로 인증 서버 검색 강화

**변경 내용:**

- [OpenID Connect Discovery 1.0](https://openid.net/specs/openid-connect-discovery-1_0.html) 지원 추가

**참조:**

- PR [#797](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/797)

**설명:**

- OAuth 2.0 인증 서버 메타데이터 외에 OIDC Discovery도 지원
- 더 넓은 범위의 인증 서버와 호환성 향상
- 표준화된 검색 메커니즘 제공

**영향:**

- 인증 서버 통합이 더 유연해짐
- OIDC를 사용하는 기존 시스템과의 통합 용이

---

### 2. 도구, 리소스, 프롬프트에 아이콘 메타데이터 지원

**변경 내용:** 서버가 다음 항목에 대한 추가 메타데이터로 아이콘을 노출할 수 있음:

- Tools (도구)
- Resources (리소스)
- Resource Templates (리소스 템플릿)
- Prompts (프롬프트)

**참조:**

- [SEP-973](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/973)

**예시:**

```json
{
  "name": "search_files",
  "description": "Search for files",
  "icon": "🔍",
  "inputSchema": { ... }
}
```

**이점:**

- 사용자 인터페이스 개선
- 시각적 식별 용이
- 더 나은 사용자 경험

---

### 3. WWW-Authenticate를 통한 점진적 범위 동의

**변경 내용:**

- `WWW-Authenticate` 헤더를 통한 증분 범위 동의 지원

**참조:**

- [SEP-835](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/835)

**동작 방식:**

```http
HTTP/1.1 401 Unauthorized
WWW-Authenticate: Bearer 
  realm="mcp",
  scope="mcp:tools mcp:resources",
  error="insufficient_scope"
```

**이점:**

- 필요할 때만 추가 권한 요청
- 사용자 경험 개선
- 세분화된 권한 관리

---

### 4. 도구 이름 지침 제공

**변경 내용:**

- 도구 이름에 대한 가이드라인 제공

**참조:**

- [SEP-986](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/1603)

**권장 사항:**

- 명확하고 설명적인 이름 사용
- 일관된 명명 규칙
- 충돌 방지를 위한 네임스페이스 고려

**예시:**

```
좋은 예: get_weather, search_files, create_document
나쁜 예: tool1, do_stuff, execute
```

---

### 5. ElicitResult 및 EnumSchema 개선

**변경 내용:**

- 더 표준 기반 접근 방식 사용
- 제목이 있는/없는 열거형 지원
- 단일 선택 및 다중 선택 열거형 지원

**참조:**

- [SEP-1330](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/1330)

**개선 사항:**

**단일 선택 열거형:**

```json
{
  "type": "string",
  "enum": ["option1", "option2", "option3"]
}
```

**다중 선택 열거형:**

```json
{
  "type": "array",
  "items": {
    "type": "string",
    "enum": ["tag1", "tag2", "tag3"]
  }
}
```

**제목이 있는 열거형:**

```json
{
  "type": "string",
  "enum": ["sm", "md", "lg"],
  "enumTitles": ["Small", "Medium", "Large"]
}
```

---

### 6. URL 모드 유도(Elicitation) 지원 추가

**변경 내용:**

- [URL 모드 유도](https://claude.ai/specification/2025-11-25/client/elicitation#url-elicitation-requests) 지원

**참조:**

- [SEP-1036](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/887)

**기능:**

- URL을 통한 정보 수집
- 웹 기반 입력 양식
- 외부 리소스 참조

**사용 사례:**

- 복잡한 입력 양식
- 파일 업로드
- OAuth 흐름

---

### 7. 샘플링에 도구 호출 지원 추가

**변경 내용:**

- `tools` 및 `toolChoice` 매개변수를 통한 도구 호출 지원

**참조:**

- [SEP-1577](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/1577)

**예시:**

```json
{
  "method": "sampling/createMessage",
  "params": {
    "messages": [...],
    "tools": [
      {
        "name": "get_weather",
        "description": "Get weather information",
        "inputSchema": { ... }
      }
    ],
    "toolChoice": "auto"
  }
}
```

**이점:**

- 에이전틱 워크플로우 지원
- 복잡한 작업 자동화
- 재귀적 도구 사용

---

### 8. OAuth 클라이언트 ID 메타데이터 문서 지원

**변경 내용:**

- 권장 클라이언트 등록 메커니즘으로 OAuth 클라이언트 ID 메타데이터 문서 지원

**참조:**

- [SEP-991](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/991)
- PR [#1296](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/1296)

**메타데이터 문서 예시:**

```json
{
  "client_id": "my-mcp-client",
  "client_name": "My MCP Client",
  "redirect_uris": ["http://localhost:3000/callback"],
  "grant_types": ["authorization_code", "refresh_token"]
}
```

**이점:**

- 클라이언트 등록 간소화
- 표준화된 메타데이터 형식
- 동적 클라이언트 등록 지원

---

### 9. 작업(Tasks) 실험적 지원 추가

**변경 내용:**

- [작업(Tasks)](https://claude.ai/specification/2025-11-25/basic/utilities/tasks)에 대한 실험적 지원
- 폴링 및 지연된 결과 검색을 통한 지속적인 요청 추적 가능

**참조:**

- [SEP-1686](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/1686)

**기능:**

- 장기 실행 작업 관리
- 진행 상황 추적
- 비동기 결과 검색

**사용 사례:**

```json
// 작업 생성
{
  "method": "tasks/create",
  "params": {
    "name": "process_large_dataset",
    "metadata": { ... }
  }
}

// 작업 상태 폴링
{
  "method": "tasks/get",
  "params": {
    "taskId": "task-123"
  }
}
```

**워크플로우:**

```
1. 작업 생성 → 작업 ID 반환
2. 작업 상태 폴링 → 진행률 확인
3. 작업 완료 → 결과 검색
```

---

## 소소한 변경사항 (Minor Changes)

### 1. stdio 전송에서 stderr 로깅 명확화

**변경 내용:**

- stdio 전송을 사용하는 서버는 오류 메시지뿐만 아니라 모든 유형의 로깅에 stderr를 사용할 수 있음을 명확화

**참조:**

- PR [#670](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/670)

**이유:**

- stdout은 JSON-RPC 메시지 전용
- stderr는 모든 진단 정보에 사용 가능

**로깅 레벨:**

```
stderr: ERROR, WARN, INFO, DEBUG
stdout: JSON-RPC 메시지만
```

---

### 2. Implementation 인터페이스에 description 필드 추가

**변경 내용:**

- `Implementation` 인터페이스에 선택적 `description` 필드 추가

**목적:**

- MCP 레지스트리 server.json 형식과 일치
- 초기화 중 사람이 읽을 수 있는 컨텍스트 제공

**예시:**

```json
{
  "name": "my-server",
  "version": "1.0.0",
  "description": "A server for managing project files and resources"
}
```

---

### 3. Streamable HTTP 전송에서 Origin 헤더 처리 명확화

**변경 내용:**

- 잘못된 Origin 헤더에 대해 HTTP 403 Forbidden으로 응답해야 함을 명확화

**참조:**

- PR [#1439](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/1439)

**보안:**

```http
# 잘못된 Origin
Origin: https://malicious-site.com

# 서버 응답
HTTP/1.1 403 Forbidden
```

**목적:**

- CORS 보안 강화
- 무단 접근 방지

---

### 4. 보안 모범 사례 가이드 업데이트

**변경 내용:**

- [보안 모범 사례 가이드](https://modelcontextprotocol.io/specification/draft/basic/security_best_practices) 업데이트

**개선 사항:**

- 더 상세한 보안 지침
- 실제 공격 시나리오
- 완화 전략
- 코드 예시

---

### 5. 입력 검증 오류를 도구 실행 오류로 반환

**변경 내용:**

- 입력 검증 오류는 프로토콜 오류가 아닌 도구 실행 오류로 반환해야 함

**참조:**

- [SEP-1303](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/1303)

**이유:**

- 모델의 자가 수정 가능
- 더 나은 오류 복구

**예시:**

```json
// 이전 (프로토콜 오류)
{
  "error": {
    "code": -32602,
    "message": "Invalid params"
  }
}

// 현재 (도구 실행 오류)
{
  "content": [
    {
      "type": "text",
      "text": "Error: Invalid input - 'location' field is required"
    }
  ],
  "isError": true
}
```

---

### 6. 서버가 임의로 연결을 끊을 수 있도록 SSE 스트림 폴링 지원

**변경 내용:**

- 서버가 자유롭게 연결을 끊을 수 있도록 허용하여 SSE 스트림 폴링 지원

**참조:**

- [SEP-1699](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/1699)

**이점:**

- 리소스 관리 개선
- 장기 연결 부담 감소
- 클라이언트가 필요할 때 재연결

---

### 7. SEP-1699 명확화: GET 스트림 폴링 및 재개

**변경 내용:**

- GET 스트림은 폴링 지원
- 스트림 원본에 관계없이 항상 GET을 통한 재개
- 이벤트 ID는 스트림 ID를 인코딩해야 함
- 연결 끊김에는 서버 시작 종료 포함

**참조:**

- Issue [#1847](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/1847)

**구현 세부사항:**

```http
# 초기 연결
GET /events HTTP/1.1

# 재개 (Last-Event-ID 사용)
GET /events HTTP/1.1
Last-Event-ID: stream-123:event-456
```

---

### 8. RFC 9728에 맞춰 OAuth 2.0 메타데이터 검색 조정

**변경 내용:**

- `WWW-Authenticate` 헤더를 선택 사항으로 변경
- `.well-known` 엔드포인트로 폴백

**참조:**

- [SEP-985](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/985)

**폴백 메커니즘:**

```
1. WWW-Authenticate 헤더 확인
2. 없으면 /.well-known/oauth-protected-resource 시도
3. 메타데이터 검색 및 사용
```

---

### 9. 유도 스키마의 모든 기본 타입에 기본값 지원

**변경 내용:**

- 모든 기본 타입(string, number, enum)에서 기본값 지원

**참조:**

- [SEP-1034](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/1034)

**예시:**

```json
{
  "type": "object",
  "properties": {
    "name": {
      "type": "string",
      "default": "Unnamed"
    },
    "count": {
      "type": "number",
      "default": 0
    },
    "size": {
      "type": "string",
      "enum": ["sm", "md", "lg"],
      "default": "md"
    }
  }
}
```

---

### 10. JSON Schema 2020-12를 기본 방언으로 설정

**변경 내용:**

- MCP 스키마 정의의 기본 방언으로 JSON Schema 2020-12 설정

**참조:**

- [SEP-1613](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/1613)

**이점:**

- 최신 JSON Schema 기능 사용
- 표준화된 스키마 검증
- 더 나은 도구 지원

---

## 기타 스키마 변경사항 (Other Schema Changes)

### 요청 페이로드를 독립형 매개변수 스키마로 분리

**변경 내용:**

- RPC 메서드 정의에서 요청 페이로드 분리
- 독립형 매개변수 스키마로 변환

**참조:**

- [SEP-1319](https://github.com/modelcontextprotocol/specification/issues/1319)
- PR [#1284](https://github.com/modelcontextprotocol/specification/pull/1284)

**이전:**

```typescript
interface ListToolsRequest {
  method: "tools/list";
  params?: { cursor?: string };
}
```

**현재:**

```typescript
interface ListToolsRequest {
  method: "tools/list";
  params?: ListToolsParams;
}

interface ListToolsParams {
  cursor?: string;
}
```

**이점:**

- 재사용 가능한 스키마
- 더 나은 타입 안전성
- 명확한 문서화

---

## 거버넌스 및 프로세스 업데이트 (Governance and Process Updates)

### 1. MCP 거버넌스 구조 공식화

**변경 내용:**

- Model Context Protocol 거버넌스 구조 공식화

**참조:**

- [SEP-932](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/932)

**구조:**

- 스티어링 커미티
- 기술 워킹 그룹
- 커뮤니티 대표

**목적:**

- 투명한 의사 결정
- 커뮤니티 참여
- 장기적인 전략 수립

---

### 2. MCP 커뮤니티를 위한 공유 커뮤니케이션 관행 및 가이드라인 수립

**변경 내용:**

- 공유 커뮤니케이션 관행 및 가이드라인 수립

**참조:**

- [SEP-994](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/994)

**가이드라인:**

- 코드 오브 컨덕트
- 커뮤니케이션 채널
- 이슈 템플릿
- PR 가이드라인

---

### 3. 워킹 그룹 및 관심 그룹 공식화

**변경 내용:**

- MCP 거버넌스에서 워킹 그룹 및 관심 그룹 공식화

**참조:**

- [SEP-1302](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/1302)

**그룹 유형:**

- **워킹 그룹**: 특정 기술 영역 담당
- **관심 그룹**: 특정 사용 사례 또는 도메인 탐색

**예시:**

- 보안 워킹 그룹
- 도구 표준화 워킹 그룹
- 엔터프라이즈 통합 관심 그룹

---

### 4. 명확한 요구사항을 갖춘 SDK 계층 시스템 수립

**변경 내용:**

- 기능 지원 및 유지 관리 약속에 대한 명확한 요구사항을 갖춘 SDK 계층 시스템 수립

**참조:**

- [SEP-1730](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/1730)

**SDK 계층:**

**Tier 1 (공식):**

- ✅ 모든 핵심 기능 지원
- ✅ 활발한 유지 관리
- ✅ 포괄적인 문서
- ✅ 예제 및 튜토리얼

**Tier 2 (커뮤니티):**

- ✅ 핵심 기능 지원
- ⚠️ 커뮤니티 유지 관리
- ✅ 기본 문서

**Tier 3 (실험적):**

- ⚠️ 부분 기능 지원
- ⚠️ 최소 유지 관리
- ⚠️ 제한적 문서

---

## 전체 변경 로그 (Full Changelog)

마지막 프로토콜 개정 이후 변경된 모든 사항의 전체 목록은 다음을 참조하세요:

**GitHub 비교:** [2025-06-18...2025-11-25](https://github.com/modelcontextprotocol/specification/compare/2025-06-18...2025-11-25)

---

## 요약

### 주요 개선사항

**인증 및 보안:**

- ✅ OpenID Connect Discovery 지원
- ✅ 점진적 범위 동의
- ✅ OAuth 클라이언트 ID 메타데이터
- ✅ 개선된 보안 모범 사례

**사용자 경험:**

- ✅ 아이콘 메타데이터 지원
- ✅ 도구 이름 지침
- ✅ URL 모드 유도

**기능 강화:**

- ✅ 샘플링에서 도구 호출
- ✅ 개선된 열거형 스키마
- ✅ 작업 지원 (실험적)
- ✅ 기본값 지원

**프로토콜 개선:**

- ✅ JSON Schema 2020-12
- ✅ SSE 스트림 폴링
- ✅ 개선된 오류 처리

**거버넌스:**

- ✅ 공식화된 구조
- ✅ 커뮤니티 가이드라인
- ✅ SDK 계층 시스템

### 주요 변경사항 수

- **주요 변경**: 9개
- **소소한 변경**: 10개
- **스키마 변경**: 1개
- **거버넌스 업데이트**: 4개

**총 24개의 중요한 개선사항**이 이번 버전에 포함되었습니다!

---

## 다음 단계

### 업그레이드 가이드

기존 구현을 업그레이드하는 경우:

1. **인증 시스템 검토**
    
    - OIDC Discovery 지원 확인
    - 점진적 범위 동의 구현
2. **스키마 업데이트**
    
    - JSON Schema 2020-12로 마이그레이션
    - 새로운 열거형 형식 적용
3. **오류 처리 개선**
    
    - 도구 실행 오류 vs 프로토콜 오류 구분
    - 모델 자가 수정 지원
4. **새 기능 탐색**
    
    - 작업(Tasks) API
    - URL 모드 유도
    - 샘플링에서 도구 호출

### 추가 리소스

- **사양 문서**: [Specification](https://claude.ai/specification/2025-11-25)
- **아키텍처**: [Architecture](https://claude.ai/specification/2025-11-25/architecture/index)
- **보안 가이드**: [Security Best Practices](https://claude.ai/specification/2025-11-25/basic/security_best_practices)
- **GitHub**: https://github.com/modelcontextprotocol

---

_이 문서는 Model Context Protocol 공식 변경 로그에서 가져온 내용입니다._