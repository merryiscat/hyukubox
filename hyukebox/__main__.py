"""진입점: python -m hyukebox"""
import os
import sys
from hyukebox.server import mcp
from hyukebox.middleware import (
    OAuthMiddleware,
    OriginValidationMiddleware,
    RateLimitMiddleware
)


def main():
    # 환경변수로 트랜스포트 선택
    transport = os.getenv("MCP_TRANSPORT", "stdio")

    if transport == "stdio":
        # 로컬 개발용 (기존 방식)
        print("Starting MCP server with stdio transport...", file=sys.stderr)
        mcp.run(transport="stdio")

    elif transport == "http":
        # HTTP 서버 (프로덕션)
        host = os.getenv("MCP_HOST", "0.0.0.0")
        port = int(os.getenv("MCP_PORT", "8000"))
        path = os.getenv("MCP_PATH", "/mcp")

        print(f"Starting MCP HTTP server at {host}:{port}{path}...", file=sys.stderr)

        # 미들웨어 설정 (일단 비활성화 - 테스트 후 활성화)
        # middleware = [
        #     OAuthMiddleware,
        #     OriginValidationMiddleware,
        #     RateLimitMiddleware
        # ]

        # HTTP 서버 실행
        # stateless_http=True: 세션 없이 매 요청마다 독립 처리 (테스트용)
        # stateless_http=False: 세션 기반 (프로덕션 권장)
        mcp.run(
            transport="http",
            host=host,
            port=port,
            path=path,
            stateless_http=True,  # 세션 없이 사용
            # middleware=middleware,  # 미들웨어 비활성화
            log_level="info"
        )

    else:
        print(f"Unknown transport: {transport}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
