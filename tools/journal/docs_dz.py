"""Refresh scripts/algeria-law/repo/ README.md, LICENSE and jurisdiction.json from corpus.json + corpus.d (idempotent)."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT.parent / 'gitlaw_common'))
import build as B  # noqa: E402

c = B.load(ROOT)[0]
REPO = ROOT / 'repo'
NL = '\n'

HIST = {
    'constitution': 'As promulgated on 30 December 2020 (Décret présidentiel n° 20-442), 225 articles, the preamble and the two oaths',
    'code-procedure-civile-administrative': 'As enacted by Loi n° 08-09 (in force 23 April 2009, one year after publication), then Loi n° 22-13 of 12 July 2022 as printed in the Journal Officiel n° 48 of 17 July 2022',
    'code-procedure-penale': 'The code of 2025 as enacted by Loi n° 25-14 (Journal Officiel n° 54 of 13 August 2025), 890 articles; the 1966 code it replaced is not included',
    'code-penal': "The Ministry of Justice edition of 2005 (oldest version available), then each amending law printed in the Journal Officiel from 2006 to 2024 (Loi n° 06-23 to Loi n° 24-06), on the day of the issue that printed it",
}


def rows():
    out = ['| Folder | Act | Versions | History |', '| --- | --- | ---: | --- |']
    for a in c['acts']:
        out.append(f"| `{a['slug']}/` | {a['title']} | {len(a['versions'])} | {HIST.get(a['slug']) or 'As enacted, from the Journal Officiel issue that printed it (' + a['versions'][0]['from'] + '); later amending laws applied where they could be matched'} |")
    return NL.join(out)


t = (REPO / 'README.md').read_text(encoding='utf-8').replace('\r\n', NL)
t = re.sub(r'\| Folder \| Act \|[^\n]*\n\| --- [^\n]*\n(?:\|[^\n]*\n?)+', rows() + NL, t, count=1)
SRC_J = ("**Source (amending laws).** Journal Officiel de la République Algérienne, French edition, one issue per amending law, "
         "from https://www.joradp.dz, retrieved 2 November 2026 (text layer, no OCR). Each version applies the articles the law "
         "gives in full; where the gazette leaves part of an article \"(sans changement)\" it is filled in from the earlier text, "
         "and the few articles where that could not be matched keep their earlier text (the version's commit message lists them).")
if '**Source (amending laws).**' not in t:
    t = t.replace('**Source (Constitution).**', SRC_J + NL + NL + '**Source (Constitution).**', 1)
t = re.sub(r'Each commit is dated at noon, Africa/Algiers, on the day the change took effect\.[^\n]*',
           'Each commit is dated at noon, Africa/Algiers, on the day the change took effect. The Constitution of 2020 took effect on its '
           'promulgation and publication, 30 December 2020. An amending law is dated by the issue of the Journal Officiel that printed it '
           '(a law takes effect on publication), unless the law itself sets a later day. Earlier constitutions are not in this record.', t, count=1)
t = t.replace('The one version here is credited to the promulgating decree, Décret présidentiel n° 20-442.',
              'The Constitution is credited to its promulgating decree (Décret présidentiel n° 20-442), and each later version of a code to the amending law printed in the Journal Officiel. A first version that is not the act as enacted is credited to its publisher as the oldest version available.')
lim = ("This is a partial build: the Constitution as promulgated in December 2020; the Code pénal from the 2005 Ministry edition "
       "with the amending laws of 2006 to 2024; the Code de procédure civile et administrative (2008, amended 2022); the Code de "
       "procédure pénale of 2025; and " + str(len(c['acts']) - 4) + " other statutes, each as enacted, with the later amending laws whose articles could all be matched. Amendments that change only some alinéas, phrases or words are applied only where "
       "the gazette's wording can be matched to the earlier text; headings of chapters and sections are not recorded. The Code civil "
       "and the Code de commerce (1975) are printed in gazettes that are scanned images and are not yet included; the rest of Algerian law is not included.")
t = re.sub(r'(## Limits\n\n)[^\n]*', lambda m: m.group(1) + lim, t, count=1)
(REPO / 'README.md').write_text(t, encoding='utf-8', newline=NL)

L = (REPO / 'LICENSE').read_text(encoding='utf-8').replace('\r\n', NL)
LIC = ("The amending laws are the texts printed in the Journal Officiel de la République Algérienne (French edition), Secrétariat "
       "Général du Gouvernement, https://www.joradp.dz, retrieved 2 November 2026. Official texts are not protected by copyright in "
       "Algeria: Ordonnance n° 03-05 du 19 juillet 2003 relative aux droits d'auteur et aux droits voisins, article 11: \"Les lois et "
       "règlements, les décisions et les actes administratifs des organes de l'Etat et des collectivités locales, les décisions de "
       "justice et la traduction officielle de ces textes ne sont pas soumises à la protection des droits d'auteur prévue par la "
       "présente ordonnance.\"")
if 'Ordonnance n° 03-05' not in L:
    k = L.find('Changes made by Lexifina')
    L = L[:k] + LIC + NL + NL + L[k:]
(REPO / 'LICENSE').write_text(L, encoding='utf-8', newline=NL)

jp = REPO / 'jurisdiction.json'
j = json.loads(jp.read_text(encoding='utf-8'))
j['build'] = 'built: ' + '; '.join('%s (%d version%s)' % (a['title'], len(a['versions']), '' if len(a['versions']) == 1 else 's') for a in c['acts'])
j['sources'] = len(c['sources'])
jp.write_text(json.dumps(j, ensure_ascii=False, indent=2) + NL, encoding='utf-8', newline=NL)
print(rows())
