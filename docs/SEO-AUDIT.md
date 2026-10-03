# SEO 전면 점검: 수정 전 기준선 (2026-10-03)

## 전체 조사 범위

GitHub `Hyeopgeon-Lee/hyeopgeon-Lee.github.io` main과 실제 운영 사이트를 대조했다. 추적 파일 59개, 정적 검색 페이지 5개, 기술글 26개다. CNAME은 `prof.k-bigdata.kr`, HTTPS 강제 적용, GitHub Pages main 루트의 Jekyll 기본 빌드 방식이다. 정상 URL을 유지한다.

| 항목 | 수정 전 조사 결과 |
| --- | --- |
| URL | `/`, `/about/`, `/research/`, `/teaching/`, `/blog/`; 글은 `/YYYY/MM/DD/slug.html` |
| 전체 글 | `_posts` 26개와 실서비스 sitemap 26개 일치; 최신 글 2026-10-02 Data Agent Kit |
| head | 사용자 정의 include; 한 글만 remote theme single 레이아웃 사용 |
| title | 대부분 고유하지만 게시글 작성자/사이트 맥락 부족, Blog 제목은 일반적 |
| description | Blog는 사이트 공통값, 오래된 글은 제목 중심 자동 excerpt에 의존 |
| canonical | 전체 31개 정상; index.html 중복 표현을 명시적으로 정규화할 필요 |
| OG/Twitter | 전체 기본 메타 존재; 이미지 타입/크기가 사용자 지정 이미지와 무관하게 고정 |
| robots | 전체 Allow와 sitemap 안내 정상; 유지 |
| sitemap | 31 URL 전부 포함; 주요 정적 페이지 lastmod 없음; 글 수정 후 게시일 유지 문제 |
| JSON-LD | 글 BlogPosting와 About ProfilePage 있음; 홈 WebSite, 목록 Blog, breadcrumb 없음; 개인 사이트 publisher를 학과로 표현 |
| 링크 | 목록은 전체 글 정적 HTML 링크; 홈 최신글 및 footer 작성자 링크 정상; 태그 관련글 있음 |
| H1 | networking 글은 테마 제목과 본문 제목 중복; Ingress EOL 글은 여러 H1 |
| 이미지 | 교수 사진과 OG 자산 존재; 오래된 기술글 이미지 5개에 크기 없음, 일부 alt는 image |
| favicon/모바일 | favicon, viewport, ko-KR, 반응형 CSS 있음 |
| 성능 | CSS 47KB, 사진 252KB, OG 561KB; 본문 복사 라이브러리는 동기 로드; 원격 웹폰트 사용 |
| 404 | 잘못된 주소 HTTP 404 정상; 사이트 맞춤 탐색 404 없음 |
| 신규 글 | sitemap 및 HTML 목록 자동; RSS 없음, 수정일 자동 추적 없음 |
| IndexNow | 기존 키 확인 파일 및 main push workflow 존재; 배포 성공 확인 없이 별도 빌드/알림 |
| 인증 | Google/Naver/Bing의 기존 소유 확인 파일 존재; 값 변경/새 인증 생성 금지 |

실서비스 31개 URL의 HTTP, head, H1, JSON-LD, 내부 링크를 전수 수집한 기준선은 작업 산출물 `prof-seo-before.json`에 보관했다. 404와 feed도 직접 요청했다. 페이지 응답시간은 네트워크 관측값이며 Core Web Vitals 현장 지표를 대신하지 않는다.

## 결정

기존 디자인, 콘텐츠, 글 URL을 보존한다. Jekyll을 유지하고 GitHub Actions에서 전체 Git 이력으로 실제 소스 수정일을 산출한다. sitemap/RSS/메타/구조화데이터는 빌드에서 자동 생성한다. 전수 SEO 검증을 통과한 산출물만 Pages에 배포하고 그 뒤 IndexNow를 요청한다. 로그인한 검색 도구의 실제 색인/노출과 현장 LCP·CLS·INP는 운영자가 별도로 확인한다.

## 수정 전 전체 URL 목록

- https://prof.k-bigdata.kr/2025/05/06/kubernetes-intro.html
- https://prof.k-bigdata.kr/2025/05/07/k8s-core-components.html
- https://prof.k-bigdata.kr/2025/05/08/k8s-pod-lifecycle.html
- https://prof.k-bigdata.kr/2025/05/09/k8s-networking-basics.html
- https://prof.k-bigdata.kr/2025/05/10/k8s-scheduling-principles.html
- https://prof.k-bigdata.kr/2025/05/12/k8s-controller-types.html
- https://prof.k-bigdata.kr/2026/01/12/rtx_a6000pro_ai_education.html
- https://prof.k-bigdata.kr/2026/01/28/ingress-nginx-eol.html
- https://prof.k-bigdata.kr/2026/01/29/cloud-native-msa-12factor.html
- https://prof.k-bigdata.kr/2026/01/30/n8n-intro.html
- https://prof.k-bigdata.kr/2026/02/01/devops-overview.html
- https://prof.k-bigdata.kr/2026/02/02/api-gateway-cloud-native.html
- https://prof.k-bigdata.kr/2026/02/25/mcp-vs-tool-calling.html
- https://prof.k-bigdata.kr/2026/02/26/gpt-oss.html
- https://prof.k-bigdata.kr/2026/09/02/openai-hugging-face-agent-security-lessons.html
- https://prof.k-bigdata.kr/2026/09/04/github-copilot-pr-approval-governance.html
- https://prof.k-bigdata.kr/2026/09/07/gpt-6-astra-agent-harness-benchmark.html
- https://prof.k-bigdata.kr/2026/09/09/npm-oidc-trusted-publishing-supply-chain.html
- https://prof.k-bigdata.kr/2026/09/11/bigquery-graph-gql-ga.html
- https://prof.k-bigdata.kr/2026/09/14/aws-lambda-90-minute-managed-instances.html
- https://prof.k-bigdata.kr/2026/09/16/github-https-sha1-sunset.html
- https://prof.k-bigdata.kr/2026/09/21/cloud-storage-intelligence-advisor-ga.html
- https://prof.k-bigdata.kr/2026/09/23/github-actions-workflow-execution-protections-ga.html
- https://prof.k-bigdata.kr/2026/09/28/aws-resilience-hub-dependency-insights.html
- https://prof.k-bigdata.kr/2026/09/30/google-intelligent-endpoints-browser-agent-security.html
- https://prof.k-bigdata.kr/2026/10/02/google-cloud-data-agent-kit-ga.html
- https://prof.k-bigdata.kr/about/
- https://prof.k-bigdata.kr/blog/
- https://prof.k-bigdata.kr/
- https://prof.k-bigdata.kr/research/
- https://prof.k-bigdata.kr/teaching/
