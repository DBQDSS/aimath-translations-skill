# Review Checklist

Use three distinct passes. Combining them encourages the reviewer to notice
fluent Chinese while missing a mathematical or structural defect.

## Pass 1: Chinese And Terminology

- [ ] The Chinese is natural, concise, and suitable for mathematical writing.
- [ ] No source sentence, heading, caption, footnote, or list item is omitted.
- [ ] Terms match the project glossary and current authoritative usage.
- [ ] Pronouns and omitted subjects remain unambiguous.
- [ ] Logical connectors retain their force.
- [ ] Proper names, transliterations, acronyms, and capitalization are stable.
- [ ] Punctuation and spacing are consistent.
- [ ] Chinese double quotes use the TeX ligatures (two grave accents opening,
      two straight apostrophes closing), not Unicode curly quotes.
- [ ] If the MathTranslations template is selected, Chinese prose sentences
      end in ASCII `.` and first-introduction terms use unique `\newterm` keys.
- [ ] Translator additions are visibly distinguished from source content.

## Pass 2: Mathematics And Structure

- [ ] Every definition preserves the defined object and its scope.
- [ ] Every hypothesis, conclusion, quantifier, negation, and uniqueness claim
  matches the source.
- [ ] Formula symbols, indices, limits, signs, delimiters, and equation order
  match the source PDF.
- [ ] Theorem-like environment types and proof boundaries are preserved.
- [ ] Section hierarchy, lists, examples, exercises, figures, and tables are
  complete and in the correct order.
- [ ] Every arrow-and-node mathematical diagram is rebuilt with `tikzcd`;
  nodes, labels, directions, arrow styles, and commutativity match the source.
- [ ] Other figures follow the template priority: re-rendered at 400 DPI from a
  clean vector source PDF with `pymupdf` and autocropped (preferred for clarity),
  ordinary TikZ for simple figures.
- [ ] Display formulas use `align`-family environments with no juxtaposed
  `\[ \]` blocks; ordered lists use `enumerate`, never manual numbering.
- [ ] Labels are unique and all references resolve to the intended objects.
- [ ] Citation keys and locators match the source.
- [ ] Suspected source errors are recorded instead of silently altered.

## Pass 3: Build And Visual Comparison

- [ ] The full project build succeeds from a clean or documented state
  (`bash tools/build.sh full` for the `mathtranslation.cls` workflow: xelatex ×2
  → biber → xelatex ×2). Auxiliary files were cleared after any template or
  `main.tex` change.
- [ ] Bibliography, index, glossary, and cross-references are resolved; no
  undefined references/citations, no `LaTeX Error`, no missing figures, no rerun
  warnings in the log.
- [ ] The audit script reports no unexplained errors or warnings
  (`--profile mathtranslations --strict`).
- [ ] Displayed numbering was verified by extracting text from the compiled PDF:
  定义 `X.M.K`, 定理/问题/图 `X.Y` match the source book; no stray three-level
  numbers.
- [ ] The generated PDF has been compared with the source PDF page by page or
  section by section.
- [ ] Display equations, tables, figures, captions, footnotes, and page breaks
  are readable and not clipped.
- [ ] Every `tikzcd` diagram compiles without overlap, clipping, missing labels,
  or arrows pointing to the wrong node.
- [ ] Fonts contain all required Chinese and mathematical glyphs.
- [ ] Overfull boxes, bad breaks, widows, and orphans have been reviewed where
  they materially affect reading.
- [ ] Links and bookmarks point to the correct destinations.
- [ ] `biblatex` is loaded only by the class — `main.tex` does not contain a
  manual `\usepackage{biblatex}` (would cause an option clash).
- [ ] MathTranslations long-proof links and environments are paired.
- [ ] MathTranslations exercises and answer prefixes preserve source order and
  navigate to the intended counterparts.
- [ ] Cover metadata no longer contains sample title, author, translator,
      model, edition, or date values, and the `\Translator 翻译及重排` credit
      line sits directly below the publisher line.
- [ ] `\makecover`, `\makecontents`, `\makebibliography`, and `\printterminology`
      are each called exactly as required; `\printterminology` is the final
      document content.

## Completion Note

Record:

- scope reviewed;
- source edition and files used;
- compilation command and result;
- date or version of external terminology resources consulted;
- unresolved ambiguities and known visual differences;
- any intentional departure from the source.
