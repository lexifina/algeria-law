# How this repository was made (Algeria)

This file is written by the build on 2026-11-02, the day the source data was retrieved.

## Sources

| Source | Address | Retrieved | Licence |
| --- | --- | --- | --- |
| JORADP, Journal Officiel no. 82 (30 December 2020), French edition | <https://www.joradp.dz/FTP/JO-FRANCAIS/2020/F2020082.pdf> | 2026-10-29 | Official gazette; no licence stated. Attribution to JORADP. |
| Ministère de la Justice (Algérie), Code pénal, 4e édition, ONTE 2005, bilingual (French|Arabic), as hosted by UNODC SHERLOC | <https://sherloc.unodc.org/cld/uploads/res/document/dza/code-pnal-french-arabic_html/code_penal_avec_mod_06.pdf> | 2026-10-30 | Official publication of the Ministry of Justice; no licence stated. Attribution to the Ministère de la Justice. |
| JORADP, Journal Officiel de la République algérienne, French edition: the issues printing each amending law | <https://www.joradp.dz/HFR/Index.htm> | 2026-11-02 | Not protected by copyright: Ordonnance n° 03-05 du 19 juillet 2003 relative aux droits d'auteur et aux droits voisins, art. 11. |
| JORADP, Journal Officiel n° 21 of 2008, French edition (Loi n° 08-09, code de procédure civile et administrative) | <https://www.joradp.dz/FTP/jo-francais/2008/F2008021.pdf> | 2026-11-02 | Not protected by copyright: Ordonnance n° 03-05 du 19 juillet 2003, art. 11 (laws and their official translations). |
| JORADP, Journal Officiel n° 48 of 2022, French edition (Loi n° 22-13 amending the code) | <https://www.joradp.dz/FTP/jo-francais/2022/F2022048.pdf> | 2026-11-02 | Not protected by copyright: Ordonnance n° 03-05 du 19 juillet 2003, art. 11 (laws and their official translations). |
| JORADP, Journal Officiel n° 54 of 2025, French edition (Loi n° 25-14, code de procédure pénale) | <https://www.joradp.dz/FTP/jo-francais/2025/F2025054.pdf> | 2026-11-02 | Not protected by copyright: Ordonnance n° 03-05 du 19 juillet 2003, art. 11 (laws and their official translations). |

Every word of law in this repository comes from these sources. Lexifina reads them and records each act's dated versions, and the laws that made each change, in one corpus file. This repository is built from that file.

## What is in it

| Act | Title | Versions | Span |
| --- | --- | ---: | --- |
| `constitution` | Constitution de la République algérienne démocratique et populaire (révision de 2020) | 1 | 2020-12-30 to 2020-12-30 |
| `code-penal` | Code pénal (Ordonnance n° 66-156 du 8 juin 1966), édition du ministère de la Justice, 2005 | 11 | 2005-08-23 to 2024-04-30 |
| `code-procedure-civile-administrative` | Code de procédure civile et administrative (Loi n° 08-09 du 25 février 2008) | 2 | 2009-04-23 to 2022-07-17 |
| `code-procedure-penale` | Code de procédure pénale (Loi n° 25-14 du 3 août 2025) | 1 | 2025-08-13 to 2025-08-13 |

The build made 15 commits:

| Commits | Kind |
| ---: | --- |
| 4 | first version of an act |
| 11 | one law on its in-force day |
| 0 | changes no amendment note explains, credited to the publisher |

Other counts:
- 0 commits on the branch `futur`: laws not yet in force on 2026-11-02.
- 0 commits dated 1 January 1970: in force before 1970, with the real day in their `In-force` trailer.
- 16 laws in the record.
- 29 tags.

## Dates

Each commit is dated at noon (Africa/Algiers) on the day the change took effect. The other dates, enacted and published, are trailers.

When a law gives no date of its own, the default rule applies: A law takes effect on publication in the Journal Officiel; the revised Constitution of 2020 was promulgated by Décret présidentiel n° 20-442 of 30 December 2020 and published the same day. https://www.joradp.dz/FTP/JO-FRANCAIS/2020/F2020082.pdf

## How the history is built

`tools/build.py` turns the corpus into this history in one pass: one commit per law, on the day it took effect. The same corpus always gives the same commit hashes. `tools/check_repo.py` reads every version back from git and compares it with the corpus. `tools/on.py` shows the law as it stood on any date. The corpus format is described in `tools/SCHEMA.md`.

- Corpus: sha256 `4688002878a1b7e47b790163d3c5961d08d1e7a871dd3348612e4337e21de35d` (1969947 bytes).
- Builder blob hashes (`git hash-object`): `build.py` `a4faa25af85facb64b956b372f6b528aafdd7ec1`, `check.py` `3d00541d258745461ab52b1b0cb4e1716a27a95d`, `on.py` `644a6c0857fbcc72562032b58d57aa113fee0641`.
- Python 3.12.10; git version 2.46.0.windows.1.

## Checks

Not yet run for this build.

No second build of this corpus has been compared yet.

## Decisions made by hand

- Only the Constitution as promulgated on 30 December 2020 is recorded; earlier constitutions are not included.
- The French translation edition of the gazette is used (text layer); the Arabic original was fetched but not parsed.
- Title and chapter headings are omitted from the units; each article is one file.
- The two oath texts that follow the Constitution in the gazette are kept as units serment-art-090 and serment-art-186.
- code-penal: single 'oldest version available' dated 2005-08-23, the last amending text included in the Ministry of Justice 2005 edition (Ordonnance n° 05-06 of 23 August 2005); the edition itself carries no day. Headings are omitted; each article is one file; amendment attributions in brackets are kept as printed; footnote markers are dropped and footnotes are not recorded.
- code-penal: each later version applies one amending law printed in the Journal Officiel (French edition) to the text before it: an article the law gives in full replaces the earlier one or is added; an article it repeals is removed; parts the gazette marks '(sans changement)' or '(le reste sans changement)' are filled in from the earlier text where they can be matched, and otherwise the article keeps its earlier text and the version note says so.
- code-penal: each amending law is dated by the issue of the Journal Officiel that printed it (the default rule: a law takes effect on publication); none of these laws sets a later commencement.
- code-penal: amendments that replace or repeal only some alinéas, phrases or words, and changes to the headings of chapters and sections, are not applied (headings are not units); the version notes list them.
- code-procedure-civile-administrative: the code as enacted by Loi n° 08-09, dated 2009-04-23, the day art. 1062 sets (one year after publication on 23 April 2008); then Loi n° 22-13 applied as printed in the Journal Officiel n° 48 of 17 July 2022, dated by that issue.
- code-procedure-civile-administrative: headings (livres, titres, chapitres, sections) are not units; each article is one file.
- code-procedure-penale: the code of 2025 (Loi n° 25-14) as enacted, dated by its publication (13 August 2025) under the default rule; the earlier code of 1966 and its amendments are not included.

## What AI did and did not do

The scripts that read the sources and build this repository were written by Claude Code running Claude Opus 5.5 (`claude-opus-5-5`) under Lexifina's direction.

No model wrote, translated or corrected legal text. No model runs at build time. Every word of law in this repository comes from the official sources above.

The commit messages are written by `build.py` from the source data.

Model use at data-build time:
- Claude Code wrote the parsing code and chose the sources; it did not write or alter any legal text. The code is deterministic and runs no model.
- Claude Code wrote the parsing code and chose the sources; it did not write or alter any legal text. The code is deterministic and runs no model.
- Claude Code wrote the parsing code and chose the sources; it did not write or alter any legal text. The code is deterministic and runs no model.
