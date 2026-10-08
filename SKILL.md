---
name: aimath-translations-skill
description: Translate AI, machine learning, and mathematics books, papers, notes, or existing LaTeX projects into rigorous Chinese LaTeX; review and repair translations while preserving mathematics, code, pseudocode, experiments, and references. Use for technical translation and source-fidelity review, including optional MathTranslations templates. Do not use for ordinary nontechnical translation or software modernization.
---

# AI & Math Translations

Produce a Chinese AI or mathematical translation that can be compiled, checked against
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
   template, its supplied class or bundled legacy TeX governs typesetting
   conventions.

## Prepare The Project

- Preserve an existing project's document class, packages, file layout, labels,
  citation keys, macros, and build system unless a change is necessary or the
  user explicitly chooses the MathTranslations template.
- For a new project, consult the current MathTranslations guide before choosing
  a MathTranslations template or mathematical terminology source. For AI terms,
  use the source's definitions and established Chinese usage in that field.
  MathTranslations resources are an optional upstream reference, not an AI glossary.
- When a `mathtranslations-translation-template.zip` or
  `mathtranslations-translation-template.tex` is supplied, inspect that exact
  version instead of relying on memory. Archives under the older name
  `MathTranslations-Template.zip` are earlier releases of the same template.
  Read [references/mathtranslations-template.md](references/mathtranslations-template.md)
  before adapting it.
- A supplied MathTranslations book template may use `mathtranslation.cls`
  (ctexbook-based). Inspect the supplied version and use its public
  interface (`\makecover`, `\frontmatter`, `\makecontents`, `\makebibliography`,
  `\printterminology`). Use `tools/build.sh full` only if the project supplies
  that driver; otherwise use its actual build system. If the inspected class
  loads biblatex from `BibStyle`/`BibFile`, only call `\addbibresource`, not
  `\usepackage{biblatex}`. The
  older single-file `mathtranslations-translation-template.tex` (ctexart) is
  bundled under `assets/` as a legacy reference only.
- If the user selects the MathTranslations template but supplies no template
  files, copy `assets/mathtranslations-translation-template.tex` and
  `assets/logo.pdf` into the project for the legacy variant. This skill does not
  bundle `mathtranslation.cls` or the optional project build/crop tools: obtain
  a user-supplied class if that variant is required. Keep the bundled
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
- Preserve code and pseudocode keywords, identifiers, literals, operators,
  indentation, control flow, and algorithm line numbers. Keep `for`, `do`,
  `end for`, `if`, `return`, `Input`, and `Output` in the source language;
  do not localize algorithm-package keyword definitions. Translate descriptive
  captions, explanatory prose, and safe natural-language comments only.
  Read [references/ai-code-fidelity.md](references/ai-code-fidelity.md) for any
  AI/ML source or any source containing code, pseudocode, or experiments.
- Recreate commutative diagrams, morphism diagrams, category diagrams,
  pullback or pushout squares, and other arrow-and-node mathematical diagrams
  with the `tikz-cd` package and `tikzcd` environment. Do not replace them with
  screenshots or raster images. Preserve every node, label, arrow direction,
  arrow style, and commutative relationship from the source.
- For ordinary figures, prefer a faithful PDF crop; a raster export at a suitable
  resolution (e.g. 400 DPI) is a fallback, not a lossless vector copy. Redraw
  simple figures with TikZ when needed. Neural-network architectures, computation
  graphs, flowcharts, and plots need their own geometry, not forced `tikzcd`.
  Verify crop boundaries, labels, legends, and any translated text.
- When the selected template requires it, typeset display formulas in `align`, `aligned`, or `align*`
  environments. Never place multiple `\[ \]` blocks side by side; merge them
  into a single environment.
- Use `enumerate` for ordered prose lists; preserve algorithm line numbering
  and code indentation using the project's algorithm or listing environment.
- With the MathTranslations template, write Chinese double quotes with TeX ligatures: two grave accents for the
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

1. Compile early and repeatedly with the project's actual build command.
   Rebuild generated auxiliary files when a template change or stale state
   requires it; do not delete source material or hand-maintained bibliography files.
2. Compare the generated PDF with the source PDF section by section. Also assert
   the rendered numbering against the source edition, including algorithms,
   listings, theorems, and figures; a clean build can still ship wrong numbers.
3. Perform three separate passes: Chinese language and terminology;
   mathematics and structural fidelity; compilation and visual layout.
4. Run `scripts/audit_latex.py <project-or-tex-file>` for deterministic checks.
   Add `--profile mathtranslations` for projects based on the
   selected MathTranslations template (legacy or supplied class), and use `--strict` when warnings should fail
   CI.
5. Read [references/review-checklist.md](references/review-checklist.md) before
   declaring a chapter or project complete.

For focused audits, read the relevant `skills/<name>/SKILL.md` only when needed
(see the README inventory). These inherited helpers may assume a particular book,
OCR schema, counter model, or toolchain. Verify those assumptions and required
files before running them. Their examples do not override the source or the
code/pseudocode preservation rules above; scanner hits require source review.

## Report The Result

Summarize:

- translated or reviewed scope;
- source files and authority used;
- build command and whether it succeeded;
- checks performed;
- unresolved ambiguities, suspected source errors, missing assets, or visual
  differences that still need human judgment.
