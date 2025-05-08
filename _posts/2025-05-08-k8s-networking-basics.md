--- 
layout: post
title: "(4장)쿠버네티스 네트워킹의 기초: Pod는 어떻게 통신할까?"
date: 2025-05-08
---

# 🌐 쿠버네티스 네트워킹의 기초: Pod는 어떻게 통신할까?

쿠버네티스를 처음 접한 사람들에게 가장 헷갈리는 부분 중 하나는 바로 **네트워킹**입니다. 
Pod 간 통신은 어떻게 되는지, 외부에서 접근은 어떤 방식으로 처리되는지, 
`ClusterIP`, `DNS`, `CNI 플러그인`이란 단어들은 무엇을 의미하는지, 이 글에서 자세히 알아보겠습니다.

...

📎 참고자료:
- https://kubernetes.io/docs/concepts/services-networking/
- https://www.weave.works/
- https://cilium.io/
- 한국폴리텍대학 강의자료
