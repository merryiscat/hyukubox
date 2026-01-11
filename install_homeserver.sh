#!/bin/bash

# Hyukebox MCP Server 홈서버 자동 설치 스크립트

set -e

echo "============================================"
echo "Hyukebox MCP Server 홈서버 설치"
echo "============================================"
echo ""

# 현재 사용자 확인
CURRENT_USER=$(whoami)
HOME_DIR=$(eval echo ~$CURRENT_USER)

echo "사용자: $CURRENT_USER"
echo "홈 디렉토리: $HOME_DIR"
echo ""

# 1. Python 버전 확인
echo "[1/8] Python 버전 확인..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python 버전: $PYTHON_VERSION"

if ! python3 -c 'import sys; exit(0 if sys.version_info >= (3, 10) else 1)'; then
    echo "Error: Python 3.10 이상이 필요합니다."
    exit 1
fi
echo "✓ Python 버전 OK"
echo ""

# 2. uv 설치 확인
echo "[2/8] uv 설치 확인..."
if ! command -v uv &> /dev/null; then
    echo "uv가 설치되어 있지 않습니다. 설치 중..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.cargo/env
    echo "✓ uv 설치 완료"
else
    echo "✓ uv 이미 설치됨"
fi
echo ""

# 3. 의존성 설치
echo "[3/8] 의존성 설치 중..."
uv sync
echo "✓ 의존성 설치 완료"
echo ""

# 4. .env 파일 확인
echo "[4/8] 환경변수 파일 확인..."
if [ ! -f .env ]; then
    echo "Error: .env 파일이 없습니다."
    echo ".env.example을 복사하여 .env를 생성하세요."
    exit 1
fi

# MCP_TRANSPORT가 http로 설정되어 있는지 확인
if ! grep -q "MCP_TRANSPORT=http" .env; then
    echo "Warning: .env 파일에서 MCP_TRANSPORT=http로 설정되어 있지 않습니다."
    read -p "자동으로 수정하시겠습니까? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sed -i 's/MCP_TRANSPORT=.*/MCP_TRANSPORT=http/' .env
        echo "✓ MCP_TRANSPORT를 http로 설정했습니다."
    fi
fi
echo "✓ 환경변수 파일 확인 완료"
echo ""

# 5. 방화벽 설정
echo "[5/8] 방화벽 설정..."
if command -v ufw &> /dev/null; then
    echo "ufw 방화벽 감지됨"

    if sudo ufw status | grep -q "Status: active"; then
        echo "방화벽이 활성화되어 있습니다."

        if ! sudo ufw status | grep -q "8000.*ALLOW"; then
            read -p "포트 8000을 방화벽에서 허용하시겠습니까? (y/n) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                sudo ufw allow 8000/tcp
                echo "✓ 포트 8000 허용됨"
            fi
        else
            echo "✓ 포트 8000 이미 허용됨"
        fi
    else
        echo "방화벽이 비활성화되어 있습니다."
    fi
else
    echo "ufw가 설치되어 있지 않습니다. 방화벽 설정을 건너뜁니다."
fi
echo ""

# 6. systemd 서비스 파일 생성
echo "[6/8] systemd 서비스 설정..."

# 서비스 파일 템플릿에서 사용자명과 경로 치환
SERVICE_FILE="/tmp/hyukebox-mcp.service"
cp hyukebox-mcp.service $SERVICE_FILE
sed -i "s/YOUR_USERNAME/$CURRENT_USER/g" $SERVICE_FILE
sed -i "s|/home/YOUR_USERNAME|$HOME_DIR|g" $SERVICE_FILE

# 로그 파일 생성
sudo touch /var/log/hyukebox-mcp.log
sudo touch /var/log/hyukebox-mcp-error.log
sudo chown $CURRENT_USER:$CURRENT_USER /var/log/hyukebox-mcp*.log

# 서비스 파일 설치
sudo cp $SERVICE_FILE /etc/systemd/system/hyukebox-mcp.service
sudo systemctl daemon-reload

echo "✓ systemd 서비스 파일 생성 완료"
echo ""

# 7. 서비스 시작
echo "[7/8] 서비스 시작..."
read -p "서비스를 시작하시겠습니까? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo systemctl start hyukebox-mcp
    sleep 2

    if sudo systemctl is-active --quiet hyukebox-mcp; then
        echo "✓ 서비스 시작 성공"

        read -p "부팅 시 자동 시작을 활성화하시겠습니까? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            sudo systemctl enable hyukebox-mcp
            echo "✓ 자동 시작 활성화됨"
        fi
    else
        echo "Error: 서비스 시작 실패"
        echo "로그 확인: sudo journalctl -u hyukebox-mcp -n 50"
        exit 1
    fi
fi
echo ""

# 8. 설치 완료 및 정보 출력
echo "[8/8] 설치 완료!"
echo ""
echo "============================================"
echo "Hyukebox MCP Server 설치 완료"
echo "============================================"
echo ""

# 공인 IP 확인
PUBLIC_IP=$(curl -s ifconfig.me || echo "확인 실패")
echo "공인 IP: $PUBLIC_IP"
echo "MCP Endpoint: http://$PUBLIC_IP:8000/mcp"
echo ""

echo "다음 단계:"
echo "1. 공유기에서 포트포워딩 설정 (8000 → 이 서버)"
echo "2. 외부 접근 테스트"
echo "3. Claude Desktop 연결"
echo ""

echo "유용한 명령어:"
echo "  서비스 상태: sudo systemctl status hyukebox-mcp"
echo "  로그 확인: sudo tail -f /var/log/hyukebox-mcp.log"
echo "  서비스 재시작: sudo systemctl restart hyukebox-mcp"
echo "  서비스 중지: sudo systemctl stop hyukebox-mcp"
echo ""

echo "자세한 가이드는 HOME_SERVER_SETUP.md를 참고하세요."
