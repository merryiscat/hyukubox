# MCP SDK

## 개요

Model Context Protocol로 구축하기 위한 공식 SDK

공식 SDK를 사용하여 MCP 서버와 클라이언트를 구축하세요. 모든 SDK는 동일한 핵심 기능과 완전한 프로토콜 지원을 제공합니다.

---

## 사용 가능한 SDK

MCP는 다양한 프로그래밍 언어에 대한 공식 SDK를 제공합니다. 각 SDK는 해당 언어의 관용구와 모범 사례를 따르면서도 동일한 기능을 제공합니다.

### 1. TypeScript SDK

**GitHub**: https://github.com/modelcontextprotocol/typescript-sdk

**특징:**

- Node.js 및 브라우저 환경 지원
- 타입 안전성 및 자동 완성
- Promise 기반 비동기 API
- STDIO 및 HTTP 전송 프로토콜

**추천 대상:**

- Node.js 서버 애플리케이션
- 웹 기반 MCP 클라이언트
- TypeScript/JavaScript 개발자

**시작하기:**

```bash
npm install @modelcontextprotocol/sdk
```

---

### 2. Python SDK

**GitHub**: https://github.com/modelcontextprotocol/python-sdk

**특징:**

- asyncio 기반 비동기 지원
- 타입 힌트 및 Pydantic 검증
- 간단한 데코레이터 기반 API
- FastMCP로 빠른 시작 가능

**추천 대상:**

- Python 서버 애플리케이션
- 데이터 과학 및 ML 통합
- 스크립팅 및 자동화

**시작하기:**

```bash
pip install mcp
```

---

### 3. Go SDK

**GitHub**: https://github.com/modelcontextprotocol/go-sdk

**특징:**

- 네이티브 Go 관용구
- 고루틴 기반 동시성
- 강력한 타입 시스템
- 높은 성능

**추천 대상:**

- 고성능 서버
- 시스템 프로그래밍
- 클라우드 네이티브 애플리케이션

**시작하기:**

```bash
go get github.com/modelcontextprotocol/go-sdk
```

---

### 4. Kotlin SDK

**GitHub**: https://github.com/modelcontextprotocol/kotlin-sdk

**특징:**

- 코루틴 기반 비동기
- 널 안전성
- JVM 호환성
- 함수형 프로그래밍 지원

**추천 대상:**

- Android 애플리케이션
- JVM 기반 서버
- Kotlin 멀티플랫폼 프로젝트

**시작하기:**

```kotlin
implementation("io.modelcontextprotocol:kotlin-sdk:0.4.0")
```

---

### 5. Swift SDK

**GitHub**: https://github.com/modelcontextprotocol/swift-sdk

**특징:**

- Swift Concurrency (async/await)
- 타입 안전성
- iOS/macOS 네이티브 통합
- SwiftUI 친화적

**추천 대상:**

- iOS 애플리케이션
- macOS 데스크톱 앱
- Apple 생태계 통합

**시작하기:**

```swift
.package(url: "https://github.com/modelcontextprotocol/swift-sdk", from: "0.1.0")
```

---

### 6. Java SDK

**GitHub**: https://github.com/modelcontextprotocol/java-sdk

**특징:**

- Spring Boot 통합
- 동기 및 비동기 API
- 엔터프라이즈급 기능
- Maven/Gradle 지원

**추천 대상:**

- 엔터프라이즈 Java 애플리케이션
- Spring Boot 프로젝트
- 레거시 Java 시스템 통합

**시작하기:**

```xml
<dependency>
    <groupId>org.springframework.ai</groupId>
    <artifactId>spring-ai-starter-mcp-server</artifactId>
</dependency>
```

---

### 7. C# SDK

**GitHub**: https://github.com/modelcontextprotocol/csharp-sdk

**특징:**

- .NET Core/.NET Framework 지원
- async/await 패턴
- NuGet 패키지 관리
- Microsoft.Extensions.AI 통합

**추천 대상:**

- .NET 애플리케이션
- Windows 데스크톱 앱
- Azure 클라우드 서비스

**시작하기:**

```bash
dotnet add package ModelContextProtocol --prerelease
```

---

### 8. Ruby SDK

**GitHub**: https://github.com/modelcontextprotocol/ruby-sdk

**특징:**

- Ruby 관용구
- 블록 기반 API
- Gem 패키지
- Rails 통합 가능

**추천 대상:**

- Ruby on Rails 애플리케이션
- 스크립팅
- 웹 애플리케이션

**시작하기:**

```ruby
gem install mcp
```

---

### 9. Rust SDK

**GitHub**: https://github.com/modelcontextprotocol/rust-sdk

**특징:**

- 메모리 안전성
- 제로 비용 추상화
- async/await 지원
- 높은 성능

**추천 대상:**

- 고성능 시스템
- 임베디드 시스템
- 시스템 프로그래밍

**시작하기:**

```toml
[dependencies]
rmcp = { version = "0.3", features = ["server", "macros", "transport-io"] }
```

---

### 10. PHP SDK

**GitHub**: https://github.com/modelcontextprotocol/php-sdk

**특징:**

- PSR 표준 준수
- Composer 패키지
- Laravel/Symfony 통합
- PHP 8+ 타입 시스템

**추천 대상:**

- PHP 웹 애플리케이션
- Laravel/Symfony 프로젝트
- WordPress 플러그인

**시작하기:**

```bash
composer require modelcontextprotocol/php-sdk
```

---

## SDK 공통 기능

모든 SDK는 동일한 핵심 기능을 제공하지만 각 언어의 관용구와 모범 사례를 따릅니다.

### 1. MCP 서버 생성

**기능:**

- 도구(Tools) 노출
- 리소스(Resources) 제공
- 프롬프트(Prompts) 정의
- 서버 기능 구성

**예시 (Python):**

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("my-server")

@mcp.tool()
async def my_tool(arg: str) -> str:
    return f"Processed: {arg}"
```

**예시 (TypeScript):**

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";

const server = new McpServer({
  name: "my-server",
  version: "1.0.0",
});

server.registerTool("my_tool", { ... }, async (args) => {
  return { content: [{ type: "text", text: "Result" }] };
});
```

---

### 2. MCP 클라이언트 구축

**기능:**

- 모든 MCP 서버에 연결
- 도구 호출
- 리소스 읽기
- 프롬프트 사용

**예시 (Python):**

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        tools = await session.list_tools()
```

**예시 (TypeScript):**

```typescript
import { Client } from "@modelcontextprotocol/sdk/client/index.js";

const client = new Client({ name: "my-client", version: "1.0.0" });
await client.connect(transport);
const tools = await client.listTools();
```

---

### 3. 전송 프로토콜 지원

**로컬 전송 (STDIO):**

- 표준 입력/출력 사용
- 프로세스 간 통신
- 로컬 서버 연결에 적합

**원격 전송 (HTTP/SSE):**

- HTTP 기반 통신
- Server-Sent Events
- 원격 서버 연결에 적합

---

### 4. 프로토콜 준수

**타입 안전성:**

- 자동 타입 검증
- 스키마 기반 검증
- JSON-RPC 2.0 준수

**오류 처리:**

- 표준 오류 코드
- 명확한 오류 메시지
- 재시도 로직 지원

---

## SDK 선택 가이드

### 언어별 추천

|사용 사례|추천 SDK|이유|
|---|---|---|
|웹 서버|TypeScript, Python|풍부한 웹 프레임워크 생태계|
|모바일 앱|Swift (iOS), Kotlin (Android)|네이티브 플랫폼 통합|
|데스크톱 앱|C# (.NET), Swift (macOS)|플랫폼 네이티브 UI|
|고성능 서버|Go, Rust|낮은 오버헤드, 높은 동시성|
|엔터프라이즈|Java, C#|기존 인프라 통합|
|스크립팅|Python, Ruby|빠른 프로토타이핑|
|시스템 프로그래밍|Rust, Go|메모리 안전성, 성능|

---

### 고려 사항

#### 1. 성능 요구사항

**높은 처리량 필요:**

- Go, Rust - 네이티브 컴파일, 낮은 오버헤드
- C# - JIT 최적화

**중간 처리량:**

- TypeScript (Node.js) - 이벤트 루프 기반
- Python - asyncio 지원

#### 2. 개발 속도

**빠른 프로토타이핑:**

- Python - FastMCP로 신속한 개발
- TypeScript - 풍부한 라이브러리

**안정적인 개발:**

- Java, C# - 강력한 타입 시스템
- Kotlin - 간결한 구문 + 타입 안전성

#### 3. 생태계 통합

**기존 스택:**

- Java → Spring Boot 통합
- Python → 데이터 과학 라이브러리
- TypeScript → Node.js 생태계
- C# → .NET 플랫폼

#### 4. 팀 경험

**팀의 전문성:**

- 기존 언어 경험 활용
- 학습 곡선 고려
- 도구 및 인프라 재사용

---

## 시작하기

### 1단계: SDK 선택

위의 가이드를 참조하여 프로젝트에 가장 적합한 SDK를 선택합니다.

### 2단계: 설치

선택한 언어의 패키지 매니저를 사용하여 SDK를 설치합니다.

### 3단계: 튜토리얼 따라하기

각 SDK의 GitHub 저장소에는 다음이 포함되어 있습니다:

- 📚 상세한 문서
- 💡 예제 코드
- 🚀 빠른 시작 가이드
- 🔧 API 참조

### 4단계: 예제 실행

공식 예제를 실행하여 SDK의 기능을 탐색합니다:

- 기본 서버 구축
- 클라이언트 연결
- 도구 구현
- 리소스 제공

---

## 다음 단계

MCP로 구축을 시작할 준비가 되셨나요? 경로를 선택하세요:

### 1. 서버 구축

**MCP 서버를 만드는 방법 학습**

- [서버 구축 가이드](https://claude.ai/docs/develop/build-server)
- 도구, 리소스, 프롬프트 구현
- 로컬 및 원격 서버 배포

### 2. 클라이언트 구축

**MCP 서버에 연결하는 애플리케이션 생성**

- [클라이언트 구축 가이드](https://claude.ai/docs/develop/build-client)
- 서버와 통신
- 도구 호출 및 리소스 사용

### 3. 보안

**MCP 애플리케이션 보안**

- [보안 가이드](https://claude.ai/docs/tutorials/security/authorization)
- 인증 및 권한 부여
- 모범 사례

---

## SDK 비교표

|SDK|버전|비동기|타입 안전|성능|학습 곡선|생태계|
|---|---|---|---|---|---|---|
|TypeScript|1.0+|✅|✅|⭐⭐⭐|⭐⭐|⭐⭐⭐⭐⭐|
|Python|1.0+|✅|✅|⭐⭐|⭐|⭐⭐⭐⭐⭐|
|Go|0.x|✅|✅|⭐⭐⭐⭐⭐|⭐⭐⭐|⭐⭐⭐|
|Kotlin|0.4+|✅|✅|⭐⭐⭐⭐|⭐⭐|⭐⭐⭐|
|Swift|0.1+|✅|✅|⭐⭐⭐⭐|⭐⭐⭐|⭐⭐|
|Java|1.0+|✅|✅|⭐⭐⭐⭐|⭐⭐⭐|⭐⭐⭐⭐|
|C#|0.x|✅|✅|⭐⭐⭐⭐|⭐⭐|⭐⭐⭐⭐|
|Ruby|0.x|⚠️|⚠️|⭐⭐|⭐|⭐⭐⭐|
|Rust|0.3+|✅|✅|⭐⭐⭐⭐⭐|⭐⭐⭐⭐|⭐⭐|
|PHP|0.x|⚠️|✅|⭐⭐|⭐⭐|⭐⭐⭐|

**범례:**

- ⭐⭐⭐⭐⭐ = 최고
- ⭐ = 기본
- ✅ = 완전 지원
- ⚠️ = 부분 지원

---

## 커뮤니티 및 지원

### 도움 받기

**공식 리소스:**

- 📖 [공식 문서](https://modelcontextprotocol.io/docs)
- 💬 [GitHub Discussions](https://github.com/modelcontextprotocol/discussions)
- 🐛 [Issue Tracker](https://github.com/modelcontextprotocol/issues)

**커뮤니티:**

- 질문하기
- 예제 공유
- 기여하기

### 기여하기

모든 SDK는 오픈 소스이며 기여를 환영합니다:

- 버그 수정
- 기능 추가
- 문서 개선
- 예제 제공

---

## 요약

MCP SDK는 다양한 언어로 MCP 서버와 클라이언트를 구축할 수 있는 강력한 도구를 제공합니다.

**핵심 장점:**

- ✅ 10개 언어 지원
- ✅ 동일한 기능, 언어별 관용구
- ✅ 완전한 프로토콜 준수
- ✅ 타입 안전성 및 검증
- ✅ 로컬 및 원격 전송
- ✅ 활발한 개발 및 지원

**선택 기준:**

1. 팀의 언어 경험
2. 성능 요구사항
3. 기존 스택 통합
4. 생태계 및 라이브러리

원하는 언어의 SDK를 선택하고 MCP로 강력한 AI 애플리케이션을 구축하세요!

---

## 추가 리소스

- **공식 사이트**: https://modelcontextprotocol.io
- **GitHub 조직**: https://github.com/modelcontextprotocol
- **예제 서버**: [Examples](https://claude.ai/examples)
- **예제 클라이언트**: [Clients](https://claude.ai/clients)
- **사양**: [Specification](https://claude.ai/specification/2025-11-25)

---

_이 문서는 Model Context Protocol 공식 문서에서 가져온 내용입니다._