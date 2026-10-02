---
name: latex-ocr-math-defect-audit
description: >
  Find and repair mathematics that an OCR layer silently mangled BEFORE it reached a
  re-typeset LaTeX book, and prove none survived. Use when a scanned classic is being
  re-typeset from an OCR block dump and a reader reports "the formulas look strange",
  especially formulas inside FOOTNOTES; when an integral has been stolen into an
  exponent, a set-of-integration subscript has been lost, a brace is misplaced in
  set-builder notation, a differential sits outside math, or a whole word is typeset in
  math; or when you must decide whether the OCR dump or the printed page is the
  authority (spoiler: the page image).
agent_created: true
---

# OCR-inherited math defect audit for a re-typeset LaTeX book

## When to use

A scanned math book is being re-typeset from per-block OCR output
(`<<pN|label|bbox=[...]>>` style). The numbering / formula / footnote / coverage
audits all read **0**, the book compiles clean, and yet a reader says the formulas
— usually **the ones inside footnotes** — "look strange". They are right: the OCR
layer mangled the math, and the transcription copied it faithfully.

This is a different axis from footnote *presence* (see the sibling skill
`latex-footnote-fidelity-audit`). Here every note is present; the math inside it is
wrong.

## The one thing to internalise

**The OCR block dump is not a reference. Neither is `pdftotext`. The page IMAGE is.**

The block dump your converter consumed already contains the corruption, so a
transcriber who "faithfully copies the OCR" ships the corruption. Measured cases in
one book (Stein–Weiss PMS-32), where the printed page is in fact correct:

| in the OCR dump (already wrong) | on the printed page |
|---|---|
| `$\int_0 < \varepsilon \leq \|t\|$ $[f(x - t)/t]$ dt` | `\int_{0<\varepsilon\leq\|t\|}[f(x-t)/t]\,dt` |
| `(1/\pi)^{\int_{-\infty}^{\infty}} f(x - t)[t/(t^2 + y^2)]$ dt` | `(1/\pi)\int_{-\infty}^{\infty} f(x - t)[t/(t^2 + y^2)]\,dt` |
| `\{(x,y)\in\bar{E}_{n+1}^+\}; \|x-x_0\|^2+y^2=a^2\}` | `\{(x,y)\in\bar{E}_{n+1}^+ ; \|x-x_0\|^2+y^2=a^2\}` |
| `\{z = (z_1,\ldots,z_n) \in \mathbf{C}_n\}; \|z_1-z_1^0\| < r_1, \ldots\}` | `\{z \in C_n ; \|z_1-z_1^0\| < r_1, \ldots \}` |

So: **never "verify" a suspect formula against the OCR text or the PDF text layer —
they are the same broken source.** Render the page
(`pdftoppm -f N -l N -r 150 -png book.pdf out`, and `-r 300 -x .. -y .. -W .. -H ..`
to zoom a footnote band) and read the glyphs.

## The four defect classes

All four are cheap to detect with a scanner and each has a distinctive shape:

| tag | meaning | detection pattern | fix |
|---|---|---|---|
| `SUPINT` | a big operator stolen into an exponent | `\^\s*\{?\s*\\(int\|sum\|oint\|iint\|prod)` | delete the `^{...}` wrapper, keep `\int...` in the main line |
| `LIMIT` | the set of integration lost from the subscript | `\\(int\|sum\|oint)[_^]?\s*[0-9]?\s*(<\|>\|\leq\|\geq)` — e.g. `\int_0 <` | brace the whole set: `\int_{0<\varepsilon\leq\|t\|}` |
| `SEMIBR` | `\}` misplaced in set-builder notation | `\}\s*;` inside a math group | move `\}` to the end of the element description: `\{x \in X ; P\}` |
| `ROMAND` | a roman differential left OUTSIDE math | a `$` (or `\]`) that **closes** math followed by `\s*d[tsxyzruvwnm]\b` | move it inside and set it `\,dt` |

Plus one non-math-pattern class worth a separate one-liner search:

* **whole word in math** — `\$[A-Za-z]{2,}\$` (e.g. `$norm$`). The book italicises a
  term it is defining; the fix is `\textit{norm}`, and the tell is that it is the
  only "word" in math in the whole book. (`\ $` with a single letter is normal —
  `$f$`, `$x$` — do **not** flag those.)
* **hard-coded numbers** — `Theorem`/`Corollary`/`Lemma`/`Inequality`/`Eq.`
  followed by a literal `1.25`. Convert to `\ref{...}` **only if the label exists**;
  check first (`grep -c 'label{thm:c1-1-25}' chapters/*.tex`).

## Beyond the four: what a FULL-TEXT pass actually turns up

Running the four classes over the whole book is necessary but not sufficient. A
full-text proofreading pass (`先全文审稿`) on Stein–Weiss PMS-32 found **~90 further
defects**, clustering into these shapes. Each one has a cheap detector:

| tag | shape | detector | real example found |
|---|---|---|---|
| `NOBRACE` | super/subscript missing its braces, so only ONE char is scripted | `\^[A-Za-z]{2,}` / `_[A-Za-z]{2,}` | `e^irs` → `e^{irs}`; `e^-ry` → `e^{-ry}`; `\varepsilon^np-n` → `\varepsilon^{np-n}` |
| `BAR_SWALLOW` | an absolute-value `\|` eaten into `[`/`{`/`,` | count `\|` per inline-math group, flag ODD; or `\int\limits_{[`/`\big]` | `\|t\|>\varepsilon` → `[t]>\varepsilon`; `\big\|_{0}^{\eta}` → `\big]_{0}^{\eta}` (OCR read the bar as `]`) |
| `SUB_COMMA` | a subscript digit eaten into a comma | `[a-z], *[<>]` | `x_1 > 0` → `x, > 0` |
| `EMPTYOP` | `\mathop{}` / `\operatorname{}` left empty by OCR | `\\math(op|open|ord|bin|rel)\{\}` | `e^{i t s}\mathop{}` → delete |
| `WORDSPLIT` | an English word cut in half by a stray `$` | `\$[a-z]{1,3} [a-z]{1,3}\$`, `Iff ` | `$of f$` → `of $f$`; `Iff is` → `If $f$ is`; `tends t o` → `tends to`; `{a s}` → `as`; `iong` → `long` |
| `TEXTGLUE` | `\text{…}` lost its leading/trailing space | `\\text\{[a-z]+\}[a-z]` | `\text{for}k` → `\text{ for }k` |
| `STARPOS` | `*` placed as superscript vs baseline | grep `weak` / `sgn` | `weak*` is a **superscript star**; `sgn*` is a **baseline star** — in the SAME book. Never assume, always check the page. |

Two of these are worth extra emphasis:

* **`BAR_SWALLOW` is the most damaging and the least visible.** An odd `|` count
  inside `$…$` is the cheapest detector there is and it caught three real defects in
  one pass (`scan_ocr4.py`). `\big]` where `\big|` is meant is the same bug in
  big-delimiter form — look for `\big`/`\Big`/`\bigg`/`\Bigg` followed by `]` or `[`
  and check each has a partner.
* **`STARPOS` proves you cannot generalise within a book.** `weak*` and `sgn*` sit
  three chapters apart and are typeset *differently*. The only authority is the page.

### Prose layer: a bootstrap spell scan (when you have no dictionary)

`pip install pyspellchecker` will fail on an offline/sandboxed box, and there is no
`aspell`/`/usr/share/dict`. Use the book's **own** word frequency instead — an OCR
residue is almost always a *hapax* one edit away from a common word:

1. strip comments and math, tokenise prose words;
2. keep tokens appearing **exactly once** in the whole book;
3. for each, find high-frequency words (count ≥ 20) at edit distance ≤ 1;
4. report `rare -> common`.

This found `thorem`→`theorem` and `moveover`→`moreover`. **Both turned out to be
typos in the PRINTED BOOK** (`moveover,`, `Thorem 4.6` are on the page), so under the
"page image is the authority" rule they were **kept**. That is the correct outcome —
the scan's job is to *nominate*, the page decides. Expect ~40 nominations per book of
which ~2 are real; the rest are legitimate words (`shell`, `band`, `pt`, `act`).

### LaTeX-structure defects masquerading as OCR defects

Not every breakage is OCR. Splitting a long `aligned` row across source lines left a
`{{}` group unclosed, producing a genuine `Missing } inserted.` — but only visible
under `-file-line-error` as `ch04.tex:665:`, **not** as `! `. See the sibling skill
`mathtranslation-build-verify` (§ Scan the log) for that trap. Check brace balance
**per alignment row** (split on unescaped `\\`, then count `{}` with `\{`/`\}` removed)
rather than per source line — that is what localises it to one row.

## Method

1. **Locate the reader's complaint by page.** Dump the PDF text
   (`pdftotext main.pdf /tmp/mt.txt`), split on `\f`, and search for the phrases
   around footnote bands. Render each candidate page and actually look at it.
2. **Run the scanners, not your eyes.**
   * `scripts/mathaudit.py [chapters/chXX.tex …]` — inline **and** display blocks,
     all four classes. Aim for **0 findings**.
   * `scripts/fnaudit.py` — footnote-only pass: `$` parity, `\left/\right`, brace
     balance, display-in-footnote, whole-word-in-math, hard-coded numbers.
   * `scripts/fndump.py --all`, `scripts/fnshow.py` — dump note bodies with their
     source line numbers when you need to read one.
3. **Triage every hit against the page image** before touching anything. Some hits
   are correct as written (see the false-positive catalogue below). Confirm the
   *intended* form on the image, not from the OCR.
4. **Fix with substring-replace edits**, one module per batch:
   `EDITS = [(file, 1-based-line, old_substring, new_substring), …]`. Before applying,
   assert every `old` occurs **exactly once** in its line — a batch that dies halfway
   leaves the tree half-edited. Apply bottom-up per file so line numbers stay valid,
   and preserve the file's line-ending style.
   * If the finding came from a `$…$` group that **opened** on an earlier line (a
     footnote body spans lines!), the reported line is where `$` opened, not where
     the text sits. Re-grep the literal text (`grep -n '\$norm\$' chapter.tex`) to get
     the real line.
5. **Re-scan to 0** and rebuild. Acceptance: scanners 0; **both**
   `grep -cE '\.tex:[0-9]+:' main.log` **and** `grep -c '^!' main.log` equal 0
   (with `-file-line-error` most errors have no leading `!`, so the first grep alone
   is not a valid clean bill of health); `undefined` 0, `\newlabel` count unchanged,
   `Overfull` count unchanged.
6. **Render the fixed spots** and compare side-by-side with the same page of the
   original book. A scanner proves the pattern is gone; only the render proves the
   *layout* came out right (an integral restored to the main line changes the line
   count of the paragraph).
7. **Record the class in the project's conventions file** with the concrete
   before/after pair, so the next transcription pass does not re-introduce it.

## False-positive catalogue (do not "fix" these)

* **`$dx_1 dx_2$` opening math.** A regex for "roman `d`-word after a closing `$`"
  must track in/out of math, otherwise every `$dx = …$` is flagged. Also exclude the
  English word *do* — whitelist the differential letters (`tsxyzruvwnm`).
* **`y_0 > 0`, `p_0 < 1`, `\|f\|_2 \leq \ldots`.** A subscript digit followed by a
  relation is usually just a comparison. Only flag it when it hangs off a *big
  operator* (`\int`, `\sum`, `\oint`).
* **A display inside a footnote.** Two books' worth of these are faithful — e.g. the
  Jensen `(*)` note and an operator-definition note. Confirm by finding the
  `display_formula` block at the same place in the OCR dump; if it is there, the
  display is the book's, keep it.
* **"Section 3 of Chapter II", "see (5.5)".** Prose section references are correct
  as literals when the book's sections carry no labels. Only flag
  theorem/corollary/lemma/inequality/equation numbers.
* **`\left.` / `\right.` partials.** Count `\left`/`\right` *with* the dotted
  variants folded in, or a legitimate multi-line split reports a mismatch.
* **Single letters in math.** `$T$`, `$F$`, `$f$` are normal. Only a **multi-letter**
  bare word (`{2,}`) is suspicious.

## Bugs your own scanner will have (all of these bit once)

* **Clearing the math buffer only on close.** If you clear the accumulator when `$`
  closes but not when it opens, every "group" is prefixed by the prose that preceded
  it, and every balance check reports nonsense.
* **Swallowing backslash commands.** If the escape branch (`\` + next char) `continue`s
  without appending to the buffer, all `\`-based checks (`\int…`, `\}`, `\left`)
  silently never fire — the scanner reports a clean bill of health. Keep the two
  characters in the buffer while in math.
* **Splitting `$` parity across a footnote.** Scanning a chapter as one stream is
  fine **only** if you treat `\footnote{…}` as its own context (or reset parity at
  blank lines); a single stray `$` otherwise cascades and mis-groups the rest of the
  chapter.
* **Heredoc backslash mangling.** Piping a Python scanner through a quoted shell
  heredoc can eat one backslash per escape (`'\\'` → `'\'`), killing the script with
  `SyntaxError`. Write the scanner to a real file; do not inline it.

## Closing the loop

Report the root cause explicitly ("the OCR layer was wrong; the transcription copied
it; the printed page is correct — here is the image"), because the instinct is to
blame the transcriber. Then note what is **not** yet covered: in a book that
italicises defined terms on first use, a full emphasis audit needs a page-by-page
image comparison and is a separate, larger job — say so rather than silently fixing
one word.
