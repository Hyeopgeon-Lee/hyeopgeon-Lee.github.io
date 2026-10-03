"""Notify only after the exact validated revision is publicly available."""
import json, pathlib, subprocess, time, urllib.request, xml.etree.ElementTree as ET
from lxml import html

BASE = 'https://prof.k-bigdata.kr'
ROOT = pathlib.Path(__file__).resolve().parents[1]

def main():
    revision = subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    for attempt in range(18):
        with urllib.request.urlopen(BASE+'/?deployment='+revision,timeout=30) as r:
            document = html.fromstring(r.read())
        if document.xpath('//meta[@name="site-build"]/@content') == [revision]: break
        time.sleep(10)
    else: raise RuntimeError('Expected site revision was not published; no IndexNow request sent')
    subprocess.run(['python',str(ROOT/'tools/audit_seo.py'),'--strict'],cwd=ROOT,check=True)
    # IndexNow keys are PUBLIC domain-verification identifiers, not API credentials.
    key_file = next(ROOT.glob('bc*.txt'))
    key = key_file.read_text(encoding='utf-8').strip()
    with urllib.request.urlopen(BASE+'/'+key_file.name,timeout=30) as r:
        assert r.read().decode().strip()==key, 'IndexNow public key file mismatch'
    with urllib.request.urlopen(BASE+'/sitemap.xml',timeout=30) as r:
        tree=ET.fromstring(r.read())
    urls=[n.text for n in tree.findall('{http://www.sitemaps.org/schemas/sitemap/0.9}url/{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
    payload={'host':'prof.k-bigdata.kr','key':key,'keyLocation':BASE+'/'+key_file.name,'urlList':urls}
    req=urllib.request.Request('https://api.indexnow.org/indexnow',data=json.dumps(payload).encode(),
                               headers={'Content-Type':'application/json; charset=utf-8'},method='POST')
    with urllib.request.urlopen(req,timeout=30) as r:
        assert r.status in (200,202), 'IndexNow rejected notification'
        print('IndexNow accepted',len(urls),'URLs; HTTP',r.status)

if __name__=='__main__': main()
