# hyeopgeon-Lee.github.io

이 저장소는 **이협건 교수 기술 블로그**(GitHub Pages)를 위한 정적 사이트 소스입니다.  
Jekyll 기반으로 운영되며, 클라우드/인공지능/빅데이터 관련 강의 및 기술 노트를 게시합니다.

## 사이트 정보

- 사이트 URL: `https://hyeopgeon-lee.github.io`
- 블로그 메인: `https://hyeopgeon-lee.github.io/blog/`
- 언어/로케일: `ko-KR`
- 시간대: `Asia/Seoul`

## 기술 스택

- **Jekyll** (GitHub Pages 환경)
- **Minimal Mistakes** 테마 (`mmistakes/minimal-mistakes@4.24.0`)
- Ruby Gems
  - `github-pages`
  - `webrick` (Windows 로컬 실행 대응)
  - `jekyll-include-cache`
  - `jekyll-seo-tag`

## 주요 디렉터리 구조

- `_config.yml`: 사이트 설정 (제목, SEO, 메뉴, 작성자 정보 등)
- `_posts/`: 블로그 게시글 (`YYYY-MM-DD-title.md`)
- `_layouts/`: 레이아웃 템플릿
- `_includes/`: 공통 include 조각
- `assets/`: 이미지/CSS 등 정적 리소스
- `index.md`: 홈 페이지
- `blog/index.md`: 기술 블로그 목록 페이지
- `.github/workflows/`: GitHub Actions 자동화 (sitemap 생성)

## 로컬 실행 방법

### 1) Ruby / Bundler 준비

로컬에 Ruby와 Bundler가 설치되어 있어야 합니다.

```bash
gem install bundler
bundle install
```

### 2) Jekyll 서버 실행

```bash
bundle exec jekyll serve
```

실행 후 브라우저에서 아래 주소로 확인합니다.

- `http://127.0.0.1:4000`

## 글 작성 방법

`_posts/` 폴더에 아래 형식으로 Markdown 파일을 추가합니다.

- 파일명 규칙: `YYYY-MM-DD-slug.md`

예시:

```text
_posts/2026-02-26-example-post.md
```

기본 Front Matter 예시:

```yaml
---
title: "게시글 제목"
date: 2026-02-26 09:00:00 +0900
categories: [cloud]
tags: [kubernetes, devops]
excerpt: "게시글 요약"
---
```

## 배포

이 저장소는 GitHub Pages용 저장소(`username.github.io`) 형태로 운영됩니다.  
`main` 브랜치에 반영된 내용이 GitHub Pages에 배포됩니다(저장소 설정 기준).

## 자동화 (sitemap.xml)

`.github/workflows/generate-sitemap.yml` 워크플로가 `main` 브랜치 푸시 시 실행되어:

- `sitemap.xml` 생성
- 변경 사항이 있을 경우 자동 커밋/푸시

## 참고 사항

- `_config.yml`의 `author`, `nav`, `seo` 설정으로 사이트 정보/메뉴를 관리합니다.
- 페이지/포스트 기본 CSS는 `assets/css/custom.css`가 적용되도록 설정되어 있습니다.
