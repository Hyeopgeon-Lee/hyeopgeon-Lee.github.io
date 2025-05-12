---
layout: default
title: "(5장) 쿠버네티스 스케줄링 원리: Pod는 어떻게 배치될까?"
date: 2025-05-10
---

# 🎯 쿠버네티스 스케줄링 원리: Pod는 어떻게 배치될까?

쿠버네티스는 여러 컴퓨터(Node)로 구성된 큰 시스템이에요.  
그럼 이런 질문이 생기겠죠?

> “새로운 애플리케이션(Pod)은 어떤 컴퓨터에 설치되지?”

바로 이걸 결정해주는 게 **스케줄링(Scheduling)** 입니다!

---

## 📦 스케줄링이란?

Pod가 만들어지면, 그것을 **어느 컴퓨터(Node)에 실행시킬지 결정하는 과정**이에요.  
이 역할을 하는 것이 바로 **쿠버네티스 스케줄러(kube-scheduler)**입니다.

스케줄러는 다음 3단계를 거쳐 Pod의 배치를 결정합니다:

```
[1단계] 필터링: 가능한 Node 고르기  
[2단계] 점수 매기기: 어떤 Node가 더 좋은지 판단  
[3단계] 선택하기: 가장 좋은 Node에 배치
```

---

## 🧮 1단계: 필터링 (Filtering)

먼저 “이 Pod를 실행할 수 있는 컴퓨터가 누구야?”라고 물어요.

### ✅ 필터링 조건 예시:
- 컴퓨터가 꺼져 있지 않고(Ready 상태)
- CPU나 메모리가 충분하고
- Pod가 원하는 조건을 만족하는지

---

## 🏅 2단계: 점수 매기기 (Scoring)

“어떤 Node가 가장 적합한가?”를 판단하는 단계입니다.

| 기준 | 설명 |
|------|------|
| 사용량 적은 Node | 여유가 많은 Node 우선 |
| 자원이 고르게 사용된 Node | CPU/메모리 균형 잡힌 Node 선호 |
| 이미지가 이미 있는 Node | 이미지 다운로드 시간 절약 |

> 점수가 가장 높은 Node가 최종 선택됩니다.

---

## 🖐 3단계: 배치 (Binding)

점수가 제일 높은 Node에 Pod가 **실제로 배치(Binding)** 됩니다.

---

## 🚫 Taint & Toleration

특정 Node는 “특수 용도”로만 사용하고 싶을 수 있어요.  
예: GPU 전용, 관리자 전용 서버 등

- **Taint (Node 입장):** “특정 Pod 아니면 나한테 오지 마!”
- **Toleration (Pod 입장):** “저는 괜찮아요, 조건 만족해요!”

> 서로 조건이 맞아야만 배치가 됩니다.

---

## 🧲 Affinity (친화성 설정)

Pod는 **어떤 Node에 배치되길 원하는지**를 설정할 수 있어요.

### 🔹 Node Affinity
Node 라벨 기준으로 “이런 Node에 배치해주세요!”

### 🔹 Pod Affinity
“같은 종류의 다른 Pod 근처에서 실행하고 싶어요.”

### 🔹 Pod Anti-Affinity
“같은 종류의 Pod와는 떨어져서 실행하고 싶어요.”

> 친화성 설정을 통해 Pod 배치를 더 **스마트하게 제어**할 수 있어요.

---

## 🧪 실습 예시

### 🏷️ 1. 특정 Node에 라벨 붙이기
```
kubectl label nodes node1 disktype=ssd
```

### 📦 2. 해당 라벨이 있는 Node에만 배치되는 Pod 만들기
```
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

“같은 종류의 Pod가 한 곳에 몰리면 장애 발생 시 위험해요.”  
⇒ 그래서 **Pod들을 골고루 분산시키는 기능**이 필요합니다.

```
topologySpreadConstraints:
  - maxSkew: 1
    topologyKey: kubernetes.io/hostname
    whenUnsatisfiable: ScheduleAnyway
```

> 이렇게 하면 여러 서버에 Pod가 퍼져서 장애에 더 강해져요! 👍

---

## 🧠 마무리 요약

| 개념              | 설명                                      |
|------------------|-------------------------------------------|
| 스케줄링         | Pod를 Node에 배치하는 과정                |
| 필터링           | 실행 가능한 Node를 골라내기               |
| 점수화           | 어떤 Node가 더 좋은지 판단               |
| Taint & Toleration | 금지/허용 조건으로 노드 제어            |
| Affinity         | 배치 희망 조건 설정                      |
| Spread           | 고르게 분산 배치                         |

---

쿠버네티스는 단순한 배치가 아닌, **똑똑하게** Pod를 배치합니다.  
이해하면 클러스터 운영이 훨씬 안정적이고 효율적으로 바뀔 수 있어요!

📎 **참고자료**  
- https://kubernetes.io/docs/concepts/scheduling-eviction/  
- 한국폴리텍대학 서울강서캠퍼스 빅데이터과 이협건 교수 강의자료