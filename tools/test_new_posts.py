"""Exercise future Markdown/HTML publication without publishing test content."""
import json, pathlib, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
fixtures = {
    '2000-01-01-seo-markdown-fixture.md': '''---
title: "자동 SEO 검증용 Markdown 글"
date: 2000-01-01 09:00:00 +0900
tags: [SEO검증]
---
Markdown 파일만 추가한 경우의 자동 요약과 메타데이터를 확인하는 테스트 본문입니다.

## 확인할 내용
이 글은 배포되지 않는 테스트 문서입니다.
''',
    '2000-01-02-seo-html-fixture.html': '''---
title: "자동 SEO 검증용 HTML 글"
date: 2000-01-02 09:00:00 +0900
tags: [SEO검증]
---
<p>HTML 파일만 추가한 경우의 자동 요약과 메타데이터를 확인하는 별도의 테스트 본문입니다.</p>
<h2>확인할 내용</h2><p>이 글은 배포되지 않는 테스트 문서입니다.</p>
'''
}
paths = [ROOT / '_posts' / name for name in fixtures]
assert not any(p.exists() for p in paths), 'Fixture name already exists; do not overwrite'
try:
    for name, content in fixtures.items():
        (ROOT / '_posts' / name).write_text(content,encoding='utf-8')
    with tempfile.TemporaryDirectory(prefix='jekyll-seo-fixture-') as tmp:
        destination = pathlib.Path(tmp) / 'site'
        report = pathlib.Path(tmp) / 'audit.json'
        subprocess.run(['bundle','exec','jekyll','build','--destination',str(destination)],cwd=ROOT,check=True)
        subprocess.run([sys.executable,str(ROOT/'tools/audit_seo.py'),'--site',str(destination),
                        '--strict','--output',str(report)],cwd=ROOT,check=True)
        data=json.loads(report.read_text(encoding='utf-8'))
        locations={p['url'] for p in data['pages']}
        for path in ['/2000/01/01/seo-markdown-fixture.html','/2000/01/02/seo-html-fixture.html']:
            assert 'https://prof.k-bigdata.kr'+path in locations
        print('New Markdown/HTML posts automatically pass sitemap, feed, metadata, schema and H1 checks')
finally:
    for p in paths:
        if p.exists(): p.unlink()
