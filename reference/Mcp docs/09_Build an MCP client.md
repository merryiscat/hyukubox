# MCP 클라이언트 구축하기

## 개요

모든 MCP 서버와 통합할 수 있는 자체 클라이언트 구축을 시작합니다.

이 튜토리얼에서는 MCP 서버에 연결하는 LLM 기반 챗봇 클라이언트를 구축하는 방법을 배웁니다.

> **권장 사항**: 시작하기 전에 [MCP 서버 구축](https://claude.ai/docs/develop/build-server) 튜토리얼을 먼저 진행하면 클라이언트와 서버가 어떻게 통신하는지 이해하는 데 도움이 됩니다.

---

## 지원 언어

이 가이드는 다음 언어로 클라이언트를 구축하는 방법을 제공합니다:

- [Python](https://claude.ai/chat/d1892e31-8053-4913-8394-fadb47edcd3a#python-%EA%B5%AC%ED%98%84)
- [TypeScript](https://claude.ai/chat/d1892e31-8053-4913-8394-fadb47edcd3a#typescript-%EA%B5%AC%ED%98%84)
- [Java](https://claude.ai/chat/d1892e31-8053-4913-8394-fadb47edcd3a#java-%EA%B5%AC%ED%98%84)
- [Kotlin](https://claude.ai/chat/d1892e31-8053-4913-8394-fadb47edcd3a#kotlin-%EA%B5%AC%ED%98%84)
- [C#](https://claude.ai/chat/d1892e31-8053-4913-8394-fadb47edcd3a#c-%EA%B5%AC%ED%98%84)

---

## Python 구현

### 완성된 코드

[GitHub에서 완성된 코드 보기](https://github.com/modelcontextprotocol/quickstart-resources/tree/main/mcp-client-python)

### 시스템 요구사항

- Mac 또는 Windows 컴퓨터
- 최신 Python 버전 설치
- 최신 버전의 `uv` 설치

### 환경 설정

#### 1. Python 프로젝트 생성

**macOS/Linux:**

```bash
# 프로젝트 디렉토리 생성
uv init mcp-client
cd mcp-client

# 가상 환경 생성
uv venv

# 가상 환경 활성화
source .venv/bin/activate

# 필요한 패키지 설치
uv add mcp anthropic python-dotenv

# 보일러플레이트 파일 제거
rm main.py

# 메인 파일 생성
touch client.py
```

**Windows:**

```bash
uv init mcp-client
cd mcp-client
uv venv
.venv\Scripts\activate
uv add mcp anthropic python-dotenv
del main.py
New-Item client.py
```

#### 2. API 키 설정

[Anthropic Console](https://console.anthropic.com/settings/keys)에서 Anthropic API 키가 필요합니다.

`.env` 파일 생성:

```bash
echo "ANTHROPIC_API_KEY=your-api-key-goes-here" > .env
```

`.gitignore`에 `.env` 추가:

```bash
echo ".env" >> .gitignore
```

> **보안**: `ANTHROPIC_API_KEY`를 안전하게 보관하세요!

---

### 클라이언트 생성

#### 1. 기본 클라이언트 구조

먼저 imports를 설정하고 기본 클라이언트 클래스를 생성합니다:

```python
import asyncio
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()  # .env에서 환경 변수 로드

class MCPClient:
    def __init__(self):
        # 세션 및 클라이언트 객체 초기화
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.anthropic = Anthropic()
    # 메서드는 여기에 추가됩니다
```

#### 2. 서버 연결 관리

MCP 서버에 연결하는 메서드를 구현합니다:

```python
async def connect_to_server(self, server_script_path: str):
    """MCP 서버에 연결

    Args:
        server_script_path: 서버 스크립트 경로 (.py 또는 .js)
    """
    is_python = server_script_path.endswith('.py')
    is_js = server_script_path.endswith('.js')
    if not (is_python or is_js):
        raise ValueError("Server script must be a .py or .js file")

    command = "python" if is_python else "node"
    server_params = StdioServerParameters(
        command=command,
        args=[server_script_path],
        env=None
    )

    stdio_transport = await self.exit_stack.enter_async_context(
        stdio_client(server_params)
    )
    self.stdio, self.write = stdio_transport
    self.session = await self.exit_stack.enter_async_context(
        ClientSession(self.stdio, self.write)
    )

    await self.session.initialize()

    # 사용 가능한 도구 나열
    response = await self.session.list_tools()
    tools = response.tools
    print("\nConnected to server with tools:", [tool.name for tool in tools])
```

#### 3. 쿼리 처리 로직

쿼리 처리 및 도구 호출을 처리하는 핵심 기능을 추가합니다:

```python
async def process_query(self, query: str) -> str:
    """Claude 및 사용 가능한 도구를 사용하여 쿼리 처리"""
    messages = [
        {
            "role": "user",
            "content": query
        }
    ]

    response = await self.session.list_tools()
    available_tools = [{
        "name": tool.name,
        "description": tool.description,
        "input_schema": tool.inputSchema
    } for tool in response.tools]

    # 초기 Claude API 호출
    response = self.anthropic.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=messages,
        tools=available_tools
    )

    # 응답 처리 및 도구 호출 처리
    final_text = []

    assistant_message_content = []
    for content in response.content:
        if content.type == 'text':
            final_text.append(content.text)
            assistant_message_content.append(content)
        elif content.type == 'tool_use':
            tool_name = content.name
            tool_args = content.input

            # 도구 호출 실행
            result = await self.session.call_tool(tool_name, tool_args)
            final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")

            assistant_message_content.append(content)
            messages.append({
                "role": "assistant",
                "content": assistant_message_content
            })
            messages.append({
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": content.id,
                        "content": result.content
                    }
                ]
            })

            # Claude로부터 다음 응답 가져오기
            response = self.anthropic.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                messages=messages,
                tools=available_tools
            )

            final_text.append(response.content[0].text)

    return "\n".join(final_text)
```

#### 4. 대화형 채팅 인터페이스

채팅 루프 및 정리 기능을 추가합니다:

```python
async def chat_loop(self):
    """대화형 채팅 루프 실행"""
    print("\nMCP Client Started!")
    print("Type your queries or 'quit' to exit.")

    while True:
        try:
            query = input("\nQuery: ").strip()

            if query.lower() == 'quit':
                break

            response = await self.process_query(query)
            print("\n" + response)

        except Exception as e:
            print(f"\nError: {str(e)}")

async def cleanup(self):
    """리소스 정리"""
    await self.exit_stack.aclose()
```

#### 5. 메인 진입점

메인 실행 로직을 추가합니다:

```python
async def main():
    if len(sys.argv) < 2:
        print("Usage: python client.py <path_to_server_script>")
        sys.exit(1)

    client = MCPClient()
    try:
        await client.connect_to_server(sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    import sys
    asyncio.run(main())
```

완전한 `client.py` 파일은 [여기](https://github.com/modelcontextprotocol/quickstart-resources/blob/main/mcp-client-python/client.py)에서 찾을 수 있습니다.

---

### 클라이언트 실행

MCP 서버와 함께 클라이언트를 실행하려면:

```bash
uv run client.py path/to/server.py # python 서버
uv run client.py path/to/build/index.js # node 서버
```

**날씨 서버 예제:**

```bash
python client.py .../quickstart-resources/weather-server-python/weather.py
```

**클라이언트 동작:**

1. 지정된 서버에 연결
2. 사용 가능한 도구 나열
3. 대화형 채팅 세션 시작
    - 쿼리 입력
    - 도구 실행 확인
    - Claude의 응답 받기

---

## TypeScript 구현

### 완성된 코드

[GitHub에서 완성된 코드 보기](https://github.com/modelcontextprotocol/quickstart-resources/tree/main/mcp-client-typescript)

### 시스템 요구사항

- Mac 또는 Windows 컴퓨터
- Node.js 17 이상 설치
- 최신 버전의 `npm` 설치
- Anthropic API 키 (Claude)

### 환경 설정

#### 1. 프로젝트 생성 및 설정

**macOS/Linux:**

```bash
# 프로젝트 디렉토리 생성
mkdir mcp-client-typescript
cd mcp-client-typescript

# npm 프로젝트 초기화
npm init -y

# 의존성 설치
npm install @anthropic-ai/sdk @modelcontextprotocol/sdk dotenv

# dev 의존성 설치
npm install -D @types/node typescript

# 소스 파일 생성
touch index.ts
```

**Windows:**

```bash
mkdir mcp-client-typescript
cd mcp-client-typescript
npm init -y
npm install @anthropic-ai/sdk @modelcontextprotocol/sdk dotenv
npm install -D @types/node typescript
New-Item index.ts
```

#### 2. package.json 업데이트

`type: "module"` 및 빌드 스크립트 추가:

```json
{
  "type": "module",
  "scripts": {
    "build": "tsc && chmod 755 build/index.js"
  }
}
```

#### 3. tsconfig.json 생성

프로젝트 루트에 생성:

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "Node16",
    "moduleResolution": "Node16",
    "outDir": "./build",
    "rootDir": "./",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  },
  "include": ["index.ts"],
  "exclude": ["node_modules"]
}
```

#### 4. API 키 설정

`.env` 파일 생성:

```bash
echo "ANTHROPIC_API_KEY=<your key here>" > .env
```

`.gitignore`에 추가:

```bash
echo ".env" >> .gitignore
```

---

### 클라이언트 생성

#### 1. 기본 클라이언트 구조

`index.ts`에서 imports를 설정하고 기본 클라이언트 클래스를 생성합니다:

```typescript
import { Anthropic } from "@anthropic-ai/sdk";
import {
  MessageParam,
  Tool,
} from "@anthropic-ai/sdk/resources/messages/messages.mjs";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import readline from "readline/promises";
import dotenv from "dotenv";

dotenv.config();

const ANTHROPIC_API_KEY = process.env.ANTHROPIC_API_KEY;
if (!ANTHROPIC_API_KEY) {
  throw new Error("ANTHROPIC_API_KEY is not set");
}

class MCPClient {
  private mcp: Client;
  private anthropic: Anthropic;
  private transport: StdioClientTransport | null = null;
  private tools: Tool[] = [];

  constructor() {
    this.anthropic = new Anthropic({
      apiKey: ANTHROPIC_API_KEY,
    });
    this.mcp = new Client({ name: "mcp-client-cli", version: "1.0.0" });
  }
  // 메서드는 여기에 추가됩니다
}
```

#### 2. 서버 연결 관리

```typescript
async connectToServer(serverScriptPath: string) {
  try {
    const isJs = serverScriptPath.endsWith(".js");
    const isPy = serverScriptPath.endsWith(".py");
    if (!isJs && !isPy) {
      throw new Error("Server script must be a .js or .py file");
    }
    const command = isPy
      ? process.platform === "win32"
        ? "python"
        : "python3"
      : process.execPath;

    this.transport = new StdioClientTransport({
      command,
      args: [serverScriptPath],
    });
    await this.mcp.connect(this.transport);

    const toolsResult = await this.mcp.listTools();
    this.tools = toolsResult.tools.map((tool) => {
      return {
        name: tool.name,
        description: tool.description,
        input_schema: tool.inputSchema,
      };
    });
    console.log(
      "Connected to server with tools:",
      this.tools.map(({ name }) => name)
    );
  } catch (e) {
    console.log("Failed to connect to MCP server: ", e);
    throw e;
  }
}
```

#### 3. 쿼리 처리 로직

```typescript
async processQuery(query: string) {
  const messages: MessageParam[] = [
    {
      role: "user",
      content: query,
    },
  ];

  const response = await this.anthropic.messages.create({
    model: "claude-sonnet-4-20250514",
    max_tokens: 1000,
    messages,
    tools: this.tools,
  });

  const finalText = [];

  for (const content of response.content) {
    if (content.type === "text") {
      finalText.push(content.text);
    } else if (content.type === "tool_use") {
      const toolName = content.name;
      const toolArgs = content.input as { [x: string]: unknown } | undefined;

      const result = await this.mcp.callTool({
        name: toolName,
        arguments: toolArgs,
      });
      finalText.push(
        `[Calling tool ${toolName} with args ${JSON.stringify(toolArgs)}]`
      );

      messages.push({
        role: "user",
        content: result.content as string,
      });

      const response = await this.anthropic.messages.create({
        model: "claude-sonnet-4-20250514",
        max_tokens: 1000,
        messages,
      });

      finalText.push(
        response.content[0].type === "text" ? response.content[0].text : ""
      );
    }
  }

  return finalText.join("\n");
}
```

#### 4. 대화형 인터페이스

```typescript
async chatLoop() {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  try {
    console.log("\nMCP Client Started!");
    console.log("Type your queries or 'quit' to exit.");

    while (true) {
      const message = await rl.question("\nQuery: ");
      if (message.toLowerCase() === "quit") {
        break;
      }
      const response = await this.processQuery(message);
      console.log("\n" + response);
    }
  } finally {
    rl.close();
  }
}

async cleanup() {
  await this.mcp.close();
}
```

#### 5. 메인 진입점

```typescript
async function main() {
  if (process.argv.length < 3) {
    console.log("Usage: node index.ts <path_to_server_script>");
    return;
  }
  const mcpClient = new MCPClient();
  try {
    await mcpClient.connectToServer(process.argv[2]);
    await mcpClient.chatLoop();
  } catch (e) {
    console.error("Error:", e);
    await mcpClient.cleanup();
    process.exit(1);
  } finally {
    await mcpClient.cleanup();
    process.exit(0);
  }
}

main();
```

---

### 클라이언트 실행

```bash
# TypeScript 빌드
npm run build

# 클라이언트 실행
node build/index.js path/to/server.py # python 서버
node build/index.js path/to/build/index.js # node 서버
```

**날씨 서버 예제:**

```bash
node build/index.js .../quickstart-resources/weather-server-typescript/build/index.js
```

---

## 주요 구성 요소 설명

### 1. 클라이언트 초기화

- `MCPClient` 클래스는 세션 관리 및 API 클라이언트로 초기화
- 적절한 리소스 관리를 위해 `AsyncExitStack` (Python) 또는 적절한 정리 메커니즘 사용
- Claude 상호작용을 위한 Anthropic 클라이언트 구성

### 2. 서버 연결

- Python 및 Node.js 서버 모두 지원
- 서버 스크립트 타입 검증
- 적절한 통신 채널 설정
- 세션 초기화 및 사용 가능한 도구 나열

### 3. 쿼리 처리

- 대화 컨텍스트 유지
- Claude의 응답 및 도구 호출 처리
- Claude와 도구 간의 메시지 흐름 관리
- 결과를 일관된 응답으로 결합

### 4. 대화형 인터페이스

- 간단한 명령줄 인터페이스 제공
- 사용자 입력 처리 및 응답 표시
- 기본 오류 처리 포함
- 우아한 종료 허용

### 5. 리소스 관리

- 리소스의 적절한 정리
- 연결 문제에 대한 오류 처리
- 우아한 종료 절차

---

## 작동 방식

쿼리를 제출하면:

1. **클라이언트**가 서버에서 사용 가능한 도구 목록을 가져옴
2. **쿼리**가 도구 설명과 함께 Claude에 전송됨
3. **Claude**가 사용할 도구(있는 경우)를 결정
4. **클라이언트**가 서버를 통해 요청된 도구 호출을 실행
5. **결과**가 Claude로 다시 전송됨
6. **Claude**가 자연어 응답을 제공
7. **응답**이 표시됨

---

## 일반적인 사용자 정의 지점

### 1. 도구 처리

- `process_query()`를 수정하여 특정 도구 타입 처리
- 도구 호출을 위한 사용자 정의 오류 처리 추가
- 도구별 응답 형식화 구현

### 2. 응답 처리

- 도구 결과 형식화 방법 사용자 정의
- 응답 필터링 또는 변환 추가
- 사용자 정의 로깅 구현

### 3. 사용자 인터페이스

- GUI 또는 웹 인터페이스 추가
- 풍부한 콘솔 출력 구현
- 명령 기록 또는 자동 완성 추가

---

## 모범 사례

### 1. 오류 처리

- 항상 도구 호출을 try-catch 블록으로 래핑
- 의미 있는 오류 메시지 제공
- 연결 문제를 우아하게 처리

### 2. 리소스 관리

- 적절한 정리를 위해 `AsyncExitStack` (Python) 사용
- 완료되면 연결 닫기
- 서버 연결 해제 처리

### 3. 보안

- `.env`에 API 키를 안전하게 저장
- 서버 응답 검증
- 도구 권한에 주의

### 4. 도구 이름

- 도구 이름은 [여기](https://claude.ai/specification/draft/server/tools#tool-names)에 지정된 형식에 따라 검증 가능
- 도구 이름이 지정된 형식을 준수하면 MCP 클라이언트의 검증에 실패하지 않아야 함

---

## 문제 해결

### 서버 경로 문제

**문제:**

- 서버 스크립트 경로가 올바르지 않음

**해결 방법:**

- 서버 스크립트 경로가 올바른지 다시 확인
- 상대 경로가 작동하지 않으면 절대 경로 사용
- Windows 사용자는 경로에 슬래시(`/`) 또는 이스케이프된 백슬래시(`\\`) 사용
- 서버 파일 확장자가 올바른지 확인 (Python은 `.py`, Node.js는 `.js`)

**올바른 경로 사용 예시:**

```bash
# 상대 경로
uv run client.py ./server/weather.py

# 절대 경로
uv run client.py /Users/username/projects/mcp-server/weather.py

# Windows 경로 (두 형식 모두 작동)
uv run client.py C:/projects/mcp-server/weather.py
uv run client.py C:\\projects\\mcp-server\\weather.py
```

### 응답 시간

**정상적인 동작:**

- 첫 번째 응답은 최대 30초가 걸릴 수 있음
- 이는 정상이며 다음과 같은 이유로 발생:
    - 서버 초기화
    - Claude가 쿼리 처리
    - 도구가 실행 중

**권장사항:**

- 후속 응답은 일반적으로 더 빠름
- 초기 대기 기간 동안 프로세스를 중단하지 마세요

### 일반적인 오류 메시지

**오류별 해결 방법:**

- **`FileNotFoundError`**: 서버 경로 확인
- **`Connection refused`**: 서버가 실행 중이고 경로가 올바른지 확인
- **`Tool execution failed`**: 도구의 필수 환경 변수가 설정되었는지 확인
- **`Timeout error`**: 클라이언트 구성에서 타임아웃 증가 고려
- **`ANTHROPIC_API_KEY is not set`**: `.env` 파일 및 환경 변수 확인
- **TypeScript `Error: Cannot find module`**: 빌드 폴더 확인 및 TypeScript 컴파일 성공 여부 확인
- **`BadRequestError`**: Anthropic API에 액세스하기에 충분한 크레딧이 있는지 확인

---

## 다른 언어 구현

이 문서에서는 Python과 TypeScript 구현을 자세히 다뤘습니다. 다른 언어의 구현은 다음을 참조하세요:

### Java 구현

**Spring AI MCP 기반 웹 검색 챗봇**

Brave Search MCP 서버와 결합된 Spring AI의 Model Context Protocol을 사용하는 대화형 챗봇입니다.

- [완성된 코드](https://github.com/spring-projects/spring-ai-examples/tree/main/model-context-protocol/web-search/brave-chatbot)
- Spring AI MCP auto-configuration 및 boot starters 기반
- [Java SDK Client 문서](https://claude.ai/sdk/java/mcp-client)

### Kotlin 구현

- [완성된 코드](https://github.com/modelcontextprotocol/kotlin-sdk/tree/main/samples/kotlin-mcp-client)
- Kotlin 관용구 및 코루틴 사용
- Java 17 이상 필요

### C# 구현

- [완성된 코드](https://github.com/modelcontextprotocol/csharp-sdk/tree/main/samples/QuickstartClient)
- .NET 8.0 이상 필요
- Microsoft.Extensions.AI 활용

각 구현은 유사한 패턴을 따르지만 언어별 관용구와 모범 사례를 사용합니다.

---

## 다음 단계

### 1. 예제 서버 확인

**공식 MCP 서버 및 구현 갤러리 확인**

- [Examples](https://claude.ai/examples)

### 2. 예제 클라이언트 보기

**MCP 통합을 지원하는 클라이언트 목록 보기**

- [Clients](https://claude.ai/clients)

### 3. 서버 구축

**MCP 서버 구축 방법 학습**

- [서버 구축 가이드](https://claude.ai/docs/develop/build-server)

### 4. SDK 문서

**언어별 SDK 문서 확인**

- [SDKs](https://claude.ai/docs/sdk)

---

## 요약

이 가이드를 통해:

✅ MCP 클라이언트의 핵심 개념 이해 ✅ LLM 기반 챗봇 클라이언트 구축 ✅ MCP 서버 연결 방법 학습 ✅ 도구 호출 및 응답 처리 구현 ✅ 대화형 인터페이스 생성 ✅ 일반적인 문제 해결 방법 이해

이제 모든 MCP 서버와 통합할 수 있는 강력한 클라이언트를 구축할 수 있습니다!

---

## 추가 리소스

- **공식 문서**: https://modelcontextprotocol.io/docs
- **GitHub 저장소**: https://github.com/modelcontextprotocol
- **예제 코드**:
    - [Python 클라이언트](https://github.com/modelcontextprotocol/quickstart-resources/tree/main/mcp-client-python)
    - [TypeScript 클라이언트](https://github.com/modelcontextprotocol/quickstart-resources/tree/main/mcp-client-typescript)
- **SDK 문서**: [SDKs](https://claude.ai/docs/sdk)

---

_이 문서는 Model Context Protocol 공식 문서에서 가져온 내용입니다._