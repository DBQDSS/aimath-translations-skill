# Translation Workflow

Use this workflow for a new mathematical translation or a substantial new
chapter. Adapt the granularity to the project instead of forcing every job into
the same number of files or passes.

## 1. Inventory Inputs

Locate and classify:

- the published source PDF;
- editable TeX and bibliography sources;
- figures, tables, diagrams, and external data;
- custom classes, packages, fonts, and macros;
- an existing Chinese translation or terminology list;
- the build command and expected engine.

Record gaps before translating. A source PDF without TeX may require careful
transcription or OCR. TeX without the published PDF cannot support reliable
visual comparison.

## 2. Choose Evidence Priority

Use this default order for content when evidence conflicts:

1. published source PDF for the visible mathematical work;
2. source TeX for exact markup, labels, citation keys, and macro intent;
3. errata or an authoritative later edition, when the user wants corrections;
4. OCR, HTML, notes, or secondary copies as supporting evidence only.

Do not merge editions silently. Record the edition, revision, or date used when
it is known.

Presentation has a separate authority. If the user selects the
MathTranslations template, its TeX governs layout, fonts, semantic environments,
links, and terminology-index mechanics. Source content still governs what the
translation says and how displayed objects are numbered.

## 3. Bootstrap Or Preserve The Project

For an existing project, first compile an unchanged baseline when feasible.
Preserve local conventions unless they prevent a correct result.

For a new project:

- review the current resources linked from
  <https://mathtranslations.org/guide/>;
- when using the MathTranslations template, read
  [mathtranslations-template.md](mathtranslations-template.md), preserve an
  untouched copy, and compile the unchanged template as a baseline;
- if the user did not supply template files, copy the skill's bundled
  `assets/mathtranslations-translation-template.tex` and `assets/logo.pdf`
  into the project for the legacy ctexart variant, or the maintained
  `mathtranslation.cls` + `logo.pdf` for the current ctexbook variant;
- otherwise choose a Unicode-capable Chinese TeX setup appropriate to the
  environment;
- keep source assets and generated build artifacts separate;
- establish a repeatable build command — for `mathtranslation.cls` projects use
  `bash tools/build.sh full` (xelatex ×2 → biber → xelatex ×2); start from a
  clean auxiliary state after any template or `main.tex` change;
- create a minimal sample containing Chinese prose, formulas, theorem
  environments, references, citations, and one figure before scaling up.

Do not vendor a remote terminology export without checking its license and
version. The bundled MathTranslations template and logo are MIT-licensed;
prefer a user-supplied newer template when available.

The recommended extraction path is source PDF to MinerU or another parser,
then Markdown as a working draft, followed by translation and LaTeX reassembly.
Extraction output never outranks the source PDF.

## 4. Establish Terminology

Create a project glossary with at least:

| Source term | Preferred Chinese | Context or exception | Evidence |
|---|---|---|---|
| compact | 紧 | topology; not everyday "compact" | current glossary/textbook |

Use the current MathTranslations terminology page as one reference, then check
the field's established Chinese literature and the local context. The project
glossary wins only for deliberate, documented choices.

For a new or disputed term:

1. identify its mathematical field and exact sense;
2. inspect nearby definitions and usage;
3. compare established Chinese sources;
4. choose one translation and record alternatives or exceptions;
5. search the project for inconsistent variants.

Keep symbols, transliterations, capitalization, and named constructions
consistent. Do not translate a term mechanically when its meaning changes by
context.

With the MathTranslations template, encode the first formal occurrence with
`\newterm{stable-key}{中文术语}{English term}` and write the Chinese term normally
afterward. Reserve `\termcn` for emphasis that should not create an index row.

## 5. Translate In Reviewable Units

Work by a coherent unit such as a section or subsection:

1. map headings, environments, labels, citations, figures, and footnotes;
2. translate the prose while preserving all mathematical dependencies;
3. compile the unit;
4. compare it against the corresponding source pages;
5. update the glossary and issue log;
6. commit or checkpoint a clean state before moving on.

Keep units small enough that a missing paragraph, swapped equation, or broken
reference can be localized quickly.

## 6. Handle Special Content

### Definitions, Theorems, And Proofs

Preserve environment type, numbering behavior, hypotheses, conclusions, and
proof boundaries. Do not upgrade an informal claim into a theorem or fill an
omitted argument.

### Equations

Retain displayed versus inline status when it carries meaning. Preserve
alignment, tags, cases, punctuation, and surrounding grammatical connections.
Compare every symbol, subscript, superscript, delimiter, and quantifier. With
the MathTranslations template, typeset display formulas in `align`, `aligned`,
or `align*` environments and never place multiple `\[ \]` blocks side by side.

### Figures And Tables

Follow the template's figure priority: when the source PDF is a clean vector
PDF, re-render the figure region at 400 DPI with `pymupdf` and autocrop it as
the preferred asset (perfect clarity, no raster blur); redraw simple figures
with ordinary TikZ; rebuild arrow-and-node diagrams with `tikz-cd` (never
screenshots of them). Use the project's `tools/figcrop.py` to locate each
`Fig. N.M` caption and crop its bounding box to `images/fig/fig-X-Y.png`, then
repoint `\includegraphics` with `tools/rewire_figures.py` (back up `chapters/`
first). Translate captions and table text without changing data. Preserve labels
and references. If an asset is missing, use an explicit placeholder and report it
rather than inventing a replacement.

Rebuild commutative diagrams, morphism diagrams, category diagrams, exact
diagrammatic sequences, and pullback or pushout squares with `tikz-cd`. Match
the source's node arrangement, arrow direction, arrow style, labels, and
commutativity.

Record every figure that cannot follow this priority, such as photographs or
free-form illustrations that TikZ cannot faithfully express.

### Bibliography

Preserve citation keys and bibliographic facts. Translate a title only when the
project has a consistent policy. Do not fabricate metadata that cannot be
verified.

### Front And Back Matter

Translate title pages, prefaces, appendices, indices, acknowledgements, and
license notices according to project scope. Keep legal and attribution text
faithful.

For the MathTranslations cover, replace all sample metadata: Chinese and
English titles, author, edition, publisher, year, translator, model, and update
date. Keep the `\Translator 翻译及重排` credit line directly below the
publisher line. Keep the terminology index after the bibliography and all
other content.

## 7. Track Uncertainty

Maintain a short issue log for:

- suspected source errors;
- terminology disputes;
- illegible or missing source content;
- edition differences;
- unresolved references or citations;
- layout differences that may alter interpretation.

Separate observed facts from proposed fixes. This makes editorial decisions
reviewable and prevents quiet drift from the source.

## 8. Deliver

A finished handoff should include the editable project, generated PDF when the
toolchain permits, build instructions already present in the project, the
project glossary, and a concise unresolved-issues list. Do not claim a complete
PDF comparison when only source text or compilation logs were checked.
