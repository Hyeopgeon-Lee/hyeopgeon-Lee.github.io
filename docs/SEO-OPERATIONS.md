# SEO 운영 가이드

## 등록할 사이트와 제출 문서

| 서비스 | 등록 주소 | 제출 sitemap | 추가 |
| --- | --- | --- | --- |
| [Google Search Console](https://search.google.com/search-console/) | `https://prof.k-bigdata.kr/` URL 접두어 속성 또는 `prof.k-bigdata.kr` 도메인 속성 | `https://prof.k-bigdata.kr/sitemap.xml` | 중요한 새 글은 URL 검사 후 색인 생성 요청 |
| [Naver Search Advisor](https://searchadvisor.naver.com/) | `https://prof.k-bigdata.kr/` | `https://prof.k-bigdata.kr/sitemap.xml` | RSS `https://prof.k-bigdata.kr/feed.xml`도 제출 |
| [Bing Webmaster Tools](https://www.bing.com/webmasters/) | `https://prof.k-bigdata.kr/` | `https://prof.k-bigdata.kr/sitemap.xml` | Google Search Console에서 확인된 사이트 가져오기 가능 |

각 서비스에 본인 계정으로 로그인해 소유 확인을 완료한다. DNS 또는 해당 서비스가 실제 발급한 확인 방법을 사용한다. 기존 소유 확인 파일은 유지한다. 새로운 verification 값이나 계정·비밀번호·PAT를 예시로 만들어 저장하지 않는다. 도메인 속성은 DNS 확인이 필요하다. 등록 여부와 소유권 상태는 소스만으로 알 수 없다.

Google은 Sitemaps 메뉴, 네이버는 요청 → 사이트맵 제출 및 RSS 제출, Bing은 Sitemaps에서 제출한다. 입력창이 경로만 받으면 `sitemap.xml` 또는 `feed.xml`을 입력한다. Google URL 검사는 개별 글의 전체 canonical URL을 입력하고 실시간 테스트 및 색인 생성 요청을 사용한다.

## 새 글 작성: 파일 하나로 자동 반영

`_posts/YYYY-MM-DD-slug.md` 또는 `.html` 파일을 추가한다. 파일명 날짜와 실제 게시일을 일치시키고, 고유한 제목을 적는다. 본문은 H2부터 시작한다. 공통 레이아웃이 제목 H1을 만든다. 기존 글의 날짜·slug·permalink는 수정하지 않는다.

```yaml
---
title: "실제 내용을 설명하는 고유한 제목"
date: 2026-10-03 09:00:00 +0900
description: "글의 핵심 내용과 독자가 얻는 정보를 설명하는 1~2문장 요약."
tags: [Kubernetes, CloudNative, DevOps]
---

## 문제와 배경
본문...
```

`layout: default`는 `_config.yml` 기본값이다. 기존 날짜/slug 기반 URL 규칙을 명시적으로 고정했다. description이 없으면 excerpt를 HTML 제거·공백 정리·180자 제한으로 사용한다. 제목만으로 요약이 충분하지 않을 수 있으므로 작성자가 의미 있는 요약을 쓰는 것이 좋다. title, canonical, OG, Twitter, BlogPosting, breadcrumb, RSS, sitemap, 전체 목록, 홈 최신글, 작성자 소개, 태그 관련글은 자동 적용한다. 태그는 내용에 맞는 기존 표기를 우선 사용한다.

사진은 의미 있는 alt와 실제 width/height를 지정한다. 본문 이미지에는 `loading="lazy" decoding="async"`를 사용한다. 대표 이미지를 직접 지정하면 실제 절대 URL 또는 사이트 내부 경로를 사용한다. 모르는 조직·학력·프로필은 구조화데이터에 추가하지 않는다.

## 게시일·수정일과 배포

GitHub Settings → Pages의 Source는 **GitHub Actions**다. main push마다 `.github/workflows/pages.yml`이 전체 이력을 가져와 `tools/prepare_seo.py`로 `_data/seo_dates.json`을 생성한다. 이 파일과 `_data/seo_build.json`은 빌드 산출물이며 Git에 커밋하지 않는다. 각 페이지의 실제 소스 또는 구조화데이터·작성자 공통 템플릿의 최근 커밋 시각을 수정일로 사용한다. 홈과 Blog 목록은 최신 `_posts` 변경도 포함한다. 게시일은 front matter의 실제 date로 유지한다. 빌드 시각을 무조건 lastmod로 사용하지 않는다.

공통 코드의 단순 공백 변경도 해당 소스의 변경으로 기록될 수 있다. 내용과 무관한 정기 갱신 커밋을 만들지 않는다. 글 본문 변경은 반드시 Git에 커밋하고 이력을 유지한다. 미래 발행일의 글은 Jekyll이 실제 발행 시각 전까지 제외한다. 예약 발행은 그 시각 이후 별도 빌드 실행이 필요하며 이 작업에서는 예약 스케줄을 추가하지 않았다.

Jekyll 빌드에서 전체 sitemap과 전체 기술글 RSS를 생성한다. sitemap은 검색 대상 `default` 페이지 및 게시글만 포함하고 `noindex: true`, `sitemap: false` 페이지를 제외한다. 404, 개발 문서, tools와 인증 파일을 sitemap에 넣지 않는다. 향후 정적 페이지를 추가해도 default 레이아웃이면 자동 포함한다. 수동 sitemap URL 목록을 관리하지 않는다.

빌드 결과의 모든 URL을 검사하여 오류 시 배포를 막는다. 공개된 정확한 커밋을 확인하고 실서비스를 다시 전수 검사한 뒤 IndexNow에 알린다. 검증 보고서는 Actions의 `seo-build-audit`, `seo-live-audit` 산출물에서 내려받는다. 배포 성공 후 IndexNow가 실패하면 사이트는 정상 유지되며 discovery 작업만 재실행할 수 있다.

## IndexNow

기존 공개 도메인 확인용 키 파일을 재사용한다. IndexNow의 이 키는 공개 확인 식별자이며 GitHub 인증 토큰이나 비밀 API 자격증명이 아니다. 별도 개인 API 키/PAT를 소스에 넣지 않는다. Actions는 저장소가 제공하는 최소 권한의 `GITHUB_TOKEN`만 환경으로 사용한다. 기존의 독립적인 중복 빌드/알림 workflow는 배포 검증 뒤 실행하는 작업으로 통합했다. IndexNow 요청 승인(200/202)은 접수만 의미하며 색인 완료가 아니다. Google에 대한 직접 색인 요청을 대신하지 않는다.

## 발행 후 확인

1. Actions의 build, deploy, discovery 결과를 확인한다.
2. 글 URL의 HTTP 200, 하나의 H1, title/description/canonical과 실제 내용을 확인한다.
3. `/blog/`, 홈 최신글, sitemap, feed에서 새 글 링크를 확인한다.
4. [Google Rich Results Test](https://search.google.com/test/rich-results)에서 글의 BlogPosting/Breadcrumb를 검사한다.
5. [Schema Markup Validator](https://validator.schema.org/)에서 WebSite·Person·ProfilePage·Blog 관계도 확인한다. 모든 Schema 타입이 Google 리치 결과 대상인 것은 아니다.
6. Google URL 검사, 네이버 웹페이지 수집/색인 정보, Bing URL Inspection으로 실제 수집 및 색인 상태를 확인한다.
7. `site:prof.k-bigdata.kr` 및 글 제목 검색은 참고용으로 사용한다. 전체 색인 수의 정확한 판정은 각 웹마스터 도구 보고서를 사용한다.

## 수동 전수 검사

Python과 lxml 설치 후 저장소 루트에서 실행한다.

```text
python tools/prepare_seo.py
bundle exec jekyll build
python tools/audit_seo.py --site _site --strict
python tools/audit_seo.py --strict --output seo-live-audit.json
```

검사 범위는 모든 sitemap URL의 HTTP/파일 존재, canonical, title/description 중복, JSON-LD 파싱과 핵심 타입, OG/Twitter, H1, lang, 이미지 alt·크기, 전체 글 목록 링크, feed, robots, 404, 도메인·중복·날짜·noindex다. 검색 순위나 Rich Results 서비스의 최종 판정을 자동 검사가 보장하지 않는다.

## 모바일·Core Web Vitals

[PageSpeed Insights](https://pagespeed.web.dev/)에서 홈, 목록, 최근 글을 모바일/데스크톱으로 검사한다. 실제 방문자 지표는 Search Console의 Core Web Vitals/CrUX 보고서를 사용한다. 방문량이 적으면 현장 데이터가 없을 수 있다. INP는 실제 상호작용이 필요한 지표라 단일 HTTP 응답시간이나 Lighthouse의 TBT로 대체해 확정하지 않는다. 대표 사진 WebP, 명시적 이미지 크기, 지연 로드, 비동기 코드 복사와 웹폰트 `display=swap`을 유지한다.

## 공식 참고자료

- [Google sitemap 원칙](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap): 정확한 canonical URL과 의미 있는 lastmod.
- [Google Article 구조화데이터](https://developers.google.com/search/docs/appearance/structured-data/article).
- [Naver RSS·sitemap 제출](https://searchadvisor.naver.com/guide/request-feed).
- [Bing 사이트 추가와 확인](https://www2.bing.com/webmasters/help/add-and-verify-site-12184f8b).
- [IndexNow 규약](https://www.indexnow.org/documentation).
- [GitHub Pages Actions 배포](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).
- [Core Web Vitals 설명](https://web.dev/articles/vitals).

검색엔진은 자체 기준으로 수집·색인·노출을 결정한다. 기술적 준비와 알림을 완료해도 모든 글의 즉시 색인 또는 상위 노출을 보장할 수 없다.
