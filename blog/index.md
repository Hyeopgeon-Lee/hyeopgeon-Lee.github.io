---
layout: default
title: "기술 블로그"
permalink: /blog/
---

<div class="blog-intro">
  <p class="eyebrow">TECHNICAL NOTES</p>
  <h1>기술 블로그</h1>
  <p>AI, 클라우드, 빅데이터, 소프트웨어 엔지니어링을 직접 탐구하고 가르치며 정리한 기록입니다.</p>
</div>

<div class="blog-list-heading">
  <h2>전체 글</h2>
  <span>{{ site.posts | size }} Articles</span>
</div>

{% for post in site.posts %}
<div class="post-card">
  <a class="post-card__title" href="{{ post.url | relative_url }}">{{ post.title }}</a>
  <div class="post-card__meta">{{ post.date | date: "%Y-%m-%d" }}</div>
  {% if post.excerpt %}
  <div class="post-card__excerpt">{{ post.excerpt | strip_html | truncate: 180 }}</div>
  {% endif %}
</div>
{% endfor %}
