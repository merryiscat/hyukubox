"""
Starlette 미들웨어: OAuth 2.0 인증 및 보안
"""
import os
import httpx
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class OAuthMiddleware(BaseHTTPMiddleware):
    """OAuth 2.0 Bearer Token 검증 미들웨어"""

    async def dispatch(self, request, call_next):
        # 1. Health check 엔드포인트는 인증 불필요
        if request.url.path == "/health":
            return await call_next(request)

        # 2. Authorization 헤더 확인
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                {"error": "Missing or invalid Authorization header"},
                status_code=401
            )

        # 3. Token 추출
        token = auth_header.split(" ")[1]

        # 4. Token 검증 (OAuth Provider API 호출)
        is_valid = await self.verify_token(token)
        if not is_valid:
            return JSONResponse(
                {"error": "Invalid or expired token"},
                status_code=401
            )

        # 5. 요청 진행
        return await call_next(request)

    async def verify_token(self, token: str) -> bool:
        """OAuth Token 유효성 검증"""
        token_url = os.getenv("OAUTH_TOKEN_URL")

        if not token_url:
            # OAuth가 설정되지 않은 경우 (개발 모드) - 모든 토큰 허용
            return True

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{token_url}/verify",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=5.0
                )
                return response.status_code == 200
            except Exception:
                return False


class OriginValidationMiddleware(BaseHTTPMiddleware):
    """Origin 헤더 검증 (DNS rebinding 공격 방지)"""

    async def dispatch(self, request, call_next):
        allowed_origins = os.getenv("ALLOWED_ORIGINS", "").split(",")
        origin = request.headers.get("Origin")

        # Origin이 있고, 허용 목록이 설정된 경우에만 검증
        if origin and allowed_origins and allowed_origins[0]:
            if origin not in allowed_origins:
                return JSONResponse(
                    {"error": "Origin not allowed"},
                    status_code=403
                )

        return await call_next(request)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """간단한 Rate Limiting (메모리 기반)"""

    def __init__(self, app, rate_limit: str = "100/minute"):
        super().__init__(app)
        self.rate_limit = rate_limit
        self.requests = {}  # IP -> (count, timestamp)

    async def dispatch(self, request, call_next):
        # 간단한 IP 기반 rate limiting 구현
        # 실제 프로덕션에서는 Redis 등 사용 권장
        client_ip = request.client.host if request.client else "unknown"

        # TODO: Rate limit 체크 로직 구현
        # 현재는 패스스루 (모든 요청 허용)

        return await call_next(request)
