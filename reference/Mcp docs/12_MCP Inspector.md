# MCP Inspector

## 개요

Model Context Protocol 서버를 테스트하고 디버깅하기 위한 MCP Inspector 사용에 대한 심층 가이드

[MCP Inspector](https://github.com/modelcontextprotocol/inspector)는 MCP 서버를 테스트하고 디버깅하기 위한 대화형 개발자 도구입니다. [디버깅 가이드](https://claude.ai/legacy/tools/debugging)가 전체 디버깅 툴킷의 일부로 Inspector를 다루는 반면, 이 문서는 Inspector의 기능과 능력에 대한 자세한 탐구를 제공합니다.

---

## 시작하기

### 설치 및 기본 사용법

Inspector는 설치 없이 `npx`를 통해 직접 실행됩니다:

**기본 명령:**

```bash
npx @modelcontextprotocol/inspector <command>
```

**인수와 함께 실행:**

```bash
npx @modelcontextprotocol/inspector <command> <arg1> <arg2>
```

---

## 서버 검사 방법

### 1. npm 또는 PyPI에서 서버 검사

[npm](https://npmjs.com/) 또는 [PyPI](https://pypi.org/)에서 서버 패키지를 시작하는 일반적인 방법입니다.

#### npm 패키지

**일반 형식:**

```bash
npx -y @modelcontextprotocol/inspector npx <package-name> <args>
```

**예시: Filesystem 서버**

```bash
npx -y @modelcontextprotocol/inspector npx @modelcontextprotocol/server-filesystem /Users/username/Desktop
```

**설명:**

- `-y`: npm 패키지 자동 설치 확인
- `npx @modelcontextprotocol/inspector`: Inspector 실행
- `npx <package-name>`: 검사할 서버 패키지
- `<args>`: 서버에 전달할 인수

---

#### PyPI 패키지

**일반 형식:**

```bash
npx @modelcontextprotocol/inspector uvx <package-name> <args>
```

**예시: Git 서버**

```bash
npx @modelcontextprotocol/inspector uvx mcp-server-git --repository ~/code/mcp/servers.git
```

**설명:**

- `uvx`: Python 패키지 실행 도구
- `<package-name>`: 검사할 Python 서버 패키지
- `<args>`: 서버에 전달할 인수 (예: `--repository`)

---

### 2. 로컬 개발 서버 검사

로컬에서 개발했거나 저장소로 다운로드한 서버를 검사하는 가장 일반적인 방법입니다.

#### TypeScript 서버

**일반 형식:**

```bash
npx @modelcontextprotocol/inspector node path/to/server/index.js args...
```

**예시:**

```bash
npx @modelcontextprotocol/inspector node ./my-server/build/index.js --port 3000
```

**설명:**

- `node`: Node.js로 서버 실행
- `path/to/server/index.js`: 서버 진입점 파일 경로
- `args...`: 서버 인수

---

#### Python 서버

**일반 형식:**

```bash
npx @modelcontextprotocol/inspector \
  uv \
  --directory path/to/server \
  run \
  package-name \
  args...
```

**예시:**

```bash
npx @modelcontextprotocol/inspector \
  uv \
  --directory ./my-python-server \
  run \
  my-server \
  --config config.json
```

**설명:**

- `uv`: Python 패키지 관리 및 실행 도구
- `--directory`: 서버 디렉토리 경로
- `run package-name`: 실행할 패키지 이름
- `args...`: 서버 인수

---

> **⚠️ 중요**: 가장 정확한 지침은 각 서버에 첨부된 README를 주의 깊게 읽으세요.

---

## 기능 개요

MCP Inspector 인터페이스는 MCP 서버와 상호 작용하기 위한 여러 기능을 제공합니다.

![MCP Inspector 인터페이스](https://mintcdn.com/mcp/4ZXF1PrDkEaJvXpn/images/mcp-inspector.png)

---

### 1. Server Connection Pane (서버 연결 창)

서버 연결을 구성하고 관리하는 주요 인터페이스입니다.

#### 주요 기능

**전송 방식 선택:**

- 서버에 연결하기 위한 [전송 방식](https://claude.ai/legacy/concepts/transports) 선택
- STDIO, HTTP/SSE 등 지원

**로컬 서버 구성:**

- 명령줄 인수 사용자 정의
- 환경 변수 설정
- 서버 시작 매개변수 구성

**연결 상태:**

- 서버 연결 상태 표시
- 기본 연결 확인
- 기능 협상 검증

---

### 2. Resources Tab (리소스 탭)

서버가 노출하는 리소스를 탐색하고 테스트합니다.

#### 주요 기능

**리소스 목록:**

- 사용 가능한 모든 리소스 나열
- 리소스 URI 및 이름 표시

**메타데이터 표시:**

- MIME 타입
- 리소스 설명
- 추가 속성

**콘텐츠 검사:**

- 리소스 내용 확인
- 다양한 형식 지원 (텍스트, JSON, 바이너리)

**구독 테스트:**

- 리소스 변경 알림 테스트
- 실시간 업데이트 확인

#### 사용 예시

**시나리오:** 파일 시스템 서버에서 파일 리소스 확인

1. Resources 탭 열기
2. 파일 리소스 선택
3. 파일 내용 확인
4. MIME 타입 검증
5. 구독 테스트 (파일 변경 감지)

---

### 3. Prompts Tab (프롬프트 탭)

서버의 프롬프트 템플릿을 테스트하고 미리 봅니다.

#### 주요 기능

**프롬프트 목록:**

- 사용 가능한 프롬프트 템플릿 표시
- 프롬프트 이름 및 설명

**인수 정보:**

- 필수 및 선택적 인수
- 인수 타입 및 설명
- 기본값 표시

**프롬프트 테스트:**

- 사용자 정의 인수로 프롬프트 실행
- 다양한 입력 값 시도

**메시지 미리보기:**

- 생성된 프롬프트 메시지 확인
- 최종 출력 검증

#### 사용 예시

**시나리오:** 코드 검토 프롬프트 테스트

1. Prompts 탭 열기
2. "code_review" 프롬프트 선택
3. 인수 입력:
    - `file_path`: "/src/main.ts"
    - `review_type`: "security"
4. 생성된 메시지 미리보기
5. 출력 형식 확인

---

### 4. Tools Tab (도구 탭)

서버의 도구를 테스트하고 실행 결과를 확인합니다.

#### 주요 기능

**도구 목록:**

- 사용 가능한 모든 도구 나열
- 도구 이름 및 ID 표시

**스키마 및 설명:**

- 도구 입력 스키마
- 매개변수 타입 및 제약 조건
- 도구 기능 설명

**도구 테스트:**

- 사용자 정의 입력으로 도구 실행
- 다양한 매개변수 조합 시도
- 에러 케이스 테스트

**실행 결과:**

- 도구 실행 결과 표시
- 성공/실패 상태 확인
- 반환 데이터 검사

#### 사용 예시

**시나리오:** 날씨 API 도구 테스트

1. Tools 탭 열기
2. "get_weather" 도구 선택
3. 입력 매개변수:
    
    ```json
    {  "location": "Seoul",  "units": "metric"}
    ```
    
4. 도구 실행
5. 결과 확인:
    
    ```json
    {  "temperature": 15,  "condition": "cloudy",  "humidity": 65}
    ```
    

---

### 5. Notifications Pane (알림 창)

서버의 로그 및 알림을 모니터링합니다.

#### 주요 기능

**로그 기록:**

- 서버에서 기록된 모든 로그 표시
- 타임스탬프 및 로그 레벨
- 로그 메시지 내용

**서버 알림:**

- 서버로부터 받은 알림 표시
- 리소스 변경 알림
- 도구 상태 업데이트

**필터링 및 검색:**

- 로그 레벨별 필터링
- 키워드 검색
- 시간 범위 필터

#### 사용 예시

**디버깅 시나리오:**

1. Notifications Pane 열기
2. 도구 실행 중 오류 발생
3. 오류 로그 확인:
    
    ```
    [ERROR] 2025-01-02 10:30:45 - Tool execution failed: Invalid input[DEBUG] 2025-01-02 10:30:45 - Input validation: location field missing
    ```
    
4. 문제 식별 및 수정

---

## 모범 사례

### 개발 워크플로우

효과적인 MCP 서버 개발을 위한 단계별 워크플로우입니다.

---

#### 1단계: 개발 시작

**초기 설정:**

```bash
# Inspector로 서버 시작
npx @modelcontextprotocol/inspector node ./server/index.js
```

**확인 항목:**

- ✅ 기본 연결 확인
- ✅ 서버 응답 확인
- ✅ 기능 협상 검증

**체크리스트:**

- [ ] 서버가 성공적으로 시작됨
- [ ] Inspector가 서버에 연결됨
- [ ] 모든 기능이 올바르게 협상됨
- [ ] 초기 상태가 예상대로 표시됨

---

#### 2단계: 반복 테스트

**개발 사이클:**

```bash
# 1. 서버 코드 변경
vim server/tools/weather.ts

# 2. 서버 빌드
npm run build

# 3. Inspector 재시작
npx @modelcontextprotocol/inspector node ./server/build/index.js

# 4. 변경사항 테스트
# - Tools 탭에서 weather 도구 확인
# - 새 매개변수로 테스트
# - 결과 검증
```

**테스트 항목:**

- ✅ 영향받은 기능 테스트
- ✅ 메시지 모니터링
- ✅ 오류 확인
- ✅ 성능 검증

**반복 주기:**

1. 코드 수정
2. 빌드
3. 재연결
4. 테스트
5. 로그 확인
6. 필요시 1번으로 돌아가기

---

#### 3단계: 엣지 케이스 테스트

**테스트 시나리오:**

**A. 잘못된 입력:**

```json
// Tools 탭에서 테스트
{
  "location": "",  // 빈 문자열
  "units": "invalid"  // 잘못된 값
}
```

**기대 결과:**

- 적절한 오류 메시지
- 오류 코드 반환
- 서버 크래시 없음

**B. 누락된 프롬프트 인수:**

```json
// Prompts 탭에서 테스트
{
  // 필수 인수 누락
}
```

**기대 결과:**

- 인수 누락 오류
- 명확한 오류 메시지
- 필요한 인수 안내

**C. 동시 작업:**

```bash
# 여러 도구를 동시에 실행
# Tools 탭에서 빠르게 여러 번 실행
```

**기대 결과:**

- 모든 요청 처리
- 응답 순서 보장
- 리소스 경합 없음

**D. 오류 처리 검증:**

**체크리스트:**

- [ ] 모든 오류에 명확한 메시지
- [ ] 적절한 HTTP 상태 코드 (해당되는 경우)
- [ ] 오류 복구 메커니즘
- [ ] 로그에 오류 세부 정보 기록

---

## 고급 사용법

### 1. 환경 변수 설정

**Inspector에서 환경 변수 전달:**

```bash
npx @modelcontextprotocol/inspector \
  node ./server/index.js \
  --env API_KEY=your-api-key \
  --env DEBUG=true
```

**사용 사례:**

- API 키 설정
- 디버그 모드 활성화
- 구성 경로 지정

---

### 2. 여러 서버 동시 테스트

**터미널 1:**

```bash
npx @modelcontextprotocol/inspector node ./server1/index.js
```

**터미널 2:**

```bash
npx @modelcontextprotocol/inspector node ./server2/index.js
```

**목적:**

- 서버 간 통합 테스트
- 성능 비교
- 호환성 검증

---

### 3. 로그 레벨 조정

**상세 로깅:**

```bash
DEBUG=mcp:* npx @modelcontextprotocol/inspector node ./server/index.js
```

**특정 모듈만:**

```bash
DEBUG=mcp:transport,mcp:protocol npx @modelcontextprotocol/inspector node ./server/index.js
```

---

## 문제 해결

### 일반적인 문제

#### 1. 연결 실패

**증상:**

- Inspector가 서버에 연결할 수 없음
- 타임아웃 오류

**해결 방법:**

```bash
# 서버 경로 확인
ls -la ./server/index.js

# 서버 직접 실행 테스트
node ./server/index.js

# 올바른 명령으로 Inspector 재시작
npx @modelcontextprotocol/inspector node ./server/index.js
```

---

#### 2. 도구가 표시되지 않음

**증상:**

- Tools 탭이 비어 있음
- 예상한 도구가 나열되지 않음

**확인 사항:**

- [ ] 서버가 도구를 올바르게 등록했는지
- [ ] `list_tools` 응답 확인
- [ ] 서버 로그에서 오류 확인

**디버깅:**

```javascript
// 서버 코드에서 확인
console.log('Registered tools:', server.listTools());
```

---

#### 3. 리소스 접근 오류

**증상:**

- 리소스를 읽을 수 없음
- 권한 오류

**해결 방법:**

```bash
# 파일 권한 확인
ls -la /path/to/resource

# 올바른 권한 설정
chmod 644 /path/to/resource
```

---

## 성능 모니터링

### 응답 시간 측정

**Notifications Pane에서 확인:**

```
[INFO] Tool execution started: get_weather
[INFO] Tool execution completed: get_weather (125ms)
```

**성능 기준:**

- ✅ 간단한 도구: < 100ms
- ✅ API 호출: < 500ms
- ✅ 복잡한 작업: < 2000ms

---

## 다음 단계

### 추가 리소스

**1. Inspector 저장소**

- [GitHub 저장소](https://github.com/modelcontextprotocol/inspector)
- 소스 코드 확인
- 이슈 및 기여

**2. 디버깅 가이드**

- [전체 디버깅 전략](https://claude.ai/legacy/tools/debugging)
- 추가 디버깅 도구
- 고급 기술

**3. 서버 개발**

- [서버 구축 가이드](https://claude.ai/docs/develop/build-server)
- 모범 사례
- 예제 코드

**4. 클라이언트 개발**

- [클라이언트 구축 가이드](https://claude.ai/docs/develop/build-client)
- 통합 테스트
- 프로덕션 배포

---

## 요약

MCP Inspector는 MCP 서버 개발 및 디버깅을 위한 필수 도구입니다.

### 핵심 기능

**연결 관리:**

- ✅ 다양한 전송 방식 지원
- ✅ 환경 변수 구성
- ✅ 명령줄 인수 사용자 정의

**기능 테스트:**

- ✅ Resources: 리소스 검사 및 구독
- ✅ Prompts: 템플릿 테스트 및 미리보기
- ✅ Tools: 도구 실행 및 결과 확인
- ✅ Notifications: 로그 및 알림 모니터링

**개발 워크플로우:**

1. 연결 확인
2. 반복 테스트
3. 엣지 케이스 검증
4. 성능 모니터링

### 모범 사례

- ✅ 모든 기능을 체계적으로 테스트
- ✅ 엣지 케이스 철저히 확인
- ✅ 로그를 주의 깊게 모니터링
- ✅ 반복적인 개발 사이클 유지

MCP Inspector를 효과적으로 사용하여 견고하고 신뢰할 수 있는 MCP 서버를 구축하세요!

---

## 추가 자료

- **공식 저장소**: https://github.com/modelcontextprotocol/inspector
- **디버깅 가이드**: [Debugging Guide](https://claude.ai/legacy/tools/debugging)
- **MCP 문서**: https://modelcontextprotocol.io/docs
- **커뮤니티**: https://github.com/modelcontextprotocol/discussions

---

_이 문서는 Model Context Protocol 공식 문서에서 가져온 내용입니다._