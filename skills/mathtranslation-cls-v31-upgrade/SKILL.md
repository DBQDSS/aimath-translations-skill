---
name: mathtranslation-cls-v31-upgrade
description: "Migrate a Chinese LaTeX translation from a legacy ctexart MathTranslations template to a supplied mathtranslation.cls v3.1 book class when requested. Preserve heading hierarchy, equation/theorem counters, bibliography, terminology index, and content through regression review."
metadata:
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

1. Inspect the target `mathtranslation.cls`, declared version, and actual interface.
   Record a hash for file identity, then compare content with the supplied reference
   when available. A raw hash mismatch can reflect line endings or substantive
   changes; do not infer its cause from the hash. Compare both raw and line-ending-
   normalized content (`b.replace(b'\r\n', b'\n')`) to establish which differences
   are present. A remembered line count or byte delta is not version evidence.
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

Apply the map only to confirmed structural commands in included document files.
Protect verbatim/listing/algorithm content, literal examples, comments, macro
definitions, and generated files; a single global regex can damage them even
when its inverse restores the bytes. Preview proposed edits and review each
changed heading/TOC entry against the old hierarchy. An inverse-map diff can
detect unintended textual loss, but it does not prove semantic correctness.

## Step 3 — Equation numbering (ctexbook regression)

`ctexbook` numbers equations **per chapter** by default (`\theequation = \thechapter.\arabic{equation}`).
The old ctexart numbered them **continuously**. Restore continuity explicitly:

```latex
\makeatletter
\@removefromreset{equation}{chapter}
\renewcommand{\theequation}{\arabic{equation}}
\makeatother
```

Inspect every old `\numberwithin{X}{section}` against the source counter model.
Change it to `{chapter}` only when that counter should follow the remapped
chapter level; definitions or other objects may intentionally remain section-based.

## Step 4 — Theorem counters (the two traps)

### Trap A — shared and independent counters need different treatment
`\newtheorem{proposition}[theorem]{命题}` uses the shared theorem counter rather
than allocating an independent proposition counter. Inspect the actual theorem
package, environment definitions, `\c@...`, `\the...`, hyperlink representations,
and reference wrappers before changing them. A wrapper assuming an independent
register can fail, but that is not a universal defect in shared-counter environments.

Preserve existing counter registers and sharing relationships. Do not undefine
`\c@<name>`, allocate a replacement register, or force aliases merely to redefine
an environment. Prefer changing display/reset behavior through the project's
supported interface. If environment replacement is genuinely required, limit
it to identified environment definitions, retain the original counter state,
and verify all wrappers and hyperlink targets. Compare rendered numbers with the
baseline and source before adopting any new sharing model.

### Trap B — residual `\@addtoreset` survives the redefine
An existing reset hook can survive an environment redefinition. Inspect the
actual reset lists and intended source numbering first: after heading remapping,
a reset on `section` may be correct for one counter and incorrect for another.
Repeated visible numbers can indicate an inappropriate reset, but require
checking the shared counter and source edition before changing it.

For a confirmed counter that should no longer reset by section, remove only that
relationship (example, not an instruction to change all environments):

```latex
\makeatletter
\@removefromreset{theorem}{section}
\makeatother
```

**Do NOT clear the whole `\cl@section` list.** It also carries book-class native hooks
(`subsection`, `exercise`, …); wiping it introduces unrelated numbering defects.
Use a targeted reset operation supported by the actual toolchain, then verify
the reset boundary and displayed/hyperlink representations across sections,
chapters, and appendices. Shared counters need one change to the underlying
counter, not blind changes to every environment name.

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
   Require **errors=0, undefined=0**. Review overfull/underfull findings on the
   affected pages: some are harmless spacing warnings, while others indicate
   clipped formulas, overlapping text, or lost readability and need repair.
2. **Regression-audit the PDF against the pre-swap baseline** with `pymupdf` (text plus rendered page inspection when available):
   - Record and compare: heading sequence; equation-label multiset; theorem/lemma/prop numbering
     multiset; figure count; citation count; and the `\envenddiamond` glyph `\u22c4` count.
   - Normalize with `re.sub(r'\s+','', text)` and compare **title sequences item-by-item** —
     footnotes get extracted adjacent to body text and create "phantom differences" that vanish
     under whitespace normalization.
3. Intended visual changes (v3.1 makes `\headfont` a *real* hei font, chapter label layout differs)
   are expected and must not be "fixed".

## Portability And Review

- Locate the available Python and TeX tools instead of copying a private machine path.
- Preserve the existing encoding and line endings.
- Use the supplied class's actual interface; this migration is optional and must
  not be triggered simply because a translation concerns AI or mathematics.
- Render changed pages when visual tools are available and report any missing
  visual pass. Do not treat historical text-only limitations as current facts.
- Scope cleanup to generated artifacts and temporary files from this migration.
