# 이협건 교수 홈페이지

한국폴리텍대학 서울강서캠퍼스 이협건 교수의 **연구·교육 포트폴리오와 기술 블로그**를 운영하는 GitHub Pages 저장소입니다.

AI, 클라우드, 빅데이터, 소프트웨어 엔지니어링 분야의 연구실적과 교육 활동을 소개하고, 최신 기술을 분석한 글과 수업에 활용하는 공개 실습자료를 연결합니다.

## 바로가기

- [홈페이지](https://hyeopgeon-lee.github.io/)
- [연구실적](https://hyeopgeon-lee.github.io/research/)
- [교육](https://hyeopgeon-lee.github.io/teaching/)
- [기술 블로그](https://hyeopgeon-lee.github.io/blog/)

## 사이트 구성

### 교수 포트폴리오

- 이협건 교수 및 한국폴리텍대학 서울강서캠퍼스 소개
- AI·Cloud·Big Data·Software Engineering 연구·교육 분야
- 최신 기술 글과 최근 게시글
- 연구·교육 페이지 및 GitHub 실습자료 연결

### 연구실적

- 연도별 학술지 논문
- 논문 저자, 학술지, 권·호 및 페이지 정보
- KCI, KISS, DBpia, DOI 원문 연결

### 교육

- 인공지능 응용 소프트웨어
- 빅데이터 처리와 분석
- 백엔드 소프트웨어 개발
- 클라우드 네이티브와 K-PaaS
- 서울시 고등학교 교원·학생 대상 인공지능·빅데이터 교육
- K-PaaS 강사양성 교육 및 기술 세미나
- 학생 프로젝트와 포트폴리오

### 기술 블로그

- AI 및 AI 에이전트
- 클라우드 네이티브와 Kubernetes
- 빅데이터 및 데이터 엔지니어링
- DevOps, MSA, API Gateway
- 소프트웨어 엔지니어링과 보안

## 디자인 및 기술 구성

- **Jekyll** 기반 GitHub Pages
- **Minimal Mistakes** 원격 테마를 기반으로 한 사용자 정의 레이아웃
- Deep Navy·Blue·White 색상의 교수·기술 포트폴리오 디자인
- 데스크톱, 태블릿, 모바일 반응형 레이아웃
- 게시글 읽기에 집중한 1열 콘텐츠 구조
- `jekyll-seo-tag` 기반 검색·소셜 메타데이터
- GitHub Actions 기반 `sitemap.xml` 자동 갱신

## 주요 파일과 디렉터리

```text
.
├── _config.yml                 # 사이트 정보, 작성자, 메뉴 및 Jekyll 설정
├── _layouts/default.html       # 공통 헤더, 내비게이션, 본문 및 footer
├── _includes/                  # head 및 공통 include
├── _posts/                     # 기술 블로그 게시글
├── assets/
│   ├── css/custom.css          # 전체 디자인과 반응형 스타일
│   ├── images/profile.jpg      # 프로필 이미지
│   └── js/                     # 게시글 편의 기능
├── index.md                    # 포트폴리오형 홈페이지
├── research.md                 # 연구실적 페이지
├── teaching.md                 # 교육 및 교육실적 페이지
├── blog/index.md               # 기술 블로그 목록
├── sitemap.xml                 # 검색엔진 사이트맵
└── .github/workflows/          # 사이트맵 자동화
```

## 게시글 작성 방법

`_posts/` 디렉터리에 `YYYY-MM-DD-slug.md` 형식의 Markdown 파일을 추가합니다.

```yaml
---
layout: default
title: "게시글 제목"
date: 2026-09-03 09:00:00 +0900
excerpt: "홈과 블로그 목록에 표시할 게시글 요약"
---

# 게시글 제목

본문을 작성합니다.
```

게시글 URL은 기존 GitHub Pages 규칙에 따라 다음과 같이 생성됩니다.

```text
https://hyeopgeon-lee.github.io/YYYY/MM/DD/slug.html
```

## 로컬 실행

Ruby와 Bundler를 설치한 뒤 다음 명령을 실행합니다.

```bash
gem install bundler
bundle install
bundle exec jekyll serve
```

로컬 미리보기 주소는 `http://127.0.0.1:4000`입니다.

## 배포와 자동화

- `main` 브랜치에 반영된 변경사항은 GitHub Pages를 통해 배포됩니다.
- `.github/workflows/generate-sitemap.yml`이 사이트를 크롤링하여 `sitemap.xml`을 갱신합니다.
- 사이트맵이 변경되면 GitHub Actions가 자동으로 커밋하고 최종 Pages 배포가 다시 실행됩니다.

## 저장소 공개 범위와 보안

이 저장소에는 웹사이트에 공개할 수 있는 정적 콘텐츠만 저장합니다. API 키, 비밀번호, 개인 자료 등 민감한 정보는 커밋하지 않습니다.

GitHub Free에서 GitHub Pages를 계속 사용하려면 저장소를 공개 상태로 유지해야 합니다. GitHub Pro 이상에서는 비공개 저장소에서도 Pages를 사용할 수 있지만, 저장소가 비공개여도 배포된 홈페이지는 기본적으로 인터넷에 공개됩니다.
