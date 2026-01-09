# 로컬 MCP 서버 연결하기

## 개요

Claude Desktop을 로컬 MCP 서버로 확장하여 파일 시스템 접근 및 기타 강력한 통합 기능을 활성화하는 방법을 배웁니다.

Model Context Protocol (MCP) 서버는 로컬 리소스와 도구에 대한 안전하고 제어된 접근을 제공하여 AI 애플리케이션의 기능을 확장합니다. 많은 클라이언트가 MCP를 지원하여 다양한 플랫폼과 애플리케이션에서 다양한 통합 가능성을 제공합니다.

이 가이드는 [MCP를 지원하는 여러 클라이언트](https://claude.ai/clients) 중 하나인 Claude Desktop을 예제로 사용하여 로컬 MCP 서버에 연결하는 방법을 보여줍니다. Claude Desktop의 구현에 초점을 맞추지만, 개념은 다른 MCP 호환 클라이언트에도 광범위하게 적용됩니다.

**이 튜토리얼을 마치면:**

- Claude가 컴퓨터의 파일과 상호작용할 수 있음
- 새 문서 생성 가능
- 폴더 정리 가능
- 파일 시스템 검색 가능
- 모든 작업에 대해 명시적 권한 부여 필요

---

## 사전 요구사항

이 튜토리얼을 시작하기 전에 시스템에 다음이 설치되어 있는지 확인하세요:

### Claude Desktop

운영 체제에 맞는 [Claude Desktop](https://claude.ai/download)을 다운로드하여 설치합니다.

- **지원 플랫폼**: macOS, Windows

**버전 확인:**

- 이미 Claude Desktop이 설치되어 있다면 최신 버전인지 확인
- Claude 메뉴 → "Check for Updates…" 클릭

### Node.js

Filesystem Server와 많은 MCP 서버는 Node.js를 실행해야 합니다.

**설치 확인:**

터미널 또는 명령 프롬프트를 열고 다음 명령 실행:

```bash
node --version
```

**설치되지 않은 경우:**

- [nodejs.org](https://nodejs.org/)에서 다운로드
- 안정성을 위해 LTS (Long Term Support) 버전 권장

---

## MCP 서버 이해하기

### MCP 서버란?

MCP 서버는 컴퓨터에서 실행되며 표준화된 프로토콜을 통해 Claude Desktop에 특정 기능을 제공하는 프로그램입니다. 각 서버는 Claude가 사용할 수 있는 도구를 노출하며, 모든 작업은 사용자의 승인이 필요합니다.

### Filesystem Server가 제공하는 도구

- **파일 읽기**: 파일 내용 및 디렉토리 구조 읽기
- **파일 생성**: 새 파일 및 디렉토리 생성
- **파일 이동**: 파일 이동 및 이름 변경
- **파일 검색**: 이름 또는 내용으로 파일 검색

> **중요**: 모든 작업은 실행 전 명시적 승인이 필요하여 Claude가 액세스하고 수정할 수 있는 항목을 완전히 제어할 수 있습니다.

---

## Filesystem Server 설치하기

프로세스는 Claude Desktop을 구성하여 애플리케이션을 시작할 때마다 Filesystem Server를 자동으로 시작하도록 하는 것입니다. 이 구성은 Claude Desktop에 실행할 서버와 연결 방법을 알려주는 JSON 파일을 통해 수행됩니다.

---

### 1단계: Claude Desktop 설정 열기

Claude Desktop 설정에 액세스합니다.

**방법:**

1. 시스템 메뉴 바의 Claude 메뉴 클릭 (Claude 창 내부의 설정이 아님)
2. "Settings…" 선택

**macOS에서의 위치:**

- 상단 메뉴 바에 표시됨

이렇게 하면 Claude 계정 설정과는 별개인 Claude Desktop 구성 창이 열립니다.

---

### 2단계: Developer 설정 액세스

Settings 창에서 왼쪽 사이드바의 "Developer" 탭으로 이동합니다.

**이 섹션에 포함된 내용:**

- MCP 서버 구성 옵션
- 기타 개발자 기능

**"Edit Config" 버튼 클릭:**

- 구성 파일이 없으면 새로 생성
- 기존 구성이 있으면 열기

**구성 파일 위치:**

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

---

### 3단계: Filesystem Server 구성

구성 파일의 내용을 다음 JSON 구조로 교체합니다. 이 구성은 Claude Desktop에 특정 디렉토리에 대한 액세스 권한으로 Filesystem Server를 시작하도록 지시합니다.

#### macOS 구성

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/Users/username/Desktop",
        "/Users/username/Downloads"
      ]
    }
  }
}
```

#### Windows 구성

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "C:\\Users\\username\\Desktop",
        "C:\\Users\\username\\Downloads"
      ]
    }
  }
}
```

> **중요**: `username`을 실제 컴퓨터 사용자 이름으로 교체하세요.

**경로 사용자 정의:**

- `args` 배열에 나열된 경로는 Filesystem Server가 액세스할 수 있는 디렉토리를 지정
- 필요에 따라 이러한 경로를 수정하거나 추가 디렉토리를 추가할 수 있음

---

### 구성 이해하기

```json
{
  "mcpServers": {
    "filesystem": {                                    // 서버의 친근한 이름
      "command": "npx",                                 // Node.js의 npx 도구 사용
      "args": [
        "-y",                                           // 자동으로 패키지 설치 확인
        "@modelcontextprotocol/server-filesystem",     // Filesystem Server 패키지 이름
        "/Users/username/Desktop",                      // 접근 허용할 디렉토리
        "/Users/username/Downloads"                     // 접근 허용할 디렉토리
      ]
    }
  }
}
```

**각 필드 설명:**

- **`"filesystem"`**: Claude Desktop에 표시되는 서버의 친근한 이름
- **`"command": "npx"`**: Node.js의 npx 도구를 사용하여 서버 실행
- **`"-y"`**: 서버 패키지 설치를 자동으로 확인
- **`"@modelcontextprotocol/server-filesystem"`**: Filesystem Server의 패키지 이름
- **나머지 인수**: 서버가 액세스할 수 있는 디렉토리

---

### ⚠️ 보안 고려사항

> **주의**: Claude가 읽고 수정하는 것이 편한 디렉토리에만 액세스 권한을 부여하세요. 서버는 사용자 계정 권한으로 실행되므로 수동으로 수행할 수 있는 모든 파일 작업을 수행할 수 있습니다.

---

### 4단계: Claude Desktop 재시작

1. 구성 파일 저장 후 Claude Desktop을 완전히 종료
2. 애플리케이션 재시작

애플리케이션은 새 구성을 로드하고 MCP 서버를 시작하기 위해 재시작해야 합니다.

#### 성공 확인

재시작이 성공하면 대화 입력 상자의 오른쪽 하단에 MCP 서버 표시기가 나타납니다:

**표시기 클릭:**

- Filesystem Server가 제공하는 사용 가능한 도구 보기

**사용 가능한 도구:**

- `read_file` - 파일 내용 읽기
- `read_multiple_files` - 여러 파일 읽기
- `write_file` - 파일 생성 또는 수정
- `create_directory` - 새 디렉토리 생성
- `list_directory` - 디렉토리 내용 나열
- `move_file` - 파일 이동 또는 이름 변경
- `search_files` - 파일 검색
- `get_file_info` - 파일 메타데이터 가져오기
- `list_allowed_directories` - 액세스 가능한 디렉토리 나열

**서버 표시기가 나타나지 않는 경우:**

- [문제 해결](https://claude.ai/chat/d1892e31-8053-4913-8394-fadb47edcd3a#%EB%AC%B8%EC%A0%9C-%ED%95%B4%EA%B2%B0) 섹션 참조

---

## Filesystem Server 사용하기

Filesystem Server가 연결되면 Claude가 이제 파일 시스템과 상호작용할 수 있습니다.

### 파일 관리 예제

다음 예제 요청을 시도하여 기능을 탐색하세요:

#### 예제 1: 파일 생성

**요청:**

```
시를 작성하고 내 데스크톱에 저장해줄래?
```

**Claude의 동작:**

- 시를 작성
- 데스크톱에 새 텍스트 파일 생성
- 사용자에게 승인 요청

#### 예제 2: 파일 검색

**요청:**

```
다운로드 폴더에서 업무 관련 파일이 뭐가 있어?
```

**Claude의 동작:**

- 다운로드 폴더 스캔
- 업무 관련 문서 식별
- 파일 목록 제공

#### 예제 3: 파일 정리

**요청:**

```
내 데스크톱의 모든 이미지를 'Images'라는 새 폴더로 정리해줘
```

**Claude의 동작:**

- 새 폴더 생성
- 이미지 파일을 해당 폴더로 이동
- 각 작업에 대해 승인 요청

---

### 승인 작동 방식

모든 파일 시스템 작업을 실행하기 전에 Claude는 승인을 요청합니다. 이를 통해 모든 작업에 대한 제어를 유지할 수 있습니다.

**승인 프로세스:**

1. Claude가 수행하려는 작업을 설명
2. 작업 세부 정보 표시 (파일 경로, 작업 유형 등)
3. 사용자가 승인 또는 거부 선택

**모범 사례:**

- 승인하기 전에 각 요청을 신중하게 검토
- 제안된 작업이 불편하면 언제든지 요청을 거부할 수 있음
- 불확실한 경우 거부하고 더 많은 정보 요청

---

## 문제 해결

Filesystem Server 설정 또는 사용 중 문제가 발생하면 다음 솔루션으로 일반적인 문제를 해결할 수 있습니다:

### 문제 1: 서버가 Claude에 표시되지 않음 / 망치 아이콘이 없음

**해결 방법:**

1. **Claude Desktop 완전히 재시작**
2. **구성 파일 문법 확인**
    - `claude_desktop_config.json` 파일의 JSON 문법 확인
3. **파일 경로 유효성 확인**
    - `claude_desktop_config.json`에 포함된 파일 경로가 유효한지 확인
    - 상대 경로가 아닌 절대 경로인지 확인
4. **로그 확인**
    - [Claude Desktop에서 로그 가져오기](https://claude.ai/chat/d1892e31-8053-4913-8394-fadb47edcd3a#claude-desktop%EC%97%90%EC%84%9C-%EB%A1%9C%EA%B7%B8-%EA%B0%80%EC%A0%B8%EC%98%A4%EA%B8%B0) 참조
    - 서버가 연결되지 않는 이유 확인
5. **수동 서버 실행 테스트**
    - 명령줄에서 서버를 수동으로 실행하여 오류 확인

**macOS/Linux:**

```bash
npx -y @modelcontextprotocol/server-filesystem /Users/username/Desktop /Users/username/Downloads
```

**Windows:**

```bash
npx -y @modelcontextprotocol/server-filesystem C:\Users\username\Desktop C:\Users\username\Downloads
```

---

### Claude Desktop에서 로그 가져오기

MCP 관련 Claude.app 로깅은 다음 위치의 로그 파일에 기록됩니다:

**로그 파일 위치:**

- **macOS**: `~/Library/Logs/Claude`
- **Windows**: `%APPDATA%\Claude\logs`

**로그 파일 종류:**

- **`mcp.log`**: MCP 연결 및 연결 실패에 대한 일반 로깅
- **`mcp-server-SERVERNAME.log`**: 명명된 서버의 오류(stderr) 로깅

**로그 확인 명령:**

**macOS/Linux:**

```bash
tail -n 20 -f ~/Library/Logs/Claude/mcp*.log
```

**Windows:**

```powershell
Get-Content -Path "$env:APPDATA\Claude\logs\mcp*.log" -Tail 20 -Wait
```

이 명령은 최근 로그를 나열하고 새 로그를 실시간으로 표시합니다.

---

### 문제 2: 도구 호출이 자동으로 실패함

Claude가 도구를 사용하려고 시도하지만 실패하는 경우:

**해결 방법:**

1. **Claude의 로그에서 오류 확인**
2. **서버가 오류 없이 빌드되고 실행되는지 확인**
3. **Claude Desktop 재시작 시도**

---

### 문제 3: Windows에서 ENOENT 오류 및 경로의 `${APPDATA}`

구성된 서버가 로드되지 않고 로그에 경로 내 `${APPDATA}`를 참조하는 오류가 표시되는 경우:

**해결 방법:**

`claude_desktop_config.json`의 `env` 키에 `%APPDATA%`의 확장 값을 추가해야 할 수 있습니다:

```json
{
  "brave-search": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-brave-search"],
    "env": {
      "APPDATA": "C:\\Users\\user\\AppData\\Roaming\\",
      "BRAVE_API_KEY": "..."
    }
  }
}
```

이 변경 후 Claude Desktop을 다시 시작합니다.

---

### npm 전역 설치

`npx` 명령이 npm을 전역으로 설치하지 않은 경우 계속 실패할 수 있습니다.

**확인 방법:**

- npm이 이미 전역으로 설치되어 있으면 시스템에 `%APPDATA%\npm`이 존재

**전역 설치 명령:**

```bash
npm install -g npm
```

---

### 문제 4: 그래도 작동하지 않는 경우

더 나은 디버깅 도구와 자세한 지침은 [디버깅 가이드](https://claude.ai/legacy/tools/debugging)를 참조하세요.

---

## 다음 단계

Claude Desktop을 로컬 MCP 서버에 성공적으로 연결했으므로 다음 옵션을 탐색하여 설정을 확장하세요:

### 1. 다른 서버 탐색

**추가 기능을 위한 공식 및 커뮤니티 생성 MCP 서버 모음 탐색**

- [MCP Servers GitHub](https://github.com/modelcontextprotocol/servers)

**인기 있는 서버:**

- **GitHub Server**: GitHub 저장소 관리
- **Google Drive Server**: Google Drive 파일 액세스
- **Slack Server**: Slack 메시지 및 채널 관리
- **PostgreSQL Server**: 데이터베이스 쿼리 및 관리

### 2. 자체 서버 구축

**특정 워크플로우 및 통합에 맞춤화된 사용자 정의 MCP 서버 생성**

- [서버 구축 가이드](https://claude.ai/docs/develop/build-server)

### 3. 원격 서버에 연결

**클라우드 기반 도구 및 서비스를 위해 Claude를 원격 MCP 서버에 연결하는 방법 학습**

- [원격 서버 연결 가이드](https://claude.ai/docs/develop/connect-remote-servers)

### 4. 프로토콜 이해

**MCP의 작동 방식과 아키텍처에 대해 자세히 알아보기**

- [아키텍처 개요](https://claude.ai/docs/learn/architecture)

---

## 요약

이 가이드를 통해:

✅ Claude Desktop에 Filesystem Server 설치 ✅ 파일 시스템 액세스를 위한 구성 파일 설정 ✅ 파일 관리 작업 수행 방법 학습 ✅ 승인 메커니즘 이해 ✅ 일반적인 문제 해결 방법 학습

이제 Claude Desktop을 강력한 파일 관리 도구로 사용할 수 있으며, 더 많은 MCP 서버를 추가하여 기능을 확장할 수 있습니다.

---

## 추가 리소스

- **MCP 서버 저장소**: https://github.com/modelcontextprotocol/servers
- **아키텍처 문서**: [Architecture Overview](https://claude.ai/docs/learn/architecture)
- **서버 구축**: [Build an MCP Server](https://claude.ai/docs/develop/build-server)
- **원격 서버**: [Connect to Remote Servers](https://claude.ai/docs/develop/connect-remote-servers)

---

_이 문서는 Model Context Protocol 공식 문서에서 가져온 내용입니다._