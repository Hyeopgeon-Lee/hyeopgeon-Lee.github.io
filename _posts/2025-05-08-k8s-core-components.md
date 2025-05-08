---
layout: post
title: "쿠버네티스의 핵심 구성 요소: Pod, Deployment, Service 이해하기"
date: 2025-05-08
---

# 🧱 쿠버네티스의 핵심 구성 요소: Pod, Deployment, Service 이해하기

## ✨ 시작하기 전에
쿠버네티스를 처음 배우는 여러분, 환영합니다! 👋

이 글은 **Pod**, **Deployment**, **Service**라는 쿠버네티스의 핵심 개념 3가지를 중심으로
왜 필요한지, 무슨 역할을 하는지, 어떤 식으로 사용되는지를 쉽고 자세히 알려주는 블로그입니다.

> 📚 이 글을 읽으면, 마치 레고 블록처럼 쿠버네티스를 조립하듯 이해할 수 있어요!

---

## 🧩 쿠버네티스란?

- 컨테이너(도커 등)를 **자동으로 관리해주는 시스템**
- 구글에서 만들었고, 지금은 오픈소스로 전 세계에서 사용 중

### 쿠버네티스는 이런 걸 자동으로 해줘요:
| 기능 | 설명 |
|------|------|
| 배포 | 컨테이너를 서버에 자동으로 배치해줌 |
| 확장 | 사용자가 많아지면 자동으로 컨테이너 수 늘림 |
| 복구 | 문제가 생긴 컨테이너는 자동으로 재시작 |
| 연결 | 사용자와 컨테이너, 컨테이너 간 연결을 자동으로 설정 |

---

## 🔹 1. Pod란 무엇일까?

> "Pod는 쿠버네티스에서 **앱이 실제로 실행되는 가장 작은 단위**예요."

### 📦 쉽게 말해:
- 컨테이너를 하나 이상 감싸고 있는 상자
- 보통은 하나의 Pod에 하나의 컨테이너가 들어감

### 🎨 그림으로 이해하기
![image](https://github.com/user-attachments/assets/67c0156f-b427-4c98-a1e3-12681fcf68ea)


### 💡 왜 Pod가 필요할까?
- 컨테이너는 자체적으로는 IP나 저장소 등을 가질 수 없음
- Pod가 이걸 대신 제공해줌 (네트워크, 볼륨, 설정 등)

---

## 🔹 2. Deployment란?

> "Deployment는 여러 Pod를 **자동으로 관리**하는 매니저예요."

### 📦 쉽게 말해:
- Pod가 하나라면, Deployment는 **Pod를 몇 개나 만들지**, **언제 교체할지**, **문제가 생기면 어떻게 복구할지** 등을 정해주는 사람

### 🎨 그림으로 이해하기
![image](https://github.com/user-attachments/assets/332e2d2c-7a42-4f8a-84a1-040c897ba56c)


### ✅ Deployment가 해주는 일
| 기능 | 설명 |
|------|------|
| 자동 생성 | 원하는 수만큼 Pod 생성 |
| 복구 | 죽은 Pod 자동 재생성 |
| 업데이트 | 새로운 이미지로 교체 가능 (롤링 업데이트) |
| 롤백 | 문제가 생기면 이전 상태로 되돌리기 |

---

## 🔹 3. Service란?

> "Service는 외부에서 Pod에게 **접근할 수 있도록 도와주는 문지기**예요."

### 📦 쉽게 말해:
- Pod는 IP가 매번 바뀌는데, Service는 **고정된 주소**를 제공
- 트래픽을 여러 Pod에 골고루 분산해줌 (로드밸런서 역할)

### 🎨 그림으로 이해하기
![image](https://github.com/user-attachments/assets/a2d2ce9f-80bd-43ff-9e42-6dab7c8f7d1a)


### ✅ Service의 종류
| 종류 | 설명 |
|------|------|
| ClusterIP | 내부에서만 접근 가능 (기본값) |
| NodePort | 외부에서 특정 포트로 접근 가능 |
| LoadBalancer | 클라우드에서 외부 IP 부여 |

---

## 🧠 세 가지 구성요소 요약 비교

| 항목 | Pod | Deployment | Service |
|------|-----|------------|---------|
| 역할 | 컨테이너 실행 단위 | Pod 자동 관리 | 접근 & 연결 담당 |
| 구성 수 | 1개 이상 컨테이너 | 여러 Pod | 여러 Pod에 연결 |
| 자동화 | 없음 | 있음 | 있음 |
| 외부 노출 | 안 됨 | 안 됨 | 됨 |

---

## 🛠 예시 실습: 웹 서버 배포 흐름 보기

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-web-deploy
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-web
  template:
    metadata:
      labels:
        app: my-web
    spec:
      containers:
      - name: web
        image: nginx
        ports:
        - containerPort: 80
```

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-web-svc
spec:
  type: NodePort
  selector:
    app: my-web
  ports:
    - port: 80
      targetPort: 80
      nodePort: 30080
```

> 위 두 파일을 적용하면 3개의 웹서버 Pod가 만들어지고, 외부에서 30080 포트로 접근할 수 있어요.

---

## 📚 마무리 요약

- **Pod**: 컨테이너를 담는 최소 단위 (실행 공간)
- **Deployment**: Pod를 자동으로 관리하는 관리자
- **Service**: 외부나 내부에서 Pod에 접근하는 통로

> 이 세 가지가 합쳐져서 쿠버네티스의 기본 구조를 만듭니다!

---


📎 참고자료:
- https://kubernetes.io
- https://labs.play-with-k8s.com/
- 한국폴리텍대학 빅데이터과 이협건 교수 강의자료
