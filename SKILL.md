---
name: mathtranslations
description: Translate mathematical books, papers, notes, and existing LaTeX projects into rigorous Chinese LaTeX, or review and repair an existing mathematical translation, including projects using the MathTranslations template. Use when source fidelity, mathematical correctness, terminology consistency, cross-references, citations, compilation, and PDF-level proofreading all matter. Do not use for ordinary non-mathematical translation.
---

# MathTranslations

Produce a Chinese mathematical translation that can be compiled, checked against
the source, and maintained as a real LaTeX project.

## Establish The Source Of Truth

1. Inventory the supplied PDF, TeX sources, bibliography, figures, fonts,
   templates, and any existing translated files before editing.
2. Treat the published source PDF as the authority for visible mathematical
   content and structure. Use source TeX to recover markup and reduce
   transcription errors, but do not follow it when it conflicts with the
   published PDF.
3. If the source PDF is unavailable, state that limitation and use the best
   available source without pretending that page-level comparison was done.
4. Never silently repair a suspected error in the source. Preserve it by
   default and clearly record the issue; apply a correction only when the user
   requests it or reliable evidence resolves it.
5. Separate content authority from presentation authority. The source PDF
   governs mathematical content; when the user chooses the MathTranslations
   template, `mathtranslations-translation-template.tex` governs typesetting
   conventions.

## Prepare The Project

- Preserve an existing project's document class, packages, file layout, labels,
  citation keys, macros, and build system unless a change is necessary or the
  user explicitly chooses the MathTranslations template.
- For a new project, consult the current MathTranslations guide before choosing
  a template or terminology source. Prefer the latest stable resources linked
  from <https://mathtranslations.org/guide/> over bundled stale copies.
- When a `mathtranslations-translation-template.zip` or
  `mathtranslations-translation-template.tex` is supplied, inspect that exact
  version instead of relying on memory. Archives under the older name
  `MathTranslations-Template.zip` are earlier releases of the same template.
  Read [references/mathtranslations-template.md](references/mathtranslations-template.md)
  before adapting it.
- The current MathTranslations template for books is the `mathtranslation.cls`
  class (ctexbook-based). If the user supplies or prefers it, use its public
  interface (`\makecover`, `\frontmatter`, `\makecontents`, `\makebibliography`,
  `\printterminology`) and build via `tools/build.sh full` (xelatex ×2 → biber →
  xelatex ×2). biblatex is loaded by the class from `BibStyle`/`BibFile`
  options, so only call `\addbibresource` — never `\usepackage{biblatex}`. The
  older single-file `mathtranslations-translation-template.tex` (ctexart) is
  bundled under `assets/` as a legacy reference only.
- If the user selects the MathTranslations template but supplies no template
  files, copy `assets/mathtranslations-translation-template.tex` and
  `assets/logo.pdf` into the project for the legacy variant, or the maintained
  `mathtranslation.cls` + `logo.pdf` for the current variant. Keep the bundled
  masters unchanged; edit the project copies.
- If the user supplies a newer template, prefer that version after comparing
  its contract with the bundled baseline and recording any meaningful changes.
- Build a small project glossary before translating substantial text. Reuse
  established Chinese mathematical terms; keep named objects and symbols
  stable across chapters.
- Read [references/workflow.md](references/workflow.md) when starting a new
  translation, importing a long source, or deciding how to stage the work.

## Translate

- Translate mathematical meaning rather than sentence shape. Use natural,
  concise Chinese while preserving definitions, hypotheses, quantifiers,
  logical dependencies, notation, equation content, theorem status, and the
  force of words such as "if", "only if", "unique", and "respectively".
- Keep math in LaTeX. Reuse the source's macros and environments when they are
  sound. Do not convert formulas into prose, screenshots, or Unicode lookalikes.
- Preserve theorem-like environments, equation structure, bibliography links,
  footnotes, figures, tables, and section hierarchy.
- Recreate commutative diagrams, morphism diagrams, category diagrams,
  pullback or pushout squares, and other arrow-and-node mathematical diagrams
  with the `tikz-cd` package and `tikzcd` environment. Do not replace them with
  screenshots or raster images. Preserve every node, label, arrow direction,
  arrow style, and commutative relationship from the source.
- Handle ordinary figures by priority: when the source PDF is a clean vector
  PDF, re-render the figure region at 400 DPI with `pymupdf` and autocrop it as
  the preferred asset (perfect clarity, no raster blur); redraw simple figures
  with ordinary TikZ; keep `tikzcd` for arrow-and-node diagrams. For crooched
  crops feed a hand-verified `bbox` through an override table. Record any
  exception.
- Typeset display formulas uniformly in `align`, `aligned`, or `align*`
  environments. Never place multiple `\[ \]` blocks side by side; merge them
  into a single environment.
- Use the `enumerate` environment for every ordered list; never type the
  numbering manually.
- Write Chinese double quotes with TeX ligatures: two grave accents for the
  opening quote and two straight apostrophes for the closing quote. The
  apostrophe pair alone renders a closing quote, and Unicode curly quotes
  are not used in this template.
- On the MathTranslations cover, keep the publisher line and the
  `\Translator 翻译及重排` credit line directly below it, set slightly larger
  than the publisher line, as the template sample shows.
- With the MathTranslations template, introduce a concept once with
  `\newterm{stable-key}{中文术语}{English term}`, write the Chinese term normally
  afterward, and keep `\printterminology` as the final document content.
- Follow the selected template's punctuation policy. The inspected
  MathTranslations template uses Chinese punctuation except for an ASCII `.`
  at the end of Chinese prose sentences.
- Use `\label` plus the project's reference command for numbered objects. Do
  not hard-code theorem, equation, section, figure, table, or page numbers in
  translated prose.
- Do not invent missing proof steps, citations, definitions, labels, or
  references. Mark unresolved source ambiguity explicitly.
- Read [references/latex-quality.md](references/latex-quality.md) when editing
  TeX, resolving ambiguous notation, handling OCR, or repairing references.

## Verify

Verification is part of the translation, not an optional final polish.

1. Compile early and repeatedly with the project's actual build command
   (`bash tools/build.sh full` for the `mathtranslation.cls` workflow: xelatex
   ×2 → biber → xelatex ×2). Always start from a clean auxiliary state after any
   template or `main.tex` change — stale `.aux`/`.toc` from a previous template
   version can crash the first pass.
2. Compare the generated PDF with the source PDF section by section. Also assert
   the *rendered* numbering by extracting text from the PDF (期望 `定义 X.M.K`,
   `定理 X.Y`, `图 X.Y`); a clean build can still ship wrong numbers.
3. Perform three separate passes: Chinese language and terminology;
   mathematics and structural fidelity; compilation and visual layout.
4. Run `scripts/audit_latex.py <project-or-tex-file>` for deterministic checks.
   Add `--profile mathtranslations` for projects based on the
   `mathtranslation.cls` template, and use `--strict` when warnings should fail
   CI.
5. Read [references/review-checklist.md](references/review-checklist.md) before
   declaring a chapter or project complete.

## Report The Result

Summarize:

- translated or reviewed scope;
- source files and authority used;
- build command and whether it succeeded;
- checks performed;
- unresolved ambiguities, suspected source errors, missing assets, or visual
  differences that still need human judgment.
