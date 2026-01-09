# 개요

<Info>**Protocol Revision**: 2025-11-25</Info>

서버는 MCP를 통해 언어 모델에 컨텍스트를 추가하기 위한 기본 빌딩 블록을 제공합니다. 이러한 원시 요소들은 클라이언트, 서버, 그리고 언어 모델 간의 풍부한 상호작용을 가능하게 합니다:

* **Prompts**: 언어 모델 상호작용을 안내하는 사전 정의된 템플릿 또는 지시문
* **Resources**: 모델에 추가 컨텍스트를 제공하는 구조화된 데이터 또는 콘텐츠
* **Tools**: 모델이 행동을 수행하거나 정보를 검색할 수 있게 하는 실행 가능한 함수

각 원시 요소는 다음과 같은 제어 계층 구조로 요약될 수 있습니다:

| Primitive | Control                | Description                                        | Example                         |
| --------- | ---------------------- | -------------------------------------------------- | ------------------------------- |
| Prompts   | User-controlled        | 사용자가 선택하여 호출하는 인터랙티브 템플릿       | 슬래시 명령, 메뉴 옵션          |
| Resources | Application-controlled | 클라이언트가 첨부하고 관리하는 컨텍스트 데이터      | 파일 내용, git 히스토리         |
| Tools     | Model-controlled       | LLM에 노출되어 행동을 수행하게 하는 함수           | API POST 요청, 파일 쓰기        |

아래에서 이러한 핵심 원시 요소들을 자세히 살펴보세요:

<CardGroup cols={3}>
  <Card title="Prompts" icon="message" href="/specification/2025-11-25/server/prompts" />

  <Card title="Resources" icon="file-lines" href="/specification/2025-11-25/server/resources" />

  <Card title="Tools" icon="wrench" href="/specification/2025-11-25/server/tools" />
</CardGroup>


---

> 이 문서에서 탐색 및 기타 페이지를 찾으려면 다음 주소에서 llms.txt 파일을 가져오세요: https://modelcontextprotocol.io/llms.txt