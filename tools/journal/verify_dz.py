"""Second pass over the amended versions: every paragraph of every changed article must occur either in the gazette
issue's own text (whitespace-normalised) or in the article's earlier text. Prints mismatches; exit 1 if any."""
import json
import re
import sys
import build_dz as B
import journal_lib as J


def flat(s):
    s = J.norm(s).replace('«', '').replace('»', '')
    return re.sub(r'\s+', ' ', s)


c = json.loads((B.ROOT / 'corpus.json').read_text(encoding='utf-8'))
for f in sorted((B.ROOT / 'corpus.d').glob('*.json')):
    c['acts'] += json.loads(f.read_text(encoding='utf-8'))['acts']
bad = 0
for act in c['acts']:
    for i, v in enumerate(act['versions']):
        if 'changes' not in v or 'joradp' not in v['source_url']:
            continue
        prev = B.state(dict(act, versions=act['versions'][:i]))
        y, n = re.search(r'F(\d{4})(\d{3})\.pdf', v['source_url']).groups()
        gaz = flat(' '.join(J.paragraphs(B.pdf(int(y), int(n)))))
        checked = 0
        for k, u in v['changes'].items():
            if u is None:
                continue
            old = flat(prev.get(k, {}).get('text', ''))
            for p in u['text'].split('\n')[1:]:
                if not p:
                    continue
                fp = flat(p)
                checked += 1
                if fp not in gaz and fp not in old:
                    bad += 1
                    print(act['slug'], v['from'], k, '|', p[:160])
        print(act['slug'], v['from'], 'paragraphs checked', checked)
sys.exit(1 if bad else 0)
