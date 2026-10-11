# Optional MathTranslations Template

Read this reference only when selecting, inspecting, or adapting a MathTranslations
template. It describes two distinct variants; do not mix their commands or counters.
Source content and numbering still come from the chosen source edition.

## Select And Inspect The Actual Variant

- **Bundled legacy ctexart:** the single-file template and `logo.pdf` have their
  sole maintained copies in `../assets/`. Read [legacy-template.md](legacy-template.md)
  for this variant; copy the assets and root MIT `LICENSE` into the project and
  edit project copies. It uses legacy sectioning, `mybibliography`, and local
  semantic/link commands, not the book-class interface below.
- **Supplied book class:** `mathtranslation.cls` is a ctexbook variant supplied
  by the user or existing project. It is not bundled. Preserve and inspect that
  exact class, associated files, and build driver before adapting it. A profile
  derived from v3.x is guidance to check, not proof of another version's behavior.

Neither variant requires a website download. Provenance and snapshot scope are
in [resource-provenance.json](resource-provenance.json). Prefer supplied files
when the user selected that version. If a specifically requested class is absent,
identify the missing file; do not claim the legacy snapshot implements that class.
Do not fetch or refresh resources unless that maintenance scope was requested.

Inspect the base class, declared options, public commands, fonts, theorem/counter
definitions, bibliography loading, and terminology-index mechanism. Confirm any
claimed engine or build sequence from actual project files. Book-class v3.x
profiles often use XeLaTeX, Fandol Song/Kai/Fang, a Latin serif font, and
biblatex/biber; use those only where the supplied version establishes them.

## Authority And Numbering

The chosen source edition/version determines content, hierarchy, and displayed
numbers (its PDF when available and authoritative, its TeX for an explicitly
selected draft/revision otherwise). The selected
template determines presentation and available interfaces. OCR and extracted
Markdown are working drafts. A template default never authorizes renumbering the
source or changing terminology: apply [terminology-policy.md](terminology-policy.md).

For a ctexbook class, use real `\chapter`/`\section`/`\subsection` hierarchy;
do not reuse a legacy fake-chapter convention. Inspect which environments share
counters, which counters reset at chapters or sections, and how `\the...` is
defined. Remap only the relevant project counters to the source numbering model.
Do not blindly apply independent `\counterwithin` operations to shared theorem
counters or assume definition numbering is identical to theorem numbering.
Prefer project preamble adjustments to changing the supplied class when feasible.
Verify rendered numbers for theorems, definitions, equations, exercises, figures,
algorithms, listings, and appendices; a successful build does not establish them.

## Supplied Book-Class Interface

When inspection confirms the v3.x-style public interface, use its commands rather
than rebuilding its machinery:

| Command | Intended role to verify |
|---|---|
| `\makecover` | Cover populated from class metadata |
| `\frontmatter` | Front matter and Roman page numbers |
| `\makecontents` | Table of contents |
| `\mainmatter` | Main text and Arabic page numbers |
| `\appendix` | Lettered appendix chapters |
| `\makebibliography` | Bibliography heading and entries |
| `\printterminology` | Terminology index; once, as final document content |

Metadata commonly includes `BookTitleCN`, `BookTitleEN`, `OriginalAuthor`,
`OriginalEdition`, `OriginalPublisher`, `OriginalYear`, `Translator`, `ModelUsed`,
`TranslationDate`, and `LogoFile`. Set only options or commands supported by the
actual version. Replace sample values with evidenced project metadata; do not
invent edition, date, or author details. Preserve original author-name spellings.
Keep the translator's `翻译及重排` credit immediately below the publisher line
as the inspected cover sample requires.

If the class loads biblatex from `BibStyle`/`BibFile`, do not load biblatex again
in `main.tex`. Register the bibliography once using the supported interface
(for example, `\addbibresource` if the class has not already registered it).
The legacy `mybibliography` interface is not a substitute for biblatex.

Starred headings and manually added TOC entries require an actual hyperlink
anchor at the heading. Do not copy unverified `\chapter*`/`\addcontentsline`
pairs from samples; inspect the class's hyperref behavior and click the compiled
bookmarks to confirm their destinations. Preserve front/back matter order and
do not move appendices behind the final terminology index.

## Terminology And Semantic Environments

If supported by the inspected template, introduce an indexed concept once with
`\newterm{stable-key}{中文术语}{English term}`. Keys must be unique and label-safe;
later occurrences use ordinary prose. Person-name components stay in source
spelling in both displayed and index forms, for example
`\newterm{frechet-derivative}{Fréchet 导数}{Fréchet derivative}`.
Index machinery does not verify this translation's mathematical sense.

Use `\termcn` only for deliberate emphasis if the template defines it. A fixed
page entry through `\addterm` is appropriate only when its actual interface and
page target have been verified; do not hard-code a guessed page. Call
`\printterminology` exactly once after the bibliography and other content when
that is the inspected template contract.

Inspect available `definition`, `lemma`, `theorem`, `corollary`, `proposition`,
`remark`, `example`, `problem`, and `proof` environments rather than assuming
names, body fonts, or independent counters. Preserve source environment type.
Do not assume a `question` environment exists. Match `longproof`/`\longprooflink`
and exercise/answer pairs if the project uses them, including labels, answer
prefixes, ordering, and actual link targets; do not introduce relocated proofs
or new exercises merely because the template supports them.

## Presentation And Protected Content

The bundled legacy snapshot specifies these prose conventions. Apply them to
a supplied class only when that version confirms the same contract:

- Display formulas use `align`, `aligned`, or `align*`; put `aligned` within a
  math environment, avoid nested displays, and preserve source tags and grouping.
  Separate formulas do not become one equation merely to clear an audit warning.
- Ordered prose lists use `enumerate`; algorithm/listing line numbers retain
  their native environment.
- Chinese prose double quotes use TeX ligatures: two grave accents to open and
  two straight apostrophes to close.
- Chinese punctuation is retained inside prose, with ASCII `.` at sentence ends.

Code, pseudocode syntax, identifiers, prompts, literals, and legal notices follow
their fidelity rules rather than prose punctuation. Preserve English rendered
algorithm keywords and structural labels; translate the descriptive text after
them, natural-language steps and conditions, and safe explanatory comments.
Read [ai-code-fidelity.md](ai-code-fidelity.md) for these boundaries. A class-level
keyword override can violate fidelity even when the TeX command names stay intact.

Use Song for prose/examples, Kai for first-introduction terms, Fang for theorem
bodies, and a Latin serif font only where the actual template establishes these
roles. Check all Chinese, mathematical, and accented-name glyphs in the PDF.

## Figures And Build

For ordinary figures, prefer faithful PDF crops when usable. Use a raster crop
at suitable resolution (e.g. 400 DPI) as a fallback, then check small labels,
legends, and boundaries. Rasterization is not lossless vector extraction.
Redraw simple figures with ordinary TikZ when needed. Rebuild mathematical
commutative/morphism diagrams with `tikzcd` where expressible; use ordinary TikZ
for essential geometry it cannot express and document the reason. Architecture
graphs, flowcharts, and plots need their own geometry. Preserve measured data.

Project-specific `tools/figcrop.py`, `tools/rewire_figures.py`, or crop-override
tables are examples, not bundled dependencies. Inspect them before use and
verify caption detection and crop boxes against pages; a paragraph beginning
“Figure N.M” is not necessarily a caption. Review each changed asset reference.

Use the actual full build command, such as `tools/build.sh full` only when that
driver exists. In a confirmed biblatex/biber project, run the required engine,
bibliography, and later resolving passes. Other projects keep their own toolchain.
Clear stale auxiliary data when needed after template changes, but first identify
which files are generated. Do not remove supplied `.bbl` files or hand-maintained
bibliography/source data. Preserve source and unrelated user files.

Inspect logs, rendered numbering, references, glossary/index entries, bookmark
destinations, and changed pages. Use `audit_latex.py --profile mathtranslations`
only for a project that follows the corresponding conventions, and review scan
findings contextually. If files or tools are missing, report the limitation and
unperformed checks instead of claiming an unavailable build or visual comparison.
