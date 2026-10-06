---
layout: default
title: "GitHub AI Scan 공개 프리뷰: 탐지율보다 먼저 관리해야 할 활성화 가시성"
date: 2026-10-07 06:00:00 +0900
excerpt: "GitHub가 Security overview에서 AI Scan for pull requests의 저장소별 실제 활성화 상태를 보여 주기 시작했다. CodeQL을 보완하는 AI 탐지의 범위·비용·오탐·데이터 흐름과 조직 거버넌스 방법을 분석한다."
tags: [GitHub, AppSec, CodeQL, 생성형AI, DevSecOps]
ai_assisted: true
---

## 탐지율보다 먼저 관리해야 할 활성화 가시성

AI 코딩 도구가 널리 쓰일수록 보안팀이 먼저 답해야 하는 질문은 “AI가 취약점을 몇 개 찾았는가?”가 아닙니다.

> 어느 저장소에서 어떤 AI 보안 검사가 실제로 실행되고 있으며, 그 결과를 누가 검토하고, 비용과 데이터 흐름을 어떻게 통제하고 있는가?

GitHub는 2026년 10월 6일 **Security overview의 coverage 화면에서 Code scanning AI Scan for pull requests 활성화 상태를 조직·엔터프라이즈 단위로 확인하는 기능**을 공개했습니다. 요약에는 `enabled`와 `not enabled` 저장소 수가 표시되고, 각 저장소 행에는 최종적으로 적용된(effective) 활성화 상태가 표시됩니다. `code-scanning-ai-scan-pr-scan:enabled`와 `code-scanning-ai-scan-pr-scan:not-enabled` 필터, CSV 내보내기의 전용 열도 함께 제공됩니다.

작아 보이는 UI 개선이지만, AI 보안을 “설정한 팀의 주장”에서 “조직 전체의 측정 가능한 적용 범위”로 바꾸는 변화입니다.

> 이 글은 GitHub Changelog와 AI Scan 공식 문서, GitHub의 AI 보안 기능 책임 있는 사용 문서, 2026 GenAI Code Security Report, 그리고 최근 연구의 실험 결과를 교차 확인해 작성했습니다. AI Scan은 현재 공개 프리뷰이므로 기능·지원 언어·가격·정확도가 바뀔 수 있습니다.

## 1. AI Scan은 CodeQL의 대체품이 아니다

GitHub 공식 문서에 따르면 AI Scan은 CodeQL이 지원하지 않는 언어와 프레임워크의 Pull Request에서 보안 취약점을 찾는 AI 기반 보조 엔진입니다. CodeQL이 지원하는 언어에 대해 정밀한 정적 분석을 제공한다면, AI Scan은 PHP, Shell/Bash, Terraform HCL, Dockerfile, JSP·Blazor 같은 공백을 메우는 방향입니다.

두 기능의 차이를 운영 관점에서 정리하면 다음과 같습니다.

| 항목 | CodeQL | AI Scan for pull requests |
| --- | --- | --- |
| 분석 단위 | 지원 언어의 코드 분석과 데이터 흐름 | Pull Request의 변경 코드와 저장소 맥락 |
| 결과 위치 | 코드 스캔 경고·보안 개요·백로그 | Pull Request의 Conversation·Files changed |
| 실행 조건 | 코드 스캔 설정과 쿼리·빌드 조건 | 코드 스캔 활성화, AI Scan effective 설정, 지원 대상 변경 |
| 강점 | 재현 가능한 규칙·높은 정밀도 | CodeQL 공백 언어·프레임워크의 추가 신호 |
| 현재 한계 | 쿼리 범위와 빌드 구성이 필요 | 공개 프리뷰, 오탐 가능, PR만 지원, 병합 차단 불가 |

AI Scan은 CodeQL 기본 설정이 켜져 있지 않아도 실행할 수 있지만, 코드 스캔이 꺼져 있거나 저장소의 effective AI Scan 설정이 비활성화되어 있으면 실행되지 않습니다. 또한 Fork와 Dependabot Pull Request에는 실행되지 않고, 전체 기본 브랜치 백로그 스캔도 지원하지 않습니다.

따라서 “AI Scan을 도입했다”는 말은 충분하지 않습니다. **어떤 위험 신호를 어떤 분석기로 어느 시점에 받고, 어떤 신호만 병합 정책으로 강제할지**를 나눠야 합니다.

## 2. 10월 6일 기능이 해결하는 가시성 문제

AI Scan이 조직 설정에 존재한다고 해서 모든 저장소에서 같은 방식으로 동작하지는 않습니다. 저장소·조직·엔터프라이즈 설정, 라이선스, 지원 언어, Pull Request 변경 내용에 따라 실제 실행 여부가 달라질 수 있습니다.

이번 coverage 기능은 세 가지를 한 화면에 모읍니다.

1. **조직 수준의 적용률**: 활성화된 저장소와 그렇지 않은 저장소의 수
2. **저장소별 effective 상태**: 상위 정책과 저장소 설정을 반영한 실제 상태
3. **내보낼 수 있는 증거**: 필터와 CSV로 남기는 적용 현황

이 구분은 보안 감사에서 중요합니다. 관리자가 “조직 정책을 켰다”고 말하는 것과, 특정 저장소의 Pull Request에서 AI Scan이 실제로 실행되는 것은 다른 사실이기 때문입니다.

예를 들어 다음과 같은 질문에 CSV가 답을 줄 수 있어야 합니다.

- 고객 개인정보를 다루는 저장소 중 AI Scan이 비활성화된 곳은 어디인가?
- Terraform과 Dockerfile이 많은 저장소가 지원 언어 공백에 놓여 있지 않은가?
- 공개 프리뷰 비용을 감당할 팀만 활성화했는가?
- 비활성화 예외에 소유자와 만료일이 지정돼 있는가?
- 지난달과 비교해 적용 범위가 늘었지만 결과 검토 인력도 늘었는가?

가시성은 탐지 기능보다 덜 화려하지만, 보안 프로그램을 운영 가능한 상태로 만드는 전제입니다.

## 3. “enabled”가 곧 “취약점이 차단된다”는 뜻은 아니다

공식 문서에서 AI Scan 결과는 **advisory**이며 Pull Request 병합을 막지 않습니다. AI Scan findings는 CodeQL 경고와 나란히 표시될 수 있지만, 현재는 ruleset의 병합 요구 조건에 직접 사용할 수 없습니다.

이 정책은 프리뷰 단계에서 신중한 선택입니다. 자연어 설명과 코드 맥락을 이해하는 AI 탐지는 새로운 유형을 찾을 수 있지만, 오탐과 재현성 문제도 남아 있습니다. 병합 차단을 바로 걸면 정상 코드를 막거나 개발자가 경고를 무시하는 “알림 피로”가 생길 수 있습니다.

따라서 권장 순서는 다음과 같습니다.

- AI Scan: 새로운 신호를 수집하고 개발자에게 설명
- CodeQL·SAST·의존성 검사: 반복 가능한 규칙과 알려진 취약점 탐지
- 테스트·리뷰·보안 승인: 실제 위험과 업무 맥락을 판단
- Ruleset·배포 게이트: 신뢰도가 검증된 조건만 강제

`enabled`는 “분석을 받을 가능성이 열려 있다”는 상태이지, “취약점이 모두 발견된다”거나 “안전한 코드만 병합된다”는 보증이 아닙니다.

## 4. AI Scan이 실제로 보는 데이터

GitHub의 책임 있는 사용 문서는 AI 기반 보안 기능이 분석에 필요한 코드와 경고 맥락을 모델 입력으로 조합한다고 설명합니다. 예를 들어 CodeQL 경고의 SARIF 정보, 소스·싱크 주변의 코드 조각, 관련 파일의 앞부분, CodeQL 쿼리 도움말 등이 프롬프트에 포함될 수 있습니다.

AI Scan 공식 문서도 Pull Request 코드와 저장소의 추가 맥락을 얻기 위해 code search를 사용할 수 있다고 설명합니다. 따라서 보안팀은 단순히 “GitHub 안에서 실행되니 데이터가 안전하다”고 가정하기보다 다음을 확인해야 합니다.

| 확인 항목 | 질문 |
| --- | --- |
| 데이터 범위 | 어떤 변경 파일과 저장소 맥락이 모델 입력이 되는가? |
| 라이선스·계약 | 조직의 소스 코드가 AI 기능 처리 조건에 맞는가? |
| 민감 정보 | 코드에 비밀·개인정보·고객 데이터가 들어가지 않도록 별도 검사하는가? |
| 접근 권한 | 결과와 CSV를 볼 수 있는 조직·보안 역할은 누구인가? |
| 보존·감사 | 결과와 피드백의 보존 기간, 감사 로그, 삭제 요청 절차는 무엇인가? |
| 외부 연결 | Fork·Dependabot·외부 PR에서 코드가 어떤 경계를 넘는가? |

비밀이 저장소에 들어오지 않게 하는 것이 첫 번째 방어선입니다. AI Scan이 비밀을 찾아 줄 수 있다는 기대 때문에 소스 코드에 테스트용 토큰이나 실제 개인정보를 남겨서는 안 됩니다.

## 5. 독립 연구가 보여 주는 “AI 보안 검사”의 현실

GitHub의 새 가시성 기능은 탐지 엔진을 더 신뢰하라는 메시지가 아니라, 적용 범위와 한계를 측정하라는 신호로 읽는 편이 좋습니다.

2026 GenAI Code Security Report는 테스트한 AI 코드 생성 작업 중 약 44%에서 알려진 취약점이 만들어졌다고 보고했습니다. 이 수치는 AI Scan의 성능을 직접 측정한 결과가 아니지만, AI가 생성한 코드가 빠르게 늘어날수록 보안팀이 모든 변경을 수작업으로 읽기 어렵다는 배경을 보여 줍니다.

최근 공개된 연구의 하이브리드 파이프라인 실험도 비슷한 교훈을 줍니다. CodeQL·Bandit 같은 정적 분석 결과를 LLM 기반 검토와 함께 사용하면 잔여 findings가 줄었지만, 자동 수정 과정에서 새로운 취약점이 생긴 비율도 15~22%로 보고됐습니다. 즉 **탐지와 수정은 별도의 검증 문제**입니다.

이 연구들을 GitHub 기능에 그대로 일반화할 수는 없습니다. 테스트 데이터·모델·언어·평가 기준이 다르기 때문입니다. 다만 다음 운영 원칙을 뒷받침하는 근거로는 충분합니다.

- AI 결과를 보안 사실이 아닌 검토할 신호로 취급
- 자동 수정은 원본 테스트와 보안 스캔을 다시 통과해야 승인
- 탐지율뿐 아니라 오탐·중복·수정 후 회귀를 측정
- 모델이나 기능이 바뀔 때 같은 샘플로 재평가

## 6. 조직에서 coverage를 운영하는 방법

### 1단계: 저장소 분류표 만들기

먼저 저장소를 공개·내부·고객 데이터·인프라 코드·교육용으로 나눕니다. 언어와 프레임워크, 저장소 소유 팀, 배포 환경, 규제 요구도 같이 기록합니다.

### 2단계: effective 상태를 CSV로 고정

Security overview에서 다음 필터를 이용해 목록을 내보냅니다.

~~~text
code-scanning-ai-scan-pr-scan:enabled
code-scanning-ai-scan-pr-scan:not-enabled
~~~

CSV에는 저장소 이름·소유 팀·AI Scan 상태·점검 날짜를 함께 보관합니다. 설정 화면을 캡처하는 것보다 변경 이력과 비교하기 쉽습니다.

### 3단계: 파일 유형별 파일럿

CodeQL 공백이 큰 Terraform·Dockerfile·Shell·PHP 저장소를 우선 선정하되, 외부 공개 코드나 학습용 샘플로 먼저 오탐을 확인합니다. 고객 데이터와 운영 권한이 있는 저장소는 결과 접근자와 비용 상한을 정한 뒤 포함합니다.

### 4단계: 결과 분류 규칙 정하기

AI Scan findings를 다음처럼 분류하면 알림 피로를 줄일 수 있습니다.

- 즉시 보안 검토: 인증 우회, 명령 주입, 비밀 노출
- 개발자 수정 후 재검토: 입력 검증, 권한 경계, 안전하지 않은 기본값
- 관찰 목록: 재현 조건이 부족하거나 중복 가능성이 있는 경고
- 오탐 피드백: 코드의 보호 경로와 테스트 근거를 함께 기록

### 5단계: 병합 게이트는 별도로 유지

현재 AI Scan 결과만으로 병합을 차단하지 말고, CodeQL·의존성·단위 테스트·수동 승인 같은 검증된 게이트를 유지합니다. AI Scan이 반복적으로 높은 정밀도를 보이는 규칙이 확인되면, 그 규칙을 별도 정책이나 CodeQL 쿼리로 승격하는 방식을 검토할 수 있습니다.

## 7. 비용과 운영 부하를 함께 측정하기

AI Scan은 공개 프리뷰 동안 GitHub Advanced Security와 GitHub Copilot 라이선스가 필요하고, 사용량은 AI credits를 소비합니다. 따라서 적용률을 높이는 것만으로 성공을 판단하면 안 됩니다.

| 지표 | 의미 |
| --- | --- |
| 활성화 저장소 비율 | 정책이 실제 저장소에 적용된 범위 |
| 대상 PR 대비 실행 비율 | 지원 언어·변경 조건에서 실제로 스캔된 비율 |
| PR당 AI credits | 비용과 모델 사용량 |
| 유효 findings 비율 | 보안팀이 확인한 실제 조치 필요 경고 |
| 오탐·중복 비율 | 개발자의 신뢰를 떨어뜨리는 경고 비중 |
| 수정 후 재발률 | 자동·수동 수정이 문제를 해결했는지 |
| 평균 triage 시간 | 보안팀이 결과를 처리하는 운영 부하 |
| CodeQL 공백 감소 | AI Scan이 추가로 덮은 위험 영역 |

“AI Scan을 켠 저장소 수”가 늘어도 처리되지 않은 findings가 쌓이면 보안 태세는 좋아지지 않습니다. 도입 전후의 PR 수·팀 인력·credits를 함께 비교해야 합니다.

## 8. 교육과 실무에서 해 볼 수 있는 검증 실습

실제 고객 코드를 사용하지 않고도 AI Scan의 역할과 한계를 이해할 수 있습니다.

1. PHP·Shell·Terraform·Dockerfile을 포함한 비민감 샘플 저장소를 만듭니다.
2. 고의로 안전하지 않은 명령 실행·하드코딩된 비밀·과도한 권한 설정을 넣습니다.
3. CodeQL이 지원하는 파일과 지원하지 않는 파일을 나누어 Pull Request를 만듭니다.
4. AI Scan 결과가 어디에 표시되고, CodeQL 결과와 어떤 차이가 있는지 기록합니다.
5. findings를 수정한 뒤 동일한 테스트와 스캔을 다시 실행합니다.
6. 한 번은 오탐이 될 만한 보호 코드도 넣어 피드백과 검토 절차를 연습합니다.

학생에게는 “AI가 취약점을 찾았다”보다 다음 질문을 던지는 편이 교육적입니다.

- 어떤 코드와 맥락이 모델에 제공됐는가?
- 결과가 재현 가능한가?
- 수정안이 새로운 취약점을 만들지 않았는가?
- 왜 이 결과는 병합 차단이 아니라 advisory인가?
- 스캔이 꺼진 저장소를 조직이 어떻게 발견하는가?

## 9. 한계와 도입 전 결정 사항

AI Scan을 만능 보안 분석기로 보면 안 되는 이유는 문서에 명시돼 있습니다.

- 현재 공개 프리뷰이며 기능과 지원 범위가 바뀔 수 있음
- Pull Request만 분석하고 전체 저장소·기본 브랜치 백로그는 지원하지 않음
- Fork와 Dependabot Pull Request에는 실행되지 않음
- 결과에 false positive가 포함될 수 있음
- 결과는 advisory이며 ruleset 병합 요구 조건으로 사용할 수 없음
- 지원 언어·탐지 범주가 계속 변경될 수 있음
- 프리뷰 동안 GHAS와 Copilot 라이선스, AI credits가 필요함

또한 AI가 코드의 의미를 이해하는 것과 실제 공격 경로를 재현하는 것은 다릅니다. 런타임 설정, 데이터베이스 권한, 클라우드 IAM, 배포 환경, 사용자 입력 흐름은 PR 코드만으로 판단하기 어렵습니다.

## 결론

10월 6일 GitHub의 AI Scan coverage 기능은 새로운 탐지 모델보다 **보안 기능이 어디에서 실제로 켜져 있는지 측정하는 운영 계층**을 추가했습니다. AI Scan은 CodeQL이 다루지 못하는 언어와 프레임워크의 Pull Request에 추가 신호를 제공할 수 있지만, 프리뷰이고 advisory이며 비용·오탐·데이터 처리 조건을 함께 관리해야 합니다.

가장 현실적인 도입 순서는 다음과 같습니다.

1. effective 활성화 상태를 CSV로 수집해 사각지대를 확인합니다.
2. CodeQL 공백이 큰 비민감 저장소에서 파일럿을 실행합니다.
3. findings의 유효성·오탐·credits·triage 시간을 측정합니다.
4. CodeQL·테스트·수동 승인을 병합 게이트로 유지합니다.
5. 반복해서 검증된 패턴만 자동화 정책으로 승격합니다.

AI 보안의 성숙도는 “AI 검사를 켰다”가 아니라 **어디에 적용됐고, 어떤 데이터가 처리됐으며, 결과를 누가 검증하고, 실패하면 어떻게 되돌리는지 설명할 수 있는가**로 판단해야 합니다.

## 참고 자료

- [GitHub Changelog, Code scanning AI Scan enablement status in security overview (2026-10-06)](https://github.blog/changelog/2026-10-06-code-scanning-ai-scan-enablement-status-in-security-overview/)
- [GitHub Docs, AI Scan for pull requests](https://docs.github.com/en/code-security/concepts/code-scanning/ai-powered-security-detections)
- [GitHub Docs, Security and quality AI features: responsible use](https://docs.github.com/en/code-security/responsible-use/security-and-quality-ai-features)
- [Veracode, 2026 GenAI Code Security Report](https://view.ceros.com/veracode/genai-code-security-report2026)
- [S. Surikov et al., Securing AI-Generated Code: A Just-in-Time Vulnerability Detection and Remediation Pipeline](https://arxiv.org/abs/2608.16187)

> AI Scan은 공개 프리뷰입니다. 실제 활성화 전에는 GitHub Advanced Security·Copilot 라이선스, AI credits, 저장소 코드 처리 조건, 조직의 보안·개인정보 정책과 최신 GitHub 문서를 함께 확인하세요.
