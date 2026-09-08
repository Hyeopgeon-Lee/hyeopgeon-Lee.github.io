---
layout: default
title: "npm 패키지 배포에서 장기 토큰을 없애라: 다중 OIDC 신뢰 배포와 스테이징 승인"
date: 2026-09-09 06:00:00 +0900
excerpt: "npm이 패키지당 여러 OIDC 신뢰 배포 구성을 지원한다. 장기 배포 토큰 없이 안정·프리릴리스·스테이징 워크플로를 분리하고 공급망 위험을 낮추는 방법을 살펴본다."
---

# npm 패키지 배포에서 장기 토큰을 없애라
## 다중 OIDC 신뢰 배포와 스테이징 승인

GitHub와 npm은 2026년 9월 3일 **하나의 npm 패키지에 여러 Trusted Publishing 구성을 연결하는 기능**을 정식 제공했습니다. 이제 안정 버전, 프리릴리스, 스테이징 배포가 서로 다른 저장소나 워크플로에서 실행되더라도 장기간 유지되는 npm 쓰기 토큰을 남겨 둘 이유가 크게 줄었습니다.

같은 날 스테이징된 패키지는 악성코드 검사가 끝나기 전에는 승인할 수 없도록 바뀌었고, 관리자는 패키지 버전 화면에서 승인·거부·대기 이력을 확인할 수 있게 됐습니다.

이 변화는 단순한 CI 편의 기능이 아닙니다. 오픈소스 공급망의 중요한 질문을 **“누가 비밀 토큰을 가지고 있는가?”에서 “어떤 워크로드가 어떤 조건에서 배포할 수 있는가?”로 바꾸는 인증 구조의 전환**입니다.

> 이 글은 2026년 9월 3일 GitHub Changelog와 npm 공식 문서, OpenSSF의 Trusted Publishers 지침을 기준으로 작성했습니다.

---

## 1. 기존 npm 배포 토큰은 왜 위험한가?

전통적인 자동 배포는 npm 쓰기 토큰을 GitHub Actions 같은 CI/CD 시스템의 비밀 정보에 저장하는 방식입니다.

    개발자가 릴리스 실행
          ↓
    CI가 저장된 NPM_TOKEN 조회
          ↓
    npm registry에 패키지 업로드

구성이 단순하지만 토큰은 다음과 같은 특성을 가집니다.

- 유출된 뒤 관리자가 발견하고 폐기할 때까지 사용할 수 있습니다.
- CI 로그, 잘못된 설정, 악성 액션, 침해된 러너에서 노출될 수 있습니다.
- 여러 워크플로가 하나의 토큰을 공유하면 실제 배포 주체를 구분하기 어렵습니다.
- 만료와 교체 주기를 사람이 관리해야 합니다.
- 필요 이상으로 넓은 패키지와 작업 권한을 가질 수 있습니다.

공급망 공격에서 배포 자격 증명은 특히 가치가 큽니다. 공격자가 소스 저장소 전체를 장악하지 않아도 정상 패키지 이름으로 악성 버전을 올릴 수 있기 때문입니다.

---

## 2. OIDC Trusted Publishing은 어떻게 동작하나?

Trusted Publishing은 OpenID Connect(OIDC)를 이용해 CI/CD 워크로드의 신원을 짧은 수명의 토큰으로 증명합니다.

    GitHub Actions 워크플로 실행
          ↓
    GitHub가 서명된 OIDC ID 토큰 발급
          ↓
    npm이 발급자·서명·대상·클레임 검증
          ↓
    미리 등록한 저장소·워크플로·환경 조건과 비교
          ↓
    조건이 맞을 때만 짧은 배포 권한 부여
          ↓
    npm publish 또는 npm stage publish

관리자는 npm 패키지 설정에 신뢰할 CI 제공자와 저장소, 워크플로 파일, 환경 조건을 미리 등록합니다. npm은 배포 시 제출된 토큰이 이 정책과 일치하는지 확인합니다.

장기 토큰과의 차이는 명확합니다.

| 구분 | 장기 npm 토큰 | OIDC Trusted Publishing |
| --- | --- | --- |
| 자격 증명 수명 | 폐기 또는 만료까지 유지 | 워크플로 실행 시 짧게 발급 |
| 저장 위치 | CI 비밀 정보 | 장기 비밀 저장 불필요 |
| 권한 기준 | 토큰 소유 여부 | 저장소·워크플로·환경 신원 |
| 유출 영향 | 재사용 가능성이 큼 | 유효 시간이 짧고 조건이 제한됨 |
| 운영 부담 | 생성·저장·교체·폐기 | 신뢰 정책 중심 관리 |
| 출처 증명 | 별도 설정 필요 | 지원 조건에서 provenance 자동 생성 |

OpenSSF는 이런 구조를 패키지 저장소 보안의 중요한 단계로 봅니다. 장기 API 키를 외부 빌드 시스템에 전달하지 않고, 검증 가능한 워크로드 신원을 배포 권한과 연결할 수 있기 때문입니다.

---

## 3. 이번 업데이트의 핵심: 패키지당 최대 10개 구성

이전에는 npm 패키지 하나에 Trusted Publisher 구성을 하나만 연결할 수 있었습니다. 실제 프로젝트는 배포 경로가 하나가 아닌 경우가 많습니다.

- 태그를 기준으로 안정 버전을 배포하는 워크플로
- beta, rc 등 프리릴리스를 만드는 별도 워크플로
- 배포 전 검증을 위한 스테이징 워크플로
- GitHub Actions와 GitLab CI/CD를 함께 사용하는 전환 기간
- 저장소 이전이나 CI 제공자 교체 과정의 병행 운영
- 모노레포에서 패키지별로 분리된 릴리스 파이프라인

이제 패키지 하나에 **최대 10개의 Trusted Publisher 연결**을 둘 수 있습니다. 각 구성은 저장소, 워크플로, 환경 조건을 독립적으로 가지며 추가하거나 삭제할 수 있습니다.

중요한 동작 원칙은 다음과 같습니다.

1. 구성은 서로 독립적이고 추가적입니다.
2. 들어온 OIDC 토큰이 구성 하나와 일치하면 배포가 허용됩니다.
3. 구성 사이의 평가 순서는 보장되지 않습니다.
4. 한 구성이 다른 구성을 제한하지 않습니다.
5. 기존 연결의 필드는 직접 수정할 수 없으며, 변경하려면 삭제 후 다시 만들어야 합니다.

따라서 “첫 번째 규칙이 실패하면 두 번째 규칙을 적용한다” 같은 순서 기반 정책을 설계해서는 안 됩니다. 각 구성 하나만으로도 허용 범위가 안전해야 합니다.

---

## 4. 다중 구성이 장기 토큰을 없애는 마지막 퍼즐인 이유

단일 OIDC 구성만 가능할 때는 기본 릴리스는 Trusted Publishing으로 전환해도 예외 경로가 문제였습니다. 프리릴리스나 긴급 배포, 다른 CI에서 실행되는 작업 때문에 장기 토큰을 계속 남겨 두는 경우가 있었습니다.

다중 구성은 다음과 같이 경로를 분리할 수 있게 합니다.

| 배포 경로 | 신뢰 조건 예시 | 권장 동작 |
| --- | --- | --- |
| 안정 버전 | release.yml + production 환경 | 스테이징 후 사람 승인 |
| 프리릴리스 | prerelease.yml + beta 환경 | 스테이징 후 사람 승인 |
| 야간 빌드 | nightly.yml + 제한된 태그 정책 | 별도 dist-tag와 스테이징 |
| CI 전환 | 기존·신규 제공자를 각각 등록 | 전환 완료 후 기존 구성 삭제 |
| 긴급 복구 | 별도 보호 환경과 담당자 승인 | 평상시 비활성 또는 강한 승인 |

이제 예외 워크플로를 위해 NPM_TOKEN을 유지하는 대신, 각 경로를 명시적인 워크로드 신원으로 등록할 수 있습니다.

---

## 5. 스테이징 배포가 공급망 방어에 중요한 이유

새로 만드는 Trusted Publisher 구성은 기본적으로 **npm stage publish**를 허용하며, 즉시 공개하는 **npm publish** 권한은 구성별 선택 사항입니다. GitHub와 npm은 가능하면 스테이징 전용 구성을 유지하도록 권장합니다.

스테이징 배포의 흐름은 다음과 같습니다.

    CI가 패키지 빌드
          ↓
    OIDC로 신원 검증
          ↓
    npm 스테이징 큐에 업로드
          ↓
    악성코드 검사 완료
          ↓
    관리자가 2FA로 승인
          ↓
    공개 버전으로 전환

9월 3일 업데이트 이후 악성코드 검사가 진행 중이면 승인 버튼이 비활성화되고, 검사가 끝난 뒤에만 승인할 수 있습니다. 자동화된 워크플로가 침해돼도 즉시 공개 레지스트리에 악성 버전을 올리지 못하도록 **기계 검사와 사람 승인을 순서대로 강제**하는 구조입니다.

버전 화면에 승인, 거부, 대기 이력이 표시되는 기능도 사고 대응과 감사에 유용합니다. 단순히 어떤 버전이 존재하는지가 아니라 배포 과정에서 어떤 결정이 있었는지 확인할 수 있습니다.

---

## 6. OIDC가 해결하는 것과 해결하지 못하는 것

OIDC는 장기 토큰 유출 위험을 크게 줄이지만 모든 공급망 문제를 해결하지는 않습니다.

### 해결하는 위험

- 저장소 비밀 정보에 장기 쓰기 토큰을 보관하는 문제
- 토큰 교체와 만료 관리 부담
- 유출된 토큰을 장기간 재사용하는 공격
- 배포 주체와 원본 워크플로를 연결하기 어려운 문제
- 공개 저장소·공개 패키지의 출처 증명 생성 부담

### 여전히 남는 위험

- 신뢰하도록 등록한 워크플로 자체가 악의적으로 수정됨
- 보호되지 않은 브랜치나 환경에서 릴리스 실행
- 서드파티 액션 또는 빌드 의존성이 침해됨
- 빌드 전에 악성 코드가 산출물에 포함됨
- 짧은 수명의 OIDC 토큰이 유효 시간 안에 탈취됨
- 너무 많은 독립 구성이 불필요한 배포 경로를 늘림

OpenSSF도 Trusted Publisher가 만능 해결책은 아니라고 강조합니다. 이 방식은 신뢰를 없애는 것이 아니라 **장기 비밀에 대한 신뢰를 CI 워크플로와 저장소 정책에 대한 신뢰로 이동**시킵니다.

따라서 OIDC 전환과 함께 브랜치 보호, 환경 승인, 워크플로 코드 리뷰, 액션 버전 고정, 최소 권한을 적용해야 합니다.

---

## 7. GitHub Actions 설정 예시

npm 공식 문서 기준으로 Trusted Publishing은 npm CLI 11.5.1 이상과 Node.js 22.14.0 이상이 필요합니다. GitHub Actions에서는 GitHub 호스티드 러너를 사용하고 **id-token: write** 권한을 명시해야 합니다.

다음은 스테이징 중심의 최소 예시입니다.

    name: Stage npm package

    on:
      push:
        tags:
          - 'v*'

    permissions:
      id-token: write
      contents: read

    jobs:
      stage:
        runs-on: ubuntu-latest
        environment: production

        steps:
          - uses: actions/checkout@v6

          - uses: actions/setup-node@v6
            with:
              node-version: '24'
              registry-url: 'https://registry.npmjs.org'
              package-manager-cache: false

          - run: npm ci
          - run: npm run build --if-present
          - run: npm test
          - run: npm stage publish

npm 패키지 설정에서는 이 저장소, 워크플로 파일, production 환경을 Trusted Publisher로 등록합니다. package.json의 repository.url도 실제 GitHub 저장소와 정확히 일치해야 합니다.

---

## 8. 안전한 마이그레이션 순서

장기 토큰을 먼저 삭제하면 기존 배포가 중단될 수 있습니다. 다음 순서가 안전합니다.

### 1단계: 실행 환경 확인

- npm CLI 11.5.1 이상인지 확인합니다.
- Node.js 22.14.0 이상인지 확인합니다.
- 지원되는 클라우드 호스티드 러너인지 확인합니다.
- package.json의 저장소 URL을 검증합니다.

현재 npm Trusted Publishing은 GitHub 호스티드 러너, GitLab.com 공유 러너, CircleCI 클라우드를 지원합니다. 셀프 호스티드 러너는 아직 지원되지 않습니다.

### 2단계: 신뢰 구성 등록

npmjs.com의 패키지 설정에서 저장소, 워크플로, 환경을 정확히 등록합니다. 저장 시 실제 동작 여부를 자동 검증하지 않으므로 파일 이름과 조건을 다시 확인해야 합니다.

### 3단계: 스테이징 배포 시험

처음부터 즉시 공개 권한을 주지 말고 npm stage publish로 빌드, 검사, 승인 흐름을 검증합니다. 안정·프리릴리스 워크플로가 다르면 각각 독립적으로 시험합니다.

### 4단계: 기존 토큰 경로 차단

OIDC 배포가 정상 동작하면 패키지 설정에서 **2FA를 요구하고 토큰 배포를 허용하지 않는 정책**을 선택합니다. 이후 사용하지 않는 자동화 토큰과 CI 비밀 정보를 폐기합니다.

### 5단계: 감사와 복구 점검

등록된 구성을 정기적으로 검토하고, 더 이상 사용하지 않는 저장소·워크플로·CI 제공자의 연결을 삭제합니다. 승인 이력과 빌드 provenance도 함께 확인합니다.

---

## 9. 놓치기 쉬운 운영 주의점

### 비공개 의존성 설치에는 별도 읽기 권한이 필요할 수 있다

Trusted Publishing은 배포를 인증합니다. npm ci 과정에서 비공개 패키지를 내려받는 권한까지 대신하지 않습니다. 필요한 경우 설치 단계에만 범위가 좁은 읽기 전용 토큰을 사용하고, 배포에는 OIDC를 사용해야 합니다.

### 재사용 워크플로의 호출 관계를 확인한다

workflow_call이나 수동 실행을 사용하는 경우 npm이 실제 배포 명령이 있는 파일이 아니라 호출한 워크플로 이름을 검증할 수 있습니다. 부모와 자식 워크플로 모두 OIDC 권한이 필요할 수 있으므로 공식 문서의 검증 규칙을 확인해야 합니다.

### provenance의 지원 범위를 구분한다

GitHub Actions나 GitLab CI/CD에서 공개 저장소의 공개 패키지를 Trusted Publishing으로 배포하면 npm이 provenance 증명을 자동 생성합니다. 비공개 저장소에서 공개 패키지를 배포하는 경우에는 현재 자동 provenance가 지원되지 않습니다. CircleCI도 현재 자동 생성 대상이 아닙니다.

### 구성을 많게 만드는 것이 목표는 아니다

최대 10개를 지원한다고 해서 10개를 채울 필요는 없습니다. 사용하지 않는 신뢰 경로는 공격 표면입니다. 각 구성에는 소유자, 목적, 검토일, 폐기 조건이 있어야 합니다.

---

## 10. 운영 체크리스트

- 장기 npm 쓰기 토큰이 CI 비밀 정보에 남아 있지 않은가?
- 패키지마다 필요한 최소 Trusted Publisher 구성만 등록했는가?
- 각 구성의 저장소, 워크플로, 환경 조건이 정확한가?
- 안정 버전과 프리릴리스의 권한 경계가 분리돼 있는가?
- 기본 배포가 npm stage publish를 사용하는가?
- 악성코드 검사 완료 후에만 승인되는지 시험했는가?
- 사람 승인이 2FA와 보호된 환경을 통해 수행되는가?
- 릴리스 브랜치와 워크플로 변경에 코드 리뷰가 필요한가?
- 서드파티 GitHub Action을 불변 커밋 SHA로 고정했는가?
- 비공개 의존성 토큰은 읽기 전용이며 배포 권한이 없는가?
- provenance와 승인 이력을 정기적으로 확인하는가?
- CI 전환이 끝난 뒤 이전 Trusted Publisher 구성을 삭제했는가?

---

## 결론

npm의 다중 Trusted Publishing 지원은 현실의 복잡한 배포 파이프라인을 OIDC 보안 모델 안으로 가져온 변화입니다. 안정 버전과 프리릴리스, 여러 CI 제공자 때문에 남겨 두었던 장기 토큰을 제거하고, 각 배포 경로를 검증 가능한 워크로드 신원으로 표현할 수 있게 됐습니다.

가장 안전한 운영 방식은 **여러 OIDC 구성 + 스테이징 배포 + 악성코드 검사 + 사람의 2FA 승인 + 기존 토큰 차단**을 함께 적용하는 것입니다.

그러나 인증 기술만 바꿔서는 충분하지 않습니다. OIDC가 신뢰하는 저장소와 워크플로를 보호하고, 구성 수를 최소화하며, 빌드 결과와 승인 이력을 계속 검증해야 합니다. 공급망 보안의 목표는 비밀을 더 잘 숨기는 것이 아니라 **오래 재사용할 수 있는 비밀 자체를 없애고, 허용된 작업의 신원을 짧고 명확하게 증명하는 것**입니다.

---

## 참고 자료

- [GitHub Changelog, Multiple trusted publishing configurations for npm (2026-09-03)](https://github.blog/changelog/2026-09-03-multiple-trusted-publishing-configurations-for-npm/)
- [npm Docs, Trusted publishing for npm packages](https://docs.npmjs.com/trusted-publishers/)
- [npm Docs, npm trust command](https://docs.npmjs.com/cli/v11/commands/npm-trust/)
- [npm Docs, Securing your code](https://docs.npmjs.com/packages-and-modules/securing-your-code/)
- [OpenSSF, Trusted Publishers for All Package Repositories](https://repos.openssf.org/trusted-publishers-for-all-package-repositories.html)
- [OpenSSF, Principles for Package Repository Security](https://repos.openssf.org/principles-for-package-repository-security.html)
- [OpenSSF, Build Provenance for All Package Registries](https://repos.openssf.org/build-provenance-for-all-package-registries.html)

> 기능과 지원 환경은 변경될 수 있습니다. 실제 전환 전에는 npm과 CI 제공자의 최신 공식 문서를 확인해야 합니다.
