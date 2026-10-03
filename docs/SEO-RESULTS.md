# SEO 수정 및 운영 배포 검증 결과

검증일: 2026-10-03 (한국 시간). 저장소: https://github.com/Hyeopgeon-Lee/hyeopgeon-Lee.github.io

## 1. 기존 문제와 수정 범위

[수정 전 전수 점검](SEO-AUDIT.md)에 전체 URL과 23개 점검 항목을 기록했다. 기존 sitemap에는 이미 31개 URL이 있었다. 이를 일부 누락된 것으로 판단하지 않고 유지하면서 실제 수정일과 자동 검증을 보강했다. RSS가 없었고, 게시글 description 일부가 제목과 같았으며, H1 중복, 게시글 제목의 작성자 식별 부족, 구조화데이터 관계와 breadcrumb 부족, 정적 페이지 수정일 부족, 이미지 크기 누락, 모바일 가로 넘침이 있었다. IndexNow는 실제 배포 완료를 확인하지 않고 실행되는 구조였다.

기존 31개 정상 URL 집합과 디자인을 유지했다. 게시글의 실질적인 기술 내용은 보존하고 요약·heading·작성자 및 관련 링크를 개선했다. CNAME prof.k-bigdata.kr과 HTTPS 설정을 유지했다. GitHub Pages Source를 GitHub Actions로 전환하여 검증된 Jekyll 결과만 배포한다.

## 2. 수정·생성·삭제 파일

수정 38개, 생성 16개, 삭제 2개. 생성된 Git 날짜/빌드 정보는 임시 빌드 자료이며 커밋하지 않는다.

### 수정

- `README.md`
- `_config.yml`
- `_includes/head.html`
- `_includes/head/custom.html`
- `_includes/post-footer.html`
- `_layouts/default.html`
- `_posts/2025-05-06-kubernetes-intro.md`
- `_posts/2025-05-07-k8s-core-components.md`
- `_posts/2025-05-08-k8s-pod-lifecycle.md`
- `_posts/2025-05-09-k8s-networking-basics.md`
- `_posts/2025-05-10-k8s-scheduling-principles.md`
- `_posts/2025-05-12-k8s-controller-types.md`
- `_posts/2026-01-12-rtx_a6000pro_ai_education.md`
- `_posts/2026-01-28-ingress-nginx-eol.md`
- `_posts/2026-01-29-cloud-native-msa-12factor.md`
- `_posts/2026-01-30-n8n-intro.md`
- `_posts/2026-02-01-devops-overview.md`
- `_posts/2026-02-02-api-gateway-cloud-native.md`
- `_posts/2026-02-25-mcp-vs-tool-calling.md`
- `_posts/2026-02-26-gpt-oss.md`
- `_posts/2026-09-02-openai-hugging-face-agent-security-lessons.md`
- `_posts/2026-09-04-github-copilot-pr-approval-governance.md`
- `_posts/2026-09-07-gpt-6-astra-agent-harness-benchmark.md`
- `_posts/2026-09-09-npm-oidc-trusted-publishing-supply-chain.md`
- `_posts/2026-09-11-bigquery-graph-gql-ga.md`
- `_posts/2026-09-14-aws-lambda-90-minute-managed-instances.md`
- `_posts/2026-09-16-github-https-sha1-sunset.md`
- `_posts/2026-09-21-cloud-storage-intelligence-advisor-ga.md`
- `_posts/2026-09-23-github-actions-workflow-execution-protections-ga.md`
- `_posts/2026-09-28-aws-resilience-hub-dependency-insights.md`
- `_posts/2026-09-30-google-intelligent-endpoints-browser-agent-security.md`
- `_posts/2026-10-02-google-cloud-data-agent-kit-ga.md`
- `about.md`
- `assets/css/custom.css`
- `assets/js/analytics.js`
- `blog/index.md`
- `index.md`
- `teaching.md`

### 생성

- `.github/workflows/pages.yml`
- `.gitignore`
- `404.html`
- `_includes/seo-schema.html`
- `assets/css/fonts.css`
- `assets/images/profile.webp`
- `assets/js/code-copy.js`
- `docs/SEO-AUDIT.md`
- `docs/SEO-OPERATIONS.md`
- `feed.xml`
- `sitemap.xml`
- `tools/audit_seo.py`
- `tools/notify_indexnow.py`
- `tools/prepare_seo.py`
- `tools/test_new_posts.py`
- `docs/SEO-RESULTS.md`

### 삭제

- `.github/workflows/indexnow.yml`
- `assets/js/clipboard.min.js`

## 3. robots.txt

기존 올바른 내용을 유지했고 실제 URL은 HTTP 200이다. 개발 도구·문서는 빌드 대상에서 제외한다.

```text
User-agent: *
Allow: /

Sitemap: https://prof.k-bigdata.kr/sitemap.xml
```

## 4. 사이트맵

https://prof.k-bigdata.kr/sitemap.xml 에 주요 페이지 5개와 게시글 26개, 합계 31개 URL을 포함한다. 31개 모두 lastmod를 제공한다. 전체 Git 이력에서 실제 콘텐츠 및 공통 템플릿 수정 시각을 계산한다. 게시일은 원래 front matter 날짜를 유지한다. 중복·다른 도메인·HTTP·잘못된 날짜·noindex·404·누락 URL은 자동 검증한다.

## 5. 구조화데이터와 작성자

모든 검색 대상 페이지에 Person, WebSite, 학교 CollegeOrUniversity와 학과 Organization 관계를 정의했다. About은 ProfilePage, Blog 목록은 CollectionPage와 Blog, 모든 26개 게시글은 BlogPosting과 BreadcrumbList를 제공한다. 작성자와 발행자는 실제 개인 작성자 엔티티를 참조한다. sameAs는 확인된 GitHub만 사용하며 학위나 학술 프로필 주소를 추측하지 않았다. 글 하단 작성자 소개, About 링크와 주제별 관련 글을 제공한다.

## 6. canonical 및 페이지 메타데이터

31개 모두 자기 URL의 HTTPS canonical, 고유 title·description, OG·Twitter, 한국어 lang, H1 한 개를 제공한다. HTTP는 HTTPS로, GitHub 원본 도메인은 사용자 도메인으로 연결된다. index.html 및 추적 파라미터 변형도 정상 canonical을 갖는다. www 하위 도메인은 DNS에 설정되어 있지 않아 별도 중복 서비스가 아니다. 기존 게시글 URL 규칙 /YYYY/MM/DD/slug.html을 유지한다.

## 7. RSS

https://prof.k-bigdata.kr/feed.xml 은 HTTP 200이며 현재 전체 26개 글의 요약과 본문을 포함한다. 신규 글은 자동으로 반영되고 head에 RSS 탐색 링크를 제공한다.

## 8. IndexNow

기존 공개 도메인 검증 키를 이용한다. 비밀번호·개인 API 키·PAT를 추가하지 않았다. 배포 완료 후 공개된 커밋을 확인하고 실사이트 전수 검증을 통과한 뒤 URL을 제출한다. 실제 제출에서 31개 URL, HTTP 200 수락을 확인했다. 수락은 검색 색인 완료를 의미하지 않는다.

## 9. 신규 글 자동화

_posts에 날짜 형식의 Markdown 또는 HTML 파일과 title/date front matter를 추가하면 공통 레이아웃이 title, description 기본값, canonical, OG/Twitter, H1, JSON-LD, 작성자와 관련 글을 제공한다. description은 명시 값 → excerpt → 사이트 설명 순으로 대체되므로 좋은 요약을 excerpt 또는 description에 작성하는 것이 좋다. sitemap, RSS, 최신순 Blog 목록과 홈 최근 글은 Jekyll 빌드로 갱신된다. 본문은 H2부터 작성한다.

GitHub Actions는 날짜 생성 → 빌드 → 전체 SEO 검증 → 임시 Markdown/HTML/한글 파일명 신규 글 3개 자동화 검사 → 배포 → 실사이트 검사 → IndexNow 순서로 실행한다. 임시 테스트 글은 운영 배포에 포함되지 않는다.

## 10–12. Google·Naver·Bing 등록 URL

| 검색엔진 | 등록할 사이트 | 제출 sitemap |
|---|---|---|
| Google Search Console | https://prof.k-bigdata.kr/ | https://prof.k-bigdata.kr/sitemap.xml |
| Naver Search Advisor | https://prof.k-bigdata.kr/ | https://prof.k-bigdata.kr/sitemap.xml |
| Bing Webmaster Tools | https://prof.k-bigdata.kr/ | https://prof.k-bigdata.kr/sitemap.xml |

Naver RSS 제출 주소는 https://prof.k-bigdata.kr/feed.xml 이다. Bing에서는 Google Search Console의 사이트 가져오기도 사용할 수 있다. 상세 등록·검사 절차는 [SEO 운영 가이드](SEO-OPERATIONS.md)에 기록했다. 인증 값을 임의 생성하지 않았고 기존 검증 파일은 보존했다.

## 13. 사람이 직접 해야 하는 작업

각 검색엔진 계정에서 사이트 소유 확인과 실제 등록 상태를 확인하고 sitemap을 제출한다. 계정 내부의 기존 등록 상태는 소스만으로 확인할 수 없다. 중요 신규 글은 Google URL 검사에서 색인 요청하고, 이후 페이지 색인·크롤링·검색 실적 보고서를 확인한다. 실제 서비스에서 발급된 인증 절차만 사용한다. 검색 노출 시점과 순위는 검색엔진이 결정하며 기술 검증 통과가 색인 완료를 보장하지 않는다.

## 14. 배포 후 실사이트 검사

전체 31개 URL을 직접 검사했다. 모두 HTTP 200, title·description·canonical·OG·JSON-LD·H1·내부 링크 검증에 오류가 없다. 블로그의 정적 HTML 링크와 sitemap/RSS는 전체 26개 게시글을 포함한다. robots.txt, sitemap.xml, feed.xml과 favicon은 정상 응답한다. 잘못된 경로는 실제 HTTP 404이며 noindex와 홈·Blog·About 복귀 링크를 제공한다.

전체 전수 검사 외 다음 무작위 5개와 최신 글을 명시적으로 확인했다.

- /2026/09/30/google-intelligent-endpoints-browser-agent-security.html
- /2025/05/12/k8s-controller-types.html
- /2026/09/02/openai-hugging-face-agent-security-lessons.html
- /2026/09/16/github-https-sha1-sunset.html
- /2026/01/30/n8n-intro.html
- 최신: /2026/10/02/google-cloud-data-agent-kit-ga.html

최신 글의 [Google Rich Results Test](https://search.google.com/test/rich-results/result?id=507QXrazjtPQwn1Mp7BBEQ)는 Article 1개와 Breadcrumb 1개, 유효한 항목 2개를 확인했다.

## 15. 모바일·성능 및 남은 한계

주요 5개 페이지와 최신 글을 모바일에서 확인했으며 가로 넘침이 없다. 데스크톱의 기존 디자인도 유지했다. 프로필 WebP는 기존 JPEG보다 약 50% 작고 JPEG fallback을 유지한다. 기존 웹폰트 선언을 약 80% 줄이고 늦은 글꼴 교체를 방지했다. 복사 라이브러리를 브라우저 기본 API로 대체하고 분석 스크립트를 초기 표시 후 로딩하도록 변경했다. 빠르게 떠나는 방문에서는 분석 수집 일부가 누락될 수 있다.

2026-10-03 11:07 KST 모바일 PageSpeed 실험 결과:

| 대상 | 성능 | SEO | LCP | CLS | TBT |
|---|---:|---:|---:|---:|---:|
| [홈](https://pagespeed.web.dev/analysis/https-prof-k-bigdata-kr/ylqgyp5qz9?form_factor=mobile) | 80 | 100 | 3.9초 | 0 | 80ms |
| [최신 글](https://pagespeed.web.dev/analysis/https-prof-k-bigdata-kr-2026-10-02-google-cloud-data-agent-kit-ga-html/9e6yulmqmn?form_factor=mobile) | 80 | 100 | 3.6초 | 0 | 30ms |

느린 모바일 연결 실험의 LCP는 권장 2.5초보다 높아 추가 개선 여지가 있다. 실제 사용자 CrUX 표본이 없어 INP를 확인할 수 없으며 TBT를 INP로 간주하지 않는다. Core Web Vitals 전체 통과나 실제 색인 완료를 주장하지 않는다.

### 전체 URL 검증 목록

| URL | HTTP | H1 | SEO 오류 |
|---|---:|---:|---|
| https://prof.k-bigdata.kr/2026/10/02/google-cloud-data-agent-kit-ga.html | 200 | 1 | 없음 |
| https://prof.k-bigdata.kr/2026/09/30/google-intelligent-endpoints-browser-agent-security.html | 200 | 1 | 없음 |
| https://prof.k-bigdata.kr/2026/09/28/aws-resilience-hub-dependency-insights.html | 200 | 1 | 없음 |
| https://prof.k-bigdata.kr/2026/09/23/github-actions-workflow-execution-protections-ga.html | 200 | 1 | 없음 |
| https://prof.k-bigdata.kr/2026/09/21/cloud-storage-intelligence-advisor-ga.html | 200 | 1 | 없음 |
| https://prof.k-bigdata.kr/2026/09/16/github-https-sha1-sunset.html | 200 | 1 | 없음 |
| https://prof.k-bigdata.kr/2026/09/14/aws-lambda-90-minute-managed-instances.html | 200 | 1 | 없음 |
| https://prof.k-bigdata.kr/2026/09/11/bigquery-graph-gql-ga.html | 200 | 1 | 없음 |
| https://prof.k-bigdata.kr/2026/09/09/npm-oidc-trusted-publishing-supply-chain.html | 200 | 1 | 없음 |
| https://prof.k-bigdata.kr/2026/09/07/gpt-6-astra-agent-harness-benchmark.html | 200 | 1 | 없음 |
| https://prof.k-bigdata.kr/2026/09/04/github-copilot-pr-approval-governance.html | 200 | 1 | 없음 |
| https://prof.k-bigdata.kr/2026/09/02/openai-hugging-face-agent-security-lessons.html | 200 | 1 | 없음 |
| https://prof.k-bigdata.kr/2026/02/26/gpt-oss.html | 200 | 1 | 없음 |
| https://prof.k-bigdata.kr/2026/02/25/mcp-vs-tool-calling.html | 200 | 1 | 없음 |
| https://prof.k-bigdata.kr/2026/02/02/api-gateway-cloud-native.html | 200 | 1 | 없음 |
| https://prof.k-bigdata.kr/2026/02/01/devops-overview.html | 200 | 1 | 없음 |
| https://prof.k-bigdata.kr/2026/01/30/n8n-intro.html | 200 | 1 | 없음 |
| https://prof.k-bigdata.kr/2026/01/29/cloud-native-msa-12factor.html | 200 | 1 | 없음 |
| https://prof.k-bigdata.kr/2026/01/28/ingress-nginx-eol.html | 200 | 1 | 없음 |
| https://prof.k-bigdata.kr/2026/01/12/rtx_a6000pro_ai_education.html | 200 | 1 | 없음 |
| https://prof.k-bigdata.kr/2025/05/12/k8s-controller-types.html | 200 | 1 | 없음 |
| https://prof.k-bigdata.kr/2025/05/10/k8s-scheduling-principles.html | 200 | 1 | 없음 |
| https://prof.k-bigdata.kr/2025/05/09/k8s-networking-basics.html | 200 | 1 | 없음 |
| https://prof.k-bigdata.kr/2025/05/08/k8s-pod-lifecycle.html | 200 | 1 | 없음 |
| https://prof.k-bigdata.kr/2025/05/07/k8s-core-components.html | 200 | 1 | 없음 |
| https://prof.k-bigdata.kr/2025/05/06/kubernetes-intro.html | 200 | 1 | 없음 |
| https://prof.k-bigdata.kr/about/ | 200 | 1 | 없음 |
| https://prof.k-bigdata.kr/blog/ | 200 | 1 | 없음 |
| https://prof.k-bigdata.kr/ | 200 | 1 | 없음 |
| https://prof.k-bigdata.kr/research/ | 200 | 1 | 없음 |
| https://prof.k-bigdata.kr/teaching/ | 200 | 1 | 없음 |
