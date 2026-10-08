---
name: math-pdf-bookmark
description: Add precise clickable bookmarks to AI or mathematics PDFs, individually or in a folder. Use text-span geometry for PDFs with usable text; use OCR only where needed for scans. Verify that each bookmark lands on its actual heading rather than an assumed page.
---

# Precise PDF Bookmarks

Use when the user requests PDF bookmarks or a navigable table of contents.
Preserve the PDF content and map every bookmark to a verified page and heading
position. Work on output copies before replacing originals within the requested scope.

## Inventory And Classify

- Identify existing usable bookmarks; keep them unless the user requests changes.
- Sample body pages throughout the book, not just the final page. A scan with
  metadata text on one page must not be mistaken for a text-layer book.
- Distinguish usable text, pure scans, and hybrid books whose TOC alone is scanned.
  OCR only the affected pages of a hybrid book when the body already has good text.
- Use the sibling `pdf-scanned-ocr-bookmark` instructions if OCR is required.
  Select concurrency based on measured memory and CPU capacity, not a fixed
  worker count inherited from another machine.

## Reconstruct The TOC

1. Locate actual TOC pages; distinguish them from a numbered bibliography or
   a list of other volumes. Check title/page correspondence in the body.
2. For text-layer TOCs, cluster spans by vertical position, then sort by x to
   reconstruct number/title/page rows. A line may be split across several spans.
3. Deduplicate repeated text spans. Require multiple leader characters when
   stripping dot leaders so the period in `1. Title` survives.
4. Parse chapter, section, appendix, and part hierarchy from numbering and
   indentation. Calibrate clustering tolerances for the actual layout.
5. Read detached page columns, full-width parentheses, and page ranges carefully.
   If a TOC lacks page numbers, locate headings sequentially in the body using
   a forward cursor, not the first occurrence of the title in the entire PDF.

## Resolve Every Heading

- Determine the printed-to-physical page mapping from multiple verified anchors.
  Roman front matter, inserted plates, and restarted page numbering may require
  separate segments rather than a single offset.
- Use a trustworthy page mapping to choose the page; search that page for the
  heading's vertical position. Search neighboring pages only when evidence supports it.
- If the mapping is unavailable, search within the interval bounded by verified
  neighboring entries. Compare title tokens while preserving word boundaries;
  deleting spaces before tokenization destroys English word overlap.
- Exclude TOC pages, running heads, folios, and mentions inside body prose from
  heading matches. Respect chapter-local section numbering.
- Record unresolved entries for review. Never invent a target using the last
  cursor page, clamp a wrong page into range, or force a nonmonotonic destination
  to match its neighbor.

## Write Destinations And Verify

Use the installed PDF library's supported destination format. For PyMuPDF,
simple TOC entries use 1-based page numbers; a fourth numeric value can specify
heading height in points. Do not pass an arbitrary unvalidated dictionary as a
destination. Read back `get_toc(simple=False)` to verify the resulting links.

OCR geometry is in pixels and must be converted with `72 / actual_render_dpi`.
Text-span geometry is already in page coordinates; do not apply an OCR scale to it.
Account for page rotation and the library's coordinate convention when necessary.

Check hierarchy, page bounds, live destinations, title/heading correspondence,
and intended reading order. Inspect bookmarks on headings below the page top.
Reject collapsed destination sets and report any intentional nonmonotonic order.
Confirm the output opens, retains page count/content, and is no longer being
written before copying it back. A process log alone does not prove saved bookmarks exist.

## Tool Availability And Delivery

Historical project helpers such as `tlbmk.py`, `build_t1.py`, `diag.py`,
`verify.py`, and `recover_empties.py` are not bundled with this skill. Use them
only if the current project supplies them; otherwise implement the required
focused processing with the available library. Do not assume private paths,
logs, worklist indices, or root variables belong to the current corpus.

Report input/output files, PDFs processed, bookmarks written and verified,
skipped existing bookmarks, unresolved entries, and books without a usable TOC.
Do not claim full coverage when some targets were omitted or require OCR review.
