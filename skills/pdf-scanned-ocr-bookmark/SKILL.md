---
name: pdf-scanned-ocr-bookmark
description: Add a searchable text layer and faithful heading bookmarks to image-only PDFs using available OCR tools. Use for individual or batch scanned AI/mathematics books; preserve originals and verify page geometry, OCR failures and saved destinations.
metadata:
  agent_created: true
---

# OCR and bookmarks for scanned PDFs

Discover installed OCR engines, models, PDF tools and fonts before selecting a
route. Use a copy of each input and validate saved output. This skill does not bundle
a complete OCR pipeline; helpers named in historical projects are not dependencies.

Read the shared [terminology policy](../../references/terminology-policy.md) when
editing generated titles. Preserve source titles and human names, including accents;
do not translate or transliterate a source name as an OCR cleanup operation.

## Classify and render the input

Sample body pages across the book. One page of metadata text does not establish a
usable text layer; some PDFs have text only in front matter. Check extraction
directly, because a viewer's encoding error can resemble PDF corruption.
Prefer usable span geometry over OCR, and OCR only the pages or regions that need it.

Choose render resolution from the source image's native dimensions, small glyphs
and a sample comparison. Record the actual DPI per page or book. OCR geometry is in
pixels; convert to points with 72 / actual_render_dpi. Preserve image rotation,
crop boxes and the page transformation. A fixed 150/300 DPI is not universal.

## OCR pipeline and recovery

Use an available command-line or connected engine that supports the requested
batching. For RapidOCR/ONNX or another engine, inspect the installed API and model
availability. Install dependencies only within the task's authorized environment;
do not assume model packages run offline or request global upgrades unnecessarily.

Keep page-specific OCR results and failures with input identity, page number,
render DPI, engine/model configuration and any coordinate transform. Cache using
JSON or another safe serialization format where practical. Do not load untrusted
pickle caches. Invalidate stale cache entries when inputs or configuration change.

Start with conservative worker/thread counts and measure time and memory on samples.
Use the environment's supported background-job mechanism for long runs. Failed or
empty pages need distinct states: a genuinely blank page is not an OCR failure.
Retry only the failed pages after diagnosing the cause. If an engine repeatedly
fails, switch to an available fallback or report the limitation.

On Windows, WinRT OCR can be an alternative when its language pack is installed.
Load each required WinRT type explicitly, await asynchronous calls, and emit per-line
or per-word geometry. Check failed calls and missing output instead of treating them
as blank text. Other platforms need their own supported engine.

## Build a faithful searchable layer

Insert invisible text using a font that covers the recognized script and appropriate
line geometry. A Windows font path is only an environment-specific example; discover
or supply an available font. Text insertion must not remove or alter original page
images. Reopen the result and compare page count, size, rotation and sample renders.

Searchability is approximate: baseline insertion does not necessarily preserve
word boxes, reading order or text fidelity. Record pages needing review. Do not claim
“zero OCR errors” merely because every process returned successfully.

## Locate bookmark headings

Parse the actual TOC and body headings. Reconstruct TOC rows from word/span geometry
rather than trusting extraction order. Cluster by locally calibrated vertical gaps
and column positions. Dedupe identical overlapping spans and distinguish dot leaders
from the dot in a heading number. Preserve source order and existing bookmarks unless
the requested repair requires replacing them.

Determine printed-to-physical page mapping from verified folios/body anchors, with
separate segments for front matter, resets or inserts. Locate each heading within
its expected window, excluding TOC pages and running headers. A matching title can
repeat; the first search hit or neighbouring page is a candidate, not a confirmed target.
For TOCs lacking pages, search sequentially within chapter boundaries and review ambiguity.

Classify hierarchy from source structure. Reject or flag unresolved/out-of-range
destinations; do not clamp pages, sort away a wrong mapping, or invent a heading.
See [math-pdf-bookmark](../math-pdf-bookmark/SKILL.md) for text-geometry checks.

## Save and verify

Use the installed PDF library's documented bookmark-destination API. PyMuPDF can
accept a vertical offset or a fully specified destination dictionary depending on
the supported form; an incomplete dictionary can create a dead link. Inspect
get_toc(simple=False) after reopening output: require actual internal page
destinations and check their coordinates visually.

Keep source and output paths distinct while processing. Preserve originals until
validation is complete. Replace an original only if the user requested replacement,
after all writers have finished and the output has reopened successfully. Do not
force-copy a “usually intact” recovery file; validate it and retain the damaged copy
when it may hold the only recoverable data. Limit batch validation to the requested
corpus, and report OCR coverage, candidate headings, verified destinations and failures.
