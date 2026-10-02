---
name: latex-bookmark-anchor-audit
description: >
  Audit and repair the PDF bookmark / TOC hyperlink anchors of a LaTeX document, so that
  clicking an entry actually lands on that heading. Use when readers report that bookmarks
  or the table of contents "jump to the wrong place", when star-numbered headings
  (`\subsection*{...}`, `\section*{...}`, `\chapter*{...}`) are paired with
  `\addcontentsline`, when TOC entries appear in the wrong order or are missing, or when a
  translation must be checked for "every section has an exercises booklet entry". Covers the
  root cause (starred headings create NO hyperref anchor), the critical
  `\phantomsection` ordering trap that silently offsets destinations by one page, how to
  detect a borrowed anchor in `.toc`, the PyMuPDF verification loop, and the
  idempotent normalisation script for mixed legacy spellings.
agent_created: true
---

# Audit & repair PDF bookmark / TOC anchors

## Symptom → root cause

**Symptom.** In the PDF, clicking a bookmark (or the same entry on the TOC page) jumps to an
unrelated location — a theorem, a proof, the previous subsection — even though the *page
number printed in the TOC looks correct*.

**Root cause.** A **starred** heading (`\subsection*{习题}`, `\section*{Bibliographie}`, …)
is typeset with the `\@sect`-star variant: it calls neither `\refstepcounter` nor hyperref's
anchor machinery, so **it defines no destination**. The `\addcontentsline` that follows
therefore inherits whatever `\@currentHref` was set last — normally the anchor of the
preceding theorem / proof / subsection. hyperref then writes that foreign anchor into the
`.toc` as the 4th field of `\contentsline`:

```
\contentsline {subsection}{\numberline {}习题}{253}{theorem.5.20}     % <-- borrowed anchor
```

The printed page (`253`) is right because `\addcontentsline` samples `\thepage` at that
moment; only the destination is wrong. This makes the defect easy to miss in a text-only
review.

## Fix

Give the heading its own destination with `\phantomsection`. Canonical three-line form:

```latex
\subsection*{习题}
\phantomsection
\addcontentsline{toc}{subsection}{习题}
```

### ★ The ordering trap (cost: 20 of 63 entries off by one page)

`\phantomsection` **must come AFTER the starred heading**, not before.

- `\phantomsection` → `\subsection*{...}` → `\addcontentsline` : **WRONG**
- `\subsection*{...}` → `\phantomsection` → `\addcontentsline` : **correct**

Why: `\phantomsection` records the current position immediately. If the subsequent
`\subsection*` happens to trigger a page break (the heading is pushed to the next page), the
anchor stays on the *old* page while `\addcontentsline` samples `\thepage` on the *new*
page. Net effect: TOC page number correct, bookmark destination one page early — a
maddening, intermittent, ~30 %-of-entries bug. Verified by rendering the target page and
finding the heading there while the bookmark pointed at the previous page.

## Detecting the bad state

`.toc` (or the `chapters/*.toc` written per chapter) is the ground truth. A healthy
starred-heading entry ends with an anchor of the form `section*.N` (hyperref's
`\Hy@MakeCurrentHrefAuto{section*}` counter). Anything else is borrowed:

```
grep 'contentsline {subsection}{习题}' main.toc
```

Bad anchors seen in the wild: `theorem.*`, `proof.*`, `subsection.*`, `subparagraph*.*`,
`paragraph*.*`. Good: `section*.N`.

## Normalising mixed legacy spellings (idempotent)

A real book migrates through several conventions. All of these must collapse to the
canonical form — collect every heading block and rewrite it as a unit:

| form | what it looks like | missing |
|---|---|---|
| A | `\subsection*{习题}` + `\addcontentsline` | anchor |
| B | `\subsection*{习题}` alone | anchor + TOC entry |
| C | `\begin{center}\textbf{习题}\end{center}` | anchor + TOC entry + consistent styling |
| D | a bare `\addcontentsline` with **no visible heading at all** | anchor + the heading itself |
| E | `\subsection*{习题}\addcontentsline{...}` on one line | anchor |

Write one script that: (1) locates blocks over all five forms; (2) **absorbs an immediately
preceding `\phantomsection` into the block** so re-running never doubles it; (3) emits the
canonical three lines; (4) splits form E into three lines. Then assert idempotency by
re-running in dry mode and expecting `0 rewritten`.

Also cross-check the *count*: for a book where every section ends with an exercises
booklet, `#(exercises blocks)` must equal `#(\section)` per chapter. A mismatch exposes a
whole booklet whose heading was never typeset (check the original book for an `Exercises`
line before assuming it is intentional).

## Verification loop (PyMuPDF)

```python
import pymupdf
doc = pymupdf.open('main.pdf')
toc = doc.get_toc(simple=False)      # [level, title, page, dest]
```

- Compare each booklet bookmark against its `.toc` entry: the bookmark page must equal
  `printed page + offset`, where the offset is that book's constant (`正文印刷页 = PDF 物理页 − 18`
  here). Report every mismatch with the expected value.
- `bookmarksnumbered=true` means bookmark titles carry the number (`7.7 Galois 理论应用简述`),
  so match with `in`, not `==`.
- Levels should mirror the sectioning: chapter → 1, `\section` → 2, `\subsection` and the
  exercises booklet → 3.
- The `dest['to']` point is in **PDF native coordinates (origin bottom-left)**; y ≈ 727 on
  A4 means ~114 pt from the top, i.e. the heading area — not the page bottom.

A clean run reads: *N entries in `.toc` / N bookmarks / 0 mismatches / 100 % `section*.N`*.

## Environment gotchas (Windows / WorkBuddy)

- **Never inline LaTeX regexes in a `bash -c "python -c ..."` one-liner.** Backslash
  collapsing silently turns `\\section\{` into a non-matching pattern and the script reports
  "0 sections" instead of failing. Write the script to a file and run the file.
- Preserve the source line ending when rewriting: read bytes, decide the separator from
  `raw.count(b'\r\n')`, join with it, then **assert `LF-only == 0` after writing**. A helper
  that appends to memory/log files must take the separator from the target file too (some
  files in the same repo are CRLF, others LF).
- Rewriting `.toc`-producing sources requires a full multi-pass rebuild (xelatex ×3 for the
  TOC/anchors to settle), then re-run the checker — a single pass will still show stale
  anchors.
- If `main.pdf` is open in a reader, the final `xdvipdfmx` step fails with a write lock;
  close the viewer first.
