---
name: mathtranslation-hardref
description: Convert confirmed hard-coded theorem, equation, section, and page references in Chinese LaTeX translations into clickable links using the project's actual printed numbering. Preview first, protect code and pseudocode, and leave ambiguous or external references for source review.
metadata:
  agent_created: true
---

# Clickable references in mathematical translations

Read the shared [terminology policy](../../references/terminology-policy.md) and
[code fidelity rules](../../references/ai-code-fidelity.md) when editing prose.
Preserve names as written in the source, including diacritics (Cauchy, Fréchet);
do not transliterate them or change an identifier to match a glossary candidate.

## Establish the target before replacing a number

Record the actual class, theorem/equation counters, reset boundaries, input order,
and reference macros. A number such as 2.3 can denote a theorem, exercise, section,
equation, data value, or an external work. Its shape is not enough to choose a label.

Use the printed number in field 1 of \newlabel from a fresh build. Hyperref's
anchor is a destination identifier, not the printed number. The label's spelling
can help locate the chapter but is not evidence that its suffix equals the number.
Skip @cref companion entries. Parse nested aux groups with balanced braces.

Resolve against the appropriate document/chapter/section scope and target kind.
When several targets share a number, inspect the source passage and leave the
reference unresolved until the target is established. Brackets, nearby exercise
references, and a unique match in another file do not prove the intended target.
Do not automatically link foreign chapter/page references to this translation.

## Bundled preview helpers

Run helpers from their scripts directory or use their full paths:

- convert_hardrefs.py uses the current directory or MT_ROOT, fresh aux labels,
  and a configurable source glob. It handles explicit Chinese theorem/equation
  prefixes; other spellings or counter models may need a focused adaptation.
- convert_bare_refs.py is a configurable recipe for an aux-derived chapter map.
  Set BASE, FILES, CHAP_OF, HAND, and EXACT for the actual project first.
  Its initial main.tex/i values are examples, not a detected chapter model.
- For Roman chapter references and per-chapter aux files, use the companion
  latex-translation-fidelity-audit helpers aux_number_map.py and xref_bare_scan.py.

Examples (paths are relative to this skill):

    python scripts/convert_hardrefs.py --files "chapters/*.tex"
    python scripts/convert_hardrefs.py --files "chapters/*.tex" --apply
    python scripts/convert_bare_refs.py
    python scripts/convert_bare_refs.py --go

The helpers default to preview. Apply only after reviewing every proposed target.
The explicit --scope-group file list permits a known continuous scope across files;
do not infer it from historical filenames or an appended paper. Writes reject
unresolved/ambiguous candidates and EXACT count mismatches, retain UTF-8 bytes and
line endings, and create .before-ref-conversion.bak copies before atomic replacement.

These bounded filters mask supported comments, literal code, pseudocode and math;
they do not parse all TeX, custom wrappers, macro arguments, or nested inline code.
Inspect custom structures and restrict the selected files accordingly.
Backups are recovery evidence; inspect the actual diff before further edits.

## Preserve what the reader sees

Prefer the project's existing reference commands when defined. Otherwise retain
the prose prefix with \ref or \eqref. Record the displayed number before and after.
If \ref already carries the chapter, adding a literal chapter duplicates it.
If the printed reference omits the chapter, a cross-chapter link may need a literal
chapter prefix. Establish this from aux and the rendered PDF rather than a class name.

A hand-typeset numbered item absent from aux may need \hypertarget plus \hyperlink,
or a suitable \label following a real reference-stepping command. Validate that
the target exists; \hypertarget entries do not appear as ordinary aux labels.
For original printed-page references, add an anchor at the corresponding passage
only after locating that passage; translated page numbers need not match the source.

## Rebuild and verify

Run the actual project build with enough passes for references to settle. Check
for undefined and duplicate labels, compare every changed displayed number, and
verify hyperlink destinations in the saved PDF. A zero undefined-reference count
does not prove that a link points to the right theorem.

When redefining theorem environments supplied by a class, inspect its registered
counter reset lists. Removing environment commands can be safe; killing a counter
still registered for a section reset breaks later headings. Use a separate shared
counter or the class's supported interface when a new numbering model is required.
Do not alter counter behavior merely to make a reference conversion convenient.
