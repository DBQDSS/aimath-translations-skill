---
name: latex-footnote-fidelity-audit
description: >
  Audit a re-typeset LaTeX math book so that EVERY footnote the OCR recorded actually
  reaches the printed PDF, then fix the ones that do not. Use when a scanned classic is
  being re-typeset (chapters/*.tex built from an OCR source) and you must prove nothing
  silently vanished — especially when a footnote reference was written by the scanner in
  an odd form ($^3$, {~}^2, .^4, ^{	extrm{5}}, {}^{2}, \ldots^{7}, Unicode superscripts),
  when a note body is missing, when a footnote band sits above the usual page threshold,
  or when an index entry disappeared because the \index{} mark lived inside a lost note.
metadata:
  agent_created: true
---

# Footnote fidelity audit for OCR-based LaTeX re-typesetting

## When to use

You are re-typesetting a scanned math book from an OCR block dump
(`<<pN|label|bbox=[...]>>` style, or any per-block OCR output) and the numbering /
formula / coverage audits all read **0**, yet the book may still be losing whole
footnotes. Run this audit **before** declaring the book finished.

Why it matters: a dropped footnote is not a small typographic loss.

> **Sibling skill.** This one covers whether every note *reaches* the PDF. Once they
> are all there, the *math inside them* may still be mangled by the OCR layer —
> integrals stolen into exponents, lost set-of-integration subscripts, misplaced
> braces, differentials outside math. Use `latex-ocr-math-defect-audit` for that axis;
> a green board here says nothing about it.

1. The note text disappears.
2. The sentence that follows the reference is often parsed as **mathematics** and
   rendered as italic gibberish (the scanner's marker was the only thing separating
   prose from math).
3. Any `\index{}` mark living inside the note body disappears too, so the printed
   index silently loses a real entry (measured once: 174 marks instead of 175).

## The one thing to internalise

**The scanner writes the same footnote reference in at least seven different ways,
and every one of them has been observed in a single book.** A converter that
recognises only `$ ^n $` will drop most notes. The forms seen:

| form | example | why it is safe to accept |
|---|---|---|
| `$ ^3 $` | the canonical one | — |
| `{~}^{2}` | canonical variant | — |
| `.^4`, `,^1`, `.~^9` | caret right after sentence punctuation | a superscript there cannot be an exponent |
| `^{\mathrm{5}}`, `^{\mathrm{~15~}}` | at the end of a display | an accent command is not an exponent |
| `{}^{2}`, `{}^{8}`, `{}^{10}` | empty group + superscript | an empty base is never a real exponent |
| `\ldots^{7}` | exp **on** `\ldots` | never a real exponent (keep the `\ldots`!) |
| `¹²³⁴⁵⁶⁷⁸⁹`, `¹²` | real Unicode superscript **characters** | usually only footnote marks in a math book |

Accept a candidate number **only when a note with that number really exists** —
that single guard makes all seven rules safe.

Two references defeat every generic rule and need an explicit repair table:
`$\theta$` for note 6, `^{	ext S}` for note 9. Always read the original page
(ABBYY/`pdftotext -layout` text layer is a fast guide) and register them by hand.

## Three independent loss modes

Check all three; fixing only the first is the classic mistake.

1. **Reference written in an unrecognised form** — the note is collected but never
   emitted. Diagnose by instrumenting the emitter: subclass it, record every note
   number that is actually expanded, and diff against the notes collected.
2. **Note never collected** — the collection rule is a geometric test
   (`bbox y0 > FN_TOP`, e.g. 950) and a tall footnote band can start *above* it
   (seen at y0 = 851 and 943). Widening the threshold naively is **wrong**: on one
   page the body text *resumes below* the footnote band, so a wider threshold
   swallows a whole paragraph into a note. Use an explicit per-page override
   (`{(chapter, page, note): how_many_following_blocks}`).
3. **Note absorbed or split wrongly** — a note can span several blocks (prose +
   display + continuation). Stop absorbing at the next footnote head, and remember
   the head itself is not part of the tail count.

## Two traps that only show up once footnotes are restored

- **A display inside a note.** A tagged display can live inside a footnote
  (`(*)` in a note). If you build the note body as one string and then run a
  dollar-counting "scanner repair" over it, a `\begin{equation}` in the middle makes
  the running `$` parity fall out of step and one `$` is **silently eaten**
  (`range of $f$` → `range of $f`). Fix each piece separately when a display is present.
- **Placeholder collision.** Reusing the repair pass's private sentinel character
  for your own footnote placeholder will corrupt it (`IndexError` on a saved-text
  list). Use a fresh control character that the rest of the pipeline does not own.

## Method

1. `scripts/footnote_survey.py <src-dir> <n>` — list every footnote-looking block
   per chapter with its page, `y0`, number and opening words. Spot y0 values below
   the collection threshold, and duplicate numbers (a repeated number silently
   overwrites the earlier note in a number-keyed dict).
2. `scripts/check_footnote_text.py <project-root> <n>...` — for each OCR note, look
   for its words in `chapters/ch0N.tex`. Reports `LOST`/`OK` per chapter.
3. Compare **counts**, not just text: the number of `\footnote{` in each `.tex`
   must equal the number of distinct notes the OCR recorded. A mismatch is the
   fastest signal; the text probe tells you *which* one went missing.
4. For every missing note, read the original page to find where the mark really sits
   (`pdftotext -layout -f P -l P book.pdf -`, then the page image), then fix by:
   extending the marker patterns, or adding a page-scoped repair entry.
5. Rebuild and **render the pages** that carry the restored notes. Verify the mark
   sits where the original prints it and the note text sits at the page foot.

## Pitfalls

- A footnote number repeated on two pages silently overwrites the first note in a
  `{number: text}` dict — key by `(page, number)` or refuse duplicates loudly.
- The `.tex` count can legitimately be **higher** than the OCR count: the OCR
  misreads an occasional number (a printed `16` read as `10`). Verify against the
  page image before "fixing" the `.tex` down to the OCR count.
- Hand-written chapters are not converter output — a converter-level probe reports
  false losses for them. Check those by counting `\footnote{}` in the delivered
  `.tex` and matching opening words.
- Word-matching normalisation must compare **runs of alphabetic words only**; a
  symbol written as plain text by the OCR becomes `$x$` in the `.tex` and is
  dropped by any normaliser that strips math. Match any 3-word window, not the
  opening words.
- Restoring a note can restore an `\index{}` with it — re-run the index audit
  afterwards and expect the mark count to go **up**.

## Closing the loop

After fixes: rebuild, then re-run *all* audits (numbering, formulas, index,
footnotes, coverage). Footnote failures are invisible to every other audit, so a
green board without this one proves nothing. Finally render and eyeball the pages
that carry restored notes — the audit proves presence, only the render proves
placement.
