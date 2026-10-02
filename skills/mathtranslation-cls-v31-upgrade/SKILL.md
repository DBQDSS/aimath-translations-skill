---
name: mathtranslation-cls-v31-upgrade
description: "Use when migrating a Chinese math-book translation from the OLD mathtranslation template (v1.x, ctexart-based, single-file or thin wrapper) onto the NEW mathtranslation.cls v3.1 (ctexbook-based, kvoptions class options). Covers the three-layer heading remap (Section->Chapter->Subsection), continuous equation numbering on ctexbook, the shared-theorem-counter / \\@addtoreset hook traps, the \\printterminology unnumbered-chapter override, and the pymupdf-based regression audit that proves nothing was lost."
agent_created: true
---

# Migrate a translation to mathtranslation.cls v3.1

## Purpose

The old `mathtranslation` templates wrap **`ctexart`** with a hand-rolled compatibility layer
(`\ChapterSectionLabel`, `\sectionbreak{\clearpage}`, `mybibliography`, a `\titleformat{\section}[display]`
that paints "Chapter N" headings). `mathtranslation.cls` **v3.1** wraps **`ctexbook`** and exposes real
class options via `kvoptions`. The visible layout is intentionally similar, but the *underlying
counters and hooks are different*, so a naive `\documentclass` swap compiles yet silently mangles
numbering. This skill is the safe, auditable recipe.

## When to use

- A translation uses the old ctexart template and must move to
  `.../mathtranslations-translation-template/mathtranslation.cls` (v3.1).
- The old source uses `\section` for chapters (because old `\section` rendered like a chapter).
- Symptom that this skill is needed: after the swap, equations become `(n.m)`, theorem numbers
  restart inside chapters, or "术语索引" becomes "第 N 章".

## Step 0 — Identify the target and the old style

1. Confirm the reference class: `md5`(or normalized content) of the target `mathtranslation.cls`.
   **Compare with line endings normalized** (`b.replace(b'\r\n', b'\n')`) — a raw md5 mismatch is
   usually just CRLF vs LF (699 lines ⇒ 699-byte delta), NOT a content difference.
2. Grep the old project for the old-template fingerprints:
   `\ChapterSectionLabel`, `\sectionbreak`, `mybibliography`, `\chapter` absent, `ctexart`.

## Step 1 — Class line

Replace the old `\documentclass[UTF8,11pt,fontset=none]{ctexart}` (+ inlined defs) with:

```latex
\documentclass[BookTitleCN={...},BookTitleEN={...},OriginalAuthor={...},
  HeadingFont=hei,Biblatex=true,BibStyle=numeric-comp]{mathtranslation}
```

- `Biblatex=false` ⇒ the class falls back to **bibtex**; use it when the body has literal
  `\bibitem`s and no `.bib`. v3.1 has **no `mybibliography`** environment — use `thebibliography`
  (the class already patches the heading / TOC entry / bookmark / header for it).
- Keep per-project extras the class lacks, e.g. `\usepackage{esint}`.

## Step 2 — Heading remap (three layers)

Because the old `\section` *rendered* as a chapter, shift everything down one level. Include the
`toc` layer:

| old | new |
|---|---|
| `\section` / `\section*` | `\chapter` / `\chapter*` |
| `\subsection` | `\section` |
| `\subsubsection` | `\subsection` |
| `\addcontentsline{toc}{section}` | `\addcontentsline{toc}{chapter}` |

Do it as a single regex pass, then **prove it lossless**: apply the *inverse* map to the new files
and diff against the backup — it must restore byte-for-byte. Watch for `\subsubsection` inside
comment lines (harmless, but count it so your roundtrip check is exact).

## Step 3 — Equation numbering (ctexbook regression)

`ctexbook` numbers equations **per chapter** by default (`\theequation = \thechapter.\arabic{equation}`).
The old ctexart numbered them **continuously**. Restore continuity explicitly:

```latex
\makeatletter
\@removefromreset{equation}{chapter}
\renewcommand{\theequation}{\arabic{equation}}
\makeatother
```

Also swap any old `\numberwithin{X}{section}` → `{chapter}` (otherwise on ctexbook you get `n.m.k`).

## Step 4 — Theorem counters (the two traps)

### Trap A — a shared counter has no register
`\newtheorem{proposition}[theorem]{命题}` does **not** create `\c@proposition`; it only makes
`\theproposition` point at `\thetheorem`. `hyperref` / `cleveref` still evaluate `\the\c@proposition`,
and if that register is `\relax` you get **`You can't use \relax after \the`**.

When you tear down the class's theorem defs and rebuild them:

```latex
\def\MT@undefthm#1{%
  \expandafter\let\csname #1\endcsname\relax
  \expandafter\let\csname end#1\endcsname\relax
  \expandafter\let\csname c@#1\endcsname\relax}
% ... rebuild with \newtheorem{theorem}{定理}[chapter] then aliases [theorem] ...
% then re-point each alias register at the shared one:
\makeatletter
\let\c@definition\c@theorem  \let\c@lemma\c@theorem
\let\c@corollary\c@theorem   \let\c@proposition\c@theorem
% ... one line per alias ...
\makeatother
```

### Trap B — residual `\@addtoreset` survives the redefine
Redefining a theorem **does not** clear the class's `\@addtoreset{X}{section}` hook registered on
`\cl@section`. After the remap, `\section` means a *subsection*, so every theorem counter resets on
each subsection ⇒ visible number churn (1.1, 1.1, 1.1 …).

Fix per-counter:

```latex
\makeatletter
\@removefromreset{theorem}{section}
\@removefromreset{definition}{section}  % ... etc ...
\makeatother
```

**Do NOT clear the whole `\cl@section` list.** It also carries book-class native hooks
(`subsection`, `exercise`, …); wiping it stops subsubsections from resetting per section and
introduces a *new* bug. On TeX Live 2026 `\@removefromreset` performs a precise list surgery — use it.

## Step 5 — Unnumbered 术语索引 / 参考文献 chapters

`\printterminology` emits `\chapter{术语索引}`. If the document has **no `\appendix`**, that chapter
gets numbered and the index appears as "第 N 章". Override the chapter command locally:

```latex
\let\MTOrigChapter\chapter
\newcommand{\MTStarChapter}[1]{\MTOrigChapter*{#1}\phantomsection\addcontentsline{toc}{chapter}{#1}}
\let\MTOrigPrintTerminology\printterminology
\renewcommand{\printterminology}{%
  \begingroup\let\chapter\MTStarChapter\MTOrigPrintTerminology\endgroup}
```

(When `\appendix` *is* present, the class's default is correct and you should not override.)

## Step 6 — Body skeleton

```latex
\makecover            % NOT \maketitle — v3.1 redefines it to the book cover
\frontmatter
  % 获奖说明 / \chapter*{译者说明} / \tableofcontents
\mainmatter
  \chapter{...} ...   % content, \input files
\backmatter
  \chapter*{参考文献}\nocite{*}\printbibliography[...]
  \printterminology
```

## Step 7 — Verify (do not trust "rc=0")

1. Build with the project driver (`xelatex` ×3 + `biber`/`bibtex`; `texindy` for the index).
   Require **errors=0, undefined=0**; treat `overfull`/`underfull` as cosmetic only.
2. **Regression-audit the PDF against the pre-swap baseline** with `pymupdf` (text, since the
   renderer cannot see images):
   - Record and compare: heading sequence; equation-label multiset; theorem/lemma/prop numbering
     multiset; figure count; citation count; and the `\envenddiamond` glyph `\u22c4` count.
   - Normalize with `re.sub(r'\s+','', text)` and compare **title sequences item-by-item** —
     footnotes get extracted adjacent to body text and create "phantom differences" that vanish
     under whitespace normalization.
3. Intended visual changes (v3.1 makes `\headfont` a *real* hei font, chapter label layout differs)
   are expected and must not be "fixed".

## Environment notes (this Windows/WorkBuddy box)

- `dirname`/`head`/`ls`/`wc`/`tail` are **broken** in the Bash tool. Use Python for all file work:
  `C:/Users/asus/.workbuddy/binaries/python/versions/3.13.12/python.exe`.
- TeX binaries live in `D:\texlive\2026\bin\windows\`.
- Preserve each source file's original line endings (many are CRLF); do not let an editor flip them.
- Deleting many temp files (`_cltest*`) can trip `SAFE_DELETE_BULK_CONFIRM_REQUIRED`; just re-issue
  the build instead of chaining a big delete.
