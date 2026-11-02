# Algeria: law history in git

The law of Algeria as a git history: one file per provision, one commit per law on the day it took effect, and the law that made each change as the commit's author. `git blame` names the law behind every paragraph; `git log` lists every change; picking a date gives the text in force that day.

It follows the shared design of [lexifina/global-law](https://github.com/lexifina/global-law).

**What is in it now (a first build, not complete)**

| Folder | Act | Versions | History |
| --- | --- | ---: | --- |
| `constitution/` | Constitution de la République algérienne démocratique et populaire (révision de 2020) | 1 | As promulgated on 30 December 2020 (Décret présidentiel n° 20-442), 225 articles, the preamble and the two oaths |
| `code-penal/` | Code pénal (Ordonnance n° 66-156 du 8 juin 1966), édition du ministère de la Justice, 2005 | 11 | The Ministry of Justice edition of 2005 (oldest version available), then each amending law printed in the Journal Officiel from 2006 to 2024 (Loi n° 06-23 to Loi n° 24-06), on the day of the issue that printed it |
| `code-procedure-civile-administrative/` | Code de procédure civile et administrative (Loi n° 08-09 du 25 février 2008) | 2 | As enacted by Loi n° 08-09 (in force 23 April 2009, one year after publication), then Loi n° 22-13 of 12 July 2022 as printed in the Journal Officiel n° 48 of 17 July 2022 |
| `code-procedure-penale/` | Code de procédure pénale (Loi n° 25-14 du 3 août 2025) | 1 | The code of 2025 as enacted by Loi n° 25-14 (Journal Officiel n° 54 of 13 August 2025), 890 articles; the 1966 code it replaced is not included |

**Language.** The text is in French, the language of the official French edition of the Journal Officiel (the Arabic text is the original). English is not available from the publisher.

**Source (Code pénal).** Ministère de la Justice, Code pénal, 4th edition (Éditions de l'ONTE, 2005), the French column of the bilingual edition, as hosted by UNODC SHERLOC (https://sherloc.unodc.org), retrieved 30 October 2026. The version is dated 23 August 2005, the last amending text it includes.

**Source (amending laws).** Journal Officiel de la République Algérienne, French edition, one issue per amending law, from https://www.joradp.dz, retrieved 2 November 2026 (text layer, no OCR). Each version applies the articles the law gives in full; where the gazette leaves part of an article "(sans changement)" it is filled in from the earlier text, and the few articles where that could not be matched keep their earlier text (the version's commit message lists them).

**Source (Constitution).** Journal Officiel de la République Algérienne no. 82 of 30 December 2020, French edition, from the Secrétariat Général du Gouvernement's site https://www.joradp.dz, retrieved 29 October 2026. Algeria publishes gazettes, not consolidated texts.

## Dates

Each commit is dated at noon, Africa/Algiers, on the day the change took effect. The Constitution of 2020 took effect on its promulgation and publication, 30 December 2020. An amending law is dated by the issue of the Journal Officiel that printed it (a law takes effect on publication), unless the law itself sets a later day. Earlier constitutions are not in this record.

## How it is checked

Every version is read back from git on the day it took effect and on the day before (`tools/check_repo.py`) and must match `corpus.json`; results are in `REPRODUCE.md`.

## What "author" means

The author of a commit is the law that made the change, with an e-mail address that cannot exist (`<law key>@joradp.invalid`). The Constitution is credited to its promulgating decree (Décret présidentiel n° 20-442), and each later version of a code to the amending law printed in the Journal Officiel. A first version that is not the act as enacted is credited to its publisher as the oldest version available. The committer is always Lexifina.

## Limits

This is a partial build: the Constitution as promulgated in December 2020, and the Code pénal from the 2005 Ministry edition with the amending laws of 2006 to 2024. Amendments that change only some alinéas, phrases or words are applied only where the gazette's wording can be matched to the earlier text; headings of chapters and sections are not recorded. The Code civil and the Code de commerce (1975) are printed in gazettes that are scanned images and are not yet included; the rest of Algerian law is not included.
