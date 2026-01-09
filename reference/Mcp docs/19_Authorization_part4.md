# MCP 인증 (Authorization) - Part 4 (최종)

## Security Considerations (계속)

### 4. Authorization Code Protection (인증 코드 보호)

**위협:** 인증 응답에 포함된 인증 코드에 접근한 공격자는 인증 코드를 액세스 토큰으로 교환하려고 시도하거나 인증 코드를 다른 방식으로 사용할 수 있습니다.

**참조:** [OAuth 2.1 Section 7.5](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-v2-1-13#section-7.5)에 자세히 설명되어 있습니다.

---

#### PKCE 필수 구현

**클라이언트 요구사항:**

- ✅ MCP 클라이언트는 **반드시(MUST)** [OAuth 2.1 Section 7.5.2](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-v2-1-13#section-7.5.2)에 따라 PKCE를 구현해야 함
- ✅ **반드시(MUST)** 인증을 진행하기 전에 PKCE 지원을 확인해야 함

**PKCE의 역할:** PKCE는 클라이언트가 비밀 검증자-챌린지 쌍을 생성하도록 요구하여 인증 코드 가로채기 및 주입 공격을 방지하여 원래 요청자만 인증 코드를 토큰으로 교환할 수 있도록 보장합니다.

---

**Code Challenge Method:**

- ✅ MCP 클라이언트는 **반드시(MUST)** 기술적으로 가능한 경우 [OAuth 2.1 Section 4.1.1](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-v2-1-13#section-4.1.1)에서 요구하는 대로 `S256` 코드 챌린지 방법을 사용해야 함

---

#### PKCE 지원 검증

OAuth 2.1 및 PKCE 사양은 클라이언트가 PKCE 지원을 검색하는 메커니즘을 정의하지 않으므로:

**필수 검증:**

- ✅ MCP 클라이언트는 **반드시(MUST)** 인증 서버 메타데이터에 의존하여 이 기능을 확인해야 함

---

**OAuth 2.0 Authorization Server Metadata:**

- `code_challenge_methods_supported`가 없으면 인증 서버가 PKCE를 지원하지 않음
- ✅ MCP 클라이언트는 **반드시(MUST)** 진행을 거부해야 함

**OpenID Connect Discovery 1.0:**

- [OpenID Provider Metadata](https://openid.net/specs/openid-connect-discovery-1_0.html#ProviderMetadata)는 `code_challenge_methods_supported`를 정의하지 않음
- 그러나 이 필드는 일반적으로 OpenID 공급자에 포함됨
- ✅ MCP 클라이언트는 **반드시(MUST)** 공급자 메타데이터 응답에서 `code_challenge_methods_supported`의 존재를 확인해야 함
- ✅ 필드가 없으면 MCP 클라이언트는 **반드시(MUST)** 진행을 거부해야 함

---

**OpenID Provider 요구사항:**

- ✅ OpenID Connect Discovery 1.0을 제공하는 인증 서버는 **반드시(MUST)** MCP 호환성을 보장하기 위해 메타데이터에 `code_challenge_methods_supported`를 포함해야 함

---

**메타데이터 예시:**

```json
{
  "authorization_endpoint": "https://auth.example.com/authorize",
  "token_endpoint": "https://auth.example.com/token",
  "code_challenge_methods_supported": ["S256"]  ← 필수
}
```

---

**PKCE 구현 예시:**

```typescript
// 1. Code Verifier 생성
const codeVerifier = generateRandomString(128);

// 2. Code Challenge 생성
const codeChallenge = base64url(sha256(codeVerifier));

// 3. 인증 요청
const authUrl = buildAuthUrl({
  code_challenge: codeChallenge,
  code_challenge_method: 'S256'
});

// 4. 토큰 교환
const tokenResponse = await exchangeCode({
  code: authorizationCode,
  code_verifier: codeVerifier  // 원래 검증자
});
```

---

### 5. Open Redirection (오픈 리디렉션)

**위협:** 공격자가 악의적인 redirect URI를 조작하여 사용자를 피싱 사이트로 유도할 수 있습니다.

---

#### 클라이언트 요구사항

**Redirect URI 등록:**

- ✅ MCP 클라이언트는 **반드시(MUST)** 인증 서버에 redirect URI를 등록해야 함

**State 매개변수:**

- ✅ MCP 클라이언트는 **권장(SHOULD)** 인증 코드 흐름에서 state 매개변수를 사용하고 검증해야 함
- ✅ 원래 state와 일치하지 않거나 포함하지 않는 결과는 **권장(SHOULD)** 폐기해야 함

**State 검증 예시:**

```typescript
// 1. State 생성 및 저장
const state = generateRandomString();
sessionStorage.setItem('oauth_state', state);

// 2. 인증 요청에 포함
const authUrl = buildAuthUrl({ state });

// 3. 콜백에서 검증
function handleCallback(receivedState) {
  const expectedState = sessionStorage.getItem('oauth_state');
  
  if (receivedState !== expectedState) {
    throw new Error('State mismatch - possible CSRF attack');
  }
  
  sessionStorage.removeItem('oauth_state');
  // 계속 진행...
}
```

---

#### Authorization Server 요구사항

**정확한 URI 검증:**

- ✅ 인증 서버는 **반드시(MUST)** 리디렉션 공격을 방지하기 위해 사전 등록된 값에 대해 정확한 redirect URI를 검증해야 함

**신뢰할 수 없는 URI 처리:**

- ✅ 인증 서버는 **반드시(MUST)** [OAuth 2.1 Section 7.12.2](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-v2-1-13#section-7.12.2)에 제시된 제안에 따라 사용자 에이전트를 신뢰할 수 없는 URI로 리디렉션하는 것을 방지하기 위한 예방 조치를 취해야 함

**권장 동작:**

- ✅ 인증 서버는 **권장(SHOULD)** 리디렉션 URI를 신뢰하는 경우에만 사용자 에이전트를 자동으로 리디렉션해야 함
- URI를 신뢰할 수 없는 경우, 인증 서버는 사용자에게 알리고 사용자가 올바른 결정을 내리도록 할 수 있음

---

### 6. Client ID Metadata Document Security

Client ID Metadata Documents를 구현할 때:

- ✅ 인증 서버는 **반드시(MUST)** [OAuth Client ID Metadata Document, Section 6](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-client-id-metadata-document-00#name-security-considerations)에 자세히 설명된 보안 영향을 고려해야 함

---

#### Authorization Server Abuse Protection

**위협:** 인증 서버는 알 수 없는 클라이언트로부터 URL을 입력으로 받아 해당 URL을 가져옵니다. 악의적인 클라이언트가 이를 사용하여 인증 서버가 임의의 URL(예: 인증 서버가 접근할 수 있는 개인 관리 엔드포인트에 대한 요청)에 대한 요청을 하도록 트리거할 수 있습니다.

**SSRF (Server-Side Request Forgery):** 메타데이터 문서를 가져오는 인증 서버는:

- ✅ **권장(SHOULD)** [OAuth Client ID Metadata Document: Server Side Request Forgery (SSRF) Attacks](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-client-id-metadata-document-00#name-server-side-request-forgery)에 설명된 대로 SSRF 위험을 고려해야 함

---

**SSRF 완화 조치:**

```typescript
// 1. URL 검증
function isValidMetadataUrl(url: string): boolean {
  const parsed = new URL(url);
  
  // HTTPS만 허용
  if (parsed.protocol !== 'https:') {
    return false;
  }
  
  // 내부 IP 차단
  const blockedIPs = [
    '127.0.0.1',
    'localhost',
    '169.254.169.254',  // AWS 메타데이터
    '::1'
  ];
  
  if (blockedIPs.includes(parsed.hostname)) {
    return false;
  }
  
  // 사설 IP 대역 차단
  if (isPrivateIP(parsed.hostname)) {
    return false;
  }
  
  return true;
}

// 2. 타임아웃 및 크기 제한
async function fetchMetadata(url: string) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 5000);
  
  try {
    const response = await fetch(url, {
      signal: controller.signal,
      redirect: 'manual',  // 리디렉션 따르지 않음
      headers: {
        'Accept': 'application/json'
      }
    });
    
    // 크기 제한 (예: 100KB)
    const MAX_SIZE = 100 * 1024;
    const contentLength = response.headers.get('content-length');
    if (contentLength && parseInt(contentLength) > MAX_SIZE) {
      throw new Error('Metadata document too large');
    }
    
    return await response.json();
  } finally {
    clearTimeout(timeout);
  }
}
```

---

#### Localhost Redirect URI Risks

**위협:** Client ID Metadata Documents 자체만으로는 `localhost` URL 사칭을 방지할 수 없습니다.

**공격 시나리오:**

1. 합법적인 클라이언트의 메타데이터 URL을 `client_id`로 제공
2. 임의의 `localhost` 포트에 바인딩하고 해당 주소를 redirect_uri로 제공
3. 사용자가 승인하면 리디렉션을 통해 인증 코드 수신

서버는 합법적인 클라이언트의 메타데이터 문서를 보고 사용자는 합법적인 클라이언트의 이름을 보게 되어 공격 탐지가 어렵습니다.

---

**완화 조치:**

**Authorization Server:**

- ✅ **권장(SHOULD)** `localhost` 전용 redirect URI에 대해 추가 경고를 표시해야 함
- ✅ **가능(MAY)** 보안 강화를 위해 추가 증명 메커니즘을 요구할 수 있음
- ✅ **반드시(MUST)** 인증 중에 redirect URI 호스트 이름을 명확히 표시해야 함

**사용자 인터페이스 예시:**

```
┌─────────────────────────────────────┐
│  권한 부여 요청                     │
├─────────────────────────────────────┤
│                                     │
│  Example MCP Client가                │
│  다음을 요청합니다:                  │
│                                     │
│  ✓ 파일 읽기                        │
│  ✓ 파일 쓰기                        │
│                                     │
│  ⚠️ 경고:                           │
│  이 앱은 localhost로 리디렉션합니다 │
│  Redirect: http://localhost:3000    │
│                                     │
│  [승인]  [거부]                     │
└─────────────────────────────────────┘
```

---

#### Trust Policies (신뢰 정책)

인증 서버는 **가능(MAY)** 도메인 기반 신뢰 정책을 구현할 수 있습니다:

**1. 신뢰할 수 있는 도메인 허용 목록:**

- 보호된 서버용
- 사전 승인된 도메인만 허용

```typescript
const trustedDomains = [
  'app.example.com',
  'client.example.com'
];

function isTrustedDomain(clientId: string): boolean {
  const url = new URL(clientId);
  return trustedDomains.includes(url.hostname);
}
```

---

**2. HTTPS client_id 수락:**

- 개방형 서버용
- 모든 HTTPS `client_id` 수락

```typescript
function acceptsAnyHTTPS(clientId: string): boolean {
  const url = new URL(clientId);
  return url.protocol === 'https:';
}
```

---

**3. 평판 확인:**

- 알 수 없는 도메인에 대한 평판 확인
- 도메인 연령 또는 인증서 검증에 따른 제한

```typescript
async function checkDomainReputation(domain: string): Promise<boolean> {
  // 도메인 연령 확인
  const domainAge = await getDomainAge(domain);
  if (domainAge < 30) {  // 30일 미만
    return false;
  }
  
  // SSL 인증서 확인
  const certValid = await validateSSLCert(domain);
  return certValid;
}
```

---

**4. 피싱 방지:**

- CIMD 및 기타 관련 클라이언트 호스트 이름을 눈에 띄게 표시하여 피싱 방지

```
인증 화면에 표시:
━━━━━━━━━━━━━━━━━━━━━━━
Client ID:
https://app.example.com/client.json

Redirect URI:
http://localhost:3000/callback

⚠️ 이 정보를 확인하세요
━━━━━━━━━━━━━━━━━━━━━━━
```

---

**서버 제어:** 서버는 접근 정책에 대한 완전한 제어권을 유지합니다.

---

### 7. Confused Deputy Problem (혼동된 대리인 문제)

**위협:** 공격자가 제3자 API의 중개자 역할을 하는 MCP 서버를 악용하여 혼동된 대리인 취약점을 야기할 수 있습니다.

**참조:** [Confused Deputy Problem](https://claude.ai/specification/2025-11-25/basic/security_best_practices#confused-deputy-problem) 상세 설명

---

**공격 시나리오:** 도용된 인증 코드를 사용하여 사용자 동의 없이 액세스 토큰을 얻을 수 있습니다.

**완화 조치:**

- ✅ 정적 클라이언트 ID를 사용하는 MCP 프록시 서버는 **반드시(MUST)** 제3자 인증 서버로 전달하기 전에 동적으로 등록된 각 클라이언트에 대해 사용자 동의를 얻어야 함 (추가 동의가 필요할 수 있음)

---

### 8. Access Token Privilege Restriction

**위협:** MCP 서버가 다른 리소스용으로 발급된 토큰을 수락하면 공격자가 무단 접근을 얻거나 MCP 서버를 손상시킬 수 있습니다.

---

**두 가지 중요한 차원:**

**1. Audience 검증 실패:** MCP 서버가 토큰이 특별히 자신을 위한 것인지 검증하지 않으면 (예: [RFC9068](https://www.rfc-editor.org/rfc/rfc9068.html)에 언급된 대로 audience 클레임을 통해), 원래 다른 서비스용으로 발급된 토큰을 수락할 수 있습니다. 이는 기본 OAuth 보안 경계를 깨뜨려 공격자가 의도된 것과 다른 서비스에서 합법적인 토큰을 재사용할 수 있게 합니다.

**2. Token Passthrough (토큰 통과):** MCP 서버가 잘못된 audience를 가진 토큰을 수락할 뿐만 아니라 이러한 수정되지 않은 토큰을 다운스트림 서비스로 전달하면 ["confused deputy" 문제](https://claude.ai/chat/d1892e31-8053-4913-8394-fadb47edcd3a#confused-deputy-problem)를 잠재적으로 야기할 수 있으며, 다운스트림 API가 토큰이 MCP 서버에서 온 것처럼 또는 업스트림 API가 토큰을 검증했다고 잘못 신뢰할 수 있습니다.

**참조:** 자세한 내용은 Security Best Practices 가이드의 [Token Passthrough 섹션](https://claude.ai/specification/2025-11-25/basic/security_best_practices#token-passthrough) 참조

---

**MCP 서버 요구사항:**

**1. 토큰 검증:**

- ✅ MCP 서버는 **반드시(MUST)** 요청을 처리하기 전에 액세스 토큰을 검증해야 함
- ✅ 액세스 토큰이 특별히 MCP 서버를 위해 발급되었는지 확인해야 함
- ✅ 무단 당사자에게 데이터가 반환되지 않도록 모든 필요한 조치를 취해야 함

**2. 표준 준수:**

- ✅ MCP 서버는 **반드시(MUST)** [OAuth 2.1 - Section 5.2](https://www.ietf.org/archive/id/draft-ietf-oauth-v2-1-13.html#section-5.2)의 지침을 따라 인바운드 토큰을 검증해야 함

**3. Audience 검증:**

- ✅ MCP 서버는 **반드시(MUST)** 자신을 위한 토큰만 수락해야 함
- ✅ audience 클레임에 자신을 포함하지 않거나 의도된 수신자임을 확인하지 않는 토큰은 **반드시(MUST)** 거부해야 함

**참조:** 자세한 내용은 [Security Best Practices Token Passthrough 섹션](https://claude.ai/specification/2025-11-25/basic/security_best_practices#token-passthrough) 참조

---

**업스트림 API 요청:**

- MCP 서버가 업스트림 API에 요청하는 경우, OAuth 클라이언트로서 그들에게 작동할 수 있음
- 업스트림 API에서 사용되는 액세스 토큰은 업스트림 인증 서버에서 발급한 별도의 토큰
- ✅ MCP 서버는 **절대(MUST NOT)** MCP 클라이언트로부터 받은 토큰을 통과해서는 안 됨

---

**MCP 클라이언트 요구사항:**

- ✅ MCP 클라이언트는 **반드시(MUST)** [RFC 8707 - Resource Indicators for OAuth 2.0](https://www.rfc-editor.org/rfc/rfc8707.html)에 정의된 대로 `resource` 매개변수를 구현하고 사용하여 토큰이 요청되는 대상 리소스를 명시적으로 지정해야 함
- 이 요구사항은 [RFC 9728 Section 7.4](https://datatracker.ietf.org/doc/html/rfc9728#section-7.4)의 권장사항과 일치함
- 액세스 토큰이 의도된 리소스에 바인딩되고 다른 서비스에서 오용될 수 없도록 보장

---

## MCP Authorization Extensions

### 개요

핵심 프로토콜에 대한 여러 인증 확장이 있으며, 이는 추가 인증 메커니즘을 정의합니다.

---

### 확장 특성

**1. Optional (선택 사항):**

- 구현은 이러한 확장을 채택할지 선택할 수 있음

**2. Additive (추가형):**

- 확장은 핵심 프로토콜 기능을 수정하거나 깨뜨리지 않음
- 핵심 프로토콜 동작을 보존하면서 새로운 기능 추가

**3. Composable (구성 가능):**

- 확장은 모듈식이며 충돌 없이 함께 작동하도록 설계됨
- 구현은 여러 확장을 동시에 채택할 수 있음

**4. Versioned Independently (독립적으로 버전 관리):**

- 확장은 핵심 MCP 버전 관리 주기를 따르지만 필요에 따라 독립적인 버전 관리를 채택할 수 있음

---

### 지원되는 확장

지원되는 확장 목록은 [MCP Authorization Extensions](https://github.com/modelcontextprotocol/ext-auth) 저장소에서 찾을 수 있습니다.

---

## 요약

### MCP Authorization 핵심 요소

**1. 역할:**

- MCP Server = OAuth 2.1 Resource Server
- MCP Client = OAuth 2.1 Client
- Authorization Server = 토큰 발행자

**2. 표준 기반:**

- OAuth 2.1 (필수)
- RFC 8414, RFC 9728 (필수)
- RFC 7591 (선택)
- Client ID Metadata Documents (권장)

**3. 클라이언트 등록 (3가지 방법):**

- Client ID Metadata Documents (권장)
- Pre-registration (우선순위 1)
- Dynamic Client Registration (폴백)

**4. 필수 보안 기능:**

- PKCE (필수)
- Resource Parameter (필수)
- HTTPS (필수)
- Audience Validation (필수)

**5. 토큰 사용:**

- Authorization 헤더만 사용
- 세션당 모든 요청에 포함
- URI 쿼리 문자열 금지

**6. 오류 처리:**

- 401: 인증 필요/토큰 무효
- 403: 범위 부족
- Step-Up Authorization Flow

**7. 주요 보안 위협 완화:**

- Token Theft (단기 토큰, 안전한 저장)
- Authorization Code Interception (PKCE)
- Open Redirection (정확한 URI 검증)
- SSRF (URL 검증, 크기 제한)
- Confused Deputy (사용자 동의, audience 검증)
- Token Passthrough (금지)

---

### 구현 체크리스트

#### Authorization Server

- [ ] OAuth 2.1 구현
- [ ] Protected Resource Metadata 제공 (RFC 9728)
- [ ] Authorization Server Metadata 제공 (RFC 8414 또는 OIDC)
- [ ] Client ID Metadata Documents 지원 (권장)
- [ ] PKCE 지원 및 메타데이터에 표시
- [ ] Resource Indicators 지원 (RFC 8707)
- [ ] 단기 액세스 토큰 발행
- [ ] HTTPS 엔드포인트
- [ ] Redirect URI 정확한 검증
- [ ] SSRF 방어

#### MCP Server

- [ ] OAuth 2.1 Resource Server로 작동
- [ ] Protected Resource Metadata 제공
- [ ] WWW-Authenticate 헤더 제공 (401/403)
- [ ] 토큰 검증 구현
- [ ] Audience 검증 구현
- [ ] 토큰 통과 금지
- [ ] HTTPS 사용

#### MCP Client

- [ ] OAuth 2.1 Client로 작동
- [ ] Protected Resource Metadata 검색
- [ ] Authorization Server Discovery
- [ ] Client ID Metadata Documents 지원 (권장)
- [ ] PKCE 구현 (S256)
- [ ] Resource Parameter 사용
- [ ] Authorization 헤더 사용
- [ ] State 매개변수 사용 및 검증
- [ ] 안전한 토큰 저장
- [ ] Step-Up Authorization Flow
- [ ] Localhost 또는 HTTPS redirect URI만 사용

---

### 참조 링크

**핵심 사양:**

- OAuth 2.1: https://datatracker.ietf.org/doc/html/draft-ietf-oauth-v2-1-13
- RFC 8414: https://datatracker.ietf.org/doc/html/rfc8414
- RFC 9728: https://datatracker.ietf.org/doc/html/rfc9728
- RFC 8707: https://www.rfc-editor.org/rfc/rfc8707.html
- RFC 7591: https://datatracker.ietf.org/doc/html/rfc7591

**Client ID Metadata:**

- Draft: https://datatracker.ietf.org/doc/html/draft-ietf-oauth-client-id-metadata-document-00

**MCP 리소스:**

- Security Best Practices: /specification/2025-11-25/basic/security_best_practices
- Extensions: https://github.com/modelcontextprotocol/ext-auth

---

MCP Authorization은 OAuth 2.1을 기반으로 안전하고 표준화된 인증 프레임워크를 제공하여 MCP 생태계 전반에 걸쳐 신뢰할 수 있는 클라이언트-서버 통신을 가능하게 합니다!

---

_이 문서는 Model Context Protocol 공식 Authorization 사양에서 가져온 내용입니다._