---
layout: default
title: "GitHub Actions Runner Controller 0.15.0: 러너 확장보다 먼저 설계할 제어 루프"
date: 2026-10-09 06:00:00 +0900
excerpt: "GitHub Actions Runner Controller 0.15.0이 대규모 러너 풀의 패치·종료·메트릭·재조정 동작을 개선했다. Kubernetes 기반 CI를 도입할 때 확장 속도보다 제어 루프, 비용, 격리와 관측성을 어떻게 설계해야 하는지 분석한다."
tags: [GitHub Actions, Kubernetes, DevOps, CI/CD, 보안]
ai_assisted: true
---

## 러너 수보다 제어 루프가 먼저다

CI 작업이 늘면 조직은 곧바로 “러너를 몇 개 더 띄울 것인가?”를 묻습니다. 그러나 Kubernetes에서 GitHub Actions self-hosted runner를 운영할 때 병목은 Pod 개수만이 아닙니다.

> GitHub의 작업 큐, ARC listener, Kubernetes API 서버, controller 재조정, 노드 오토스케일러가 한 번의 빌드 지연을 함께 만든다.

GitHub는 2026년 10월 1일 Actions Runner Controller(ARC) 0.15.0을 공개했습니다. 이번 릴리스는 runner scale set의 안정성·확장성·관측성을 다듬는 데 초점을 맞췄습니다. 패치 업그레이드 시 리소스를 제자리에서 갱신하고, controller 종료 시간을 조정할 수 있으며, 사라진 Actions 서비스의 scale set을 다시 등록하고, 러너 상태를 CRD status 대신 메트릭으로 집계합니다. listener의 Kubernetes API QPS·burst와 controller별 동시 reconcile 수도 조정할 수 있습니다.

이 글은 GitHub Changelog와 ARC 0.15.0 릴리스, GitHub의 runner scale set 문서, self-hosted runner 보안 지침, GitLab의 독립적인 self-managed runner 보안 문서와 OIDC·SPIFFE 연구를 교차 확인해 작성했습니다. ARC 버전과 차트의 세부 동작은 계속 바뀔 수 있으므로 운영 전에는 최신 릴리스 노트를 다시 확인해야 합니다.

## 1. ARC는 무엇을 자동화하는가

ARC는 Kubernetes operator로서 GitHub Actions의 runner scale set API와 Kubernetes 리소스를 연결합니다. 조직 또는 저장소에 연결된 AutoscalingRunnerSet이 작업 수요를 감지하면 listener가 필요한 수의 ephemeral runner Pod를 요청하고, 작업이 끝난 러너는 회수됩니다.

GitHub 공식 문서는 ARC를 Kubernetes 환경에서 self-hosted runner를 자동 확장하기 위한 권장 reference implementation으로 설명합니다. runner scale set은 저장소·조직·엔터프라이즈 수준에 배치할 수 있고, GitHub App 인증과 runner group으로 접근 범위를 제한할 수 있습니다.

구조를 단순화하면 다음과 같습니다.

~~~text
GitHub Actions 작업 큐
        ↓
ARC listener ── 작업 수와 runner 상태 확인
        ↓
AutoscalingRunnerSet controller
        ↓
EphemeralRunner Pod 생성·회수
        ↓
Kubernetes scheduler·노드 오토스케일러
        ↓
빌드·테스트 실행
~~~

이 구조에서 runner 수를 무작정 늘리면 Kubernetes API 요청, 이미지 pull, 노드 부팅, GitHub 등록 지연이 함께 늘어날 수 있습니다. 따라서 이번 릴리스의 핵심은 “더 많은 Pod”가 아니라 **제어 루프가 불필요한 일을 덜 하고 실패에서 빨리 회복하도록 만든 것**입니다.

## 2. 0.15.0의 변화와 운영 의미

| 변경 | 기술적 의미 | 운영자가 확인할 지표 |
| --- | --- | --- |
| 패치 업그레이드 시 리소스 in-place 갱신 | AutoscalingRunnerSet과 EphemeralRunnerSet 사이의 불필요한 재생성 감소 | 업그레이드 중 대기 작업 수, Pod 재생성 수 |
| terminationGracePeriodSeconds 설정 가능 | controller 종료와 graceful shutdown 시간 정렬 | 롤링 업데이트 중 처리 완료율 |
| 사라진 scale set 재등록 | Actions 서비스의 상태 유실 뒤 수동 복구 작업 감소 | 등록 실패·재등록 횟수 |
| Update 대신 Patch 사용 | Kubernetes API payload와 충돌 범위 축소 | API 서버 요청량, 409/429 응답 |
| 러너 상태를 메트릭으로 집계 | CRD status 쓰기 경쟁과 API 서버 쓰기 감소 | 메트릭 수집 간격, status write 감소 |
| listener QPS·burst 설정 | 대규모 작업 큐에서 API 클라이언트 속도 조절 | API throttling, queue latency |
| controller 동시 reconcile 설정 | 처리량과 API 서버 부하를 환경에 맞게 조정 | reconcile duration, workqueue depth |
| 이벤트 필터링 | 소유 리소스의 의미 없는 재조정 감소 | reconcile rate, CPU 사용량 |
| 정상 종료한 ephemeral runner 빠른 삭제 | 끝난 작업의 자원 회수 지연 단축 | 종료 후 Pod 잔류 시간 |

여기서 “Patch로 바뀌었다”는 사실만으로 성능이 보장되지는 않습니다. 동시 reconcile 수를 올리면 controller는 빠르게 보일 수 있지만, Kubernetes API 서버와 etcd에 같은 비율로 여유가 있다는 뜻은 아닙니다. 0.15.0은 튜닝할 손잡이를 늘렸고, 최적값은 클러스터 규모·작업 폭주 패턴·노드 프로비저닝 시간에 따라 달라집니다.

## 3. 상태를 CRD에서 메트릭으로 옮긴 이유

대규모 controller는 리소스의 상태를 Kubernetes API의 status 필드에 계속 기록합니다. 상태가 러너 수와 함께 빠르게 바뀌면 다음 문제가 생길 수 있습니다.

- 같은 리소스를 여러 reconcile이 갱신하며 충돌이 발생
- API 서버와 etcd에 쓰기 요청이 쌓임
- 상태 기록 자체가 작업 처리보다 느려짐
- 운영자가 오래된 status를 현재 실행 상태로 오해함

ARC 0.15.0은 EphemeralRunnerSet과 AutoscalingRunnerSet의 runner 상태 집계를 메트릭으로 이동했습니다. 이는 “상태를 잃었다”는 뜻이 아니라, **운영 대시보드의 원본을 CRD 조회에서 메트릭 스크랩으로 바꿔야 한다**는 뜻입니다.

도입 전에는 다음을 확인해야 합니다.

1. Prometheus가 controller와 listener의 메트릭 endpoint를 수집하는가?
2. 대시보드가 CRD status에만 의존하고 있지 않은가?
3. 메트릭 라벨에 저장소·조직·runner scale set을 넣을 때 카디널리티가 폭증하지 않는가?
4. 메트릭이 끊겼을 때 알림과 kubectl 기반의 보조 진단 절차가 있는가?
5. 메트릭의 scrape interval이 작업 큐 지연을 설명할 만큼 짧은가?

메트릭으로 옮긴 것은 관측성의 품질을 높일 수 있는 변화지만, 기존 대시보드를 자동으로 고쳐 주지는 않습니다. 릴리스 업그레이드의 완료 조건에 “빌드가 성공했다”뿐 아니라 “운영자가 queue-to-runner 지연을 계속 볼 수 있다”를 포함해야 합니다.

## 4. maxRunners와 minRunners는 비용·대기시간 계약이다

GitHub 문서의 runner scale set은 maxRunners와 minRunners로 범위를 정합니다. minRunners를 0으로 두면 대기 작업이 없을 때 0개까지 내려갈 수 있고, minRunners를 유지하면 첫 작업을 받을 warm runner를 남길 수 있습니다. maxRunners를 두지 않으면 할당된 작업 수만큼 확장할 수 있지만, 노드·레지스트리·클라우드 계정의 상한을 대신 만들어야 합니다.

예를 들어 다음 세 정책은 서로 다른 서비스 수준을 만듭니다.

| 정책 | 장점 | 대가 |
| --- | --- | --- |
| min 0, max 10 | 유휴 비용 최소화 | 첫 작업의 Pod·노드 cold start 지연 |
| min 2, max 10 | 평균 대기시간 감소 | 항상 두 runner의 노드·이미지 비용 |
| min 10, max 50 | 사내 대규모 병렬 빌드에 유리 | idle 비용과 패치 면적 증가 |

ARC는 예정된 시간대별 min/max 스케줄을 자체적으로 제공하지 않습니다. 업무 시간에만 warm runner를 유지하려면 별도의 스케줄러나 설정 변경 자동화를 설계해야 합니다.

운영자는 “runner당 단가” 대신 다음을 함께 측정해야 합니다.

- 작업 큐에 들어온 시각부터 runner가 job을 시작한 시각까지의 p50·p95
- Pod 생성부터 등록까지 걸린 시간
- 노드가 없을 때 새 노드가 Ready가 되기까지의 시간
- 이미지 pull과 캐시 적중률
- minRunners가 유휴로 남은 시간과 비용
- maxRunners에 막혀 재대기한 작업 수
- 작업 취소·재시도·노드 부족 비율

이 지표가 있어야 “minRunners를 2에서 5로 올리자”라는 결정을 비용과 사용자 경험의 언어로 설명할 수 있습니다.

## 5. graceful shutdown과 in-place 업그레이드

CI controller는 배포 중에도 작업을 잃으면 안 됩니다. 0.15.0은 terminationGracePeriodSeconds를 설정 가능하게 하고 controller manager의 graceful shutdown timeout과 정렬합니다. 패치 업그레이드가 리소스를 제자리에서 갱신하는 변화와 결합하면, 업그레이드 때 scale set 전체가 잠깐 사라지는 상황을 줄일 수 있습니다.

하지만 graceful shutdown은 이미 실행 중인 작업을 무한정 보호하지 않습니다. 종료 시 다음 경계를 먼저 정해야 합니다.

- 새 작업을 받지 않는 drain 시간
- 이미 실행 중인 job이 완료되기를 기다리는 최대 시간
- 시간이 지나면 재시도할 작업과 실패 처리할 작업
- controller와 listener 중 어느 쪽을 먼저 종료할지
- 노드 오토스케일러가 drain 중인 Pod를 강제 삭제하지 않는지

교육 환경에서는 작은 kind 클러스터에서 controller deployment를 롤링 업데이트하며 queue latency와 job 재시도 수를 기록해 볼 수 있습니다. 운영 환경에서는 업그레이드 전후에 같은 테스트 workflow를 여러 번 실행해 “한 번 성공했다”가 아니라 “작업 손실률이 허용 범위 안이다”를 검증해야 합니다.

## 6. API 서버 부하를 줄이는 튜닝 순서

listener QPS·burst와 controller 동시 reconcile은 강력하지만 위험한 튜닝 포인트입니다. 값을 먼저 크게 잡고 API 서버가 버티는지 보는 방식은 장애를 키울 수 있습니다.

권장 순서는 다음과 같습니다.

1. 현재 listener 요청량, API throttling, workqueue depth를 기준선으로 수집합니다.
2. 이벤트 필터링과 Patch 전환만 적용한 뒤 같은 workload를 재생합니다.
3. reconcile duration과 queue latency가 안정된 범위에서 동시성을 조금씩 올립니다.
4. Kubernetes API 서버의 429, etcd fsync latency, controller CPU·메모리를 함께 관찰합니다.
5. 폭주 시 maxRunners와 동시성을 낮추는 운영 runbook을 만듭니다.

여기서 중요한 것은 처리량의 최대값이 아니라 **백프레셔**입니다. GitHub 작업이 갑자기 1,000개 들어와도 Kubernetes API와 클라우드 노드 프로비저너가 감당할 수 없는 속도로 Pod를 만들면, 결과는 빠른 CI가 아니라 API throttling과 긴 대기열입니다.

## 7. 보안은 ephemeral이라는 단어만으로 끝나지 않는다

ARC는 ephemeral runner를 만들고 작업이 끝나면 회수하지만, 격리는 Kubernetes 설정에 달려 있습니다. GitLab의 self-managed runner 보안 문서도 비영구 runner를 쓰지 않거나 privileged container를 공유하면 다른 프로젝트의 코드와 비밀이 노출될 수 있다고 경고합니다. Docker privileged 모드와 host PID namespace는 컨테이너 탈출 위험을 키우므로 신뢰되지 않은 코드에 그대로 제공해서는 안 됩니다.

ARC를 도입할 때 최소한 다음 경계를 별도로 설계해야 합니다.

| 경계 | 점검 질문 |
| --- | --- |
| runner group | 어떤 조직·저장소가 어떤 scale set을 사용할 수 있는가? |
| GitHub App | 토큰·private key가 Kubernetes Secret에만 보관되는가? |
| 노드 격리 | runner Pod가 업무 서비스와 같은 노드·네임스페이스를 공유하는가? |
| 네트워크 | 빌드가 내부 데이터베이스·메타데이터 서버에 접근할 수 있는가? |
| 이미지 | runner image와 action dependency를 어떻게 서명·갱신하는가? |
| 파일시스템 | 작업 종료 후 workspace·캐시·임시 비밀이 남지 않는가? |
| fork PR | 외부 코드가 내부 권한 runner에 도달하지 않는가? |
| 클라우드 권한 | 정적 키 대신 OIDC 또는 짧은 수명의 workload identity를 쓰는가? |

OIDC·SPIFFE 기반 CI/CD 연구는 runner를 단순한 컴퓨팅 자원이 아니라 비인간 주체의 신원으로 보고, 런타임에 발급한 신원과 정책 기반 접근을 권장합니다. ARC의 scale-to-zero가 클라우드 비용을 낮춰도, Pod가 발급받는 IAM 권한이 과도하면 공격 표면은 줄지 않습니다.

특히 Docker-in-Docker를 위해 privileged를 켜는 경우에는 “ephemeral Pod니까 안전하다”는 결론을 내리면 안 됩니다. 전용 노드, 짧은 수명의 자격 증명, 네트워크 정책, 이미지 서명, 작업별 cleanup을 함께 적용해야 합니다.

## 8. 0.15.0에서 바로 적용할 수 있는 파일럿

민감한 운영 저장소로 시작하기보다 다음과 같은 비민감 샘플로 기능과 메트릭을 확인하는 편이 안전합니다.

1. GitHub App과 전용 runner group을 만듭니다.
2. 테스트 저장소에 ARC scale set을 연결하고 minRunners 0, maxRunners 3으로 시작합니다.
3. 1개·3개·10개의 병렬 workflow를 순서대로 실행합니다.
4. GitHub queue time, listener 요청량, reconcile duration, Pod 등록 시간을 수집합니다.
5. controller deployment를 롤링 업데이트해 graceful shutdown과 작업 재시도를 확인합니다.
6. Actions 서비스에서 scale set을 제거한 뒤 controller가 다시 등록하는지 확인합니다.
7. runner Pod 종료 후 workspace·캐시·토큰이 남지 않는지 검사합니다.
8. maxRunners를 초과한 작업과 API throttling이 발생했을 때의 대응 절차를 문서화합니다.

교육에서는 같은 실습을 두 번 수행하면 효과적입니다. 첫 번째는 minRunners 0으로 비용과 cold start를 관찰하고, 두 번째는 minRunners 1 또는 2로 대기시간을 비교합니다. 학생은 “autoscaling이 빠르다”가 아니라 **대기시간·비용·격리·관측성 사이의 계약을 수치로 설명하는 방법**을 배우게 됩니다.

## 9. 도입하지 않는 편이 나은 경우

ARC가 모든 팀에 적합한 것은 아닙니다.

- CI 작업이 적고 GitHub-hosted runner로 요구사항을 충족하는 경우
- Kubernetes control plane을 운영할 역량이나 비용이 없는 경우
- Windows·macOS 전용 빌드가 대부분인 경우
- privileged 빌드가 많지만 격리된 노드·런타임을 준비하지 못한 경우
- 작업 큐·메트릭·보안 이벤트를 모니터링할 인력이 없는 경우
- 조직 정책상 소스 코드가 클러스터 내부로 들어갈 수 없는 경우

이 경우에는 GitHub-hosted runner, VM 기반 ephemeral runner, 또는 별도 CI 플랫폼이 더 단순할 수 있습니다. ARC를 선택하는 기준은 “Kubernetes를 이미 쓴다”가 아니라, **runner 수명주기와 클러스터 제어 루프를 직접 운영할 이유가 있는가**입니다.

## 결론

ARC 0.15.0은 GitHub Actions를 Kubernetes에 올리는 방법을 새로 만든 릴리스라기보다, 규모가 커진 runner fleet에서 제어 루프를 덜 시끄럽고 더 복구 가능하게 만드는 운영 릴리스입니다. in-place 패치·Patch API·이벤트 필터링은 불필요한 작업을 줄이고, graceful shutdown·재등록·빠른 ephemeral 삭제는 장애 후 회복을 돕습니다. 상태 집계를 메트릭으로 옮긴 변화는 대시보드와 SLO를 다시 설계해야 한다는 신호입니다.

도입 순서는 다음처럼 잡는 것이 현실적입니다.

1. GitHub App·runner group·네트워크·노드 격리를 먼저 설계합니다.
2. 작은 비민감 저장소에서 min/max와 queue latency 기준선을 만듭니다.
3. ARC 0.15.0의 메트릭과 API throttling을 관찰하며 동시성을 단계적으로 조정합니다.
4. graceful shutdown·scale set 재등록·작업 cleanup을 장애 주입으로 검증합니다.
5. OIDC 기반 짧은 권한과 전용 노드로 공급망 공격의 blast radius를 줄입니다.
6. 비용 절감보다 작업 대기시간, 실패율, 보안 경계를 함께 보고 확장 여부를 결정합니다.

대규모 CI의 품질은 러너 Pod 숫자가 아니라 **큐에서 실행까지 이어지는 제어 루프를 측정하고, 안전하게 멈추고, 다시 복구할 수 있는가**로 결정됩니다.

## 참고 자료

- [GitHub Changelog, Actions Runner Controller release 0.15.0 (2026-10-01)](https://github.blog/changelog/2026-10-01-actions-runner-controller-release-0-15-0/)
- [Actions Runner Controller 0.15.0 release notes](https://github.com/actions/actions-runner-controller/releases/tag/gha-runner-scale-set-0.15.0)
- [GitHub Docs, Deploying runner scale sets with Actions Runner Controller](https://docs.github.com/en/actions/how-tos/manage-runners/use-actions-runner-controller/deploy-runner-scale-sets)
- [GitHub Docs, Self-hosted runners reference](https://docs.github.com/en/actions/reference/runners/self-hosted-runners)
- [GitLab Docs, Security for self-managed runners](https://docs.gitlab.com/runner/security/)
- [Establishing Workload Identity for Zero Trust CI/CD: From Secrets to SPIFFE-Based Authentication](https://arxiv.org/abs/2504.14760)

> ARC 0.15.0의 experimental Helm chart는 릴리스 노트에서 production workload용으로 지원되지 않는다고 명시합니다. 운영 환경에는 안정 버전 chart와 최신 GitHub 문서를 사용하고, GitHub App 권한·Kubernetes Secret·runner image·네트워크 정책을 별도로 검토하세요.
