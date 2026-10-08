---
name: mathtranslation-build-verify
description: "Build and verify a LaTeX translation using its actual toolchain; inspect logs, rendered pages, numbering, bookmarks, glyphs, bibliography, and indices. Use after TeX/template changes or for build diagnosis. The bundled driver supports a conventional XeLaTeX, biber, texindy workflow; other projects retain their own build commands."
metadata:
  agent_created: true
---

# Build And Verify A LaTeX Translation

## Environment And Scope

Use the project's actual build driver and inspect the supplied class/version.
Historical recipes below are conditional examples, not facts about this machine.
Discover Python, TeX binaries, fonts, and shell capabilities locally. The bundled
driver finds tools on PATH or in `TEXLIVE_BIN`; it must not assume a private
installation path. Verify whether the project needs biber, bibtex, texindy,
makeindex, or a custom index driver before selecting the fallback sequence.

Preserve UTF-8 encoding and existing line endings. If log bytes are not UTF-8,
decode them using the actual producer's encoding; retain original logs for diagnosis.
If non-ASCII paths or PDF write locks cause failure, diagnose those conditions
from the current tools rather than assuming every shell or platform has the issue.
Use absolute paths and an explicit working directory for background jobs.

Render changed pages and inspect them when image tools are available. If direct
visual inspection is unavailable, report that limitation. Check algorithm and
listing pages too: their source-language keywords, indentation, line numbers,
and symbols must survive the build. Compilation is not a proof of translation,
mathematical, or algorithmic correctness.

## Build the document

For the conventional fallback below, use enough XeLaTeX passes to resolve all generated data; respect the actual project driver.
**If the project has an index (`\makeindex` / `main.idx`), it is 5 steps, not 3** — see below.

```powershell
$d = "<the directory containing main.tex>"
Set-Location $d
Remove-Item "main.aux","main.bcf","main.log","main.out","main.toc","main.run.xml" -ErrorAction SilentlyContinue
& "xelatex" -interaction=nonstopmode -file-line-error main.tex *> "build1.log"
if (Test-Path "main.bcf") { & "biber" main *> "build_biber.log" }
& "xelatex" -interaction=nonstopmode -file-line-error main.tex *> "build2.log"
& "xelatex" -interaction=nonstopmode -file-line-error main.tex *> "build3.log"
```

- `-file-line-error` is what makes `./file.cls:69: message` appear — keep it.
- Do **not** use `-halt-on-error` while diagnosing: you want to see every error in one run.
- Judge success on **build3**, not build1 (`Citation undefined` in pass 1 is normal).

### Index step (omit only if there is no `main.idx`)

`texindy` must run **between** the passes that write and read `main.ind`, i.e. the real order is
`xelatex → biber → xelatex → texindy → xelatex` (5 steps). Skipping it does **not** error — LaTeX
silently re-uses the *previous* `main.ind`, so the printed index keeps stale/`??` page numbers and a
"successful" build is actually wrong. **Treat a missing `texindy` step as a silent-corruption bug.**

`texindy` is a Perl script and **dies on a UTF-8 locale** (`perl: warning: Setting locale failed`,
exit code 2, no `main.ind` written). Always force the C locale for this one step:

```powershell
$env:LC_ALL="C"; $env:LANG="C"; $env:LC_CTYPE="C"
& "texindy" -M texindy -I xelatex -C utf8 main.idx
Remove-Item Env:LC_ALL,Env:LANG,Env:LC_CTYPE
```

Verify afterwards: `main.ind` exists **and** its `\indexentry` lines carry real page numbers.
Then confirm on the rendered index page that numbers are printed, not `??`.

> **The `imakeidx` warning "Remember to run xelatex again after calling texindy" is NOT evidence that
> the index is stale — it is timestamp-based and fires on every build**, because each `xelatex` pass
> rewrites `main.idx` and thereby makes it newer than `main.ind`. Settle it by **content, not by the
> warning**: hash `main.idx`, rerun `texindy` (C locale) and hash `main.ind` — if that hash is
> unchanged, the index already matches the aux page numbers; then rerun `xelatex` and hash `main.idx`
> again — if unchanged too, the run has converged and you stop. Do **not** enter a build loop chasing
> this message.

### Do NOT pass `-output-directory` when the project path is non-ASCII

`xelatex -output-directory="D:\…\中文目录"` fails fatally before doing any work:

```
! I can't write on file `main.log'.
... putenv(TEXMF_OUTPUT_DIRECTORY=…) …
```

and returns non-zero with no PDF. TeX cannot handle the non-ASCII value in the environment
variable. **Fix: don't pass the flag at all.** Change the *working directory* instead
(`Set-Location $d` / `subprocess.run(..., cwd=$d)`); every tool then writes to cwd by default.

Independently of the non-ASCII failure, `-output-directory` is also a **silent-staleness trap**:
it redirects the PDF/aux/TOC to the given directory while the `bookmark`/`.out` write can land
elsewhere (or not happen), so the freshly written PDF embeds an **old bookmark tree** — the PDF and
`.aux` get new mtimes and only `.out` stays stale. Always build with cwd = project dir and no
`-output-directory` flag.

### Bundled Fallback Driver

Run `python scripts/build_and_check.py <project_dir>` from this skill directory
only for projects compatible with its XeLaTeX/biber/texindy sequence. It writes
`_build_report.txt` and returns failure for failed build steps or reported defects.
It is not a replacement for a supplied driver with custom bibliography or indices.
For file-backed commands, keep regexes and LaTeX strings out of ambiguous nested
shell quoting. Inspect process return codes as well as the final log.

## Scan the log

```powershell
$t = [System.IO.File]::ReadAllText("$d\build3.log", [System.Text.Encoding]::GetEncoding(28591))
$ls = $t -split "`r?`n"
"errors: "   + ($ls | Where-Object { $_ -match '^! ' -or $_ -match ':\d+: ' }).Count
"overfull: " + ($ls | Where-Object { $_ -match '^Overfull \\hbox' }).Count
"missing char: " + ($ls | Where-Object { $_ -match 'Missing character' }).Count
$ls | Where-Object { $_ -match 'undefined|Output written' }
```

A clean verdict looks like: `LaTeX Error` = 0, `Overfull/Underfull \hbox` = 0,
`Missing character` = 0, `Font shape ... not available` = 0, `undefined` = 0 on pass 3.

> **TRAP — `grep -c '^! '` is NOT a sufficient error check.** Under `-file-line-error`
> (which you are told to keep above) most errors are printed as
> `./chapters/ch04.tex:665: Missing } inserted.` — **no leading `!`**. A build that
> returns non-zero and shows a *real* error can therefore still report
> `grep -c '^! ' main.log` == 0, and you will declare it clean. This has silently
> hidden a genuine `Missing } inserted.` for several rounds in a real project.
> **Always grep BOTH patterns** — `grep -cE '\.tex:[0-9]+:' main.log` *and*
> `grep -c '^!' main.log` — and require both to be 0. `-file-line-error` is the
> whole reason the `^! ` form stops being reliable, so the two go together.

`Missing character` is the one to take seriously with `fontset=none`: it means a CJK font was
never assigned (`\setCJKsansfont` / `\setCJKmonofont` missing) and text silently vanished.

> **TRAP — `Font shape … undefined` can hide a silent *emphasis* failure.** TeX substitutes silently
> and warns only **once per shape**, so a build reporting `errors: 0` can still be typesetting
> something wrong. Concrete case (AJbook.cls): `\theorembodyfont{\fangsong}` puts every
> theorem / lemma / proposition / **definition** body in FandolFang — which ships **no bold face**.
> A CJK `\textbf{…}` inside such a body is therefore typeset at *normal* weight with no error at all;
> the only trace is one line,
> `LaTeX Font Warning: Font shape 'TU/FandolFang-Regular(0)/b/n' undefined`, and the defined term
> ends up visually indistinguishable from its surrounding text.
> **Fix by convention, not by adding a font:** in these bodies use `\emph` — under ctex it maps CJK to
> 黑体 (`FandolHei-Bold`) and does emphasise. **Verify by font name, never by eye:** read the span out
> of the PDF and assert the family —
> `for l in page.get_text("dict")["blocks"]…: [s["font"] for s in l["spans"]]` — `FandolHei-Bold`
> means emphasised, `FandolFang-Regular` means the emphasis was dropped. Cheap sweep: for each
> fangsong-bodied environment, list every `\textbf` / `\emph` / `\bfseries` whose argument contains
> CJK (`[\u4e00-\u9fff]`), then check those spans in the rendered PDF.

## Visual verification (mandatory before reporting success)

Write a small script and run it with the managed Python:

```python
import os, pymupdf
d = r"<dir>"
doc = pymupdf.open(os.path.join(d, "main.pdf"))
out = os.path.join(d, "_verify"); os.makedirs(out, exist_ok=True)
print("pages", doc.page_count)
for i in [0, 1, 2, doc.page_count - 1]:          # cover / body / TOC / last page
    doc[i].get_pixmap(dpi=110).save(os.path.join(out, "page%02d.png" % (i+1)))
    print("=== page", i+1, "==="); print(doc[i].get_text().strip())
```

Then `Read` the PNGs — **only if the probe above showed the running model is multimodal**; on a
text-only model see the environment facts instead of pretending to look. Check, at minimum:

- **Cover**: title, author, logo actually resolved (not the `LOGO` placeholder box), imprint line.
- **TOC**: `第 X 章` prefix on numbered sections and `附录 X` after `\appendix`.
- **Terminology index** (last page): rows present and page numbers filled (not `??`).
- **Cross-references**: `\autoref` / `\eqref` render as `引理1.1.1` / `式(1)`, never `??`.

Also compare page count against a pre-change backup to catch a silently dropped section.

## Typography / font changes: decide with a probe, then measure

Never argue a font pairing from intuition. Two cheap techniques:

**A. Variant probe.** Write a throwaway `.tex` that renders the *same* string under each candidate
font command on a single page, compile once, then rasterise a **cropped, magnified** region —
`get_pixmap(matrix=pymupdf.Matrix(z, z), clip=pymupdf.Rect(...))` with `z` around 5. A full page at
100 dpi is far too small to judge stroke weight or 衬线 details. Locate the crop with
`page.search_for("<marker>")` rather than guessing coordinates. Pick from the image, *then* edit the
real class, then re-verify the real document.

**B. Measure the rendered result.** `page.get_text("rawdict")` returns a bbox per glyph, which turns
"did the punctuation backspace survive the font swap?" into a number instead of an opinion:

```python
for b in pg.get_text("rawdict")["blocks"]:
    for l in b.get("lines", []):
        cs = [(c["c"], c["bbox"]) for s in l["spans"] for c in s["chars"]]
        # cs[i][1][2] = right edge of glyph i ; cs[i+1][1][0] = left edge of the next one
```

The bbox is the **advance box, not the ink** — for a full-width CJK glyph it is the whole em
(a Fandol 「：」 measures 11.96 pt at 12 pt). So compare like with like, and compare the same
measurement before/after the change. Useful consequence: Fandol's Song and Hei share punctuation
metrics, so a spacing constant tuned for 宋体 still holds after switching to 黑体.

## Reducing Overfull boxes in a narrow text block (115 mm / 327.4 pt)

Long display formulas from a printed book rarely fit a 115 mm measure. Work **measurement-driven**,
never by character count — math width is not linear in characters.

1. **Measure every display row in pt.** Write a probe `.tex` that `\sbox`es each row in
   `\ensuremath{\displaystyle ...}` and emits `\typeout{MEAS|tag|\the\wd\mb}`; compile once
   (`-no-pdf`) and parse `MEAS|...|NNN.NNpt`. The probe preamble must mirror the real one
   (fontspec + `unicode-math` + `mathtools`), and must define any project-local macros the rows
   use, or the recovered width is garbage.
2. **Drive the breaker from those widths.** A row wider than the measure gets split at a top-level
   relation sign (`=`, `\le`, `\to`, …), preferring the last sign that keeps the first piece
   inside budget. Prefer breaking a *whole display* by wrapping it in `aligned`; a row already
   inside `align*`/`aligned` gets an extra `\\` + `&` continuation row.
3. **`aligned` computes ONE column width from the widest cell-1.** If one row puts a long
   expression before its first `&`, every other row's cell-2 is pushed right by that width and the
   whole block overflows even when each row measured alone fits. Fix: keep cell-1 empty — every
   row is written `&<content>`.
4. **`\label`/`\tag` stay OUTSIDE the `aligned`**; strip them before splitting and re-attach.
5. Iterate: recompile → re-measure → re-split. Guard every iteration with a `\label`→number
   snapshot diff so re-typesetting can never silently renumber equations.
6. Expect a residual tail in shapes that resist mechanical splitting: side-by-side `cases`, already
   balanced `multline*`, and prose-in-display. Judge those individually; pushing them to zero moves
   the text further from the source layout than it is worth.

## PDF bookmarks (the `.out` file): verify from the built PDF, never only from `main.out`

`hyperref` writes the bookmark tree to `main.out`; the PDF embeds it. Three failure modes bite here:

- **A starred heading (`\section*`, `\chapter*`) creates NO anchor of its own.** With
  `\section*{T}` + `\addcontentsline{toc}{section}{T}` and no `\phantomsection`, the bookmark
  inherits the anchor of the **previous** numbered environment (`Item.11`, `proposition.1`, a
  theorem, an `exercise`), so it is mislabelled *and* jumps to the wrong page — and two such
  headings can even collide on one anchor, producing a dead duplicate. Fix: (a) put
  `\phantomsection` immediately before the `\addcontentsline` of every `\chapter*` front/back-matter
  heading — **and never before the starred heading itself**. The order is
  `\subsection*{T}` → `\phantomsection` → `\addcontentsline{...}`, and the failure mode of getting
  it wrong is intermittent and misleading: `\phantomsection` samples the position at once, so if
  the following `\section*` happens to trigger a page break, the anchor stays on the *old* page
  while `\addcontentsline` samples `\thepage` on the *new* one — TOC page number correct, bookmark
  one page early. Measured at 20 of 63 entries in a real book; it reads like an off-by-one
  *page-offset* bug and will send you chasing the offset constant instead. (Dedicated treatment:
  skill `latex-bookmark-anchor-audit`.) (b) for in-chapter subheadings, define `\newcommand{\subsec}[1]{\section{#1}}` and use a
  numbered `\section` — it creates its own anchor *and* restores the printed `x.y` numbering. Do
  **not** hand-roll a counter + `\pdfbookmark`; under this toolchain that silently emits nothing.
- **The `bookmark` package can silently stop writing `.out` under xelatex.** It loads
  `bkm-dvipdfm.def` (dvipdfm backend) even though hyperref correctly picked `hxetex.def`, and
  `main.out` is then **never rewritten** — every rebuild embeds the *stale* tree, which looks exactly
  like "I fixed the source but the bookmarks did not change" (the PDF/aux/TOC all get fresh mtimes,
  only `.out` stays old). Fix: drop `\usepackage{bookmark}` and rely on hyperref's native
  `bookmarksnumbered` / `bookmarksopen` / `bookmarksopenlevel` in `\hypersetup`. Prove it by
  deleting `main.out`, rebuilding, and confirming it is recreated.
- **`\printindex` ordering.** `\phantomsection` must come **before** `\printindex`, otherwise the
  "Index" bookmark lands past the index (its last page). Since `theindex` opens with
  `\twocolumn[...]` (which starts a fresh page), a bare reorder is not enough — you also need
  `\cleardoublepage` first:
  `\cleardoublepage \phantomsection \addcontentsline{toc}{chapter}{Index} \printindex`.

**Verify against the PDF, not the log.** `main.out` proves what was *written*; only the PDF proves
what a reader sees. With PyMuPDF:

```python
import pymupdf
d = pymupdf.open("main.pdf")
print(d.page_count, len(d.get_toc()))
for lvl, title, page in d.get_toc():          # page is 1-based
    ...
```

Sanity-check every level-1 bookmark by asserting its heading keyword appears on the target page
(allow ±1 page for a heading sitting near the top of the next page). One wrong target — e.g. `Index`
pointing at the last index page instead of the first — is the entire bug.

## Gotchas hit in practice

- **★ The index processor's `-o` filename must be the file `\printindex` actually `\input`s —
  otherwise the PDF index is silently frozen.**
  With `imakeidx` + `splitindex` + `noautomatic`, for a job `main` and the DEFAULT index, LaTeX
  reads **`main-main.ind`** (visible in the log as `(./main-main.ind [605] [606] …)`); a second
  named index `sym1` reads `main-sym1.ind`. A build script that runs
  `texindy -o main-min.ind main-main.idx` looks perfectly healthy — file written, non-zero size,
  plausible entry count — while **no step reads `main-min.ind`**, so the shipped PDF keeps
  whatever `main-main.ind` was produced last time. In the project where this was found the
  noun index was **28 days stale** (522 top-level entries instead of 546; every term added in the
  meantime missing from the PDF), and several earlier "index has N entries" measurements had been
  taken from the unused file, so the regression stayed invisible.
  **Detection (30 seconds):** `grep -o '(\./main[a-z0-9-]*\.ind' <job>.log | sort | uniq -c` —
  compare against the files your script writes; then compare `ls -la` timestamps of the `.ind`
  files against the last build, and confirm a term you just added appears in the rendered PDF
  (`pdftotext -f <idxpage> -l <last> <job>.pdf - | grep <term>`).
  **Fix + guard:** write to the correct name AND put it in the build's cleanup list, so a stale
  survivor cannot be reused after a failed run. Do not rely on "some later step renames it".
- **`&` at the END of a line inside `aligned`/`align*` is a fatal trap when `mathtools` is loaded.**
  Writing
  ```
  \begin{aligned}&
  \int\cos(\beta x)\,dx = \dots\\
  \end{aligned}
  ```
  (cell content starting on the *next* line) dies with
  `! Missing control sequence inserted. <inserted text> \inaccessible`,
  because the newline becomes a space token at the start of the alignment entry and amsmath's
  `\@ifnextchar` look-ahead misreads it while scanning the `\halign` template.
  It only fires when the affected cell later contains a **top-level math operator** (`\cos`,
  `\sin`, `\log`, …); `\cos` nested inside `\frac{}{}` is safe, and so is a cell with no operator.
  **The same file compiles fine with plain `amsmath` and no `mathtools`** — which is exactly why a
  minimal standalone probe can pass while the real document fails. `mathtools` plus a
  leading-`&` `aligned` is the reproduction recipe.
  **Fix:** never leave `&` at end-of-line; write `&<content>` on one line. The reverse of this trap
  also holds, so when a `&`-heavy block suddenly fails at a line that looks perfectly legal, suspect
  an *earlier* line ending in `&` first.
- **Diagnosing "the same code works in a probe but fails in the document": bisect both axes.**
  (a) `\errorcontextlines=99` then recompile — the printed context names the macro being expanded
  (`<template> ...` + `\@ifnextchar` pointed straight at the alignment machinery).
  (b) Run the block under the *real* preamble (`\usepackage{<project>.sty}`) vs. plain `amsmath`;
  the delta is the culprit package.
  (c) Run the same block with and without a newline after `&`; one token is the whole difference.
- **`\ProcessKeyvalOptions*` takes NO argument.** The family comes from `\SetupKeyvalOptions`.
  Writing `\ProcessKeyvalOptions*{MT}` makes TeX typeset `{MT}` in the preamble and raises
  `LaTeX Error: Missing \begin{document}.` at that exact line. Correct forms:
  `\ProcessKeyvalOptions{MT}` (unstarred, needs the family) or `\ProcessKeyvalOptions*` (starred).
- **`\IfFileExists` does NOT consult `\graphicspath`.** A class that sets
  `\graphicspath{{graphics/}}` and then tests `\IfFileExists{logo.pdf}` will take the *false*
  branch while `\includegraphics{logo.pdf}` would have worked. Test explicit candidates.
- **A bare `\par` must never appear inside a `\titleformat` argument.** titlesec's
  `\ttl@format@ii` is not `\long`, so scanning hits the `\par` and reports
  `Paragraph ended before \ttl@format@ii was complete`, followed by cascading
  `Too many }'s` and `Missing \begin{document}` — the reported line is the one *containing* the
  `\par`. Wrap the code in a `\newcommand` and call that instead.
- **Do not hand-roll a "第 X 章" TOC prefix on ctex classes.** `ctexbook`/`ctexrep`'s `\@chapter`
  already writes `\numberline{\CTEXthechapter\hspace{.3em}}` into the `.toc`, and `\appendix`
  turns it into `\numberline{附录 A\hspace{.3em}}` by itself. A custom `\numberline` override
  prints *both*, overlapping. Check `main.toc` before writing any TOC styling.
  The same trick exists for other levels via `\CTEXnumberline`.
- **`ctexbook` has no `\maketitle`** (only the `article` family does). Use
  `\providecommand{\maketitle}{}` before `\renewcommand{\maketitle}{...}`.
- **Moving an article-style class to `ctexbook` renumbers equations** from global `(1)` to
  per-chapter `(1.1)` — that is book-class default. Revert with
  `\counterwithout{equation}{chapter}` if the project wants global numbering.
- `ctex` + `titlesec` do coexist (ctex ships an explicit `\ctex_at_end_package:nn{titlesec}`
  hook), but ctex's own `\ctexset{chapter=...}` settings are bypassed once you call
  `\titleformat{\chapter}`.
- **To restyle a TOC level's font, `\patchcmd` the `\bfseries` — never rewrite `\l@chapter`.**
  `\l@chapter` / `\l@part` in the `book` family carry the label width (`\@tempdima`), the penalties
  and the dotted-leader logic; a hand-written replacement silently changes all of that (and on ctex
  it collides with the `\numberline` above). In `\AtBeginDocument`:
  `\patchcmd{\l@chapter}{\bfseries}{\headfont}{}{\typeout{MT-WARN: patch failed}}` swaps only the
  font token. **Always give `\patchcmd` a failure branch that `\typeout`s** — that is how you learn
  a future LaTeX release moved the `\bfseries`.
- **A class with heading font options needs an in-page CJK font family, not `\sffamily`.**
  With `fontset=none`, `\sffamily` silently falls back to the Latin sans for CJK. Define the family
  explicitly, e.g. `\newCJKfontfamily\heifont{FandolHei-Regular.otf}[BoldFont=FandolHei-Regular.otf]`
  — mapping `BoldFont` back to the regular keeps the CJK at normal weight while `\bfseries` still
  bolds the Latin. Resolve a string class option into a font command inside `\AtBeginDocument`
  with etoolbox's `\ifdefstring`, otherwise you hit a load-order problem (the option exists before
  the font families do).
- **`@` is already catcode 11 inside `.cls`/`.sty`.** `\makeatother` there *breaks* every later
  `\@`-macro; never use the pair in a class file.
- **Preserve script encoding when paths contain non-ASCII characters.** Use the
  current shell's supported encoding or a file-backed Python driver.
- **Back up the existing `main.pdf`** (`main.pdf.bak`) before the first rebuild, and delete the
  backup plus all `_*.log` / `_*.txt` / `_verify/` scratch afterwards. Leave `main.aux/.bcf/.toc/
  .run.xml/.blg/.bbl` in place — they are normal build artifacts.
- If a `.cls` is shared, remember the **class file must sit next to `main.tex`** (or on
  `TEXINPUTS`); a copy at the workspace root will not be found when compiling from a nested dir.
- **A class that redefines `\[`→`equation*` and `\qedhere`→`\tag*` breaks two things at once**, both
  reported as `Package amsmath Error`:
  (a) **`align*` must NOT be wrapped in `\[ \]`** — nesting it inside `equation*` gives
  `Erroneous nesting of equation`. Make the `align*` a *top-level* display (drop the outer `\[ \]`).
  (b) **`\qedhere` is illegal *inside* `aligned`** (→ `\tag not allowed here`); write
  `\end{aligned}\qedhere` so the `\tag*` lands at the `equation*` level (or put it on the last row of
  a top-level `align*`). A `Missing $ inserted` a few lines later is usually just the cascade.
- **A macro that `\sbox`es its argument captures it in TEXT mode.** If callers pass raw math you get
  `Missing $ inserted` / `Undefined control sequence` on a line that looks perfectly fine. Fix at the
  **call site** by wrapping math args in `$...$` (match the class's own documented usage), not by
  editing the macro (which would then mis-typeset genuinely-textual arguments).
- **`\xlongequal` may simply be undefined** if the class deliberately avoids mathtools' version —
  check the class for a house macro (e.g. a `\reason`-style rule-with-label) before assuming it exists.
- **A sub-threshold overfull (`< 25pt`) can be absorbed locally** without touching global settings:
  `{\emergencystretch=3em …the paragraph…\par}` — the explicit `\par` must be **inside** the group,
  else the group closes first and the extra stretch never applies (the implicit `\par` before the
  following display happens after the group).
- **`xdvipdfmx: fatal: Unable to open "main.pdf"` is a FILE LOCK, not a content error.** A PDF viewer
  (Foxit / Edge / …) that has the file open re-locks it after each rewrite, so pass N can fail while
  pass N−1 succeeded. Retry the pass (2–3×, ~3 s apart) instead of hunting for a LaTeX bug; the
  preceding pass already wrote a complete PDF.
