"""Print, for one amending law, each article left unresolved: the gazette's paragraphs and the earlier text."""
import json
import sys
import build_dz as B
import journal_lib as J
y, n, num = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
c = json.loads((B.ROOT / 'corpus.json').read_text(encoding='utf-8'))
act = next(a for a in c['acts'] if a['slug'] == 'code-penal')
idx = [v['source_url'] for v in act['versions']].index(B.url(y, n)) if B.url(y, n) in [v['source_url'] for v in act['versions']] else len(act['versions'])
act = dict(act, versions=act['versions'][:idx])
prev = B.state(act)
a = J.slice_act(J.paragraphs(B.pdf(y, n)), r'^(Loi|Ordonnance) n° ' + num + r' du ')
new, rep, part = J.operations(a, r'66-156')
ch, un = J.apply_amendment(prev, new, rep)
for k in (sys.argv[4:] or un):
    print('=====', k)
    print('NEW:', '\n     '.join(new[k][1]))
    print('BAD:', un.get(k))
    print('OLD:', prev.get(k, {}).get('text', '')[:1500])
