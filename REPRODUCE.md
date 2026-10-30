# How this repository was made (Algeria)

This file is written by the build on 2026-10-30, the day the source data was retrieved.

## Sources

| Source | Address | Retrieved | Licence |
| --- | --- | --- | --- |
| JORADP, Journal Officiel no. 82 (30 December 2020), French edition | <https://www.joradp.dz/FTP/JO-FRANCAIS/2020/F2020082.pdf> | 2026-10-29 | Official gazette; no licence stated. Attribution to JORADP. |
| Ministère de la Justice (Algérie), Code pénal, 4e édition, ONTE 2005, bilingual (French|Arabic), as hosted by UNODC SHERLOC | <https://sherloc.unodc.org/cld/uploads/res/document/dza/code-pnal-french-arabic_html/code_penal_avec_mod_06.pdf> | 2026-10-30 | Official publication of the Ministry of Justice; no licence stated. Attribution to the Ministère de la Justice. |

Every word of law in this repository comes from these sources. Lexifina reads them and records each act's dated versions, and the laws that made each change, in one corpus file. This repository is built from that file.

## What is in it

| Act | Title | Versions | Span |
| --- | --- | ---: | --- |
| `constitution` | Constitution de la République algérienne démocratique et populaire (révision de 2020) | 1 | 2020-12-30 to 2020-12-30 |
| `code-penal` | Code pénal (Ordonnance n° 66-156 du 8 juin 1966), édition du ministère de la Justice, 2005 | 1 | 2005-08-23 to 2005-08-23 |

The build made 2 commits:

| Commits | Kind |
| ---: | --- |
| 2 | first version of an act |
| 0 | one law on its in-force day |
| 0 | changes no amendment note explains, credited to the publisher |

Other counts:
- 0 commits on the branch `futur`: laws not yet in force on 2026-10-30.
- 0 commits dated 1 January 1970: in force before 1970, with the real day in their `In-force` trailer.
- 3 laws in the record.
- 3 tags.

## Dates

Each commit is dated at noon (Africa/Algiers) on the day the change took effect. The other dates, enacted and published, are trailers.

When a law gives no date of its own, the default rule applies: A law takes effect on publication in the Journal Officiel; the revised Constitution of 2020 was promulgated by Décret présidentiel n° 20-442 of 30 December 2020 and published the same day. https://www.joradp.dz/FTP/JO-FRANCAIS/2020/F2020082.pdf

## How the history is built

`tools/build.py` turns the corpus into this history in one pass: one commit per law, on the day it took effect. The same corpus always gives the same commit hashes. `tools/check_repo.py` reads every version back from git and compares it with the corpus. `tools/on.py` shows the law as it stood on any date. The corpus format is described in `tools/SCHEMA.md`.

- Corpus: sha256 `f36f122b9e53f689a2c3749238d9e123490704892af49436586a001891866056` (463891 bytes).
- Builder blob hashes (`git hash-object`): `build.py` `a4faa25af85facb64b956b372f6b528aafdd7ec1`, `check.py` `3e59cb6f05eccb94a9ec14431a7f6781221e83ef`, `on.py` `644a6c0857fbcc72562032b58d57aa113fee0641`.
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

## What AI did and did not do

The scripts that read the sources and build this repository were written by Claude Code running Claude Opus 5.5 (`claude-opus-5-5`) under Lexifina's direction.

No model wrote, translated or corrected legal text. No model runs at build time. Every word of law in this repository comes from the official sources above.

The commit messages are written by `build.py` from the source data.

Model use at data-build time:
- none
