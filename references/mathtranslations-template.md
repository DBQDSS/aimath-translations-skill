# Optional MathTranslations Template Profile

Read this reference when the user supplies or requests a MathTranslations-style
LaTeX template. There are two related templates in circulation, and they are
**not** interchangeable:

- **Supplied book variant:** `mathtranslation.cls` — a
  `ctexbook`-based class with real `\chapter`/`\section`/`\subsection`
  hierarchy, a public build/cover/bibliography interface, and biblatex+biber
  bibliography. Use it only when supplied or selected for the project; it is
  not bundled with AI & Math Translations.
- **Legacy (reference only):** `mathtranslations-translation-template.tex` —
  the older single-file `ctexart` template (numbering by subsection,
  `exercises`/`answers`/`longproof`, local `mybibliography`). The skill still
  bundles this file and `logo.pdf` under `assets/`; it is the self-contained
  fallback when no newer class is supplied.

The class file is externally maintained, so inspect the *supplied* `mathtranslation.cls` instead of
relying on memory. The profile below was derived from `mathtranslation.cls` v3.x.

## Authority

Keep two priorities separate:

1. the source book or paper PDF is the highest authority for content, formulas,
   structure, and displayed numbering;
2. the supplied `mathtranslation.cls` is the highest authority for typesetting
   when the user has selected this template;
3. OCR, MinerU Markdown, or extracted TeX is a working draft only.

If source numbering conflicts with the template counters, adapt counters or
environment definitions so the displayed result matches the relevant source
edition. Do not hard-code visible numbers in prose.

## Engine And Base Layout

The current template expects:

- **XeLaTeX**, run through the actual project build driver (for example,
  `tools/build.sh full` when supplied). A lone `xelatex` invocation will not
  resolve the table of contents, cross-references, the biblatex bibliography,
  or the terminology index.
- `mathtranslation.cls`, which wraps **`ctexbook`** — so `\part`/`\chapter`/
  `\section`/`\subsection` are real, native levels. Do not fake a chapter with
  `\section` (the v1.2 convention); use `\chapter` directly.
- `tikz-cd` for commutative and arrow-and-node mathematical diagrams.
- **Fandol** CJK fonts: Fandol Song for prose/examples, Fandol Kai for a newly
  introduced term, Fandol Fang (via `\theoremfont`) for theorem-like bodies.
  CMU Serif or a Latin font for English.
- A4 paper with the class's default margins; 2-em paragraph indentation and the
  class's line spacing.

## Public Interface (v3.x)

The class exposes these commands; call them in `main.tex` rather than rebuilding
the machinery:

```tex
\makecover                 % title page (uses the BookTitle*/Translator metadata)
\frontmatter               % Roman numerals; for 译者说明 / 前言 (\chapter*)
\makecontents             % table of contents
\mainmatter               % Arabic numerals; the book body
\appendix                 % switches chapter counters to letters A, B, C, ...
\makebibliography         % emits \chapter{参考文献} + prints biblatex entries
\printterminology         % emits \chapter{术语索引}; call once, last
```

Minimal `main.tex` shape:

```tex
\documentclass[
  BookTitleCN={...}, BookTitleEN={...}, OriginalAuthor={...},
  OriginalEdition={...}, OriginalPublisher={...}, OriginalYear={...},
  Translator={...}, ModelUsed={...}, BibStyle=numeric
]{mathtranslation}

\addbibresource{references.bib}   % biblatex is loaded by the class; do NOT \usepackage{biblatex} here

\begin{document}
\makecover
\frontmatter
\chapter*{译者说明}\addcontentsline{toc}{chapter}{译者说明}
\chapter*{前言}\addcontentsline{toc}{chapter}{前言}
\makecontents
\mainmatter
\include{chapters/ch01}
% ... chapters ...
\appendix
\include{chapters/chA}
\makebibliography
\printterminology
\end{document}
```

## Cover Metadata

Set metadata through the `\documentclass` options (the class defines
`\BookTitleCN`, `\BookTitleEN`, `\OriginalAuthor`, `\OriginalEdition`,
`\OriginalPublisher`, `\OriginalYear`, `\Translator`, `\ModelUsed`,
`\TranslationDate`; you can also `\renewcommand` them). Cover logo is the
`LogoFile` option (default `logo.pdf`, searched in `graphics/` then the project
root). The cover prints the publisher line followed by a
`\Translator\ 翻译及重排` credit line. Keep provenance accurate.

## Terminology Contract

At the first formal introduction of a concept, use:

```tex
\newterm{stable-key}{中文术语}{English term}
```

The stable key must be unique and label-safe. The command typesets the Chinese
term in Kai, appends the English term in parentheses, and records the first page
for the terminology index. After first introduction, write the Chinese term
normally. Use `\termcn{...}` only for deliberate visual emphasis (no index row).
Use `\addterm{中文术语}{English term}{页码文字}` to force a fixed page entry.
Place exactly one `\printterminology` call at the very end of the document.

## Semantic Environments

The class provides (all default to numbering **by section**, `X.M`):

- `definition`, `lemma`, `theorem`, `corollary`, `proposition`, `remark` —
  Fang body;
- `example`, `problem` — Song body;
- `proof` — Song, ends with `\square`;
- `longproof` / `\longprooflink` — move a long proof to the end of its section
  with a clickable link;
- `exercises` / `answers` — subsection exercise/answer pairs with back-links.

Keep the source environment type. Use labels and real references
(`\autoref`, `\ref`, `\eqref`, `\cref`). The class provides Chinese `\autoref`
and `\cref` names.

### Remapping numbering to match a source book

Inspect the class defaults and the source book first. If the source numbers
theorems/problems/questions/figures **by chapter** (`X.Y`) and
definitions **by section** (`X.M.K`), achieve that in `main.tex` with counter
surgery — do not edit the class:

```tex
% 定理/引理/推论/命题/注/例/问题 按章编号 (X.Y)
\counterwithout{theorem}{section}   \counterwithin{theorem}{chapter}
\counterwithout{lemma}{section}     \counterwithin{lemma}{chapter}
\counterwithout{corollary}{section} \counterwithin{corollary}{chapter}
\counterwithout{proposition}{section}\counterwithin{proposition}{chapter}
\counterwithout{remark}{section}    \counterwithin{remark}{chapter}
\counterwithout{example}{section}   \counterwithin{example}{chapter}
\counterwithout{problem}{section}   \counterwithin{problem}{chapter}
% definition 保持按节编号 (X.M.K)：不动
% 图按章编号 (X.Y)
\counterwithout{figure}{section}    \counterwithin{figure}{chapter}
% 正文穿插的 Question 环境（按章）
\theoremstyle{mtsong}\newtheorem{question}{问题}[chapter]
\crefname{question}{问题}{问题}
\makeatletter\MT@defautorefname{question}{问题}\makeatother
```

Verify the *actual* rendered numbers by extracting text from the compiled PDF
(see "Common Pitfalls" below) rather than trusting `exit code 0`.

## Display Math, Lists, And Quotes

The template requires three uniform typesetting habits:

- display formulas use `align`, `aligned`, or `align*` environments only;
  multiple `\[ \]` blocks in a row must be merged into one environment;
- every ordered list uses `enumerate`; manual numbering is not accepted;
- Chinese double quotes use the TeX ligatures — two grave accents for the
  opening quote and two straight apostrophes for the closing quote — never
  Unicode curly quotes;
- Chinese prose sentences end with an ASCII `.` (not `。`), matching the
  template's punctuation policy.

These conventions apply to prose, not literal code or algorithm syntax. Preserve
English pseudocode keywords and input/output labels, and avoid Chinese
`\algrenewcommand`, `\renewcommand{\algorithmic...}`, or `\SetKw...` keyword
overrides. Use the source-compatible algorithm/listing setup without introducing
conflicting packages. See [ai-code-fidelity.md](ai-code-fidelity.md).

The audit script flags consecutive display-math blocks, Unicode curly quotes,
manual numbering, and stray `。` under the `mathtranslations` profile.

## Figures

Figure handling follows this priority, and the figures must be **clear**:

1. When the source PDF is a clean **vector** PDF, re-render the figure region
   at high resolution (400 DPI) from the original and autocrop — `pymupdf`
   (`fitz`) produces a raster fallback, not a lossless vector copy. If supplied, use the project's
   `tools/figcrop.py` to locate each `Fig. N.M` caption, crop its bounding box,
   and autotrim whitespace to `images/fig/fig-X-Y.png`.
2. Redraw simple figures with ordinary TikZ; rebuild every commutative diagram,
   morphism diagram, category diagram, pullback/pushout square, and similar
   arrow-and-node diagram in a `tikzcd` environment — never as a screenshot.
3. For incorrect crops (figures whose caption sits *below* the art, or unusual
   boundaries), feed a hand-verified `bbox` through an override table such as
   `tools/_figoverride.json` rather than editing the source.

After cropping, repoint every `\includegraphics` with
the project's `tools/rewire_figures.py` if available (back up `chapters/` first).
Those crop/rewiring tools are not bundled; ordinary PDF cropping is also valid.
Architecture graphs, flowcharts, and data plots are not commutative diagrams
and need not use `tikzcd`. Distinguish a real
figure caption `Fig. N.M` from an explanatory paragraph that merely begins with
"Figure N.M …".

## Common Pitfalls (learned the hard way)

- **Stale auxiliary files when switching templates.** After changing the class
  or `main.tex` substantially, delete `main.aux`, `main.toc`, `main.out`,
  `main.bbl`, `main.bcf`, `main.run.xml` and rebuild clean. An old `.toc` from
  a previous template version can contain conditional tokens (e.g.
  `\InAppendixToctrue`) the new class does not define, which crashes the first
  pass with `! Undefined control sequence`.
- **Do not load biblatex twice.** `mathtranslation.cls` already loads biblatex
  from the `BibStyle`/`BibFile` options. Adding `\usepackage{biblatex}` in
  `main.tex` causes option-clash or double-load errors. Only call
  `\addbibresource`.
- **Class version drift.** v1.2 faked `\chapter` with `\section` and numbered
  definitions by subsection; v3.x is genuine `ctexbook`. Inspect the supplied
  `.cls` (`grep` for `ctexbook`, `\newtheorem`, the public commands) before
  assuming the environment names, numberings, or public macros. The class
  defines `problem` but **not** `question`; define `question` in `main.tex`.
- **Verify numbering from the PDF, not the exit code.** A clean build can still
  ship numbers that disagree with the source. Extract text with
  `pymupdf` and verify the source edition's actual numbering before
  declaring done.
- **Front/back matter order.** The terminology index and bibliography must come
  after `\appendix`/`\mainmatter` in the right order; `\printterminology` is
  literally the last call.

## Adoption Procedure

1. Keep an untouched copy of the supplied `mathtranslation.cls` for comparison.
2. If no class is supplied, use the bundled legacy template or obtain the requested
   class from the user. Do not claim an unbundled class or driver is available.
   Keep project-specific changes in `main.tex` or its preamble where feasible.
3. Compile the unchanged project once to establish a baseline.
4. Replace all cover metadata and keep the `\Translator 翻译及重排` credit line.
5. Import the source structure; remap counters (above) to match the edition.
6. Crop figures with available tools and update their references (back up first).
7. Use `\newterm` once per indexed concept; keep long-proof and
   exercise-answer link pairs balanced.
8. Typeset display math with `align`-family environments, ordered lists with
   `enumerate`, Chinese quotes with the TeX ligatures.
9. Put `\printterminology` last; run the actual project build command; compare the
   generated PDF with both the source PDF and the expected numbering.
