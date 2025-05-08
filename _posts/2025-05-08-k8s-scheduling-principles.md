---
layout: post
title: "(5장)쿠버네티스 스케줄링 원리: Pod는 어떻게 배치될까?"
date: 2025-05-08
---

# 🎯 쿠버네티스 스케줄링 원리: Pod는 어떻게 배치될까?

쿠버네티스는 여러 컴퓨터(Node)로 구성된 큰 시스템이에요.  
그럼 이런 질문이 생기겠죠?

> “새로운 애플리케이션(Pod)은 어떤 컴퓨터에 설치되지?”

바로 이걸 결정해주는 게 **스케줄링(Scheduling)** 입니다!  

---

## 📦 스케줄링이란?

Pod가 만들어지면, 그것을 **어느 컴퓨터(Node)에 실행시킬지 결정하는 과정**이에요.

이 역할을 하는 게 바로 **쿠버네티스 스케줄러**(kube-scheduler)입니다.  
스케줄러는 3단계로 Pod의 배치를 결정해요:

```
[1단계] 필터링: 가능한 Node 고르기
[2단계] 점수 매기기: 어떤 Node가 더 좋은지 판단
[3단계] 선택하기: 가장 좋은 Node에 배치
```

---

## 🧮 1단계: 필터링 (Filtering)

먼저 “이 Pod를 실행할 수 있는 컴퓨터가 누구야?”라고 물어요.

### ✅ 예시 기준
- 컴퓨터가 꺼져 있지 않고(Ready 상태)
- CPU나 메모리가 충분하고
- Pod가 원하는 조건을 갖춘 컴퓨터인지 확인해요.

이렇게 **조건에 맞는 후보 Node만 남기고** 다음 단계로 넘어가요.

---

## 🏅 2단계: 점수 매기기 (Scoring)

“어떤 Node가 제일 좋은지” 점수를 매기는 단계입니다.

| 기준 | 설명 |
|------|------|
| 사용량 적은 Node | 여유가 많은 Node 우선 |
| 자원이 고르게 사용된 Node | CPU/메모리 균형 잡힌 Node 선호 |
| 이미지 이미 있는 Node | 다운로드 시간 절약됨 |

> 점수 제일 높은 Node가 다음 단계로 선택돼요.

---

## 🖐 3단계: 배치 (Binding)

점수가 제일 높은 Node가 최종 선택돼서, Pod가 해당 Node에 실행됩니다.

---

## 🚫 Taint & Toleration

어떤 Node는 “특별한 용도”로만 쓰고 싶을 때가 있어요.  
예를 들어 GPU 전용 서버나 관리자 전용 서버 같은 거죠.

### 🔸 Taint (노드가 말함)
> “이런 Pod 아니면 나한테 오지 마세요!”

### 🔹 Toleration (Pod가 답함)
> “저는 괜찮아요~ 그 조건 만족해요!”

이렇게 서로 조건이 맞아야 배치됩니다.

---

## 🧲 Affinity (같이 있고 싶은 친구)

Pod가 “나는 이 Node에서 실행되고 싶어요” 혹은  
“이런 다른 Pod 근처에서 실행되고 싶어요” 라고 요청할 수 있어요.

### 🎯 Node Affinity
Node의 라벨을 기준으로 “이런 Node에 배치해줘”

### 🎯 Pod Affinity
“같은 종류의 Pod 근처에서 실행해줘”

### 🎯 Pod Anti-Affinity
“같은 종류의 Pod랑은 떨어져서 실행해줘”

> 이런 설정을 하면 Pod의 배치를 더 **똑똑하게 조절**할 수 있어요!

---

## 🧪 실습 예시

1. 특정 Node에 라벨 붙이기:
```bash
kubectl label nodes node1 disktype=ssd
```

2. 해당 라벨이 있는 Node에만 배치되는 Pod 만들기:
```yaml
spec:
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
        - matchExpressions:
          - key: disktype
            operator: In
            values:
            - ssd
```

---

## 📐 Topology Spread (분산 배치)

“같은 종류의 Pod가 한 곳에 몰리면 위험해요.”  
⇒ 그래서 **Pod들을 골고루 퍼뜨리는 기능**이 필요합니다.

```yaml
topologySpreadConstraints:
- maxSkew: 1
  topologyKey: kubernetes.io/hostname
  whenUnsatisfiable: ScheduleAnyway
```

> 이렇게 하면 장애가 나도 다른 서버에서 서비스가 살아 있어요! 👍

---

## 🧠 마무리 요약

| 개념 | 설명 |
|------|------|
| 스케줄링 | Pod를 Node에 배치하는 과정 |
| 필터링 | 가능한 Node만 고르기 |
| 점수화 | 어떤 Node가 더 좋은지 판단 |
| Taint & Toleration | 금지/허용 조건 설정 |
| Affinity | 같이 있고 싶은 조건 설정 |
| Spread | 골고루 분산되도록 배치 |

---

쿠버네티스는 단순한 배치가 아니라, **똑똑하게** Pod를 배치합니다.  
이해하면 클러스터 운영이 훨씬 안정적이고 효율적으로 바뀔 수 있어요!

📎 참고자료:
- https://kubernetes.io/docs/concepts/scheduling-eviction/
- 한국폴리텍대학 서울강서캠퍼스 빅데이터과 이협건 교수 강의자료
