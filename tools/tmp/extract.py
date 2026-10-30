"""Shared: French-column article extraction from Algerian bilingual (French|Arabic) edition PDFs."""
import fitz, re
AR = re.compile('[؀-ۿݐ-ݿﭐ-﷿ﹰ-﻿]')
ART = re.compile(r'^\s*Art(?:icle|\.)?\s*(1er|\d+)(?:\s+(bis|ter|quater|quinquies|sexies|septies|octies|nonies|decies|undecies|duodecies))?(?:\s+(\d+))?\s*[.\-–—:]')
HEAD = re.compile(r'^\s*(LIVRE|Livre|TITRE|Titre|Chapitre|CHAPITRE|Section|SECTION|Paragraphe|Sous-section|PARTIE|PREMIERE PARTIE|DEUXIEME PARTIE|Sous|De la|Des)\b')
def norm(t):
    t = t.replace(' ',' ').replace('’',"'").replace('‘',"'").replace('–','-').replace('—','-')
    return re.sub(r'[ \t]+',' ',t).strip()
def blocks(path, first=0, last=None, xfrac=0.5):
    d = fitz.open(path)
    out = []
    for pn in range(first, last if last is not None else len(d)):
        p = d[pn]
        bl = p.get_text('blocks')
        bl = [b for b in bl if b[6]==0 and not AR.search(b[4])]
        bl.sort(key=lambda b:(-b[0], b[1]))
        for b in bl:
            t = b[4].strip()
            if not t or re.fullmatch(r'\d+\s*(bis)?',t): continue
            out.append((pn+1, t))
    return out

SUF = {'quinquiès':'quinquies','sixiès':'sexies','septiès':'septies','octiès':'octies','noniès':'nonies','décies':'decies','deciès':'decies'}
ART2 = re.compile(r'^\s*Art(?:icle|\.)?\s*(1er|\d+)\s*\.?\s*(bis|ter|quater|quinquiès|quinquies|sexiès|sixiès|sexies|septiès|septies|octiès|octies|noniès|nonies|decies|décies|undecies|duodecies)?\s*\.?\s*(\d+)?\s*(?:\.\s*[\-–—:]?|[\-–—:])\s*(.*)$', re.S)
RANGE = re.compile(r'^\s*Articles?\s+(?:de\s+)?(\d+)\s*\.?\s*(?:à|a)\s*(\d+)\s*\.?\s*[\-–—:]\s*(.*)$', re.S)
HEADB = re.compile(r'^\s*(LIVRE|Livre|TITRE|Titre|Chapitre|CHAPITRE|Section|SECTION|Paragraphe|Sous-section|PREMIERE PARTIE|DEUXIEME PARTIE|TROISIEME PARTIE|QUATRIEME PARTIE|DISPOSITIONS|Dispositions)\s*[IVXLC0-9ère]*\s*$')
def key_label(m):
    n = 1 if m.group(1)=='1er' else int(m.group(1))
    k = f'art-{n:03d}'; lab = f'Art. {n}'
    if m.group(2):
        s = SUF.get(m.group(2), m.group(2)); s = {'sexiès':'sexies'}.get(s,s)
        k += '-'+s; lab += ' '+s
    if m.group(3):
        k += '-'+m.group(3); lab += ' '+m.group(3)
    return k, lab
def parse_articles(bl, start_pred=None):
    units = {}; order = []
    cur = None; paras = []; expect_title = 0; pg_now = [0]; skip_lower = False
    def flush():
        nonlocal cur, paras
        if cur:
            k, lab = cur
            if k in units: print('DUP', k, pg_now[0]); k = k+'-dup'
            units[k] = {'label': lab, 'kind': 'art', 'text': '# '+lab+'\n'+'\n'.join(paras)+'\n' if paras else '# '+lab+'\n'}
        cur = None; paras = []
    for pg, t in bl:
        pg_now[0] = pg
        first = t.split('\n')[0].strip()
        if re.match(r'^(\*|\)\d+\(|\(\d+\)\s*[A-Z]|\d+\s*\)\s)', first) and not ART2.match(t): continue
        lines = [norm(l) for l in t.split('\n') if norm(l)]
        if not lines: continue
        txt = ' '.join(lines)
        for ii, l in enumerate(lines):
            pass
        # a block may begin with heading lines then Art.
        idx = [i for i, l in enumerate(lines) if ART2.match(l) or RANGE.match(l)]
        if idx and idx[0] > 0 and all(not (re.match(r'^[a-zà-ÿ]', lines[0])) for _ in [0]):
            head, lines = lines[:idx[0]], lines[idx[0]:]
            # head lines are headings
            if cur is not None and False: pass
            expect_title = 0
            txt = ' '.join(lines)
        elif not idx and (HEADB.match(txt) or (txt.isupper() and len(txt) < 140) or re.match(r'^(LIVRE|TITRE|Chapitre|CHAPITRE|Section|SECTION|Paragraphe)\b.{0,12}$', txt)):
            expect_title = 2 if HEADB.match(txt) else 1; continue
        if lines and (ART2.match(lines[0]) or RANGE.match(lines[0])):
            # multi-line block: first Art plus any more Art lines
            chunks = []
            for l in lines:
                if ART2.match(l) or RANGE.match(l): chunks.append([l])
                else: chunks[-1].append(l)
            for ch in chunks:
                s = ' '.join(ch)
                flush(); expect_title = 0
                r = RANGE.match(s)
                if r:
                    k = f'art-{int(r.group(1)):03d}-a-{int(r.group(2)):03d}'; lab = f'Art. {int(r.group(1))} à {int(r.group(2))}'
                    cur = (k, lab); paras = [r.group(3).strip()] if r.group(3).strip() else []
                    continue
                m = ART2.match(s)
                cur = key_label(m); paras = [m.group(4).strip()] if m.group(4).strip() else []
            continue
        if expect_title and len(txt) < 140 and not txt.endswith(('.', ':', ';')):
            expect_title -= 1; continue
        expect_title = 0
        if cur is None: continue
        if re.fullmatch(r'\((Loi|Ordonnance|Décret)[^)]*\)', txt): continue
        if paras and re.search(r'[.;:!?»)]$', paras[-1]) and len(txt) < 130 and not re.search(r'[.:,!?]$', txt) and not re.match(r'^[-\d«(]', txt) and not re.match(r'^[a-zà-ÿ]', txt):
            skip_lower = True; continue
        if skip_lower and re.match(r'^[a-zà-ÿ]', txt) and len(txt) < 130: continue
        skip_lower = False
        if re.match(r'^[a-zà-ÿ]', txt) and paras and not re.search(r'[.;:!?]$', paras[-1]):
            paras[-1] += ' ' + txt
        else:
            paras.append(txt)
    flush()
    for u in units.values():
        u['text'] = re.sub(r'(\)) \(\d{1,2}\) ', r' ', u['text']); u['text'] = re.sub(r'(?<=[a-zé])\(\d{1,2}\)', '', u['text'])
    return units
