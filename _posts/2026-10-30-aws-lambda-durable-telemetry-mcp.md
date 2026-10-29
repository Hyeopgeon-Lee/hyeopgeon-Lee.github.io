---
layout: default
title: "AWS Lambda Durable Functions 텔레메트리와 MCP: 실행 단위 관찰성을 설계하는 법"
date: 2026-10-30 06:00:00 +0900
excerpt: "AWS가 2026년 10월 28일 Lambda Durable Functions용 Durable Execution Telemetry Exporter와 MCP 서버를 공개했다. 여러 Lambda 호출과 대기·재시도를 하나의 실행 기록으로 묶는 구조, 13개 전송 대상, 자연어 조회의 장점과 보안·비용·관찰성의 한계를 실무 관점에서 정리한다."
tags: [AWSLambda, 서버리스, 관찰성, MCP, AI운영]
ai_assisted: true
description: "AWS가 2026년 10월 28일 Lambda Durable Functions용 Durable Execution Telemetry Exporter와 MCP 서버를 공개했다. 여러 Lambda 호출과 대기·재시도를 하나의 실행 기록으로 묶는 구조, 13개 전송 대상, 자연어 조회의 장점과 보안·비용·관찰성의 한계를 실무 관점에서 정리한다."
---

서버리스 애플리케이션의 장애를 조사할 때 로그가 없어서 문제가 되는 경우보다, 로그가 너무 잘게 흩어져 있어 실행 전체를 복원하기 어려운 경우가 더 많습니다. 특히 오래 실행되는 워크플로는 한 번의 업무가 여러 Lambda 호출로 나뉘고, 그 사이에 대기·재시도·콜백이 들어갑니다. CloudWatch에는 호출별 로그가 남지만 “어느 단계에서 몇 번 재시도했고, 전체 주문이 얼마나 오래 걸렸는가?”라는 질문에는 여러 로그 스트림을 다시 연결해야 합니다.

AWS는 2026년 10월 28일 **Durable Execution Telemetry Exporter**와 **Durable Execution Telemetry MCP 서버**를 공개했습니다. Lambda Durable Functions가 재개될 때마다 누적 실행 상태를 하나의 텔레메트리 레코드로 만들고, CloudWatch Logs·S3·DynamoDB·Aurora·OpenSearch 등 13개 목적지로 보낼 수 있게 한 플러그인입니다. MCP 서버를 연결하면 Kiro, Claude Code, Cursor 같은 MCP 클라이언트가 저장된 실행 기록을 읽기 전용으로 조회할 수 있습니다.

이 글은 [AWS What's New 발표](https://aws.amazon.com/about-aws/whats-new/2026/10/lambda-durable-telemetry/), [AWS Compute Blog의 구현 설명](https://aws.amazon.com/blogs/compute/observing-aws-lambda-durable-functions-with-the-durable-execution-telemetry-exporter/), [Durable Execution SDK MCP 문서](https://docs.aws.amazon.com/durable-execution/sdk-reference/observability/telemetry/mcp/), 그리고 독립 AWS 변경사항 다이제스트의 공개일·제공 범위 정리를 교차 확인해 작성했습니다. AWS가 제시한 기능은 “AI가 운영을 자동으로 해결한다”는 뜻이 아니라, 실행 데이터를 일관된 형태로 만들고 조회 경로를 표준화하는 기능입니다.

## 1. 왜 기존 Lambda 관찰성만으로는 부족한가

일반적인 Lambda 함수는 한 번 호출되면 짧은 시간 안에 끝납니다. 호출 로그, 함수 오류율, 실행 시간, X-Ray 트레이스만으로도 원인을 어느 정도 찾을 수 있습니다. 그러나 Durable Functions는 실행을 여러 번 나눠서 진행합니다.

예를 들어 주문 처리 워크플로가 다음처럼 구성될 수 있습니다.

1. 주문 유효성 검사
2. 재고 예약
3. 30분 대기
4. 결제 승인
5. 배송 시스템 호출
6. 완료 또는 보상 작업

각 단계가 별도의 Lambda 호출로 실행되고, 대기와 재시도 뒤에 같은 핸들러가 재개됩니다. CloudWatch 로그에는 호출별 스트림이 생기고, 여러 주문의 실행이 섞입니다. 일반 메트릭은 함수 수준의 오류율은 보여주지만, 특정 주문이 어느 단계에서 멈췄는지는 말해주지 않습니다. 분산 추적은 한 실행의 시간 흐름을 보여주는 데 유용하지만, “이번 주에 가장 자주 실패한 단계”처럼 많은 실행을 가로질러 집계하는 질문에는 별도 데이터 모델이 필요합니다.

AWS Compute Blog가 지적하듯 핵심 질문은 “이번 호출이 무엇을 했는가?”가 아니라 다음과 같습니다.

- 실행 전체는 어느 단계까지 진행됐는가?
- 어느 단계가 가장 많이 재시도됐는가?
- 배포 이후 특정 단계의 지연이 늘었는가?
- 결제가 실패한 주문 중 수동 승인이 필요한 고객은 누구인가?

이 질문은 호출 단위 로그가 아니라 **실행 단위 레코드**가 있어야 간단해집니다.

## 2. Telemetry Exporter의 구조

Exporter는 Durable Execution SDK의 플러그인으로 함수 프로세스 안에서 동작합니다. 별도의 수집 에이전트를 운영하거나 비즈니스 코드에 수동 로깅을 대량으로 삽입하는 방식이 아닙니다.

Durable Function이 호출될 때 플러그인은 체크포인트 상태와 SDK의 실행 생명주기를 이용해 지금까지의 전체 실행을 재구성합니다. 그 결과는 `DurableExecutionTelemetryRecord`라는 JSON 문서입니다. 기본적으로 다음 정보를 담습니다.

- 실행 ARN과 실행 이름
- 함수 이름과 시작·종료 시각
- 전체 상태(`SUCCEEDED`, `FAILED` 등)
- 총 실행 시간
- 실행 입력과 출력
- 단계·대기·콜백·병렬 작업의 이름과 유형
- 각 연산의 상태, 소요 시간, 재시도 횟수와 오류

중요한 점은 매 호출의 델타가 아니라 **현재까지 누적된 스냅샷**이라는 것입니다. 워크플로가 네 번 일시 중단되고 재개돼도 최신 레코드 하나만 읽으면 전체 진행 경로를 볼 수 있습니다. 그래서 여러 로그 스트림을 실행 ARN으로 조합하는 맞춤형 파이프라인의 양이 줄어듭니다.

Exporter는 요청 처리 경로와 분리된 플러그인으로 동작하지만, 함수가 호출되는 시점에 레코드를 생성합니다. 기본 `on-complete` 모드는 실행이 성공하거나 실패했을 때 한 번 내보냅니다. 진행 중인 상태를 보고 싶으면 `on-change`, 실패만 수집하려면 `on-failure`를 선택할 수 있습니다.

## 3. 13개 전송 대상이 의미하는 것

이번 발표는 단순히 CloudWatch에 JSON을 추가하는 기능이 아닙니다. 목적에 따라 서로 다른 저장소를 고를 수 있습니다.

| 대상 | 적합한 용도 | 주의할 점 |
| --- | --- | --- |
| 함수 자체 CloudWatch Logs | 가장 빠른 시작, 별도 권한 최소화 | 보존 기간과 쿼리 비용 관리 |
| 중앙 CloudWatch Logs | 여러 함수의 실행 기록 통합 | 로그 그룹 접근 정책과 비용 |
| S3 | 장기 보관, Athena SQL 분석 | 파티션·스키마 관리 |
| DynamoDB | 실행 ARN별 빠른 조회, 대시보드 | 아이템 크기·쓰기 비용 |
| Aurora | 업무 데이터와 워크플로 조인 | DB 용량과 읽기 권한 |
| Redshift | 대규모 분석과 BI | 적재·쿼리 운영 |
| OpenSearch | 검색·대시보드 | 인덱스 보존과 노드 비용 |
| EventBridge | 실패 알림과 자동 대응 | 중복 이벤트·재처리 |
| Firehose | S3·Splunk 등으로 팬아웃 | 버퍼링과 변환 지연 |
| SQS | 비동기 후속 처리 | 큐 자체는 질의 저장소가 아님 |
| OTLP | 외부 관찰성 플랫폼 연동 | 스키마와 인증 매핑 |
| HTTPS | 사내 수집기·웹훅 | 엔드포인트 신뢰와 재시도 |
| 파일시스템·EFS | 로컬 개발·지속 저장 | 운영 환경의 공유 스토리지 고려 |

여러 목적지를 동시에 설정하면 Exporter가 각 전송기로 레코드를 병렬 전송합니다. 예를 들어 DynamoDB에는 최근 실행 조회용으로 저장하고, S3에는 장기 분석용으로 보낼 수 있습니다. 이때 “저장소를 하나 더 붙이면 관찰성이 무료로 늘어난다”는 생각은 위험합니다. S3·DynamoDB·CloudWatch 각각의 저장·읽기·보존 비용이 합산되고, 동일한 실행 스냅샷을 여러 곳에 복제하게 됩니다.

## 4. 샘플링과 민감정보 제어가 핵심이다

실행 입력과 출력에는 주문번호뿐 아니라 고객명, 이메일, 결제 식별자, 내부 프롬프트가 들어갈 수 있습니다. AWS 문서와 블로그는 기본 설정이 개발 환경에는 편리하지만 운영 환경에는 그대로 부적절할 수 있다고 설명합니다.

운영에서는 최소한 다음 세 가지를 결정해야 합니다.

### emitMode

- `on-complete`: 성공·실패 시 한 번 기록
- `on-failure`: 실패 실행만 기록
- `on-change`: 재개·단계 변화마다 기록

장애 분석이 목적이면 `on-failure`가 저장량을 줄일 수 있습니다. 반대로 장시간 실행의 진행률을 대시보드에 표시하려면 `on-change`가 필요하지만 레코드 수가 크게 늘어납니다.

### samplingRate

실행 ARN의 해시를 기준으로 샘플링하므로 같은 실행이 중간에 일부만 선택되는 문제가 줄어듭니다. 0.1로 설정하면 대략 10%의 실행을 선택하고, 선택된 실행은 설정된 emitMode에 따라 일관되게 기록합니다. 단, 규제·금융 감사처럼 모든 실행을 보존해야 하는 범위에는 샘플링을 적용하면 안 됩니다.

### content transform

입력·출력 전체를 그대로 내보내지 말고, 필요한 필드만 남기는 변환 함수를 사용해야 합니다. 예를 들어 주문 ID와 상태만 기록하고 이메일·결제 토큰·자유 형식 고객 메시지는 제거할 수 있습니다. 저장소에 이미 평문이 들어간 뒤 삭제하는 것보다 함수 안에서 내보내기 전 최소화하는 편이 안전합니다.

각 목적지는 payload 크기 제한도 다릅니다. AWS는 CloudWatch Logs 이벤트가 256KB, DynamoDB 아이템이 400KB 범위라는 예를 들며, 레코드가 커지면 일부 내용을 잘라내고 `truncated: true`로 표시한다고 설명합니다. 이 동작에 기대기보다, 업무적으로 필요한 필드만 설계해 크기를 예측 가능하게 만드는 것이 좋습니다.

## 5. MCP 서버는 관찰성 조회를 어떻게 바꾸는가

Durable Execution Telemetry MCP 서버는 로컬에서 stdio로 실행되는 읽기 전용 MCP 서버입니다. 환경 변수로 목적지와 리전을 지정하고, 표준 AWS SDK 자격 증명 체인을 사용합니다. 설정 파일에 장기 비밀을 저장하는 방식이 아닙니다.

서버가 제공하는 핵심 도구는 다음과 같습니다.

- `test_destination`: 목적지 연결과 필요한 설정을 확인
- `describe_schema`: 레코드 구조와 목적지별 질의 방언을 반환
- `list_executions`: 상태·함수·기간으로 최근 실행을 필터링
- `get_execution`: 실행 ARN 하나의 전체 기록을 조회
- `query`: 필터로 표현하기 어려운 읽기 전용 질의 실행

이 계층의 가치는 AI가 “마음대로 AWS를 조작한다”는 데 있지 않습니다. DynamoDB PartiQL, Athena SQL, Aurora PostgreSQL, OpenSearch, CloudWatch Logs Insights는 질의 문법과 필드 경로가 서로 다릅니다. MCP 서버가 저장소별 스키마와 질의 방식을 알고 있으므로, 운영자는 “어제 실패한 결제 단계에서 재시도가 세 번 이상 발생한 주문을 찾아줘”라고 물어볼 수 있습니다.

AWS 문서는 SQL 목적지에서 `SELECT` 또는 `WITH`로 시작하는 읽기 질의만 허용하고, 쓰기 키워드·두 번째 문장·지원하지 않는 구문을 사전에 거부한다고 설명합니다. 그래도 이것이 완전한 보안 경계는 아닙니다. 데이터베이스 자격 증명이 쓰기 권한을 갖고 있으면 모델이 아닌 SQL 함수나 저장 프로시저를 통해 부작용이 생길 수 있으므로, MCP 서버에는 목적지별 최소 읽기 권한만 부여해야 합니다.

## 6. “자연어 조회”가 운영팀에 주는 실제 이점

MCP를 붙였다고 장애 대응이 자동으로 끝나는 것은 아닙니다. 그러나 다음과 같은 반복 작업은 줄어듭니다.

1. 장애가 발생한 실행 ARN을 검색합니다.
2. 실패한 단계와 재시도 횟수를 확인합니다.
3. 같은 단계의 최근 실패율을 집계합니다.
4. 배포 시각과 오류 증가 시점을 비교합니다.
5. 영향을 받은 고객·주문 목록을 추출합니다.

이 과정에서 운영자는 쿼리 언어를 매번 바꾸지 않고 결과의 의미에 집중할 수 있습니다. 교육 관점에서도 유용합니다. 학생들이 CloudWatch 로그 스트림을 수동으로 합치는 대신, 실행 레코드의 스키마와 필터를 먼저 이해하고 그 질의를 SQL이나 자연어로 비교할 수 있습니다.

다만 AI가 반환한 설명은 원본 레코드의 대체물이 아닙니다. “결제 단계가 원인”이라는 요약이 맞더라도, 실제 실패 코드·재시도 정책·외부 결제사의 응답을 확인해야 합니다. MCP 결과에는 실행 입력과 출력이 포함될 수 있으므로, 모델 컨텍스트에 들어간 데이터가 어디로 전송되고 얼마나 보존되는지도 조직의 AI 사용 정책으로 관리해야 합니다.

## 7. AWS Telemetry API와의 차이

AWS Lambda에는 이미 확장 프로그램이 로그·플랫폼 메트릭·트레이스를 실시간으로 받는 Telemetry API가 있습니다. 그러나 Telemetry API는 실행 환경과 호출 단위의 신호를 전달하는 인터페이스입니다. Durable Execution Telemetry Exporter는 Durable Functions의 상태 모델을 이해해 여러 호출을 하나의 누적 실행 레코드로 만듭니다.

둘은 경쟁 관계가 아니라 계층이 다릅니다.

- Telemetry API: 런타임 로그·메트릭·트레이스를 수집하는 저수준 경로
- Durable Exporter: 단계·대기·콜백·재시도를 포함한 워크플로 의미 계층
- MCP 서버: 저장된 실행 의미를 운영자가 질의하는 읽기 계층

이미 OpenTelemetry나 외부 APM을 사용하는 팀은 OTLP exporter를 통해 기존 파이프라인으로 보낼 수 있습니다. 그 경우에도 기존 트레이스와 DurableExecutionTelemetryRecord의 실행 ARN을 연결해 중복 집계와 누락을 피해야 합니다.

## 8. 관찰되지 않는 종료 상태를 기억하라

Exporter가 모든 실행 종료를 자동으로 보장하는 것은 아닙니다. 함수 프로세스 안에서 실행되므로, Lambda 서비스가 호출 없이 상태를 종료한 경우에는 플러그인이 레코드를 내보낼 기회가 없습니다.

AWS Compute Blog는 예로 다음 상태를 설명합니다.

- 관리자가 수동으로 중지한 `STOPPED`
- 실행 제한시간 초과로 서비스가 종료한 `TIMED_OUT`

완전한 수명주기 기록이 필요하면 기본 EventBridge 버스의 Lambda Durable Execution 상태 변경 이벤트를 별도 핸들러에서 받아 저장소를 보완해야 합니다. 이 차이를 모르면 “모든 실패가 Telemetry 레코드에 있다”고 믿게 되고, 실제 운영 대시보드에서 종료 상태가 빠집니다.

또 하나의 한계는 스냅샷이 누적 기록이라는 점입니다. `on-change`를 켜도 전송이 실패하거나 함수가 종료되면 중간 업데이트 일부가 없을 수 있고, 최신 스냅샷이 이전 레코드를 대체합니다. 감사 목적의 불변 이벤트 로그가 필요하다면 S3 Object Lock이나 별도의 이벤트 저장 설계를 함께 검토해야 합니다.

## 9. 비용과 성능을 함께 설계하는 체크리스트

### 데이터 경로

- 실행 레코드를 어느 리전에 저장할지 정했는가?
- 고객·결제·프롬프트 데이터의 국외 전송과 보존 정책을 확인했는가?
- S3·DynamoDB·CloudWatch 각각의 수명주기와 삭제 정책을 설정했는가?
- OTLP나 HTTPS 목적지의 재시도·중복 제거를 구현했는가?

### 권한

- 함수 실행 역할에 목적지별 최소 쓰기 권한만 부여했는가?
- MCP 서버에는 목적지별 읽기 전용 자격 증명만 사용했는가?
- AI 에이전트가 조회할 수 있는 테넌트·리전·기간을 제한했는가?
- 실행 입력·출력의 민감 필드를 content transform으로 제거했는가?

### 품질

- `executionArn`과 로그·트레이스·업무 ID를 상호 연결하는가?
- 샘플링으로 빠진 실행을 지표에서 명확히 구분하는가?
- `truncated` 레코드를 완전한 기록으로 오인하지 않는가?
- `STOPPED`·`TIMED_OUT` EventBridge 이벤트를 보완하는가?
- 레코드 schemaVersion 변경을 감지하고 파서 버전을 관리하는가?

### 운영

- on-complete와 on-change의 저장량을 부하 테스트했는가?
- 가장 빈번한 실패 단계, 재시도율, 실행 전체 지연을 대시보드로 만들었는가?
- MCP의 자연어 답변에 원본 실행 ARN과 질의 시간을 함께 표시하는가?
- 에이전트가 생성한 원인 분석을 사람 검토 없이 자동 조치로 연결하지 않는가?

## 10. 도입 실험

실제 고객 정보 없이 합성 주문 워크플로를 만들어 다음 순서로 검증할 수 있습니다.

1. Durable Execution SDK로 유효성 검사·대기·재시도·결제 모의 단계를 구성합니다.
2. 기본 CloudWatch Logs만 켠 상태에서 실행이 여러 로그 스트림으로 나뉘는 모습을 확인합니다.
3. Exporter를 `on-complete`로 등록하고 DynamoDB 또는 S3에 레코드를 보냅니다.
4. 동일한 실행 ARN에 단계, 대기, 오류, 재시도가 누적되는지 확인합니다.
5. `content` 변환으로 입력·출력의 이메일과 결제 토큰을 제거합니다.
6. 샘플링률을 0.1로 낮추고 선택된 실행이 일관되게 기록되는지 측정합니다.
7. MCP 서버를 읽기 전용 역할로 연결해 최근 실패 실행과 최다 재시도 단계를 조회합니다.
8. 쓰기 키워드가 포함된 SQL이 차단되는지, `SELECT` 질의가 예상 행 수로 제한되는지 확인합니다.
9. 실행을 수동 중지하거나 제한시간을 초과시켜 EventBridge 보완 이벤트가 필요한지 확인합니다.
10. 레코드 크기와 저장소 비용을 계산해 on-change와 on-failure 중 운영 정책을 선택합니다.

이 실험의 성공 기준은 “AI가 장애 원인을 말해줬다”가 아닙니다. 원본 실행 레코드, 사용된 질의, 권한, 민감정보 필터, 누락 가능한 종료 상태를 재현할 수 있어야 합니다.

## 한계와 결론

Durable Execution Telemetry Exporter는 Lambda Durable Functions의 실행 모델에 맞는 관찰성 단위를 제공합니다. 여러 호출·대기·재시도를 하나의 누적 레코드로 만들고, 13개 목적지와 OTLP를 통해 기존 분석·관찰성 시스템에 연결할 수 있습니다. MCP 서버는 저장소별 질의 문법을 감춘 읽기 전용 인터페이스를 제공해, 운영자가 실행 기록을 자연어로 탐색하도록 돕습니다.

그러나 다음을 기억해야 합니다.

- Exporter는 함수 안에서 실행되므로 서비스 수준의 `STOPPED`·`TIMED_OUT` 종료를 모두 볼 수 없습니다.
- 자연어 답변은 레코드와 질의를 대체하지 않으며, MCP 자격 증명은 반드시 읽기 전용이어야 합니다.
- 입력·출력을 그대로 내보내면 로그·데이터베이스·모델 컨텍스트에 민감정보가 복제됩니다.
- on-change와 다중 목적지는 저장·전송 비용과 중복 레코드를 늘립니다.
- 누적 스냅샷은 최신 상태를 보여주지만 불변 감사 이벤트 로그와는 다릅니다.
- 실행 레코드가 있어도 외부 결제사·데이터베이스·도구 호출의 의미는 별도 상관관계 키가 있어야 복원됩니다.

권장 도입 순서는 다음과 같습니다.

1. 한 개의 합성 워크플로에서 실행 ARN·업무 ID·트레이스를 연결합니다.
2. 실패 중심의 on-failure와 최소 필드 변환으로 데이터 경계를 확인합니다.
3. S3나 DynamoDB 한 곳에 저장하고 보존·비용을 측정합니다.
4. EventBridge로 서비스 수준 종료 상태를 보완합니다.
5. 읽기 전용 MCP 서버를 연결하되, 자연어 결과에 원본 레코드와 질의를 함께 남깁니다.
6. 효과가 검증된 뒤에 on-change, 다중 목적지, 자동 대응으로 범위를 넓힙니다.

이번 발표의 핵심은 “AI가 로그를 대신 본다”가 아닙니다. 장기 실행 서버리스 워크플로를 실행 단위로 기록하고, 저장소와 질의 경계를 표준화해 사람이든 AI든 같은 증거를 조회할 수 있게 했다는 점입니다. 그 증거를 최소 권한·민감정보 최소화·EventBridge 보완과 함께 운영할 때, MCP 기반 자연어 분석이 편의 기능을 넘어 신뢰할 수 있는 서버리스 운영 도구가 될 수 있습니다.

## 참고 자료

- [AWS What's New: AWS Lambda durable functions now exports live telemetry for execution insights](https://aws.amazon.com/about-aws/whats-new/2026/10/lambda-durable-telemetry/) (2026-10-28)
- [AWS Compute Blog: Observing AWS Lambda durable functions with the Durable Execution Telemetry Exporter](https://aws.amazon.com/blogs/compute/observing-aws-lambda-durable-functions-with-the-durable-execution-telemetry-exporter/) (2026-10-28)
- [AWS Durable Execution SDK Developer Guide: Durable Execution Telemetry MCP server](https://docs.aws.amazon.com/durable-execution/sdk-reference/observability/telemetry/mcp/)
- [AWS Lambda Developer Guide: Telemetry API](https://docs.aws.amazon.com/lambda/latest/dg/telemetry-api.html)
- [AWS Lambda Durable Execution SDK repositories](https://github.com/aws/aws-durable-execution-sdk-js)
- [AWS What's New Digest (independent cross-check)](https://hyuraku.github.io/aws-what-new-digest/2026/10/29.html) (2026-10-29)
