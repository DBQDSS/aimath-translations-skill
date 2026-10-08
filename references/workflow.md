# Translation Workflow

Use this workflow for a new AI/ML or mathematical translation or a substantial new
chapter. Adapt the granularity to the project instead of forcing every job into
the same number of files or passes.

## 1. Inventory Inputs

Locate and classify:

- the published source PDF;
- editable TeX and bibliography sources;
- figures, tables, diagrams, and external data;
- code listings, pseudocode, literal prompts, model input/output examples,
  experiment results, and any supplied software/version information;
- custom classes, packages, fonts, and macros;
- an existing Chinese translation or terminology list;
- the build command and expected engine.

Record gaps before translating. A source PDF without TeX may require careful
transcription or OCR. TeX without the published PDF cannot support reliable
visual comparison.

Unless the user explicitly requests selected pages/chapters or a summary, the
scope is the whole supplied work. Inventory front matter, all body sections,
appendices (including lettered sections), supplementary proofs, acknowledgements,
notes, bibliography, and indices. Inspect the body and final source pages even if
the TOC or PDF bookmarks omit them. Use one row per coherent unit in a project log:

| Source unit and heading | Source PDF pages (1-based) | Translation file/heading | Status | Comparison evidence or unresolved issue |
|---|---|---|---|---|
| Appendix A / source title | actual page range | actual destination | pending / translated / source-reviewed | source and rendered-page checks |

Rows are a coverage map, not proof of completion. Do not mark a unit translated
because its heading exists or the original pages were inserted. Distinguish physical
PDF page numbers from printed page labels; translated page numbers may differ.

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

- read the bundled [local guide](../MathTranslations/guide.md); website links in
  resource metadata record provenance and are not workflow prerequisites;
- when using the MathTranslations template, read
  [local template instructions](../MathTranslations/legacy-template.md), or the
  [book-class profile](../MathTranslations/template-profile.md) for a supplied class; preserve an
  untouched copy, and compile the unchanged template as a baseline;
- if the user did not supply template files, copy the skill's bundled
  `MathTranslations/templates/legacy/mathtranslations-translation-template.tex`,
  `MathTranslations/templates/legacy/logo.pdf`, and the accompanying MIT `LICENSE`
  into the project for the bundled legacy ctexart variant; the ctexbook variant
  needs a supplied `mathtranslation.cls`, which is not bundled;
- otherwise choose a Unicode-capable Chinese TeX setup appropriate to the
  environment;
- keep source assets and generated build artifacts separate;
- establish a repeatable build command using the project's existing driver;
  `tools/build.sh full` is an example for projects that provide it, not a
  bundled dependency. Clear generated auxiliary state when it is stale;
- create a minimal sample containing Chinese prose, formulas, theorem
  environments, references, citations, and one figure before scaling up.

The bundled resources are fixed local snapshots; do not fetch or refresh them
during ordinary translation. Prefer a user-supplied template when available.
If the user requests a resource refresh, check provenance, license, version, and
compatibility before vendoring an export or replacing the authorized assets.

The recommended extraction path is source PDF to MinerU or another parser,
then Markdown as a working draft, followed by translation and LaTeX reassembly.
Extraction output never outranks the source PDF.

## 4. Establish Terminology

Create a project glossary with at least:

| Source term | Preferred Chinese | Context or exception | Evidence |
|---|---|---|---|
| compact | 紧 | topology; not everyday "compact" | local reference/source definition |

Use [local terminology notes](../MathTranslations/terminology.md) and the
[starter TSV](../MathTranslations/terminology.tsv), together with the source
definitions and locally supplied references. The project glossary wins only for
deliberate, documented choices. Missing or disputed entries do not require website
access: retain the English term on introduction and record the uncertainty. Use
online research only when explicitly requested.

For a new or disputed term:

1. identify its mathematical field and exact sense;
2. inspect nearby definitions and usage;
3. compare available local Chinese references and the supplied project glossary;
4. choose one translation and record alternatives or exceptions;
5. search the project for inconsistent variants.

Keep symbols, transliterations, capitalization, and named constructions
consistent. Do not translate a term mechanically when its meaning changes by
context.

For AI/ML books, include model, dataset, metric, and library names in the glossary
as preserved identifiers. Resolve terms from their source definitions; do not
use a mathematical glossary as the sole authority for AI terminology.

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
an available raster fallback (not lossless vector output); redraw simple figures
with ordinary TikZ; rebuild arrow-and-node diagrams with `tikz-cd` (never
screenshots of them). If supplied, use the project's `tools/figcrop.py` to locate each
`Fig. N.M` caption and crop its bounding box to `images/fig/fig-X-Y.png`, then
repoint `\includegraphics` with its `tools/rewire_figures.py` (back up `chapters/`
first). Translate captions and table text without changing data. Preserve labels
and references. If an asset is missing, use an explicit placeholder and report it
rather than inventing a replacement.

Rebuild commutative diagrams, morphism diagrams, category diagrams, exact
diagrammatic sequences, and pullback or pushout squares with `tikz-cd`. Match
the source's node arrangement, arrow direction, arrow style, labels, and
commutativity.

Record every figure that cannot follow this priority, such as photographs or
free-form illustrations that TikZ cannot faithfully express.

### Code, Algorithms, And AI Experiments

Read [ai-code-fidelity.md](ai-code-fidelity.md). Protect code and pseudocode tokens
before translating captions, prose, or safe comments. Inspect algorithm-package
keyword overrides: rendered `for`, `do`, `end for`, `Input`, and `Output` must
retain the source language. Keep indentation, loop bounds, updates, algorithm line
numbers, literal prompts, and expected outputs intact. Prose `enumerate` and
MathTranslations punctuation rules do not apply to literal code or algorithm syntax.
Translate descriptions after those labels, prose steps (e.g. “Sample”), verbal
conditions, and explanatory comments inside the algorithm. These are human-language
content, not protected syntax. Review both token fidelity and prose completeness.

Preserve experimental values, metric direction, units, tensor shapes, model/dataset
identifiers, and uncertainty qualifiers. Architecture diagrams and computational
graphs may require ordinary TikZ or faithful assets instead of `tikzcd`. Never
invent results or update examples to a different software version.

### Bibliography

Preserve citation keys and bibliographic facts. Translate a title only when the
project has a consistent policy. Do not fabricate metadata that cannot be
verified.

### Front And Back Matter

Translate title pages, prefaces, appendices, indices, acknowledgements, and
license explanations within the agreed scope. Appendices and supplementary proofs
receive the same paragraph-by-paragraph translation and mathematical review as the
main text; never skip them because they are technical, long, or placed after the
bibliography. Preserve required legal notices and attribution verbatim when needed,
with a clearly separated Chinese explanation. Bibliographic titles, names, and
identifiers may follow the bibliography policy; this exception does not extend to
appendix prose, headings, proofs, or footnotes.

Do not substitute `\includepdf`, screenshots, source-English TeX, or an untranslated
OCR dump for translated appendix content. A source facsimile may be an explicitly
requested extra, separately labeled and excluded from completed translation coverage.

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

Reconcile every coverage-map row with actual translated content and the rendered
PDF, through the last source unit. Check appendix headings/bookmarks and their
proofs, tables, algorithms, footnotes, and references. A whole-document delivery
requires all in-scope units translated and source-reviewed. If resources prevent
completion, checkpoint the project, retain pending rows and exact source ranges,
and continue in further batches; report a partial translation until those rows are
finished. Context/time pressure and compilation success do not authorize replacing
remaining sections with English pages or redefining the requested scope.
