---
layout: default
title: "GKE MicroVM Sandbox GA: AI 에이전트 실행의 격리 경계를 다시 설계하다"
date: 2026-10-12 06:00:00 +0900
excerpt: "Google Cloud가 GKE Sandbox의 microVM 타입을 GA로 전환했다. Kata Containers와 Cloud Hypervisor로 Pod마다 별도 커널을 제공하는 이 기능의 보안 효과, 비용·성능 조건, 네트워크와 스토리지 한계를 실무와 교육 관점에서 분석한다."
tags: [Google Cloud, GKE, Kubernetes, 클라우드보안, AI 에이전트]
ai_assisted: true
---

## 컨테이너보다 강한 격리가 필요한 순간

AI 에이전트가 코드를 실행하고, 브라우저를 조작하고, 외부에서 받은 파일을 변환하는 일이 늘고 있습니다. 이때 “컨테이너로 감쌌으니 안전하다”는 설명만으로는 부족합니다. 일반 컨테이너는 호스트 커널을 공유하므로, 커널 취약점이나 잘못된 권한 설정이 여러 테넌트의 경계를 동시에 무너뜨릴 수 있습니다.

Google Cloud는 2026년 10월 7일 GKE Sandbox의 microVM 샌드박스 타입을 GA로 전환했습니다. GKE 1.37.0-gke.4713000 이상에서 사용할 수 있으며, Kata Containers와 Cloud Hypervisor가 Pod마다 별도의 경량 가상 머신과 Linux 커널을 제공합니다. 공식 문서는 이를 신뢰할 수 없는 워크로드, AI 에이전트 런타임, 멀티테넌트 환경을 위한 하드웨어 가상화 기반 격리로 설명합니다.

이번 변화의 핵심은 “모든 Pod를 더 안전하게 만든다”가 아닙니다.

> 어떤 작업을 일반 컨테이너로 실행하고, 어떤 작업만 microVM 경계 안에 넣을지 선택할 수 있는 런타임 계층이 정식 운영 범위에 들어왔다는 뜻입니다.

이 글은 GKE 릴리스 노트와 Sandbox 공식 문서, Kata Containers의 설계·제한 문서, USENIX 연구와 최근 공유 스토리지 사이드채널 연구를 교차 확인해 작성했습니다. GKE 버전, 머신 시리즈, 지원 기능은 바뀔 수 있으므로 실제 배포 전 최신 문서를 다시 확인해야 합니다.

## 1. microVM은 gVisor와 무엇이 다른가

GKE Sandbox에는 gVisor와 microVM이라는 두 격리 방식이 있습니다. 둘 다 일반 Pod보다 강한 경계를 제공하지만, 내부 구조와 호환성의 대가가 다릅니다.

| 실행 방식 | 커널 경계 | 강점 | 주의할 점 |
| --- | --- | --- | --- |
| 일반 컨테이너(runc) | 호스트 커널 공유 | 가장 높은 호환성·밀도 | 커널 취약점과 권한 설정의 영향 범위가 큼 |
| gVisor | 사용자 공간 커널 인터페이스 | 기존 컨테이너와 비교적 낮은 운영 부담 | 일부 시스템 호출·GPU·성능 기능의 제한 |
| GKE microVM | Pod마다 게스트 Linux 커널과 VMM | 하드웨어 가상화에 가까운 강한 격리 | nested virtualization, 시작·메모리 오버헤드, GPU·TPU 미지원 |

GKE 문서에 따르면 microVM은 Kata Containers가 Pod의 VM 수명주기를 관리하고 Cloud Hypervisor가 VMM 역할을 수행합니다. 각각의 Pod가 별도 Linux 커널을 사용하므로, 한 Pod의 커널 모듈이나 시스템 호출이 호스트와 다른 Pod에 직접 공유되는 경로를 줄입니다.

그러나 microVM이 “작은 가상 머신이니 완전한 VM과 동일하다”는 뜻은 아닙니다. Kubernetes의 네트워크·스토리지·노드·컨트롤 플레인과 연결된 운영 경계는 그대로 남습니다. 격리 강도가 높아져도 권한, 네트워크, 이미지, 비밀 관리가 자동으로 안전해지는 것은 아닙니다.

## 2. 10월 7일 GA가 바꾸는 것

이번 GA는 새로운 샌드박스 실험을 시작한다는 의미보다, 일정한 조건을 갖춘 팀이 운영 SLO와 보안 정책에 microVM을 포함할 수 있다는 의미가 큽니다.

### 첫째, 에이전트 실행을 전용 런타임으로 분리할 수 있다

코드 인터프리터, 브라우저 자동화, 문서 변환, 플러그인 실행처럼 입력을 완전히 신뢰하기 어려운 작업을 별도 RuntimeClass로 라우팅할 수 있습니다. 데이터 처리 API와 장기 실행 웹 서비스는 일반 컨테이너에 두고, 에이전트가 생성한 임시 프로세스만 microVM node pool에 배치하는 식입니다.

### 둘째, 격리 수준과 호환성을 정책으로 선택할 수 있다

모든 워크로드를 microVM에 넣으면 비용과 시작 시간이 늘어날 수 있습니다. 반대로 모든 작업을 일반 컨테이너에 넣으면 외부 코드 실행의 blast radius가 커집니다. 런타임을 Pod 단위로 선택하면 팀·데이터 등급·실행 유형에 따라 다른 보안 프로파일을 만들 수 있습니다.

### 셋째, Kubernetes 보안 교육의 추상화 수준이 올라간다

학생이나 개발자는 namespace와 PodSecurity만으로 격리가 끝난다고 오해하기 쉽습니다. microVM을 사용하면 커널 공유, 게스트 커널, VMM, 네트워크 정책, IAM이라는 서로 다른 경계를 한 번에 비교할 수 있습니다. 보안 기능을 켜는 것보다 어떤 경계가 실제로 바뀌는지 설명하는 데 교육적 가치가 있습니다.

## 3. 활성화 조건은 생각보다 구체적이다

GKE 공식 릴리스 노트와 Sandbox 문서에서 확인되는 핵심 조건은 다음과 같습니다.

- GKE 버전 1.37.0-gke.4713000 이상
- Linux 노드만 지원
- Container-Optimized OS 또는 Ubuntu 노드 이미지
- 노드에서 nested virtualization 활성화
- Standard 클러스터는 GKE 시스템 워크로드용 비샌드박스 node pool을 최소 하나 유지
- Google Cloud Console에서는 microVM 타입 선택을 지원하지 않으며 gcloud CLI 또는 GKE API 사용
- microVM은 GPU와 TPU를 지원하지 않음

예를 들어 전용 node pool은 다음과 같은 형태로 생성합니다.

~~~bash
gcloud container node-pools create MICROVM_POOL \
  --cluster=CLUSTER_NAME \
  --location=CONTROL_PLANE_LOCATION \
  --sandbox=type=microvm \
  --enable-nested-virtualization \
  --machine-type=MACHINE_TYPE
~~~

Pod에서는 RuntimeClass를 지정해 해당 node pool로 보냅니다.

~~~yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: untrusted-agent
spec:
  replicas: 2
  selector:
    matchLabels:
      app: untrusted-agent
  template:
    metadata:
      labels:
        app: untrusted-agent
    spec:
      runtimeClassName: microvm
      containers:
        - name: agent
          image: example.com/agent-runner:2026.10
          resources:
            requests:
              cpu: "1"
              memory: "1Gi"
~~~

이 설정은 격리 런타임을 선택할 뿐입니다. 실제로 microVM node pool에 스케줄되도록 taint·toleration·node selector·ComputeClass 정책을 함께 설계해야 하며, 네트워크와 서비스 계정 권한도 별도로 제한해야 합니다.

## 4. 왜 nested virtualization이 운영 변수인가

microVM은 노드 안에서 다시 가상 머신을 실행하므로 일반 컨테이너보다 하드웨어 가상화 경로에 더 의존합니다. 노드 머신 시리즈가 nested virtualization을 지원하는지, 리전에서 필요한 용량을 확보할 수 있는지, 클러스터 오토스케일러가 해당 node pool을 올바르게 확장하는지 확인해야 합니다.

운영팀이 확인할 항목은 다음과 같습니다.

| 영역 | 확인 질문 |
| --- | --- |
| 용량 | 선택한 머신 타입과 리전에서 nested virtualization 용량이 충분한가? |
| 부팅 | Pod 생성부터 게스트 커널 준비까지 p50·p95는 얼마인가? |
| 오토스케일링 | 새 노드 부팅과 microVM 시작 지연이 작업 SLO 안에 들어오는가? |
| 이미지 | 게스트에서 이미지 pull과 레이어 캐시가 어떻게 동작하는가? |
| 비용 | 같은 작업을 일반 컨테이너로 실행할 때보다 CPU·메모리 비용이 얼마나 늘어나는가? |
| 장애 | nested virtualization이 비활성화되거나 노드가 부족할 때 어떤 fallback이 있는가? |

특히 scale-to-zero를 사용하는 에이전트 플랫폼에서는 “Pod가 0개일 때 비용이 없다”는 계산이 정확하지 않을 수 있습니다. 첫 요청 때 노드 프로비저닝, 게스트 부팅, 이미지 다운로드가 연달아 발생하기 때문입니다. 반대로 min node를 유지하면 지연은 줄지만 유휴 비용과 패치 대상이 늘어납니다.

## 5. 강한 격리에는 메모리와 시작 시간의 대가가 있다

Kata Containers의 설계 문서는 VMM, shim, 가상 CPU, I/O 백엔드가 Pod마다 추가 CPU·메모리를 사용한다고 설명합니다. Pod 리소스 요청만 맞추면 되는 것이 아니라 sandbox overhead를 노드 용량과 cgroup에 반영해야 합니다.

USENIX ATC 2022의 Kata 연구는 100개 이상의 컨테이너를 동시에 시작할 때 rootfs와 cgroup 준비가 병목이 될 수 있고, 128MB 사양의 microVM 1,000개를 한 노드에 배치하면 게스트 커널과 rootfs 메모리만으로도 밀도가 크게 떨어질 수 있다고 보고했습니다. 이 수치는 GKE의 모든 머신 타입을 직접 측정한 결과는 아니지만, “microVM을 많이 만들수록 일반 Pod와 같은 밀도를 기대할 수 없다”는 구조적 경고로 읽어야 합니다.

따라서 도입 전 다음 지표를 별도로 측정해야 합니다.

- 일반 컨테이너 대비 microVM Pod의 시작 시간
- 게스트 커널과 VMM이 사용하는 memory overhead
- 동시 Pod 생성 시 Kubernetes API와 노드 CPU 부하
- 이미지 pull·filesystem mount·네트워크 연결에 걸리는 시간
- 같은 작업을 반복했을 때 캐시 적중률과 비용
- 노드 drain·업그레이드 중 실행 중인 에이전트의 재시작 횟수

보안팀이 “microVM을 사용하라”고 결정해도, 플랫폼팀은 그 요구를 작업 큐 지연과 비용으로 번역해야 합니다. 측정 없이 모든 에이전트를 microVM으로 전환하면 보안 개선보다 서비스 품질 저하가 먼저 나타날 수 있습니다.

## 6. 격리 경계가 강해져도 데이터 경계는 남는다

GKE 문서는 microVM에서 클러스터 메타데이터에 접근하지 못하도록 NetworkPolicy로 메타데이터 IP를 차단할 것을 안내합니다. 사용 중인 Dataplane V2와 설정에 따라 차단 대상 주소와 포트가 달라질 수 있으므로, 문서의 최신 값을 확인해 적용해야 합니다.

또한 다음 경계는 microVM이 대신 처리하지 않습니다.

- Pod가 접근할 수 있는 내부 API와 데이터베이스
- Kubernetes Secret과 서비스 계정 권한
- 컨테이너 이미지와 패키지 저장소의 신뢰성
- 공유 PVC·emptyDir·호스트 파일시스템의 데이터 잔존
- 로그·트레이스·에이전트 대화에 포함된 개인정보
- node pool 사이의 네트워크 정책과 방화벽

최근 공개된 공유 스토리지 사이드채널 연구는 Docker, gVisor, Kata, Cloud Hypervisor 기반 환경에서도 host-backed filesystem과 페이지 캐시가 공유되면 타이밍 신호가 남을 수 있다고 분석했습니다. 이는 GKE microVM에 즉시 취약점이 있다는 뜻이 아니라, VM 경계만으로 공유 하드웨어와 스토리지의 모든 정보 흐름이 사라지지는 않는다는 뜻입니다.

고위험 테넌트 사이에 같은 노드와 공유 스토리지를 사용한다면, 별도 node pool·전용 디스크·직접 I/O·강한 네트워크 분리·작업 종료 후 삭제를 함께 검토해야 합니다. microVM을 켠 뒤에도 데이터 분류와 저장 위치를 다시 설계해야 하는 이유입니다.

## 7. AI 에이전트에 적합한 작업과 부적합한 작업

microVM의 비용을 정당화하기 쉬운 작업은 실행 내용을 사전에 완전히 신뢰하기 어려운 단기 작업입니다.

### 적합한 예

- 사용자가 업로드한 문서·압축파일·코드의 변환
- 브라우저 에이전트가 방문한 외부 페이지의 스크립트 실행
- AI가 생성한 코드를 테스트하는 임시 환경
- 여러 고객이 같은 에이전트 플랫폼을 공유하는 멀티테넌트 작업
- 플러그인과 도구를 동적으로 설치하는 실험 환경

### 일반 컨테이너가 더 나은 예

- 내부에서 관리하는 고정된 API 서버
- GPU·TPU를 사용하는 추론 및 학습
- 낮은 지연시간이 최우선인 장기 실행 서비스
- 호스트 장치·특수 커널 기능·높은 I/O 성능이 필요한 작업
- 신뢰된 단일 팀의 단순 배치 작업

GKE 문서도 신뢰할 수 있는 first-party workload를 Sandbox에 넣는 일반적인 이점은 크지 않다고 설명합니다. 격리 강도를 높이는 것이 목적이 아니라, **실행 코드의 신뢰 경계가 실제로 불분명한가**를 기준으로 RuntimeClass를 선택해야 합니다.

## 8. 운영 정책으로 연결하는 방법

microVM을 단순한 Pod 옵션으로 배포하면 팀마다 서로 다른 보안·성능 설정이 생깁니다. 다음과 같이 정책으로 묶는 편이 좋습니다.

1. 데이터 등급과 실행 유형을 기준으로 일반 컨테이너·gVisor·microVM 프로파일을 정의합니다.
2. admission policy로 외부 코드 실행 workload가 지정된 RuntimeClass를 사용하도록 합니다.
3. microVM node pool에는 전용 service account와 제한된 egress 정책을 적용합니다.
4. 이미지 서명과 SBOM 검증을 통과하지 못한 agent image를 거부합니다.
5. Workload Identity Federation을 사용해 정적 클라우드 키를 Pod에 넣지 않습니다.
6. 메타데이터 endpoint, 내부 관리 API, Kubernetes API에 대한 egress를 명시적으로 차단합니다.
7. 실행 종료 후 workspace, 토큰, 임시 디스크, 캐시의 보존 정책을 확인합니다.
8. 시작 지연·비용·재시작률·보안 이벤트를 일반 컨테이너와 분리해 대시보드에 기록합니다.

이 정책이 있어야 개발자가 “에이전트니까 microVM”이라고만 선언하지 않고, 왜 그 런타임과 격리 수준이 필요한지 설명할 수 있습니다.

## 9. 교육에서 해 볼 수 있는 비교 실습

실제 고객 데이터를 사용하지 않고도 microVM의 장단점을 확인할 수 있습니다.

1. GKE 테스트 클러스터에 일반 node pool과 microVM node pool을 만듭니다.
2. 같은 이미지와 같은 CPU·메모리 요청으로 두 RuntimeClass에 Deployment를 배포합니다.
3. Pod 시작 시간, 파일 I/O, 네트워크 왕복, 삭제 후 재생성 시간을 기록합니다.
4. 1개·10개·100개의 Pod를 동시에 생성해 노드 CPU와 API 응답을 비교합니다.
5. 외부 입력을 처리하는 샘플 에이전트를 실행하고 NetworkPolicy로 메타데이터 접근을 차단합니다.
6. microVM에서 지원되지 않는 GPU 요청과 호스트 장치 접근을 시도해 실패 조건을 확인합니다.
7. node pool 업그레이드와 drain 중 작업 재시작·데이터 잔존 여부를 검증합니다.

학생에게는 “microVM이 더 안전하다”를 암기시키기보다 다음 질문을 던지는 편이 좋습니다.

- 컨테이너와 microVM 사이에서 실제로 공유되는 것은 무엇인가?
- 강한 격리의 비용을 어떤 SLO와 예산으로 지불하는가?
- 왜 GPU 작업은 같은 런타임을 사용할 수 없는가?
- NetworkPolicy와 IAM이 빠지면 microVM이 해결하지 못하는 공격 경로는 무엇인가?
- 시작 지연이 늘어날 때 사용자는 어떤 fallback을 경험하는가?

## 10. 도입 전 한계 체크리스트

GKE microVM Sandbox GA는 강력한 기본 기능이지만 모든 환경의 기본값은 아닙니다.

- GKE 1.37 계열과 지원 머신 타입으로 업그레이드해야 함
- nested virtualization이 필요한 node pool을 별도로 운영해야 함
- Standard 클러스터에는 비샌드박스 시스템 node pool이 계속 필요함
- microVM은 GPU·TPU를 지원하지 않음
- Linux와 COS·Ubuntu 노드만 지원함
- 콘솔이 아닌 gcloud 또는 GKE API로 타입을 선택해야 함
- Kata의 privileged·장치·filesystem 동작은 runc와 다를 수 있음
- sandbox overhead 때문에 Pod 밀도와 시작 시간이 악화될 수 있음
- VM 경계가 네트워크·스토리지·IAM·공유 하드웨어의 모든 위험을 제거하지 않음
- 신뢰된 first-party workload에는 비용 대비 이점이 작을 수 있음

이 체크리스트를 통과하지 못하면 gVisor, 전용 VM, 별도 클러스터, 또는 완전히 격리된 실행 서비스가 더 적합할 수 있습니다.

## 결론

GKE Sandbox microVM 타입의 GA는 Kubernetes 보안을 한 단계 더 강하게 만드는 만능 스위치가 아니라, **실행 코드의 신뢰 수준에 따라 커널 경계를 선택할 수 있게 한 운영 옵션**입니다. Kata Containers와 Cloud Hypervisor를 통해 Pod마다 별도 Linux 커널을 제공하므로 AI 에이전트, 브라우저 자동화, 외부 파일 처리처럼 입력을 신뢰하기 어려운 작업의 blast radius를 줄이는 데 유용합니다.

동시에 nested virtualization, 노드 용량, 게스트 부팅, GPU·TPU 미지원, filesystem과 공유 하드웨어의 잔여 위험을 받아들여야 합니다. 가장 현실적인 도입 순서는 다음과 같습니다.

1. 에이전트·플러그인·외부 파일 처리처럼 불신 경계가 분명한 workload를 분류합니다.
2. 일반 컨테이너와 microVM의 시작 시간·비용·오류율을 같은 샘플로 측정합니다.
3. 전용 node pool, RuntimeClass, NetworkPolicy, Workload Identity를 함께 설계합니다.
4. 공유 디스크와 메타데이터 endpoint에서 데이터가 새지 않는지 검증합니다.
5. SLO와 예산을 만족하는 작업만 microVM으로 승격합니다.
6. GKE·Kata·Cloud Hypervisor의 버전 변경 때 회귀 테스트를 반복합니다.

보안 런타임의 성숙도는 “VM을 썼다”가 아니라 **어떤 코드가 어떤 커널·네트워크·스토리지 경계를 넘고, 그 격리의 비용과 실패 모드를 측정했는가**로 판단해야 합니다.

## 참고 자료

- [Google Cloud GKE release notes, microVM sandbox GA (2026-10-07)](https://docs.cloud.google.com/kubernetes-engine/docs/release-notes-new-features)
- [Google Cloud Docs, GKE Sandbox](https://docs.cloud.google.com/kubernetes-engine/docs/concepts/sandbox-pods)
- [Google Cloud Docs, Isolate workloads by using GKE Sandbox](https://docs.cloud.google.com/kubernetes-engine/docs/how-to/sandbox-pods)
- [Kata Containers, Limitations](https://github.com/kata-containers/kata-containers/blob/main/docs/Limitations.md)
- [Kata Containers, virtualization design](https://kata-containers.github.io/kata-containers/design/virtualization/)
- [Li et al., RüN: Secure and Fast Container Runtime with Hardware-Assisted Isolation, USENIX ATC 2022](https://www.usenix.org/system/files/atc22-li-zijun-rund.pdf)
- [Isolation Failure From Shared Storage: Characterizing and Exploiting Page-Cache SCA Leakage Across Containers and VMs](https://arxiv.org/abs/2607.17518)

> microVM 샌드박스는 GA이지만 지원되는 GKE 버전·머신 타입·GPU·TPU·스토리지 기능이 제한됩니다. 운영 전에는 최신 GKE Sandbox 문서와 조직의 보안·개인정보·비용 정책을 함께 검토하세요.
