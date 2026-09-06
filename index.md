---
layout: default
title: "이협건 교수 | AI · Cloud · Big Data"
description: "한국폴리텍대학 서울강서캠퍼스 이협건 교수의 연구·교육 포트폴리오와 기술 블로그"
---

<section class="landing-hero" aria-labelledby="hero-title">
  <div class="hero-copy">
    <p class="eyebrow">AI · CLOUD · BIG DATA · SOFTWARE ENGINEERING</p>
    <h1 id="hero-title">기술을 연구하고,<br><span>가르치고, 기록합니다.</span></h1>
    <p class="hero-lead">현장의 기술을 교육으로 연결하고, 학생들의 가능성을 실무 역량으로 바꿉니다.</p>

    <div class="hero-identity">
      <strong>이협건 교수</strong>
      <span>한국폴리텍대학 서울강서캠퍼스<br>빅데이터소프트웨어공학과</span>
    </div>

    <div class="hero-actions">
      <a class="button button--primary" href="{{ '/blog/' | relative_url }}">기술 블로그 보기 <span aria-hidden="true">→</span></a>
      <a class="button button--secondary" href="https://apply.jinhakapply.com/Notice/5041044/A" target="_blank" rel="noopener noreferrer">수시 1차 원서접수 <span aria-hidden="true">↗</span></a>
    </div>
  </div>

  <div class="hero-visual" aria-label="이협건 교수 프로필">
    <div class="portrait-frame">
      <img src="{{ site.author.avatar | relative_url }}" alt="이협건 교수" width="480" height="600">
    </div>
    <div class="hero-badge">
      <span class="status-dot" aria-hidden="true"></span>
      <span><strong>Professor</strong> &amp; Technology Educator</span>
    </div>
  </div>
</section>

<section class="section-block expertise-section" id="expertise" aria-labelledby="expertise-title">
  <div class="section-heading">
    <div>
      <p class="eyebrow">RESEARCH &amp; TEACHING AREAS</p>
      <h2 id="expertise-title">연구와 교육의 중심 분야</h2>
    </div>
    <p>빠르게 변하는 기술을 원리부터 실습까지 연결해<br>현장에서 작동하는 지식으로 만듭니다.</p>
  </div>

  <div class="expertise-grid">
    <article class="expertise-card">
      <div class="expertise-icon" aria-hidden="true">
        <svg viewBox="0 0 24 24" role="img"><path d="M12 3a5 5 0 0 0-3.9 8.13A4 4 0 0 0 9 19h6a4 4 0 0 0 .9-7.87A5 5 0 0 0 12 3Z"/><path d="M9 14h6M10 17h4"/></svg>
      </div>
      <span class="card-number">01</span>
      <h3>Artificial Intelligence</h3>
      <p>생성형 AI와 AI 에이전트의 원리, 활용, 안전한 시스템 설계를 탐구합니다.</p>
      <span class="card-keywords">Generative AI · AI Agent</span>
    </article>

    <article class="expertise-card">
      <div class="expertise-icon" aria-hidden="true">
        <svg viewBox="0 0 24 24" role="img"><ellipse cx="12" cy="5" rx="7" ry="3"/><path d="M5 5v6c0 1.66 3.13 3 7 3s7-1.34 7-3V5M5 11v6c0 1.66 3.13 3 7 3s7-1.34 7-3v-6"/></svg>
      </div>
      <span class="card-number">02</span>
      <h3>Big Data</h3>
      <p>대규모 데이터를 수집·처리·분석하는 데이터 엔지니어링 역량을 다룹니다.</p>
      <span class="card-keywords">Hadoop · Spark · Data Pipeline</span>
    </article>

    <article class="expertise-card">
      <div class="expertise-icon" aria-hidden="true">
        <svg viewBox="0 0 24 24" role="img"><path d="M7 18h10a4 4 0 0 0 .72-7.94A6 6 0 0 0 6.2 8.4 4.8 4.8 0 0 0 7 18Z"/><path d="M9 14h6M12 11v6"/></svg>
      </div>
      <span class="card-number">03</span>
      <h3>Cloud Native</h3>
      <p>클라우드 환경에서 확장 가능하고 안정적인 서비스 아키텍처를 설계합니다.</p>
      <span class="card-keywords">Kubernetes · MSA · DevOps</span>
    </article>

    <article class="expertise-card">
      <div class="expertise-icon" aria-hidden="true">
        <svg viewBox="0 0 24 24" role="img"><path d="m8 8-4 4 4 4M16 8l4 4-4 4M14 4l-4 16"/></svg>
      </div>
      <span class="card-number">04</span>
      <h3>Software Engineering</h3>
      <p>좋은 구조와 협업 방식을 바탕으로 유지보수 가능한 소프트웨어를 만듭니다.</p>
      <span class="card-keywords">Architecture · CI/CD · Quality</span>
    </article>
  </div>
</section>

{% assign latest_post = site.posts | first %}
{% if latest_post %}
<section class="section-block latest-section" aria-labelledby="latest-title">
  <div class="section-heading section-heading--compact">
    <div>
      <p class="eyebrow">LATEST TECHNOLOGY</p>
      <h2 id="latest-title">지금 주목하는 기술</h2>
    </div>
  </div>

  <article class="featured-post">
    <div class="featured-post__accent" aria-hidden="true">
      <span>LATEST</span>
      <strong>{{ latest_post.date | date: "%m.%d" }}</strong>
    </div>
    <div class="featured-post__body">
      <div class="post-meta"><span class="new-label">NEW</span><time datetime="{{ latest_post.date | date_to_xmlschema }}">{{ latest_post.date | date: "%Y.%m.%d" }}</time></div>
      <h3><a href="{{ latest_post.url | relative_url }}">{{ latest_post.title }}</a></h3>
      {% if latest_post.excerpt %}
        <p>{{ latest_post.excerpt | strip_html | truncate: 220 }}</p>
      {% endif %}
      <a class="text-link" href="{{ latest_post.url | relative_url }}">글 읽기 <span aria-hidden="true">→</span></a>
    </div>
  </article>
</section>
{% endif %}

<section class="section-block recent-section" aria-labelledby="recent-title">
  <div class="section-heading">
    <div>
      <p class="eyebrow">RECENT NOTES</p>
      <h2 id="recent-title">최근 기술 글</h2>
    </div>
    <a class="section-link" href="{{ '/blog/' | relative_url }}">전체 글 보기 <span aria-hidden="true">→</span></a>
  </div>

  <div class="post-grid">
    {% for post in site.posts offset: 1 limit: 6 %}
    <article class="post-grid-card">
      <div class="post-meta"><span>TECH NOTE</span><time datetime="{{ post.date | date_to_xmlschema }}">{{ post.date | date: "%Y.%m.%d" }}</time></div>
      <h3><a href="{{ post.url | relative_url }}">{{ post.title }}</a></h3>
      {% if post.excerpt %}
        <p>{{ post.excerpt | strip_html | truncate: 125 }}</p>
      {% endif %}
      <a class="card-arrow" href="{{ post.url | relative_url }}" aria-label="{{ post.title }} 읽기">→</a>
    </article>
    {% endfor %}
  </div>
</section>

<section class="section-block profile-summary" aria-labelledby="profile-title">
  <div class="summary-intro">
    <p class="eyebrow">PROFILE</p>
    <h2 id="profile-title">배움이 현장으로<br>이어지도록</h2>
    <p>기술을 이해하는 데서 그치지 않고 직접 설계하고 구현하는 경험을 중요하게 생각합니다.</p>
  </div>

  <div class="summary-list">
    <article class="summary-item" id="about">
      <span>01</span>
      <div>
        <h3>About</h3>
        <p>한국폴리텍대학 서울강서캠퍼스에서 빅데이터소프트웨어 분야의 교육과 연구를 수행하고 있습니다.</p>
      </div>
    </article>
    <article class="summary-item" id="teaching">
      <span>02</span>
      <div>
        <h3>Teaching</h3>
        <p>프로젝트와 실습을 중심으로, 졸업 후 바로 활용할 수 있는 문제 해결 역량을 함께 키웁니다.</p>
        <a class="summary-link" href="{{ '/teaching/' | relative_url }}">교육과 실적 보기 <span aria-hidden="true">→</span></a>
      </div>
    </article>
    <article class="summary-item" id="research">
      <span>03</span>
      <div>
        <h3>Research</h3>
        <p>AI, 클라우드 네이티브, 빅데이터, 소프트웨어 엔지니어링의 접점에서 새로운 가능성을 연구합니다.</p>
        <a class="summary-link" href="{{ '/research/' | relative_url }}">연구실적 보기 <span aria-hidden="true">→</span></a>
      </div>
    </article>
  </div>
</section>
