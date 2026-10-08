---
name: latex-display-layout-audit
description: Compare display-math layout in a LaTeX AI or mathematics translation with the original PDF and repair confirmed wrapping, alignment, nesting, or OCR spacing defects while preserving equation numbers and labels.
metadata:
  agent_created: true
---

# Display-Math Layout Audit

Use when a displayed formula looks excessively wrapped, misaligned, nested
incorrectly, or affected by OCR spacing. Obtain the original page before editing.

## Locate And Measure

1. Find the source block using a distinctive formula fragment or nearby prose.
2. Locate the original page from its heading, number, or text layer; calibrate
   printed-to-physical page mapping for that PDF. Do not reuse another book's offset.
3. Render the original and translated formula regions. Text-layer bounding boxes
   help locate a formula, but the rendered glyphs determine its appearance.
4. Compare logical line count, relation alignment, horizontal centering, and glyph
   style. `\Re` and italic `Re`, for example, are not interchangeable.
   If images cannot be inspected, report the limitation and use measurements
   without claiming a visual comparison.

## Scan For Candidates

From this skill's directory:

```bash
python scripts/scan_layout_oddities.py path/to/chapters
```

The scanner reports nested math environments and numbered environments whose
rows all carry `\notag` or `\nonumber`. Treat these as candidates: an `aligned`
or `split` inside a suitable outer display can be valid. All-notag derivations
are often intentional. A leading `&` alone is not evidence of a defect.

## Preserve Numbering During Repairs

Before editing, record the label-to-printed-number map from `.aux`, including
custom `\tag`, starred environments, and per-row `\notag` behavior.

| Source block | Repair constraint |
|---|---|
| Fully unnumbered | Rewrap or regroup without introducing a number. |
| Numbered or labeled | Keep every label, tag, numbered row, and counter effect. |
| Mixed numbered/unnumbered rows | Inspect each row and preserve its number behavior. |

Do not replace an environment blindly merely because a scanner finds nesting.
Fix only the confirmed spacing or break points. Under a MathTranslations template,
use its `align` family conventions; for other projects preserve their native
display conventions. Never wrap a top-level `align`/`align*` inside `\[ ... \]`.

For an unnumbered formula that needs a second line within an `align*` block:

```latex
\begin{align*}
\lambda_1 &= -\alpha - \frac{\varepsilon}{\sqrt{2}}, \\
\lambda_1 &\leq \lambda_2 \leq \cdots \leq \lambda_n.
\end{align*}
```

Choose breaks and alignment from the source's mathematical grouping and the
available text width. Do not force the source's line count if it clips the translation.

## OCR Hyphen Spacing

Verify the spelling against the original before changing `Hilbert - Schmidt`
or similar prose inside `\text{...}`. The helper supports a dry run:

```bash
python scripts/fix_hyphen_spacing.py path/to/chapters
python scripts/fix_hyphen_spacing.py path/to/chapters --apply
```

It backs up changed files and currently requires pure CRLF input. Do not normalize
LF files merely to satisfy it; use a targeted edit preserving their existing style.
Do not apply a prose spacing rewrite to code or pseudocode operators.

## Build And Compare

- Run the project's full build and inspect final logs for errors, unresolved
  references, missing glyphs, clipping, and remaining rerun requests.
- Compare the complete label-to-number map before/after; label count alone is
  insufficient. Recheck index/page references if pagination changed.
- Render repaired formula pages and compare them with the original crops.
  Source line counts do not measure rendered layout quality.
- Preserve encoding and line endings. Read complete source lines: truncated
  output can hide a `\notag` and create a false diagnosis.
- Report confirmed repairs, remaining candidates, and any tool limitations.
  Shell or toolchain failures must be diagnosed in the current environment.
