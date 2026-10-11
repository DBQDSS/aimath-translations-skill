---
name: latex-footnote-fidelity-audit
description: Audit footnotes in a re-typeset LaTeX translation against source pages and OCR dumps, including unusual markers, page-local numbering, missing bodies, and index entries inside notes. Treat word/count scans as candidates and verify restored notes in the PDF.
metadata:
  agent_created: true
---

# Footnote fidelity audit

Preserve source spelling of human names and follow the shared
[terminology policy](../../references/terminology-policy.md) when translating note bodies.
Use the original rendered page as the authority; OCR is an inventory aid.

## Inventory markers and note bodies separately

Record the source page, local marker, body and corresponding translated note.
Numbers can restart per page, chapter or section. Key an inventory by source page
and marker/occurrence rather than a bare number; do not keep only the first occurrence.
Inspect notes above a usual footer threshold as well as conventional footnote bands.

OCR can represent markers as $^3$, {~}^2, {}^{2}, \ldots^{7}, punctuation plus a
superscript, Unicode superscripts, or a mangled symbol. These forms are candidates,
not universal proof of a footnote: empty-base exponents and superscript ellipses can
have mathematical uses. Check the rendered page and the note body before moving them.

A complete comparison considers:
- The in-text marker and its actual note body.
- All prose, mathematics and references inside the body.
- Index entries or citations carried by the note.
- Whether the note is actually printed in the delivered PDF.

## Bundled candidate checks

    python scripts/footnote_survey.py <OCR-block-file> [FN_TOP]
    python scripts/check_footnote_text.py <project-root> [chapter numbers...]

The survey expects <<pPAGE|label|bbox=[x0,y0,x1,y1]>> blocks and reports suspicious
heads and repeated numbers. FN_TOP uses that OCR dump's coordinate scale;
calibrate it from source pages instead of transferring a historical threshold.

The text checker discovers src/chN.blocks.md files unless chapters are supplied
and expects chapters/ch0N.tex. It compares counts and English word overlaps with
TeX footnote bodies. A Chinese translation normally does not share the English
source's words. Empty normalized text, count differences and unmatched words require
review; neither overlap nor zero candidates proves a faithful translation.
Its marker/TeX-macro filters are bounded; inspect custom note commands separately.

For note-math candidates and complete note display, use the sibling
latex-ocr-math-defect-audit scripts fnaudit.py, fndump.py and fnshow.py.
No historical chapter range or source line is an expected target.

## Restore only confirmed omissions

Use a balanced extraction and exact reviewed patch. Preserve encoding, line endings,
code examples and source mathematics. Keep the project's numbering mechanism.
Do not insert an OCR number directly as a global footnote counter without establishing
the reset model. If a note contains an index entry, retain it in the correct body.

Run the actual build, then inspect each repaired note and its marker in the PDF for
presence, numbering, wrapping, clipping and hyperlink behavior. Check the refreshed
index when restoring entries carried inside notes. Report source-reviewed coverage
and any notes still requiring manual identification.
