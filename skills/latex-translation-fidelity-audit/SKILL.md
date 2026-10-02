---
name: latex-translation-fidelity-audit
description: "Audit a re-typeset Chinese LaTeX translation of a maths book for fidelity to the original. Covers STRUCTURAL fidelity first (whole missing sections vs the original ToC; bare un-hyperlinked cross-chapter refs like §VI.7.2 / 习题~VI.6.5 / [VI.6.16]; the printed-number-vs-hyperref-anchor trap in .aux; missing or malformed per-section 习题 headings; untranslated section titles; silently dropped glyphs; stale index; FandolFang missing bold-shape fallback) and then LEXICAL/MATH fidelity (operator macros Frob/Nm, fraktur letters, residual untranslated English, digit/degree mistranslations, per-section math-cluster equivalence). Use when a reader has flagged errors, before a final delivery, or during '全面审查' of a math-translation project. Captures the original-PDF ↔ OCR-markdown ↔ translation-.tex comparison strategy, the fragile-$ balance trap (\\erratum{} embeds $), PaddleOCR artifacts, page drift, and the CRLF/heredoc landmines."
agent_created: true
---

# Translation-fidelity audit for a re-typeset LaTeX math book

When a reader reports "several errors in the first pages" or you are doing a final
pass over a Chinese translation of a maths book, run a **three-pronged** audit — in
this order, because each prong costs more than the one before it:

0. **Structural audit (cheapest, highest yield)** — is anything *missing*, and is
   everything *navigable*? Section-count parity with the original ToC, bare
   cross-references, exercise-heading integrity. See "First: structural &
   cross-reference fidelity" below. **Do not skip this to get to the maths.**
1. **Pattern audit (fast, reliable)** — GREP / script scans for known error classes
   (operator macros, fraktur letters, residual English, digit/degree slips).
2. **Cross-source text + math comparison** — compare the translation against
   (a) the original PDF and (b) an OCR markdown of the original, at the
   section/paragraph level (NOT page level — see "Page drift" below).

The bundled `scripts/` make every step reproducible. Run them with the managed
Python: `C:/Users/asus/.workbuddy/binaries/python/versions/3.13.12/python.exe`.

## Environment facts (for this Windows / WorkBuddy setup)

- **Whether `Read` can display an image depends on the running MODEL, not on the tool or the
  machine — probe it, never assume it either way.** Early project notes recorded an absolute claim
  that "Read cannot render PNGs"; that was because **the authoring model at the time was text-only**,
  mistaking its own lack of vision for an environment/tool limitation.
  In reality, image display depends strictly on whether the running model is multimodal or text-only.
  Both states have been observed on this very project: sessions up to 2026-09-13 ran on a text-only model
  and got a refusal (`当前模型不支持图片`); from 2026-09-13 on a multimodal model the *same* `Read` calls render the
  PNG fine. Rendering always works; *looking* may not. So render first, then attempt one `Read`
  on the PNG and branch:
  - **It renders** → multimodal model. Render and *look* whenever a diagram, an arrow direction,
    or a display break is in question — it settles in one glance what text diffing cannot:
    ```
    pdftoppm -png -r 100 -f <first> -l <last> target.pdf <prefix>
    ```
  - **It answers `Content filtered` / `当前模型不支持图片` / refuses the binary** → text-only model.
    Fall back to source-level + text-level evidence, and **say so explicitly** in the report
    instead of implying a visual comparison was made.
  Note the output naming: a **range** produces `<prefix>-<page>.png`, a **single
  page** produces `<prefix><page>-<page>.png`. Mind the printed-page ≠ physical-page
  offset (in the book this was learned on: original = PDF − 21, translation = PDF − 18)
  — always render by *physical* page. Also: `\operatorname{Coker}`-style operator
  names do **not** survive `pdftotext`, so locate a diagram by a Chinese phrase or by
  looking at the render, never by searching for the operator name.
- If image reading is ever unavailable, fall back to PDF **text** extraction
  (`pymupdf`) + paragraph/section math comparison.
- **Write Python scripts to files — never inline regex/heredocs into Bash.**
  The bash shim strips a backslash level, so `python - <<'PY' … PY` and
  `python -c '…\\mathfrak…'` silently corrupt regexes/macros. Always use the
  **Write** tool for anything with a regex, a LaTeX macro, or a Windows path.
- A readable **OCR markdown** of the original is the best comparison source:
  PaddleOCR-VL produces one with print-page markers. But it has systematic
  artifacts (next section). The original **PDF** is authoritative for anchoring
  pages (extract text with `scripts/extract_pdf_text.py`).
- Managed Python already has `pymupdf` (`import pymupdf`).

## First: structural & cross-reference fidelity (cheapest check, highest yield)

Do this **before** any math diff. Polish prose in a book that is missing a whole
section is wasted work, and none of the lexical scans below can see a missing page.

### F1. Section-count parity with the original ToC ← start here

Count the translation's `\section{}` per chapter and compare with the original
book's table of contents. **An entire section can be missing** and nothing else
detects it: both PDFs look complete, the page count is plausible, and the
translation's own in-text references to the missing section compile to dead numbers.
Real case: a Chapter VI translation stopped at §5 while the original has §6 and §7 —
~26 printed pages, 42 numbered items, 42 exercises — **and 7 references to that
missing content were already sitting in five other chapters.**

```
python section_parity.py <project_dir> [--expect "I=6,II=5,III=8,..."]
#                                               ^ read the counts off the original ToC
```

### F2. Bare (never-hyperlinked) cross-chapter references

A hand-made translation routinely types references as plain text: `\S V.3`,
`§VI.7.2`, `习题~VI.6.5`, `[VI.6.16]`, `定义~VI.6.12`, `[8.8, 9.1, III.1.4, VI.6.16]`,
`Exercises VI.4.13 and VI.4.14`, `[VI.7.11, §VII.2.3]`. The PDF *looks* right — the
digits are correct — but they are dead text: no hyperlink, and they do not follow
renumbering. Expect 50–100 spots in a 600-page book; **square-bracket exercise hint
blocks are the densest source** ("[§2.4.3, 4.15 4.16, §IV.6.3]").

```
python aux_number_map.py <project_dir>           # printed number -> label map
python xref_bare_scan.py <project_dir> report    # dry run; read the table
python xref_bare_scan.py <project_dir> apply     # rewrite as \ref (keeps CRLF)
```

Each number needs a *disposition*. The script encodes the ones that mattered:
`§`/`\S` prefix → subsection, else section; a preceding 习题 / Exercise(s) / 定义 /
定理 (Chinese **or** English) → exercise / theorem-like; inside a `[...]` hint block →
exercise (the book's convention); near an existing `\ref{ex:…}` → exercise; otherwise
subsection → theorem → exercise. **Check the ambiguous ones against the original
English** — one bracket can mix kinds, e.g. `[VI.7.11, §VII.2.3]` is exercise +
subsection. Rewrite rule: section/subsection refs become a plain `\ref{label}`
(which carries the chapter number); theorem/exercise refs keep a *literal* chapter
number, `VI.\ref{label}`, because their printed number omits it.

### F3. ★ The number map must come from the PRINTED number, not the hyperref anchor

This trap makes a naive implementation look correct on the chapter you happen to
test with, and wrong everywhere else. Raw `.aux`:

```
\newlabel{def:companion-matrix}{{7.4}{118}{...}{theorem.6.4}{...}}
                                 ^^^                       ^^^^^^^^^
                       printed number                    anchor
```

- **field 1 = `7.4`** — what the book prints; the theorem counter is reset per
  **section**.
- **field 4 = `theorem.6.4`** — the hyperref anchor; the `6` is the **chapter**
  number.

In §VI.6 the two coincide (section 6 == chapter 6), so an anchor-derived map passes
the smoke test; in §VI.7 every single entry is off by one. **Always take field 1.**
Two more traps in the same line: field 3 may contain a nested `\texorpdfstring{…}{…}`,
so the "obvious" regex `\\newlabel\{..\}\{\{..\}\{..\}\{..\}\{..\}\}` truncates —
parse with brace-balanced scanning (backslash-aware, `\{` does not open a group);
and the entry `<label>@cref` must be skipped or it double-counts.

The only reliable way to tell a theorem-like label from an exercise label is the
**counter name** in the anchor (`theorem` vs `probctr`) — not the number shape, since
both print as `sec.item`. In one project 72 labels were shared across both counters
in the same section, so shape alone is genuinely ambiguous.

### F4. Exercise-heading integrity

Every `\section` in the original ends with an *Exercises* heading, and a translation
may render it in five different shapes — several broken:
`\subsection*{习题}` alone (no ToC entry, no anchor); `\begin{center}\textbf{习题}\end{center}`
(foreign style, no ToC entry); a bare `\addcontentsline{toc}{subsection}{习题}` with
**no visible heading at all**; the heading and the `\addcontentsline` on one line; or —
in one real case — **no heading whatsoever** for a section carrying 19 exercises
(the original's page 543 clearly shows `Exercises`; it was a typesetting omission).
`section_parity.py` flags the missing-heading case; fix the anchor/ToC side with the
`latex-bookmark-anchor-audit` skill.

### F5. Residual untranslated *titles*

The body scans (class C below) do not look at headings. Scan titles separately:

```
grep -n '^\\section{[A-Za-z]' chapters/*.tex
```

Real finds: `Short march through applications of Galois theory` → `Galois 理论应用简述`;
`Hom and duals` → `Hom 与对偶`. **Expected false positives**: titles that legitimately
begin with mathematics (`$\End$`, `PID $\Rightarrow$ UFD`, `$A_n$`) — 9 of them in one
book, all correct.

### F6. Silently dropped glyphs — `Missing character` must be 0

Not a mistranslation, but a fidelity error the reader experiences as a blank:
`grep -c 'Missing character' build.log` must be **0**. Real case: a bare `≥` (U+2265)
in **index display text** — the Latin roman font has no such glyph, so the character
simply vanished, with only a log warning. Fix by writing `$\ge$`. Watch the *index*
display layer specifically: a `中文@拼音` → `拼音@中文` swap script must carry a guard
that refuses to move bare mathematics (`_ ^ $ \` or a backslash macro) into the
display layer, or it will inject a real error.

### F7. Index staleness — the build will lie to you

If the printed index lags the body, nothing warns. Check which `.ind` xelatex truly
reads against the name texindy writes:

```
grep -o '(\./main[a-z0-9-]*\.ind' build.log | sort | uniq -c
```

Real case: xelatex read `main-main.ind` while the build wrote `main-min.ind` — for a
month. Every "index has N entries" report had been counting the file nobody used, and
the printed index was 522 entries instead of 546 (missing every entry from newly
translated sections). See `mathtranslation-build-verify` for the `.ind` naming rule.
Related: a summary line like `grep -c '^\\item' main-main.ind` reporting **0** on a
healthy 546-entry index — xindy indents its `\item`s, so the pattern needs
`'^ *\\item'`. An audit script that silently reports 0 is worse than none.

### F8. New labels: grep for duplicates *before* using them, and re-check `undefined` after

Before introducing a theorem/exercise label in newly written content, grep **all**
chapter files for it — `def:faithful` and `ex:rees-algebra` were both real
collisions. And after appending content, never trust the first compile: a `\ref` to a
label you never defined compiles cleanly and renders as a dead `??` number that is
easy to miss among 2000 references. Verify: `0` fatal errors **and** `0` undefined
references, then spot-check the new numbers in the PDF text.

### F9. Chinese emphasis vs bold — the FandolFang missing bold-shape trap

In Chinese math book re-typesetting (especially `ctex` + `fandol`), theorem-like bodies
typically use Fangsong (`\fangsong` / `FandolFang-Regular`). FandolFang provides **no bold
glyph shape**. Writing `\textbf{中文术语}` inside a definition/theorem body produces a log warning
(`Font shape TU/FandolFang-Regular/b/n undefined, using TU/FandolFang-Regular/m/n instead`),
and the text silently falls back to regular weight — **the intended bolding completely fails
to render on the page**.

Standard Chinese typography convention: term definitions and conceptual emphasis in text
and theorem bodies must use `\emph{中文术语}` (which maps to KaiTi/FandolKai or the project's
emphasis font family), providing a distinct, beautiful glyph contrast against both SongTi and
FangSong. Grep for `\textbf` across chapter bodies and ensure terminology emphasis is written as
`\emph{...}`, keeping `\textbf` strictly for Western numerals/labels or display titles.


## The known error classes to scan

### A. Operator macros (Frob / Nm …)
Readers typically catch **wrong operator names**: a translation that writes
`\operatorname{Fr}`, `\operatorname{N}` instead of the project's defined macros
(`\Frob`, `\Nm`). Per the mathtranslation convention, these macros live in
`mycommand.sty` and are **never edited**; overrides (if any) go only in
`main.tex` via `\renewcommand`. Scan with
`scripts/operator_macro_scan.py <dir>`:
- it flags only the canonical wrong names `\operatorname{Fr}` / `\operatorname{N}`
  (extend `ERROR_PATTERNS` in the script only with evidence — do **not** add
  `Hom`/`Aut`/`Res`/`ord`/`Tr`/`Art`, which are legitimate operator names);
- it also prints the FULL inventory of every `\operatorname{X}` token used, so
  you can eyeball whether any other name should have been a project macro;
- it skips `_scratch`/`backup` copies and reports `found: 0` when clean.

### B. Fraktur fonts (𝔭 𝔪 𝔞 𝔟 𝔮 𝔣 𝔨 𝔬 𝔠 𝔗 𝔄 𝔐 𝔓 𝔔 …)
CFT and most algebraic-number-theory books live in fraktur (prime ideals,
orders, modules, ray class groups). A faithful translation must use
`\mathfrak` for the same letters as the original. Scan with
`scripts/fraktur_audit.py <orig.md> <trans_dir>` (pass the project **directory**,
not a single chapter — the script concatenates all `*.tex` and compares
whole-book vs whole-book; a single chapter would show false gaps):

- It counts every `\mathfrak{X}` single letter in each source and prints
  `letter | orig | trans`.
- Real gaps show as a letter present in the original with high count but
  **absent** in the translation (e.g. `\mathfrak{p}` used 500× in orig, 0 in trans).
- **Single-occurrence "only-original" letters are ~always OCR artifacts** — verify
  before flagging. The classic one: the OCR markdown's `\mathfrak{K}(s)` is really
  `\Re(s)` (real part of *s*) in the original; the translation correctly wrote
  `\Re(s)`. Inspect context with `scripts/show_context.py <orig.md> '\\mathfrak\{K\}'`.

### C. Residual English / untranslated prose
A translation must not leave English theorem-like words in the body
(Theorem / Lemma / Proof / Remark / Corollary / Proposition / Definition /
Example / Exercise / Chapter / Section / Appendix). Scan with
`scripts/residual_english_scan.py <dir>`. It **excludes** hits that are:
- inside a `%` comment,
- a `\bibitem` reference line or a `thebibliography` block,
- inside an intentional `\erratum{…}` correction note
  (e.g. "原书此处误作 Lemma 2.15" — these carry English on purpose),
- a book/article **title** (`\emph{…}` span, or a `\noindent Author: \emph{Title}…
  publisher, pp.` reference entry — these carry English on purpose),
- in a `_scratch`/`backup` copy.

Any remaining hit is a candidate untranslated-prose location to inspect.

### D. Digit / degree mistranslations (the reader's most common catch)
Number-theory books hide degree/exponent errors. Spot-check the formula-heavy
spots by GREP for the *expected* correct forms and confirm they are present:
- Lubin-Tate / local class field theory: `$(q-1)q^{n-1}$`, norm
  `$(-1)^{(q-1)q^{n-1}}$`, `$\deg F = p^{n-1}(p-1)$` — and confirm the
  translation applies the author's own errata (e.g. a `\erratum{}` correcting
  "unless q=2 and n=1").
- Quadratic reciprocity exponent `$(-1)^{(p-1)(q-1)/4}$` and the Legendre symbol
  `(\frac{m}{p})` — the translation may use a custom Legendre macro, so search
  loosely (`Legendre`, `\\Leg`, `(q-1)`, `(p-1)`).
- Pell equation `X^2 - A Y^2 = 1`, Fermat `m=4`, etc. — confirm context matches.

### E. Per-section math-cluster comparison (best-effort)
`scripts/math_cluster_audit.py <orig.md> <trans_dir>` extracts math clusters
locally (whole-book) and normalizes them, then reports clusters unique to each source.
**Read its output as a *spot-check*, not a verdict**: PaddleOCR wraps very little
math in `$…$`, so the "orig-only" set is mostly noise (naming diffs like
`\ldots`↔`\dots`, `\frac`→`frac` residue, superscript fragments, custom-macro
differences). The translation's clusters normalizing to expected forms is the
real signal. See "Normalization" for what it equates.

## The fragile-$ trap (why naive math diff fails)

The translation `.tex` has a **globally unbalanced `$` count** because:
- `\erratum{…}` notes embed `$\Q$`-style math, and
- `\[ … \]` displays sometimes nest `$…$` inside.

So any extractor that tries to **balance `$` globally** across a whole file will
swallow whole paragraphs of prose as "math" and drown the result in noise
(the first version of the audit died this way). **Always extract math LOCALLY**,
per delimiter, with `re.findall` on each pattern in turn
(`\$\$…\$\$`, `\$…\$`, `\\\[…\\\]`, `\\\(…\\\)`) — never a stack/balance loop.

## PaddleOCR markdown artifacts (when comparing against the OCR source)

- **Spaced multi-letter command args**: `\operatorname{o r d}`,
  `\mathrm{G a l}`, `\mathrm{m o n i c}`. Normalize by dropping *all* whitespace
  before comparing (`\operatorname{ord}` ≡ `\ord`).
- **`\Re(s)` misread as `\mathfrak{K}(s)`** (real-part *s*). If a fraktur audit
  shows a lone `\mathfrak{K}`, it is this artifact — confirm the translation wrote
  `\Re(s)`.
- **Sparse / incomplete chapter headers** in the markdown — do **not** split the
  markdown by `#` headers to get per-chapter regions; some chapters (III, V) have
  no header. Align per **section/paragraph**, not by markdown header.
- **`-`-prefixed line-break fragments** occasionally appear; harmless to
  normalization.

## Page drift (compare by section, not by page)

The book-PDF ↔ translation-PDF page mapping is reliable **only at a chapter
start**. Within a chapter the translation reorganizes/merges subsections, so
`translation p(N)` does **not** correspond to `original p(M)` body content even
when chapter titles match. Concrete case: translation `main.pdf` p109
(印刷页 91, "局部 Artin 映射") vs original PDF p106 (Chapter III intro + §1
cohomology of units) — titles match, body does not.

**Protocol:**
1. Anchor each chapter by extracting the original PDF chapter-start page
   (`extract_pdf_text.py orig <p>`) and the translation PDF chapter-start page,
   and confirm the opening definitions/theorems match textually.
2. For body content, compare **by section title / theorem statement**, not by
   paired page numbers. Use the OCR markdown paragraph as the "what should be
   there" reference per topic.

## Normalization (what the math comparator equates)

`scripts/math_cluster_audit.py` normalizes each cluster before comparing:
- strip thin/negative spaces `\, \; \: \!` and `~`;
- strip font commands `\mathbb \mathfrak \mathrm \mathbf \mathcal
  \operatorname \text \textbf \mathit \mathsf \mathscr`;
- **strip single-letter macros** `re.sub(r'\\([A-Za-z])', r'\1', s)` so
  `\Q` ≡ `\mathbb{Q}`, `\C` ≡ `\mathbb{C}`;
- remove all braces `{ }` and all whitespace.

This makes `\mathbb{Q}_p` (orig) and `\Q_p` (trans) compare equal, as they must.

## The `is_math` double-gate (to avoid prose false positives)

A raw `$…$` extractor pulls in prose. Keep a cluster only if:
1. it contains a maths signal char (`\ _ ^ 0-9 + - * / | < > . ~ = ( ) [ ]`) **or**
   a Greek letter; **AND**
2. it does **not** contain ≥3 English words of length ≥3 (otherwise it is prose
   wrapped in stray `$`, e.g. `$\mathit{the following lemma}$`).

## Audit checklist (run in this order)

**Structural pass — do this first; it is minutes of work and it finds the worst defects.**

1. `section_parity.py <project_dir> --expect "…"` → per-chapter section count matches
   the original ToC; no section is missing; every section that has exercises has an
   exercise heading (and it carries a `\phantomsection`).
2. `aux_number_map.py <project_dir>` → builds `_auxmap.json` from the **printed**
   numbers. Check the reported anchor-kind inventory: every counter must land in
   section / subsection / theorem / exercise, with nothing unclassified.
3. `xref_bare_scan.py <project_dir> report` → read the table; confirm each
   disposition against the original English. Then `apply`.
4. `grep -n '^\\section{[A-Za-z]' chapters/*.tex` → residual English titles (ignore
   maths-initial titles).
5. After any new content: recompile and require **0** undefined references, and
   `grep -c 'Missing character'` = 0.
6. `grep -o '(\./main[a-z0-9-]*\.ind' build.log | sort | uniq -c` → the `.ind`
   xelatex reads is the one texindy wrote.

**Lexical / math pass.**

7. `operator_macro_scan.py <project_dir>` → expect 0 error-pattern macros.
8. `fraktur_audit.py <orig.md> <trans_dir>` → every high-count fraktur letter
   present in both; investigate any single-occurrence gap with `show_context.py`.
9. `residual_english_scan.py <project_dir>` → expect 0 body hits (only
   comment/bib/erratum excluded).
10. GREP the digit/degree hotspots (class D) for the *correct* forms.
11. `extract_pdf_text.py` to anchor each chapter start; confirm opening text.
12. `math_cluster_audit.py <orig.md> <trans_dir>` as a spot-check.
13. `pdftoppm` + look at the render for every diagram whose arrow direction matters.
14. Finally run a clean build (`mathtranslation-build-verify` skill) and confirm
    0 errors / 0 undefined / 0 missing char / 0 overfull, plus the page count and
    index entry count.

## Gotchas hit in practice

- **A whole section can be missing.** Compare section counts with the original ToC
  before anything else. (F1)
- **Bare cross-references are invisible to the build.** `§VI.7.2` typed as plain text
  renders correctly and links nowhere; bracket exercise hints are the densest source. (F2)
- **`\newlabel` field 1 is the printed number; field 4 is the anchor, numbered by
  *chapter*.** An anchor-derived map is right only where chapter == section. (F3)
- **`<label>@cref` double-counts**; **field 3 may nest `\texorpdfstring`** — use
  brace-balanced parsing, not a fixed-group regex. (F3)
- **Theorem vs exercise labels are told apart only by the counter name** in the
  anchor, never by the number's shape. (F3)
- **`Missing character` is a fidelity defect, not noise** — a glyph with no shape in
  the current font is dropped silently. Must be 0; check the index display layer too. (F6)
- **A summary grep can report 0 on a healthy file** — xindy indents `\item`, so
  `'^\\item'` misses everything while `'^ *\\item'` is right. Never let an audit
  metric silently read 0. (F7)
- **The `.ind` xelatex reads may not be the `.ind` you write** — verify from the log. (F7)
- **A `\ref` to a non-existent label compiles cleanly** and leaves a dead `??` among
  2000 references; grep labels for duplicates before adding, and re-check `undefined`
  after appending. (F8)
- **Model vision capability branching (Read PNG vs text fallback)**: Whether `Read`
  displays an image is a property of the **running model** (multimodal vs text-only),
  not of the tool or the environment. Probe once:
  - If the model is **multimodal** (renders the PNG) → render with `pdftoppm` and inspect
    visually for diagrams, arrow directions, and formula line-breaks. Operator names like
    `\Coker` do not survive `pdftotext`, so locate diagrams by visual inspection or Chinese captions.
  - If the model is **text-only** (returns `当前模型不支持图片` / `Content filtered`) →
    downgrade to geometric measurements (`page.get_drawings()`, bbox coordinates), OCR text diffs,
    and source inspection. State the limitation truthfully in the report.
- **Bash heredoc eats backslashes** → every script in this skill is a file; run
  with the managed Python, never `python -c`/`python - <<'PY'`. The shim also strips
  one backslash level from patterns typed *inline*, so a correct regex can test as
  broken — put the pattern in a file.
- **Editing `.tex` must preserve CRLF**: `open(f,'w',encoding='utf-8',newline='')`
  flattens CRLF→LF across a whole file. Write bytes, or pass `newline='\r\n'`, and
  assert the count afterwards.
- **Narrow globs hide references**: scanning only `chapters/ch*.tex` for
  `\includegraphics` misses `preface.tex` / `coverpage.tex`, and deleting a figure
  believed "unused" then breaks the build. Scan every `.tex` in the project.
- **Global `$` balancing fails** → extract locally per delimiter.
- **OCR `\mathfrak{K}` = `\Re(s)`** → not a translation gap; verify before flagging.
- **Within-chapter page drift** → anchor at chapter start, compare body by topic.
- **OCR spaced command args** → normalize whitespace before comparing.
- **Math-cluster "orig-only" noise** → trust it only as a spot-check, not a verdict.
- **`\erratum{}` intentionally carries English** → exclude from residual-English scan.
