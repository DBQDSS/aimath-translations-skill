---
name: latex-translation-fidelity-audit
description: Audit Chinese LaTeX translations of AI and mathematics texts against original PDFs for missing units, broken references, mathematical fidelity, terminology, and untranslated prose. Preserve executable code and pseudocode syntax; confirm scanner candidates against source pages before repair.
metadata:
  agent_created: true
---

# Translation fidelity audit

Read the [terminology policy](../../references/terminology-policy.md) and
[AI/code fidelity rules](../../references/ai-code-fidelity.md). Keep human names in
source spelling, including accents (Cauchy, Fréchet); terminology-table entries are
review candidates, not global replacement instructions.

Select checks appropriate to the request. For a whole-work review, inventory the
source TOC and actual body through the final page, including appendices, proofs,
footnotes, tables, algorithms and front/back matter. Map each source unit to its
translated file and review status. Heading counts or imported original PDF pages
do not establish that an appendix's prose was translated.

## Align the evidence

Locate corresponding passages by heading, statement, number and nearby prose.
Calibrate physical/printed page mappings separately for each PDF and each numbering
segment. Translation pagination can drift within a chapter. OCR and text extraction
help locate evidence; source-page glyphs decide disputed formulas and diagrams.
If visual inspection is unavailable, report that limitation and the remaining scope.

Preserve notation, hypotheses, quantifiers, indices, signs, constants, equation
numbers and code behavior. Do not infer a “correct” formula from mathematical
plausibility, an OCR vote, or a familiar textbook example. Record source errata
separately when the project convention permits it.

## Helpers and their limits

Use the actual scripts/ paths and discover required dependencies. These helpers
generate candidates, not completeness certificates:

- section_parity.py counts numbered sections under chapters/ch*.tex and
  candidate exercise headings. Configure --chapters-dir and --tex-glob.
  --expect uses numeric filename chapter keys, for example "1=6,2=5".
  Compare counts with the source; inspect unnumbered/custom/imported units separately.
- residual_english_scan.py reports English structural words and algorithm prose.
  It masks supported code, comments and reference-title spans. Names, quotations,
  citations, identifiers, syntax and literal examples can legitimately stay English.
  Short prose or custom environments can escape the filter.
- operator_macro_scan.py inventories \operatorname uses. There are no universally
  wrong Fr/N names. Supply a source- and project-verified mapping with
  --expect "Fr=\Frob" to generate a focused candidate list.
- fraktur_audit.py compares single-letter \mathfrak counts across matching scope.
  Counts can differ due to macros, OCR, scope or translation errors. Inspect both
  source glyph and passage; rare discrepancies deserve the same review as common ones.
- math_cluster_audit.py reports differences in extracted math signatures.
  It retains font commands, braces and macros; equality is still not a proof of
  mathematical equivalence, and differences are not automatic defects.
  The bounded delimiter extractor does not understand every TeX environment.
- extract_pdf_text.py uses inclusive 1-based physical pages; show_context.py prints
  candidate surroundings. Neither replaces rendered-source inspection.

Do not translate code keywords, identifiers, strings, prompts or expected outputs.
Translate captions, natural-language descriptions and safe comments when requested
without changing execution or pseudocode syntax. Review descriptions inside algorithm
environments rather than exempting their entire contents.

## Reference and navigation checks

Fresh aux field 1 contains the printed number; field 4 is the hyperref destination.
Parse nested fields with balanced braces and skip @cref companion entries.
Determine theorem/exercise kind from the actual counter or environment; the number
shape alone cannot distinguish them.

    python scripts/aux_number_map.py <project_dir>
    python scripts/xref_bare_scan.py <project_dir> report

These helpers model numeric chapter filenames and a Roman chapter.sec.item reference
scheme. Configure actual counter names and source globs; adapt for other models.
Duplicate printed-number keys are emitted as null. Missing/unknown counters or
unrecognized filenames mean incomplete mapping, not absent source content.

Review every proposed link against the original before using apply. Explicit
prefixes can identify target kind; brackets and nearby exercise links cannot settle
a collision. Ambiguous/unresolved candidates reject writes. Supported code,
pseudocode, comments and math remain protected; custom wrappers still need review.
Changed files receive backups and retain original newline sequences.

Check visible exercise headings and saved bookmark destinations under the actual
class. A missing \phantomsection alone is not proof of a broken link; the class may
create anchors. Use the bookmark audit when actual navigation is wrong.

## Build and rendered verification

Use the project's real build and inspect the final log and PDF. Verify changed
references, numbering, bibliography, glyphs, figures and index entries. Check the
.ind file read by TeX against the file written by the index processor; multi-index
projects can have different names. A stale index can compile without warning.

Treat Missing character warnings as possible lost glyphs and inspect their locations.
Font-shape substitution can lose intended emphasis: use the project/source's intended
style and a font that supports it rather than universally replacing bold with \emph.
Inspect overfull boxes for clipping; harmless warnings need not force unrelated changes.

Report confirmed defects and repairs with source locations, candidate-only findings,
checked scope, build results and remaining limitations. A clean log or zero scanner
hits does not establish full translation, appendix coverage, or semantic correctness.
