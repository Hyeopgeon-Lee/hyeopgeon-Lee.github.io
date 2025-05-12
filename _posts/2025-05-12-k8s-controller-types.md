---
layout: post
title: "ReplicaSet, StatefulSet, DaemonSet 차이점 이해하기"
date: 2025-05-12
---

# ⚙️ ReplicaSet, StatefulSet, DaemonSet 차이점 쉽게 이해하기

쿠버네티스(Kubernetes)는 애플리케이션을 자동으로 관리해주는 똑똑한 시스템이에요.  
그중에서도 Pod를 **어떻게 배치하고 유지할지**를 담당하는 것이 바로 **컨트롤러(controller)**입니다.

이번 글에서는 대표적인 세 가지 컨트롤러인 **ReplicaSet, StatefulSet, DaemonSet**을 비교해보고,  
**각각의 목적, 사용 시나리오, 동작 방식**을 고등학생도 이해할 수 있도록 쉽게 설명해볼게요.

---

## 🤖 컨트롤러란?

먼저 컨트롤러가 무엇인지부터 살펴볼게요.

> 컨트롤러는 "원하는 상태"를 유지하도록 Pod를 자동으로 관리해주는 쿠버네티스의 관리자입니다.

예를 들어, 내가 "항상 3개의 웹서버가 떠 있어야 해!"라고 명령하면,  
컨트롤러는 Pod가 하나 꺼지더라도 다시 자동으로 새로 띄워줘요.

---

## 🧱 ReplicaSet이란?

> ✅ 목적: **같은 Pod 여러 개를 유지**하기 위한 컨트롤러

### ✅ 예시 상황
웹 서버를 3개 띄워서 여러 사람이 동시에 들어와도 빠르게 처리하고 싶을 때

### 🔄 동작 방식
- 내가 원하는 개수의 Pod(예: 3개)를 설정하면, ReplicaSet이 자동으로 그 수를 유지해줘요.
- Pod가 하나 꺼지면? → 새로운 Pod를 자동으로 생성!

```
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: web-replicaset
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
      - name: nginx
        image: nginx
```

---

## 🏷️ StatefulSet이란?

> ✅ 목적: **순서와 이름이 중요한 Pod를 다룰 때 사용하는 컨트롤러**

### ✅ 예시 상황
- 데이터베이스처럼 **각 Pod가 고유한 이름**을 갖고, 순서대로 켜지고 꺼져야 할 때
- 예: Kafka, MySQL, MongoDB 클러스터 구성 시

### 🧠 특징
- Pod 이름이 `myapp-0`, `myapp-1`, `myapp-2`처럼 **고정됨**
- **삭제했다가 다시 만들어도 이름과 데이터 유지됨**
- **순서대로** 생성되고 삭제됨 (0 → 1 → 2 순으로 생성, 반대 순으로 삭제)

```
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: db-stateful
spec:
  serviceName: "db"
  replicas: 3
  selector:
    matchLabels:
      app: db
  template:
    metadata:
      labels:
        app: db
    spec:
      containers:
      - name: mysql
        image: mysql:5.7
```

---

## 🛠️ DaemonSet이란?

> ✅ 목적: **모든 Node(서버)마다 하나씩 Pod를 띄우고 싶을 때 사용하는 컨트롤러**

### ✅ 예시 상황
- 모든 서버에서 **로그 수집기**, **모니터링 에이전트**를 실행하고 싶을 때
- 예: Fluentd, Prometheus Node Exporter

### 🌍 특징
- 클러스터에 Node가 5개 있다면? → Pod도 5개!
- Node가 추가되면? → 자동으로 새로운 Node에도 Pod가 실행됨

```
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: log-agent
spec:
  selector:
    matchLabels:
      app: logger
  template:
    metadata:
      labels:
        app: logger
    spec:
      containers:
      - name: fluentd
        image: fluent/fluentd
```

---

## 🧾 비교 요약표

| 항목         | ReplicaSet              | StatefulSet                          | DaemonSet                         |
|--------------|--------------------------|--------------------------------------|-----------------------------------|
| 목적         | 동일한 Pod를 여러 개 유지 | 고유한 Pod 이름과 순서 관리          | 모든 Node마다 Pod 실행            |
| Pod 이름     | 랜덤                     | 고정 (ex: app-0, app-1)              | 랜덤                              |
| 실행 순서    | 상관없음                 | 순서 보장                            | 모든 Node에서 자동 실행           |
| 저장 데이터  | 저장소 유지 안 함        | 각 Pod가 자신의 저장소 유지          | 주로 로그나 모니터링용            |
| 예시 용도    | 웹 서버, API 서버        | 데이터베이스, 메시지 브로커          | 로그 수집, 보안 검사, 모니터링    |

---

## 🖼️ 그림으로 이해하기

### ReplicaSet 구조
         +---------------------+
         |     ReplicaSet      |
         +---------------------+
              |    |    |
            Pod  Pod  Pod

### StatefulSet 구조
         +----------------------+
         |     StatefulSet      |
         +----------------------+
              |     |     |
          Pod-0  Pod-1  Pod-2   (순서 보장, 이름 고정)

### DaemonSet 구조
+--------+     +--------+     +--------+
| Node 1 |     | Node 2 |     | Node 3 |
|  Pod   |     |  Pod   |     |  Pod   |
+--------+     +--------+     +--------+

---

## 📚 마무리 요약

- ReplicaSet: 똑같은 Pod 여러 개 유지할 때 (예: 웹 서버)
- StatefulSet: 순서와 이름이 중요한 경우 (예: 데이터베이스)
- DaemonSet: 모든 서버마다 Pod를 하나씩 실행하고 싶을 때 (예: 로그 수집기)

> 🎓 이 세 가지 컨트롤러만 잘 이해해도, 쿠버네티스를 훨씬 쉽게 다룰 수 있어요!

---

📎 참고자료:
- https://kubernetes.io/docs/concepts/workloads/controllers/
- 한국폴리텍대학 강의자료