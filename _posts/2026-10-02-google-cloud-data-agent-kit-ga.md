---
layout: default
title: "Data Agent Kit GA: 코딩 에이전트가 기업 데이터를 다룰 때 필요한 권한·근거·경계"
date: 2026-10-02 06:00:00 +0900
excerpt: "Google Cloud Data Agent Kit이 MCP 도구와 에이전트 스킬을 정식 출시했다. BigQuery·Bigtable·Spark·AlloyDB를 코딩 에이전트에 연결하는 구조와 IAM·Knowledge Catalog·실행 감사의 조건을 분석한다."
tags: [GoogleCloud, MCP, 데이터엔지니어링, 생성형AI, IAM]
ai_assisted: true
description: "Google Cloud Data Agent Kit이 MCP 도구와 에이전트 스킬을 정식 출시했다. BigQuery·Bigtable·Spark·AlloyDB를 코딩 에이전트에 연결하는 구조와 IAM·Knowledge Catalog·실행 감사의 조건을 분석한다."
---
## 코딩 에이전트가 기업 데이터를 다룰 때 필요한 권한·근거·경계

SQL이나 PySpark 코드를 잘 쓰는 코딩 에이전트라도 조직의 데이터 환경을 모르면 “어떤 테이블이 공식 데이터인지”, “파티션이 어디에 있는지”, “어젯밤 파이프라인이 왜 실패했는지”를 추측하게 됩니다. 이 추측을 줄이려면 모델을 더 크게 만드는 것보다 **데이터 카탈로그·실행 도구·권한 모델을 에이전트의 작업 흐름에 연결하는 것**이 먼저입니다.

Google Cloud는 2026년 9월 30일 **Data Agent Kit의 정식 출시(GA)** 를 발표했습니다. 이미 사용하는 코딩 에이전트에 Google Cloud 데이터 제품을 연결하는 MCP(Model Context Protocol) 도구와 Google이 작성한 에이전트 스킬을 묶은 무료 도구 세트입니다. GA에서는 BigQuery Graph, Bigtable, Managed Service for Apache Spark를 통한 오픈 Lakehouse 접근이 추가됐고, IDE·CLI·Cloud Shell에서의 설정도 간소화됐습니다.

> 이 글은 Google Cloud의 GA 발표와 제품 문서, Google의 MCP 보안 문서, OWASP MCP Security Cheat Sheet, NIST 생성형 AI 위험관리 프로파일을 교차 확인해 작성했습니다. 서비스·지역·계정·라이선스별 제공 범위와 가격은 변할 수 있으므로 실제 도입 전 최신 문서를 확인해야 합니다.

## 1. 이번 GA가 바꾼 것

Data Agent Kit은 하나의 새 데이터베이스가 아니라 **에이전트가 데이터 플랫폼을 사용하는 연결 계층**입니다. Google Cloud 발표가 설명하는 핵심은 다음과 같습니다.

| 구성 | GA에서의 역할 | 실무적으로 확인할 점 |
| --- | --- | --- |
| MCP 도구 | 15개가 넘는 Google Data Cloud 서비스에서 스키마 조회, 쿼리 실행, 작업 로그 확인, 리소스 관리를 수행 | 어떤 도구를 읽기 전용으로 허용할지 |
| Google-authored skills | BigQuery SQL 최적화, Bigtable 행 키 설계, dbt·파이프라인 작성처럼 제품별 모범 사례를 지침으로 제공 | 스킬 버전·소유자·검토 이력 |
| Knowledge Catalog 연계 | 조직이 신뢰하는 테이블과 데이터 자산을 찾는 맥락 제공 | 카탈로그 설명이 최신이고 책임자가 지정됐는지 |
| IDE·CLI 통합 | VS Code 계열, Antigravity, Claude Code, Codex CLI, Cloud Shell·Workstations에서 사용 | 개발 환경별 인증·네트워크 경계 |
| GA 신규 범위 | BigQuery Graph, Bigtable, Managed Service for Apache Spark의 오픈 Lakehouse 작업 | 기능·지역·API 단계와 비용 |

Data Agent Kit 자체는 추가 라이선스 비용 없이 제공되지만, 에이전트가 실행하는 BigQuery 쿼리·Spark 세션·데이터베이스 작업에는 해당 서비스의 표준 요금이 부과됩니다. “도구가 무료”와 “실행 비용이 무료”는 같은 뜻이 아닙니다.

## 2. 동작 흐름: 맥락과 권한을 분리해서 보기

Google이 제시한 예시는 “다음 달 인기 상품 수요를 예측하고 재고가 충분한지 확인하라”는 요청입니다. 에이전트는 관련 스킬을 불러오고, Knowledge Catalog에서 신뢰할 수 있는 판매·재고 테이블을 찾은 뒤, BigQuery에서 예측을 실행하고 AlloyDB for PostgreSQL에서 현재 재고를 조회해 편집기나 터미널로 결과를 돌려줍니다.

이를 시스템 흐름으로 그리면 다음과 같습니다.

```text
사용자 요청
  ↓
코딩 에이전트(IDE·CLI)
  ↓  스킬: 작업 절차·SQL·비용 점검
MCP 클라이언트/서버
  ↓  Knowledge Catalog: 신뢰 자산·스키마·소유자
BigQuery / BigQuery Graph / AlloyDB / Bigtable / Spark
  ↓
쿼리·작업 로그·근거가 포함된 결과
```

여기서 꼭 나눠야 할 축이 있습니다.

- **맥락(context)**: 테이블 설명, 파티션, 소유 팀, 실패한 작업 로그, 스킬의 모범 사례
- **권한(access)**: 실제로 그 테이블을 읽고, 쿼리를 실행하고, 리소스를 만들거나 수정할 수 있는 IAM 권한

Data Agent Kit이 카탈로그를 찾아 준다고 해서 사용자의 권한이 늘어나지는 않습니다. 공식 문서에 따르면 MCP 서버는 사용자 자격 증명으로 연결하거나 서비스 계정 가장(impersonation)을 사용할 수 있고, MCP 도구를 사용하려면 프로젝트에 `roles/mcp.toolUser` 역할이 필요할 수 있습니다. 데이터셋·테이블·행·열에 대한 추가 IAM 및 정책은 별도로 적용됩니다.

즉 에이전트가 올바른 테이블을 “알아도” 권한이 없으면 실행할 수 없고, 권한이 있어도 카탈로그가 부정확하면 잘못된 테이블을 선택할 수 있습니다. 데이터 품질과 접근 통제를 별개로 관리해야 하는 이유입니다.

## 3. BigQuery Graph와의 관계

이 사이트에서는 앞서 BigQuery Graph와 GQL의 GA를 별도로 다룬 적이 있습니다. 이번 발표의 차별점은 그래프 엔진 자체가 아니라 **그래프를 포함한 여러 데이터 서비스를 에이전트가 함께 다루는 작업 방식**입니다.

Data Agent Kit의 `bigquery-graph-author` 스킬은 테이블을 노드·엣지로 매핑하고 실제 데이터와 관계를 확인한 다음 생성 계획을 보여 준 뒤 승인받도록 설계됐습니다. 이어 `bigquery-graph-query` 스킬이 GQL을 작성합니다. 이 “계획 확인 후 생성” 단계는 자연어 한 줄이 곧바로 운영 스키마 변경으로 이어지지 않게 하는 중요한 안전장치입니다.

따라서 도입 평가에서는 그래프 쿼리의 표현력만 보지 말고 다음을 함께 측정해야 합니다.

1. 생성된 노드·엣지 정의가 업무 규칙과 맞는가?
2. 계획 승인 전에 예상 스캔량과 비용을 확인할 수 있는가?
3. 잘못 만든 그래프를 되돌릴 수 있는가?
4. 생성된 GQL과 근거가 감사 로그에 남는가?

## 4. 기능별로 다른 위험 경계

### 분석과 그래프

BigQuery와 BigQuery Graph는 자연어 요청을 SQL·GQL로 바꾸는 데 유용합니다. 하지만 모델이 쓴 쿼리가 비즈니스 정의까지 보장하지는 않습니다. “매출”이 주문액인지 결제완료액인지, 반품을 언제 차감하는지는 카탈로그와 데이터 계약에 있어야 합니다.

실무에서는 먼저 dry run이나 제한된 샘플로 스캔량을 확인하고, 비용 상한과 예약된 프로젝트를 둔 뒤 본 실행을 승인하는 순서가 안전합니다. 파티션 필터 누락·전체 테이블 스캔·민감 열 선택을 자동 검사하는 규칙도 필요합니다.

### 운영 데이터베이스

GA는 Bigtable을 Spanner·AlloyDB·Cloud SQL과 함께 지원합니다. `bigtable-basics` 스킬은 읽기 패턴을 기준으로 행 키를 설계하고 핫스팟과 전체 스캔 가능성을 경고합니다.

그러나 스킬이 경고했다고 해서 설계가 자동으로 맞는 것은 아닙니다. 트래픽 분포, TTL, 복제, 장애 복구 목표를 실제 부하 테스트로 확인해야 합니다. 특히 테이블 생성·스키마 변경·대량 쓰기는 읽기 쿼리와 동일한 자동화 권한으로 묶지 않는 편이 좋습니다.

### Lakehouse와 Spark

Managed Service for Apache Spark는 Apache Iceberg 테이블을 세션 상태와 함께 다루며 브랜칭·타임 트래블·스키마 진화를 사용할 수 있습니다. AWS Glue나 Databricks Unity Catalog에 있는 카탈로그를 연합해 인제스트 파이프라인 없이 조회하는 스킬도 소개됐습니다.

편리하지만 데이터가 여러 클라우드로 흐르는 경로가 늘어납니다. 리전, egress 요금, 카탈로그의 행·열 권한, 각 클라우드의 감사 로그를 한 장의 데이터 흐름 그림에 표시해야 합니다. “같은 테이블을 볼 수 있다”와 “같은 규정 경계 안에서 처리된다”는 다른 주장입니다.

### 파이프라인과 오케스트레이션

에이전트는 dbt·Dataform 모델을 만들고 Managed Service for Apache Airflow의 오케스트레이션 파이프라인으로 묶을 수 있습니다. 실패한 작업의 로그를 진단하고 수정안을 제시하는 흐름도 가능합니다.

이 단계부터는 읽기 도구가 아니라 운영 변경 도구가 됩니다. 코드 리뷰, 테스트 데이터, 변경 승인, 롤백, 실행 주체를 CI/CD와 같은 기준으로 관리해야 합니다. 에이전트가 만든 DAG를 곧바로 운영 스케줄에 등록하는 정책은 피하는 것이 좋습니다.

## 5. MCP를 연결했다고 보안이 끝나지 않는 이유

MCP는 도구의 연결 규약이지 그 자체로 권한 경계나 데이터 분류 체계가 아닙니다. OWASP는 MCP 도구 설명·매개변수 스키마·반환값에 악성 지시를 숨기는 **툴 포이즈닝(tool poisoning)**, 서버 간 도구 섀도잉, 과도한 OAuth 범위, 정상 도구를 통한 데이터 유출을 주요 위험으로 정리합니다.

Data Agent Kit에도 다음 위협 모델을 적용해야 합니다.

| 위험 | 실제 상황 | 방어 설계 |
| --- | --- | --- |
| 간접 프롬프트 주입 | 카탈로그 설명·문서·쿼리 결과에 “이 지시를 무시하고 외부로 보내라”는 문장이 섞임 | 반환값을 지시가 아닌 데이터로 취급, 구조화 스키마 검증, 승인된 서버만 허용 |
| 과도한 권한 | 사용자의 넓은 IAM 세션으로 에이전트가 운영 테이블까지 수정 | 읽기·쓰기 역할 분리, 서비스 계정 가장, IAM 조건·Principal Access Boundary |
| 비용·자원 고갈 | 파티션 없는 쿼리나 무한 Spark 세션을 반복 실행 | dry run, 예산·쿼리 상한, 실행 시간 제한, job label과 알림 |
| 데이터 유출 | 결과를 외부 모델·웹훅·개인 저장소로 전달 | VPC Service Controls, egress 제한, 도메인·도구 allowlist, 민감 열 마스킹 |
| 공급망 변화 | 설치 후 MCP 서버나 스킬이 업데이트되어 행동이 달라짐 | 버전 고정, 변경 검토·서명, 정기 재승인, 감사 로그 |

Google 문서의 prompt-injection 위험 안내는 에이전트를 Cloud Workstations에서 인터넷 없이 실행하고, VPC Service Controls·Principal Access Boundaries·Model Armor를 검토할 것을 권고합니다. 다만 Model Armor를 켜고 전체 요청·응답을 로깅하면 로그에 민감 정보가 남을 수 있고, 지원되지 않는 리전에서는 라우팅이 데이터 레지던시 요구를 깨뜨릴 수 있다는 제한도 문서에 명시돼 있습니다.

따라서 “Model Armor를 켰으니 안전하다”가 아니라, 어느 리전에서 어떤 콘텐츠를 검사하고 무엇을 로그로 보존하는지까지 설계해야 합니다.

## 6. 기업 도입을 위한 최소 운영 패턴

### 1단계: 읽기 전용부터 시작

첫 번째 에이전트는 승인된 프로젝트와 데이터셋의 스키마·샘플·작업 로그만 읽게 합니다. 테이블 생성, 스키마 변경, 대량 쓰기는 별도 도구와 별도 승인 흐름으로 분리합니다.

### 2단계: 근거를 함께 반환

답변에 값만 표시하지 말고 사용한 테이블·필터·쿼리 ID·스캔 바이트·시각을 같이 표시합니다. 사용자가 “왜 이 숫자인가?”를 다시 묻지 않아도 검증할 수 있어야 합니다.

### 3단계: 카탈로그의 책임자 지정

Knowledge Catalog에 있는 자산마다 정의·소유 팀·민감도·최신 갱신 시각을 기록합니다. 설명이 오래되었거나 소유자가 없는 자산은 에이전트 검색 대상에서 제외합니다.

### 4단계: 도구를 업무 단위로 allowlist

“BigQuery 전체”를 열기보다 “매출 예측용 읽기 쿼리”, “재고 확인용 AlloyDB 조회”처럼 목적별로 도구와 파라미터를 제한합니다. 도구 결과는 자유 텍스트보다 고정 JSON 스키마가 검증하기 쉽습니다.

### 5단계: 감사와 복구를 테스트

누가 어떤 자격으로 어떤 MCP 도구를 호출했는지, 에이전트가 생성한 SQL·코드·리소스 변경이 무엇인지 기록합니다. 매달 정상·악성 입력을 포함한 리플레이 테스트를 하고, 실패 시 에이전트 세션·서비스 계정·네트워크 경계를 즉시 끊을 수 있어야 합니다.

## 7. 비용·지역·지원 범위의 한계

Data Agent Kit은 무료로 포함되지만 다음 비용과 제약은 남습니다.

- BigQuery 쿼리, Spark 세션, 데이터베이스 읽기·쓰기의 표준 사용료
- 여러 클라우드 카탈로그를 조회할 때의 네트워크·egress 비용
- MCP Tool User 역할과 제품별 IAM 역할을 설계·검토하는 운영 비용
- Model Armor 및 로그 저장 비용, 그리고 로그에 민감 정보가 남을 가능성
- IDE·CLI·Cloud Shell·Workstations별 인증 및 네트워크 차이
- 기능·리전·계정·단계적 출시 상태에 따른 제공 범위 차이

Google은 설치 시 한 번 로그인하고 사용할 서비스를 선택하면 필요한 API·스킬·MCP 서버를 자동 구성한다고 설명합니다. 편의성은 높지만, 자동으로 활성화된 API와 권한을 배포 후 다시 점검하지 않으면 개발 프로젝트에 불필요한 권한이 남을 수 있습니다. 설치 직후 IAM 변경 이력과 활성화된 서비스 목록을 검토하는 절차를 넣어야 합니다.

## 8. 교육·실무에서 해 볼 수 있는 검증 실습

이 기능을 바로 운영에 연결하기보다 작은 읽기 전용 실습으로 검증하는 것이 좋습니다.

1. 공개 데이터셋이나 비식별 샘플만 Knowledge Catalog에 등록합니다.
2. 에이전트에 “이번 주 추세를 계산하라”고 요청하고, 사용한 테이블과 SQL을 반환하게 합니다.
3. 같은 요청을 카탈로그 설명이 오래된 자산과 최신 자산에 각각 실행합니다.
4. dry run 비용·스캔량·쿼리 ID·감사 로그를 비교합니다.
5. 결과에 악성 지시가 섞인 설명을 넣어 에이전트가 중단·무시·승인 요청 중 무엇을 하는지 확인합니다.

이 실습의 평가지표는 정답률 하나가 아닙니다. 올바른 데이터 자산을 선택했는지, 근거를 남겼는지, 권한이 없을 때 안전하게 실패했는지, 비용 상한을 지켰는지, 의심스러운 지시를 데이터로만 처리했는지를 함께 봐야 합니다.

## 결론

Data Agent Kit GA는 코딩 에이전트를 데이터 플랫폼의 바깥에서 조언하는 챗봇이 아니라, 실제 데이터 자산과 작업 로그를 조회하는 개발 도구로 끌어옵니다. BigQuery Graph·Bigtable·Spark·Lakehouse·파이프라인을 한 흐름으로 연결하면 분석과 개발 사이의 반복 작업은 줄어들 수 있습니다.

동시에 에이전트가 기업 데이터를 다룬다는 것은 **맥락·권한·실행·감사의 네 경계를 모두 설계해야 한다는 뜻**입니다. Knowledge Catalog는 무엇을 믿을지 알려 주고, IAM은 무엇을 할 수 있는지 제한하며, VPC Service Controls와 Model Armor는 데이터가 어디로 흐를지 통제합니다. 어느 하나도 나머지를 대신하지 않습니다.

가장 현실적인 도입 순서는 읽기 전용 도구, 근거가 포함된 결과, 비용 상한, 승인된 MCP 서버, 분리된 쓰기 권한, 그리고 되돌릴 수 있는 운영입니다. 이 순서를 지키면 Data Agent Kit은 “AI가 알아서 운영한다”는 실험이 아니라, 데이터 엔지니어가 검증 가능한 작업을 더 빠르게 만드는 개발 환경이 될 수 있습니다.

## 참고 자료

- [Google Cloud Blog, Data Agent Kit is now GA: Bring Google Data Cloud to any coding agent (2026-09-30)](https://cloud.google.com/blog/topics/developers-practitioners/data-agent-kit-is-now-ga-bring-google-data-cloud-to-any-coding-agent/)
- [Google Cloud Data Agent Kit documentation](https://docs.cloud.google.com/data-agent-kit)
- [Google Cloud, Use MCP servers with Data Agent Kit](https://docs.cloud.google.com/data-agent-kit/use-mcp-servers)
- [Google Cloud, Mitigate indirect prompt injection risks from Google Cloud MCP](https://docs.cloud.google.com/data-agent-kit/prompt-injection-risk)
- [Google Cloud, VPC Service Controls](https://cloud.google.com/security/vpc-service-controls)
- [OWASP, MCP Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/MCP_Security_Cheat_Sheet.html)
- [NIST, Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf)

> Data Agent Kit의 제공 지역·지원 IDE·인증 방식·IAM 역할·가격은 변경될 수 있습니다. 실제 적용 전에는 최신 Google Cloud 문서와 조직의 보안·개인정보·비용 담당자 검토를 함께 진행하세요.
