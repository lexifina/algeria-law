"""Compute every number the page shows, from .build/ (written by make.py), into .build/data.json.

    python prep.py <.build folder>

Everything is read from the files make.py extracted from git: the commits and their trailers, the files each law
commit wrote, the article files at the reference commit and in every version of the acts that have several, and the
tables in data/. Nothing is fetched from the web.
"""
import collections, csv, datetime as dt, json, os, re, statistics, sys

B = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), '.build')
SHA = os.environ.get('HEAD_SHA', '')


def jl(name):
    for line in open(os.path.join(B, name), encoding='utf-8'):
        yield json.loads(line)


commits = list(jl('commits.jsonl'))
names = {r['h']: r['f'] for r in jl('names.jsonl')}
laws = {r['key']: r for r in csv.DictReader(open(os.path.join(B, 'repo', 'laws.csv'), encoding='utf-8'))}
paths = json.load(open(os.path.join(B, 'repo', 'paths.json'), encoding='utf-8'))['paths']
ccsv = list(csv.DictReader(open(os.path.join(B, 'repo', 'commits.csv'), encoding='utf-8')))
VERS = json.load(open(os.path.join(B, 'versions.json'), encoding='utf-8'))
head = [l.rstrip('\n').split('\t') for l in open(os.path.join(B, 'head.tsv'), encoding='utf-8')]
titles = {}
for line in open(os.path.join(B, 'titles.tsv'), encoding='utf-8'):
    f, t, meta = line.rstrip('\n').split('\t')
    titles[f] = t
X = {r['o']: r['x'] for r in jl('blobs.jsonl')}
D = lambda s: dt.date.fromisoformat(s)


def body(t):
    """an article file without its '# Art. N' heading line"""
    return '\n'.join(l for l in t.split('\n') if not l.startswith('# '))


def words(t):
    return len(re.findall(r'\w+', body(t)))


def label(t, f):
    first = t.split('\n', 1)[0]
    return first[2:].strip() if first.startswith('# ') else f.replace('.md', '')


def first_sentence(t, n=190):
    s = re.sub(r'\s+', ' ', body(t)).strip()
    m = re.match(r'(.{30,}?[.;:])(?:\s|$)', s)
    s = m.group(1) if m and len(m.group(1)) <= n else s
    return s if len(s) <= n else s[:n - 1].rsplit(' ', 1)[0] + '…'


# ------------------------------------------------------------------------------------------------ short names
# [French, English] for every act; used for labels (the page names acts in its own language)
NAMES = {
    'constitution/constitution': ['Constitution', 'Constitution'],
    'code/code-penal': ['Code pénal', 'Penal Code'],
    'code/code-procedure-penale': ['Code de procédure pénale', 'Code of Criminal Procedure'],
    'code/code-procedure-civile-administrative': ['Code de procédure civile et administrative', 'Code of Civil and Administrative Procedure'],
    'code/code-justice-militaire': ['Code de justice militaire', 'Code of Military Justice'],
    'code/code-organisation-penitentiaire': ['Code de l’organisation pénitentiaire', 'Prison Organisation Code'],
    'code/code-route': ['Code de la route', 'Highway Code'],
    'loi-organique/2004/04-11': ['Statut de la magistrature (2004)', 'Statute of the judiciary (2004)'],
    'loi-organique/2004/04-12': ['Conseil supérieur de la magistrature (2004)', 'High Council of the Judiciary (2004)'],
    'loi-organique/2005/05-11': ['Organisation judiciaire (2005)', 'Judicial organisation (2005)'],
    'loi-organique/2007/07-07': ['Report des élections locales', 'Postponement of local elections'],
    'loi-organique/2011/11-12': ['Cour suprême', 'Supreme Court'],
    'loi-organique/2012/12-01': ['Régime électoral (2012)', 'Electoral system (2012)'],
    'loi-organique/2012/12-02': ['Incompatibilités parlementaires', 'Parliamentary incompatibilities'],
    'loi-organique/2012/12-03': ['Représentation des femmes', 'Women’s representation'],
    'loi-organique/2012/12-04': ['Partis politiques (2012)', 'Political parties (2012)'],
    'loi-organique/2012/12-05': ['Information (2012)', 'Information (2012)'],
    'loi-organique/2016/16-10': ['Régime électoral (2016)', 'Electoral system (2016)'],
    'loi-organique/2016/16-11': ['Surveillance des élections (2016)', 'Election monitoring body (2016)'],
    'loi-organique/2018/18-15': ['Lois de finances', 'Finance laws'],
    'loi-organique/2018/18-16': ['Exception d’inconstitutionnalité', 'Plea of unconstitutionality'],
    'loi-organique/2018/18-17': ['Académie de la langue amazighe', 'Amazigh Language Academy'],
    'loi-organique/2019/19-07': ['Autorité des élections (2019)', 'Election authority (2019)'],
    'loi-organique/2022/22-10': ['Organisation judiciaire (2022)', 'Judicial organisation (2022)'],
    'loi-organique/2022/22-12': ['Conseil supérieur de la magistrature (2022)', 'High Council of the Judiciary (2022)'],
    'loi-organique/2022/22-19': ['Saisine de la Cour constitutionnelle', 'Referrals to the Constitutional Court'],
    'loi-organique/2023/23-14': ['Information (2023)', 'Information (2023)'],
    'loi-organique/2026/26-03': ['Statut de la magistrature (2026)', 'Statute of the judiciary (2026)'],
    'loi-organique/2026/26-08': ['Partis politiques (2026)', 'Political parties (2026)'],
    'loi/2002/02-01': ['Électricité et gaz', 'Electricity and gas'],
    'loi/2002/02-08': ['Villes nouvelles', 'New towns'],
    'loi/2002/02-09': ['Personnes handicapées (2002)', 'Persons with disabilities (2002)'],
    'loi/2003/03-01': ['Tourisme', 'Tourism'],
    'loi/2003/03-02': ['Plages', 'Beaches'],
    'loi/2003/03-03': ['Zones d’expansion touristique', 'Tourist expansion zones'],
    'loi/2003/03-09': ['Armes chimiques', 'Chemical weapons'],
    'loi/2003/03-10': ['Environnement', 'Environment'],
    'loi/2004/04-02': ['Pratiques commerciales', 'Commercial practices'],
    'loi/2004/04-03': ['Zones de montagne', 'Mountain areas'],
    'loi/2004/04-04': ['Normalisation', 'Standardisation'],
    'loi/2004/04-06': ['Architecture (abrogation partielle)', 'Architecture (partial repeal)'],
    'loi/2004/04-07': ['Chasse', 'Hunting'],
    'loi/2004/04-08': ['Activités commerciales', 'Commercial activities'],
    'loi/2004/04-09': ['Énergies renouvelables', 'Renewable energy'],
    'loi/2004/04-10': ['Éducation physique et sports', 'Physical education and sport'],
    'loi/2004/04-18': ['Stupéfiants', 'Narcotics'],
    'loi/2004/04-19': ['Placement des travailleurs', 'Job placement'],
    'loi/2004/04-20': ['Risques majeurs (2004)', 'Major hazards (2004)'],
    'loi/2005/05-01': ['Blanchiment d’argent', 'Money laundering'],
    'loi/2005/05-03': ['Semences et obtentions végétales', 'Seeds and plant varieties'],
    'loi/2005/05-07': ['Hydrocarbures (2005)', 'Hydrocarbons (2005)'],
    'loi/2005/05-12': ['Eau', 'Water'],
    'loi/2006/06-01': ['Corruption', 'Corruption'],
    'loi/2006/06-05': ['Titrisation des créances', 'Securitisation'],
    'loi/2006/06-06': ['Orientation de la ville', 'Urban policy'],
    'loi/2006/06-11': ['Capital investissement', 'Private equity'],
    'loi/2006/06-21': ['Promotion de l’emploi', 'Employment incentives'],
    'loi/2007/07-01': ['Coopératives d’épargne et de crédit', 'Savings and credit cooperatives'],
    'loi/2007/07-02': ['Titres de propriété', 'Land titles'],
    'loi/2007/07-06': ['Espaces verts', 'Green spaces'],
    'loi/2007/07-11': ['Système comptable financier', 'Financial accounting system'],
    'loi/2008/08-04': ['Éducation nationale', 'National education'],
    'loi/2008/08-07': ['Formation professionnelle', 'Vocational training'],
    'loi/2008/08-11': ['Étrangers', 'Foreigners'],
    'loi/2008/08-15': ['Conformité des constructions', 'Building compliance'],
    'loi/2008/08-16': ['Orientation agricole', 'Agricultural policy'],
    'loi/2009/09-03': ['Protection du consommateur', 'Consumer protection'],
    'loi/2009/09-04': ['Infractions liées aux TIC', 'ICT offences'],
    'loi/2010/10-01': ['Expertise comptable', 'Accounting professions'],
    'loi/2010/10-03': ['Terres agricoles de l’État', 'State farmland'],
    'loi/2010/10-12': ['Personnes âgées', 'Older persons'],
    'loi/2011/11-02': ['Aires protégées', 'Protected areas'],
    'loi/2011/11-03': ['Cinématographie (2011)', 'Cinema (2011)'],
    'loi/2011/11-04': ['Promotion immobilière', 'Property development'],
    'loi/2011/11-10': ['Commune', 'Municipalities'],
    'loi/2012/12-06': ['Associations', 'Associations'],
    'loi/2012/12-07': ['Wilaya', 'Wilayas'],
    'loi/2013/13-07': ['Profession d’avocat', 'Legal profession'],
    'loi/2014/14-03': ['Documents de voyage', 'Travel documents'],
    'loi/2014/14-04': ['Audiovisuel (2014)', 'Broadcasting (2014)'],
    'loi/2014/14-05': ['Mines', 'Mining'],
    'loi/2014/14-06': ['Service national', 'National service'],
    'loi/2014/14-07': ['Ressources biologiques', 'Biological resources'],
    'loi/2015/15-01': ['Fonds de la pension alimentaire', 'Maintenance fund'],
    'loi/2015/15-02': ['Mutuelles sociales', 'Mutual societies'],
    'loi/2015/15-03': ['Modernisation de la justice', 'Modernising justice'],
    'loi/2015/15-04': ['Signature électronique', 'Electronic signatures'],
    'loi/2015/15-10': ['Médaille de bravoure', 'Medal of bravery'],
    'loi/2015/15-11': ['Médaille de participation', 'Medal of participation'],
    'loi/2015/15-12': ['Protection de l’enfant', 'Child protection'],
    'loi/2015/15-13': ['Livre', 'Books'],
    'loi/2015/15-21': ['Recherche scientifique', 'Scientific research'],
    'loi/2016/16-03': ['Empreinte génétique', 'DNA evidence'],
    'loi/2016/16-07': ['Commissaires-priseurs', 'Auctioneers'],
    'loi/2016/16-09': ['Investissement (2016)', 'Investment (2016)'],
    'loi/2016/16-13': ['Conseil national des droits de l’homme', 'National Human Rights Council'],
    'loi/2017/17-01': ['Hautes fonctions et nationalité', 'Senior posts and nationality'],
    'loi/2017/17-02': ['Petites et moyennes entreprises', 'Small and medium enterprises'],
    'loi/2017/17-09': ['Métrologie', 'Metrology'],
    'loi/2018/18-04': ['Poste et communications électroniques', 'Post and electronic communications'],
    'loi/2018/18-05': ['Commerce électronique', 'E-commerce'],
    'loi/2018/18-07': ['Données personnelles', 'Personal data'],
    'loi/2018/18-10': ['Apprentissage', 'Apprenticeship'],
    'loi/2018/18-11': ['Santé', 'Health'],
    'loi/2019/19-01': ['Règlement budgétaire 2016', 'Budget settlement for 2016'],
    'loi/2019/19-02': ['Incendie et panique', 'Fire and panic risks'],
    'loi/2019/19-05': ['Activités nucléaires', 'Nuclear activities'],
    'loi/2019/19-06': ['Activités spatiales', 'Space activities'],
    'loi/2019/19-13': ['Hydrocarbures (2019)', 'Hydrocarbons (2019)'],
    'loi/2020/20-01': ['Conseil national de la recherche', 'National Research Council'],
    'loi/2020/20-04': ['Radiocommunications', 'Radiocommunications'],
    'loi/2020/20-05': ['Discrimination et discours de haine', 'Discrimination and hate speech'],
    'loi/2020/20-09': ['Journée de la mémoire', 'Day of Remembrance'],
    'loi/2020/20-15': ['Enlèvement', 'Kidnapping'],
    'loi/2021/21-15': ['Spéculation illicite', 'Illicit speculation'],
    'loi/2022/22-07': ['Découpage judiciaire', 'Judicial map'],
    'loi/2022/22-08': ['Haute autorité de transparence', 'High Transparency Authority'],
    'loi/2022/22-15': ['Zones franches', 'Free zones'],
    'loi/2022/22-18': ['Investissement (2022)', 'Investment (2022)'],
    'loi/2022/22-20': ['Réserve militaire', 'Military reserve'],
    'loi/2022/22-23': ['Auto-entrepreneur', 'Self-employment'],
    'loi/2023/23-02': ['Droit syndical', 'Trade union rights'],
    'loi/2023/23-04': ['Traite des personnes', 'Human trafficking'],
    'loi/2023/23-07': ['Comptabilité publique', 'Public accounting'],
    'loi/2023/23-08': ['Conflits collectifs et grève', 'Labour disputes and strikes'],
    'loi/2023/23-09': ['Loi monétaire et bancaire', 'Monetary and banking law'],
    'loi/2023/23-12': ['Marchés publics', 'Public procurement'],
    'loi/2023/23-17': ['Foncier économique', 'Land for investment'],
    'loi/2023/23-18': ['Terres de l’État', 'State land'],
    'loi/2023/23-19': ['Presse écrite et électronique', 'Print and online press'],
    'loi/2023/23-20': ['Audiovisuel (2023)', 'Broadcasting (2023)'],
    'loi/2023/23-21': ['Forêts', 'Forests'],
    'loi/2024/24-01': ['Pension alimentaire', 'Maintenance payments'],
    'loi/2024/24-02': ['Faux et usage de faux', 'Forgery'],
    'loi/2024/24-04': ['Risques de catastrophes (2024)', 'Disaster risks (2024)'],
    'loi/2024/24-07': ['Industrie cinématographique (2024)', 'Film industry (2024)'],
    'loi/2025/25-01': ['Personnes à besoins spécifiques (2025)', 'Persons with special needs (2025)'],
    'loi/2025/25-05': ['Mobilisation générale', 'General mobilisation'],
    'loi/2025/25-06': ['Wakfs', 'Waqfs'],
    'loi/2025/25-15': ['Médailles militaires', 'Military medals'],
    'loi/2026/26-02': ['Services de confiance électroniques', 'Electronic trust services'],
    'loi/2026/26-07': ['Circonscriptions électorales', 'Electoral districts'],
    'loi/2026/26-10': ['Criminalisation de la colonisation', 'Criminalising colonisation'],
    'ordonnance/2003/03-04': ['Importation et exportation', 'Imports and exports'],
    'ordonnance/2003/03-05': ['Droits d’auteur', 'Copyright'],
    'ordonnance/2003/03-07': ['Brevets d’invention', 'Patents'],
    'ordonnance/2003/03-08': ['Circuits intégrés', 'Integrated circuits'],
    'ordonnance/2003/03-11': ['Monnaie et crédit', 'Money and credit'],
    'ordonnance/2003/03-12': ['Assurance des catastrophes naturelles', 'Natural disaster insurance'],
    'ordonnance/2005/05-06': ['Contrebande', 'Smuggling'],
    'ordonnance/2006/06-02': ['Statut des personnels militaires', 'Military personnel'],
    'ordonnance/2020/20-03': ['Bandes de quartiers', 'Neighbourhood gangs'],
    'ordonnance/2021/21-01': ['Régime électoral (2021)', 'Electoral system (2021)'],
    'ordonnance/2021/21-09': ['Informations et documents administratifs', 'Administrative information'],
    'ordonnance/2021/21-12': ['Mesures exceptionnelles (employeurs)', 'Emergency measures for employers'],
}

# ------------------------------------------------------------------------------------------------ the acts
start = {r['acts']: r for r in ccsv if r['kind'] == 'start'}
LAWLABEL = {}
for c in commits:
    if c['t'].get('Law') and c['ae'].endswith('@joradp.invalid'):
        LAWLABEL[c['ae'].split('@')[0]] = dict(label=c['t']['Law'], enacted=c['t'].get('Enacted'), published=c['t'].get('Published'), subj=c['subj'])
amend_rows = [r for r in ccsv if r['kind'] == 'law']
by_folder = collections.defaultdict(list)
for p, o in head:
    by_folder[p.rsplit('/', 1)[0]].append((p.rsplit('/', 1)[1], o))
assert len(by_folder) == 155, len(by_folder)
assert set(by_folder) == set(NAMES), set(by_folder) ^ set(NAMES)

RE_LABEL = re.compile(r'^(Loi organique|Loi|Ordonnance|Décret présidentiel)\s*n°\s*(\d{2})-(\d{2,3})')


def law_num(key):
    """('loi'|'ord'|'dec', 'yy', n) of a law key in laws.csv, from its title"""
    m = RE_LABEL.match(laws[key]['title'])
    if not m: return None
    seq = 'ord' if m.group(1) == 'Ordonnance' else ('dec' if m.group(1).startswith('Décret') else 'loi')
    return seq, m.group(2), int(m.group(3)), m.group(1)


acts = {}
for slug, s in start.items():
    folder = paths.get(slug, slug)
    key = s['law'] or None
    L = laws.get(key) if key else None
    kind = folder.split('/')[0]
    if folder == 'code/code-penal': inst = 'ordonnance'
    elif kind == 'constitution': inst = 'decret'
    else:
        lab = RE_LABEL.match(L['title']).group(1)
        inst = {'Loi': 'loi', 'Loi organique': 'lo', 'Ordonnance': 'ordonnance'}[lab]
    jo = None
    if L and re.search(r'/F(\d{4})(\d{3})\.pdf$', L['url'], re.I):
        m = re.search(r'/F(\d{4})(\d{3})\.pdf$', L['url'], re.I); jo = [int(m.group(1)), int(m.group(2))]
    acts[folder] = dict(f=folder, slug=slug, key=key, kind=kind, inst=inst, title=titles[folder],
                        enacted=L['enacted'] if L else None, published=L['published'] if L else None,
                        in_force=s['day'], jo=jo, fr=NAMES[folder][0], en=NAMES[folder][1])
assert len(acts) == 155

# run-on texts: files that repeat, blob for blob, the text printed after them in the same gazette issue
runon = set()
issue = collections.defaultdict(list)
for a in acts.values():
    if a['jo']: issue[tuple(a['jo'])].append(a['f'])
for iss, fs in issue.items():
    for i, f1 in enumerate(fs):
        for f2 in fs[i + 1:]:
            s1, s2 = set(by_folder[f1]), set(by_folder[f2])
            shared = s1 & s2
            if len(shared) >= 10:
                lo_, hi_ = sorted([f1, f2])           # the lower number runs on into the higher one
                runon |= {(lo_, f) for f, o in shared}
print('run-on files', len(runon), sorted({r[0] for r in runon}))
for f, a in acts.items():
    files = [(fn, o) for fn, o in by_folder[f] if (f, fn) not in runon]
    a['files'] = len(by_folder[f])
    a['n'] = sum(1 for fn, o in files if fn.startswith('art-'))
    a['w'] = sum(words(X[o]) for fn, o in files)
    a['runon'] = sum(1 for fn, o in by_folder[f] if (f, fn) in runon)
YEAR = {f: int((a['enacted'] or a['in_force'])[:4]) for f, a in acts.items()}
YEAR['code/code-penal'] = 2005
YEAR['loi/2002/02-01'] = 2002          # the record dates it 1991-04-27 (In-force and Published); enacted 2002-02-05

# the history: law commits in the order of their in-force day
law_commits = []
for c in commits:
    t = c['t']
    if t.get('Kind') in ('law', 'decree', 'publisher'):
        law_commits.append(c)
print('law commits', len(law_commits))
version_count = collections.Counter()
for c in law_commits:
    slugs = {p.split('/')[0] for st, p in names[c['h']] if not p.endswith('README.md')}
    for s in slugs: version_count[paths.get(s, s)] += 1
for f in acts: acts[f]['v'] = version_count[f]
assert sum(version_count.values()) == 172, sum(version_count.values())

# ================================================================================================ charts
C = {}

# ---- c01: every text, its size and kind (treemap)
C['c01'] = [dict(f=a['f'], k=a['kind'], i=a['inst'], y=YEAR[a['f']], w=a['w'], n=a['n'], v=a['v'], fr=a['fr'], en=a['en'], t=a['title'][:220]) for a in acts.values()]

# ---- c02: law numbers per year: held as a text, applied as an amendment, named only, or not in the record
held_keys = {a['key'] for a in acts.values() if a['key']}
applied_keys = {r['law'] for r in amend_rows}
grid = collections.defaultdict(dict)
for key, L in laws.items():
    ln = law_num(key)
    if not ln: continue
    seq, yy, n, lab = ln
    if seq == 'dec' or int(yy) > 30: continue            # the décret 20-442 and the Code pénal of 1966
    st = 'act' if key in held_keys else ('applied' if key in applied_keys else 'named')
    folder = next((a['f'] for a in acts.values() if a['key'] == key), None)
    grid[(seq, 2000 + int(yy))][n] = [st, key, lab, folder, L['enacted']]
missing_in_table = []
for r in amend_rows:
    if r['law'] in laws: continue
    lab = LAWLABEL.get(r['law'], {}).get('label', '')
    m = re.match(r'(Loi organique|Loi|Ordonnance) n°\s*(\d{2})-(\d{2,3})', lab)
    if m:
        seq = 'ord' if m.group(1) == 'Ordonnance' else 'loi'
        grid[(seq, 2000 + int(m.group(2)))][int(m.group(3))] = ['applied', r['law'], m.group(1), None, LAWLABEL[r['law']]['enacted']]
        missing_in_table.append(r['law'])
print('applied in the history but not in laws.csv:', missing_in_table)
c02 = []
for (seq, y), d in sorted(grid.items()):
    mx = max(d)
    cells = []
    for n in range(1, mx + 1):
        if n in d:
            st, key, lab, folder, en = d[n]
            ttl = laws[key]['title'][:200] if key in laws else LAWLABEL[key]['subj'][:200]
            cells.append([n, st, (acts[folder]['fr'] if folder else ttl[:160]), (acts[folder]['en'] if folder else None), lab, en, ttl])
        else:
            cells.append([n, 'none'])
    c02.append(dict(seq=seq, y=y, max=mx, cells=cells))
C['c02'] = c02

# ---- c03: from signature to the Journal officiel
c03 = []
for a in acts.values():
    if a['inst'] not in ('loi', 'lo', 'ordonnance') or not a['enacted'] or not a['published']: continue
    d = (D(a['published']) - D(a['enacted'])).days
    c03.append(dict(f=a['f'], i=a['inst'], y=int(a['enacted'][:4]), d=d, e=a['enacted'], p=a['published'], jo=a['jo'], fr=a['fr'], en=a['en']))
C['c03'] = sorted(c03, key=lambda r: r['e'])
bad = [r for r in c03 if r['d'] < 0]
print('c03 negative delays (left out on the page):', [(r['f'], r['d']) for r in bad])

# ---- c04: month of signature by instrument
C['c04'] = [dict(f=a['f'], i=a['inst'], e=a['enacted'], fr=a['fr'], en=a['en']) for a in acts.values() if a['inst'] in ('loi', 'lo', 'ordonnance') and a['enacted']]
# ordinances approved by a law (in the register of laws)
C['c04_approve'] = [dict(key=k, t=L['title'][:220], e=L['enacted']) for k, L in laws.items() if re.search(r"portant approbation de l'ordonnance", L['title'])]

# ---- c05 / c06 / c07: the Constitution
cons_v = VERS['constitution']
v20, v26 = cons_v[0]['files'], cons_v[1]['files']
cons = sorted(by_folder['constitution/constitution'])
LO_RE = re.compile(r"\blois? organiques?\b", re.I)
LAW_RE = re.compile(r"\b(?:la|une|les|des|cette|par la|en vertu de la) lois?\b(?! organiques?)(?! de finances)(?! portant)(?! cadre)", re.I)
c05 = []
for fn, o in cons:
    t = X[o]
    if not fn.startswith('art-'): continue
    num = re.match(r'art-(\d+)', fn).group(1)
    cls = 'lo' if LO_RE.search(body(t)) else ('loi' if LAW_RE.search(body(t)) else 'none')
    st = 'added' if fn not in v20 else ('changed' if v20[fn] != v26.get(fn) else 'same')
    c05.append(dict(a=int(num), c=cls, s=st, w=words(t), t=first_sentence(t)))
C['c05'] = c05
print('c05 articles', len(c05), collections.Counter(r['c'] for r in c05), collections.Counter(r['s'] for r in c05))
C['c05_extra'] = dict(preamble_words=words(X[dict(cons)['preambule.md']]), oath=[fn for fn, o in cons if fn.startswith('serment')])

import difflib
TOK = re.compile(r"\w+|[^\w\s]")
c06 = []
for fn in sorted(set(v20) | set(v26)):
    if v20.get(fn) == v26.get(fn) or not fn.startswith('art-'): continue
    ta = TOK.findall(body(X[v20[fn]])) if fn in v20 else []
    tb = TOK.findall(body(X[v26[fn]])) if fn in v26 else []
    sm = difflib.SequenceMatcher(None, ta, tb, autojunk=False)
    add = dele = 0
    ins, rem = [], []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op in ('replace', 'delete'):
            dele += sum(1 for x in ta[i1:i2] if re.match(r'\w', x)); rem.append(' '.join(ta[i1:i2]))
        if op in ('replace', 'insert'):
            add += sum(1 for x in tb[j1:j2] if re.match(r'\w', x)); ins.append(' '.join(tb[j1:j2]))
    fix = lambda s: re.sub(r"\s+([,.;:)])", r"\1", re.sub(r"(\w) ' (\w)", r"\1'\2", s)).replace('( ', '(')
    c06.append(dict(a=int(re.match(r'art-(\d+)', fn).group(1)), add=add, rem=dele, w20=words(X[v20[fn]]) if fn in v20 else 0,
                    w26=words(X[v26[fn]]), ins=[fix(s) for s in ins if re.search(r'\w', s)][:6], dels=[fix(s) for s in rem if re.search(r'\w', s)][:6]))
C['c06'] = c06
print('c06', [(r['a'], r['rem'], r['add']) for r in c06])

INST = [
    ['pr', 'exec', r"Président de la République"],
    ['pm', 'exec', r"Premier ministre|Chef du Gouvernement"],
    ['gov', 'exec', r"(?<!Chef du )\bGouvernement\b"],
    ['cm', 'exec', r"Conseil des [Mm]inistres"],
    ['parl', 'leg', r"\bParlement\b"],
    ['apn', 'leg', r"Assembl[ée]e Populaire Nationale"],
    ['cn', 'leg', r"Conseil de la Nation"],
    ['cc', 'ctrl', r"Cour constitutionnelle"],
    ['cs', 'jud', r"Cour suprême"],
    ['ce', 'jud', r"Conseil d'[EÉ]tat"],
    ['csm', 'jud', r"Conseil [Ss]upérieur de la [Mm]agistrature"],
    ['anie', 'ctrl', r"Autorité nationale indépendante des élections"],
    ['cdc', 'ctrl', r"Cour des comptes"],
    ['hcs', 'exec', r"Haut Conseil de Sécurité"],
    ['anp', 'exec', r"Armée Nationale Populaire"],
    ['peuple', 'people', r"\b[Pp]euple\b"],
    ['ref', 'people', r"\bréférendum\b"],
]
arts26 = [(fn, o) for fn, o in cons if fn.startswith('art-')]
c07 = []
for k, g, pat in INST:
    hits = [int(re.match(r'art-(\d+)', fn).group(1)) for fn, o in arts26 if re.search(pat, body(X[o]))]
    c07.append(dict(k=k, g=g, n=len(hits), arts=hits))
C['c07'] = dict(rows=c07, total=len(arts26))
print('c07', [(r['k'], r['n']) for r in c07])

# ---- abrogation clauses: every earlier text a held text repeals (used by c08, c14, c16)
REF = re.compile(r"\b(loi organique|loi|ordonnance|décret législatif|décret exécutif|décret)\s+n°\s*(\d{2})\s*[-‑–]\s*(\d{1,3})\b(?:\s+du\s+((?:[^,;()]{0,60}?correspondant au\s+)?(?:1er|\d{1,2})\s+[a-zéû]+\s+\d{4}))?", re.I)
MONTHS = {m: i + 1 for i, m in enumerate(['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre'])}


def gdate(s):
    if not s: return None
    m = re.search(r'(1er|\d{1,2})\s+([a-zéû]+)\s+(\d{4})\s*$', s, re.I)
    if not m or m.group(2).lower() not in MONTHS: return None
    return f"{m.group(3)}-{MONTHS[m.group(2).lower()]:02d}-{1 if m.group(1) == '1er' else int(m.group(1)):02d}"


held_by_num = {}
for a in acts.values():
    if a['key'] and law_num(a['key']):
        seq, yy, n, lab = law_num(a['key'])
        held_by_num[('ordonnance' if seq == 'ord' else 'loi', f'{yy}-{n:02d}')] = a['f']
held_by_num[('ordonnance', '66-156')] = 'code/code-penal'
repeals = []
for f, files in by_folder.items():
    if f == 'code/code-penal': continue        # its 'abrogé' mentions are the 2005 edition's notes on its own history
    for fn, o in files:
        if (f, fn) in runon: continue
        lines = body(X[o]).split('\n')
        paras = []
        for i, line in enumerate(lines):   # "Sont abrogées, les dispositions de :" followed by a dashed list: one paragraph
            if re.match(r'\s*[—–-]\s', line) and paras and paras[-1][1]:
                paras[-1][0] += ' ' + line.strip(); continue
            paras.append([line, line.rstrip().endswith(':')])
        for para, _ in paras:
            if not re.search(r'\babrog', para, re.I): continue
            if re.search(r"textes? (?:d'application|pris|réglementaires)[^.]*abrog", para, re.I) and not re.search(r'\b(?:est|sont) abrog', para, re.I): continue
            for m in REF.finditer(para):
                kind = m.group(1).lower(); kind = 'loi' if kind == 'loi organique' else kind
                if kind.startswith('décret') and kind != 'décret législatif': continue
                num = f"{m.group(2)}-{int(m.group(3)):02d}"
                if f.endswith('/' + num): continue
                before = para[max(0, m.start() - 200):m.start()]
                if re.search(r"abrog\w*\s+par\s+(?:l'|la\s+|le\s+)?\s*$", before, re.I): continue   # the repealing law, not the repealed one
                partial = bool(re.search(r"(?:\b\d+(?:er)?(?:\s+(?:bis|ter|quater|quinquies))?(?:\s+\d+)?|\b[IVXL]+)\s*,?\s*(?:de|des|du)\s+(?:l'|la\s+|le\s+)?\s*$", before)
                               or re.search(r"\bcontenues?\s+dans\b|\bcertaines dispositions\b", para[:m.start()], re.I))
                repeals.append(dict(by=f, fn=fn, kind=kind, num=num, date=gdate(m.group(4)), partial=partial,
                                    held=held_by_num.get((kind if kind != 'décret législatif' else 'dl', num)), para=para[:400]))
# keep one row per (repealing text, repealed text); a whole repeal wins over a partial one
rp = {}
for r in repeals:
    k = (r['by'], r['kind'], r['num'])
    if k not in rp or (rp[k]['partial'] and not r['partial']): rp[k] = r
repeals = sorted(rp.values(), key=lambda r: (r['by'], r['num']))
print('repeal rows', len(repeals), 'whole', sum(1 for r in repeals if not r['partial']), 'of held texts', sum(1 for r in repeals if r['held']))

# ---- c08: the organic laws by domain
DOM = [
    ['elec', 'Régime électoral', 'Electoral system', ['loi-organique/2012/12-01', 'loi-organique/2016/16-10', 'ordonnance/2021/21-01']],
    ['auth', 'Autorité des élections', 'Election authority', ['loi-organique/2016/16-11', 'loi-organique/2019/19-07']],
    ['postp', 'Report des élections locales', 'Postponed local elections', ['loi-organique/2007/07-07']],
    ['incomp', 'Incompatibilités parlementaires', 'Parliamentary incompatibilities', ['loi-organique/2012/12-02']],
    ['women', 'Représentation des femmes', 'Women’s representation', ['loi-organique/2012/12-03']],
    ['parties', 'Partis politiques', 'Political parties', ['loi-organique/2012/12-04', 'loi-organique/2026/26-08']],
    ['info', 'Information', 'Information', ['loi-organique/2012/12-05', 'loi-organique/2023/23-14']],
    ['mag', 'Statut de la magistrature', 'Statute of the judiciary', ['loi-organique/2004/04-11', 'loi-organique/2026/26-03']],
    ['csm', 'Conseil supérieur de la magistrature', 'High Council of the Judiciary', ['loi-organique/2004/04-12', 'loi-organique/2022/22-12']],
    ['oj', 'Organisation judiciaire', 'Judicial organisation', ['loi-organique/2005/05-11', 'loi-organique/2022/22-10']],
    ['cs', 'Cour suprême', 'Supreme Court', ['loi-organique/2011/11-12']],
    ['exc', 'Exception d’inconstitutionnalité', 'Plea of unconstitutionality', ['loi-organique/2018/18-16', 'loi-organique/2022/22-19']],
    ['fin', 'Lois de finances', 'Finance laws', ['loi-organique/2018/18-15']],
    ['amz', 'Langue amazighe', 'Amazigh language', ['loi-organique/2018/18-17']],
]
lo_all = [f for f, a in acts.items() if a['inst'] == 'lo'] + ['ordonnance/2021/21-01']
assert sorted(sum((d[3] for d in DOM), [])) == sorted(lo_all), set(sum((d[3] for d in DOM), [])) ^ set(lo_all)
rep_pairs = {(r['by'], r['held']) for r in repeals if r['held'] and not r['partial']}
c08 = []
for k, fr, en, fs in DOM:
    items = []
    for f in fs:
        a = acts[f]
        items.append(dict(f=f, num=f.split('/')[-1], i=a['inst'], e=a['enacted'], fr=a['fr'], en=a['en'], n=a['n'],
                          rep_by=next((g for (g, h) in rep_pairs if h == f), None)))
    c08.append(dict(k=k, fr=fr, en=en, items=items))
# amendments applied to an organic law in the history
lo_amend = []
for r in amend_rows:
    f = paths.get(r['acts'], r['acts'])
    if f in lo_all:
        lab = laws[r['law']]['label'] if r['law'] in laws else LAWLABEL.get(r['law'], {}).get('label', r['law'])
        lo_amend.append(dict(f=f, law=r['law'], label=lab, day=r['day'], files=int(r['files'])))
C['c08'] = dict(rows=c08, amend=lo_amend)

# ---- the Code pénal: versions, articles, writers
cp_v = VERS['code-penal']
cp_head = cp_v[-1]['files']
NOTE = re.compile(r"\((Loi|Ordonnance|Décret législatif)\s*n°\s*(\d{2})\s*-\s*(\d{2,3}) du ([^)]*?)(\d{4})\)", re.I)
first = cp_v[0]['files']
notes = collections.Counter(); note_date = {}
for fn, o in first.items():
    for n in {(x[0].capitalize(), f"{x[1]}-{x[2]}", x[3].strip() + ' ' + x[4]) for x in NOTE.findall(body(X[o]))}:
        notes[(n[0], n[1])] += 1; note_date[(n[0], n[1])] = n[2]
# amendments in git: per law commit on the Code pénal, files added (inserted), modified (changed), deleted (removed)
cp_git = []
for r in cp_v[1:]:
    c = next(c for c in law_commits if c['h'] == r['h'])
    st = collections.Counter(s for s, p in names[r['h']] if p.startswith('code-penal/art-'))
    # the articles the commit message says could not be applied ("Not applied here, because …: Art. 100, Art. 166, art-177-bis-1, Art. 350.")
    nap = re.search(r"Not applied here[^:]*:\s*(.*?)\.(?:\s*\n|\s+[A-Z]|\s*$)", c['body'], re.S)
    na = len(re.findall(r"Art\.\s*\d+(?:\s+(?:bis|ter|quater|quinquies|sexies)(?:\s+\d+)?)?|art-[\w-]+", nap.group(1))) if nap else 0
    cp_git.append(dict(law=c['t'].get('Law'), e=c['t'].get('Enacted'), d=r['in_force'], ins=st['A'], chg=st['M'], rem=st['D'],
                       na=na, n=sum(1 for f in r['files'] if f.startswith('art-'))))


def ndate(s):
    """'13 février 1982' -> '1982-02-13' for the edition's notes"""
    return gdate(s) or (s[-4:] + '-01-01')


C['c09'] = dict(notes=[dict(law=f"{k[0]} n° {k[1]}", d=ndate(note_date[k]), n=v) for k, v in sorted(notes.items(), key=lambda kv: ndate(note_date[kv[0]]))],
                git=cp_git, n2005=sum(1 for f in first if f.startswith('art-')), noted=sum(1 for fn, o in first.items() if NOTE.search(body(X[o]))))
print('c09 notes', C['c09']['notes'])

# c10: who wrote the text in force of each article; articles another held text repeals
ART_LIST = re.compile(r"(?:articles?|art\.)\s+((?:\d+(?:\s+(?:bis|ter|quater)(?:\s+\d+)?)?(?:\s*,\s*|\s+et\s+|\s+à\s+)?)+)", re.I)


def art_keys(txt):
    """'119, 119 bis 1, 121 ... et 134' / '172, 173 et 174' -> {'art-119', 'art-119-bis-1', ...}"""
    out = set()
    parts = re.split(r'\s*,\s*|\s+et\s+', txt.strip())
    for p in parts:
        m = re.match(r'(\d+)(?:\s+(bis|ter|quater))?(?:\s+(\d+))?\s*(?:à\s+(\d+))?$', p.strip())
        if not m: continue
        if m.group(4) and not m.group(2):
            for k in range(int(m.group(1)), int(m.group(4)) + 1): out.add(f'art-{k:03d}')
            continue
        key = f'art-{int(m.group(1)):03d}' + (f'-{m.group(2)}' if m.group(2) else '') + (f'-{m.group(3)}' if m.group(3) else '')
        out.add(key)
    return out


TAIL_LIST = re.compile(r"((?:\d+(?:er)?(?:\s+(?:bis|ter|quater)(?:\s+\d+)?)?(?:\s*,\s*|\s+et\s+|\s+à\s+)?)+)\s+(?:de|du|des)\s+(?:l'|la\s+|le\s+)?\s*$")


def parse_partial(r):
    """the article files of the held target that a partial repeal names: the numbers just before 'de l'ordonnance n° …'"""
    para = r['para']
    yy, nn = r['num'].split('-')
    m = re.search(r"(?:loi organique|loi|ordonnance)\s+n°\s*" + yy + r"\s*[-‑–]\s*0*" + str(int(nn)) + r"\b", para, re.I)
    if not m: return set()
    seg = para[:m.start()]
    t = TAIL_LIST.search(seg)
    return art_keys(re.sub(r'(\d)er\b', r'\1', t.group(1))) if t else set()


repealed_inside = collections.defaultdict(dict)     # target folder -> {file: repealing folder}
for r in repeals:
    if not r['held'] or not r['partial']: continue
    tgt = r['held']
    keys = parse_partial(r)
    tfiles = {fn for fn, o in by_folder[tgt]}
    for k in keys:
        if k + '.md' in tfiles: repealed_inside[tgt][k + '.md'] = r['by']
print('articles of held texts repealed by another held text, still present:', {k: len(v) for k, v in repealed_inside.items()})

writer = {}
for fn, o in cp_head.items():
    if not fn.startswith('art-'): continue
    last, prevo = None, None
    for r in cp_v:
        oo = r['files'].get(fn)
        if oo is not None and oo != prevo: last = r
        prevo = oo
    if last is cp_v[0]:
        ns = NOTE.findall(body(X[o]))
        if ns:
            n = max(ns, key=lambda n: (n[4], n[1]))
            writer[fn] = ['note', f"{n[0].capitalize()} n° {n[1]}-{n[2]}", int(n[4])]
        else:
            writer[fn] = ['none', None, None]
    else:
        writer[fn] = ['git', last['law'], int(last['in_force'][:4])]


def art_sort(fn):
    m = re.match(r'art-(\d+)(?:-(bis|ter|quater|quinquies|sexies|septies|octies|nonies|a))?(?:-(\d+))?', fn)
    rank = ['', 'bis', 'ter', 'quater', 'quinquies', 'sexies', 'septies', 'octies', 'nonies', 'a']
    return (int(m.group(1)), rank.index(m.group(2) or ''), int(m.group(3) or 0), fn)


c10 = []
for fn in sorted(writer, key=art_sort):
    o = cp_head[fn]
    w = writer[fn]
    c10.append(dict(fn=fn, l=label(X[o], fn), c=w[0], law=w[1], y=w[2], ab=repealed_inside.get('code/code-penal', {}).get(fn),
                    bis=bool(re.search(r'-(bis|ter|quater|quinquies|sexies|septies|octies|nonies)', fn)), t=first_sentence(X[o], 150)))
C['c10'] = c10
print('c10', collections.Counter((r['c'], r['law']) for r in c10).most_common(25), 'abrogated inside', sum(1 for r in c10 if r['ab']))

# c11: the death penalty, article by article and version by version
DEATH_P = [re.compile(p, re.I | re.M) for p in [
    r"\bpunie?s? de (?:la peine de )?mort\b", r"\bpunie?s? de la peine capitale\b", r"\bemporte (?:également )?la peine de mort\b",
    r"\bpeine (?:encourue )?est (?:la mort|celle de la mort)\b", r"\bpassible de (?:la )?peine de mort\b", r"\bla peine de mort est encourue\b",
    r"\bencour(?:t|ent) la peine de mort\b", r"^\s*(?:[—–-]\s*)?(?:\d+°\)?\s*)?(?:dans les cas[^,\n]*,\s*)?de la peine de mort\b",
    r"^\s*[—–-]\s*la peine de mort, lorsque"]]
DEATH_X = re.compile(r"\bcrimes? (?:est |sont )?(?:punie?s?|passibles?)\b|\bs'il s'agit d'un crime\b|peine de mort est remplacée|\bsi ce crime est puni", re.I)


def death(t):
    for sent in re.split(r'(?<=[.;])\s+|\n', body(t)):
        if any(p.search(sent) for p in DEATH_P) and not DEATH_X.search(sent): return True
    return False


c11 = []
prev = set()
for r in cp_v:
    cur = {fn for fn, o in r['files'].items() if fn.startswith('art-') and death(X[o])}
    c11.append(dict(d=r['in_force'], law=r['law'], n=len(cur), plus=sorted(cur - prev, key=art_sort), minus=sorted(prev - cur, key=art_sort),
                    arts=sorted(cur, key=art_sort)))
    prev = cur
C['c11'] = c11
print('c11', [(r['d'], r['n'], len(r['plus']), len(r['minus'])) for r in c11])
# the second series: articles whose heaviest penalty is life imprisonment (réclusion à perpétuité)
LIFE_RE = re.compile(r"réclusion (?:criminelle )?(?:à )?perpétu", re.I)
for r, row in zip(cp_v, c11):
    row['life'] = sum(1 for fn, o in r['files'].items() if fn.startswith('art-') and not death(X[o]) and LIFE_RE.search(body(X[o])))
# what the articles that stopped providing death provide in the next version
for i, row in enumerate(c11):
    if row['minus']:
        nxt = cp_v[i]['files']
        row['minus_to'] = {fn: ('life' if LIFE_RE.search(body(X[nxt[fn]])) else ('recl' if re.search('réclusion', body(X[nxt[fn]]), re.I) else 'other')) if fn in nxt else 'gone' for fn in row['minus']}
print('c11 life', [r['life'] for r in c11], [r.get('minus_to') for r in c11 if r.get('minus_to')])
death_labels = {}
for r in cp_v:
    for fn, o in r['files'].items():
        if fn.startswith('art-') and death(X[o]): death_labels[fn] = label(X[o], fn)
C['c11_labels'] = death_labels

# c12: the highest fine each article names, version by version
AMT = re.compile(r"(\d{1,3}(?:[ .  ]\d{3})+|\d+)\s*(?:de\s+)?(?:DA\b|dinars?\b)", re.I)
BANDS = [10000, 100000, 1000000, 10000000]


def max_fine(t):
    best = None
    for sent in re.split(r'(?<=[.;])\s+|\n', body(t)):
        if not re.search(r'\bamendes?\b', sent, re.I): continue
        for m in AMT.finditer(sent):
            v = int(re.sub(r'\D', '', m.group(1)))
            best = v if best is None or v > best else best
    return best


c12 = []
prev_f = {}
for r in cp_v:
    cur_f = {fn: max_fine(X[o]) for fn, o in r['files'].items() if fn.startswith('art-')}
    vals = sorted(v for v in cur_f.values() if v)
    b = [0] * 5
    for v in vals: b[sum(1 for x in BANDS if v > x)] += 1
    up = sum(1 for fn, v in cur_f.items() if v and prev_f.get(fn) and v > prev_f[fn])      # articles whose highest fine this version raised
    new = sum(1 for fn, v in cur_f.items() if v and fn not in prev_f) if prev_f else 0      # articles this version inserts with a fine
    gain = sum(1 for fn, v in cur_f.items() if v and fn in prev_f and not prev_f[fn])      # existing articles that get a fine in DA
    c12.append(dict(d=r['in_force'], law=r['law'], n=len(vals), b=b, med=statistics.median(vals), up=up, gain=gain, new=new, arts=sum(1 for f in r['files'] if f.startswith('art-'))))
    prev_f = cur_f
C['c12'] = c12
print('c12', [(r['d'], r['n'], r['b'], r['med']) for r in c12])

# c13: article 87 bis, the definition of a terrorist act, version by version
v87 = []
for r in cp_v:
    o = r['files'].get('art-087-bis.md')
    if o and (not v87 or v87[-1]['o'] != o):
        t = body(X[o])
        lines = t.split('\n')
        items = [re.sub(r'^\s*[-—–]\s*', '', l).strip() for l in lines if re.match(r'\s*[-—–]', l)]
        v87.append(dict(o=o, d=r['in_force'], law=r['law'], w=words(X[o]), head=re.sub(r'^\(Ordonnance[^)]*\)\s*', '', lines[0]).strip(), items=items))
for v in v87: v.pop('o')
C['c13'] = v87
print('c13', [(v['d'], v['w'], len(v['items'])) for v in v87])

# ---- c14: what the held texts repeal (whole repeals, one row per repealed text)
c14 = []
for r in repeals:
    if r['partial']: continue
    by = acts[r['by']]
    d_by = by['enacted'] or by['in_force']
    yy = int(r['num'].split('-')[0]); y_old = (1900 if yy > 30 else 2000) + yy
    c14.append(dict(by=r['by'], kind=r['kind'], num=r['num'], d=r['date'], y=int(r['date'][:4]) if r['date'] else y_old, y_by=int(d_by[:4]), d_by=d_by,
                    held=r['held'], fr=by['fr'], en=by['en'], txt=re.sub(r'\s+', ' ', r['para'])[:260]))
# a text repealed by two held texts (e.g. both run-on copies) counts once, for the earliest repeal
seen = {}
for r in sorted(c14, key=lambda r: r['d_by']):
    seen.setdefault((r['kind'], r['num']), r)
C['c14'] = sorted(seen.values(), key=lambda r: (r['y'], r['num']))
print('c14 rows', len(C['c14']), 'held', sum(1 for r in C['c14'] if r['held']), 'undated', [r['num'] for r in C['c14'] if not r['d']])

# ---- c15: how much of the text a replacing law takes over from the law it replaces (both held)
def toks(t): return re.findall(r"\w+", body(t).lower())


def shingles(ts, k=5): return {' '.join(ts[i:i + k]) for i in range(max(0, len(ts) - k + 1))} or ({' '.join(ts)} if ts else set())


PUB = re.compile(r"sera publiée? au Journal officiel", re.I)
c15 = []
for r in C['c14']:
    if not r['held']: continue
    old, new = r['held'], r['by']
    S_old = set()
    olds = set()
    for fn, o in by_folder[old]:
        if (old, fn) in runon: continue
        S_old |= shingles(toks(X[o])); olds.add(re.sub(r'\s+', ' ', body(X[o])).strip())
    cls = collections.Counter(); wcls = collections.Counter()
    for fn, o in by_folder[new]:
        if (new, fn) in runon or not fn.startswith('art-') or PUB.search(body(X[o])): continue
        ts = toks(X[o]); s = shingles(ts)
        if re.sub(r'\s+', ' ', body(X[o])).strip() in olds: c = 'same'
        else:
            q = len(s & S_old) / len(s) if s else 0
            c = 'same' if q >= 0.98 else ('most' if q >= 0.8 else ('part' if q >= 0.4 else 'new'))
        cls[c] += 1; wcls[c] += len(ts)
    c15.append(dict(old=old, new=new, y_old=YEAR[old], y_new=YEAR[new], c=[cls[k] for k in ('same', 'most', 'part', 'new')],
                    w=[wcls[k] for k in ('same', 'most', 'part', 'new')], fr_old=acts[old]['fr'], en_old=acts[old]['en'], fr=acts[new]['fr'], en=acts[new]['en']))
C['c15'] = sorted(c15, key=lambda r: -(r['c'][0] + r['c'][1]) / max(1, sum(r['c'])))
print('c15', [(r['old'], r['new'], r['c']) for r in C['c15']])

# ---- c16: after enactment: the changes the record applies, names without applying, and the repeals it does not mark
c16 = collections.defaultdict(lambda: dict(applied=[], named=[], whole=None, partial=[]))
for r in amend_rows:
    f = paths.get(r['acts'], r['acts'])
    L = laws.get(r['law'])
    c16[f]['applied'].append(dict(key=r['law'], label=L['label'] if L else LAWLABEL.get(r['law'], {}).get('label', r['law']), d=r['day'], files=int(r['files']), t=(L['title'] if L else '')[:220]))
TARGET = re.compile(r"(modifiant et complétant|modifiant|complétant|portant approbation de)\s+(?:certaines dispositions de\s+)?(?:la|l')\s*(loi organique|loi|ordonnance)\s+n°\s*(\d{2})-(\d{2,3})", re.I)
misapplied = []
for key, L in laws.items():
    m = TARGET.search(L['title'])
    if not m: continue
    kind = 'ordonnance' if m.group(2).lower() == 'ordonnance' else 'loi'
    tgt = held_by_num.get((kind, f"{m.group(3)}-{int(m.group(4)):02d}"))
    applied_to = [paths.get(r['acts'], r['acts']) for r in amend_rows if r['law'] == key]
    if applied_to and tgt not in applied_to:
        misapplied.append(dict(key=key, label=L['label'], target_kind=kind, target=f"{m.group(3)}-{m.group(4)}", applied_to=applied_to, t=L['title'][:240]))
    if int(L['commits']) == 0 and tgt:
        c16[tgt]['named'].append(dict(key=key, label=L['label'], d=L['published'] or L['enacted'], t=L['title'][:220], approve=m.group(1).lower().startswith('portant approbation')))
for r in C['c14']:
    if r['held']: c16[r['held']]['whole'] = dict(by=r['by'], d=r['d_by'], fr=acts[r['by']]['fr'], en=acts[r['by']]['en'])
for tgt, d in repealed_inside.items():
    byf = collections.Counter(d.values())
    for g, n in byf.items():
        c16[tgt]['partial'].append(dict(by=g, n=n, d=acts[g]['enacted'] or acts[g]['in_force'], fr=acts[g]['fr'], en=acts[g]['en'], arts=sorted([k for k, v in d.items() if v == g], key=art_sort)))
C['c16'] = [dict(f=f, fr=acts[f]['fr'], en=acts[f]['en'], e=acts[f]['enacted'] or acts[f]['in_force'], y=YEAR[f], **v) for f, v in c16.items()]
C['c16_misapplied'] = misapplied
print('c16 texts', len(C['c16']), 'misapplied', misapplied)

# ---- c17: articles that set a penalty outside the Code pénal, by year of the text and heaviest penalty
PEN = re.compile(r"\b(?:est|sont)\s+punie?s?\b|\bpunie?s?\s+(?:d'|de\s|des\s)|\bpassibles?\s+d|\bencour(?:t|ent)\b", re.I)
LIFE = re.compile(r"réclusion (?:criminelle )?(?:à )?perpétu", re.I)


def penalty(t):
    b = body(t)
    if death(t): return 'death'
    if not PEN.search(b): return None
    if LIFE.search(b): return 'life'
    if re.search(r'réclusion', b, re.I): return 'recl'
    if re.search(r'emprisonnement', b, re.I): return 'prison'
    if re.search(r'\bamendes?\b', b, re.I): return 'fine'
    return None


c17 = collections.defaultdict(collections.Counter)
c17_acts = collections.Counter(); c17_cls = collections.defaultdict(collections.Counter)
cp_pen = collections.Counter()
for f, files in by_folder.items():
    for fn, o in files:
        if (f, fn) in runon or not fn.startswith('art-'): continue
        p = penalty(X[o])
        if not p: continue
        if f == 'code/code-penal': cp_pen[p] += 1; continue
        c17[YEAR[f]][p] += 1; c17_acts[f] += 1; c17_cls[f][p] += 1
C['c17'] = dict(years=[dict(y=y, **c17[y]) for y in range(2002, 2027)],
                acts=[dict(f=f, n=n, fr=acts[f]['fr'], en=acts[f]['en'], y=YEAR[f], **c17_cls[f]) for f, n in c17_acts.most_common()],
                cp=dict(cp_pen), n_acts=len(c17_acts))
print('c17 total outside CP', sum(c17_acts.values()), 'texts', len(c17_acts), 'CP', dict(cp_pen))

# ---- c18: the time limits the texts set ("dans un délai de quinze (15) jours")
DL = re.compile(r"\b(?:délai|dans les|au plus tard|avant l'expiration)\b[^.;:\n]{0,60}?\((\d+)\)\s*(heures?|jours?|semaines?|mois|ans|années?)\b", re.I)
UNIT = {'heure': 'h', 'heures': 'h', 'jour': 'd', 'jours': 'd', 'semaine': 'w', 'semaines': 'w', 'mois': 'm', 'an': 'y', 'ans': 'y', 'année': 'y', 'années': 'y'}
PROC = {'code/code-procedure-penale', 'code/code-procedure-civile-administrative', 'code/code-justice-militaire'}
c18 = collections.defaultdict(lambda: [0, 0])
for f, files in by_folder.items():
    for fn, o in files:
        if (f, fn) in runon: continue
        for m in DL.finditer(body(X[o])):
            c18[(int(m.group(1)), UNIT[m.group(2).lower()])][0 if f in PROC else 1] += 1
C['c18'] = [dict(n=k[0], u=k[1], proc=v[0], other=v[1]) for k, v in c18.items()]
print('c18 total', sum(sum(v) for v in c18.values()), sorted(c18.items(), key=lambda kv: -sum(kv[1]))[:12])

# ---- c19: the custodial ranges the texts set ("emprisonnement de deux (2) ans à cinq (5) ans"), in months
NW = {'un': 1, 'une': 1, 'deux': 2, 'trois': 3, 'quatre': 4, 'cinq': 5, 'six': 6, 'sept': 7, 'huit': 8, 'neuf': 9, 'dix': 10, 'onze': 11, 'douze': 12,
      'treize': 13, 'quatorze': 14, 'quinze': 15, 'seize': 16, 'dix-sept': 17, 'dix-huit': 18, 'vingt': 20, 'trente': 30, 'quarante': 40}
DUR = (r"(?:d'|de\s+)?(?:(?P<w{i}>un|une|deux|trois|quatre|cinq|six|sept|huit|neuf|dix-sept|dix-huit|dix|onze|douze|treize|quatorze|quinze|seize|vingt|trente|quarante)\s*)?"
       r"(?:\((?P<d{i}>\d+)\)\s*)?(?P<n{i}>\d+\s*)?(?P<u{i}>ans?|années?|mois|jours?)?")
RANGE = re.compile(r"(?P<kind>emprisonnement|réclusion(?: criminelle)?(?: à temps)?)\s+(?:d'une durée\s+)?(?:de|d')\s*" + DUR.format(i=1)
                   + r"\s*(?:au moins\s*)?(?:à|jusqu'à)\s*" + DUR.format(i=2), re.I)


def rval(m, i):
    d = m.group(f'd{i}') or m.group(f'n{i}')
    if d: return int(d)
    w = m.group(f'w{i}')
    return NW.get(w.lower()) if w else None


def months(v, u):
    return v * 12 if u.startswith('an') else (v if u == 'mois' else round(v / 30, 2))


c19 = collections.defaultdict(lambda: [0, 0, 0])      # (min, max) -> [prison in the Code pénal, prison elsewhere, réclusion]
c19_bad = 0
for f, files in by_folder.items():
    for fn, o in files:
        if (f, fn) in runon: continue
        for m in RANGE.finditer(body(X[o])):
            a, b = rval(m, 1), rval(m, 2)
            ua, ub = (m.group('u1') or '').lower(), (m.group('u2') or '').lower()
            if a is None or b is None or not ub: c19_bad += 1; continue
            lo_, hi_ = months(a, ua or ub), months(b, ub)
            if lo_ >= hi_: c19_bad += 1; continue
            k = 2 if m.group('kind').lower().startswith('réclusion') else (0 if f == 'code/code-penal' else 1)
            c19[(lo_, hi_)][k] += 1
C['c19'] = dict(cells=[dict(a=k[0], b=k[1], cp=v[0], other=v[1], recl=v[2]) for k, v in c19.items()], unparsed=c19_bad)
print('c19 ranges', sum(sum(v) for v in c19.values()), 'unparsed', c19_bad, sorted(c19.items(), key=lambda kv: -sum(kv[1]))[:6])

# ---- c09 cards: the six codes
cards = []
for f in ['code/code-penal', 'code/code-procedure-civile-administrative', 'code/code-procedure-penale', 'code/code-justice-militaire', 'code/code-organisation-penitentiaire', 'code/code-route']:
    a = acts[f]
    pen = sum(1 for fn, o in by_folder[f] if fn.startswith('art-') and penalty(X[o]))
    rep = next((r for r in C['c14'] if r['by'] == f), None)
    vers = VERS.get(a['slug'], [])
    changed = 0
    if len(vers) > 1:
        v0 = vers[0]['files']; vl = vers[-1]['files']
        changed = sum(1 for fn, o in vl.items() if fn.startswith('art-') and v0.get(fn) != o)
    cards.append(dict(f=f, fr=a['fr'], en=a['en'], key=a['key'], title=a['title'][:200], inst=a['inst'], e=a['enacted'], inf=a['in_force'], n=a['n'], w=a['w'], v=a['v'], pen=pen,
                      changed=changed, rep=dict(kind=rep['kind'], num=rep['num'], y=rep['y'], d=rep['d']) if rep else None))
C['c09cards'] = cards
print('cards', [(c['f'], c['n'], c['v'], c['pen'], c['changed'], c['rep']) for c in cards])

# ---- profile, tiles
P = dict(head=SHA, built=dt.date.today().isoformat(), acts=len(acts), versions=sum(a['v'] for a in acts.values()),
         files=sum(a['files'] for a in acts.values()), articles=sum(a['n'] for a in acts.values()), words=sum(a['w'] for a in acts.values()),
         runon=len(runon), laws=len(laws), named=sum(1 for L in laws.values() if int(L['commits']) == 0), amend=len(amend_rows),
         commits=len(commits), law_commits=len(law_commits), first=min(a['in_force'] for a in acts.values() if a['f'] != 'loi/2002/02-01'),
         last=max(c['t'].get('In-force', '') for c in law_commits), by_kind=dict(collections.Counter(a['kind'] for a in acts.values())),
         by_inst=dict(collections.Counter(a['inst'] for a in acts.values())), cp_versions=len(cp_v), multi=[f for f, a in acts.items() if a['v'] > 1],
         bad_date=dict(f='loi/2002/02-01', recorded=acts['loi/2002/02-01']['published'], enacted=acts['loi/2002/02-01']['enacted'], jo=acts['loi/2002/02-01']['jo']))
data = dict(profile=P, charts=C, acts={f: dict(fr=a['fr'], en=a['en'], i=a['inst'], k=a['kind'], e=a['enacted'], p=a['published'], y=YEAR[f], n=a['n'], w=a['w'], v=a['v'], jo=a['jo'], t=a['title'][:220]) for f, a in acts.items()})
json.dump(data, open(os.path.join(B, 'data.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('data.json', os.path.getsize(os.path.join(B, 'data.json')), 'bytes', P)
