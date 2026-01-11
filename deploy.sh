#!/bin/bash

# Hyukebox MCP Server 배포 스크립트

set -e  # 에러 발생 시 즉시 중단

echo "============================================"
echo "Hyukebox MCP Server 배포 시작"
echo "============================================"

# 1. 의존성 설치
echo ""
echo "[1/5] 의존성 설치 중..."
if command -v uv &> /dev/null; then
    uv sync
else
    pip install -e .
fi

# 2. 환경변수 확인
echo ""
echo "[2/5] 환경변수 확인 중..."
if [ ! -f .env ]; then
    echo "Error: .env 파일이 없습니다."
    echo "OAUTH_SETUP.md를 참고하여 .env 파일을 생성하세요."
    exit 1
fi

# 필수 환경변수 확인
source .env
required_vars=("LASTFM_API_KEY" "MCP_TRANSPORT")

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "Error: $var 환경변수가 설정되지 않았습니다."
        exit 1
    fi
done

echo "환경변수 확인 완료"

# 3. HTTP 모드 설정
echo ""
echo "[3/5] HTTP 서버 모드로 설정 중..."
export MCP_TRANSPORT=http
export MCP_HOST=${MCP_HOST:-0.0.0.0}
export MCP_PORT=${MCP_PORT:-8000}
export MCP_PATH=${MCP_PATH:-/mcp}

echo "  - Transport: $MCP_TRANSPORT"
echo "  - Host: $MCP_HOST"
echo "  - Port: $MCP_PORT"
echo "  - Path: $MCP_PATH"

# 4. 포트 확인
echo ""
echo "[4/5] 포트 사용 가능 여부 확인 중..."
if lsof -Pi :$MCP_PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "Warning: 포트 $MCP_PORT가 이미 사용 중입니다."
    read -p "기존 프로세스를 종료하시겠습니까? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        lsof -ti:$MCP_PORT | xargs kill -9
        echo "기존 프로세스를 종료했습니다."
    else
        echo "배포를 중단합니다."
        exit 1
    fi
fi

# 5. 서버 실행
echo ""
echo "[5/5] MCP HTTP 서버 실행 중..."
echo "============================================"
echo ""

# 백그라운드 실행 옵션
if [ "$1" == "--background" ] || [ "$1" == "-b" ]; then
    echo "백그라운드 모드로 실행합니다..."
    nohup python -m hyukebox > hyukebox.log 2>&1 &
    SERVER_PID=$!
    echo "서버 PID: $SERVER_PID"
    echo "로그 파일: hyukebox.log"
    echo ""
    echo "서버 상태 확인: ps aux | grep $SERVER_PID"
    echo "서버 중지: kill $SERVER_PID"
    echo "로그 확인: tail -f hyukebox.log"
else
    # 포어그라운드 실행
    python -m hyukebox
fi

echo ""
echo "============================================"
echo "서버 실행 중: http://$MCP_HOST:$MCP_PORT$MCP_PATH"
echo "============================================"
echo ""
echo "테스트 명령:"
echo "  curl http://localhost:$MCP_PORT$MCP_PATH -H 'Content-Type: application/json' -d '{\"jsonrpc\":\"2.0\",\"method\":\"tools/list\",\"id\":1}'"
echo ""
