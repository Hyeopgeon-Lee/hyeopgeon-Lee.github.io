"""Build metadata from Git history; never invent publication dates or commit files."""
import datetime, json, pathlib, subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]
def modified(paths):
    value = subprocess.check_output(['git','log','-1','--format=%cI','--',*paths],cwd=ROOT,text=True).strip()
    return value or None

def main():
    # Shared changes alter the article's structured data, author context or related links.
    shared = ['_includes/head.html','_includes/seo-schema.html','_includes/post-footer.html',
              '_layouts/default.html','_config.yml']
    tracked = subprocess.check_output(['git','ls-files','-z','*.md','*.html'],cwd=ROOT,encoding='utf-8').split('\0')[:-1]
    sources = [ROOT / p for p in tracked
               if not p.startswith(('_includes/','_layouts/'))
               and (ROOT / p).read_text(encoding='utf-8').startswith('---')]
    metadata = {}
    for source in sources:
        if not source.is_file(): continue
        path = source.relative_to(ROOT).as_posix()
        dependencies = [path,*shared]
        if path in ('index.md','blog/index.md'):
            dependencies.append('_posts')
        value = modified(dependencies)
        if value: metadata[path] = value
    target = ROOT / '_data/seo_dates.json'
    target.parent.mkdir(exist_ok=True)
    target.write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding='utf-8')
    revision = subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    (ROOT / '_data/seo_build.json').write_text(json.dumps({'revision':revision}),encoding='utf-8')
    print('Git modification dates:',len(metadata))

if __name__ == '__main__': main()
