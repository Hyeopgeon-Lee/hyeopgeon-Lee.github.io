---
layout: default
title: "(4장)쿠버네티스 네트워킹의 기초: Pod는 어떻게 통신할까?"
date: 2025-05-09
---

# 🌐 쿠버네티스 네트워킹의 기초: Pod는 어떻게 통신할까?

쿠버네티스를 처음 접한 사람들에게 가장 헷갈리는 부분 중 하나는 바로 **네트워킹**입니다.  
Pod 간 통신은 어떻게 되는지, 외부에서 접근은 어떤 방식으로 처리되는지,  
`ClusterIP`, `DNS`, `CNI 플러그인`이란 단어들은 무엇을 의미하는지, 이 글에서 자세히 알아보겠습니다.

--- 

## 🧩 쿠버네티스 네트워킹의 기본 철학

쿠버네티스는 다음과 같은 네트워킹 철학을 따릅니다:

1. **모든 Pod는 다른 모든 Pod와 직접 통신할 수 있어야 한다.**  
2. **Pod는 고유한 IP를 가진다.**  
3. **통신 시 NAT(Network Address Translation)을 사용하지 않는다.**

즉, 마치 하나의 평평한 네트워크에 모든 Pod가 연결된 것처럼 동작해야 합니다.

> 📌 이는 기존의 가상머신 네트워킹 방식과 큰 차이가 있습니다.

---

## 📦 Pod 간 통신의 구조

각 Pod는 쿠버네티스 내부에서 **고유한 IP 주소**를 부여받습니다.  
하지만 이 IP는 **클러스터 내부 전용**이며, 외부에서는 접근할 수 없습니다.

예시:
- `pod-a`: 10.244.0.12  
- `pod-b`: 10.244.2.7

`pod-a` → `pod-b` 직접 통신 가능 (내부 IP 기반)

---

## 🔗 Service와 ClusterIP란?

Pod는 자주 생성·삭제되므로, IP가 바뀌는 문제를 해결하기 위해 **Service**를 사용합니다.

### 📘 Service란?
- 여러 Pod에 **공통 주소**를 부여하는 쿠버네티스 객체
- Pod IP가 바뀌어도 Service를 통해 계속 접근 가능

### 📘 ClusterIP란?
- **기본 서비스 타입**
- **내부 통신 전용 가상 IP**를 부여

```
kubectl expose deployment myapp --port=80 --target-port=8080 --name=myapp-svc
```

| 항목         | 설명                           |
|--------------|--------------------------------|
| 기본 타입    | ClusterIP (내부 전용)         |
| 외부 접근    | ❌ 불가능                      |
| 내부 통신    | ✅ 가능 (DNS 이름으로 연결)    |
| 자동 로드밸런싱 | ✅ 여러 Pod에 자동 분산       |

---

## 🧠 DNS로 이름 기반 통신하기

쿠버네티스는 **CoreDNS**를 이용해  
`서비스명.네임스페이스.svc.cluster.local` 형태의 주소로 통신합니다.

```
curl http://myapp-svc
```

> DNS는 서비스 이름만으로도 Pod 간 연결을 가능하게 해줍니다.

---

## 🛠 실습 예시: ClusterIP 통신 확인

```
kubectl create deployment web --image=nginx
kubectl expose deployment web --port=80 --target-port=80 --name=web-svc
kubectl run curl-pod --image=busybox --restart=Never -it -- sh
wget -qO- http://web-svc
```

---

## 🌉 CNI 플러그인: 네트워크의 핵심

쿠버네티스 자체는 네트워크를 직접 구현하지 않으며,  
**CNI (Container Network Interface)** 플러그인을 통해 Pod 간 통신을 지원합니다.

| CNI 종류  | 특징                             |
|-----------|----------------------------------|
| Flannel   | 간단한 구조, 학습용에 적합       |
| Calico    | 고성능, 네트워크 정책 지원       |
| Cilium    | BPF 기반, 보안/확장성 우수       |
| Weave     | 설치 간편, 소규모에 적합         |

> 기본 설정 파일은 `/etc/cni/net.d`에 존재합니다.

---

## 📊 클러스터 외부 접근 방법

| 타입         | 설명                                           |
|--------------|------------------------------------------------|
| NodePort     | 노드 IP + 포트 (30000~32767)로 접근 가능      |
| LoadBalancer | 클라우드에서 외부 IP 자동 할당                |
| Ingress      | 도메인/경로 기반 라우팅 + TLS 지원            |

Ingress는 하나의 URL로 여러 서비스를 나누어 제공할 수 있는 기능입니다.

---

## 🧩 핵심 요약 정리

| 구성 요소 | 설명                                      |
|------------|-------------------------------------------|
| Pod IP     | Pod에 자동 부여되는 내부 IP               |
| Service    | 여러 Pod에 하나의 가상 IP 제공            |
| ClusterIP  | 내부에서만 접근 가능한 서비스 IP          |
| DNS        | 서비스 이름 → IP 매핑                     |
| CNI        | 네트워크 구성 처리 (IP 할당 및 라우팅 등)  |
| Ingress    | 외부 접근을 위한 고급 라우팅 설정          |

---

## 📚 마무리

- 쿠버네티스의 네트워킹은 Pod 간 통신을 위한 **자동화된 환경**입니다.  
- 외부 연결을 위해서는 NodePort, LoadBalancer, Ingress 등을 조합합니다.  
- DNS와 CNI를 이해하면 안정적인 서비스 배포가 훨씬 쉬워집니다.

> ☁️ 네트워킹을 잘 이해하면 클러스터 설계와 디버깅 능력이 쑥쑥 자랍니다!

---

📎 참고자료:
- https://kubernetes.io/docs/concepts/services-networking/
- https://www.weave.works/
- https://cilium.io/
- 한국폴리텍대학 서울강서캠퍼스 빅데이터과 이협건 교수 강의자료