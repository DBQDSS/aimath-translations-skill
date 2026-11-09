# PDF figures, text layers, and rendering defects

## Choose an asset by verified behavior

Prefer the author's standalone figure when it matches the selected edition.
`trim,clip`, CropBox changes and `show_pdf_page(..., clip=...)` control visible
bounds; they do not establish deletion of source-page objects. Garbage collection
and compression do not remove objects that remain referenced. A visibly correct
crop can therefore retain off-crop text or resources; extraction behavior varies
between libraries and readers. Do not label a crop clean from one empty extraction.

For each imported PDF region, record source physical page (1-based), crop rectangle,
coordinate convention/rotation, output filename, and final printed width. Compare
its rendering with the same rectangle rendered directly from the source. Check
extracted text for source headers, captions and surrounding prose, and inspect
selection/copy behavior on the final compiled page when a reader is available.
For page-clipping imports with a reported leakage risk, inspect referenced content
streams/resources or choose a direct opaque source-page raster when reliable
object-level validation is unavailable. Empty text extraction alone is not an
acceptance gate for retaining such imports.
English labels inside a figure may be intentional; do not globally delete English.

If a clipped page leaks text or renders incorrectly, use a direct source-page
raster crop. With PyMuPDF, `page.get_pixmap(clip=rect, dpi=400,
colorspace=fitz.csRGB, alpha=False)` creates an opaque RGB rendering; save as PNG
and embed that PNG directly. Coordinates must be validated against the displayed
page, particularly for rotated pages. 400 DPI is an example, not a guarantee:
calculate effective DPI as pixel width / final width in inches, and inspect tiny
labels at final size and zoom. Render the source page, not a defective imported
crop. Reassembling individual embedded images can lose masks and vector labels.
Do not discard a soft mask from an extracted image without correct compositing.
Rasterization loses selectable labels and vector scalability; report that tradeoff.
A PDF wrapper around a raster may be useful but must not re-import the source page.

## Distinguish black patches from text-layer leakage

A black region is a symptom, not proof of a transparency bug. First locate it:
figure, formula, prose, or selection overlay. Compare source page, standalone asset,
and compiled page with selection cleared. If possible compare a second renderer
and the affected reader. A black block that appears only during selection may be
a viewer/text-selection issue; a defect present in normal raster rendering needs
content, font, mask, blending or embedding diagnosis. Do not claim a figure repair
fixes a formula-area selection artifact without reproduction. Preserve screenshots
and label hypotheses separately from confirmed findings.

## Acceptance and limits

- Render changed figures and final pages; verify crop edges, labels, color,
  backgrounds, thin lines and neighboring formulas against the source.
- Extract text from the final PDF and check for known out-of-crop source phrases.
  Empty extraction is a limited observation, not proof of absent PDF objects.
- Where possible select/copy across the affected paragraphs in the reported reader.
  Record reader/version and whether selection was active; otherwise state untested.
- Retain the original inputs and generate a separate repair build. Match checks to
  the output actually delivered, not an older PDF or standalone asset alone.
- Keep private source PDFs, screenshots and generated case outputs outside the
  distributed skill. Reusable tests should use synthetic documents.

## Request-size failures are a separate issue

HTTP 413 means a server or gateway rejected request size. A report of that status
without a captured request does not establish which image or history component
caused it. Count or estimate serialized bytes locally (base64 commonly adds about
one third); avoid logging credentials or full private payloads. Use bounded text
extraction and small review previews, preserving production assets locally. An
offline reduction in bytes is not a successful live API retry; state that limit.
