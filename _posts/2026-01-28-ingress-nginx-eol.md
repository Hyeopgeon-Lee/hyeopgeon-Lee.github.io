---
layout: single
title: "Ingress-NGINX EOL(지원 종료) 발표: 무엇이 바뀌고, Gateway API로 어떻게 전환할까?"
date: 2026-01-28
author_profile: false
read_time: true
toc: true
toc_sticky: true
classes: wide
---

# 🛑 Ingress-NGINX 지원 종료(EOL): 무엇이 바뀌나?

쿠버네티스 네트워크 진입점의 사실상 표준이던 **Ingress-NGINX가 2026년 3월 EOL(End-Of-Life)**을 맞이합니다.  
이는 단순한 프로젝트 종료가 아니라, **클라우드 네이티브 네트워크 트래픽 관리의 패러다임 전환**을 의미합니다.

이 글에서는 **지원 종료의 의미**, **왜 이런 결정이 내려졌는지**, 그리고 **Gateway API 기반 전환 전략**과 **대안 Ingress 컨트롤러 비교**까지 자세히 정리합니다.

---

## 📌 1. 공식 발표 요약: 무엇이 바뀌나?

Kubernetes SIG Network와 Security Response Committee는 2025년 11월 공식 블로그를 통해 다음 계획을 발표했습니다.

- **Ingress-NGINX 유지보수 및 정기 릴리스는 2026년 3월까지 진행**
- 2026년 3월 이후:
    - 신규 릴리스 없음
    - 버그 수정 없음
    - 보안 패치 및 CVE 대응 없음
    - 저장소는 읽기 전용(read-only) 상태 전환

즉, **2026년 3월 이후에는 동작은 하지만 보안/운영 리스크가 빠르게 누적되는 상태**가 됩니다.  
장기간 운영 환경에서는 **치명적인 보안 공백**이 생길 수 있습니다.

---

## 🧠 2. 왜 지원이 종료되는가?

Ingress-NGINX는 쿠버네티스 초기부터 대표 Ingress 컨트롤러로 자리잡았습니다. 하지만 시간이 지나며 다음과 같은 구조적 문제가 누적되었습니다.

### 📍 유지보수 인력 부족
- 핵심 기여자는 오랜 기간 1~2명 수준
- 대부분 **본업 외 시간으로 유지보수**를 수행
- 결과적으로 지속 가능성이 크게 저하

### 📍 기술 부채와 보안 리스크
- 유연한 애노테이션 기반 설정이 오히려 위험 요소가 됨
- **임의 NGINX 설정 주입**은 보안 관점에서 위험
- 유지보수 비용과 공격 표면이 동시에 증가

### 📍 InGate 프로젝트 실패
- Gateway API 기반 대체 컨트롤러(InGate) 시도
- 커뮤니티 참여 부족으로 **성숙 단계 도달 실패**

---

## 🌐 3. Ingress-NGINX가 남긴 유산

Ingress-NGINX는 다음과 같은 역할을 수행해 왔습니다:

- **모든 쿠버네티스 클러스터의 기본 HTTP/HTTPS 진입점** 역할
- 퍼블릭 클라우드, 온프레미스, 홈랩까지 광범위 채택
- 높은 유연성, 풍부한 기능 제공

즉, **Ingress-NGINX의 역사는 쿠버네티스 네트워킹 발전사와 궤를 같이**합니다.

---

## 📈 4. EOL 이후 달라지는 점 한눈에 보기

| 항목 | 2026년 3월 이전 | 2026년 3월 이후 |
|------|----------------|----------------|
| 신규 릴리스 | ✅ | ❌ |
| 버그 수정 | ✅ | ❌ |
| 보안 패치(CVE) | ✅ | ❌ |
| 기능 개선 | 제한적 | ❌ |
| 저장소 상태 | Active | Read-only |

👉 **운영은 가능하지만, 보안 패치가 불가능한 ‘고스트 소프트웨어’가 됩니다.**

---

## ✅ 5. 지금 해야 할 일: 체크리스트

### 1) 사용 여부 확인
```bash
kubectl get pods --all-namespaces --selector app.kubernetes.io/name=ingress-nginx
```
해당 파드가 있다면 **Ingress-NGINX가 실제 운영 중**입니다.

### 2) 마이그레이션 우선순위 설정
- 운영 영향도가 큰 서비스부터 이관 계획 수립
- 멀티클러스터/멀티테넌트 환경일수록 조기 전환 필요

---

# 🚀 6. Gateway API vs Ingress: 무엇이 다른가?

Ingress API는 아직 deprecated는 아니지만, **feature-frozen 상태**입니다.  
반면 Gateway API는 **차세대 표준**으로 설계되어 **확장성/안정성/표준화**를 강화했습니다.

## ✅ 비교 표: Ingress vs Gateway API

| 항목 | Ingress API | Gateway API |
|------|------------|-------------|
| 상태 | 안정적이지만 기능 동결 | 차세대 표준 (활발히 발전 중) |
| 리소스 모델 | 단일 Ingress 객체 | Gateway / HTTPRoute / TCPRoute 분리 |
| 멀티테넌시 | 제한적 | **강력한 멀티테넌시 설계** |
| 확장성 | 애노테이션 의존 | 표준 필드 기반 확장 |
| 권한 분리 | 약함 | **권한 분리 모델 내장** |
| L4/L7 지원 | L7 중심 | L4/L7 통합 지원 |

### 🔍 구조적 차이 예시

Ingress는 **단일 객체에 모든 설정이 몰리는 구조**입니다:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-ingress
spec:
  rules:
    - host: example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: app
                port:
                  number: 80
```

Gateway API는 **역할 분리와 멀티테넌시를 염두에 둔 구조**입니다:

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: shared-gateway
spec:
  gatewayClassName: nginx
  listeners:
    - name: http
      protocol: HTTP
      port: 80
```

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: app-route
spec:
  parentRefs:
    - name: shared-gateway
  rules:
    - matches:
        - path:
            type: PathPrefix
            value: /
      backendRefs:
        - name: app
          port: 80
```

> **Gateway는 인프라팀, HTTPRoute는 서비스팀이 관리**하는 식으로 권한과 책임을 분리할 수 있습니다.

---

# 🧭 7. 대체 Ingress Controller 후보 비교

Gateway API로의 전환이 최선이지만, **조직 상황상 즉시 전환이 어렵다면 다른 Ingress 컨트롤러를 고려**해야 합니다.

| 컨트롤러 | 특징 | 장점 | 주의사항 |
|----------|------|------|----------|
| **Traefik** | 동적 라우팅 강점 | 사용 편의성, 커뮤니티 활발 | 고급 정책 기능 제한 가능 |
| **HAProxy Ingress** | 성능 강점 | 고성능/안정성 | 설정 복잡도 높음 |
| **Envoy 기반 Ingress** | 현대적 아키텍처 | 확장성, 서비스메시 연계 | 러닝커브 존재 |
| **클라우드 제공 Ingress** | 관리형 서비스 | 운영 부담 감소 | 특정 클라우드 종속성 |

---

# 🧩 8. 권장 마이그레이션 전략

### ✅ 단계 1: 현황 파악
- Ingress-NGINX 사용 여부 확인
- 인그레스 리소스와 애노테이션 목록 파악

### ✅ 단계 2: 위험도 평가
- 외부 노출 서비스 우선순위 파악
- TLS/인증/리디렉션 등 핵심 기능 체크

### ✅ 단계 3: Gateway API PoC
- 테스트 클러스터에서 Gateway API 컨트롤러 도입
- 기존 인그레스 룰을 HTTPRoute로 변환

### ✅ 단계 4: 점진적 전환
- 신규 서비스는 Gateway API 적용
- 기존 서비스는 단계적으로 전환

---

# ✅ 9. 결론: 지금이 전환의 타이밍

Ingress-NGINX EOL은 단순한 종료가 아니라, **쿠버네티스 네트워크 스택이 보다 안전하고 표준화된 모델로 이동한다는 신호**입니다.

- **단기적으로는 대체 컨트롤러 도입**
- **장기적으로는 Gateway API 전환**

운영 중인 클러스터를 안정적으로 유지하려면 **지금부터 로드맵을 마련하는 것이 가장 안전한 선택**입니다.

---

📎 참고자료:
- https://kubernetes.io/docs/concepts/services-networking/gateway/
- https://gateway-api.sigs.k8s.io/
- https://kubernetes.github.io/ingress-nginx/

