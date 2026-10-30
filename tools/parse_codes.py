"""Algeria phase 2: adds statutes to the constitution-only corpus.json. Reads .cache only. Idempotent: rebuilds from tmp/corpus.base.json."""
import json, hashlib, re, sys
from pathlib import Path
here = Path(__file__).parent
sys.path.insert(0, str(here/'tmp'))
import extract as e
corpus = json.load(open(here/'tmp'/'corpus.base.json', encoding='utf8'))
only = sys.argv[1:]   # statute slugs to include (default: all that exist)

def sha(p): return hashlib.sha256((here/'.cache'/p).read_bytes()).hexdigest()
def clean(units):
    for u in units.values():
        u['text'] = re.sub(r'\n(Fait à Alger[^\n]*|Houari BOUMEDIENE\.?|Houari BOUMEDIENE)(?=\n)', '', u['text'])
    return units

STAT = {}
def penal():
    f = 'cp06.pdf'
    u = clean(e.parse_articles(e.blocks(str(here/'.cache'/f), 1, 154)))
    return dict(slug='code-penal', short='CP', title='Code pénal (Ordonnance n° 66-156 du 8 juin 1966), édition du ministère de la Justice, 2005',
        url='https://sherloc.unodc.org/cld/uploads/res/document/dza/code-pnal-french-arabic_html/code_penal_avec_mod_06.pdf',
        file=f, units=u, vfrom='2005-08-23', first_law=None, earlier=['ordonnance-66-156', 'ordonnance-05-06'],
        note='Ministry of Justice bilingual edition (4th edition, ONTE 2005), amended through Ordonnance n° 05-06 of 23 August 2005; the French column is recorded.')
STAT['code-penal'] = penal

LAWS = {
 'ordonnance-66-156': ('Ordonnance n° 66-156', 'Ordonnance n° 66-156 du 8 juin 1966 portant Code pénal', '1966-06-08', '1966-06-11'),
 'ordonnance-05-06': ('Ordonnance n° 05-06', 'Ordonnance n° 05-06 du 23 août 2005 modifiant et complétant l\'ordonnance n° 66-156 portant Code pénal', '2005-08-23', None),
}

used = [n for n in (only or STAT) if n in STAT]
corpus['sources'].append({'name': 'Ministère de la Justice (Algérie), Code pénal, 4e édition, ONTE 2005, bilingual (French|Arabic), as hosted by UNODC SHERLOC', 'url': STAT['code-penal']()['url'], 'retrieved': '2026-10-30', 'requests': 1,
  'licence': 'Official publication of the Ministry of Justice; no licence stated. Attribution to the Ministère de la Justice.', 'notes': 'Text layer of the PDF; the French left column only. The PDF ends with annexed amending texts (Loi 06-23 of 2006), which are not recorded.'})
for n in used:
    st = STAT[n]()
    for lk in st['earlier']:
        l = LAWS[lk]
        corpus['laws'][lk] = {'label': l[0], 'title': l[1], 'kind': 'law', 'enacted': l[2], 'published': l[3], 'url': st['url'], 'temporary_until': None, 'restores': None, 'note': None}
    corpus['acts'].append({'slug': st['slug'], 'short': st['short'], 'title': st['title'], 'url': st['url'], 'first_law': st['first_law'], 'earlier_laws': st['earlier'],
        'publisher': {'name': 'Ministère de la Justice (Algérie), Code pénal, 4e édition (ONTE, 2005)', 'email': 'justice@mjustice.invalid'},
        'versions': [{'from': st['vfrom'], 'source_url': st['url'], 'sha256': sha(st['file']), 'units': st['units'], 'credits': {}, 'note': st['note']}]})
    corpus['decisions'].append(f"{st['slug']}: single 'oldest version available' dated {st['vfrom']}, the last amending text included in the Ministry of Justice 2005 edition (Ordonnance n° 05-06 of 23 August 2005); the edition itself carries no day. Headings are omitted; each article is one file; amendment attributions in brackets are kept as printed; footnote markers are dropped and footnotes are not recorded.")
json.dump(corpus, open(here/'corpus.json', 'w', encoding='utf8'), ensure_ascii=False, indent=1)
print({a['slug']: len(a['versions'][0]['units']) for a in corpus['acts']})
