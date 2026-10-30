# Algeria: law history in git

The law of Algeria as a git history: one file per provision, one commit per law on the day it took effect, and the law that made each change as the commit's author. `git blame` names the law behind every paragraph; `git log` lists every change; picking a date gives the text in force that day.

It follows the shared design of [lexifina/global-law](https://github.com/lexifina/global-law).

**What is in it now (a first build, not complete)**

| Folder | Act | Versions | History |
| --- | --- | ---: | --- |
| `constitution/` | Constitution de la République algérienne démocratique et populaire (the Constitution, revision of 2020) | 1 | As promulgated on 30 December 2020 (Décret présidentiel n° 20-442), 225 articles, the preamble and the two oaths |
| `code-penal/` | Code pénal (Ordonnance n° 66-156 du 8 juin 1966) | 1 | The Ministry of Justice edition of 2005, amended through Ordonnance n° 05-06 of 23 August 2005; the oldest version available (the edition carries no day) |

**Language.** The text is in French, the language of the official French edition of the Journal Officiel (the Arabic text is the original). English is not available from the publisher.

**Source (Code pénal).** Ministère de la Justice, Code pénal, 4th edition (Éditions de l'ONTE, 2005), the French column of the bilingual edition, as hosted by UNODC SHERLOC (https://sherloc.unodc.org), retrieved 30 October 2026. The version is dated 23 August 2005, the last amending text it includes.

**Source (Constitution).** Journal Officiel de la République Algérienne no. 82 of 30 December 2020, French edition, from the Secrétariat Général du Gouvernement's site https://www.joradp.dz, retrieved 29 October 2026. Algeria publishes gazettes, not consolidated texts.

## Dates

Each commit is dated at noon, Africa/Algiers, on the day the change took effect. The Constitution of 2020 took effect on its promulgation and publication, 30 December 2020. Earlier constitutions are not in this record.

## How it is checked

Every version is read back from git on the day it took effect and on the day before (`tools/check_repo.py`) and must match `corpus.json`; results are in `REPRODUCE.md`.

## What "author" means

The author of a commit is the law that made the change, with an e-mail address that cannot exist (`<law key>@joradp.invalid`). The one version here is credited to the promulgating decree, Décret présidentiel n° 20-442. The committer is always Lexifina.

## Limits

This is a first build: the Constitution as promulgated in December 2020 and the Code pénal as of 2005 (later amendments are not included). Any later amendment and the rest of Algerian law are not included.
