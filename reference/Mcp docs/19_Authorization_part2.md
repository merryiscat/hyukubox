# MCP 인증 (Authorization) - Part 2

## Client Registration Approaches (클라이언트 등록 방법)

MCP는 세 가지 클라이언트 등록 메커니즘을 지원합니다. 시나리오에 따라 선택하세요:

### 등록 방법 비교

|방법|사용 시기|우선순위|
|---|---|---|
|**Client ID Metadata Documents**|클라이언트와 서버에 사전 관계가 없을 때 (가장 일반적)|✅ 권장|
|**Pre-registration**|클라이언트와 서버에 기존 관계가 있을 때|1순위|
|**Dynamic Client Registration**|하위 호환성 또는 특정 요구사항|폴백|

---

### 클라이언트 우선순위

모든 옵션을 지원하는 클라이언트는 **권장(SHOULD)** 다음 우선순위 순서를 따라야 합니다:

**1. Pre-registered 클라이언트 정보 사용**

- 클라이언트가 서버에 대해 사용 가능한 사전 등록된 클라이언트 정보가 있는 경우

**2. Client ID Metadata Documents 사용**

- Authorization Server가 지원을 표시하는 경우
- OAuth Authorization Server Metadata의 `client_id_metadata_document_supported` 확인

**3. Dynamic Client Registration 사용**

- Authorization Server가 지원하는 경우 폴백으로 사용
- OAuth Authorization Server Metadata의 `registration_endpoint` 확인

**4. 사용자 입력 요청**

- 다른 옵션을 사용할 수 없는 경우 클라이언트 정보 입력 요청

---

## 1. Client ID Metadata Documents

### 개요

**권장사항:**

- ✅ MCP 클라이언트 및 인증 서버는 **권장(SHOULD)** OAuth Client ID Metadata Documents를 지원해야 함
- [OAuth Client ID Metadata Document](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-client-id-metadata-document-00) 명세 참조

**접근 방식:** 클라이언트가 HTTPS URL을 클라이언트 식별자로 사용할 수 있도록 하며, URL은 클라이언트 메타데이터를 포함하는 JSON 문서를 가리킵니다.

**해결하는 문제:** 서버와 클라이언트 간에 사전 관계가 없는 일반적인 MCP 시나리오 해결

---

### Implementation Requirements (구현 요구사항)

**필수 준수:**

- ✅ Client ID Metadata Documents를 지원하는 MCP 구현은 **반드시(MUST)** [OAuth Client ID Metadata Document](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-client-id-metadata-document-00)에 지정된 요구사항을 따라야 함

---

#### MCP 클라이언트 요구사항

**1. 메타데이터 문서 호스팅:**

- ✅ 클라이언트는 **반드시(MUST)** RFC 요구사항을 따르는 HTTPS URL에서 메타데이터 문서를 호스팅해야 함

**2. client_id URL 형식:**

- ✅ `client_id` URL은 **반드시(MUST)** "https" 스키마를 사용하고 경로 구성 요소를 포함해야 함
- 예: `https://example.com/client.json`

**3. 필수 속성:**

- ✅ 메타데이터 문서는 **반드시(MUST)** 최소한 다음 속성을 포함해야 함:
    - `client_id`
    - `client_name`
    - `redirect_uris`

**4. client_id 일치:**

- ✅ 클라이언트는 **반드시(MUST)** 메타데이터의 `client_id` 값이 문서 URL과 정확히 일치하도록 보장해야 함

**5. 클라이언트 인증 (선택):**

- ✅ 클라이언트는 **가능(MAY)** 적절한 JWKS 구성과 함께 `private_key_jwt`를 클라이언트 인증(예: 토큰 엔드포인트에 대한 요청)에 사용할 수 있음
- [Section 6.2 of Client ID Metadata Document](https://www.ietf.org/archive/id/draft-ietf-oauth-client-id-metadata-document-00.html#section-6.2) 참조

---

#### Authorization Server 요구사항

**1. 메타데이터 문서 가져오기:**

- ✅ **권장(SHOULD)** URL 형식의 client_ids를 만나면 메타데이터 문서를 가져와야 함

**2. client_id 검증:**

- ✅ **반드시(MUST)** 가져온 문서의 `client_id`가 URL과 정확히 일치하는지 검증해야 함

**3. 캐싱:**

- ✅ **권장(SHOULD)** HTTP 캐시 헤더를 존중하여 메타데이터를 캐시해야 함

**4. Redirect URI 검증:**

- ✅ **반드시(MUST)** 인증 요청에 제시된 redirect URI를 메타데이터 문서의 URI와 비교하여 검증해야 함

**5. 문서 구조 검증:**

- ✅ **반드시(MUST)** 문서 구조가 유효한 JSON이고 필수 필드를 포함하는지 검증해야 함

**6. 보안 고려사항:**

- ✅ **권장(SHOULD)** [Section 6 of Client ID Metadata Document](https://www.ietf.org/archive/id/draft-ietf-oauth-client-id-metadata-document-00.html#section-6)의 보안 고려사항을 따라야 함

---

### Example Metadata Document (메타데이터 문서 예시)

```json
{
  "client_id": "https://app.example.com/oauth/client-metadata.json",
  "client_name": "Example MCP Client",
  "client_uri": "https://app.example.com",
  "logo_uri": "https://app.example.com/logo.png",
  "redirect_uris": [
    "http://127.0.0.1:3000/callback",
    "http://localhost:3000/callback"
  ],
  "grant_types": ["authorization_code"],
  "response_types": ["code"],
  "token_endpoint_auth_method": "none"
}
```

**필드 설명:**

|필드|필수|설명|
|---|---|---|
|`client_id`|✅|메타데이터 문서 URL (정확히 일치해야 함)|
|`client_name`|✅|클라이언트 표시 이름|
|`client_uri`|❌|클라이언트 홈페이지|
|`logo_uri`|❌|클라이언트 로고 URL|
|`redirect_uris`|✅|허용된 리디렉션 URI 배열|
|`grant_types`|❌|지원되는 권한 부여 유형|
|`response_types`|❌|지원되는 응답 유형|
|`token_endpoint_auth_method`|❌|토큰 엔드포인트 인증 방법|

---

### Client ID Metadata Documents Flow

**전체 흐름:**

```
클라이언트                    Auth Server
   │                             │
   │  1. Authorization Request   │
   │     client_id=https://...   │
   ├────────────────────────────►│
   │                             │
   │                             │  2. Fetch Metadata
   │                             │     GET https://app.example.com/
   │                             │         oauth/client-metadata.json
   │                             ├───────────►┐
   │                             │            │
   │                             │  3. Metadata Response
   │                             │     {                             │
   │                             │       "client_id": "...",
   │                             │       "client_name": "...",
   │                             │       "redirect_uris": [...]
   │                             │     }
   │                             │◄───────────┘
   │                             │
   │                             │  4. Validate
   │                             │     - client_id 일치
   │                             │     - redirect_uri 검증
   │                             │     - 구조 검증
   │                             │
   │  5. Authorization Response  │
   │     code=...                │
   │◄────────────────────────────┤
   │                             │
   │  6. Token Request           │
   │     code=...                │
   ├────────────────────────────►│
   │                             │
   │  7. Token Response          │
   │     access_token=...        │
   │◄────────────────────────────┤
```

---

### Discovery (검색)

**Auth Server 지원 표시:** 인증 서버는 OAuth Authorization Server 메타데이터에 다음 속성을 포함하여 Client ID Metadata Documents를 사용하는 클라이언트를 지원함을 알립니다:

```json
{
  "client_id_metadata_document_supported": true
}
```

**클라이언트 동작:**

- ✅ MCP 클라이언트는 **권장(SHOULD)** 이 기능을 확인해야 함
- ✅ 사용할 수 없는 경우 Dynamic Client Registration 또는 사전 등록으로 **가능(MAY)** 폴백할 수 있음

---

## 2. Preregistration (사전 등록)

### 개요

**권장사항:**

- ✅ MCP 클라이언트는 **권장(SHOULD)** 사전 등록 흐름에서 제공하는 것과 같은 정적 클라이언트 자격 증명에 대한 옵션을 지원해야 함

---

### 구현 방법

**방법 1: 하드코딩**

- 해당 인증 서버와 상호작용할 때 MCP 클라이언트가 사용할 클라이언트 ID(및 해당되는 경우 클라이언트 자격 증명)를 하드코딩

**예시:**

```typescript
const CLIENT_CREDENTIALS = {
  'auth.example.com': {
    clientId: 'mcp-client-prod',
    clientSecret: 'secret-abc-123' // 기밀 클라이언트의 경우
  }
};
```

---

**방법 2: UI 제공**

- 사용자가 OAuth 클라이언트를 직접 등록한 후(예: 서버에서 호스팅하는 구성 인터페이스를 통해) 이러한 세부 정보를 입력할 수 있는 UI를 제공

**UI 예시:**

```
┌─────────────────────────────────────┐
│  클라이언트 등록 정보 입력          │
├─────────────────────────────────────┤
│                                     │
│  Client ID:                         │
│  [___________________________]      │
│                                     │
│  Client Secret (선택):              │
│  [___________________________]      │
│                                     │
│  Redirect URI:                      │
│  [___________________________]      │
│                                     │
│  [저장]  [취소]                     │
└─────────────────────────────────────┘
```

---

### 사전 등록 프로세스

**1. 서버에서 클라이언트 등록:**

```
1. 서버 관리자 콘솔 접속
2. 새 OAuth 클라이언트 생성
3. 클라이언트 정보 구성:
   - 이름: "MCP Desktop Client"
   - Redirect URIs: ["http://localhost:3000/callback"]
   - Grant Types: ["authorization_code"]
4. client_id 및 client_secret 저장
```

**2. 클라이언트 구성:**

```typescript
// 클라이언트 구성 파일
{
  "mcp_servers": {
    "example_server": {
      "url": "https://mcp.example.com",
      "auth": {
        "type": "oauth2",
        "client_id": "pre-registered-client-id",
        "client_secret": "pre-registered-secret",
        "authorization_endpoint": "https://auth.example.com/authorize",
        "token_endpoint": "https://auth.example.com/token"
      }
    }
  }
}
```

---

## 3. Dynamic Client Registration (동적 클라이언트 등록)

### 개요

**선택 사항:**

- ✅ MCP 클라이언트 및 인증 서버는 **가능(MAY)** OAuth 2.0 Dynamic Client Registration Protocol [RFC7591](https://datatracker.ietf.org/doc/html/rfc7591)을 지원할 수 있음

**목적:**

- 사용자 상호작용 없이 MCP 클라이언트가 OAuth 클라이언트 ID를 얻을 수 있도록 허용

**이유:**

- 이 옵션은 이전 버전의 MCP 인증 사양과의 하위 호환성을 위해 포함됨

---

### 등록 흐름

```
클라이언트                    Auth Server
   │                             │
   │  1. Discovery               │
   │     GET /.well-known/...    │
   ├────────────────────────────►│
   │                             │
   │  2. Metadata                │
   │     {                       │
   │       "registration_        │
   │        endpoint": "..."     │
   │     }                       │
   │◄────────────────────────────┤
   │                             │
   │  3. Registration Request    │
   │     POST /register          │
   │     {                       │
   │       "client_name": "...", │
   │       "redirect_uris": [...] │
   │     }                       │
   ├────────────────────────────►│
   │                             │
   │  4. Registration Response   │
   │     {                       │
   │       "client_id": "...",   │
   │       "client_secret": "..."│
   │     }                       │
   │◄────────────────────────────┤
```

---

## Scope Selection Strategy (범위 선택 전략)

### 최소 권한 원칙

**권장사항:** 인증 흐름을 구현할 때:

- ✅ MCP 클라이언트는 **권장(SHOULD)** 의도된 작업에 필요한 범위만 요청하여 최소 권한 원칙을 따라야 함

---

### 초기 인증 핸드셰이크 중 범위 선택

MCP 클라이언트는 **권장(SHOULD)** 다음 우선순위 순서를 따라야 합니다:

**1. WWW-Authenticate의 `scope` 매개변수 사용**

- 401 응답의 초기 `WWW-Authenticate` 헤더에서 제공된 경우

**예시:**

```http
HTTP/1.1 401 Unauthorized
WWW-Authenticate: Bearer scope="files:read files:write"
```

클라이언트 동작:

```typescript
const scope = parseWWWAuthenticate(response).scope;
// scope = "files:read files:write"
```

---

**2. scopes_supported 사용 (폴백)**

- `scope`를 사용할 수 없는 경우
- Protected Resource Metadata 문서의 `scopes_supported`에 정의된 모든 범위 사용
- `scopes_supported`가 정의되지 않은 경우 `scope` 매개변수 생략

**예시:**

```json
// Protected Resource Metadata
{
  "scopes_supported": [
    "files:read",
    "files:write",
    "user:profile"
  ]
}
```

클라이언트 동작:

```typescript
if (scope from WWW-Authenticate) {
  use that scope
} else if (scopes_supported) {
  scope = scopes_supported.join(' ')
  // "files:read files:write user:profile"
} else {
  // scope 매개변수 생략
}
```

---

### 전략의 근거

**일반 목적 클라이언트:** 이 접근 방식은 일반적으로 개별 범위 선택에 대해 정보에 입각한 결정을 내릴 도메인별 지식이 부족한 MCP 클라이언트의 일반 목적 특성을 수용합니다.

**모든 범위 요청:** 사용 가능한 모든 범위를 요청하면 인증 서버와 최종 사용자가 동의 프로세스 중에 적절한 권한을 결정할 수 있습니다.

**사용자 마찰 최소화:** 이 접근 방식은 최소 권한 원칙을 따르면서 사용자 마찰을 최소화합니다.

---

### scopes_supported 의도

**기본 기능:**

- `scopes_supported` 필드는 기본 기능에 필요한 최소 범위 집합을 나타내기 위한 것
- [Scope Minimization](https://claude.ai/specification/2025-11-25/basic/security_best_practices#scope-minimization) 참조

**증분 요청:**

- 추가 범위는 [Scope Challenge Handling](https://claude.ai/chat/d1892e31-8053-4913-8394-fadb47edcd3a#scope-challenge-handling) 섹션에 설명된 단계별 인증 흐름 단계를 통해 증분적으로 요청됨

---

## Authorization Flow Steps (인증 흐름 단계)

### 완전한 인증 흐름

```
사용자            클라이언트           MCP Server        Auth Server
 │                  │                    │                  │
 │  1. 리소스 요청  │                    │                  │
 ├─────────────────►│                    │                  │
 │                  │                    │                  │
 │                  │  2. 리소스 요청    │                  │
 │                  │    (토큰 없음)     │                  │
 │                  ├───────────────────►│                  │
 │                  │                    │                  │
 │                  │  3. 401 + Metadata │                  │
 │                  │◄───────────────────┤                  │
 │                  │                    │                  │
 │                  │  4. Get Metadata   │                  │
 │                  ├───────────────────►│                  │
 │                  │                    │                  │
 │                  │  5. Metadata       │                  │
 │                  │◄───────────────────┤                  │
 │                  │                    │                  │
 │                  │  6. Discover Auth  │                  │
 │                  │    Server          │                  │
 │                  ├────────────────────┼─────────────────►│
 │                  │                    │                  │
 │                  │  7. Auth Metadata  │                  │
 │                  │◄───────────────────┼──────────────────┤
 │                  │                    │                  │
 │  8. 브라우저 열기 │                    │                  │
 │  (인증)          │                    │                  │
 │◄─────────────────┤                    │                  │
 │                  │                    │                  │
 │  9. 인증 요청    │                    │                  │
 ├──────────────────┼────────────────────┼─────────────────►│
 │                  │                    │                  │
 │  10. 사용자 인증 │                    │                  │
 │      및 동의     │                    │                  │
 │◄─────────────────┼────────────────────┼──────────────────┤
 │                  │                    │                  │
 │  11. Redirect    │                    │                  │
 │      + Code      │                    │                  │
 ├─────────────────►│                    │                  │
 │                  │                    │                  │
 │                  │  12. Token Request │                  │
 │                  │     (code)         │                  │
 │                  ├────────────────────┼─────────────────►│
 │                  │                    │                  │
 │                  │  13. Access Token  │                  │
 │                  │◄───────────────────┼──────────────────┤
 │                  │                    │                  │
 │                  │  14. 리소스 요청   │                  │
 │                  │      + Token       │                  │
 │                  ├───────────────────►│                  │
 │                  │                    │                  │
 │                  │  15. 리소스 응답   │                  │
 │                  │◄───────────────────┤                  │
 │                  │                    │                  │
 │  16. 결과 표시   │                    │                  │
 │◄─────────────────┤                    │                  │
```

---

### 상세 단계 설명

**1-2. 초기 리소스 요청:**

```http
GET /mcp HTTP/1.1
Host: mcp.example.com
```

**3. 401 응답:**

```http
HTTP/1.1 401 Unauthorized
WWW-Authenticate: Bearer resource_metadata="https://mcp.example.com/.well-known/oauth-protected-resource",
                         scope="files:read"
```

**4-5. Protected Resource Metadata 가져오기:**

```http
GET /.well-known/oauth-protected-resource HTTP/1.1
Host: mcp.example.com
```

응답:

```json
{
  "resource": "https://mcp.example.com",
  "authorization_servers": ["https://auth.example.com"],
  "scopes_supported": ["files:read", "files:write"]
}
```

**6-7. Authorization Server Metadata 검색:**

```http
GET /.well-known/oauth-authorization-server HTTP/1.1
Host: auth.example.com
```

응답:

```json
{
  "authorization_endpoint": "https://auth.example.com/authorize",
  "token_endpoint": "https://auth.example.com/token",
  "code_challenge_methods_supported": ["S256"]
}
```

**8-9. 인증 요청 (브라우저):**

```
https://auth.example.com/authorize?
  response_type=code&
  client_id=https://app.example.com/oauth/client-metadata.json&
  redirect_uri=http://localhost:3000/callback&
  scope=files:read&
  resource=https://mcp.example.com&
  state=abc123&
  code_challenge=xyz789&
  code_challenge_method=S256
```

**10-11. 사용자 인증 및 리디렉션:**

```
http://localhost:3000/callback?code=auth_code_123&state=abc123
```

**12-13. 토큰 교환:**

```http
POST /token HTTP/1.1
Host: auth.example.com
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code&
code=auth_code_123&
redirect_uri=http://localhost:3000/callback&
client_id=https://app.example.com/oauth/client-metadata.json&
code_verifier=original_verifier
```

응답:

```json
{
  "access_token": "eyJhbGci...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "refresh..."
}
```

**14-15. 토큰으로 리소스 요청:**

```http
GET /mcp HTTP/1.1
Host: mcp.example.com
Authorization: Bearer eyJhbGci...
```

---

계속해서 Part 3을 생성하겠습니다...