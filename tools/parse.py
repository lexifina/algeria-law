"""Algeria: Constitution of 2020 from JORADP no. 82 (French translation edition). Reads .cache only."""
import json, re, hashlib, subprocess, sys
from pathlib import Path
here = Path(__file__).parent
raw = (here/'.cache'/'F2020082.pdf').read_bytes()
sha = hashlib.sha256(raw).hexdigest()
txt = subprocess.run(['pdftotext','-enc','UTF-8','-layout',str(here/'.cache'/'F2020082.pdf'),'-'],capture_output=True,text=True,encoding='utf8').stdout
lines = txt.split('\n')
start = next(i for i,l in enumerate(lines) if l.strip()=='PREAMBULE')
body = lines[start:]
def clean(l):
    return l
out=[]
for l in body:
    s=l.strip()
    if re.search(r'JOURNAL OFFICIEL DE LA REPUBLIQUE ALGERIENNE',s): continue
    if re.fullmatch(r'30 décembre 2020|15 Joumada El Oula 1442|\d+',s): continue
    if re.search(r'Imprimerie Officielle',s): continue
    out.append(l)
blocks=[]; cur=[]
for l in out:
    if l.strip()=='' :
        if cur: blocks.append(' '.join(x.strip() for x in cur)); cur=[]
    else: cur.append(l)
if cur: blocks.append(' '.join(x.strip() for x in cur))
def norm(t):
    t=t.replace(' ',' ').replace('’',"'").replace('‘',"'")
    t=re.sub(r'\s+',' ',t).strip()
    return t
units={}; order=[]
key=None; label=None; paras=[]
def flush():
    if key: units[key]={'label':label,'kind':'art' if key.startswith('art') else 'preamble' if key=='preambule' else 'other','text':'\n'.join(paras)+'\n'}
HEAD=re.compile(r'^(TITRE|CHAPITRE|SECTION|Section|Chapitre)\b')
def isheading(b):
    return not re.search(r'[a-zà-ÿ]',b) or HEAD.match(b) is not None
for b in blocks:
    b=norm(b)
    if b in ('—————','————'): continue
    m=re.match(r'^(?:Article 1er|Art\. (\d+))\s*[.]?\s*—\s*(.*)$',b)
    if b=='PREAMBULE':
        flush(); key,label,paras='preambule','Préambule',[]; continue
    if m:
        flush(); n=int(m.group(1) or 1); key=f'art-{n:03d}'; label=f'Art. {n}'; paras=[f'# {label}',m.group(2)]; continue
    m=re.match(r"^Traduction des termes du serment prévu à l'article (\d+) de la Constitution",b)
    if m:
        flush(); n=int(m.group(1)); key=f'serment-art-{n:03d}'; label=f'Serment (art. {n})'; paras=[]; continue
    if isheading(b): continue
    if key: paras.append(b)
flush()
assert len([k for k in units if k.startswith('art-')])==225, len(units)
for k,u in units.items():
    u['text']=re.sub(r'\n{2,}','\n',u['text'])
corpus={
 'country':{'code':'DZ','name':'Algeria','slug':'algeria','lang':'fr','tz':'Africa/Algiers','future_branch':'futur',
  'publisher':{'name':'Journal Officiel de la République Algérienne (JORADP), Secrétariat Général du Gouvernement','email':'joradp@joradp.invalid'},
  'default_in_force_rule':{'text':'A law takes effect on publication in the Journal Officiel; the revised Constitution of 2020 was promulgated by Décret présidentiel n° 20-442 of 30 December 2020 and published the same day.','source':'https://www.joradp.dz/FTP/JO-FRANCAIS/2020/F2020082.pdf'},
  'licence_note':'Official text of the Journal Officiel de la République Algérienne no. 82 of 30 December 2020 (French translation edition), https://www.joradp.dz.'},
 'sources':[{'name':'JORADP, Journal Officiel no. 82 (30 December 2020), French edition','url':'https://www.joradp.dz/FTP/JO-FRANCAIS/2020/F2020082.pdf','retrieved':'2026-10-29','requests':1,'licence':'Official gazette; no licence stated. Attribution to JORADP.','notes':'Text layer of the official PDF. Arabic is the original; the JORADP French edition is the translation.'}],
 'laws':{'decret-20-442':{'label':'Décret présidentiel n° 20-442','title':'Décret présidentiel n° 20-442 du 30 décembre 2020 relatif à la promulgation de la révision constitutionnelle adoptée par référendum du 1er novembre 2020','kind':'decree','enacted':'2020-12-30','published':'2020-12-30','url':'https://www.joradp.dz/FTP/JO-FRANCAIS/2020/F2020082.pdf','temporary_until':None,'restores':None,'note':None}},
 'acts':[{'slug':'constitution','short':'Const.','title':'Constitution de la République algérienne démocratique et populaire (révision de 2020)','url':'https://www.joradp.dz/FTP/JO-FRANCAIS/2020/F2020082.pdf','first_law':'decret-20-442','earlier_laws':[],
  'versions':[{'from':'2020-12-30','source_url':'https://www.joradp.dz/FTP/JO-FRANCAIS/2020/F2020082.pdf','sha256':sha,'units':units,'credits':{k:['decret-20-442'] for k in units}}]}],
 'applies':[],
 'decisions':['Only the Constitution as promulgated on 30 December 2020 is recorded; earlier constitutions are not included.','The French translation edition of the gazette is used (text layer); the Arabic original was fetched but not parsed.','Title and chapter headings are omitted from the units; each article is one file.','The two oath texts that follow the Constitution in the gazette are kept as units serment-art-090 and serment-art-186.'],
 'ai_use':['none']}
json.dump(corpus,open(here/'corpus.json','w',encoding='utf8'),ensure_ascii=False,indent=1)
print(len(units))
