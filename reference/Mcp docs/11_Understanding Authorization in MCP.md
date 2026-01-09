# MCP에서 인증(Authorization) 이해하기

## 개요

OAuth 2.1을 사용하여 MCP 서버에 대한 안전한 인증을 구현하여 민감한 리소스와 작업을 보호하는 방법을 학습합니다.

Model Context Protocol (MCP)의 인증은 MCP 서버가 노출하는 민감한 리소스와 작업에 대한 접근을 보호합니다. MCP 서버가 사용자 데이터나 관리 작업을 처리하는 경우, 인증은 허가된 사용자만 해당 엔드포인트에 접근할 수 있도록 보장합니다.

MCP는 MCP 클라이언트와 MCP 서버 간의 신뢰를 구축하기 위해 표준화된 인증 흐름을 사용합니다. 이 설계는 특정 인증 또는 ID 시스템에 초점을 맞추지 않고 [OAuth 2.1](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-v2-1-13)에 대해 설명된 규칙을 따릅니다.

자세한 내용은 [인증 사양](https://claude.ai/specification/latest/basic/authorization)을 참조하세요.

---

## 인증을 사용해야 하는 경우

MCP 서버에 대한 인증은 **선택 사항**이지만, 다음과 같은 경우 강력히 권장됩니다:

### 필수 사용 사례

✅ **사용자별 데이터 접근**

- 이메일, 문서, 데이터베이스 등 사용자 특정 데이터에 접근하는 경우

✅ **감사(Audit) 요구사항**

- 누가 어떤 작업을 수행했는지 추적해야 하는 경우

✅ **API 접근 제어**

- 사용자 동의가 필요한 API에 대한 접근을 제공하는 경우

✅ **엔터프라이즈 환경**

- 엄격한 접근 제어가 있는 엔터프라이즈 환경을 위해 구축하는 경우

✅ **사용 추적**

- 사용자별 속도 제한 또는 사용 추적을 구현하려는 경우

---

### 로컬 MCP 서버에 대한 인증

[STDIO 전송](https://claude.ai/specification/latest/basic/transports#stdio)을 사용하는 MCP 서버의 경우 대안이 있습니다:

**대안:**

- 환경 기반 자격 증명 사용
- MCP 서버에 직접 포함된 타사 라이브러리가 제공하는 자격 증명

**이유:**

- STDIO 기반 MCP 서버는 로컬에서 실행되므로 브라우저 내 인증 및 권한 부여 흐름에 의존하지 않는 다양한 옵션을 사용할 수 있음

**OAuth 흐름:**

- HTTP 기반 전송을 위해 설계됨
- MCP 서버가 원격 호스팅되는 경우
- 클라이언트가 OAuth를 사용하여 사용자가 원격 서버에 접근할 권한이 있는지 확인

---

## 인증 흐름: 단계별 설명

클라이언트가 보호된 MCP 서버에 연결하려고 할 때 발생하는 과정을 살펴보겠습니다.

---

### 1단계: 초기 핸드셰이크

MCP 클라이언트가 처음 연결을 시도하면, 서버는 `401 Unauthorized`로 응답하고 인증 정보를 찾을 위치를 알려줍니다.

**서버 응답:**

```http
HTTP/1.1 401 Unauthorized
WWW-Authenticate: Bearer realm="mcp",
  resource_metadata="https://your-server.com/.well-known/oauth-protected-resource"
```

**의미:**

- MCP 서버에 인증이 필요함
- 인증 흐름을 시작하는 데 필요한 정보를 얻을 위치

**Protected Resource Metadata (PRM) 문서:**

- [RFC 9728](https://datatracker.ietf.org/doc/html/rfc9728)에 정의
- MCP 서버에 의해 호스팅됨
- 예측 가능한 경로 패턴을 따름
- `WWW-Authenticate` 헤더 내 `resource_metadata` 매개변수로 제공됨

---

### 2단계: Protected Resource Metadata Discovery

클라이언트는 PRM 문서에 대한 URI 포인터를 사용하여 메타데이터를 가져와 권한 부여 서버, 지원되는 범위 및 기타 리소스 정보에 대해 학습합니다.

**PRM 문서 예시:**

```json
{
  "resource": "https://your-server.com/mcp",
  "authorization_servers": ["https://auth.your-server.com"],
  "scopes_supported": ["mcp:tools", "mcp:resources"]
}
```

**포함 정보:**

- `resource`: 보호된 리소스의 URI
- `authorization_servers`: 인증 서버 목록
- `scopes_supported`: 지원되는 OAuth 범위

더 포괄적인 예는 [RFC 9728 Section 3.2](https://datatracker.ietf.org/doc/html/rfc9728#name-protected-resource-metadata-r)를 참조하세요.

---

### 3단계: Authorization Server Discovery

클라이언트는 인증 서버의 메타데이터를 가져와 기능을 파악합니다.

**프로세스:**

1. **인증 서버 선택**
    
    - PRM 문서가 여러 인증 서버를 나열하면 클라이언트가 사용할 서버 결정
2. **메타데이터 URI 구성**
    
    - 표준 메타데이터 URI 구성
3. **메타데이터 요청**
    
    - [OpenID Connect (OIDC) Discovery](https://openid.net/specs/openid-connect-discovery-1_0.html) 또는
    - [OAuth 2.0 Auth Server Metadata](https://datatracker.ietf.org/doc/html/rfc8414) 엔드포인트에 요청

**메타데이터 응답 예시:**

```json
{
  "issuer": "https://auth.your-server.com",
  "authorization_endpoint": "https://auth.your-server.com/authorize",
  "token_endpoint": "https://auth.your-server.com/token",
  "registration_endpoint": "https://auth.your-server.com/register"
}
```

**주요 엔드포인트:**

- `issuer`: 인증 서버의 고유 식별자
- `authorization_endpoint`: 사용자 인증 엔드포인트
- `token_endpoint`: 토큰 교환 엔드포인트
- `registration_endpoint`: 클라이언트 등록 엔드포인트

---

### 4단계: Client Registration

클라이언트는 인증 서버에 등록되어 있는지 확인해야 합니다. 두 가지 방법이 있습니다:

#### 방법 1: 사전 등록 (Pre-registration)

**특징:**

- 클라이언트가 특정 인증 서버에 미리 등록됨
- 포함된 클라이언트 등록 정보를 사용하여 인증 흐름 완료

**장점:**

- 간단하고 빠름
- 추가 네트워크 요청 불필요

#### 방법 2: Dynamic Client Registration (DCR)

**요구사항:**

- 인증 서버가 DCR을 지원해야 함

**프로세스:**

1. 클라이언트가 `registration_endpoint`에 정보와 함께 요청 전송

**등록 요청 예시:**

```json
{
  "client_name": "My MCP Client",
  "redirect_uris": ["http://localhost:3000/callback"],
  "grant_types": ["authorization_code", "refresh_token"],
  "response_types": ["code"]
}
```

**성공 시:**

- 인증 서버가 클라이언트 등록 정보가 포함된 JSON 반환

---

#### DCR 또는 사전 등록이 없는 경우

**시나리오:**

- MCP 클라이언트가 DCR을 지원하지 않는 인증 서버를 사용하는 MCP 서버에 연결
- 클라이언트가 해당 인증 서버에 사전 등록되지 않음

**해결 방법:**

- 클라이언트 개발자가 최종 사용자가 클라이언트 정보를 수동으로 입력할 수 있는 인터페이스 제공

---

### 5단계: User Authorization

클라이언트는 사용자가 로그인하고 필요한 권한을 부여할 수 있는 `/authorize` 엔드포인트로 브라우저를 열어야 합니다.

**프로세스:**

1. **브라우저 리디렉션**
    
    - 인증 엔드포인트로 이동
    - 사용자 로그인 및 권한 부여
2. **인증 코드 수신**
    
    - 인증 서버가 인증 코드와 함께 클라이언트로 리디렉션
3. **토큰 교환**
    
    - 클라이언트가 인증 코드를 토큰으로 교환

**토큰 응답 예시:**

```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIs...",
  "refresh_token": "def502...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

**토큰 유형:**

- `access_token`: MCP 서버에 대한 요청을 인증하는 데 사용
- `refresh_token`: 액세스 토큰 갱신에 사용
- `expires_in`: 토큰 만료 시간 (초)

**표준:**

- [OAuth 2.1 authorization code with PKCE](https://oauth.net/2/grant-types/authorization-code/) 규칙을 따름

---

### 6단계: Making Authenticated Requests

클라이언트는 이제 `Authorization` 헤더에 포함된 액세스 토큰을 사용하여 MCP 서버에 요청할 수 있습니다.

**요청 예시:**

```http
GET /mcp HTTP/1.1
Host: your-server.com
Authorization: Bearer eyJhbGciOiJSUzI1NiIs...
```

**서버 동작:**

1. 토큰 검증
2. 필요한 권한이 있는지 확인
3. 유효하면 요청 처리

---

## 구현 예제

실제 구현을 시작하기 위해 Docker 컨테이너에 호스팅된 [Keycloak](https://www.keycloak.org/) 인증 서버를 사용합니다.

**Keycloak이란?**

- 오픈 소스 인증 서버
- 테스트 및 실험을 위해 로컬에 쉽게 배포 가능

**사전 요구사항:**

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) 다운로드 및 설치

---

## Keycloak 설정

### 1. Keycloak 컨테이너 시작

터미널에서 다음 명령을 실행합니다:

```bash
docker run -p 127.0.0.1:8080:8080 \
  -e KC_BOOTSTRAP_ADMIN_USERNAME=admin \
  -e KC_BOOTSTRAP_ADMIN_PASSWORD=admin \
  quay.io/keycloak/keycloak start-dev
```

**명령 설명:**

- Keycloak 컨테이너 이미지를 로컬로 가져옴
- 기본 구성을 부트스트랩
- 포트 `8080`에서 실행
- `admin` 사용자 및 `admin` 비밀번호 설정

**액세스:**

- 브라우저에서 `http://localhost:8080` 접속

> **⚠️ 프로덕션 주의사항**: 위 구성은 테스트 및 실험에만 적합합니다. 프로덕션 환경에서는 절대 사용하지 마세요. [Keycloak 프로덕션 구성 가이드](https://www.keycloak.org/server/configuration-production)를 참조하세요.

---

### 2. OIDC 구성 확인

기본 구성으로 실행할 때 Keycloak은 Dynamic Client Registration을 포함하여 MCP 서버에 필요한 많은 기능을 이미 지원합니다.

**확인 방법:**

```
http://localhost:8080/realms/master/.well-known/openid-configuration
```

---

### 3. 범위(Scope) 설정

#### Client Scopes 생성

1. Keycloak 대시보드에서 **Client scopes** 이동
2. 새 `mcp:tools` 범위 생성
3. MCP 서버의 모든 도구에 액세스하는 데 사용

**구성:**

- **Type**: Default로 설정
- **Include in token scope**: 스위치 활성화 (토큰 검증에 필요)

---

### 4. Audience 설정

**Audience란?**

- 토큰의 의도된 대상을 나타냄
- MCP 서버가 토큰이 실제로 자신을 위한 것인지 확인하는 데 도움
- 토큰 통과 시나리오 방지에 중요

**설정 방법:**

1. `mcp:tools` 클라이언트 범위 열기
2. **Mappers** 클릭 → **Configure a new mapper** → **Audience** 선택
3. 구성:
    - **Name**: `audience-config`
    - **Included Custom Audience**: `http://localhost:3000`

> **⚠️ 프로덕션 주의사항**: 위 audience 구성은 테스트용입니다. 프로덕션에서는 클라이언트에서 전달된 resource 매개변수를 기반으로 audience를 설정해야 합니다.

---

### 5. Trusted Hosts 설정

#### 목적

- 동적 클라이언트 등록을 위한 신뢰할 수 있는 호스트 지정

#### 설정 방법

1. **Clients** → **Client registration** → **Trusted Hosts** 이동
2. **Client URIs Must Match** 설정 비활성화
3. 테스트 중인 호스트 추가

**호스트 IP 확인:**

- Linux/macOS: `ifconfig` 명령
- Windows: `ipconfig` 명령
- Keycloak 로그에서 확인: `Failed to verify remote host : 192.168.215.1`

> **팁**: Docker 컨테이너에서 Keycloak을 실행하는 경우 컨테이너 로그의 터미널에서도 호스트 IP를 볼 수 있습니다.

---

### 6. MCP 서버용 클라이언트 생성

**목적:**

- MCP 서버 자체가 Keycloak과 통신할 수 있도록 함
- [토큰 검증(token introspection)](https://oauth.net/2/token-introspection/) 등에 사용

**생성 방법:**

1. **Clients** 이동
2. **Create client** 클릭
3. 고유한 **Client ID** 부여 → **Next**
4. **Client authentication** 활성화 → **Next**
5. **Save** 클릭

**Client Secret 확인:**

1. 클라이언트 세부 정보 열기
2. **Credentials** 탭
3. **Client Secret** 메모

> **🔐 보안**: 클라이언트 자격 증명을 코드에 직접 포함하지 마세요. 환경 변수 또는 전문 비밀 저장소 솔루션을 사용하는 것이 좋습니다.

---

### 7. 토큰 예시

**인증 흐름이 트리거될 때마다 MCP 서버가 받는 토큰:**

```
eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICI1TjcxMGw1WW5MWk13WGZ1VlJKWGtCS3ZZMzZzb3JnRG5scmlyZ2tlTHlzIn0.eyJleHAiOjE3NTU1NDA4MTcsImlhdCI6MTc1NTU0MDc1NywiYXV0aF90aW1lIjoxNzU1NTM4ODg4LCJqdGkiOiJvbnJ0YWM6YjM0MDgwZmYtODQwNC02ODY3LTgxYmUtMTIzMWI1MDU5M2E4IiwiaXNzIjoiaHR0cDovL2xvY2FsaG9zdDo4MDgwL3JlYWxtcy9tYXN0ZXIiLCJhdWQiOiJodHRwOi8vbG9jYWxob3N0OjMwMDAiLCJzdWIiOiIzM2VkNmM2Yi1jNmUwLTQ5MjgtYTE2MS1mMmY2OWM3YTAzYjkiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiI3OTc1YTViNi04YjU5LTRhODUtOWNiYS04ZmFlYmRhYjg5NzQiLCJzaWQiOiI4ZjdlYzI3Ni0zNThmLTRjY2MtYjMxMy1kYjA4MjkwZjM3NmYiLCJzY29wZSI6Im1jcDp0b29scyJ9.P5xCRtXORly0R0EXjyqRCUx-z3J4uAOWNAvYtLPXroykZuVCCJ-K1haiQSwbURqfsVOMbL7jiV-sD6miuPzI1tmKOkN_Yct0Vp-azvj7U5rEj7U6tvPfMkg2Uj_jrIX0KOskyU2pVvGZ-5BgqaSvwTEdsGu_V3_E0xDuSBq2uj_wmhqiyTFm5lJ1WkM3Hnxxx1_AAnTj7iOKMFZ4VCwMmk8hhSC7clnDauORc0sutxiJuYUZzxNiNPkmNeQtMCGqWdP1igcbWbrfnNXhJ6NswBOuRbh97_QraET3hl-CNmyS6C72Xc0aOwR_uJ7xVSBTD02OaQ1JA6kjCATz30kGYg
```

**디코딩된 토큰:**

```json
{
  "alg": "RS256",
  "typ": "JWT",
  "kid": "5N710l5YnLZMwXfuVRJXkBKvY36sorgDnlrirgkeLys"
}.{
  "exp": 1755540817,
  "iat": 1755540757,
  "auth_time": 1755538888,
  "jti": "onrtac:b34080ff-8404-6867-81be-1231b50593a8",
  "iss": "http://localhost:8080/realms/master",
  "aud": "http://localhost:3000",
  "sub": "33ed6c6b-c6e0-4928-a161-f2f69c7a03b9",
  "typ": "Bearer",
  "azp": "7975a5b6-8b59-4a85-9cba-8faebdab8974",
  "sid": "8f7ec276-358f-4ccc-b313-db08290f376f",
  "scope": "mcp:tools"
}.[Signature]
```

**주목할 점:**

- `aud` 클레임이 토큰에 포함됨
- 현재 테스트 MCP 서버의 URI로 설정됨
- 이전에 구성한 scope에서 추론됨
- 구현에서 검증하는 데 중요

---

## MCP 서버 설정

이제 로컬에서 실행 중인 Keycloak 인증 서버를 사용하도록 MCP 서버를 설정합니다.

프로그래밍 언어 선호도에 따라 지원되는 [MCP SDK](https://claude.ai/docs/sdk) 중 하나를 사용할 수 있습니다.

**테스트 서버 개요:**

- 두 가지 도구를 노출하는 간단한 MCP 서버
    - **add**: 덧셈 도구
    - **multiply**: 곱셈 도구
- 이러한 도구에 액세스하려면 인증이 필요

---

### TypeScript 구현

**완성된 프로젝트:** [GitHub 샘플 저장소](https://github.com/localden/min-ts-mcp-auth)

#### 환경 변수 설정

`.env` 파일 생성:

```bash
# Server host/port
HOST=localhost
PORT=3000

# Auth server location
AUTH_HOST=localhost
AUTH_PORT=8080
AUTH_REALM=master

# Keycloak OAuth client credentials
OAUTH_CLIENT_ID=<YOUR_SERVER_CLIENT_ID>
OAUTH_CLIENT_SECRET=<YOUR_SERVER_CLIENT_SECRET>
```

**설명:**

- `OAUTH_CLIENT_ID`, `OAUTH_CLIENT_SECRET`: 이전에 생성한 MCP 서버 클라이언트와 연결됨

**구현 특징:**

- MCP 인증 사양 구현
- Keycloak을 통한 토큰 검증
- 기본 로깅으로 문제 진단 용이

**자세한 내용:**

- [TypeScript SDK 문서](https://github.com/modelcontextprotocol/typescript-sdk)
- [완성된 코드](https://github.com/localden/min-ts-mcp-auth)

---

### Python 구현

**완성된 프로젝트:** [GitHub 샘플 저장소](https://github.com/localden/min-py-mcp-auth)

**특징:**

- [FastMCP](https://gofastmcp.com/getting-started/welcome) 사용으로 인증 통합 간소화
- 엔드포인트 및 토큰 검증 로직이 언어 간 일관성 유지
- 프로덕션 시나리오에서 더 간단한 통합 방법 제공

**자세한 내용:**

- [Python SDK 문서](https://github.com/modelcontextprotocol/python-sdk)
- [완성된 코드](https://github.com/localden/min-py-mcp-auth)

---

### C# 구현

**완성된 프로젝트:** [GitHub 샘플 저장소](https://github.com/localden/min-cs-mcp-auth)

**특징:**

- 표준 ASP.NET Core builder 패턴 사용
- Keycloak 검증 엔드포인트 대신 ASP.NET Core의 내장 기능 사용
- JWT 토큰 검증

**자세한 내용:**

- [C# SDK 문서](https://github.com/modelcontextprotocol/csharp-sdk)
- [완성된 코드](https://github.com/localden/min-cs-mcp-auth)

---

## MCP 서버 테스트

### Visual Studio Code 사용

테스트 목적으로 [Visual Studio Code](https://code.visualstudio.com/)를 사용하지만, MCP 및 새로운 인증 사양을 지원하는 모든 클라이언트가 적합합니다.

#### 1. 서버 추가

1. `Cmd` + `Shift` + `P` 누르기
2. **MCP: Add server…** 선택
3. **HTTP** 선택
4. `http://localhost:3000` 입력
5. Visual Studio Code 내에서 사용할 고유한 이름 제공

**`mcp.json`에 추가된 항목:**

```json
"my-mcp-server-18676652": {
  "url": "http://localhost:3000",
  "type": "http"
}
```

#### 2. 인증 프로세스

**연결 시:**

1. 브라우저로 이동
2. Visual Studio Code가 `mcp:tools` 범위에 액세스할 수 있도록 동의하라는 메시지 표시
3. 동의 후 도구가 `mcp.json`의 서버 항목 바로 위에 나열됨

#### 3. 도구 사용

**도구 호출 방법:**

- 채팅 뷰에서 `#` 기호를 사용하여 개별 도구 호출

**예시:**

```
#add 5 3
#multiply 4 7
```

---

## 일반적인 함정 및 회피 방법

포괄적인 보안 지침, 공격 벡터, 완화 전략 및 구현 모범 사례는 [보안 모범 사례](https://claude.ai/specification/draft/basic/security_best_practices)를 참조하세요.

### 🚨 중요 보안 고려사항

#### 1. 직접 구현하지 마세요

**하지 말아야 할 것:**

- ❌ 토큰 검증 또는 인증 로직을 직접 구현

**해야 할 것:**

- ✅ 잘 테스트되고 안전한 기성 라이브러리 사용
- ✅ 보안 전문가가 아니라면 처음부터 모든 것을 구현하지 말 것

---

#### 2. 짧은 수명의 액세스 토큰 사용

**권장사항:**

- ✅ 짧은 수명의 토큰 사용
- ✅ 인증 서버 설정에서 토큰 수명 구성

**이유:**

- 악의적인 행위자가 토큰을 탈취해도 장기간 액세스 유지 불가

---

#### 3. 항상 토큰 검증

**검증 항목:**

- ✅ 토큰이 유효한지
- ✅ 토큰이 서버를 위한 것인지
- ✅ 필요한 제약 조건과 일치하는지

**하지 말아야 할 것:**

- ❌ 토큰을 받았다고 해서 유효하다고 가정

---

#### 4. 안전한 저장소에 토큰 저장

**서버 측 토큰 캐싱 시:**

- ✅ 적절한 액세스 제어가 있는 저장소 사용
- ✅ 암호화된 저장소 사용
- ✅ 강력한 캐시 제거 정책 구현

**방지 사항:**

- ❌ 악의적인 당사자의 쉬운 탈취
- ❌ 만료되거나 무효한 토큰 재사용

---

#### 5. 프로덕션에서 HTTPS 강제

**규칙:**

- ✅ 프로덕션에서 HTTPS만 사용
- ✅ 개발 중 `localhost`에 대해서만 HTTP 허용

**거부 사항:**

- ❌ 일반 HTTP를 통한 토큰 또는 리디렉션 콜백

---

#### 6. 최소 권한 범위

**원칙:**

- ✅ 포괄적인 범위 사용 금지
- ✅ 도구 또는 기능별로 액세스 분할
- ✅ 리소스 서버의 경로/도구당 필요한 범위 확인

---

#### 7. 자격 증명 로깅 금지

**절대 로깅하지 말 것:**

- ❌ `Authorization` 헤더
- ❌ 토큰, 코드, 비밀
- ❌ 쿼리 문자열 및 헤더

**해야 할 것:**

- ✅ 민감한 필드 삭제
- ✅ 구조화된 로그에서 민감한 필드 수정

---

#### 8. 앱 vs 리소스 서버 자격 증명 분리

**분리 사항:**

- ❌ 최종 사용자 흐름에 MCP 서버의 클라이언트 비밀 재사용 금지
- ✅ 모든 비밀을 적절한 비밀 관리자에 저장
- ❌ 소스 제어에 비밀 저장 금지

---

#### 9. 적절한 인증 챌린지 반환

**401 응답 시:**

```http
WWW-Authenticate: Bearer realm="mcp", resource_metadata="..."
```

**포함 사항:**

- `Bearer`
- `realm`
- `resource_metadata`

**목적:**

- 클라이언트가 인증 방법을 검색할 수 있도록 함

---

#### 10. DCR (Dynamic Client Registration) 제어

**인식 사항:**

- 조직별 제약 조건 (신뢰할 수 있는 호스트, 필수 심사, 감사된 등록)
- 인증되지 않은 DCR = 누구나 인증 서버에 클라이언트 등록 가능

---

#### 11. 다중 테넌트/영역 혼동

**규칙:**

- ✅ 명시적으로 다중 테넌트가 아니면 단일 발급자/테넌트에 고정
- ❌ 동일한 인증 서버가 서명했더라도 다른 영역의 토큰 거부

---

#### 12. Audience/Resource 표시기 오용

**금지 사항:**

- ❌ 일반 audience (예: `api`) 구성 또는 수락
- ❌ 관련 없는 리소스 수락

**요구 사항:**

- ✅ audience/resource가 구성된 서버와 일치해야 함

---

#### 13. 오류 세부 정보 유출

**클라이언트에:**

- ✅ 일반 메시지 반환

**내부적으로:**

- ✅ 상관 관계 ID와 함께 자세한 이유 로깅
- ✅ 내부 정보 노출 없이 문제 해결 지원

---

#### 14. 세션 식별자 강화

**`Mcp-Session-Id` 처리:**

- ✅ 신뢰할 수 없는 입력으로 취급
- ❌ 인증과 연결하지 말 것
- ✅ 인증 변경 시 재생성
- ✅ 서버 측에서 수명 주기 검증

---

## 관련 표준 및 문서

MCP 인증은 다음과 같은 잘 확립된 표준을 기반으로 합니다:

### 핵심 표준

1. **[OAuth 2.1](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-v2-1-13)**
    
    - 핵심 인증 프레임워크
2. **[RFC 8414](https://datatracker.ietf.org/doc/html/rfc8414)**
    
    - Authorization Server Metadata 검색
3. **[RFC 7591](https://datatracker.ietf.org/doc/html/rfc7591)**
    
    - Dynamic Client Registration
4. **[RFC 9728](https://datatracker.ietf.org/doc/html/rfc9728)**
    
    - Protected Resource Metadata
5. **[RFC 8707](https://datatracker.ietf.org/doc/html/rfc8707)**
    
    - Resource Indicators

---

### 추가 리소스

- **[인증 사양](https://claude.ai/specification/draft/basic/authorization)**
    
    - MCP 특정 인증 세부 정보
- **[보안 모범 사례](https://claude.ai/specification/draft/basic/security_best_practices)**
    
    - 포괄적인 보안 지침
- **[사용 가능한 MCP SDK](https://claude.ai/docs/sdk)**
    
    - 언어별 구현 가이드

**이점:**

- 이러한 표준을 이해하면 인증을 올바르게 구현하고 문제가 발생했을 때 해결하는 데 도움이 됩니다.

---

## 요약

MCP에서 인증을 구현하는 것은 OAuth 2.1 표준을 따르는 체계적인 프로세스입니다.

### 핵심 단계

1. ✅ **초기 핸드셰이크**: 401 응답으로 인증 필요성 전달
2. ✅ **메타데이터 검색**: PRM 및 인증 서버 메타데이터 가져오기
3. ✅ **클라이언트 등록**: 사전 등록 또는 DCR 사용
4. ✅ **사용자 인증**: OAuth 2.1 authorization code flow
5. ✅ **토큰 검증**: 모든 요청에서 토큰 확인
6. ✅ **보안 모범 사례**: 짧은 수명 토큰, HTTPS, 최소 권한

### 구현 옵션

- **TypeScript**: 표준 MCP SDK + Keycloak 검증
- **Python**: FastMCP + 간소화된 통합
- **C#**: ASP.NET Core + 내장 JWT 검증

### 보안 체크리스트

- [ ] 잘 테스트된 라이브러리 사용
- [ ] 짧은 수명의 액세스 토큰
- [ ] 모든 토큰 검증
- [ ] 프로덕션에서 HTTPS 강제
- [ ] 최소 권한 범위
- [ ] 자격 증명 로깅 금지
- [ ] 적절한 오류 처리
- [ ] 세션 식별자 보안

이제 OAuth 2.1을 사용하여 안전한 MCP 서버를 구축할 준비가 되었습니다!

---

## 추가 리소스

- **Keycloak 문서**: https://www.keycloak.org/documentation
- **OAuth 2.1**: https://oauth.net/2.1/
- **MCP 사양**: https://modelcontextprotocol.io/specification
- **샘플 코드**:
    - [TypeScript](https://github.com/localden/min-ts-mcp-auth)
    - [Python](https://github.com/localden/min-py-mcp-auth)
    - [C#](https://github.com/localden/min-cs-mcp-auth)

---

_이 문서는 Model Context Protocol 공식 문서에서 가져온 내용입니다._