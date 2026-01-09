# MCP 서버 이해하기

## 개요

MCP 서버는 표준화된 프로토콜 인터페이스를 통해 AI 애플리케이션에 특정 기능을 제공하는 프로그램입니다.

**일반적인 예시:**

- **파일 시스템 서버**: 문서 접근
- **데이터베이스 서버**: 데이터 쿼리
- **GitHub 서버**: 코드 관리
- **Slack 서버**: 팀 커뮤니케이션
- **캘린더 서버**: 일정 관리

---

## 서버의 핵심 기능

서버는 세 가지 구성 요소를 통해 기능을 제공합니다:

|기능|설명|예시|누가 제어하는가|
|---|---|---|---|
|**Tools (도구)**|LLM이 능동적으로 호출할 수 있는 함수. LLM이 사용자 요청에 따라 사용 시기를 결정. 데이터베이스에 쓰기, 외부 API 호출, 파일 수정 또는 기타 로직 트리거 가능|항공편 검색<br/>메시지 전송<br/>캘린더 이벤트 생성|모델 (Model)|
|**Resources (리소스)**|파일 내용, 데이터베이스 스키마, API 문서 등 컨텍스트를 위한 정보에 읽기 전용 접근을 제공하는 수동적 데이터 소스|문서 검색<br/>지식 베이스 접근<br/>캘린더 읽기|애플리케이션 (Application)|
|**Prompts (프롬프트)**|특정 도구와 리소스를 사용하도록 모델에게 지시하는 사전 구축된 명령 템플릿|휴가 계획<br/>미팅 요약<br/>이메일 초안 작성|사용자 (User)|

이 문서에서는 가상의 시나리오를 사용하여 각 기능의 역할을 설명하고, 이들이 어떻게 함께 작동하는지 보여줍니다.

---

## 1. Tools (도구)

### 개요

도구는 AI 모델이 작업을 수행할 수 있게 합니다. 각 도구는 타입이 지정된 입력과 출력을 가진 특정 작업을 정의합니다. 모델은 컨텍스트에 따라 도구 실행을 요청합니다.

### 도구의 작동 방식

도구는 LLM이 호출할 수 있는 스키마 정의 인터페이스입니다. MCP는 검증을 위해 JSON Schema를 사용합니다.

**핵심 특징:**

- 각 도구는 명확하게 정의된 입력과 출력을 가진 단일 작업 수행
- 도구는 실행 전 사용자 동의를 요구할 수 있음
- 사용자가 모델이 수행하는 작업에 대한 제어권을 유지하도록 보장

#### 프로토콜 작업

|메서드|목적|반환값|
|---|---|---|
|`tools/list`|사용 가능한 도구 발견|스키마가 포함된 도구 정의 배열|
|`tools/call`|특정 도구 실행|도구 실행 결과|

#### 도구 정의 예시

```json
{
  "name": "searchFlights",
  "description": "Search for available flights",
  "inputSchema": {
    "type": "object",
    "properties": {
      "origin": { 
        "type": "string", 
        "description": "Departure city" 
      },
      "destination": { 
        "type": "string", 
        "description": "Arrival city" 
      },
      "date": { 
        "type": "string", 
        "format": "date", 
        "description": "Travel date" 
      }
    },
    "required": ["origin", "destination", "date"]
  }
}
```

---

### 예제: 여행 예약

도구를 통해 AI 애플리케이션은 사용자를 대신하여 작업을 수행할 수 있습니다. 여행 계획 시나리오에서 AI 애플리케이션은 여러 도구를 사용하여 휴가 예약을 도울 수 있습니다:

#### 1. 항공편 검색

```javascript
searchFlights(
  origin: "NYC", 
  destination: "Barcelona", 
  date: "2024-06-15"
)
```

여러 항공사를 쿼리하고 구조화된 항공편 옵션을 반환합니다.

#### 2. 캘린더 차단

```javascript
createCalendarEvent(
  title: "Barcelona Trip", 
  startDate: "2024-06-15", 
  endDate: "2024-06-22"
)
```

사용자의 캘린더에 여행 날짜를 표시합니다.

#### 3. 이메일 알림

```javascript
sendEmail(
  to: "[email protected]", 
  subject: "Out of Office", 
  body: "..."
)
```

동료들에게 자동 부재 중 메시지를 보냅니다.

---

### 사용자 상호작용 모델

도구는 **모델 제어형**입니다. 즉, AI 모델이 자동으로 도구를 발견하고 호출할 수 있습니다. 그러나 MCP는 여러 메커니즘을 통해 인간의 감독을 강조합니다.

#### 신뢰와 안전을 위한 애플리케이션 제어 메커니즘:

- **UI에 사용 가능한 도구 표시**: 사용자가 특정 상호작용에서 도구 사용 여부를 정의할 수 있음
- **개별 도구 실행을 위한 승인 대화상자**
- **특정 안전한 작업을 사전 승인하기 위한 권한 설정**
- **모든 도구 실행과 결과를 표시하는 활동 로그**

---

## 2. Resources (리소스)

### 개요

리소스는 AI 애플리케이션이 검색하여 모델에 컨텍스트로 제공할 수 있는 정보에 대한 구조화된 접근을 제공합니다.

### 리소스의 작동 방식

리소스는 파일, API, 데이터베이스 또는 AI가 컨텍스트를 이해하는 데 필요한 기타 소스의 데이터를 노출합니다.

**애플리케이션이 정보를 활용하는 방법:**

- 관련 부분 선택
- 임베딩을 사용한 검색
- 모든 데이터를 모델에 전달

**리소스 특징:**

- 각 리소스는 고유한 URI를 가짐 (예: `file:///path/to/document.md`)
- 적절한 콘텐츠 처리를 위해 MIME 타입 선언

#### 리소스 발견 패턴

**1. Direct Resources (직접 리소스)**

- 특정 데이터를 가리키는 고정 URI
- 예시: `calendar://events/2024` → 2024년 캘린더 가용성 반환

**2. Resource Templates (리소스 템플릿)**

- 유연한 쿼리를 위한 매개변수가 있는 동적 URI
- 예시:
    - `travel://activities/{city}/{category}` → 도시 및 카테고리별 활동 반환
    - `travel://activities/barcelona/museums` → 바르셀로나의 모든 박물관 반환

리소스 템플릿에는 제목, 설명, 예상 MIME 타입과 같은 메타데이터가 포함되어 있어 검색 가능하고 자체 문서화됩니다.

#### 프로토콜 작업

|메서드|목적|반환값|
|---|---|---|
|`resources/list`|사용 가능한 직접 리소스 나열|리소스 설명자 배열|
|`resources/templates/list`|리소스 템플릿 발견|리소스 템플릿 정의 배열|
|`resources/read`|리소스 내용 검색|메타데이터가 포함된 리소스 데이터|
|`resources/subscribe`|리소스 변경 모니터링|구독 확인|

---

### 예제: 여행 계획 컨텍스트 가져오기

여행 계획 예제를 계속하면, 리소스는 AI 애플리케이션에 관련 정보에 대한 접근을 제공합니다:

- **캘린더 데이터** (`calendar://events/2024`) - 사용자 가용성 확인
- **여행 문서** (`file:///Documents/Travel/passport.pdf`) - 중요한 문서 접근
- **이전 여정** (`trips://history/barcelona-2023`) - 과거 여행 및 선호도 참조

AI 애플리케이션은 이러한 리소스를 검색하고 처리 방법을 결정합니다:

- 임베딩 또는 키워드 검색을 사용하여 데이터의 하위 집합 선택
- 또는 원시 데이터를 모델에 직접 전달

이 경우, 캘린더 데이터, 날씨 정보, 여행 선호도를 모델에 제공하여:

- 가용성 확인
- 날씨 패턴 조회
- 과거 여행 선호도 참조

#### 리소스 템플릿 예시

```json
{
  "uriTemplate": "weather://forecast/{city}/{date}",
  "name": "weather-forecast",
  "title": "Weather Forecast",
  "description": "Get weather forecast for any city and date",
  "mimeType": "application/json"
}
```

```json
{
  "uriTemplate": "travel://flights/{origin}/{destination}",
  "name": "flight-search",
  "title": "Flight Search",
  "description": "Search available flights between cities",
  "mimeType": "application/json"
}
```

이러한 템플릿은 유연한 쿼리를 가능하게 합니다:

- **날씨 데이터**: 모든 도시/날짜 조합에 대한 예보 접근
- **항공편**: 두 공항 간의 경로 검색
- 사용자가 `origin` 공항으로 "NYC"를 입력하고 `destination` 공항으로 "Bar"를 입력하기 시작하면 시스템은 "Barcelona (BCN)" 또는 "Barbados (BGI)"를 제안할 수 있음

---

### 매개변수 완성 (Parameter Completion)

동적 리소스는 매개변수 완성을 지원합니다.

**예시:**

- `weather://forecast/{city}`에 "Par"를 입력하면 "Paris" 또는 "Park City" 제안
- `flights://search/{airport}`에 "JFK"를 입력하면 "JFK - John F. Kennedy International" 제안

시스템은 정확한 형식 지식 없이도 유효한 값을 발견할 수 있도록 도와줍니다.

---

### 사용자 상호작용 모델

리소스는 **애플리케이션 주도형**이므로 사용 가능한 컨텍스트를 검색, 처리 및 표시하는 방법에 유연성이 있습니다.

#### 일반적인 상호작용 패턴:

- **트리 또는 목록 뷰**: 익숙한 폴더 같은 구조로 리소스 탐색
- **검색 및 필터 인터페이스**: 특정 리소스 찾기
- **자동 컨텍스트 포함**: 휴리스틱 또는 AI 선택 기반 스마트 제안
- **수동 또는 대량 선택 인터페이스**: 단일 또는 여러 리소스 포함

#### 애플리케이션은 다양한 인터페이스 패턴 구현 가능:

- 미리보기 기능이 있는 리소스 선택기
- 현재 대화 컨텍스트에 기반한 스마트 제안
- 여러 리소스 포함을 위한 대량 선택
- 기존 파일 브라우저 및 데이터 탐색기와의 통합

> 프로토콜은 특정 UI 패턴을 강제하지 않으므로 필요에 맞는 리소스 발견 구현 가능

---

## 3. Prompts (프롬프트)

### 개요

프롬프트는 재사용 가능한 템플릿을 제공합니다. MCP 서버 작성자가 도메인에 대한 매개변수화된 프롬프트를 제공하거나 MCP 서버를 가장 잘 사용하는 방법을 보여줄 수 있게 합니다.

### 프롬프트의 작동 방식

프롬프트는 예상 입력과 상호작용 패턴을 정의하는 구조화된 템플릿입니다.

**주요 특징:**

- **사용자 제어형**: 자동 트리거가 아닌 명시적 호출 필요
- **컨텍스트 인식**: 사용 가능한 리소스와 도구를 참조하여 포괄적인 워크플로우 생성
- **매개변수 완성 지원**: 사용자가 유효한 인수 값을 발견할 수 있도록 도움

#### 프로토콜 작업

|메서드|목적|반환값|
|---|---|---|
|`prompts/list`|사용 가능한 프롬프트 발견|프롬프트 설명자 배열|
|`prompts/get`|프롬프트 세부 정보 검색|인수가 포함된 전체 프롬프트 정의|

---

### 예제: 간소화된 워크플로우

프롬프트는 일반적인 작업을 위한 구조화된 템플릿을 제공합니다.

#### "휴가 계획" 프롬프트

```json
{
  "name": "plan-vacation",
  "title": "Plan a vacation",
  "description": "Guide through vacation planning process",
  "arguments": [
    { 
      "name": "destination", 
      "type": "string", 
      "required": true 
    },
    { 
      "name": "duration", 
      "type": "number", 
      "description": "days" 
    },
    { 
      "name": "budget", 
      "type": "number", 
      "required": false 
    },
    { 
      "name": "interests", 
      "type": "array", 
      "items": { "type": "string" } 
    }
  ]
}
```

#### 구조화되지 않은 자연어 입력 대신 프롬프트 시스템이 가능하게 하는 것:

1. **"Plan a vacation" 템플릿 선택**
2. **구조화된 입력**: Barcelona, 7일, $3000, ["beaches", "architecture", "food"]
3. **템플릿 기반 일관된 워크플로우 실행**

---

### 사용자 상호작용 모델

프롬프트는 **사용자 제어형**이므로 명시적 호출이 필요합니다. 프로토콜은 구현자에게 애플리케이션 내에서 자연스럽게 느껴지는 인터페이스를 설계할 자유를 제공합니다.

#### 핵심 원칙:

- 사용 가능한 프롬프트의 쉬운 발견
- 각 프롬프트의 기능에 대한 명확한 설명
- 검증을 통한 자연스러운 인수 입력
- 프롬프트의 기본 템플릿에 대한 투명한 표시

#### 일반적인 UI 패턴:

- **슬래시 명령**: "/" 입력으로 사용 가능한 프롬프트 표시 (예: /plan-vacation)
- **명령 팔레트**: 검색 가능한 접근
- **전용 UI 버튼**: 자주 사용하는 프롬프트용
- **컨텍스트 메뉴**: 관련 프롬프트 제안

---

## 여러 서버를 함께 사용하기

MCP의 진정한 힘은 여러 서버가 통합 인터페이스를 통해 특화된 기능을 결합하여 함께 작동할 때 나타납니다.

### 예제: 다중 서버 여행 계획

개인화된 AI 여행 플래너 애플리케이션과 세 개의 연결된 서버를 고려해봅시다:

- **Travel Server**: 항공편, 호텔, 여정 처리
- **Weather Server**: 기후 데이터 및 예보 제공
- **Calendar/Email Server**: 일정 및 커뮤니케이션 관리

---

### 전체 흐름

#### 1단계: 사용자가 매개변수와 함께 프롬프트 호출

```json
{
  "prompt": "plan-vacation",
  "arguments": {
    "destination": "Barcelona",
    "departure_date": "2024-06-15",
    "return_date": "2024-06-22",
    "budget": 3000,
    "travelers": 2
  }
}
```

#### 2단계: 사용자가 포함할 리소스 선택

- `calendar://my-calendar/June-2024` (Calendar Server에서)
- `travel://preferences/europe` (Travel Server에서)
- `travel://past-trips/Spain-2023` (Travel Server에서)

#### 3단계: AI가 도구를 사용하여 요청 처리

**컨텍스트 수집:**

AI는 먼저 선택된 모든 리소스를 읽어 컨텍스트를 수집합니다:

- 캘린더에서 사용 가능한 날짜 식별
- 여행 선호도에서 선호하는 항공사 및 호텔 타입 학습
- 과거 여행에서 이전에 즐긴 위치 발견

**도구 실행:**

이 컨텍스트를 사용하여 AI는 일련의 도구를 실행합니다:

1. **`searchFlights()`** - NYC에서 바르셀로나까지 항공편을 항공사에 쿼리
2. **`checkWeather()`** - 여행 날짜의 기후 예보 검색

AI는 이 정보를 사용하여 예약 및 후속 단계를 생성하며, 필요한 경우 사용자의 승인을 요청합니다:

3. **`bookHotel()`** - 지정된 예산 내에서 호텔 찾기
4. **`createCalendarEvent()`** - 사용자 캘린더에 여행 추가
5. **`sendEmail()`** - 여행 세부 정보가 포함된 확인 이메일 전송

---

### 결과

여러 MCP 서버를 통해 사용자는 일정에 맞는 바르셀로나 여행을 조사하고 예약했습니다.

**"Plan a Vacation" 프롬프트가 AI를 안내하여:**

- **Resources** (캘린더 가용성 및 여행 기록)와
- **Tools** (항공편 검색, 호텔 예약, 캘린더 업데이트)를
- 다양한 서버에서 결합하여 컨텍스트를 수집하고 예약을 실행했습니다.

> **몇 시간이 걸릴 수 있는 작업이 MCP를 사용하여 몇 분 만에 완료되었습니다.**

---

## 요약

MCP 서버는 세 가지 핵심 기능을 통해 AI 애플리케이션을 강화합니다:

|기능|제어|목적|핵심 장점|
|---|---|---|---|
|**Tools**|모델|작업 수행|자동화된 작업 실행|
|**Resources**|애플리케이션|컨텍스트 제공|풍부한 정보 접근|
|**Prompts**|사용자|워크플로우 안내|일관된 상호작용 패턴|

이 세 가지 요소가 결합되면 강력하고 유연하며 사용자 제어 가능한 AI 경험을 만들 수 있습니다.

---

## 추가 리소스

- **아키텍처**: [Architecture Overview](https://claude.ai/docs/learn/architecture)
- **클라이언트 개념**: [Client Concepts](https://claude.ai/docs/learn/client-concepts)
- **서버 구축**: [Build an MCP Server](https://claude.ai/docs/develop/build-server)
- **GitHub**: https://github.com/modelcontextprotocol

---

_이 문서는 Model Context Protocol 공식 문서에서 가져온 내용입니다._