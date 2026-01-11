# OAuth 2.0 설정 가이드

Hyukebox MCP 서버를 외부에서 안전하게 사용하기 위한 OAuth 2.0 인증 설정 가이드입니다.

## 1. OAuth Provider 선택

추천하는 Provider:

### Auth0 (추천)
- **장점**: 쉬운 설정, 무료 tier 제공 (최대 7,000 active users)
- **사이트**: https://auth0.com
- **가격**: 무료 tier로 시작 가능

### Okta
- **장점**: 엔터프라이즈급 보안, 풍부한 기능
- **사이트**: https://okta.com
- **가격**: 개발자 무료 tier 제공

### Keycloak (자체 호스팅)
- **장점**: 완전한 통제, 비용 없음
- **사이트**: https://www.keycloak.org
- **가격**: 무료 (자체 서버 비용만)

## 2. OAuth Application 등록 (Auth0 예시)

### 2.1. Auth0 계정 생성
1. https://auth0.com 에서 무료 계정 생성
2. Tenant 이름 설정 (예: `hyukebox-production`)

### 2.2. Application 생성
1. Dashboard → Applications → Create Application
2. Name: `Hyukebox MCP Server`
3. Application Type: `Machine to Machine Applications` 선택
4. API: `Auth0 Management API` 선택

### 2.3. 설정 확인
- **Domain**: `your-tenant.auth0.com`
- **Client ID**: 자동 생성됨 (예: `abc123xyz`)
- **Client Secret**: 자동 생성됨 (보안 유지!)

### 2.4. Callback URL 설정
Settings → Application URIs → Allowed Callback URLs:
```
https://your-server.com/oauth/callback
```

## 3. 환경변수 설정

`.env` 파일에 발급받은 정보를 입력합니다:

```bash
# OAuth 2.0 설정
OAUTH_CLIENT_ID=your_client_id_from_auth0
OAUTH_CLIENT_SECRET=your_client_secret_from_auth0
OAUTH_TOKEN_URL=https://your-tenant.auth0.com/oauth/token
OAUTH_AUTHORIZE_URL=https://your-tenant.auth0.com/authorize
OAUTH_REDIRECT_URI=https://your-server.com/oauth/callback

# 보안 설정
ALLOWED_ORIGINS=https://claude.ai,https://your-frontend.com
```

## 4. Claude Desktop 연결

Claude Desktop에서 "새로운 MCP 서버 등록" 화면에서 다음을 입력합니다:

### 인증 방식
- **OAuth 인증** 선택

### OAuth 설정
- **Client ID**: (Auth0에서 발급받은 Client ID)
- **Client Secret**: (Auth0에서 발급받은 Client Secret)
- **Authorization Endpoint URL**: `https://your-tenant.auth0.com/authorize`
- **Token Endpoint URL**: `https://your-tenant.auth0.com/oauth/token`
- **Scope**: `openid profile email`
- **Grant Type**: `AUTHORIZATION_CODE`

### MCP Endpoint
- **MCP Endpoint**: `https://your-server.com/mcp`

### 정보 플로우 확인
MCP 엔드포인트에서는 Bearer Token을 헤더로 받아야 합니다.

## 5. 토큰 검증 테스트

### 5.1. 토큰 발급 (개발 테스트)

```bash
curl -X POST https://your-tenant.auth0.com/oauth/token \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "YOUR_CLIENT_ID",
    "client_secret": "YOUR_CLIENT_SECRET",
    "audience": "https://your-tenant.auth0.com/api/v2/",
    "grant_type": "client_credentials"
  }'
```

### 5.2. MCP 엔드포인트 테스트

```bash
# 툴 목록 조회
curl -X POST https://your-server.com/mcp \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "MCP-Protocol-Version: 2025-11-25" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'
```

예상 응답:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "tools": [
      {"name": "search_song", "description": "..."},
      {"name": "describe_song", "description": "..."}
    ]
  }
}
```

### 5.3. 인증 없이 접근 (401 확인)

```bash
curl -X POST https://your-server.com/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'
```

예상 응답:
```json
{
  "error": "Missing or invalid Authorization header"
}
```
Status: 401

## 6. 프로덕션 체크리스트

배포 전 확인 사항:

- [ ] OAuth Client Secret을 안전하게 보관 (.env 파일, 환경변수)
- [ ] `.env` 파일을 .gitignore에 추가
- [ ] HTTPS/TLS 인증서 설치 (Let's Encrypt 추천)
- [ ] nginx 역방향 프록시 설정
- [ ] Origin 헤더 검증 활성화 (ALLOWED_ORIGINS 설정)
- [ ] Rate Limiting 설정 (필요 시)
- [ ] 로깅 및 모니터링 설정
- [ ] Health check 엔드포인트 확인 (/health)

## 7. 문제 해결

### 401 Unauthorized 에러
- Client ID/Secret이 올바른지 확인
- Token이 만료되지 않았는지 확인
- Authorization 헤더 형식: `Bearer {token}`

### 403 Forbidden 에러
- Origin 헤더가 ALLOWED_ORIGINS에 포함되어 있는지 확인
- CORS 설정 확인 (nginx.conf)

### 연결 타임아웃
- 방화벽에서 포트 8000 또는 443 허용
- nginx 프록시 설정 확인
- MCP 서버가 실행 중인지 확인

## 8. 추가 리소스

- Auth0 문서: https://auth0.com/docs
- MCP Specification: https://spec.modelcontextprotocol.io
- OAuth 2.0 RFC: https://oauth.net/2/
- nginx SSE 설정: https://nginx.org/en/docs/http/ngx_http_proxy_module.html

## 9. 보안 권장사항

1. **Token Rotation**: Access Token 유효기간을 짧게 설정 (1시간 권장)
2. **Refresh Token**: 장기 세션을 위해 Refresh Token 사용
3. **Scope 제한**: 필요한 최소 권한만 부여
4. **IP 화이트리스트**: 가능한 경우 허용 IP 제한
5. **모니터링**: 비정상적인 API 사용 패턴 모니터링
6. **로그**: 인증 실패 로그 기록 및 분석
