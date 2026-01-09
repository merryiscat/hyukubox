# MCP 보안 모범 사례 (Security Best Practices) - Part 1

## 프로토콜 개정판

**현재 버전**: 2025-11-25

---

## 소개 (Introduction)

### 목적 및 범위 (Purpose and Scope)

이 문서는 [MCP Authorization](https://claude.ai/basic/authorization.mdx) 사양을 보완하는 Model Context Protocol (MCP)에 대한 보안 고려사항을 제공합니다.

**다루는 내용:**

- MCP 구현에 특정한 보안 위험
- 공격 벡터
- 모범 사례

**주요 대상:**

- MCP 인증 흐름을 구현하는 개발자
- MCP 서버 운영자
- MCP 기반 시스템을 평가하는 보안 전문가

**권장 독서 순서:**

1. 이 문서
2. MCP Authorization 사양
3. [OAuth 2.0 보안 모범 사례](https://datatracker.ietf.org/doc/html/rfc9700)

---

## 공격 및 완화 (Attacks and Mitigations)

이 섹션에서는 MCP 구현에 대한 공격을 잠재적 대응책과 함께 자세히 설명합니다.

---

## 1. Confused Deputy Problem (혼동된 대리인 문제)

### 개요

**위협:** 공격자가 제3자 API에 연결하는 MCP 프록시 서버를 악용하여 "[confused deputy](https://en.wikipedia.org/wiki/Confused_deputy_problem)" 취약점을 생성할 수 있습니다.

**공격 방식:** 이 공격은 악의적인 클라이언트가 정적 클라이언트 ID, 동적 클라이언트 등록 및 동의 쿠키의 조합을 악용하여 적절한 사용자 동의 없이 인증 코드를 얻을 수 있도록 허용합니다.

---

### 용어 정의 (Terminology)

**MCP Proxy Server (MCP 프록시 서버)**

- MCP 클라이언트를 제3자 API에 연결하는 MCP 서버
- MCP 기능을 제공하면서 작업을 위임
- 제3자 API 서버에 대한 단일 OAuth 클라이언트로 작동

**Third-Party Authorization Server (제3자 인증 서버)**

- 제3자 API를 보호하는 인증 서버
- 동적 클라이언트 등록 지원이 부족할 수 있음
- 모든 요청에 대해 MCP 프록시가 정적 클라이언트 ID를 사용하도록 요구

**Third-Party API (제3자 API)**

- 실제 API 기능을 제공하는 보호된 리소스 서버
- 이 API에 접근하려면 제3자 인증 서버에서 발급한 토큰이 필요

**Static Client ID (정적 클라이언트 ID)**

- MCP 프록시 서버가 제3자 인증 서버와 통신할 때 사용하는 고정 OAuth 2.0 클라이언트 식별자
- 이 Client ID는 제3자 API에 대한 클라이언트로 작동하는 MCP 서버를 나타냄
- 어떤 MCP 클라이언트가 요청을 시작했는지에 관계없이 모든 MCP 서버와 제3자 API 상호작용에 대해 동일한 값

---

### 취약한 조건 (Vulnerable Conditions)

이 공격은 다음 조건이 **모두** 존재할 때 가능합니다:

**1. 정적 클라이언트 ID 사용**

- ✅ MCP 프록시 서버가 제3자 인증 서버에서 **정적 클라이언트 ID**를 사용

**2. 동적 클라이언트 등록 허용**

- ✅ MCP 프록시 서버가 MCP 클라이언트의 **동적 등록**을 허용 (각각 자체 client_id 획득)

**3. 동의 쿠키 설정**

- ✅ 제3자 인증 서버가 첫 번째 인증 후 **동의 쿠키**를 설정

**4. 클라이언트별 동의 부재**

- ✅ MCP 프록시 서버가 제3자 인증으로 전달하기 전에 적절한 클라이언트별 동의를 구현하지 않음

---

### 아키텍처 및 공격 흐름

#### 정상적인 OAuth 프록시 사용 (사용자 동의 보존)

```
사용자                    MCP Client          MCP Proxy          3rd Party
 │                           │                   Server            Auth
 │                           │                      │                │
 │  1. Access Request        │                      │                │
 ├──────────────────────────►│                      │                │
 │                           │                      │                │
 │                           │  2. Auth Request     │                │
 │                           ├─────────────────────►│                │
 │                           │                      │                │
 │  3. MCP Consent Screen    │                      │                │
 │  (Approve Client A?)      │                      │                │
 │◄──────────────────────────┼──────────────────────┤                │
 │                           │                      │                │
 │  4. User Approves         │                      │                │
 ├──────────────────────────►│                      │                │
 │                           │                      │                │
 │                           │  5. Forward to 3rd   │                │
 │                           │     Party Auth       │                │
 │◄──────────────────────────┼──────────────────────┼───────────────►│
 │                           │                      │                │
 │  6. 3rd Party Consent     │                      │                │
 │     (First Time)          │                      │                │
 │◄──────────────────────────┼──────────────────────┼────────────────┤
 │                           │                      │                │
 │  7. User Approves         │                      │                │
 │     + Cookie Set          │                      │                │
 ├──────────────────────────►│                      │                │
 │                           │                      │                │
 │  8. Auth Code             │                      │                │
 │◄──────────────────────────┼──────────────────────┼────────────────┤
 │                           │                      │                │
 │                           │  9. Access Granted   │                │
 │◄──────────────────────────┤                      │                │
```

**보호 요소:**

- MCP 레벨 동의 확인
- 클라이언트별 승인 추적
- 안전한 토큰 전달

---

#### 악의적인 OAuth 프록시 사용 (사용자 동의 건너뛰기)

```
공격자                  피해자              MCP Proxy          3rd Party
 │                        │                   Server            Auth
 │                        │                      │                │
 │  1. Craft Malicious    │                      │                │
 │     Auth Link          │                      │                │
 │     (New client_id +   │                      │                │
 │      malicious         │                      │                │
 │      redirect_uri)     │                      │                │
 │                        │                      │                │
 │  2. Send Link to       │                      │                │
 │     Victim             │                      │                │
 ├───────────────────────►│                      │                │
 │                        │                      │                │
 │                        │  3. Click Link       │                │
 │                        │     (Has consent     │                │
 │                        │      cookie from     │                │
 │                        │      previous auth)  │                │
 │                        ├─────────────────────►│                │
 │                        │                      │                │
 │                        │  4. Forward to 3rd   │                │
 │                        │     Party Auth       │                │
 │                        │     (Static client_  │                │
 │                        │      id + cookie)    │                │
 │                        ├──────────────────────┼───────────────►│
 │                        │                      │                │
 │                        │  5. Cookie Detected  │                │
 │                        │     → Skip Consent!  │                │
 │                        │                      │                │
 │                        │  6. Auth Code        │                │
 │                        │     (to attacker's   │                │
 │                        │      redirect_uri)   │                │
 │◄───────────────────────┼──────────────────────┼────────────────┤
 │                        │                      │                │
 │  7. Exchange Code      │                      │                │
 │     for Token          │                      │                │
 ├────────────────────────┼─────────────────────►│                │
 │                        │                      │                │
 │  8. Access Granted     │                      │                │
 │     (Victim's Data!)   │                      │                │
 │◄───────────────────────┤                      │                │
```

**공격 성공 요인:**

- ❌ MCP 레벨 동의 확인 없음
- ❌ 동의 쿠키가 정적 client_id에 바인딩됨
- ❌ 새 client_id에 대한 재동의 요구 없음
- ❌ Redirect URI 검증 부족

---

### 공격 설명 (Attack Description)

MCP 프록시 서버가 제3자 인증 서버와 인증하기 위해 정적 클라이언트 ID를 사용할 때 다음 공격이 가능해집니다:

**단계별 공격 시나리오:**

**1단계: 정상 인증**

- 사용자가 MCP 프록시 서버를 통해 정상적으로 인증하여 제3자 API에 접근
- 이 흐름 중에 제3자 인증 서버가 사용자 에이전트에 정적 클라이언트 ID에 대한 동의를 나타내는 쿠키를 설정

**2단계: 공격 준비**

- 공격자가 나중에 사용자에게 조작된 인증 요청이 포함된 악의적인 링크를 전송
- 링크에는 악의적인 redirect URI와 새로운 동적으로 등록된 클라이언트 ID가 포함됨

**3단계: 동의 건너뛰기**

- 사용자가 링크를 클릭하면 브라우저에 이전 합법적인 요청의 동의 쿠키가 여전히 있음
- 제3자 인증 서버가 쿠키를 감지하고 동의 화면을 건너뜀

**4단계: 코드 탈취**

- MCP 인증 코드가 공격자의 서버로 리디렉션됨 ([동적 클라이언트 등록](https://claude.ai/specification/2025-11-25/basic/authorization#dynamic-client-registration) 중 악의적인 `redirect_uri` 매개변수에 지정됨)

**5단계: 토큰 획득**

- 공격자가 도용된 인증 코드를 사용자의 명시적 승인 없이 MCP 서버의 액세스 토큰으로 교환

**6단계: 무단 접근**

- 공격자가 이제 손상된 사용자로서 제3자 API에 접근할 수 있음

---

### 완화 (Mitigation)

혼동된 대리인 공격을 방지하기 위해:

- ✅ MCP 프록시 서버는 **반드시(MUST)** 클라이언트별 동의 및 적절한 보안 제어를 구현해야 함

---

#### 동의 흐름 구현

다음 다이어그램은 제3자 인증 흐름 **이전에** 실행되는 클라이언트별 동의를 적절히 구현하는 방법을 보여줍니다:

```
사용자                MCP Client          MCP Proxy          3rd Party
 │                       │                   Server            Auth
 │                       │                      │                │
 │  1. Request Access    │                      │                │
 ├──────────────────────►│                      │                │
 │                       │                      │                │
 │                       │  2. Auth Request     │                │
 │                       ├─────────────────────►│                │
 │                       │                      │                │
 │                       │  3. Check Consent    │                │
 │                       │     Registry         │                │
 │                       │     (client_id       │                │
 │                       │      approved?)      │                │
 │                       │                      │                │
 │  4. MCP Consent       │                      │                │
 │     Screen            │                      │                │
 │     ┌──────────────┐  │                      │                │
 │     │ Consent for: │  │                      │                │
 │     │ Client: X    │  │                      │                │
 │     │ Scopes: Y    │  │                      │                │
 │     │ Redirect: Z  │  │                      │                │
 │     │ [Approve]    │  │                      │                │
 │     └──────────────┘  │                      │                │
 │◄──────────────────────┼──────────────────────┤                │
 │                       │                      │                │
 │  5. User Approves     │                      │                │
 ├──────────────────────►│                      │                │
 │                       │                      │                │
 │                       │  6. Store Consent    │                │
 │                       │     (client_id +     │                │
 │                       │      user_id)        │                │
 │                       │                      │                │
 │                       │  7. Forward to 3rd   │                │
 │                       │     Party Auth       │                │
 │◄──────────────────────┼──────────────────────┼───────────────►│
 │                       │                      │                │
 │  8. 3rd Party Flow    │                      │                │
 │     (Standard OAuth)  │                      │                │
 │◄─────────────────────►│                      │                │
```

---

#### 필수 보호 조치 (Required Protections)

### 1. 클라이언트별 동의 저장

**MCP 프록시 서버는 반드시(MUST):**

**동의 레지스트리 유지:**

```typescript
// 동의 저장 구조 예시
interface ConsentRegistry {
  userId: string;
  approvedClients: {
    clientId: string;
    approvedAt: Date;
    scopes: string[];
    redirectUri: string;
  }[];
}

// 동의 확인
async function checkConsent(userId: string, clientId: string): Promise<boolean> {
  const registry = await getConsentRegistry(userId);
  return registry.approvedClients.some(
    client => client.clientId === clientId
  );
}
```

**제3자 인증 흐름 시작 전 확인:**

```typescript
async function initiateAuth(userId: string, clientId: string, redirectUri: string) {
  // 1. 동의 확인
  const hasConsent = await checkConsent(userId, clientId);
  
  if (!hasConsent) {
    // 2. MCP 동의 화면 표시
    return showMCPConsentScreen(userId, clientId, redirectUri);
  }
  
  // 3. 동의가 있으면 제3자 인증으로 진행
  return forwardToThirdPartyAuth(userId, clientId);
}
```

**안전한 저장:**

- 서버 측 데이터베이스
- 또는 서버 특정 쿠키 사용

---

### 2. 동의 UI 요구사항

**MCP 레벨 동의 페이지는 반드시(MUST):**

**클라이언트 식별:**

```html
<div class="consent-screen">
  <h2>Authorization Request</h2>
  
  <!-- 명확한 클라이언트 식별 -->
  <p><strong>Client:</strong> Example MCP Client</p>
  <p><strong>Client ID:</strong> https://app.example.com/client.json</p>
  
  <!-- 특정 범위 표시 -->
  <h3>Requested Permissions:</h3>
  <ul>
    <li>Read files</li>
    <li>Write files</li>
    <li>Access user profile</li>
  </ul>
  
  <!-- Redirect URI 표시 -->
  <p><strong>Redirect URI:</strong> https://app.example.com/callback</p>
  
  <!-- CSRF 보호 -->
  <input type="hidden" name="csrf_token" value="abc123...">
  
  <button onclick="approve()">Approve</button>
  <button onclick="deny()">Deny</button>
</div>
```

**CSRF 보호 구현:**

```typescript
// CSRF 토큰 생성
function generateCSRFToken(): string {
  return crypto.randomBytes(32).toString('hex');
}

// 검증
function validateCSRFToken(token: string, sessionToken: string): boolean {
  return crypto.timingSafeEqual(
    Buffer.from(token),
    Buffer.from(sessionToken)
  );
}
```

**클릭재킹 방지:**

```http
# CSP 헤더
Content-Security-Policy: frame-ancestors 'none'

# 또는 X-Frame-Options
X-Frame-Options: DENY
```

---

### 3. 동의 쿠키 보안

쿠키를 사용하여 동의 결정을 추적하는 경우, 반드시(MUST):

**안전한 쿠키 속성:**

```http
Set-Cookie: __Host-mcp-consent-client123=approved; 
            Secure; 
            HttpOnly; 
            SameSite=Lax; 
            Path=/; 
            Max-Age=86400
```

**쿠키 이름 규칙:**

- ✅ `__Host-` 접두사 사용
- 이유: 프로토콜 및 도메인 바인딩 강화

**필수 속성:**

- ✅ `Secure`: HTTPS만
- ✅ `HttpOnly`: JavaScript 접근 차단
- ✅ `SameSite=Lax`: CSRF 완화

**암호화 서명:**

```typescript
// 서명된 쿠키 생성
function createSignedCookie(clientId: string, userId: string): string {
  const data = `${clientId}:${userId}`;
  const signature = crypto
    .createHmac('sha256', SECRET_KEY)
    .update(data)
    .digest('hex');
  
  return `${data}.${signature}`;
}

// 검증
function verifySignedCookie(cookie: string): boolean {
  const [data, signature] = cookie.split('.');
  const expectedSignature = crypto
    .createHmac('sha256', SECRET_KEY)
    .update(data)
    .digest('hex');
  
  return crypto.timingSafeEqual(
    Buffer.from(signature),
    Buffer.from(expectedSignature)
  );
}
```

**특정 client_id에 바인딩:**

```typescript
// ❌ 잘못된 예시 - 일반 동의
Set-Cookie: consent=true

// ✅ 올바른 예시 - client_id 특정
Set-Cookie: __Host-consent-client-abc123=true
```

---

### 4. Redirect URI 검증

**MCP 프록시 서버는 반드시(MUST):**

**정확한 일치 검증:**

```typescript
function validateRedirectURI(
  requestedURI: string,
  registeredURI: string
): boolean {
  // 정확한 문자열 일치 (패턴 매칭 아님)
  return requestedURI === registeredURI;
}

// ❌ 잘못된 예시 - 패턴 매칭
function badValidation(requested: string, registered: string): boolean {
  return requested.startsWith(registered); // 위험!
}
```

**등록된 URI와 일치 확인:**

```typescript
async function authorizeRequest(clientId: string, redirectUri: string) {
  const client = await getRegisteredClient(clientId);
  
  if (!client.redirectUris.includes(redirectUri)) {
    throw new Error('Invalid redirect_uri');
  }
  
  // 진행...
}
```

**변경 시 재등록 요구:**

```typescript
async function updateRedirectURI(
  clientId: string,
  newRedirectUri: string
) {
  // 1. 기존 동의 무효화
  await revokeAllConsents(clientId);
  
  // 2. 새 URI 등록
  await updateClient(clientId, {
    redirectUris: [newRedirectUri]
  });
  
  // 3. 재동의 요구
  return { requiresNewConsent: true };
}
```

---

### 5. OAuth State 매개변수 검증

**중요성:** OAuth `state` 매개변수는 인증 코드 가로채기 및 CSRF 공격을 방지하는 데 중요합니다. 적절한 state 검증은 인증 엔드포인트에서의 동의 승인이 콜백 엔드포인트에서 시행되도록 보장합니다.

---

**OAuth 흐름을 구현하는 MCP 프록시 서버는 반드시(MUST):**

**1. State 값 생성:**

```typescript
// 암호학적으로 안전한 랜덤 state 생성
function generateState(): string {
  return crypto.randomBytes(32).toString('hex');
}
```

**2. State 값 저장 (동의 승인 후에만):**

```typescript
async function handleConsentApproval(userId: string, clientId: string) {
  // 1. 사용자가 동의 승인
  await storeConsent(userId, clientId);
  
  // 2. State 생성
  const state = generateState();
  
  // 3. State 저장 (서버 측 세션 또는 암호화된 쿠키)
  await storeState(userId, state, {
    clientId,
    expiresAt: Date.now() + 10 * 60 * 1000 // 10분
  });
  
  // 4. 제3자 IdP로 리디렉션 (동의 승인 직후)
  return redirectToThirdParty({
    state,
    clientId,
    // ...
  });
}
```

**3. State 추적 쿠키/세션 설정 (동의 승인 직전):**

```typescript
// ❌ 잘못된 예시 - 동의 전 설정
app.get('/authorize', (req, res) => {
  const state = generateState();
  res.cookie('oauth_state', state); // 너무 이름!
  res.render('consent-screen');
});

// ✅ 올바른 예시 - 동의 후 설정
app.post('/consent-approve', (req, res) => {
  const state = generateState();
  res.cookie('oauth_state', state, {
    httpOnly: true,
    secure: true,
    sameSite: 'lax',
    maxAge: 10 * 60 * 1000
  });
  
  // 즉시 제3자로 리디렉션
  res.redirect(buildThirdPartyAuthUrl({ state }));
});
```

**4. 콜백에서 State 검증:**

```typescript
app.get('/callback', async (req, res) => {
  const { state: receivedState, code } = req.query;
  
  // 1. State 존재 확인
  if (!receivedState) {
    return res.status(400).send('Missing state parameter');
  }
  
  // 2. 저장된 State와 비교
  const storedState = req.cookies.oauth_state;
  
  if (receivedState !== storedState) {
    return res.status(400).send('State mismatch - possible CSRF attack');
  }
  
  // 3. State 삭제 (단일 사용)
  res.clearCookie('oauth_state');
  
  // 4. 코드 교환 진행
  const tokens = await exchangeCode(code);
  // ...
});
```

**5. State 거부 처리:**

```typescript
// 누락되거나 일치하지 않는 state는 거부
if (!state || state !== storedState) {
  throw new Error('Invalid state parameter');
}
```

**6. 단일 사용 및 만료:**

```typescript
// State는 단일 사용
await deleteState(userId, state);

// State는 짧은 만료 시간 (예: 10분)
const stateData = {
  value: state,
  expiresAt: Date.now() + 10 * 60 * 1000
};
```

---

**중요:** 동의 쿠키 또는 `state` 값을 포함하는 세션은 **절대(MUST NOT)** MCP 서버의 인증 엔드포인트에서 사용자가 동의 화면을 승인하기 **전에** 설정되어서는 안 됩니다. 동의 승인 전에 이 쿠키를 설정하면 공격자가 악의적인 인증 요청을 조작하여 동의 화면을 우회할 수 있으므로 동의 화면이 무효화됩니다.

---

## 2. Token Passthrough (토큰 통과)

### 개요

**정의:** "Token passthrough"는 MCP 서버가 토큰이 _MCP 서버를 위해_ 적절히 발급되었는지 검증하지 않고 MCP 클라이언트로부터 토큰을 수락하고 다운스트림 API로 통과시키는 안티패턴입니다.

**금지:** 토큰 통과는 [인증 사양](https://claude.ai/specification/2025-11-25/basic/authorization)에서 명시적으로 금지되어 있습니다.

---

### 위험 (Risks)

토큰 통과는 여러 보안 위험을 야기합니다:

#### 1. 보안 제어 우회

**문제:** MCP 서버 또는 다운스트림 API가 다음과 같은 중요한 보안 제어를 구현할 수 있습니다:

- 속도 제한
- 요청 검증
- 트래픽 모니터링

이러한 제어는 토큰 audience 또는 기타 자격 증명 제약에 의존합니다.

**위험:** 클라이언트가 MCP 서버가 적절히 검증하지 않거나 토큰이 올바른 서비스를 위해 발급되었는지 확인하지 않고 다운스트림 API에서 직접 토큰을 얻고 사용할 수 있으면 이러한 제어를 우회합니다.

**예시:**

```typescript
// ❌ 잘못된 예시 - 토큰 통과
app.get('/api/data', async (req, res) => {
  const token = req.headers.authorization;
  
  // 토큰 검증 없이 다운스트림으로 전달
  const response = await fetch('https://downstream-api.com/data', {
    headers: {
      'Authorization': token  // 위험!
    }
  });
  
  res.json(await response.json());
});

// ✅ 올바른 예시 - 토큰 검증 및 새 토큰 획득
app.get('/api/data', async (req, res) => {
  const token = req.headers.authorization;
  
  // 1. 토큰이 MCP 서버를 위한 것인지 검증
  const validated = await validateToken(token, {
    expectedAudience: 'https://mcp-server.example.com'
  });
  
  if (!validated) {
    return res.status(401).send('Invalid token');
  }
  
  // 2. 다운스트림 API를 위한 새 토큰 획득
  const downstreamToken = await getDownstreamToken(validated.userId);
  
  // 3. 새 토큰으로 다운스트림 호출
  const response = await fetch('https://downstream-api.com/data', {
    headers: {
      'Authorization': `Bearer ${downstreamToken}`
    }
  });
  
  res.json(await response.json());
});
```

---

#### 2. 책임 및 감사 추적 문제

**MCP 서버 문제:**

- MCP 서버가 MCP 클라이언트를 식별하거나 구별할 수 없음
- 업스트림 발급 액세스 토큰(MCP 서버에 불투명할 수 있음)으로 클라이언트가 호출할 때

**다운스트림 리소스 서버 로그:**

- 요청이 다른 소스에서 온 것처럼 보일 수 있음
- 실제로 토큰을 전달하는 MCP 서버가 아닌 다른 ID로 표시

**영향:**

- 사고 조사 어려움
- 제어 및 감사 복잡
- MCP 서버가 토큰의 클레임(예: 역할, 권한 또는 audience) 또는 기타 메타데이터를 검증하지 않고 토큰을 통과하면, 도용된 토큰을 소유한 악의적인 행위자가 서버를 데이터 유출의 프록시로 사용할 수 있음

---

#### 3. 신뢰 경계 문제

**다운스트림 신뢰:**

- 다운스트림 리소스 서버는 특정 엔터티에 신뢰를 부여
- 이 신뢰에는 출처 또는 클라이언트 동작 패턴에 대한 가정이 포함될 수 있음

**위험:**

- 이 신뢰 경계를 깨면 예기치 않은 문제가 발생할 수 있음
- 토큰이 적절한 검증 없이 여러 서비스에서 수락되면, 하나의 서비스를 손상시킨 공격자가 토큰을 사용하여 다른 연결된 서비스에 접근할 수 있음

**예시:**

```
Service A (손상됨) → 토큰 도용
    ↓
MCP Server (토큰 통과)
    ↓
Service B (의도하지 않은 접근)
```

---

#### 4. 향후 호환성 위험

**현재:**

- MCP 서버가 오늘날 "순수 프록시"로 시작할 수 있음

**미래:**

- 나중에 보안 제어를 추가해야 할 수 있음
- 적절한 토큰 audience 분리로 시작하면 보안 모델을 발전시키기가 더 쉬움

---

### 완화 (Mitigation)

**필수 요구사항:**

- ✅ MCP 서버는 **절대(MUST NOT)** MCP 서버를 위해 명시적으로 발급되지 않은 토큰을 수락해서는 안 됨

**올바른 구현:**

```typescript
// 1. 토큰 검증
async function validateInboundToken(token: string) {
  const decoded = await verifyJWT(token);
  
  // Audience 확인
  if (decoded.aud !== 'https://mcp-server.example.com') {
    throw new Error('Invalid token audience');
  }
  
  return decoded;
}

// 2. 다운스트림 토큰 획득
async function getDownstreamToken(userId: string) {
  // 다운스트림 Auth Server에서 새 토큰 요청
  const response = await fetch('https://downstream-auth.com/token', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    body: new URLSearchParams({
      grant_type: 'client_credentials',
      scope: 'downstream-api',
      // MCP 서버의 자격 증명
      client_id: MCP_SERVER_CLIENT_ID,
      client_secret: MCP_SERVER_CLIENT_SECRET
    })
  });
  
  const { access_token } = await response.json();
  return access_token;
}

// 3. API 엔드포인트
app.get('/api/resource', async (req, res) => {
  // 인바운드 토큰 검증
  const validated = await validateInboundToken(
    req.headers.authorization?.replace('Bearer ', '')
  );
  
  // 다운스트림용 새 토큰 획득
  const downstreamToken = await getDownstreamToken(validated.sub);
  
  // 새 토큰으로 다운스트림 호출
  const data = await callDownstreamAPI(downstreamToken);
  
  res.json(data);
});
```

---

계속해서 Part 2를 생성하겠습니다...