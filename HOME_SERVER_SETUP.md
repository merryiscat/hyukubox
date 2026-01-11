# 홈서버 MCP Endpoint 배포 가이드

Ubuntu/Debian Linux 홈서버에 Hyukebox MCP 서버를 배포하는 전체 가이드입니다.

## 사전 준비

### 필요한 것
- Ubuntu/Debian Linux 홈서버
- 공인 IP 주소
- 공유기 관리자 접근 (포트포워딩 설정용)
- SSH 접근 가능

### 확인할 것
```bash
# 홈서버 접속
ssh user@your-home-server-ip

# Python 버전 확인 (3.10 이상 필요)
python3 --version

# pip/uv 확인
pip3 --version
```

## Step 1: 홈서버에 프로젝트 복사

### 방법 1: Git 사용 (추천)
```bash
# 홈서버에서
cd ~
git clone https://github.com/your-username/hyukubox.git
cd hyukubox
```

### 방법 2: 직접 전송
```bash
# 로컬 PC에서 (Windows에서 실행)
# scp로 전체 프로젝트 전송
scp -r C:\Users\minhy\project\hyukubox user@your-home-server-ip:~/
```

## Step 2: 의존성 설치

```bash
# 홈서버에서
cd ~/hyukubox

# uv 설치 (추천)
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env

# 또는 pip 사용
# python3 -m pip install -e .

# uv로 의존성 설치
uv sync
```

## Step 3: 환경변수 설정

```bash
# .env 파일 편집
nano .env
```

**중요 설정**:
```bash
# API 키들 (기존)
LASTFM_API_KEY=your_key
TAVILY_API_KEY=your_key
OPENAI_API_KEY=your_key

# MCP HTTP Server 설정
MCP_TRANSPORT=http
MCP_HOST=0.0.0.0          # 모든 인터페이스에서 접근 가능
MCP_PORT=8000             # 외부 포트 (포트포워딩할 포트)
MCP_PATH=/mcp

# OAuth 2.0 설정 (나중에 설정 가능)
OAUTH_CLIENT_ID=your_client_id
OAUTH_CLIENT_SECRET=your_client_secret
OAUTH_TOKEN_URL=https://oauth.provider.com/token
OAUTH_AUTHORIZE_URL=https://oauth.provider.com/authorize
OAUTH_REDIRECT_URI=https://your-domain.com/oauth/callback

# 보안 설정
ALLOWED_ORIGINS=https://claude.ai
RATE_LIMIT=100/minute
```

## Step 4: 방화벽 설정 (ufw)

```bash
# ufw 설치 (없는 경우)
sudo apt update
sudo apt install ufw

# SSH 포트 허용 (먼저!)
sudo ufw allow 22/tcp

# MCP 서버 포트 허용
sudo ufw allow 8000/tcp

# 방화벽 활성화
sudo ufw enable

# 상태 확인
sudo ufw status
```

예상 출력:
```
Status: active

To                         Action      From
--                         ------      ----
22/tcp                     ALLOW       Anywhere
8000/tcp                   ALLOW       Anywhere
```

## Step 5: 수동 테스트

```bash
# 홈서버에서 서버 실행
cd ~/hyukubox
python3 -m hyukebox
```

**다른 터미널에서 테스트**:
```bash
# 로컬 테스트 (홈서버 내부)
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'
```

성공하면 `Ctrl+C`로 서버 종료하고 다음 단계로 진행합니다.

## Step 6: systemd 서비스 설정

서버가 자동으로 시작되고 재시작되도록 systemd 서비스를 만듭니다.

```bash
# 서비스 파일 생성
sudo nano /etc/systemd/system/hyukebox-mcp.service
```

**서비스 파일 내용**:
```ini
[Unit]
Description=Hyukebox MCP Server
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/hyukubox
Environment="PATH=/home/YOUR_USERNAME/.local/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/usr/bin/python3 -m hyukebox
Restart=always
RestartSec=10

# 로그 설정
StandardOutput=append:/var/log/hyukebox-mcp.log
StandardError=append:/var/log/hyukebox-mcp-error.log

[Install]
WantedBy=multi-user.target
```

**YOUR_USERNAME을 실제 사용자명으로 변경하세요!**

```bash
# 로그 파일 생성 및 권한 설정
sudo touch /var/log/hyukebox-mcp.log
sudo touch /var/log/hyukebox-mcp-error.log
sudo chown YOUR_USERNAME:YOUR_USERNAME /var/log/hyukebox-mcp*.log

# systemd 리로드
sudo systemctl daemon-reload

# 서비스 시작
sudo systemctl start hyukebox-mcp

# 상태 확인
sudo systemctl status hyukebox-mcp

# 부팅 시 자동 시작 활성화
sudo systemctl enable hyukebox-mcp
```

**로그 확인**:
```bash
# 실시간 로그 확인
sudo tail -f /var/log/hyukebox-mcp.log

# 에러 로그 확인
sudo tail -f /var/log/hyukebox-mcp-error.log

# journalctl로 확인
sudo journalctl -u hyukebox-mcp -f
```

## Step 7: 공유기 포트포워딩 설정

공유기 관리 페이지에 접속하여 포트포워딩을 설정합니다.

### 일반적인 공유기 접속 주소
- `192.168.0.1` 또는 `192.168.1.1`
- ipTIME: `192.168.0.1`
- 공유기 제조사별 기본 주소 확인 필요

### 포트포워딩 설정
1. 공유기 관리 페이지 접속
2. "포트포워딩" 또는 "Port Forwarding" 메뉴 찾기
3. 새 규칙 추가:
   - **내부 IP**: 홈서버 IP (예: `192.168.0.100`)
   - **내부 포트**: `8000`
   - **외부 포트**: `8000` (또는 원하는 포트)
   - **프로토콜**: `TCP`
   - **설명**: `Hyukebox MCP Server`

### 홈서버 IP 고정 (권장)
공유기에서 DHCP 고정 할당(MAC 주소 기반) 설정

```bash
# 홈서버의 IP와 MAC 주소 확인
ip addr show
```

## Step 8: 공인 IP 확인

```bash
# 홈서버에서 공인 IP 확인
curl ifconfig.me

# 또는
curl icanhazip.com
```

출력된 IP를 메모하세요 (예: `123.45.67.89`)

## Step 9: 외부 접근 테스트

### 방법 1: 로컬 PC에서 테스트
```bash
# Windows PowerShell에서
curl -X POST http://YOUR_PUBLIC_IP:8000/mcp `
  -H "Content-Type: application/json" `
  -H "Accept: application/json, text/event-stream" `
  -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'
```

### 방법 2: 온라인 도구 사용
- https://reqbin.com/
- https://httpie.io/cli

**Request URL**: `http://YOUR_PUBLIC_IP:8000/mcp`
**Method**: `POST`
**Headers**:
```
Content-Type: application/json
Accept: application/json, text/event-stream
```
**Body**:
```json
{"jsonrpc":"2.0","method":"tools/list","id":1}
```

## Step 10: Claude Desktop 연결

### Claude Desktop 설정
1. Settings → Developer → MCP Servers
2. "Add Server" 클릭
3. 정보 입력:
   - **Server Name**: `Hyukebox Home Server`
   - **Connection Type**: `HTTP`
   - **MCP Endpoint**: `http://YOUR_PUBLIC_IP:8000/mcp`
   - **Authentication**: None (일단 테스트용)

## 문제 해결

### 서비스가 시작되지 않음
```bash
# 상태 확인
sudo systemctl status hyukebox-mcp

# 로그 확인
sudo journalctl -u hyukebox-mcp -n 50

# 직접 실행해서 에러 확인
cd ~/hyukubox
python3 -m hyukebox
```

### 포트 접근 불가
```bash
# 포트가 열려있는지 확인
sudo netstat -tlnp | grep 8000

# 방화벽 확인
sudo ufw status

# 외부에서 포트 확인 (다른 PC에서)
telnet YOUR_PUBLIC_IP 8000
```

### 포트포워딩 확인
- 온라인 포트 체크 도구: https://www.yougetsignal.com/tools/open-ports/
- 포트 8000이 열려있는지 확인

### 로그 확인
```bash
# 에러 로그
sudo tail -100 /var/log/hyukebox-mcp-error.log

# 일반 로그
sudo tail -100 /var/log/hyukebox-mcp.log

# systemd 로그
sudo journalctl -u hyukebox-mcp --since "10 minutes ago"
```

## 보안 강화 (선택 사항)

### 1. HTTPS 설정 (Let's Encrypt)

**도메인이 있는 경우만 가능**

```bash
# Certbot 설치
sudo apt update
sudo apt install certbot

# 인증서 발급 (standalone 모드)
sudo certbot certonly --standalone -d your-domain.com

# nginx 설치 및 설정
sudo apt install nginx
sudo nano /etc/nginx/sites-available/hyukebox
```

`nginx.conf.example` 파일을 참고하여 설정

### 2. OAuth 인증 활성화

`OAUTH_SETUP.md` 파일 참고

### 3. Rate Limiting

nginx 또는 애플리케이션 레벨에서 설정

### 4. IP 화이트리스트

```bash
# ufw로 특정 IP만 허용
sudo ufw delete allow 8000/tcp
sudo ufw allow from YOUR_CLIENT_IP to any port 8000 proto tcp
```

## 유지보수

### 서비스 재시작
```bash
sudo systemctl restart hyukebox-mcp
```

### 서비스 중지
```bash
sudo systemctl stop hyukebox-mcp
```

### 로그 로테이션
```bash
# logrotate 설정
sudo nano /etc/logrotate.d/hyukebox-mcp
```

```
/var/log/hyukebox-mcp*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
```

### 업데이트
```bash
cd ~/hyukubox
git pull  # 또는 파일 재전송
uv sync
sudo systemctl restart hyukebox-mcp
```

## 모니터링

### 서비스 상태 확인 스크립트
```bash
#!/bin/bash
# ~/check_mcp.sh

echo "=== Hyukebox MCP Server Status ==="
echo ""
echo "Service Status:"
sudo systemctl status hyukebox-mcp --no-pager | grep "Active"
echo ""
echo "Port Status:"
sudo netstat -tlnp | grep 8000
echo ""
echo "Recent Logs:"
sudo tail -5 /var/log/hyukebox-mcp.log
```

```bash
chmod +x ~/check_mcp.sh
./check_mcp.sh
```

## 요약: 빠른 배포 체크리스트

- [ ] 홈서버에 프로젝트 복사
- [ ] `uv sync`로 의존성 설치
- [ ] `.env` 파일 설정 (MCP_TRANSPORT=http)
- [ ] 방화벽 포트 8000 허용 (`sudo ufw allow 8000/tcp`)
- [ ] systemd 서비스 생성 및 시작
- [ ] 공유기 포트포워딩 설정 (8000 → 홈서버 IP)
- [ ] 공인 IP 확인 (`curl ifconfig.me`)
- [ ] 외부 접근 테스트
- [ ] Claude Desktop 연결

## 다음 단계

1. **도메인 연결** (선택): DDNS 또는 실제 도메인 구매
2. **HTTPS 설정**: Let's Encrypt로 무료 SSL 인증서
3. **OAuth 인증**: 프로덕션 보안 강화
4. **모니터링**: Prometheus + Grafana 설정
5. **백업**: 정기적인 설정 파일 백업

## 참고 링크

- systemd 문서: https://www.freedesktop.org/software/systemd/man/systemd.service.html
- ufw 가이드: https://help.ubuntu.com/community/UFW
- Let's Encrypt: https://letsencrypt.org/
