# MCP 인증 (Authorization) - Part 1

## 프로토콜 개정판

**현재 버전**: 2025-11-25

---

## 소개 (Introduction)

### 목적 및 범위 (Purpose and Scope)

Model Context Protocol은 전송 계층에서 인증 기능을 제공하여 MCP 클라이언트가 리소스 소유자를 대신하여 제한된 MCP 서버에 요청을 할 수 있도록 합니다.

**이 사양의 정의:** HTTP 기반 전송을 위한 인증 흐름

**적용 범위:**

- MCP 서버: OAuth 2.1 리소스 서버
- MCP 클라이언트: OAuth 2.1 클라이언트
- 인증 서버: 토큰 발행 담당

---

### 프로토콜 요구사항 (Protocol Requirements)

**선택 사항:**

- ✅ 인증은 MCP 구현에서 **선택(OPTIONAL)** 사항

**지원되는 경우:**

**HTTP 기반 전송:**

- ✅ **권장(SHOULD)** 이 사양을 준수해야 함

**STDIO 전송:**

- ❌ **권장하지 않음(SHOULD NOT)** 이 사양을 따르지 않아야 함
- ✅ 대신 환경에서 자격 증명을 검색해야 함

**대체 전송:**

- ✅ **반드시(MUST)** 해당 프로토콜에 대한 확립된 보안 모범 사례를 따라야 함

---

### 표준 준수 (Standards Compliance)

이 인증 메커니즘은 아래 나열된 확립된 사양을 기반으로 하지만, 보안과 상호 운용성을 보장하면서 단순성을 유지하기 위해 선택된 기능의 하위 집합을 구현합니다:

**기반 표준:**

|표준|참조|설명|
|---|---|---|
|OAuth 2.1|[draft-ietf-oauth-v2-1-13](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-v2-1-13)|핵심 인증 프로토콜|
|OAuth 2.0 Authorization Server Metadata|[RFC8414](https://datatracker.ietf.org/doc/html/rfc8414)|인증 서버 메타데이터|
|OAuth 2.0 Dynamic Client Registration|[RFC7591](https://datatracker.ietf.org/doc/html/rfc7591)|동적 클라이언트 등록|
|OAuth 2.0 Protected Resource Metadata|[RFC9728](https://datatracker.ietf.org/doc/html/rfc9728)|보호된 리소스 메타데이터|
|OAuth Client ID Metadata Documents|[draft-ietf-oauth-client-id-metadata-document-00](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-client-id-metadata-document-00)|클라이언트 ID 메타데이터 문서|

---

## 역할 (Roles)

### OAuth 2.1 역할 매핑

```
┌─────────────────────────────────────────┐
│         OAuth 2.1 생태계                │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────────────────────────────┐  │
│  │   Authorization Server           │  │
│  │   (인증 서버)                    │  │
│  │   - 사용자 인증                  │  │
│  │   - 토큰 발행                    │  │
│  └──────────────────────────────────┘  │
│           ▲                             │
│           │ 토큰 요청                   │
│           │                             │
│  ┌────────┴─────────┐                  │
│  │                  │                  │
│  │  MCP Client      │                  │
│  │  (OAuth 2.1      │                  │
│  │   Client)        │                  │
│  │                  │                  │
│  └──────────────────┘                  │
│           │                             │
│           │ 토큰 사용                   │
│           ▼                             │
│  ┌──────────────────┐                  │
│  │  MCP Server      │                  │
│  │  (OAuth 2.1      │                  │
│  │   Resource       │                  │
│  │   Server)        │                  │
│  └──────────────────┘                  │
└─────────────────────────────────────────┘
```

---

### 1. MCP Server (리소스 서버)

**정의:** 보호된 _MCP 서버_는 [OAuth 2.1 리소스 서버](https://www.ietf.org/archive/id/draft-ietf-oauth-v2-1-13.html#name-roles) 역할을 수행합니다.

**역할:**

- ✅ 액세스 토큰을 사용하여 보호된 리소스 요청 수락
- ✅ 토큰 검증
- ✅ 보호된 리소스에 대한 응답 제공

**예시:**

```http
GET /mcp HTTP/1.1
Host: mcp.example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

---

### 2. MCP Client (클라이언트)

**정의:** _MCP 클라이언트_는 [OAuth 2.1 클라이언트](https://www.ietf.org/archive/id/draft-ietf-oauth-v2-1-13.html#name-roles) 역할을 수행합니다.

**역할:**

- ✅ 리소스 소유자를 대신하여 보호된 리소스 요청 수행
- ✅ 인증 흐름 관리
- ✅ 토큰 저장 및 사용

**책임:**

- 사용자 인증 시작
- 액세스 토큰 획득
- 토큰으로 보호된 요청 수행

---

### 3. Authorization Server (인증 서버)

**정의:** _인증 서버_는 사용자와 상호작용(필요한 경우)하고 MCP 서버에서 사용할 액세스 토큰을 발행하는 역할을 담당합니다.

**역할:**

- ✅ 사용자 인증
- ✅ 사용자 동의 획득
- ✅ 액세스 토큰 발행
- ✅ 토큰 검증 지원

**구현:**

- 인증 서버의 구현 세부사항은 이 사양의 범위를 벗어남
- 리소스 서버와 함께 호스팅되거나 별도 엔터티일 수 있음
- [Authorization Server Discovery](https://claude.ai/chat/d1892e31-8053-4913-8394-fadb47edcd3a#authorization-server-discovery) 섹션에서 MCP 서버가 해당 인증 서버의 위치를 클라이언트에 알리는 방법 지정

---

## 개요 (Overview)

### 필수 요구사항 요약

**1. 인증 서버:**

- ✅ **반드시(MUST)** 기밀 클라이언트와 공개 클라이언트 모두에 대해 적절한 보안 조치와 함께 OAuth 2.1을 구현해야 함

**2. Client ID Metadata Documents (권장):**

- ✅ 인증 서버 및 MCP 클라이언트는 **권장(SHOULD)** OAuth Client ID Metadata Documents를 지원해야 함
    - [draft-ietf-oauth-client-id-metadata-document-00](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-client-id-metadata-document-00)

**3. Dynamic Client Registration (선택):**

- ✅ 인증 서버 및 MCP 클라이언트는 **가능(MAY)** OAuth 2.0 Dynamic Client Registration Protocol을 지원할 수 있음
    - [RFC7591](https://datatracker.ietf.org/doc/html/rfc7591)

**4. Protected Resource Metadata:**

- ✅ MCP 서버는 **반드시(MUST)** OAuth 2.0 Protected Resource Metadata를 구현해야 함
    - [RFC9728](https://datatracker.ietf.org/doc/html/rfc9728)
- ✅ MCP 클라이언트는 **반드시(MUST)** 인증 서버 검색을 위해 OAuth 2.0 Protected Resource Metadata를 사용해야 함

**5. Authorization Server Discovery:**

- ✅ MCP 인증 서버는 **반드시(MUST)** 다음 검색 메커니즘 중 하나 이상을 제공해야 함:
    - OAuth 2.0 Authorization Server Metadata ([RFC8414](https://datatracker.ietf.org/doc/html/rfc8414))
    - [OpenID Connect Discovery 1.0](https://openid.net/specs/openid-connect-discovery-1_0.html)
- ✅ MCP 클라이언트는 **반드시(MUST)** 인증 서버와 상호작용하는 데 필요한 정보를 얻기 위해 두 검색 메커니즘을 모두 지원해야 함

---

## Authorization Server Discovery (인증 서버 검색)

### 개요

이 섹션에서는 MCP 서버가 관련 인증 서버를 MCP 클라이언트에 알리는 메커니즘과 MCP 클라이언트가 인증 서버 엔드포인트 및 지원되는 기능을 결정할 수 있는 검색 프로세스를 설명합니다.

---

### Authorization Server Location (인증 서버 위치)

**필수 구현:**

- ✅ MCP 서버는 **반드시(MUST)** OAuth 2.0 Protected Resource Metadata ([RFC9728](https://datatracker.ietf.org/doc/html/rfc9728)) 사양을 구현하여 인증 서버의 위치를 나타내야 함

**메타데이터 요구사항:**

- ✅ MCP 서버가 반환하는 Protected Resource Metadata 문서는 **반드시(MUST)** 하나 이상의 인증 서버를 포함하는 `authorization_servers` 필드를 포함해야 함

**메타데이터 예시:**

```json
{
  "resource": "https://mcp.example.com",
  "authorization_servers": [
    "https://auth.example.com"
  ],
  "scopes_supported": [
    "files:read",
    "files:write"
  ]
}
```

---

**다중 인증 서버:** Protected Resource Metadata 문서는 여러 인증 서버를 정의할 수 있습니다.

**클라이언트 책임:** 사용할 인증 서버를 선택하는 책임은 MCP 클라이언트에 있으며, [RFC9728 Section 7.6 "Authorization Servers"](https://datatracker.ietf.org/doc/html/rfc9728#name-authorization-servers)에 지정된 가이드라인을 따릅니다.

**여러 인증 서버 예시:**

```json
{
  "resource": "https://mcp.example.com",
  "authorization_servers": [
    "https://auth1.example.com",
    "https://auth2.example.com"
  ]
}
```

---

### Protected Resource Metadata Discovery Requirements

MCP 서버는 **반드시(MUST)** MCP 클라이언트에 인증 서버 위치 정보를 제공하기 위해 다음 검색 메커니즘 중 하나를 구현해야 합니다:

#### 메커니즘 1: WWW-Authenticate 헤더

**구현:**

- `401 Unauthorized` 응답을 반환할 때 `WWW-Authenticate` HTTP 헤더에 `resource_metadata` 아래에 리소스 메타데이터 URL 포함
- [RFC9728 Section 5.1](https://datatracker.ietf.org/doc/html/rfc9728#name-www-authenticate-response)에 설명된 대로

**예시:**

```http
HTTP/1.1 401 Unauthorized
WWW-Authenticate: Bearer resource_metadata="https://mcp.example.com/.well-known/oauth-protected-resource"
```

---

#### 메커니즘 2: Well-Known URI

**구현:** [RFC9728](https://datatracker.ietf.org/doc/html/rfc9728)에 지정된 대로 well-known URI에서 메타데이터 제공

**옵션 A: MCP 엔드포인트 경로에서**

```
서버 엔드포인트: https://example.com/public/mcp
메타데이터 위치: https://example.com/.well-known/oauth-protected-resource/public/mcp
```

**옵션 B: 루트에서**

```
메타데이터 위치: https://example.com/.well-known/oauth-protected-resource
```

---

**클라이언트 요구사항:**

- ✅ MCP 클라이언트는 **반드시(MUST)** 두 검색 메커니즘을 모두 지원해야 함
- ✅ 파싱된 `WWW-Authenticate` 헤더의 리소스 메타데이터 URL이 있으면 사용해야 함
- ✅ 그렇지 않으면 **반드시(MUST)** 위에 나열된 순서대로 well-known URI를 구성하고 요청해야 함

---

### Scope 매개변수 (권장)

**권장사항:**

- ✅ MCP 서버는 **권장(SHOULD)** [RFC 6750 Section 3](https://datatracker.ietf.org/doc/html/rfc6750#section-3)에 정의된 대로 `WWW-Authenticate` 헤더에 `scope` 매개변수를 포함하여 리소스에 접근하는 데 필요한 범위를 나타내야 함

**목적:**

- 권한 부여 중에 요청할 적절한 범위에 대한 즉각적인 지침 제공
- 최소 권한 원칙 준수
- 클라이언트가 과도한 권한을 요청하는 것 방지

**예시:**

```http
HTTP/1.1 401 Unauthorized
WWW-Authenticate: Bearer resource_metadata="https://mcp.example.com/.well-known/oauth-protected-resource",
                         scope="files:read"
```

---

**Scope 관계:** 챌린지에 포함된 범위는:

- `scopes_supported`와 일치할 수 있음
- 하위 집합일 수 있음
- 상위 집합일 수 있음
- 엄격한 하위 집합도 상위 집합도 아닌 대체 컬렉션일 수 있음

**클라이언트 규칙:**

- ❌ 클라이언트는 **절대(MUST NOT)** 챌린지된 범위 집합과 `scopes_supported` 사이에 특정 집합 관계를 가정해서는 안 됨
- ✅ 클라이언트는 **반드시(MUST)** 챌린지에 제공된 범위를 현재 요청을 충족하기 위한 권위 있는 것으로 취급해야 함

**서버 권장사항:**

- ✅ 서버는 **권장(SHOULD)** 범위 집합을 구성하는 방법에서 일관성을 위해 노력해야 함
- 그러나 `scopes_supported`를 통해 모든 동적으로 발행된 범위를 표시할 필요는 없음

---

**Scope 부재 시:**

- ✅ `scope` 매개변수가 없으면, 클라이언트는 **권장(SHOULD)** [Scope Selection Strategy](https://claude.ai/chat/d1892e31-8053-4913-8394-fadb47edcd3a#scope-selection-strategy) 섹션에 정의된 폴백 동작을 적용해야 함

---

**클라이언트 파싱 요구사항:**

- ✅ MCP 클라이언트는 **반드시(MUST)** `WWW-Authenticate` 헤더를 파싱할 수 있어야 함
- ✅ MCP 서버의 `HTTP 401 Unauthorized` 응답에 적절히 응답할 수 있어야 함

---

### Authorization Server Metadata Discovery

다양한 발급자 URL 형식을 처리하고 OAuth 2.0 Authorization Server Metadata 및 OpenID Connect Discovery 1.0 사양 모두와의 상호 운용성을 보장하기 위해:

**필수 요구사항:**

- ✅ MCP 클라이언트는 **반드시(MUST)** 인증 서버 메타데이터를 검색할 때 여러 well-known 엔드포인트를 시도해야 함

---

**기반:**

- [RFC8414 Section 3.1 "Authorization Server Metadata Request"](https://datatracker.ietf.org/doc/html/rfc8414#section-3.1) - OAuth 2.0 Authorization Server Metadata 검색
- [RFC8414 Section 5 "Compatibility Notes"](https://datatracker.ietf.org/doc/html/rfc8414#section-5) - OpenID Connect Discovery 1.0 상호 운용성

---

#### 경로 구성 요소가 있는 발급자 URL

**예시:** `https://auth.example.com/tenant1`

**시도 순서:**

1. **OAuth 2.0 경로 삽입:**
    
    ```
    https://auth.example.com/.well-known/oauth-authorization-server/tenant1
    ```
    
2. **OpenID Connect 경로 삽입:**
    
    ```
    https://auth.example.com/.well-known/openid-configuration/tenant1
    ```
    
3. **OpenID Connect 경로 추가:**
    
    ```
    https://auth.example.com/tenant1/.well-known/openid-configuration
    ```
    

---

#### 경로 구성 요소가 없는 발급자 URL

**예시:** `https://auth.example.com`

**시도 순서:**

1. **OAuth 2.0 Authorization Server Metadata:**
    
    ```
    https://auth.example.com/.well-known/oauth-authorization-server
    ```
    
2. **OpenID Connect Discovery 1.0:**
    
    ```
    https://auth.example.com/.well-known/openid-configuration
    ```
    

---

### Authorization Server Discovery Sequence Diagram

**검색 흐름 예시:**

```
클라이언트                    MCP Server              Auth Server
   │                             │                        │
   │  GET /mcp                   │                        │
   ├────────────────────────────►│                        │
   │                             │                        │
   │  401 Unauthorized           │                        │
   │  WWW-Authenticate: Bearer   │                        │
   │    resource_metadata=...    │                        │
   │◄────────────────────────────┤                        │
   │                             │                        │
   │  GET /.well-known/          │                        │
   │      oauth-protected-       │                        │
   │      resource               │                        │
   ├────────────────────────────►│                        │
   │                             │                        │
   │  Protected Resource         │                        │
   │  Metadata                   │                        │
   │  {                          │                        │
   │    "authorization_servers": │                        │
   │    ["https://auth..."]      │                        │
   │  }                          │                        │
   │◄────────────────────────────┤                        │
   │                             │                        │
   │  GET /.well-known/          │                        │
   │      oauth-authorization-   │                        │
   │      server                 │                        │
   ├─────────────────────────────┼───────────────────────►│
   │                             │                        │
   │  Authorization Server       │                        │
   │  Metadata                   │                        │
   │  {                          │                        │
   │    "authorization_endpoint":│                        │
   │    "...",                   │                        │
   │    "token_endpoint": "..."  │                        │
   │  }                          │                        │
   │◄────────────────────────────┼────────────────────────┤
   │                             │                        │
```

---

계속해서 Part 2를 생성하겠습니다...