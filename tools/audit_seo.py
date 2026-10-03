"""Audit every canonical page, locally after Jekyll build or on the live site."""
import argparse, concurrent.futures, datetime, json, pathlib, random, time
import urllib.request, urllib.error, urllib.parse
import xml.etree.ElementTree as ET
from lxml import html

BASE = 'https://prof.k-bigdata.kr'
NS = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

def read_live(path):
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(BASE + urllib.parse.quote(path, safe='/%?=&:+'), timeout=40) as r:
            return r.status, r.read(), round(time.perf_counter()-start, 3)
    except urllib.error.HTTPError as e:
        return e.code, e.read(), round(time.perf_counter()-start, 3)

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--site', type=pathlib.Path)
    p.add_argument('--output', type=pathlib.Path, default=pathlib.Path('seo-audit.json'))
    p.add_argument('--strict', action='store_true')
    args = p.parse_args()
    def read(path):
        if not args.site:
            return read_live(path)
        target = args.site / (urllib.parse.unquote(path).lstrip('/') + ('index.html' if path.endswith('/') else ''))
        return (200, target.read_bytes(), 0) if target.exists() else (404, b'', 0)
    status, data, _ = read('/sitemap.xml')
    assert status == 200, 'sitemap not available'
    tree = ET.fromstring(data)
    entries = tree.findall('s:url', NS)
    urls = [x.findtext('s:loc', namespaces=NS) for x in entries]
    errors = []
    if len(urls) != len(set(urls)): errors.append('duplicate sitemap URLs')
    for entry in entries:
        loc = entry.findtext('s:loc', namespaces=NS)
        if not loc.startswith(BASE + '/'): errors.append('wrong domain: ' + loc)
        mod = entry.findtext('s:lastmod', namespaces=NS)
        if mod:
            try:
                d = datetime.datetime.fromisoformat(mod.replace('Z','+00:00'))
                if d.date() > datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).date():
                    errors.append('future lastmod: '+loc)
            except ValueError: errors.append('invalid lastmod: '+loc)
    def audit(url):
        path = urllib.parse.urlsplit(url).path
        status, data, elapsed = read(path)
        doc = html.fromstring(data)
        one = lambda xp: doc.xpath('string(' + xp + ')').strip()
        title = one('//title')
        desc = one('//meta[@name="description"]/@content')
        canonical = one('//link[@rel="canonical"]/@href')
        blocks, types = [], []
        for s in doc.xpath('//script[@type="application/ld+json"]/text()'):
            obj = json.loads(s)
            blocks.append(obj)
            types.extend(x.get('@type') for x in obj.get('@graph', [obj]))
        issues = []
        if status != 200: issues.append('HTTP '+str(status))
        if len(doc.xpath('//title')) != 1 or not title: issues.append('title')
        if len(doc.xpath('//meta[@name="description"]')) != 1 or not desc: issues.append('description')
        if canonical != url or len(doc.xpath('//link[@rel="canonical"]')) != 1: issues.append('canonical')
        if len(doc.xpath('//h1')) != 1: issues.append('H1')
        if 'noindex' in one('//meta[@name="robots"]/@content'): issues.append('noindex in sitemap')
        for name in ['title','description','type','url','image']:
            if not one('//meta[@property="og:'+name+'"]/@content'): issues.append('og:'+name)
        for name in ['card','title','description','image']:
            if not one('//meta[@name="twitter:'+name+'"]/@content'): issues.append('twitter:'+name)
        if not blocks: issues.append('JSON-LD')
        if path.endswith('.html'):
            if 'BlogPosting' not in types or 'BreadcrumbList' not in types: issues.append('article schema')
            if not doc.xpath('//a[@href="/about/"]'): issues.append('author link')
        if not one('//html/@lang').startswith('ko'): issues.append('lang')
        for img in doc.xpath('//img'):
            if img.get('alt') is None: issues.append('image alt')
            if not img.get('width') or not img.get('height'): issues.append('image dimensions')
        return {'url':url,'status':status,'seconds':elapsed,'bytes':len(data),'title':title,
                'description':desc,'canonical':canonical,'h1':len(doc.xpath('//h1')),
                'schema':types,'internal_links':len(doc.xpath('//a[starts-with(@href,"/")]')),
                'issues':issues}
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        pages = list(pool.map(audit, urls))
    for field in ['title','description']:
        values = [x[field] for x in pages]
        if len(set(values)) != len(values): errors.append('duplicate '+field)
    posts = [x for x in urls if urllib.parse.urlsplit(x).path.endswith('.html')]
    blog = html.fromstring(read('/blog/')[1])
    blog_links = {urllib.parse.urljoin(BASE, x) for x in blog.xpath('//a/@href')}
    if not set(posts) <= blog_links: errors.append('posts missing from blog HTML links')
    required = [BASE+x for x in ['/','/about/','/research/','/teaching/','/blog/']]
    if not set(required) <= set(urls): errors.append('missing primary pages')
    robots = read('/robots.txt')
    if robots[0] != 200 or b'Sitemap: https://prof.k-bigdata.kr/sitemap.xml' not in robots[1]: errors.append('robots')
    feed = read('/feed.xml')
    feed_count = 0
    if feed[0] == 200:
        ft = ET.fromstring(feed[1])
        feed_count = len(ft.findall('.//item')) or len(ft.findall('{http://www.w3.org/2005/Atom}entry'))
        feed_links = {item.findtext('link') for item in ft.findall('.//item')}
        if not set(posts) <= feed_links: errors.append('posts missing from RSS')
    else: errors.append('feed missing')
    if args.site:
        excluded = ['README.md','tools/audit_seo.py','docs/SEO-OPERATIONS.md']
        if any((args.site / p).exists() for p in excluded): errors.append('development files published')
    missing_status = read('/seo-missing-check-20261003/')[0]
    if missing_status != 404: errors.append('soft 404')
    report = {'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'sitemap_urls':len(urls),'posts':len(posts),'feed_entries':feed_count,
              'missing_url_status':missing_status,'errors':errors,'pages':pages}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2), encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='pages'}, ensure_ascii=False))
    print('Page issues:', [(x['url'],x['issues']) for x in pages if x['issues']])
    if args.strict and (errors or any(x['issues'] for x in pages)): raise SystemExit(1)

if __name__ == '__main__': main()
