---
layout: default
title: "EKS에서 GKE로 옮기는 AI 에이전트: 결정론적 가드레일이 필요한 이유"
date: 2026-10-05 06:00:00 +0900
excerpt: "Google Cloud가 EKS-to-GKE 마이그레이션을 지원하는 오픈소스 에이전트 플러그인을 공개했다. LLM 번역을 Terraform·Kubernetes 검증, GitOps PR, 데이터 이동 런북으로 감싸는 구조와 한계를 분석한다."
tags: [Kubernetes, GKE, 클라우드마이그레이션, 생성형AI, GitOps]
ai_assisted: true
---

# EKS에서 GKE로 옮기는 AI 에이전트
## 결정론적 가드레일이 필요한 이유

클라우드 마이그레이션에서 가장 어려운 일은 YAML 문법을 바꾸는 것이 아닙니다. AWS EKS에 묶인 네트워크, IAM, 로드 밸런서, 스토리지, 노드 자동 확장, 배포 파이프라인의 의미를 다른 클라우드의 자원과 운영 모델로 보존하는 일입니다.

Google Cloud는 2026년 9월 24일 **GKE agentic migration**의 오픈소스 공개를 발표했습니다. 10월 2일 Google Cloud 최신 소식은 이 기능을 **결정론적 가드레일을 갖춘 AI-assisted EKS-to-GKE 마이그레이션 공개 프리뷰**로 소개했습니다. 이 플러그인은 일반적인 “코드를 바꿔 줘” 프롬프트 대신, 소스 저장소를 분석하고 번역 결과를 오프라인에서 검증한 뒤 검토 가능한 Pull Request와 데이터 이동 런북을 만드는 흐름을 목표로 합니다.

> 이 글은 Google Cloud의 발표와 10월 2일 제공 범위 안내, AWS의 9월 30일 EKS 마이그레이션 평가 에이전트 기술 글, Kubernetes 공식 워크로드·RBAC 문서, CNCF의 복구 검증 연구를 교차 확인해 작성했습니다. 공개 프리뷰인 만큼 지원 범위와 구현 세부는 바뀔 수 있으므로 실제 마이그레이션에서는 저장소와 최신 문서를 함께 검토해야 합니다.

## 1. 왜 일반 LLM 프롬프트만으로는 부족한가

EKS 구성 파일을 GKE 구성 파일로 바꾸는 작업에 LLM을 사용하면 첫 초안은 빨리 얻을 수 있습니다. 하지만 다음과 같은 오류는 겉보기 YAML 검토만으로 발견하기 어렵습니다.

- 존재하지 않는 클라우드 리소스 속성이나 폐기된 Kubernetes API를 생성함
- AWS IAM Roles for Service Accounts(IRSA)를 GKE Workload Identity로 옮기면서 주체·조건·토큰 흐름을 누락함
- AWS Application Load Balancer의 동작을 단순 Ingress 객체로 바꾸고 헬스 체크·TLS·네트워크 정책을 잃음
- Karpenter의 노드 요구 조건을 GKE의 Node Auto Provisioning 또는 Custom Compute Classes로 바꾸지 못함
- EBS/EFS 볼륨과 스냅샷을 매니페스트만 복사해 데이터가 옮겨졌다고 오해함
- 여러 파일에 흩어진 ConfigMap, Secret, DNS, 메시지 큐, 외부 데이터베이스 의존성의 순서를 잃음

Google은 이러한 문제를 “자동화 신뢰 격차”로 설명합니다. 코드가 거의 맞는 수준이면 오히려 사람이 모든 파일을 다시 디버깅해야 하므로, 작성 시간이 줄어도 검증 비용과 실행 위험이 커질 수 있습니다.

핵심은 모델이 모든 결정을 내리게 하는 것이 아니라, **모델이 잘하는 해석과 사람이·도구가 보장해야 하는 제약을 분리하는 것**입니다.

## 2. GKE agentic migration의 구조

Google의 플러그인은 에이전트 스킬 모음과 로컬 MCP 서버를 결합합니다. 중앙 제어면이 실시간 클러스터를 변경하는 방식이 아니라, 개발자의 기존 에이전트 하네스에서 다음 흐름을 수행합니다.

```text
EKS Git 저장소 또는 읽기 전용 클러스터 스캔
        ↓
매니페스트·Terraform·의존성 인덱싱
        ↓
호환성 평가와 blocker 보고서
        ↓
GKE landing zone 설계
        ↓
LLM 기반 번역 + 결정론적 변환
        ↓
Terraform·Kubernetes 오프라인 검증
        ↓
Pull Request와 데이터 이동 런북
        ↓
사람 승인 후 기존 CI/CD로 배포
```

발표에서 설명한 주요 단계는 다음과 같습니다.

| 단계 | 에이전트가 하는 일 | 사람이 결정해야 하는 일 |
| --- | --- | --- |
| 발견 | 소스 저장소를 복제하거나 EKS를 스캔하고 리소스·의존성을 목록화 | 스캔 대상과 민감 정보 범위 |
| 평가 | 아키텍처 호환성, blocker, 예상 작업을 보고 | 마이그레이션 경계와 우선순위 |
| Landing zone | VPC, 서브넷, GKE 클러스터, 조직 정책 Terraform 초안 생성 | Autopilot과 Standard, 리전·네트워크·규정 선택 |
| 번역 | IRSA·ALB·Karpenter 등 클라우드 전용 개념을 대응 개념으로 변환 | 의미가 같은지, 성능·보안 요구를 유지하는지 |
| 검증 | `terraform validate`, 매니페스트 계약, 출력 형식 검증 | 테스트 데이터와 승인 기준 |
| 전달 | 직접 배포하지 않고 PR과 런북 생성 | 코드 리뷰, 병합, 실행·롤백 |

이 구조에서 중요한 문장은 **플러그인이 라이브 클러스터에 직접 변경을 적용하지 않는다**는 점입니다. 소스의 목표 상태를 만들고 PR로 보낼 뿐이므로, 조직의 CI/CD와 리뷰·승인·감사 체계를 그대로 사용할 수 있습니다.

## 3. “AI 번역 + 결정론적 검증”의 의미

LLM은 서로 의존하는 Terraform과 YAML의 의도를 추론하고, 사람이 작성한 설명에서 반복 패턴을 찾아내는 데 강합니다. 반면 다음과 같은 것은 결정론적 도구가 더 잘합니다.

- 허용된 API 버전과 필수 필드 확인
- 리소스 간 참조가 끊기지 않았는지 검사
- Workload Identity 주석과 이미지 레지스트리 주소의 정확한 매핑
- Terraform 문법·provider 스키마·출력 계약 확인
- 금지된 권한, 공개 엔드포인트, 누락된 네트워크 정책 차단

GKE agentic migration은 이 둘을 하이브리드로 묶습니다. LLM이 Terraform·Kubernetes YAML을 작성하더라도, 서버가 정확한 변환을 수행하고 `terraform validate`와 매니페스트 검사를 통과해야 사용자에게 제안됩니다. 마지막에는 사람이 승인해야 합니다.

여기서 주의할 점은 “검증 통과 = 운영 의미 보장”이 아니라는 것입니다. `terraform validate`는 문법과 provider 수준의 구조를 확인하지만 다음을 알 수는 없습니다.

- 실제 트래픽 패턴에서 새 로드 밸런서가 같은 지연·보호 수준을 내는가
- IAM 권한이 최소 권한인가
- 데이터베이스의 일관성과 복구 목표가 유지되는가
- 요금과 egress가 예산 안에 들어오는가
- 암호화 키와 감사 로그가 규정에 맞는가

따라서 결정론적 검증은 필요한 바닥선이지, 운영 승인 자체가 아닙니다.

## 4. 클라우드 전용 개념을 바꾸는 순간

### IRSA에서 Workload Identity로

EKS의 IRSA는 Kubernetes 서비스 계정과 AWS IAM 역할의 연결입니다. GKE에서는 Workload Identity Federation for GKE 같은 Google Cloud의 주체·토큰 모델을 사용합니다. 이름이 비슷한 권한으로 치환하는 작업이 아니라 다음을 다시 설계해야 합니다.

- 어떤 Kubernetes 서비스 계정이 어떤 Google 서비스 계정 또는 주체가 되는가
- 토큰 교환의 대상과 조건은 무엇인가
- 버킷·Secret·Pub/Sub·데이터베이스별 최소 권한이 적용됐는가
- 애플리케이션이 AWS SDK 환경 변수에 의존하고 있지 않은가

에이전트가 주석을 바꿔 줄 수는 있지만, 권한의 업무 목적과 데이터 경계를 판정할 수는 없습니다. 권한 diff를 별도 리뷰 대상으로 두어야 합니다.

### ALB에서 Gateway API로

AWS Application Load Balancer에 들어 있던 TLS 종료, 호스트 기반 라우팅, 보안 그룹, 헬스 체크, WAF 연계는 단순한 Ingress 이름 변경으로 보존되지 않습니다. Google 발표는 ALB Ingress를 Gateway API로 매핑하는 흐름을 예로 듭니다.

번역 후에는 다음을 테스트해야 합니다.

1. 외부·내부 서비스의 경로와 포트가 같은가?
2. 인증서 갱신과 TLS 최소 버전이 같은가?
3. 원본 클라이언트 IP와 로깅 필드가 유지되는가?
4. WAF·rate limit·NetworkPolicy가 같은 요청을 허용하거나 차단하는가?
5. 장애 시 헬스 체크와 연결 드레이닝 동작이 같은가?

### Karpenter에서 GKE 노드 모델로

Karpenter의 노드 클레임은 AWS 인스턴스 선택·가용 영역·용량 유형·taint/toleration을 조합합니다. GKE에서는 Node Auto Provisioning과 Custom Compute Classes 등으로 같은 의도를 표현할 수 있지만, 인스턴스 이름을 1:1로 바꾸는 문제가 아닙니다.

CPU·메모리·GPU·로컬 디스크·Spot/Preemptible 정책과 함께 다음을 다시 계산해야 합니다.

- 파드의 requests/limits와 실제 사용량
- 노드 부팅 시간과 이미지 캐시
- GPU 분할 또는 드라이버 버전
- 비용과 선점 시 재시작 허용 범위
- Pod topology spread와 장애 영역 분산

## 5. GitOps PR이 만드는 안전 경계

마이그레이션 도구가 실시간 `kubectl apply`나 클라우드 API 호출을 해 버리면 편해 보이지만, 변경이 Git 기록을 벗어나고 롤백 기준이 흐려집니다. Google은 이 방식을 “ClickOps 위험”으로 지적하며, GKE agentic migration은 검증된 결과를 PR로만 전달한다고 설명합니다.

PR 기반 흐름의 장점은 다음과 같습니다.

- 변경 전·후 diff를 사람이 읽을 수 있음
- 기존 CI에서 정책·보안 스캔·테스트를 재사용할 수 있음
- 리뷰어와 승인자가 변경 소유권을 가질 수 있음
- 실패한 배포를 이전 커밋으로 되돌릴 수 있음
- 마이그레이션 작업과 운영 배포를 분리할 수 있음

그러나 GitOps가 데이터까지 복구해 주는 것은 아닙니다. CNCF의 2026년 복구 실험은 Git이 선언된 리소스를 재생성해도 Persistent Volume의 실제 데이터가 자동으로 돌아오지 않는 사례를 보여 줍니다. Kubernetes 공식 문서도 Deployment는 주로 무상태 워크로드에, StatefulSet은 안정적인 식별자와 영속 스토리지가 필요한 워크로드에 사용한다고 구분합니다.

즉 PR에는 다음이 함께 있어야 합니다.

- 매니페스트·Terraform 변경
- 데이터베이스·파일·메시지 큐별 데이터 이동 계획
- 백업 검증과 복구 리허설 결과
- DNS·인증서·비밀·외부 연동 전환 순서
- 중단 허용 시간과 되돌리기 조건

## 6. 번역과 데이터 이동을 분리한 이유

GKE agentic migration은 상태 있는 데이터를 직접 옮기지 않고, Database Migration Service나 Storage Transfer Service 같은 전용 도구를 사용할 런북을 생성한다고 설명합니다.

이 분리는 설계상 중요합니다.

| 구분 | 번역 플러그인 | 데이터 이동 도구 |
| --- | --- | --- |
| 대상 | Terraform, Kubernetes YAML, 의존성·정책 | 데이터베이스 레코드, 객체, 볼륨, 로그 |
| 검증 | 문법·구조·매핑·정책 | 일관성, 체크섬, 복제 지연, 재시작 |
| 실패 복구 | PR revert와 재생성 | 스냅샷·증분 복제·재동기화 |
| 책임 | 원하는 목표 상태를 표현 | 실제 데이터의 손실·중복·순서 방지 |

매니페스트가 성공적으로 적용돼도 데이터가 비어 있으면 서비스는 정상적으로 복구된 것이 아닙니다. 특히 StatefulSet과 외부 데이터베이스는 애플리케이션의 쓰기 중단, 복제 지연, cutover, DNS TTL, 재처리 방지까지 포함하는 별도 런북이 필요합니다.

## 7. 장기 마이그레이션을 위한 상태와 역할

마이그레이션은 한 번의 프롬프트로 끝나지 않고 여러 팀이 몇 주 동안 나눠 진행하는 작업입니다. Google은 플러그인이 마이그레이션 상태 그래프를 유지하고, 플랫폼 엔지니어가 landing zone을 만들고 애플리케이션 개발자가 권한이 분리된 폴더에서 워크로드를 이어서 번역할 수 있다고 설명합니다.

이 구조를 운영할 때는 다음을 명확히 해야 합니다.

- 플랫폼 팀: 네트워크·조직 정책·클러스터 버전·공통 보안 기준
- 애플리케이션 팀: 서비스 매니페스트·이미지·환경 변수·SLO
- 데이터 팀: 데이터 이동·정합성·보존·복구
- 보안 팀: IAM·Secret·감사·외부 통신
- 승인자: blocker 해소 여부와 cutover 기준

Kubernetes RBAC 공식 권고처럼 서비스 계정과 사용자는 필요한 리소스와 네임스페이스에만 최소 권한을 가져야 합니다. 상태 그래프가 편리하더라도, 그 파일과 작업 폴더에 운영 자격 증명이 들어가지 않도록 해야 합니다.

## 8. AWS의 EKS 평가 에이전트와 비교하기

AWS도 2026년 9월 30일 Bedrock AgentCore와 Strands Agents SDK를 이용한 EKS 마이그레이션 평가 에이전트 예제를 공개했습니다. 이 에이전트는 Git 저장소와 컨테이너 산출물을 읽고, 코드 수준의 blocker·준비도 점수·추정 작업량·마이그레이션 계획을 생성합니다. 비밀·스토리지·네트워크·인증·메시징·관측성까지 분석하고, 결과를 구조화된 보고서로 반환합니다.

두 접근은 경쟁 제품의 승패보다 서로 다른 문제를 보여 줍니다.

| 관점 | GKE agentic migration | AWS EKS migration assessment |
| --- | --- | --- |
| 주된 목적 | EKS 구성의 GKE 목표 상태 번역과 PR 생성 | 애플리케이션의 EKS 이동 준비도 평가 |
| 안전 경계 | 결정론적 변환·오프라인 검증·PR-only | AgentCore 세션 격리·구조화된 평가 보고서 |
| 데이터 처리 | 상태 데이터는 전용 이동 서비스 런북으로 분리 | 소스·컨테이너 분석 후 평가 결과 생성 |
| 판단 시점 | 번역 전 blocker 소유자·해결일 지정 | 평가 점수·심각도·예상 시간으로 우선순위화 |
| 한계 | GKE로의 목표 상태와 클라우드 의미에 집중 | EKS 준비도 분석이며 실제 cutover는 별도 |

이 비교에서 얻는 교훈은 **에이전트의 출력 형식보다 경계가 중요하다**는 것입니다. 평가 에이전트, 번역 에이전트, 배포 파이프라인, 데이터 이동 도구를 하나의 자격 증명으로 묶으면 편리해도 실패 반경이 커집니다.

## 9. 도입 전 체크리스트

### 발견과 개인정보

- 소스 저장소와 클러스터 스캔 범위를 최소화했는가?
- Secret 값과 고객 데이터가 모델 입력·로그·상태 파일에 들어가지 않는가?
- 외부 MCP 서버나 플러그인의 네트워크 egress를 제한했는가?
- 에이전트가 읽기 전용 자격으로 시작하는가?

### 번역 품질

- IRSA, ALB, Karpenter, EBS/EFS, CloudWatch 등 AWS 전용 개념의 대응 설계를 문서화했는가?
- API 버전과 폐기 예정 필드를 결정론적으로 검사하는가?
- 이미지 레지스트리·서명·SBOM·취약점 정책을 유지하는가?
- Terraform validate 외에 정책 테스트와 실제 트래픽 테스트가 있는가?

### 운영 승인

- 모든 변경이 PR과 CI를 거치는가?
- 플랫폼·애플리케이션·데이터·보안의 승인자가 명확한가?
- blocker마다 소유자와 해결 목표일이 있는가?
- cutover와 rollback을 실제로 연습했는가?

### 상태 데이터

- 데이터베이스, 오브젝트, 볼륨, 메시지 큐를 각각 어떤 도구로 옮기는가?
- 증분 복제 지연과 체크섬을 어떻게 검증하는가?
- DNS TTL·인증서·비밀 전환 순서가 정해져 있는가?
- 복구 클러스터에서 애플리케이션과 실제 데이터를 함께 확인했는가?

## 10. 교육·실무 실습으로 검증하기

이 기능은 클라우드 중립성보다 **검증 가능한 자동화**를 가르치는 실습에 적합합니다.

1. 작은 공개 EKS 샘플 저장소를 준비하고, 민감한 Secret은 제거합니다.
2. 에이전트에게 먼저 “분석만” 요청해 리소스·의존성·blocker 보고서를 만듭니다.
3. IRSA 하나, ALB 하나, StatefulSet 하나를 골라 대응 설계를 사람이 먼저 작성합니다.
4. 에이전트의 번역 결과와 사람이 만든 설계를 비교하고, 권한·네트워크·스토리지 차이를 표로 기록합니다.
5. `terraform validate`, Kubernetes schema 검사, 정책 테스트, 이미지 취약점 스캔을 CI에서 실행합니다.
6. PR을 병합하지 않은 상태에서 데이터 이동 런북만 리허설하고, 복구 클러스터에서 실제 데이터가 있는지 검증합니다.

평가 기준은 “몇 줄의 YAML을 자동 생성했는가”가 아닙니다.

- 잘못된 매핑을 사람이 발견할 수 있는가
- 에이전트가 권한 부족을 안전하게 보고하는가
- 생성된 변경이 Git 기록과 재현 가능한가
- 데이터와 선언 상태를 함께 복구할 수 있는가
- 비용·성능·보안의 회귀를 측정하는가

## 결론

GKE agentic migration의 핵심은 클라우드 이동을 한 번의 AI 프롬프트로 자동화한다는 데 있지 않습니다. **LLM의 해석 능력을 결정론적 변환, 오프라인 검증, GitOps PR, 사람 승인, 데이터 이동 런북으로 둘러싸는 것**이 진짜 변화입니다.

EKS에서 GKE로 옮길 때 IRSA·ALB·Karpenter 같은 개념은 이름만 바꾸면 되는 리소스가 아니라 권한·네트워크·성능·운영 정책의 묶음입니다. 또한 Kubernetes의 선언 상태와 데이터 저장 상태는 서로 다르므로, PR이 성공했다고 마이그레이션이 끝난 것은 아닙니다.

공개 프리뷰를 실제 프로젝트에 적용한다면 읽기 전용 발견과 평가부터 시작하고, 작은 무상태 서비스에서 번역·검증·PR 흐름을 시험한 뒤, StatefulSet과 데이터 이동을 별도 단계로 확대하는 것이 안전합니다. AI가 생성한 목표 상태를 빠르게 얻는 것보다 **왜 그 상태가 안전한지, 어떻게 검증하고 되돌릴지 설명할 수 있는 팀**을 만드는 것이 클라우드 마이그레이션의 성패를 좌우합니다.

## 참고 자료

- [Google Cloud Blog, Introducing GKE agentic migration for AI-assisted EKS-to-GKE migrations with built-in governance (2026-09-24)](https://cloud.google.com/blog/products/containers-kubernetes/gke-agentic-migration)
- [Google Cloud, What’s new with Google Cloud (2026-10-02)](https://cloud.google.com/blog/topics/inside-google-cloud/whats-new-google-cloud?hl=en)
- [AWS Containers Blog, AI-powered EKS migration assessment with Amazon Bedrock AgentCore (2026-09-30)](https://aws.amazon.com/blogs/containers/ai-powered-eks-migration-assessment-with-amazon-bedrock-agentcore/)
- [Kubernetes, Workloads](https://kubernetes.io/docs/concepts/workloads/)
- [Kubernetes, RBAC good practices](https://kubernetes.io/docs/concepts/security/rbac-good-practices/)
- [CNCF, Kubernetes disaster recovery: Guidance from three reproducible failure scenarios (2026-09-10)](https://www.cncf.io/blog/2026/09/10/kubernetes-disaster-recovery-guidance-from-three-reproducible-failure-scenarios/)

> GKE agentic migration은 공개 프리뷰이며, 지원되는 클라우드 매핑·에이전트 하네스·지역·검증 규칙은 변경될 수 있습니다. 실제 마이그레이션 전에는 공식 저장소의 온보딩 가이드, 조직의 보안 정책, 백업·복구 담당자의 승인을 함께 확인하세요.
