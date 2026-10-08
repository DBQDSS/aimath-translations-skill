---
name: pdf-scanned-ocr-bookmark
description: >-
  Add a searchable invisible text layer to pure-scan (image-only) PDFs via a
  command-line OCR pipeline (RapidOCR / PP-OCRv6, offline), then rebuild a
  faithful table-of-contents bookmark tree from the recognised text. Use when a
  PDF has no text layer (get_text() empty) and you need OCR + bookmarks, or when
  someone asks to batch-OCR scanned PDFs (e.g. "福昕/Adobe OCR 只能一本本做，
  能否批量 OCR 再加书签"). Do NOT rely on Foxit/Adobe built-in OCR — it is
  GUI-only and cannot be scripted.
metadata:
  agent_created: true
---

# Scanned PDF -> OCR text layer -> faithful bookmarks

The WinRT fallback is Windows-specific; the Python OCR path needs its own dependencies.
Historical performance figures and helper names below are examples from earlier
projects. `ocr_batch.py`, `winocr.ps1`, and the other project helpers are not
bundled: use them only if supplied, otherwise create the focused equivalent.
Discover installed engines, models, fonts, and tools before choosing a route.
Work on a copy and validate it before replacing an original within the requested scope.

## 0. Why not Foxit/Adobe built-in OCR
Foxit PDF Editor's OCR is a GUI plugin (`plugins\OCRRecognition.fpi` +
`plugins\OCR\FX_ABBYY_OCR.dll`, ABBYY engine) loaded inside `FoxitPDFEditor.exe`.
There is **no CLI / COM / external SDK**; `ActionWizard.fpi` batch is GUI-only and
cannot write custom bookmarks. Adobe Acrobat OCR is likewise not scriptable via CLI.
=> Use a command-line engine instead.

## 1. Environment (one-time)
```bash
python -m pip install -i https://pypi.org/simple --upgrade onnxruntime rapidocr pymupdf
```
- rapidocr 3.x bundles PP-OCRv6 models (`.../rapidocr/models/*.onnx`), fully offline.
- API: `from rapidocr import RapidOCR; eng=RapidOCR(); r=eng(img);
  r.txts (list[str]), r.boxes (Nx4x2)`. Empty result => `r.txts is None`.
- Thread control (important!): default uses ALL cores per process; running several
  workers oversubscribes and gives NO speedup. Set explicitly:
  `RapidOCR(params={"EngineConfig.onnxruntime.intra_op_num_threads":2,
                    "EngineConfig.onnxruntime.inter_op_num_threads":1,
                    "Global.log_level":"error"})`.

## 2. Batch OCR script (`ocr_batch.py`, parallel + resumable)
Phase 1 (multiprocess Pool): render page with `page.get_pixmap(dpi=300)` ->
`np.frombuffer(pix.samples,...).reshape(h,w,pix.n)[:,:,:3]` -> RapidOCR -> collect
`(boxes, txts)` per page; save to a `--cache` pickle (resume).
Phase 2 (single): for each page `page.insert_font(fontname="oc",
fontfile=r"C:\Windows\Fonts\msyh.ttc")` then per line
`page.insert_text((x0,y1), text, fontname="oc", fontsize=~h*0.82, render_mode=3)`
(invisible). `doc.save(out, garbage=3, deflate=True)`.
Also dump a sidecar `.txt` (`===== PAGE n =====` + text) for TOC parsing.
- Run: `python ocr_batch.py --pdf IN --out OUT.pdf --txt OUT.txt --cache C.pkl
  --workers 8 --threads 2 --dpi 300`, env `OMP_NUM_THREADS=1`.
- Throughput ~1.2-1.6 s/pg (8x2 on 16 cores). ~1450 pages ≈ 34 min.

### Pitfalls (learned the hard way)
- **Memory**: running other heavy python concurrently => `Unable to allocate ...`,
  pages become `__OCR_ERROR__`. Use <=4 workers if unsure; to fix, re-run with the
  same `--cache` (the todo filter re-OCRs only pages whose txt starts with
  `__OCR_ERROR__`).
- **Background jobs**: launch long jobs with the tool's run_in_background (a
  `nohup ... &` child may be killed when the tool call returns). Log to a file.
- Do NOT overwrite the original until the run reports 0 `__OCR_ERROR__`.

## 3. Rebuild bookmarks from the text layer
Once the PDF has a text layer, use the normal mathtranslation bookmark workflow:
1. Dump the sidecar / `page.get_text()` to find the 目录 / CONTENTS page(s).
2. Determine the **printed -> PDF page offset**: read the running header/footer
   number on a few body pages, compute `pdf - printed` (usually constant; if it
   drifts, build a monotonic printed->phys table from headers and interpolate).
   Front-matter (roman) pages do NOT follow the arabic offset.
3. Parse chapter/section headings. Two robust patterns seen in real books:
   - `第N讲/第N章 <title>` (Chinese) — chapter marker; sections `N.M`, `N.M.K`.
   - `Chapter N.` / `N.M.` (English). Chapters sometimes have the number on its
     own line; join "pure-number line + next line" into the heading.
   - OCR quirks: `1.` misread as `l.`/`I.`; `习题8・1` uses a middle dot; a
     3-digit garbled `221` = `2.2.1` (only accept when followed by a real title,
     else it's a page number).
   - Locate chapter headings in the BODY (cleaner than the OCR'd TOC) and use the
     body page; take section titles/pages from the TOC.
4. `doc.set_toc([...])`, enforce hierarchy (`level <= prev+1`) and monotonic
   pages, `saveIncr()`.
5. Verify: read back `get_toc()`, assert no out-of-range pages, monotonic, and
   spot-check that each mapped page contains the heading.

## 4. Verify & place
- `len(get_toc())`, max level, `oob=0`, monotonic, and non-empty text on a mid page.
- Only after 0 OCR errors, copy the OCR'd PDF over the original (images identical,
  only an invisible text layer + bookmarks are added).
- **Never copy back while a worker is still writing that book's output** — you get a
  truncated/corrupt PDF. Check `wocr_out/<NN>_*.pdf` mtime vs the worker log before
  copying. If a file ends up corrupt, the `wocr_out` copy is usually intact: force
  `cp` it back (the normal copy-back script opens the DESTINATION and will refuse).
- After any batch, run a corpus-wide `fitz.open()` sweep to catch corruption.

## 5. FALLBACK when RapidOCR is unavailable: Windows built-in OCR (WinRT)
**Symptom**: after a sandbox outage, ANY process loading `onnxruntime` is killed
instantly with `SIGTERM` — even `python -c "import onnxruntime"` fails (managed AND
system python). RapidOCR is then unusable. Do NOT keep retrying it.

**Fix**: use the OS OCR engine via PowerShell WinRT — no native libs, no sandbox issue,
and `zh-Hans-CN` is usually installed. Pipeline (all in `_build/`):

1. `render_pages.py <pdf> <a> <b> <outdir> [dpi]` — pymupdf renders each page to PNG
   (use 150–220 dpi; 220 for TOC pages, 150 for bulk).
2. `winocr.ps1 -PngDir <> -OutFile <>` — WinRT OCR. Key details:
   - `Add-Type -AssemblyName System.Runtime.WindowsRuntime`; need an `Await` helper
     built from `[System.WindowsRuntimeSystemExtensions].AsTask` generic method.
   - **Preload every WinRT type you touch**, including
     `$null = [Windows.Globalization.Language, Windows.Globalization, ContentType=WindowsRuntime]`
     before `New-Object Windows.Globalization.Language("zh-Hans-CN")`. If it is not
     preloaded you get an INTERMITTENT `TypeNotFound` →
     `NullReferenceException` on `TryCreateFromLanguage` (works most of the time,
     fails when PowerShell starts cold) and the run silently yields no xy file.
   - `New-Object Windows.Globalization.Language("zh-Hans-CN")` ->
     `[Windows.Media.Ocr.OcrEngine]::TryCreateFromLanguage($lang)`.
   - **Emit per-line geometry** `y \t x0 \t x1 \t h \t text` so two-column TOCs can be
     reconstructed. Materialise words with `$ws = @($ln.Words)` — without `@()` the
     bounding rects of successive lines are wrong (all identical).
3. `winocr_toc.py <xyfile>` — cluster lines into rows by **nearest-y (±24 px)**; label
   column `x0<265`, title column `265<=x0<820`, page column `x0>=1000`. This fixes the
   classic two-column TOC failure where OCR returns all titles then all page numbers.

Speed: Windows OCR is much faster than RapidOCR per page; the bottleneck is rendering.

**Detecting a broken (unrecoverable) text layer** — needed to decide "OCR the TOC pages":
- Latin-1-supplement heavy (chars U+0080–U+00FF, excluding ° ± · × ÷) OR
- page has ≥200 CJK chars but <10 % are common Chinese characters (`的一是了我不…`).
- CAUTION: mojibake produced by a *display* tool (e.g. reading a UTF-8 file with the
  wrong codec) is NOT a broken PDF. Always confirm with a direct `get_text()` in python.
- Custom font encodings (e.g. the Chinese EGA translations) are NOT reversible by any
  codec round-trip — they genuinely need OCR.

## 5b. CRITICAL: match the render DPI to the scan's native resolution
A fixed render DPI (e.g. 150) **silently down-samples small-page scans** and ruins OCR.
Symptom: garbage like `己椏 / 数季 / 语訁` where the source is fine.
Cause: `page.rect` can be small (e.g. 236×353 pt) while the embedded scan is 300 dpi —
rendering at 150 dpi yields only 492×735 px, half the native linear resolution.

Rule: `native_dpi = image_width / (page_width_pt / 72)`;
choose `render_dpi = 150 if page_width_pt/72*150 >= 1000 else clamp(native_dpi, 200, 300)`.
A/B on the same page: **150 dpi = many errors, 300 dpi = perfect**, 450 dpi ≈ 300 dpi.
So: 150 is fine for A4-ish pages; upscale to native (cap 300) for small-page books.

Parallelism: the whole pipeline is single-threaded per book, so run **N books
concurrently** (e.g. 4 python processes, disjoint index sets, each writing its own
per-book PNG/xy files). Rendering ~0.65 s/pg, WinRT OCR ~0.7 s/pg at 300 dpi.

## 6. PRECISE bookmark destinations (jump to the heading, not the page top)
The user requirement "标题不在页首时要点到标题的位置". PyMuPDF supports this:
`doc.set_toc([[lvl, title, page, top_margin_points], ...])` — the **4th element is a
plain float = the vertical offset from the page top, in points** (NOT a dict!).
Passing `{"to": Point(...)}` silently produces a dead destination (`page = -1`,
`kind = 0`). Verify with `doc.get_toc(simple=False)` — a working entry shows
`kind=1`, a real `page`, and a `to` Point.

Compute the offset from Windows-OCR line data: PNG rendered at `dpi` -> scale
`sc = 72/dpi`; the heading line's `y` (px) -> `y*sc` points. Put the destination a
little below the line top (or use the line's own y) so the heading is visible.

### Finding the heading line on the target page
`find_y(pages, phys, core, H)`:
- try page `phys` first, then `phys±1`, `phys+2`;
- match by normalised text: strip spaces/punctuation (`unicodedata.normalize('NFKC')`),
  compare the title core (after removing the leading `第N章` / `§N.M`);
- ignore anything outside `0.02H … 0.98H`;
- prefer the occurrence on the requested page, else the first neighbour.

### When the scanned book has NO usable 目录 page numbers
Fall back to detecting headings in the BODY (`heads2.py`):
- heading pattern `^(\d+)[.，,．](\d+)\s*(CJK…)$` (also allow a leading `§`);
- keep only lines whose font height `h >= median(h) * 1.0` (headings are usually larger);
- **exclude TOC-like pages** (>=5 lines that are just `N.M` numbers or heading-like);
- take the FIRST occurrence per (chapter, section) key;
- align each `第N章` to its first section's page;
- sort by (page, y) and enforce monotonic pages.

Scanned-book OCR quirks seen: `§` often lost or read as `S`/`8`/`&`；`1.1` split across
lines as `1.` + `1 …`; comma-for-dot (`2，1`); running heads repeat the current section so
the first occurrence is the section's start page but must be distinguished from the
heading itself (heading sits in the body region, running head at y < ~8 % of the page).

### Robust heading detection recipe (validated)
1. **Page number from the offset, not from search.** Once `offset` is known (mode of
   header `phys - printed`, ≥100 anchors), compute `phys = printed + offset`. Reserve
   title search for finding the **y only** — this removes most wrong-page errors.
2. For entries lacking a printed page, search by title **inside the window** bounded by
   the neighbouring entries that do have a page.
3. Heading match order: (a) exact/prefix title, (b) numbered prefix (`§N.M` / `第N章`),
   (c) any heading-like line. Require `< 0.06H` / `> 0.93H` lines to be IGNORED
   (running heads / folios) and require a numbered heading's line to START with its number.
4. **Chapter-local § numbering**: some books print `§1 §2 …` inside each chapter while the
   TOC says `§N.k`. Detect (body has `§N` + title but almost no `§N.k`) and then match the
   `k`-th § of chapter `N` — a `local_sec` mode.
5. **Exclude the TOC pages themselves** from the body search (they contain every title!).
6. Row-clustering for TOC parsing: use an **adaptive threshold** `0.55 × median(y-gap)`;
   a fixed threshold merges/splits rows when the leading between entries varies.
7. Many TOC page-number columns are unreliable at 300 dpi (dot leaders). Prefer deriving
   the page from the offset+anchor map and use the TOC only for (number, title, order).

## 7. TEXT-LAYER PDFs: a much cheaper path than OCR (prefer it when possible)
If `page.get_text()` already returns text, do NOT OCR. Use span geometry directly —
`page.get_text("dict")` gives **PDF points**, so there is no DPI and no pixel->point
conversion (sc = 1.0) and titles match exactly. Engine: `tlbmk.py` + `build_t1.py`.

### Row reconstruction (the crux)
A TOC row is almost always split into **separate spans/blocks**:
`"1.1" | "Basic properties" | "5"`. Line-level extraction fails — you get three
"lines" and cannot tell title from folio.
- Cluster **spans** (not lines) by y with a ±3 pt tolerance, then sort each row by x0.
- Leftmost token = number, middle = title, rightmost = page number.
- Drop spans outside `[0.055H, 0.935H]` first: that removes running heads and folios
  (a folio sitting in the right column otherwise gets parsed as every entry's page).

### Traps found in real books
- **Duplicated text layer**: some PDFs draw each line twice, so rows read
  `"§1.  §1.  Some Basic Terminology  Some Basic Terminology"`. Dedupe spans whose
  text is identical and whose x0 differs by < 4 pt.
- **Dot leaders**: the collapse regex must require **>= 2 leader characters**.
  `[.．·•…](?:\s*[.．·•…])+\s*` is correct; a pattern allowing a single dot silently
  eats the dot of `"1. Title"` and destroys the numbering.
- **False TOC pages**: a numbered series/bibliography page (`"1 Keith Hannabuss: ..."`,
  no page numbers) scores high on "starts with a number". Reject any candidate run that
  has neither a 目录/Contents banner nor >= 50 % of entries carrying a page number.
- **Page-number forms** to parse: detached right-column span; dot leaders + digits;
  Chinese full-width parens `（119）`; exercise ranges `"1.1 - 1.19 3/139"` (first of the
  `a/b` pair is the problem page).
- TOCs with **no page numbers** at all exist (e.g. Springer "Contents" listing only
  `1.1 Title`). Accept them, but then locate each heading by sequential title search
  with a **forward cursor** (start from the last resolved page), otherwise every entry
  resolves to the first occurrence of its title.

### Classifying scan vs text layer — do not trust mean text density
A pure scan that has a metadata blurb on its **last** page reports a nonzero mean
density and gets misclassified as "has text". Instead sample ~11 pages spread through
the book (excluding the last 2) and count how many have >= 100 chars; if fewer than
half do, it is a scan.

### precise.py dpi reminder
OCR xy coordinates are **pixels**; the pixel->point scale is `72/render_dpi`. Pass the
dpi the pages were actually rendered at (record it per book) — hardcoding 300 silently
halves every destination y for books rendered at 150.
