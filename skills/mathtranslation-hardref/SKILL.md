---
name: mathtranslation-hardref
description: "This skill should be used when working on Chinese math book translations (mathtranslation.cls 数译 / mathtranslations.org, OR a book class like AJbook.cls / ctexbook) and the task is to convert hard-coded references into clickable cross-references. Covers two families: (A) theorem/equation references like 定理 3.4 / 方程 (22) → \\ref / \\eqref, and (B) bare printed-number references like (2.3) / 见 3.25 / cross-chapter (II, § 1) / internal page refs (p. 3) → \\ref / \\hyperlink / \\pageref, including how to add anchors where the target has no label. It captures the (non-obvious) counter models, the safe aux-derived mapping rule, and the hand-typeset-item technique."
metadata:
  agent_created: true
---

# Convert hard-coded references to clickable cross-references (mathtranslation.cls)

## Purpose

In a `mathtranslation.cls` translation, the audit profile `mathtranslations` flags plain-text
references like `定理 3.4` / `方程 (22)` as WARNINGs ("possible hard-coded reference"). The
translator's note usually promises "可点击的交叉引用" (clickable cross-references), so these
should become real `\ref` / `\eqref` links. This skill turns that into a safe, verifiable,
script-driven pass instead of error-prone manual editing.

## When to use

- After a first clean compile of a mathtranslation book, the audit reports many
  "possible hard-coded reference" warnings and the goal is to make them clickable.
- When asked to "optimize the translation / 优化翻译" and the glossary + template work is done
  but references are still hard-coded.
- Do NOT use this for the profile's two known false-positives (see Limitations).

## Legacy Counter Model (Verify Before Use)

The following model describes a legacy ctexart project, not every version of
`mathtranslation.cls`. Supplied v3.x classes may wrap ctexbook. Inspect the actual
class, counters, labels, and rendered numbers before running a converter.
Never rewrite code/pseudocode literals as cross-references.

1. `mathtranslation.cls` wraps `ctexart`. Theorem-like environments (`theorem`, `proposition`,
   `lemma`, `corollary`, `definition`, `remark`, `example`, `problem`) are declared with a
   **shared** counter via a compatibility layer such as
   `\newtheorem{proposition}[theorem]{命题}`.
2. The displayed number is `\thetheorem = \arabic{subsection}.\arabic{theorem}`, i.e.
   "**subsection.theorem**". The theorem counter **resets at each subsection**
   (numberwithin-style), so within a subsection it is a local sequence 1,2,3...
3. **Counters carry across `\input` files.** A chapter split into `part06a1.tex`,
   `part06a2.tex`, `part06b.tex` continues the same subsection/theorem counters. Simulating
   numbering for `part06b.tex` in isolation is WRONG — always simulate the full chapter chain
   loaded in `main.tex` order. The appended paper (`partgf1`+`partgf2`) is one continuous
   document (equation/subsection/theorem reset once before `partgf1`, then continuous).
4. `\mtsubsec{...}` subheadings also increment the shared theorem counter and display
   "subsection.theorem", sharing the sequence with theorems. `\mtsubsecn` does NOT increment.
5. Equation numbers are sequentially global in the main book (1..N) and reset+continuous across
   the appended paper. Use a global (non-GF) or combined-GF equation index accordingly.

## Safe mapping rule

Convert a hard-coded reference to a command **only when there is a UNIQUE candidate** label
satisfying ALL of:

- **Same file** (or, for the appended paper, anywhere in `partgf1`+`partgf2`),
- **Exact printed number** (read from `main.aux` `\newlabel{X}{{PRINTED}...}`),
- **Matching environment type** — `定理`→`theorem`, `命题`→`proposition`, `引理`→`lemma`,
  `推论`→`corollary`, `定义`→`definition`, `注`→`remark`, `例`→`example`, `问题`→`problem`;
  equations `公式/式/方程 (N)`→`\eqref`.

Ref commands (from the compatibility layer): `\thmref`, `\propref`, `\lemref`, `\corref`,
`\defref`, `\remref`, `\exref`, `\probref`, plus `\eqref` for equations.

Verify by recompiling **twice**; `0 Undefined reference` in the log proves every converted label
resolves. Visually the rendered text is unchanged (e.g. `命题 1.6` → `\propref{x}` still prints
"命题 1.6"), only now it is a hyperlink.

## Workflow

1. Compile twice to produce a current `main.aux`.
2. Run `scripts/convert_hardrefs.py` (dry-run by default) from the `translated/` directory.
   It prints per-file CONVERT / SKIP plans. Inspect the SKIP list.
3. If the plan is sensible, run `python convert_hardrefs.py --apply` to rewrite the `.tex` files.
4. Recompile twice; confirm `0 error`, `0 Undefined reference`.
5. Re-run the audit to confirm the hard-coded-reference warning count dropped.

## References that must stay manual (do NOT auto-convert)

- **Illustrative meta-text** inside the translator's note (e.g. `main.tex` "如``定理 3.4''") —
  intentionally literal, leave as-is.
- **`章第 X.Y`** section references — no label exists; leave.
- **Original book's 3-level numbering** such as `定理 1.3.2` — the translation uses 2-level
  "subsection.theorem"; leave.
- **Appendix single-number theorems** like `定理 13` — different numbering scheme; leave.
- **References to unlabeled statements** (the target theorem has no `\label`). These need a
  human to (a) add `\label{...}` right after the target `\begin{env}`, then (b) re-run the
  converter. When locating the target, simulate the full chapter chain; watch for **env-type
  mismatches** where the prose says `定理` but the statement is actually a `proposition` — that is
  an editorial discrepancy requiring a human decision (preserve the original word with `\thmref`
  to avoid changing the translated text, or fix the environment).

## Audit Findings

Review warnings against the selected template. The main audit supports both
legacy ctexart and supplied class projects; do not dismiss a class or final-index
warning solely because an earlier project treated it as benign.

## Bundled resources

- `scripts/convert_hardrefs.py` — the mapping/annotation script (dry-run + `--apply`). It reads
  `main.aux` for printed numbers, tracks theorem/equation environments per file (with full
  chapter-chain carryover for correct subsection numbers), and converts unique matches.
- `scripts/convert_bare_refs.py` — variant for **book classes** (AJbook.cls / ctexbook) whose
  theorem-like environments share ONE counter printed "section.item" and whose labels are
  `<type>:<chap><sec>.<item>`. Converts BARE printed numbers `(2.3)` / `见 3.25` / `(1.17, 1.22)`
  into `\ref`, plus explicit cross-chapter / page-ref / anchor edits via a config `EXACT` dict,
  and falls back to `\hyperlink` for hand-typeset unlabeled items. Dry-run + `--go`.

## Variant B — bare printed-number refs in a book class (AJbook.cls / Milne project)

When the source is a re-typeset **book** (not mathtranslation.cls), the same goal reappears in a
different shape. Real cases seen: `(2.3)`, `(1.2e)`, `见 3.25`, `(1.17, 1.22)`, cross-chapter
`(II, § 1)` / `(I, 例 A.5(d))` / `(VII, 注 A.6(a))`, and internal page refs `(p. 3)`.

Counter/label model (non-obvious):
- The book class declares theorem-like envs (`theorem`/`proposition`/`lemma`/`corollary`/
  `definition`/`remark`/`example` + custom `para`/`npara`/`summary`/`erratum`) sharing ONE
  `theorem` counter, printed per-section via `\counterwithin{theorem}{section}` → "**sec.item**".
- Labels are `<type>:<chap_prefix><sec>.<item>` — chap prefix in the label (`ii.`, `iv.`, …);
  chI (the first chapter) historically uses FLAT names (`lem:1.3`, `thm:0.1`). Exercises use
  `exc:`/`ex:` and can collide in printed number with theorems → always resolve by (chapter, number)
  from `main.aux`, never by guessing the type.
- Equations are NOT auto-numbered (`equation*` + hard `\tag`). So `(N.M)` in the running text is
  almost always a *theorem-counter* item, NOT an equation. Continuous formula refs `(5)`…`(44)`
  (single integer in parens) must be LEFT ALONE — they are `\tag`s, self-consistent.

**Derive the number→label map from `main.aux`, never hand-write it.** Parse
`\newlabel{lab}{{PRINTED}{PAGE}...}`, split the label into `type:` + `chap.item`, bucket by
chapter. Then for a bare number N in file F: look up `by_chap[chap(F)][N]` → `\ref{lab}`.
This is exactly `scripts/convert_bare_refs.py`.

Hand-typeset (unlabeled) numbered items — the tricky case:
- Some items (e.g. chII §1 `1.6`–`1.9`, chIV §1 `1.8`, chV §1 `1.12`/§4 `4.4`, chVIII §5 `5.3`/`5.8`)
  are typed as `\noindent\textbf{N.M}` or `\emph{N.M.}` (or `\subsubsection*{N.M …}`) and carry
  NO `\label`, so they never appear in `main.aux`.
- Do NOT add `\label` (it would rewrite the bold/emph visual and can disturb numbering). Instead
  insert `\phantomsection\hypertarget{item:<chap>.<N.M>}{}` immediately before them, and reference
  with `\hyperlink{item:<chap>.<N.M>}{N.M}` (preserves the exact printed look, still clickable).
- `\phantomsection` matters: without it hyperref reuses the previous anchor and links jump wrong.
- `\hyperlink` is legal inside math (e.g. a `\stackrel{(\hyperlink{...}{2.1})}{\simeq}` label).

Internal page references ("原书 p. 3" / "证明 p. 4 上定义的映射" / "见下文 p. 138"):
- Convert to `(本书 p.\pageref{<label-of-target>})`. If the target sentence has a label already
  (a section/theorem), reuse it; otherwise insert `\phantomsection\label{pg:origNN}` right before
  the target sentence and `\pageref` it. Keep `\erratum` footnotes and *external* bibliography
  page numbers untouched.

Cross-chapter references:
- `(II, § 1)` → `II, \S \ref{sec:II.1}` (section labels are `sec:<Roman>.<n>`, Roman is UPPER).
- `(I, 例 A.5(d))` → `(I, 例 \ref{ex:A.5}(d))`; `(VII, 注 A.6(a))` → `(VII, 注 \ref{rem:vii.A.6}(a))`.
- `(I 1.3)` → `(I \ref{lem:1.3})` (chI flat label); `(1.39e)` in chIII → `(\ref{prop:ii.1.39}e)`.
- **Chapter-number style — unify the book's OWN chapters, but never the foreign ones.** A `第 X 章`
  that points at *this* book must use the numeral the chapter headings actually print (here Roman
  `I`–`VIII`) and be clickable: `第 \ref{ch:VIII} 章`. The trap is that a finished translation often
  mixes styles for one and the same book — Chinese numerals, Roman, and bare `\ref{ch:X}` coexisting
  (this project: 30 / 12 / 5). Sweep the **whole tree**, not just the chapter files: the Introduction
  and the appendices carry some too.
  **Leave references to other books exactly as the original wrote them** — their numeral system is
  part of the citation. E.g. ANT / FT / Bucur–Deleanu / Artin–Tate print arabic (`ANT, Chapter 6` →
  `第 6 章`), while Serre 1962 / Serre 1970 / Milne 2006 print Roman (`Appendix to Chapter I` →
  `第 I 章`). Decide "foreign" from the preceding ~110 characters containing
  `\cite` / `ANT` / `FT` / `GT` / `Serre` / `Weiss` / `ArtinTate` / `Bucur` — and **mask comments
  first**, because a `% 第七章 …` file header is not a reference. Getting this wrong is silent:
  detect it only by rendering and grepping the PDF text for
  `第\s*(?:[0-9]+|[一二三四五六七八九十]+|[IVX]+)\s*章`, then reviewing each hit by hand.

Verification (mandatory): the acceptance bar for these books is
**0 error / 0 undefined reference / 0 multiply-defined / 0 Missing character / 0 Overfull hbox**,
then eyeball a few rendered snippets in the PDF (`page.get_text()`) to confirm real numbers
appear (never `??`). `\hypertarget` does not write to `.aux`, so those labels showing as "MISSING"
in `main.aux` is EXPECTED — confirm instead via the absence of hyperref "has been referenced but
does not exist" warnings.

## Variant A2 — cross-chapter bare refs `§VI.7.2` / `VI.6.16` (AJbook.cls, Roman-numeral style)

A finished AJbook translation often still carries the ORIGINAL book's Roman-numeral reference
style in running text: `\S V.3`, `§VI.7.1`, `[VI.\ref{ex:x}, VI.6.16]`, `习题~VI.6.5`,
`定义~VI.6.12`. These are cross-chapter refs that were never linked because the targets were
missing (or simply forgotten). Convert them with `scripts/`-style dry-run/apply scripts, but the
numbering model has three traps.

**Trap 1 — the aux anchor / `@cref` field is NOT the printed number.**
With `\thetheorem = \arabic{section}.\arabic{theorem}` and `\theprobctr` similar, the *printed*
number is `section.counter`, but hyperref writes the anchor as
`\newlabel{def:companion-matrix}{{7.4}{327}{…}{theorem.6.4}{}}` — `theorem.**6**.4` where 6 is the
**chapter**, not the section. The `@cref` entry repeats the same wrong field
(`{[theorem][4][6]7.4}`). This is invisible when chapter number == section number (e.g. §VI.6),
and wrong for every other section. **Always build the number→label map from field 1 of
`\newlabel` (the printed number), split by the counter named in field 4.**
Useful cross-check: `@cref` bracket 2 = counter value, bracket 3 = section (or `chapter,section`
for `probctr`).

**Trap 2 — four number spaces share the same key.** In an AJbook book the key `VI.7.2` can
simultaneously be (a) subsection 7.2, (b) theorem-counter item 7.2, (c) exercise 7.2, (d) in some
chapters a section. Never pick by "first map that has it". Resolve by context, in this order:

1. explicit `§` / `\S` prefix → section / subsection;
2. immediately-preceding marker word `定义|定理|命题|引理|推论|例|注记|断言|玩笑` → theorem counter;
3. immediately-preceding `习题|练习|题` → exercise counter;
4. inside a same-line `[...]` hint → exercise counter (the book's bracket hints point at exercises);
5. `习题` or `\ref{ex:` within the previous ~80 chars → exercise counter (catches
   `习题~V.\ref{ex:a} 与 V.4.8` and `Exercises VI.4.13 and VI.4.14`);
6. fallback subsection → theorem → exercise.

Then **verify the ambiguous ones against the original book text** (pdftotext dump):
grep for the literal hint string. Real case: `[VI.7.11, §VII.2.3]` and `[8.8, 9.1, III.1.4, VI.6.16]`
in the original proved both were EXERCISES even though a theorem item with the same number existed.

**Trap 3 — printed numbers differ in whether they carry the chapter.** In this family:
sections print `\thesection = chapter.section` (so `\ref{sec:…}` → `6.7`, chapter included),
while theorem items and exercises print only `section.counter` (`\ref{thm:…}` → `7.5`,
`\ref{ex:…}` → `4.13`). Hence the replacement rule:

- section / subsection target → replace the number with plain `\ref{lab}` (chapter comes along);
- theorem / exercise target → replace the number with `ROMAN.\ref{lab}` (keep the literal chapter
  numeral in the text, because `\ref` will not supply it).

Corollaries of the rule, both easy to get wrong:

- **Replace only the number; leave the prefix in place.** If the matched range starts at the
  number (not at `§`/`\S`), do NOT re-emit the prefix in the replacement or you get
  `\S \S~\ref{…}`. Back up the chapter files first and diff.
- **Count every `\begin{prob}`**, not only those whose `\label` follows immediately — in this
  book 14 exercises had the label several lines later, and an "immediately-following" regex
  silently shifted every later exercise number in those sections.

Same as Variant B: mask `\index{}` / `\label{}` / `\ref{}` / `\cite{}` regions before scanning
(index-heavy lines can carry real prose at the end — do not discard a whole line just because it
starts with `\index`), keep CRLF (`open(...,'wb')` after normalizing to `\r\n`), and finish with
`0 error / 0 undefined reference` plus a spot check that the printed PDF shows real digits.

## Pitfall: redefining theorem environments in an article-style child doc

When building a *standalone article* on top of `mathtranslation.cls` (e.g. extracting the
appendix paper from a book, `\documentclass{mathtranslation}` + own `\maketitle`), the class
already declares `theorem/definition/lemma/corollary/proposition/remark/example/problem` with
`[subsection]` counters. To re-declare them with your own numbering:

- DO `\let\theorem\relax\let\endtheorem\relax` (undefine env commands only).
- DO NOT `\let\c@theorem\relax` (do NOT kill the counters!). The cls registered these
  counters in its `\cl@subsection` reset list; killing them makes every later `\section`
  fail with `LaTeX Error: No counter 'definition' defined.` (error text is mis-attributed
  to the `\section` line — very confusing).
- Instead keep the class counters alive, create fresh shared counters
  (`\newcounter{mtthm}[section]`, `\newtheorem{theorem}[mtthm]{定理}`,
  `\newtheorem{definition}[mtthm]{定义}`, ...) and pin numbers with `\setcounter{mtthm}{N}`.
- Starred variants (`theorem*`, `problem*`, `conjecture*`, ...) are NOT auto-created by the
  class/amsthm; declare them explicitly with `\newtheorem*{theorem*}{定理}` etc.
- enumitem: legacy shorthand `enumerate[label=i.)]`/`[i.)]` fails with
  `Package enumitem Error: i.) undefined.` — use `enumerate[label=\roman*.)]`.
- amsthm `\newtheorem{example}[examplecnt]{例}[section]` is invalid (two optional args);
  use `\newcounter{examplecnt}[section]` + `\newtheorem{example}[examplecnt]{例}`.
