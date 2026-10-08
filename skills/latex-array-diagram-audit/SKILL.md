---
name: latex-array-diagram-audit
description: Audit commutative diagrams in a LaTeX translation against the original PDF. Convert array-based diagrams to tikzcd where needed and verify existing tikzcd arrow directions, styles, labels, rows, and columns. Use for diagram fidelity review or repair, not for converting neural architectures or general flowcharts into commutative diagrams.
metadata:
  agent_created: true
---

# LaTeX Commutative Diagram Audit

Locate diagrams, compare the original and translated pages, make the smallest
confirmed correction, then compile and inspect the repaired diagrams.

## Scope

- Inspect `array`-based mathematical diagrams and existing `tikzcd` blocks.
- Distinguish diagrams from ordinary arrays, formulas, filtrations, and matrices.
- Use `tikzcd` for commutative/morphism diagrams. Neural-network architecture
  diagrams, computation graphs, flowcharts, and plots may need ordinary TikZ or
  faithful source assets instead.

## Locate The Evidence

1. Inventory all relevant environments with file names and source lines.
2. Use the translated `.aux` to locate the translated statement or figure.
   Its page field is a translated printed page, not the original book's page.
   Determine each PDF's physical/printed page mapping independently; do not
   transfer a translation offset to the original.
3. Find the original statement by its heading, number, or nearby prose. Formula
   text extraction can be incomplete; failure to find a formula is not proof
   that it is absent. A statement and a diagram inside its proof may lie on
   different pages.
4. Render corresponding regions and compare them. If direct image inspection is
   unavailable, use text and geometric evidence and report the missing visual pass.

For a vector PDF, `page.get_drawings()` can help locate nonhorizontal strokes
and distinguish arrowheads from plain inclusion lines. It is supporting evidence:
text glyphs or raster graphics may not appear as drawing segments.

## Compare Every Diagram

- Check node order and relative placement, including entire missing rows/columns.
- Check leading and trailing zeros, quotient nodes, and exact-sequence endpoints.
- Check each edge's endpoints, direction, label, and label side.
- Distinguish ordinary, hooked, two-headed, equal, double, dashed, and curved edges.
- Preserve crossings and commutativity as the original states or depicts them.
- A field tower or ideal chain may use lines without arrowheads. Preserve that
  choice; do not assume an upward arrow is equivalent to an unheaded inclusion line.

## Rebuild Only Confirmed Defects

For an `array` assembled with `\Big\downarrow` and `\xrightarrow`, rebuild the
same node layout with `tikzcd`, retaining every label. Examples of edge options:
`\ar[r,"\phi"]`, `\ar[d,"\tau \mapsto \tau|_L"]`, `hook`, `two heads`,
`equal`, `no head`, and `no head, double`. Empty rows change the distance to the
target node; use explicit directions such as `ddl` when required.

An exact-sequence grid with zero padding can use:

```latex
\begin{tikzcd}[column sep=1.1em, row sep=1.1em]
 & 0 \ar[d] & 0 \ar[d] & 0 \ar[d] & \\
0 \ar[r] & B\cap C \ar[r, hook] \ar[d, hook] & B \ar[r, two heads] \ar[d, hook] & BC/C \ar[d, hook] \ar[r] & 0 \\
0 \ar[r] & A\cap C \ar[r, hook] \ar[d, two heads] & A \ar[r, two heads] \ar[d, two heads] & AC/C \ar[d, two heads] \ar[r] & 0 \\
0 \ar[r] & A\cap C/B\cap C \ar[r, two heads] \ar[d, two heads] & A/B \ar[r, two heads] \ar[d, two heads] & AC/BC \ar[r, two heads] \ar[d, two heads] & 0 \\
 & 0 & 0 & 0 &
\end{tikzcd}
```

The top zeros have downward arrows; the bottom zeros have no outgoing vertical
arrows. This is an example, not a universal grid: select every edge from the
actual source.

## Edit And Verify

- Edit the same file sequentially. For batch replacements, confirm every old
  block occurs exactly once before applying changes.
- Preserve the source encoding and line endings. Avoid unrelated prose or macro
  changes; keep project-specific adjustments in the existing preamble when possible.
- Use the actual full build, including bibliography and index steps when needed.
  If texindy has a locale failure, use a working locale and verify the generated
  index file, rather than trusting a stale survivor.
- Require resolved references and inspect repaired pages for alignment, clipping,
  arrowheads, labels, and narrow-column overflow. Source correctness alone does
  not prove the diagram renders correctly.
- Report changed diagrams, source pages, checks, and unresolved uncertainties.
  Remove only temporary artifacts created by this audit after review.
