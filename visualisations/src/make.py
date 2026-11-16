"""Rebuild visualisations/le-droit-algerien-en-20-graphiques.html from this repository.

    python visualisations/src/make.py [--repo PATH] [--ref REF] [--skip-extract]

Steps (all read-only on the repository; scratch output goes to visualisations/src/.build/):
  1. git log of REF, streamed: every commit with its author (the text that made the change) and the trailers
     (Law, Kind, Enacted, Published, In-force, Source, Words-changed, Affecting, Act, Provisions)  -> .build/commits.jsonl
  2. git log --name-status of REF, streamed: the files each law commit adds, changes or removes -> .build/names.jsonl
  3. the tree of REF: every article file of the Constitution, the codes, the lois, lois organiques and
     ordonnances                                                                                -> .build/head.tsv
  4. for each act with more than one version (the Code pénal, the Constitution and five others): the article
     files of every version, from the tree of the commit that made it                         -> .build/versions.json
  5. the text of every article blob named in 3 and 4, read one at a time                      -> .build/blobs.jsonl
  6. the tables in data/ (laws.csv, versions.json, paths.json, commits.csv)                    -> .build/repo/
  7. prep.py turns those into .build/data.json; build.py fills page.tpl.html with it.
Works in a blobless or --no-checkout clone: everything is read from git objects, and the blobs a partial
clone lacks (some 15,000 small article files, about 5 MB) are fetched in one batch.
"""
import argparse, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument('--repo', default=os.path.abspath(os.path.join(HERE, '..', '..')))
ap.add_argument('--ref', default=None, help='default: origin/main if present, else HEAD')
ap.add_argument('--out', default=os.path.join(HERE, '..', 'le-droit-algerien-en-20-graphiques.html'))
ap.add_argument('--skip-extract', action='store_true', help='reuse .build/ from a previous run (prep and build only)')
a = ap.parse_args()
B = os.path.join(HERE, '.build')
os.makedirs(os.path.join(B, 'repo'), exist_ok=True)
NOLAZY = dict(os.environ, GIT_NO_LAZY_FETCH='1')
GIT = ['git', '-C', a.repo, '-c', 'core.quotepath=off']
KINDS = ('constitution', 'code', 'loi', 'loi-organique', 'ordonnance')


def git(*args, **kw):
    return subprocess.run([*GIT, *args], check=True, capture_output=True, env=NOLAZY, **kw).stdout


ref = a.ref
if not ref:
    ref = 'origin/main' if subprocess.run([*GIT, 'rev-parse', '--verify', '-q', 'origin/main'], capture_output=True).returncode == 0 else 'HEAD'
sha = git('rev-parse', ref).decode().strip()
print('ref', ref, sha)


def fetch_missing(oids):
    """one batched fetch for the blobs a partial clone does not have yet"""
    oids = sorted(set(oids))
    chk = subprocess.run([*GIT, 'cat-file', '--batch-check'], input=''.join(o + '\n' for o in oids).encode(),
                         capture_output=True, env=NOLAZY).stdout.decode().split('\n')
    missing = [l.split()[0] for l in chk if l.endswith(' missing')]
    if missing:
        print('fetching', len(missing), 'blobs', flush=True)
        subprocess.run([*GIT, '-c', 'fetch.negotiationAlgorithm=noop', 'fetch', 'origin', '--no-tags', '--no-write-fetch-head',
                        '--recurse-submodules=no', '--filter=blob:none', '--stdin'], input=''.join(m + '\n' for m in missing).encode(), check=False)


def read_blobs(oids):
    """yield (oid, text) one blob at a time"""
    p = subprocess.Popen([*GIT, 'cat-file', '--batch'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, env=NOLAZY)
    for oid in oids:
        p.stdin.write((oid + '\n').encode()); p.stdin.flush()
        head = p.stdout.readline().split()
        if len(head) < 3:
            sys.exit('cannot read blob ' + oid)
        data = p.stdout.read(int(head[2])); p.stdout.read(1)
        yield oid, data.decode('utf-8', 'replace')
    p.stdin.close(); p.wait()


def ls_tree(commit, *paths):
    out = []
    for l in git('ls-tree', '-r', commit, '--', *paths).decode('utf-8').split('\n'):
        if not l: continue
        meta, path = l.split('\t', 1)
        _, typ, oid = meta.split()
        if typ == 'blob': out.append((path, oid))
    return out


TRAILERS = ('Law', 'Kind', 'Enacted', 'Published', 'In-force', 'Source', 'Words-changed', 'Affecting', 'Act', 'Provisions', 'Consolidated')
if not a.skip_extract:
    # 1. the history, streamed: one JSON line per commit
    fmt = '%x1e%H%x1f%an%x1f%ae%x1f%aI%x1f%P%x1f%B'
    lg = subprocess.Popen([*GIT, 'log', ref, '--format=' + fmt], stdout=subprocess.PIPE, env=NOLAZY)
    n = 0
    with open(os.path.join(B, 'commits.jsonl'), 'w', encoding='utf-8', newline='\n') as out:
        buf = b''
        def flush(rec):
            global n
            h, an, ae, ad, parents, body = rec.decode('utf-8', 'replace').split('\x1f', 5)
            lines = body.strip('\n').split('\n')
            tr, rest = {}, []
            for l in lines[1:]:
                k, sep, v = l.partition(': ')
                if sep and k in TRAILERS and k not in tr: tr[k] = v.strip()
                else: rest.append(l)
            out.write(json.dumps({'h': h, 'an': an, 'ae': ae, 'ad': ad, 'p': parents.split(), 'subj': lines[0], 't': tr,
                                  'body': '\n'.join(rest).strip()[:6000]}, ensure_ascii=False) + '\n')
            n += 1
        for chunk in iter(lambda: lg.stdout.read(1 << 16), b''):
            buf += chunk
            parts = buf.split(b'\x1e')
            buf = parts.pop()
            for rec in parts:
                if rec.strip(): flush(rec)
        if buf.strip(): flush(buf)
        lg.wait()
    print('commits', n)

    # 2. the files of each law commit (the layout move of 2026-11-11 renamed every folder: kept out)
    laws = set()
    for l in open(os.path.join(B, 'commits.jsonl'), encoding='utf-8'):
        r = json.loads(l)
        if r['t'].get('Kind') in ('law', 'decree', 'publisher'): laws.add(r['h'])
    lg = subprocess.Popen([*GIT, 'log', ref, '--format=@@C %H', '--name-status', '--no-renames'], stdout=subprocess.PIPE, env=NOLAZY)
    cur, files = None, []
    with open(os.path.join(B, 'names.jsonl'), 'w', encoding='utf-8', newline='\n') as out:
        for raw in lg.stdout:
            l = raw.decode('utf-8', 'replace').rstrip('\n')
            if l.startswith('@@C '):
                if cur in laws: out.write(json.dumps({'h': cur, 'f': files}, ensure_ascii=False) + '\n')
                cur, files = l[4:], []
            elif l and cur in laws:
                st, _, path = l.partition('\t')
                files.append([st, path])
        if cur in laws: out.write(json.dumps({'h': cur, 'f': files}, ensure_ascii=False) + '\n')
        lg.wait()

    # 3. the article files at REF
    head = [(p, o) for p, o in ls_tree(ref, *KINDS) if p.endswith('.md') and not p.endswith('/README.md')]
    with open(os.path.join(B, 'head.tsv'), 'w', encoding='utf-8', newline='\n') as out:
        for p, o in head: out.write(f'{p}\t{o}\n')
    print('article files at', ref, len(head))

    # 4. every version of the acts that have more than one: the tree of each commit that wrote them
    names = {}
    for l in open(os.path.join(B, 'names.jsonl'), encoding='utf-8'):
        r = json.loads(l); names[r['h']] = r['f']
    commits = [json.loads(l) for l in open(os.path.join(B, 'commits.jsonl'), encoding='utf-8')]
    per_slug = {}
    for c in commits:
        if c['h'] not in names: continue
        for st, path in names[c['h']]:
            if '/' in path and not path.endswith('README.md'):
                per_slug.setdefault(path.split('/')[0], set()).add(c['h'])
    versions = {}
    for slug, hs in per_slug.items():
        if len(hs) < 2: continue
        rows = []
        for c in commits:
            if c['h'] in hs:
                files = {p.split('/', 1)[1]: o for p, o in ls_tree(c['h'], slug + '/') if not p.endswith('README.md')}
                rows.append({'h': c['h'], 'law': c['t'].get('Law') or c['an'], 'in_force': c['t'].get('In-force'), 'files': files})
        rows.sort(key=lambda r: r['in_force'])
        versions[slug] = rows
    json.dump(versions, open(os.path.join(B, 'versions.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    print('acts with several versions', len(versions), {k: len(v) for k, v in versions.items()})

    # 5. the text of every article blob, one at a time
    oids = {o for _, o in head}
    for rows in versions.values():
        for r in rows: oids.update(r['files'].values())
    fetch_missing(oids)
    with open(os.path.join(B, 'blobs.jsonl'), 'w', encoding='utf-8', newline='\n') as out:
        for oid, text in read_blobs(sorted(oids)):
            out.write(json.dumps({'o': oid, 'x': text}, ensure_ascii=False) + '\n')
    print('blobs', len(oids))

    # 6. the tables
    for f in ('data/laws.csv', 'data/versions.json', 'data/paths.json', 'data/commits.csv', 'data/repo.json'):
        open(os.path.join(B, 'repo', os.path.basename(f)), 'wb').write(git('show', f'{ref}:{f}'))
    # act titles: the first line of each act's README.md
    readmes = [(p, o) for p, o in ls_tree(ref, *KINDS) if p.endswith('/README.md')]
    fetch_missing([o for _, o in readmes])
    with open(os.path.join(B, 'titles.tsv'), 'w', encoding='utf-8', newline='\n') as out:
        for (p, o), (_, text) in zip(readmes, read_blobs([o for _, o in readmes])):
            out.write(p.rsplit('/', 1)[0] + '\t' + text.split('\n', 1)[0].lstrip('# ').strip() + '\t' + (text.split('\n')[2] if text.count('\n') > 2 else '') + '\n')

# 7. prep + build
env = dict(os.environ, HEAD_SHA=sha, HEAD_REF=ref)
subprocess.run([sys.executable, '-X', 'utf8', os.path.join(HERE, 'prep.py'), B], check=True, env=env)
subprocess.run([sys.executable, '-X', 'utf8', os.path.join(HERE, 'build.py'), os.path.join(B, 'data.json'), os.path.abspath(a.out)], check=True)
