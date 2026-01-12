---
layout: default
title: "기술 블로그"
permalink: /blog/
author_profile: true
---

📚 이곳은 이협건 교수의 기술 블로그입니다.  
클라우드, 인공지능, 빅데이터 관련 실습 기반 강의와 기술 노트를 공유합니다.

---

## 전체 글

{% for post in site.posts %}
<div class="post-card">
  <a class="post-card__title" href="{{ post.url | relative_url }}">{{ post.title }}</a>
  <div class="post-card__meta">{{ post.date | date: "%Y-%m-%d" }}</div>
  {% if post.excerpt %}
  <div class="post-card__excerpt">{{ post.excerpt | strip_html | truncate: 180 }}</div>
  {% endif %}
</div>
{% endfor %}
