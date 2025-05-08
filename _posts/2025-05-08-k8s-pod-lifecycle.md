---
layout: post
title: "(3장)쿠버네티스 Pod의 생명주기와 상태 관리"
date: 2025-05-08
---

# 🔄 쿠버네티스 Pod의 생명주기와 상태 관리

## 🧩 Pod란 무엇인가요?

Pod는 쿠버네티스에서 **컨테이너가 실제로 실행되는 가장 작은 단위**입니다. 보통 하나의 Pod에는 하나의 컨테이너가 들어가 있지만, 경우에 따라 여러 컨테이너가 함께 들어가기도 합니다.

쿠버네티스에서 애플리케이션이 배포되면, 그 중심에는 항상 Pod가 존재합니다. 하지만 Pod는 단순히 실행되고 끝나는 것이 아니라, 다양한 **상태(state)**를 거치며 동작합니다.

---

## 🚦 Pod 생명주기 상태 흐름도

아래는 Pod가 생성되고 종료되기까지 거치는 주요 상태입니다:

![image](https://github.com/user-attachments/assets/360d8bf3-5d42-4e2c-b5a6-2be4775725cf)


이 상태들은 `kubectl get pods` 명령어를 통해 확인할 수 있습니다.

---

## 🔍 각 상태 설명

### 1. **Pending**
- **설명**: Pod가 생성되었지만 아직 모든 컨테이너가 실행되지 않은 상태입니다.
- **원인 예시**:
  - 스케줄러가 아직 노드를 선택하지 못함
  - 필요한 이미지 다운로드 중
  - PVC(영구 볼륨)가 연결되지 않음
  - init container가 아직 종료되지 않음

### 2. **Running**
- **설명**: 모든 컨테이너가 성공적으로 시작되고, Pod가 정상적으로 동작 중인 상태입니다.
- **추가**: 이 상태에서도 `Readiness Probe`가 실패하면 서비스는 연결되지 않을 수 있음
- **내부 상태 세분화**:
  - Initializing: init container 실행 중
  - Ready: 서비스에 트래픽 전달 가능

### 3. **Succeeded**
- **설명**: Pod 내 모든 컨테이너가 성공적으로 종료되었고, 다시 시작될 필요가 없을 때 나타납니다.
- **예시**: 배치 작업(batch job), 단발성 작업이 완료된 경우
- **특징**: Pod는 자동으로 삭제되지 않으며, 사용자가 수동으로 삭제해야 합니다.

### 4. **Failed**
- **설명**: 컨테이너 중 하나 이상이 오류로 인해 비정상 종료되었고, 자동 재시작 없이 Pod가 종료된 상태입니다.
- **원인 예시**:
  - 실행 파일 오류, 잘못된 환경변수, 볼륨 마운트 실패 등
- **차이점**: `restartPolicy: Never`일 때는 실패 후 재시작하지 않음

### 5. **CrashLoopBackOff**
- **설명**: 컨테이너가 시작되었지만, 곧바로 충돌하여 반복적으로 재시작되는 상태입니다.
- **의미**: 쿠버네티스는 계속해서 컨테이너를 다시 실행하려 하지만 실패가 반복됨
- **해결 방법**:
  - `kubectl describe pod [이름]` 으로 상세 로그 확인
  - 잘못된 설정, 의존성 문제, 환경변수 오류 확인

#### 🔥 CrashLoopBackOff가 발생하는 대표적인 원인 예시

| 원인 | 설명 및 예시 |
|------|--------------|
| 애플리케이션 오류 | 컨테이너 내부 실행 파일이 예외를 발생시켜 종료<br>예: Java 애플리케이션에서 NullPointerException 발생 후 즉시 종료 |
| 잘못된 Command/Entrypoint | YAML의 `command` 또는 `args` 설정 오류<br>예: `command: ["exit", "1"]` |
| 환경변수 누락 | `ENV_VAR=DATABASE_URL` 설정이 빠져서 실행 시 DB 연결 실패 |
| 의존 서비스 미작동 | 컨테이너 시작 시 다른 API 서버나 DB에 의존할 경우, 해당 서비스가 준비되지 않아서 실패 반복 |
| Health Check 실패 | `livenessProbe`에서 실패를 반복하여 컨테이너가 강제 재시작됨 |
| 이미지 문제 | `imagePullPolicy: Always`로 설정하고 레지스트리에 없는 태그 사용 시 컨테이너 실행 실패 반복 |

---

## 🧠 상태 관리 시 체크포인트

| 명령어 | 설명 |
|--------|------|
| `kubectl get pods` | Pod 상태 목록 간략 확인 |
| `kubectl describe pod [이름]` | 상태 변화 이력, 이벤트 로그 확인 |
| `kubectl logs [이름]` | 컨테이너 로그 확인 (오류 원인 파악) |
| `kubectl exec -it [이름] -- sh` | Pod 내부에서 직접 디버깅 |

---

## 🛠 실습 예시: CrashLoopBackOff 상태 만들기

다음과 같은 명령어로 일부러 잘못된 Pod를 만들어 상태를 확인할 수 있습니다:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: crash-test
spec:
  containers:
  - name: bad-container
    image: busybox
    command: ['sh', '-c', 'exit 1']
```

```bash
kubectl apply -f crash-test.yaml
kubectl get pods
kubectl describe pod crash-test
```

이 Pod는 `exit 1` 명령으로 항상 실패하기 때문에 CrashLoopBackOff 상태로 진입하게 됩니다.

또 다른 예시:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: missing-env
spec:
  containers:
  - name: app
    image: myapp:latest
    env:
      - name: API_KEY
        valueFrom:
          configMapKeyRef:
            name: missing-config
            key: apiKey
```

위 예시는 존재하지 않는 ConfigMap을 참조해 컨테이너 시작 시 환경 변수 오류가 발생합니다.

---

## 📚 마무리 요약

- Pod는 단순히 실행되는 것이 아니라 여러 상태를 거칩니다.
- **Pending**, **Running**, **Succeeded**, **Failed**, **CrashLoopBackOff** 상태를 이해하면 운영 시 문제를 빠르게 파악할 수 있습니다.
- 상태 변화는 `kubectl` 명령어를 활용해 쉽게 확인 가능하며, 적절한 로그 분석이 중요합니다.

> 쿠버네티스의 Pod 상태를 잘 이해하는 것은 클러스터 운영 능력을 높이는 첫걸음입니다!

---

📎 참고자료:
- https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/
- https://learnk8s.io/pod-lifecycle
- 한국폴리텍대학 서울강서캠퍼스 빅데이터과 이협건 교수 강의자료
