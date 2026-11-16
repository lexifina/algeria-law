# Algerian law in 20 charts

[Français](README.md)

Charts on every country's law, from the whole of global-law: [global-law visualisations/](https://github.com/lexifina/global-law/tree/main/visualisations). These are the charts on Algeria alone.

Twenty charts on Algerian law, drawn only from the data in this repository: the Constitution as revised in 2020 and on 26 March 2026, six codes and 148 laws, organic laws and ordinances published in the Journal officiel from 2002 to 2026, that is 155 texts and 172 versions, each dated by the day it took effect and credited to the text that made it. The text is that of the French edition of the Journal officiel; 148 texts are here only as enacted, and chart 17 shows what that means.

Open [`le-droit-algerien-en-20-graphiques.html`](le-droit-algerien-en-20-graphiques.html) in a browser. The page is one file with all its data inside; it loads only the d3 library and its fonts from the web. The controls at the top right switch the language (French or English) and the theme (light or dark). Each chart names its data path in the repository, its record count and its limits, and has a table of every number under it. Hover over a mark for the exact values.

The charts are descriptive: they show what the sources record, not why.

## The charts

### I. The repository and the Journal officiel

#### 1. The repository

The 155 texts, each sized by its number of words: 1,045,998 words, 26% of them in the six codes; the longest is the Code of Criminal Procedure of 2025 (80,265 words).

![The repository](stills/en/01.png)

#### 2. Law numbers

Every law number from 2002 to 2026, up to the highest the repository knows: 154 of the 334 laws are in it, as a text or an amendment; only 2012 is complete.

![Law numbers](stills/en/02.png)

#### 3. From signature to the Journal officiel

The time between a text's signature and its publication: 3 days at the median, 2 days since 2020, and 82 days for law n° 05-07 on hydrocarbons.

![From signature to the Journal officiel](stills/en/03.png)

#### 4. Ordinances

The month ordinances, organic laws and laws are signed: 10 of the 13 ordinances in July or August.

![Ordinances](stills/en/04.png)

### II. The Constitution and the organic laws

#### 5. The Constitution article by article

The 226 articles of the Constitution in force: 29 refer to an organic law, 68 to ordinary law, and 13 were changed or added in 2026.

![The Constitution article by article](stills/en/05.png)

#### 6. The revision of 26 March 2026

The words law n° 26-04 removed and added, article by article: 13 articles, 367 words added and 89 removed.

![The revision of 26 March 2026](stills/en/06.png)

#### 7. The institutions the Constitution names

The number of articles that name each institution: the President of the Republic in 65 of the 226, the Constitutional Court in 33.

![The institutions the Constitution names](stills/en/07.png)

#### 8. Organic laws

The 22 organic laws in the repository, matter by matter, and those that repeal others: three electoral systems in nine years.

![Organic laws](stills/en/08.png)

### III. The codes and the Penal Code

#### 9. Six codes

Their articles, their versions and the texts they replace: the Code of Criminal Procedure of 2025 repeals that of 1966, after 59 years; the Penal Code is in its twelfth version.

![Six codes](stills/en/09.png)

#### 10. The Penal Code since 1966

The texts that amended it, from the notes of the 2005 edition and then the git history: at least 20, among them law n° 24-06, which touches 159 articles.

![The Penal Code since 1966](stills/en/10.png)

#### 11. The Penal Code article by article

The text that wrote each of the 708 articles: 366 written or rewritten since 2005; 25 articles that other laws in the repository repeal are still in it.

![The Penal Code article by article](stills/en/11.png)

#### 12. The death penalty in the Penal Code

The articles that punish by death, version by version: 33 in 2005, 23 from 2006 to 2026, 27 since law n° 26-13 of October 2026.

![The death penalty in the Penal Code](stills/en/12.png)

#### 13. Fines in the Penal Code

The highest fine in dinars of each article, version by version: a median of 6,000 DA in 2005, 200,000 DA since 2024.

![Fines in the Penal Code](stills/en/13.png)

#### 14. Article 87 bis

The acts article 87 bis considers terrorist, version by version: 7 in 1995, 15 since 2021.

![Article 87 bis](stills/en/14.png)

### IV. Replacing and amending

#### 15. What the texts in the repository repeal

The 86 older texts they repeal in full, from their date to their repeal: 22 years at the median; 18 are themselves in the repository.

![What the texts in the repository repeal](stills/en/15.png)

#### 16. Replacement laws

The share of articles a text takes over from the one it repeals: 53% for the 2016 electoral law, almost none for most others.

![Replacement laws](stills/en/16.png)

#### 17. After enactment

What the repository applies and what it does not: 17 amendments applied to 7 texts, 23 only named, 18 repealed texts still present, and one law applied to the wrong text.

![After enactment](stills/en/17.png)

### V. The words of the law

#### 18. Outside the Penal Code

The articles that set a penalty in the other texts, by year and by the heaviest penalty: 822, 370 of them in texts of 2020 to 2026.

![Outside the Penal Code](stills/en/18.png)

#### 19. Time limits

The time limits the texts set, from the shortest to the longest: "thirty (30) days" occurs 123 times.

![Time limits](stills/en/19.png)

#### 20. Imprisonment

The ranges of imprisonment, from minimum to maximum: "two to five years" occurs 95 times.

![Imprisonment](stills/en/20.png)

## Data

As of commit `e631376482` (16 November 2026).

| Dataset | Where in the repository | Records | Coverage |
| --- | --- | ---: | --- |
| Git history | branch `main` | 189 commits, 172 of them law | each version on the day it took effect (`In-force:`), from May 2002 to 13 October 2026; the Penal Code from its 2005 edition |
| Articles | `constitution/`, `code/`, `loi/`, `loi-organique/`, `ordonnance/` | 14,546 files; 14,342 articles, 1,045,998 words | the Constitution, 6 codes, 22 organic laws, 114 laws and 12 ordinances, in French |
| Register of laws | `data/laws.csv` | 195 laws | title, dates of signature and publication, issue of the Journal officiel; 25 laws named with no text or version |
| Versions | `data/versions.json`, `data/commits.csv` | 172 versions | 7 texts have more than one, the Penal Code among them (12) |
| Folders | `data/paths.json` | 155 texts | each folder's former name, which the history before 11 November 2026 uses |

## Limits

- **The repository is a selection.** It holds only part of the laws published since 2002 (chart 2), and neither the Civil Code, the Family Code, the Commercial Code, the finance laws, decrees nor case law. Counts by year say what the repository holds, not how much was legislated.
- **"As enacted".** 148 of the 155 texts have one version only: a later amendment is not in them, and a repealed text stays (charts 15 to 17). Counts of words, penalties, time limits and ranges read these texts as enacted, even when repealed.
- **Categories are read from the text.** References to legislation, institutions, penalties, fines, time limits and ranges follow the patterns in `src/prep.py`; a wording they do not recognise is not counted.
- **The repository's errors are flagged, not corrected.** Law n° 02-01 is dated 27 April 1991, before its signature; law n° 08-12, which amends ordinance n° 03-03 on competition, is applied to law n° 03-03 on tourist expansion zones; laws n° 04-06 and 04-09 carry on with the articles of the laws printed after them in the Journal officiel (201 files, counted once).
- **The Arabic text, which is authoritative, is not in the repository**: everything is counted in the French edition.
- **2026 is partial** (to 13 October) and drawn faded.

## Rebuilding

```sh
python visualisations/src/make.py            # history, articles and tables -> src/.build/ -> le-droit-algerien-en-20-graphiques.html
node visualisations/src/stills.cjs           # images for these READMEs (needs Playwright; PLAYWRIGHT=<path> if not global)
```

`make.py` reads everything from git objects, so it also works in a blobless (`--filter=blob:none`) or `--no-checkout` clone, where it fetches the 15,000 or so article files (about 5 MB) in one batch. It reads `origin/main` (or `HEAD`) by default; `--ref` picks another branch or commit. It writes nothing into the repository except the page and the `src/.build/` folder (which git ignores).

| File | What it does |
| --- | --- |
| `src/make.py` | extracts the history, the articles of every version and the tables into `src/.build/`, then runs `prep.py` and `build.py` |
| `src/prep.py` | computes every number for the 20 charts and the data profile into `src/.build/data.json` |
| `src/page.tpl.html` | the page: text in both languages, the charts (d3), the tables |
| `src/build.py` | puts `data.json` into the template and writes the page |
| `src/stills.cjs` | draws each chart as a PNG into `stills/fr/` and `stills/en/` |

## Source and licence

The legal text is that of the Journal officiel of the People's Democratic Republic of Algeria (French edition) and, for the first version of the Penal Code, the Ministry of Justice's 2005 edition. Laws, regulations and their official translations are not protected by copyright in Algeria (ordinance n° 03-05 of 19 July 2003, article 11). The charts, tables and scripts are dedicated to the public domain under CC0 1.0, like Lexifina's other contributions to this repository. See [`LICENSE`](../LICENSE).
