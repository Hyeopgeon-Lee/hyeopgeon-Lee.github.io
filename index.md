---
layout: default
title: "이협건 교수의 기술 노트"
author_profile: true
---

💡 **안녕하세요.**

저는 **한국폴리텍대학 서울강서캠퍼스 빅데이터소프트웨어공학과**에서 재직 중인 **이협건 교수**입니다.  
클라우드, 인공지능, 빅데이터 분야의 실무 중심 교육과 연구개발을 통해  
**졸업 후 바로 취업 가능한 역량**을 갖출 수 있도록 학생들을 교육하고 있습니다.

> 최신 기술 트렌드와 실습 중심 콘텐츠를 기반으로  
> 함께 성장하는 교육 커뮤니티를 만들어가고자 합니다.

{: .notice--info}

---

## 이번 주 주요 기술 이슈

{% assign latest_post = site.posts | first %}
{% if latest_post %}
<div class="post-card">
  <div class="post-card__meta">NEW · {{ latest_post.date | date: "%Y-%m-%d" }}</div>
  <a class="post-card__title" href="{{ latest_post.url | relative_url }}">{{ latest_post.title }}</a>
  {% if latest_post.excerpt %}
  <div class="post-card__excerpt">{{ latest_post.excerpt | strip_html | truncate: 200 }}</div>
  {% endif %}
</div>
{% endif %}

---

## 최근 글

{% for post in site.posts offset: 1 limit: 9 %}
<div class="post-card">
  <a class="post-card__title" href="{{ post.url | relative_url }}">{{ post.title }}</a>
  <div class="post-card__meta">{{ post.date | date: "%Y-%m-%d" }}</div>
  {% if post.excerpt %}
  <div class="post-card__excerpt">{{ post.excerpt | strip_html | truncate: 160 }}</div>
  {% endif %}
</div>
{% endfor %}
