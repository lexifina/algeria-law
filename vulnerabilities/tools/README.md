# Tools

The scripts behind this Algeria-only run of global-law's vulnerability detectors. They run inside a copy of
[global-law/vulnerabilities/scripts](https://github.com/lexifina/global-law/tree/main/vulnerabilities/scripts) (Python 3.11+,
`pip install duckdb pyarrow`), with a bare clone of this repository at `sources/corpus/algeria-law.git`, a blobless bare
clone of global-law at `sources/global-law.git`, and a `pins.json` that names only algeria-law and its commit.
`build_vulns.py`, `flags_chart.py`, `late_ext_select.py` and `late_ext_rebut.py` sit two folders above the scripts, next to
`config.json`.

| Script | What it does |
| --- | --- |
| `run.sh` | Indexes the history and texts, maps paths to today's folders, adds this repository's history rows, and runs the detectors (`bash run.sh <shards>`) |
| `map_moved.py` | Rewrites every file path from before 11 November 2026, when act folders were renamed (`code-penal/art-023.md` to `code/code-penal/art-023.md`), to its folder today through `data/paths.json`, so each act has one folder through its whole history |
| `add_root.py` | Builds the history rows from this repository's own commits (global-law replays it only up to an earlier commit), so the history detectors read every change |
| `run_triage.sh` | The model review: the 40 strongest flags per category, the 40 strongest lapsed time limits in law texts, and the empty periods (none here) |
| `late_ext_select.py` | Chooses the empty periods for global-law's review of that category (there were none here) |
| `late_ext_rebut.py` | Adds the second, arguing-against pass to the empty-period review, as `triage.py` does for the other categories |
| `build_vulns.py` | Builds `data/flags.csv`, `data/reviewed.csv` and `data/by_category.csv` from the findings and the model review |
| `flags_chart.py` | Draws the chart at the top of the READMEs, in French and English, light and dark |
| `config.json` | The repository, the French category names, the paths that are not law, and the chart's labels |
| `patch_detectors.py` | Fixes blind spots found in runs on several country repositories in the copy of global-law's scripts (`python -X utf8 patch_detectors.py <scripts dir>`; a fix already in place is skipped) |
| `patch_detectors_vi.py` | The Vietnamese fixes made for an earlier run, in the same form (`python -X utf8 patch_detectors_vi.py <scripts dir>`); they change nothing in French text |
| `patch_build_r7.py` | Brings an older `build_vulns.py` up to this one: links an article deleted before the folder move under its old folder (`python -X utf8 patch_build_r7.py build_vulns.py`); not needed here, as this `build_vulns.py` already had it |
| `redo.py` | Runs `patch_detectors.py`, then again only the scans and detectors the fixes change, the model review of lapsed time limits, references to deleted provisions and empty periods, and the build (`python -X utf8 redo.py <run folder> [--keep-reviews]`; `EMBED_FONTS` names the script that embeds the chart's fonts); not needed here, as the fixes were in place before the first run |

The model review needs `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL` and `LLM_AUTH` set for an OpenAI-compatible Responses API.
It was run as `bash run_triage.sh '^(data|tools|vulnerabilities)/'`.

Changes made for this repository:

- `add_root.py` also counts the kinds `decree` and `publisher` as changes to the law: the Constitution as enacted is credited
  to its promulgation decree (Décret présidentiel n° 20-442, kind `decree`), and the Code pénal's first version, the 2005
  edition, to its publisher (kind `publisher`). With them, 172 commits count as law (170 of kind `law`); only the folder move
  of 11 November 2026 (kind `documentation`) is left out. Counting the 2005 edition is what lets the history detectors see the
  articles the 2006 reform of the Code pénal removed: references to deleted provisions went from 3 to 10.
- `pins.json` names the corpus language as `fr` (global-law's list of corpora gave none), so the detectors use the French
  month names and the French currency exceptions.
- `detectors/currency_scan.py` no longer counts the dinar as a dead currency in French-language text (`NOT_CURRENCY["fr"]`
  also drops `dinara?`, which was meant for the dinars of the former Yugoslavia): the Algerian dinar is the current
  currency, and all 39 first flags were fines and fees in dinars ("une amende de 10.000 à 50.000 dinars"). Dead currencies
  went from 39 to 0.
- `detectors/placeholder_ref.py` no longer reads the French noun "abrogation(s)" as a repeal marker (`abrogat\w*` became
  `abrogat(?!ions?\b)\w*`): Article 22 of Loi n° 16-09, which begins "Les effets des révisions ou des abrogations portant
  sur la présente loi…", was taken for a repealed article. References to repealed placeholders went from 3 to 2.
