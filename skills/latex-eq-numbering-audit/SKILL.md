---
name: latex-eq-numbering-audit
description: >
  Audit the equation numbering of a re-typeset LaTeX math book against the ORIGINAL
  printed book, then report AND fix the exact sections/missing numbers. Use when the source
  is a transcription of a scanned classic (Yosida, Rudin, Bourbaki…) and you must confirm
  that formula numbers match the original "one by one" — e.g. when labels disagree with
  rendered numbers, when a numbered display was flattened into inline text, when a
  chapter's opening section does not restart the counter, or when the original used
  roman-numeral equation tags (i)(ii)(iii) that came out as arabic.
agent_created: true
---

# LaTeX equation-numbering audit against the original book

## When to use

Someone asks to "compare with the original and confirm the formula-numbering issues",
or you notice `\eqref` output that contradicts hard-coded numbers in the prose.

## The method: 4 independent sources, then a vote

| # | Source | How | Reliability |
|---|---|---|---|
| A | **Our own build** | recount LaTeX's counter independently, then verify against the real `main.aux` label by label | exact (proves model == output) |
| B | **PaddleOCR-VL JSON** | structured OCR; `formula_number` blocks assigned to sections **by geometry** | high; occasionally misses a tag placed in the right margin of a prose line |
| C | **MinerU markdown** | second OCR, reads `\tag{N}` | low on old scans — drops most display math; corroboration only |
| D | **The original PDF's own text layer** | right-margin tag band + gap filter + run-based split (see Step 3) | high **when filtered**; the most faithful to the printed page |

Vote on each section's **maximum arabic tag**:

- `CONFLICT` — every source that has data agrees *and* disagrees with us → must fix.
- `layer-ok` — source D agrees with us, the rest is noise → **we are right**.
- `layer-diff` — D disagrees → inspect by hand (usually D's own artifact, see §Tool limits).
- `agree` — everyone agrees. A source value of **0 means "no data"** and is excluded from the vote.

## Step 1 — internal consistency check (free and exact)

Many transcriptions name labels after the **original book's own number**:

```latex
\label{eq:VII.4.5}      % chapter VII, section 4, original equation (5)
\label{eq:VIII.5.vii'}  % roman-tagged equation (vii')
\label{eq:XI.0.1}       % chapter XI, unnumbered intro section, equation (1)
```

Then every `\newlabel` in `main.aux` gives the **rendered** number while the label name
gives the **intended (original)** number. Run `scripts/audit_eq_numbering.py`:

```bash
python tools/audit_eq_numbering.py [--aux main.aux]
```

- **CHECK 1** rendered ≠ name; group by section — a *constant offset over a run*
  (`rendered = name − 1`) means exactly one numbered display is missing earlier.
- **CHECK 2** section whose integer sequence is not 1,2,3,… (gap).
- **CHECK 3** duplicated integer inside a section (often a legitimate `\tag{1'}`).

**The label names are a clue, never the metric.** They are frequently **sparse**, but when a
whole section is short by one, the names still list the original set: e.g. `XIII.7` labelled
`.1, .3, .4, …, .14` is proof that the original's **(2)** exists and we dropped it. Likewise a
gap `{3,4,5,8,13}` means those five numbers are missing.

> **Fingerprint**: a **hard-coded literal** like `($13$)`, `($1$)`, `($4$)` in the prose is
> nearly always a numbered display that was flattened into inline text. Grep for it.

### Also recompute the counter ourselves

```bash
python tools/simulate_eq_numbers.py --check-aux   # must print "0 mismatches"
```

This proves the counter model equals the real LaTeX output, so later "our number" claims
rest on something verified rather than assumed.

## Step 2 — ground truth from the original (pixels)

> **The text layer is unreliable for MATH** (`‖x‖ → II-xII`, `proof of → prool 01`, OCR
> garbage materialising as phantom tag `(0)`). Never read formulas from it.
> **But its right-margin TAG BAND is reliable** — that is what Step 3 exploits.

```bash
python tools/find_orig_page.py "Cayley transform"        # fuzzy search of the original OCR layer
python tools/find_page.py ours "Unitary Operators"       # same, for our PDF
python tools/render_orig_strip.py 218 222 out.png --layout row
python tools/render_orig_strip.py 234 239 out.png --layout col --band 335 400
python tools/verify_sections.py [CH.SEC ...]             # section-bounded side-by-side
python tools/dump_tags.py orig 218 222                   # raw tag list, one PDF
```

Read the rendered image yourself. Tags sit flush right at a fixed x — measure once with
`scripts/probe_eq_tags.py` (for a 439.4 pt page the band is `x ∈ [335, 400]`; for A4 + 25 mm
margins it is `x ∈ [505, 530]`). **For a scanned book the tag band is typically
`x0 ≥ 0.74 · page_width` and there is a large horizontal gap to the left of the tag.**

## Step 3 — source D: harvest the original's own tag band (usually decides the case)

`scripts/textlayer_eqseq.py` reads every word in the right-margin band and keeps only real
equation tags. Three tricks make it dependable:

1. **Bracket tolerance** — OCR often reads the closing `)` as `}` or `]`:
   `^\((\d{1,3}|[ivxlcdm]{1,6})(['\u2032\u2033\u2019\u201d"]{0,3})[)\]}][.,]?$`
2. **Gap signature (`GAP_MIN ≈ 8 pt`)** — a real tag is pushed to the margin and is
   separated from the text on its line by a wide gap. An inline cross-reference
   ("Thus, by (1)") is flush against the prose and is **rejected**. This removes the
   biggest class of false positives.
3. **Run-based section assignment** — tags are collected globally in reading order
   `(page, y)`; when a page begins a new section, the split point is the page's **first
   arabic `(1)`** — tags before it belong to the previous section, tags from it on to the
   new one. This kills **start-page contamination** (a section often begins mid-page, and
   the previous section's tail shares that page) without needing the heading's y.

```bash
python tools/textlayer_eqseq.py            # whole book: per-section max + writes _textlayer_eqseq.json
python tools/textlayer_eqseq.py VIII.5     # one section, page by page
```

Then vote:

```bash
python tools/triangulate_eqnums.py          # 4-source verdict
python tools/triangulate_eqnums.py --strong # only CONFLICT
```

**Source D out-performs source B on prose-line tags.** On Yosida it caught six sections
(`I.7, IV.2, V.4, X.3, XII.4, XIII.7`) where the tag numbers a *condition/definition body*
placed in the right margin — B had missed every one, and A agreed with B, so only D broke
the tie.

## Defect patterns this audit reliably catches

| Pattern | Symptom in `main.aux` | Original evidence to look for |
|---|---|---|
| Numbered display flattened to inline text | `eq:VII.4.5 → 4` (whole section −1) | original shows the formula centred with a tag |
| Inline text hard-codes a number | prose contains `($4$)` | the hard-coded number is the original's |
| Chapter opening does not reset the counter | `eq:XI.0.1 → 15` (offset +14) | original prints (1),(2),(3) at the chapter head |
| Original display left unnumbered, ours numbered | ours has numbers the original lacks | original page shows no tag (check the *continuation* page too!) |
| Original used **roman** tags `(i)…(viii)` | labels `eq:….i` render as arabic (14)…(22) | original paginated with `(i)`, `(ii)`, … |

> **Beware the mirrored error**: a chapter intro may *continue onto the next page*, where its
> first numbered displays live. Judging "the intro has no tags" from its first page alone
> produces a false defect (this actually happened with Yosida XIV.0 — the (1)(2) are on the
> following folio). Always confirm the display is unnumbered in **both** the print and the
> text layer before removing a number.

## Fix recipes

**Missing numbered display** — restore the display exactly as the original sets it:

```latex
\begin{equation}\label{eq:VII.4.4}
U_{H} = (H - iI)(H + iI)^{-1} \quad \text{with the domain} \quad D(U_{H}) = D((H + iI)^{-1})
\end{equation}
```

When the original's "display" is really a **prose condition** (a definition body), keep it in
a `minipage` so it can carry a number without being treated as math:

```latex
\begin{equation}\label{eq:XIII.7.2}
\begin{minipage}[b]{0.92\linewidth}
$\lim\limits_{t \downarrow 0} t^{-1} \!\int_{d(x,y) \geqq \varepsilon} \!P(s,x,s+t,\dd y) = 0$
for all positive constants $\varepsilon$ \\
$(d(x,y) =$ the geodesic distance between two points $x$ and $y)$
\end{minipage}
\end{equation}
```

**Roman tags that must not consume the arabic counter** — the original's `(18)` → list
`(i)…(viii)` → `(19)` proves the roman list is outside the arabic numbering. amsmath's `\tag`
*increments* the counter, so use a **starred** environment, which has none:

```latex
\begin{align*}
M _{g} ^{l} (\alpha h (g))& = \alpha M _{g} ^{l} (h (g)), \tag{i}\label{eq:VIII.5.i} \\
...                                                                       \tag{viii}\label{eq:VIII.5.viii}
\end{align*}
```

(`\tag*{x}` prints without parentheses; `\tag{x}` prints `(x)`.)

**Chapter-head counter reset** — `\setcounter{equation}{0}` is usually hooked on the
sectioning command only, so an unnumbered chapter intro inherits the previous chapter's
counter. Reset at the chapter start (prefer a minimal line in the chapter file over editing
the class, if the project has a "don't touch the .sty" rule).

**Original display that is unnumbered** — change `\begin{equation}` to `\[ \]` and replace
any `\eqref` to it with literal prose.

**Hard-coded literal reference** — after adding the label, turn the literal into a real
reference: `($1$)` → `\eqref{eq:X.3.1}`. (Check first that every occurrence of that literal in
the section denotes the same equation.)

## Tool limits — the 4 residual `layer-diff` cases were all benign

Expect these, and verify rather than "fix" them:

- **Section boundary across a page.** A section often starts mid-page; the split at the first
  `(1)` can misfire when that `(1)` is unreadable (`(I}`) or on the next page, so the new
  section's first tag is billed to the previous one. *Symptom: layer max = json max + 1 and
  the extra tag sits on a page whose top line is the next section's heading.*
- **Inherited boundary on the other side.** A section whose end page is the next section's
  start can lose its tail tags.
- **Gap filter too strict.** A genuine tag that sits close to the end of its display gets
  rejected. *Symptom: layer max below both json and ours.* Cross-check json, which is free of
  this filter.
- **Under-extraction.** A word the OCR mangled so badly it no longer matches the regex.

**In all four, source B (JSON, geometric) agreed with us** — which is exactly what the vote
is for. Record them, explain the artifact, do not chase them.

## Closing the loop

After any fix: recompile (twice), confirm 0 errors and no `Reference … undefined`, re-run
`simulate_eq_numbers.py --check-aux` (must be 0 mismatches), re-run the 4-source vote until
`CONFLICT` is empty, then re-run the project's pagination-dependent tooling (index rebaser,
overflow checker, regression suite). Equation-number changes *are* supposed to change
`\eqref` output — that is the point — but **pagination will shift**, so the index links must
be rebased afterwards.

Preserve the project's line endings: check with a byte-level test
(`d.count(b'\r\n')` vs `d.count(b'\n') - d.count(b'\r\n')`) — many editors silently convert
CRLF↔LF, and the project may require CRLF.

## Bundled scripts

- `scripts/audit_eq_numbering.py` — Step 1, the exact internal check
- `scripts/textlayer_eqseq.py` — **Step 3**: harvest the original's right-margin tag band
  (bracket tolerance + gap filter + run-based section split); emits `_textlayer_eqseq.json`
- `scripts/triangulate_eqnums.py` — the 4-source vote; consumes `_orig_struct.json`
  (source B), `_mineru_eqseq.json` (C), `_ours_eqseq.json` (A), `_textlayer_eqseq.json` (D)
- `scripts/probe_eq_tags.py` — measure the right-margin tag band of a PDF (geometry + gap signature)
- `scripts/render_orig_strip.py` — render the original's tag band / whole pages for eyeballing
