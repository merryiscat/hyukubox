# MCP 인증 (Authorization) - Part 3

## Resource Parameter Implementation

### 개요

**필수 구현:**

- ✅ MCP 클라이언트는 **반드시(MUST)** [RFC 8707](https://www.rfc-editor.org/rfc/rfc8707.html)에 정의된 대로 OAuth 2.0용 Resource Indicators를 구현하여 토큰이 요청되는 대상 리소스를 명시적으로 지정해야 함

---

### resource 매개변수 요구사항

**1. 포함 위치:**

- ✅ **반드시(MUST)** 인증 요청과 토큰 요청 모두에 포함되어야 함

**2. 식별 대상:**

- ✅ **반드시(MUST)** 클라이언트가 토큰을 사용하려는 MCP 서버를 식별해야 함

**3. URI 형식:**

- ✅ **반드시(MUST)** [RFC 8707 Section 2](https://www.rfc-editor.org/rfc/rfc8707.html#name-access-token-request)에 정의된 대로 MCP 서버의 정식 URI를 사용해야 함

---

### Canonical Server URI (정식 서버 URI)

**정의:** MCP 서버의 정식 URI는 다음과 같이 정의됩니다:

- [RFC 8707 Section 2](https://www.rfc-editor.org/rfc/rfc8707.html#section-2)에 지정된 리소스 식별자
- [RFC 9728](https://datatracker.ietf.org/doc/html/rfc9728)의 `resource` 매개변수와 일치

---

**클라이언트 권장사항:**

- ✅ MCP 클라이언트는 **권장(SHOULD)** [RFC 8707](https://www.rfc-editor.org/rfc/rfc8707) 지침에 따라 접근하려는 MCP 서버에 대해 가능한 한 가장 구체적인 URI를 제공해야 함

**정식 형식:**

- 소문자 스키마 및 호스트 구성 요소 사용
- 구현은 **권장(SHOULD)** 견고성과 상호 운용성을 위해 대문자 스키마 및 호스트 구성 요소를 수락해야 함

---

**유효한 정식 URI 예시:**

```
✅ https://mcp.example.com/mcp
✅ https://mcp.example.com
✅ https://mcp.example.com:8443
✅ https://mcp.example.com/server/mcp
```

마지막 예시는 개별 MCP 서버를 식별하는 데 경로 구성 요소가 필요한 경우입니다.

---

**유효하지 않은 정식 URI 예시:**

```
❌ mcp.example.com
   이유: 스키마 누락

❌ https://mcp.example.com#fragment
   이유: 프래그먼트 포함
```

---

**후행 슬래시 처리:**

**참고사항:** `https://mcp.example.com/` (후행 슬래시 있음)과 `https://mcp.example.com` (후행 슬래시 없음) 모두 [RFC 3986](https://www.rfc-editor.org/rfc/rfc3986)에 따라 기술적으로 유효한 절대 URI입니다.

**권장사항:**

- ✅ 구현은 **권장(SHOULD)** 특정 리소스에 대해 후행 슬래시가 의미상 중요하지 않는 한 더 나은 상호 운용성을 위해 후행 슬래시 없이 형식을 일관되게 사용해야 함

---

### 사용 예시

**인증 요청:** `https://mcp.example.com`의 MCP 서버에 접근하는 경우, 인증 요청에 다음이 포함됩니다:

```
https://auth.example.com/authorize?
  response_type=code&
  client_id=...&
  redirect_uri=...&
  scope=files:read&
  resource=https%3A%2F%2Fmcp.example.com&  ← URL 인코딩된 resource
  state=...&
  code_challenge=...&
  code_challenge_method=S256
```

**토큰 요청:**

```http
POST /token HTTP/1.1
Host: auth.example.com
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code&
code=...&
redirect_uri=...&
client_id=...&
code_verifier=...&
resource=https%3A%2F%2Fmcp.example.com  ← resource 매개변수
```

---

**중요:**

- ✅ MCP 클라이언트는 **반드시(MUST)** 인증 서버가 지원하는지 여부에 관계없이 이 매개변수를 전송해야 함

---

## Access Token Usage (액세스 토큰 사용)

### Token Requirements (토큰 요구사항)

MCP 서버에 요청할 때 액세스 토큰 처리는 **반드시(MUST)** [OAuth 2.1 Section 5 "Resource Requests"](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-v2-1-13#section-5)에 정의된 요구사항을 준수해야 합니다.

---

#### 1. Authorization 헤더 사용

**필수:**

- ✅ MCP 클라이언트는 **반드시(MUST)** [OAuth 2.1 Section 5.1.1](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-v2-1-13#section-5.1.1)에 정의된 Authorization 요청 헤더 필드를 사용해야 함

**형식:**

```http
Authorization: Bearer <access-token>
```

**중요:**

- ✅ 권한 부여는 **반드시(MUST)** 동일한 논리적 세션의 일부인 경우에도 클라이언트에서 서버로의 모든 HTTP 요청에 포함되어야 함

---

#### 2. URI 쿼리 문자열 금지

**금지:**

- ❌ 액세스 토큰은 **절대(MUST NOT)** URI 쿼리 문자열에 포함되어서는 안 됨

**잘못된 예시:**

```http
❌ GET /mcp?access_token=eyJhbGci... HTTP/1.1
```

**올바른 예시:**

```http
✅ GET /mcp HTTP/1.1
   Host: mcp.example.com
   Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

---

### 요청 예시

**완전한 MCP 요청:**

```http
GET /mcp HTTP/1.1
Host: mcp.example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
MCP-Protocol-Version: 2025-11-25
MCP-Session-Id: session-abc-123
Accept: application/json, text/event-stream
```

**POST 요청:**

```http
POST /mcp HTTP/1.1
Host: mcp.example.com
Authorization: Bearer eyJhbGci...
Content-Type: application/json
MCP-Protocol-Version: 2025-11-25
MCP-Session-Id: session-abc-123

{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}
```

---

### Token Handling (토큰 처리)

#### 서버 측 검증

**필수 검증:** OAuth 2.1 리소스 서버 역할을 수행하는 MCP 서버는:

- ✅ **반드시(MUST)** [OAuth 2.1 Section 5.2](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-v2-1-13#section-5.2)에 설명된 대로 액세스 토큰을 검증해야 함

**Audience 검증:**

- ✅ MCP 서버는 **반드시(MUST)** 액세스 토큰이 [RFC 8707 Section 2](https://www.rfc-editor.org/rfc/rfc8707.html#section-2)에 따라 의도된 대상 청중으로 자신을 위해 특별히 발급되었는지 검증해야 함

---

**검증 실패 시:**

- ✅ 검증이 실패하면 서버는 **반드시(MUST)** [OAuth 2.1 Section 5.3](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-v2-1-13#section-5.3) 오류 처리 요구사항에 따라 응답해야 함
- ✅ 유효하지 않거나 만료된 토큰은 **반드시(MUST)** HTTP 401 응답을 받아야 함

**401 응답 예시:**

```http
HTTP/1.1 401 Unauthorized
WWW-Authenticate: Bearer error="invalid_token",
                         error_description="Token expired",
                         resource_metadata="https://mcp.example.com/.well-known/oauth-protected-resource"
```

---

#### 클라이언트 측 제약

**토큰 전송 제한:**

- ✅ MCP 클라이언트는 **절대(MUST NOT)** MCP 서버의 인증 서버에서 발급한 토큰 이외의 토큰을 MCP 서버에 전송해서는 안 됨

**서버 측 제약:**

- ✅ MCP 서버는 **반드시(MUST)** 자체 리소스와 함께 사용하기 위해 유효한 토큰만 수락해야 함
- ✅ MCP 서버는 **절대(MUST NOT)** 다른 토큰을 수락하거나 전송해서는 안 됨

---

## Error Handling (오류 처리)

### HTTP 상태 코드

서버는 **반드시(MUST)** 인증 오류에 대해 적절한 HTTP 상태 코드를 반환해야 합니다:

|상태 코드|설명|사용 시기|
|---|---|---|
|401|Unauthorized|인증이 필요하거나 토큰이 유효하지 않음|
|403|Forbidden|잘못된 범위 또는 권한 부족|
|400|Bad Request|잘못된 형식의 인증 요청|

---

### Scope Challenge Handling (범위 챌린지 처리)

이 섹션에서는 클라이언트가 이미 토큰을 가지고 있지만 추가 권한이 필요한 런타임 작업 중 범위 부족 오류 처리를 다룹니다.

**기반:**

- [OAuth 2.1 Section 5](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-v2-1-13#section-5)에 정의된 오류 처리 패턴
- [RFC 9728 (OAuth 2.0 Protected Resource Metadata)](https://datatracker.ietf.org/doc/html/rfc9728)의 메타데이터 필드 활용

---

#### Runtime Insufficient Scope Errors

**시나리오:** 클라이언트가 런타임 작업 중 범위가 부족한 액세스 토큰으로 요청을 할 때

**서버 응답 (권장):**

- ✅ `HTTP 403 Forbidden` 상태 코드 ([RFC 6750 Section 3.1](https://datatracker.ietf.org/doc/html/rfc6750#section-3.1) 참조)
- ✅ `Bearer` 스키마 및 추가 매개변수가 있는 `WWW-Authenticate` 헤더:

**매개변수:**

|매개변수|필수|설명|
|---|---|---|
|`error`|✅|"insufficient_scope" - 인증 실패 유형 표시|
|`scope`|✅|"required_scope1 required_scope2" - 작업에 필요한 최소 범위|
|`resource_metadata`|✅|Protected Resource Metadata 문서의 URI|
|`error_description`|❌|오류에 대한 사람이 읽을 수 있는 설명 (선택)|

---

**응답 예시:**

```http
HTTP/1.1 403 Forbidden
WWW-Authenticate: Bearer error="insufficient_scope",
                         scope="files:read files:write user:profile",
                         resource_metadata="https://mcp.example.com/.well-known/oauth-protected-resource",
                         error_description="Additional file write permission required"
Content-Type: application/json

{
  "jsonrpc": "2.0",
  "error": {
    "code": -32600,
    "message": "Insufficient scope for this operation"
  }
}
```

---

#### 서버 범위 관리

**서버 책임:** 범위 부족 오류로 응답할 때:

- ✅ 서버는 **권장(SHOULD)** `scope` 매개변수에 현재 요청을 충족하는 데 필요한 범위를 포함해야 함

**범위 포함 전략:**

서버는 포함할 범위를 결정할 때 유연성을 갖습니다:

**1. 최소 접근 방식:**

- 특정 작업에 대해 새로 필요한 범위만 포함
- 기존에 부여된 관련 범위도 필요한 경우 포함하여 클라이언트가 이전에 부여된 권한을 잃지 않도록 방지

**2. 권장 접근 방식:**

- 기존 관련 범위와 새로 필요한 범위를 모두 포함
- 클라이언트가 이전에 부여된 권한을 잃지 않도록 방지

**3. 확장 접근 방식:**

- 기존 범위, 새로 필요한 범위, 함께 작동하는 관련 범위 포함

**선택 기준:**

- 사용자 경험 영향 평가에 따라 결정
- 인증 마찰 고려

**일관성:**

- ✅ 서버는 **권장(SHOULD)** 범위 포함 전략에서 일관성을 유지하여 클라이언트에 예측 가능한 동작을 제공해야 함

**사용자 경험:**

- ✅ 서버는 **권장(SHOULD)** 포함할 범위를 결정할 때 사용자 경험 영향을 고려해야 함
- 잘못 구성된 범위는 빈번한 사용자 상호작용을 요구할 수 있음

---

### Step-Up Authorization Flow (단계별 인증 흐름)

**오류 발생 시기:** 클라이언트는 초기 인증 또는 런타임(`insufficient_scope`) 중에 범위 관련 오류를 받게 됩니다.

**클라이언트 응답 (권장):**

- ✅ 클라이언트는 **권장(SHOULD)** 단계별 인증 흐름을 통해 증가된 범위 집합으로 새 액세스 토큰을 요청하거나 다른 적절한 방법으로 오류를 처리하여 이러한 오류에 응답해야 함

---

**사용자 대신 작동하는 클라이언트:**

- ✅ **권장(SHOULD)** 단계별 인증 흐름을 시도해야 함

**자체적으로 작동하는 클라이언트 (client_credentials):**

- ✅ **가능(MAY)** 단계별 인증 흐름을 시도하거나 즉시 요청을 중단할 수 있음

---

#### 단계별 흐름 프로세스

**1. 오류 정보 파싱:**

- 인증 서버 응답 또는 `WWW-Authenticate` 헤더에서 오류 정보 추출

```typescript
const wwwAuth = parseWWWAuthenticate(response);
const error = wwwAuth.error; // "insufficient_scope"
const requiredScopes = wwwAuth.scope; // "files:write user:profile"
```

---

**2. 필요한 범위 결정:**

- [Scope Selection Strategy](https://claude.ai/chat/d1892e31-8053-4913-8394-fadb47edcd3a#scope-selection-strategy)에 설명된 대로 범위 결정

```typescript
// 챌린지된 범위 사용
const scopeToRequest = requiredScopes;
```

---

**3. (재)인증 시작:**

- 결정된 범위 집합으로 인증 시작

```typescript
const authUrl = buildAuthorizationUrl({
  authorizationEndpoint,
  clientId,
  redirectUri,
  scope: scopeToRequest,
  resource: mcpServerUrl,
  state: generateState(),
  codeChallenge: generatePKCE()
});

// 브라우저에서 authUrl 열기
```

---

**4. 원래 요청 재시도:**

- 새 인증으로 원래 요청 재시도
- 몇 번만 재시도하고 영구적인 인증 실패로 처리

```typescript
let retryCount = 0;
const MAX_RETRIES = 2;

async function retryWithNewToken() {
  if (retryCount >= MAX_RETRIES) {
    throw new Error("Authorization failed after multiple attempts");
  }
  
  retryCount++;
  const newToken = await performStepUpAuth(requiredScopes);
  return await makeRequestWithToken(newToken);
}
```

---

**재시도 제한:**

- ✅ 클라이언트는 **권장(SHOULD)** 재시도 제한을 구현해야 함
- ✅ 동일한 리소스 및 작업 조합에 대한 반복 실패를 방지하기 위해 범위 업그레이드 시도를 **권장(SHOULD)** 추적해야 함

---

**흐름 다이어그램:**

```
클라이언트                    MCP Server
   │                             │
   │  1. Request (토큰 있음)    │
   ├────────────────────────────►│
   │                             │
   │  2. 403 Insufficient Scope  │
   │     scope="files:write"     │
   │◄────────────────────────────┤
   │                             │
   │  3. Parse Error             │
   │                             │
   │  4. Determine Scopes        │
   │     (files:write + 기존)    │
   │                             │
   │  5. Step-Up Auth            │
   │     (브라우저 열기)         │
   │                             │
   │  6. Get New Token           │
   │                             │
   │  7. Retry Request           │
   │     (새 토큰)               │
   ├────────────────────────────►│
   │                             │
   │  8. Success                 │
   │◄────────────────────────────┤
```

---

## Security Considerations (보안 고려사항)

### OAuth 2.1 보안 모범 사례

**필수 준수:**

- ✅ 구현은 **반드시(MUST)** [OAuth 2.1 Section 7. "Security Considerations"](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-v2-1-13#name-security-considerations)에 명시된 OAuth 2.1 보안 모범 사례를 따라야 함

---

### 1. Token Audience Binding and Validation

**중요성:** [RFC 8707](https://www.rfc-editor.org/rfc/rfc8707.html) Resource Indicators는 **Authorization Server가 기능을 지원하는 경우** 토큰을 의도된 대상에 바인딩하여 중요한 보안 이점을 제공합니다.

**현재 및 향후 채택 지원:**

- ✅ MCP 클라이언트는 **반드시(MUST)** [Resource Parameter Implementation](https://claude.ai/chat/d1892e31-8053-4913-8394-fadb47edcd3a#resource-parameter-implementation) 섹션에 지정된 대로 인증 및 토큰 요청에 `resource` 매개변수를 포함해야 함
- ✅ MCP 서버는 **반드시(MUST)** 자신에게 제시된 토큰이 자신의 사용을 위해 특별히 발급되었는지 검증해야 함

**참조:** [Security Best Practices document](https://claude.ai/specification/2025-11-25/basic/security_best_practices#token-passthrough)에서 토큰 대상 검증이 중요한 이유와 토큰 통과가 명시적으로 금지되는 이유를 설명합니다.

---

### 2. Token Theft (토큰 도용)

**위협:** 클라이언트가 저장한 토큰 또는 서버에 캐시되거나 로그된 토큰을 획득한 공격자는 리소스 서버에 합법적으로 보이는 요청으로 보호된 리소스에 접근할 수 있습니다.

**완화 조치:**

**클라이언트 및 서버 요구사항:**

- ✅ **반드시(MUST)** 안전한 토큰 저장을 구현하고 [OAuth 2.1, Section 7.1](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-v2-1-13#section-7.1)에 설명된 대로 OAuth 모범 사례를 따라야 함

**Authorization Server 권장사항:**

- ✅ **권장(SHOULD)** 유출된 토큰의 영향을 줄이기 위해 단기 액세스 토큰을 발급해야 함

**공개 클라이언트:**

- ✅ 공개 클라이언트의 경우, 인증 서버는 **반드시(MUST)** [OAuth 2.1 Section 4.3.1 "Token Endpoint Extension"](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-v2-1-13#section-4.3.1)에 설명된 대로 리프레시 토큰을 회전해야 함

---

**보안 저장 예시:**

```typescript
// ❌ 잘못된 예시 - 평문 저장
localStorage.setItem('access_token', token);

// ✅ 올바른 예시 - 암호화된 저장
const encryptedToken = await encrypt(token, masterKey);
secureStorage.set('access_token', encryptedToken);
```

---

### 3. Communication Security (통신 보안)

**필수 요구사항:**

- ✅ 구현은 **반드시(MUST)** [OAuth 2.1 Section 1.5 "Communication Security"](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-v2-1-13#section-1.5)를 따라야 함

**구체적으로:**

**1. HTTPS 필수:**

- ✅ 모든 인증 서버 엔드포인트는 **반드시(MUST)** HTTPS를 통해 제공되어야 함

```
✅ https://auth.example.com/authorize
✅ https://auth.example.com/token
❌ http://auth.example.com/authorize  (HTTP 금지)
```

**2. Redirect URI 제한:**

- ✅ 모든 redirect URI는 **반드시(MUST)** `localhost`이거나 HTTPS를 사용해야 함

```
✅ http://localhost:3000/callback
✅ http://127.0.0.1:3000/callback
✅ https://app.example.com/callback
❌ http://app.example.com/callback  (로컬호스트가 아닌 HTTP 금지)
```

---

계속해서 나머지 보안 고려사항을 포함한 최종 문서를 생성하겠습니다...