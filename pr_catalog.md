# PR Catalog — CI Validation Portal
_Organized by feature/fix for future GitHub PRs_

---

## PR 1 — feat: Field Mapper unique values panel

**Summary**
The right-side panel in the Field Mapper tab was showing all blank values when a column was selected. Rows are stored as objects keyed by column name, so `r[idx]` was wrong — changed to `r[selectedCol]`. Panel UI was also restyled to match the Column Explorer: stats bar (Total Rows / Filled / Empty / Complete % / Distinct / Showing), search filter, By Count / A→Z sort toggle, and frequency bars on each value row.

**Files changed**
- `CI_Calculations_Validation_Portal_v1_0.html` — `FieldMapper` component, `colStats` and `uniqueValues` useMemos

**Type:** `bug fix + UI improvement`

---

## PR 2 — chore: Remove Column Explorer tab

**Summary**
Column Explorer tab was made redundant by the unique values panel added to Field Mapper. Tab, its state (`explorerUi`), the `EMPTY_UI` constant, and the stale `setExplorerUi(EMPTY_UI)` call in `handleLoad` were all removed.

**Files changed**
- `CI_Calculations_Validation_Portal_v1_0.html` — tab nav, `App` state, `handleLoad`

**Type:** `cleanup / chore`

---

## PR 3 — feat: Simplify Metrics Catalog to Live Metrics only

**Summary**
Removed the 35-row static reference table from the bottom of the Metrics Catalog page. The only content remaining is the 7 Live Metric cards. Fixed CM-6 (Service From Date) to surface the **earliest** date in the selected column. Fixed CM-7 (Service To Date) to surface the **latest** date in the selected column. `MetricsCatalog` component now simply renders `<LiveMetrics />`.

**Files changed**
- `CI_Calculations_Validation_Portal_v1_0.html` — `MetricsCatalog` component, `LiveMetrics` CM-6/CM-7 logic

**Type:** `feat + bug fix`

---

## PR 4 — feat: Multi-file combine on load

**Summary**
Added ability to select or drop multiple files at once (e.g., 12 monthly `.txt` files) and have them automatically combined into a single dataset. Headers are taken from the first successfully parsed file; rows from all subsequent files are appended. The file input `accept` attribute and label were updated to reflect multi-select support.

**Key implementation details**
- New `parseCSVChunked(text, onProgress, onDone)` function: parses in 5,000-row chunks using `setTimeout` yields to avoid blocking the browser on large files
- `parseNextFile` arrow function chains file parsing sequentially, accumulating rows into `allRows`
- `handleLoad` updated to accept either a pre-parsed `{ headers, rows, delim }` object or a raw string

**Files changed**
- `CI_Calculations_Validation_Portal_v1_0.html` — `parseCSVChunked`, `handleFiles`, `handleLoad`, file input element

**Type:** `feat`

---

## PR 5 — feat: Upload progress bar

**Summary**
Added a visible loading overlay/progress bar during file uploads so the user knows parsing is actively happening. Shows: current file name, file index out of total (e.g., "File 3 of 12"), a row-level progress bar filling as rows are parsed, and a status phase label ("Reading…" / "Parsing…").

**Files changed**
- `CI_Calculations_Validation_Portal_v1_0.html` — `loadStatus` state, `LoadingOverlay` component, `handleFiles` progress callbacks

**Type:** `feat`

---

## PR 6 — fix: Multi-file parsing reliability (headers / silent failures)

**Summary**
Several bugs caused multi-file loading to silently fail or stop early:

| Bug | Fix |
|-----|-----|
| "couldn't read headers from first file" | Restored proven `text.replace(/\r\n/g,'\n').replace(/\r/g,'\n').split('\n')` — `text.split(/\r\n|\r|\n/)` behaved differently on Windows line endings |
| Script killed mid-combine | `parseCSVChunked` now yields via `setTimeout` every 5,000 rows instead of parsing synchronously |
| Page loads blank after progress bar | Ternary `? (` with no false branch was a JS syntax error — changed to `&& (` |
| "Looks like it got to the end but no file loaded" | Added null guard on `firstParsed`; `profileColumns` rewritten as single-pass using `Int32Array` typed arrays and 5,000-row type-detection sampling (was O(rows × cols) per column) |
| Silent errors swallowing all output | Added `try/catch` at both init and chunk level of `parseCSVChunked`; `onDone` is always called |
| `function parseNextFile()` hoisting issue inside arrow fn | Changed to `const parseNextFile = () => {}` |
| Headers array could include empty strings | Added `.filter(Boolean)` after header parse |

**Files changed**
- `CI_Calculations_Validation_Portal_v1_0.html` — `parseCSVChunked`, `profileColumns`, `parseNextFile`, `LoadingScreen` JSX

**Type:** `bug fix`

---

## PR 7 — feat: .txt file support + pipe delimiter auto-detection

**Summary**
Extended file upload to accept `.txt` files in addition to `.csv` and `.tsv`. `detectDelimiter` already handled pipe (`|`) and tab (`\t`) detection; the file input `accept` attribute and the upload UI copy were updated to surface this to the user.

**Files changed**
- `CI_Calculations_Validation_Portal_v1_0.html` — file input `accept`, upload label text

**Type:** `feat`

---

## Notes
- All changes are in a single HTML file (no build step — React via Babel standalone)
- Repo does not yet exist on GitHub; these PRs are staged for when a repo is created under ClaimInformatics
