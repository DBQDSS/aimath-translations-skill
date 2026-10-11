---
name: latex-bookmark-anchor-audit
description: Audit and repair LaTeX TOC links and PDF bookmarks that land at the wrong heading. Inspect class-dependent starred-heading anchors, page breaks, hierarchy and saved destinations, then verify repairs in the built PDF.
metadata:
  agent_created: true
---

# TOC and bookmark destinations

Inspect the project's class and hyperref behavior before rewriting headings.
A starred heading can lack a fresh anchor; some classes create one automatically.
An \addcontentsline may then inherit a preceding theorem/section destination even
while its printed page number is correct.

## Diagnose the actual destination

Compare the heading source, .toc destination field, saved PDF bookmark destination,
and the rendered target heading. The .toc is evidence of generated data, not a
guarantee that a fresh PDF embedded it. A theorem-like destination attached to an
exercise heading is suspicious; anchor spelling alone is not a universal classifier.

Do not infer that every section requires an exercise heading or a TOC entry.
Establish those units and the intended hierarchy from the source and requested output.

## Repair a confirmed missing anchor

A common safe sequence for a subsection heading that may trigger a page break is:

    \subsection*{习题}
    \phantomsection
    \addcontentsline{toc}{subsection}{习题}

Putting \phantomsection before a heading that moves to the next page can leave the
destination on the preceding page. Putting it after can land just below the heading.
Verify the actual vertical position; chapter headings, custom macros and automatic
class anchors may require a class-supported patch instead of this sequence.

Normalize only the confirmed affected blocks. Retain visible headings, level,
title and source order. Absorb a redundant old anchor when appropriate, then
check idempotency. Do not add exercise headings solely because their counts differ.

## Rebuild and verify

Run enough actual project passes to settle TOC and anchors. Reopen the saved PDF
and inspect destinations with doc.get_toc(simple=False), plus actual TOC links.
Resolve printed pages using a calibrated page map, including separate front-matter
or reset segments. Do not reuse another book's offset.

PyMuPDF coordinates normally use a top-left origin; account for page rotation and
verify targets visually. Compare title, hierarchy, physical page and position,
including headings near page boundaries. A valid destination can use any
class-generated name, so do not require 100% section*.N spelling.

Preserve the original encoding and each file's line endings, including LF sources.
Use file-backed scripts for complex shell quoting when useful. Record changed
headings, verified links and any remaining uncertainties.
