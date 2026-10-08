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
- [ ] If required by the selected template, Chinese prose double quotes use the TeX ligatures (two grave accents opening,
      two straight apostrophes closing), not Unicode curly quotes.
- [ ] If the MathTranslations template is selected, Chinese prose sentences
      end in ASCII `.` and first-introduction terms use unique `\newterm` keys.
- [ ] Translator additions are visibly distinguished from source content.
- [ ] AI terminology follows source definitions; model, dataset, library, and
  metric identifiers retain their spelling and case.
- [ ] English inside code, algorithms, literal examples, and intentional bilingual
  terms has not been "fixed" by residual-English cleanup.

## Pass 2: Mathematics And Structure

- [ ] Every definition preserves the defined object and its scope.
- [ ] Every hypothesis, conclusion, quantifier, negation, and uniqueness claim
  matches the source.
- [ ] Formula symbols, indices, limits, signs, delimiters, and equation order
  match the source PDF.
- [ ] Theorem-like environment types and proof boundaries are preserved.
- [ ] Section hierarchy, lists, examples, exercises, figures, and tables are
  complete and in the correct order.
- [ ] Every commutative/morphism diagram is rebuilt with `tikzcd`;
  nodes, labels, directions, arrow styles, and commutativity match the source.
- [ ] Other figures use faithful source assets or suitable redrawings; raster
  crops retain readable labels. Architecture/flow diagrams use suitable geometry.
- [ ] If required by the selected template, display formulas use `align`-family environments with no juxtaposed
  `\[ \]` blocks; ordered lists use `enumerate`, never manual numbering.
- [ ] Labels are unique and all references resolve to the intended objects.
- [ ] Citation keys and locators match the source.
- [ ] Suspected source errors are recorded instead of silently altered.
- [ ] Code/pseudocode keywords (including `for`, `do`, `end for`, `Input`, and
  `Output`), identifiers, literals, indentation, control flow, bounds, and
  numbered lines match the source; only safe explanatory comments are translated.
- [ ] Literal prompts and expected outputs remain source data; API versions,
  hyperparameters, and examples have not been modernized.
- [ ] AI formulas preserve tensor shapes, axes, conditioning, normalization,
  gradients, and scalar/vector distinctions.
- [ ] Architecture graphs retain their dimensions, edges, and parameter labels;
  plots/tables retain values, units, scales, metrics, and experimental qualifiers.

## Pass 3: Build And Visual Comparison

- [ ] The full project build succeeds from a clean or documented state using
  its actual build command; stale generated auxiliary data was cleared if needed.
- [ ] Bibliography, index, glossary, and cross-references are resolved; no
  undefined references/citations, no `LaTeX Error`, no missing figures, no rerun
  warnings in the log.
- [ ] The audit script reports no unexplained errors or warnings; the
  `mathtranslations` profile was used only for the corresponding selected template.
- [ ] Displayed numbering, including algorithms and listings, matches the source
  edition; no template-specific numbering scheme was imposed without comparison.
- [ ] The generated PDF has been compared with the source PDF page by page or
  section by section.
- [ ] Display equations, tables, figures, captions, footnotes, and page breaks
  are readable and not clipped.
- [ ] Every `tikzcd` diagram compiles without overlap, clipping, missing labels,
  or arrows pointing to the wrong node.
- [ ] Fonts contain all required Chinese and mathematical glyphs.
- [ ] Changed code and algorithm pages were visually compared with the source;
  keywords render in the source language, with readable indentation and wrapping.
- [ ] Overfull boxes, bad breaks, widows, and orphans have been reviewed where
  they materially affect reading.
- [ ] Links and bookmarks point to the correct destinations.
- [ ] If the class loads `biblatex`, `main.tex` does not contain a
  manual `\usepackage{biblatex}` (would cause an option clash).
- [ ] When used, MathTranslations long-proof links and environments are paired.
- [ ] When used, MathTranslations exercises and answer prefixes preserve source order and
  navigate to the intended counterparts.
- [ ] If a template cover is used, metadata no longer contains sample title, author, translator,
      model, edition, or date values, and the `\Translator 翻译及重排` credit
      line sits directly below the publisher line.
- [ ] Selected template commands such as `\makecover`, `\makecontents`,
      `\makebibliography`, and `\printterminology` are called as required;
      when used, `\printterminology` is the final
      document content.

## Completion Note

Record:

- scope reviewed;
- source edition and files used;
- compilation command and result;
- date or version of external terminology resources consulted;
- unresolved ambiguities and known visual differences;
- any intentional departure from the source.
- code/algorithm review coverage and any embedded image text or custom
  environments requiring manual review.
