# LaTeX And Mathematical Fidelity

Read this reference when editing TeX, recovering content from OCR, resolving
notation, or repairing a translated project.

## Preserve Semantic Structure

- Keep definitions, lemmas, propositions, theorems, corollaries, remarks,
  examples, exercises, proofs, and solutions in their corresponding semantic
  environments.
- Preserve the distinction between assumptions and conclusions.
- Check every negation, quantifier, comparison sign, set operation, index,
  bound, and condition.
- Keep equation grouping and alignment when it communicates derivation or
  equivalence.
- Do not normalize notation merely because another notation is more familiar.
- Use `enumerate` for ordered prose lists; preserve listing and algorithm line
  numbering in their native environments.

When the source seems mathematically wrong, record the exact location and the
evidence. Preservation and correction are separate editorial choices.

## Prefer Project-Native LaTeX

- Reuse existing commands, theorem styles, bibliography tools, and reference
  packages.
- Define a new macro only when it removes meaningful repetition or encodes a
  stable semantic choice.
- Avoid global package or class changes for a local translation issue.
- Keep generated files out of source directories when the project already has
  a build directory convention.

When the user explicitly selects the MathTranslations template, treat its
supplied TeX as the project-native style. Do not replace its terminology,
theorem, long-proof, exercise-answer, section, or hyperlink systems with a
generic alternative merely for convenience.

## References And Numbering

Every numbered object that is mentioned elsewhere should have a stable label.
Use the reference command already established by the project, such as `\ref`,
`\eqref`, `\autoref`, or `\cref`.

Never translate a source phrase into hard-coded output such as:

```tex
由定理 2.3 可知
```

Prefer:

```tex
由定理~\ref{thm:main}可知
```

Do not rename existing labels without updating all callers. Keep labels unique
across included files.

## Citations

- Preserve citation keys when importing source TeX.
- Check that every cited key exists in a bibliography source or `\bibitem`.
- Preserve page, theorem, chapter, and equation locators.
- Do not infer a publication year, author spelling, DOI, or title from memory.
- Distinguish a citation in the mathematical source from a translator's note.

## Chinese Typesetting

- Use natural Chinese punctuation in prose and mathematical punctuation that
  matches the surrounding syntax.
- Keep spaces, nonbreaking spaces, and line breaks intentional around references,
  names, units, and inline mathematics.
- Avoid raw Unicode mathematical lookalikes when a LaTeX command is intended.
- Keep proper names, acronyms, and transliterations consistent with the project
  glossary.
- Follow the project's existing convention for theorem names, quotation marks,
  emphasis, and parenthetical English.

The inspected MathTranslations profile has an unusual but explicit rule:
Chinese punctuation is used inside prose, while sentence-final punctuation is
an ASCII period `.` rather than `。`. Apply this only when that template is the
selected presentation authority. The same profile requires display formulas in
`align`, `aligned`, or `align*` environments (never multiple `\[ \]` blocks in
a row), ordered lists in `enumerate`, and Chinese double quotes written with
the TeX ligatures — two grave accents opening, two straight apostrophes
closing — rather than Unicode curly quotes.

The same profile uses Song for prose and examples, Kai for first-introduction
terms, Fang for most theorem-like bodies, and CMU Serif for English. Preserve
those roles unless the supplied template version says otherwise.

These are prose conventions. Do not apply them inside code, literal prompts,
or pseudocode syntax. Preserve the source keywords even if an algorithm package
offers localized definitions; check the compiled output as well as the TeX.
Descriptions after input/output labels, prose steps, verbal conditions, and safe
comments inside an algorithm still require translation; syntax protection does
not exempt its human-language content.
Read [ai-code-fidelity.md](ai-code-fidelity.md) for protected tokens, safe comment
translation, AI mathematics, experimental data, and algorithm verification.

## OCR And Transcription

Treat OCR as a draft, not evidence. Check common confusions including:

- `0`, `O`, `o`, and `\circ`;
- `1`, `l`, `I`, and `|`;
- `v`, `\nu`, `u`, and `\upsilon`;
- minus signs, hyphens, and long dashes;
- superscripts, subscripts, primes, bars, hats, and tildes;
- opening and closing delimiters;
- `\in`, `\ni`, `\subset`, and `\subseteq`;
- equation numbers mistaken for equation content.

For a formula recovered from an image, compare the compiled result visually
with the source before accepting it.

## Figures, Tables, And Assets

Check that every `\includegraphics` target resolves with the project's extension
and search-path rules. Do not redraw or replace mathematical diagrams unless
the user requests it or the source asset cannot legally or technically be used.
When the MathTranslations template is selected, follow its figure priority:
re-render the figure region at 400 DPI from a clean vector source PDF with
`pymupdf` and autocrop for clear figures, redraw simple figures with TikZ, and
rebuild arrow-and-node diagrams with `tikz-cd`. When recreating a diagram,
compare geometry, labels, orientation, and semantic relationships, not just
visual style.

The `tikz-cd` requirement concerns mathematical commutative/morphism diagrams.
Do not impose it on neural architectures, computation graphs, flowcharts, or plots.
Rendering a vector page to PNG is a rasterization step; verify small labels and
line clarity rather than claiming the result is lossless.

For arrow-and-node mathematical diagrams, use:

```tex
\[
\begin{tikzcd}
A \arrow[r, "f"] \arrow[d, "g"'] & B \arrow[d, "h"] \\
C \arrow[r, "k"']                & D
\end{tikzcd}
\]
```

This requirement covers commutative diagrams, category diagrams, morphism
diagrams, pullback and pushout squares, and similar structures. Preserve:

- node order and relative placement;
- every arrow's source and target;
- labels and their side of the arrow;
- hooks, two-headed arrows, isomorphism marks, dashed arrows, bends, and
  parallel arrows;
- stated or visually implied commutativity.

Do not substitute a screenshot, OCR image, Mermaid diagram, or generic table
for a diagram that `tikz-cd` can express. Use ordinary TikZ or a source image
only when `tikz-cd` would lose essential geometry or visual meaning.

## Compilation Discipline

Use the project's build command. A successful single engine invocation may not
resolve bibliography, index, glossary, or cross-reference data, so run the full
build sequence.

For the `mathtranslation.cls` template, the canonical build is
the project's actual full build command (for example, `bash tools/build.sh full`
when that script is supplied): the first
xelatex pass records labels and terminology entries, biber resolves the
bibliography, and the later passes resolve page numbers, links, the table of
contents, and the terminology table. **After any change to the class or
`main.tex` changes template behavior, clear stale generated auxiliary files (`main.aux`, `main.toc`, `main.out`,
`main.bbl`, `main.bcf`, `main.run.xml`) and rebuild clean** — a stale `.toc`
from another template version can crash the first pass with an undefined
control sequence such as `\InAppendixToctrue`.

Inspect logs for:

- LaTeX errors and undefined control sequences;
- undefined or multiply defined references and citations;
- missing files and fonts;
- overfull or underfull boxes that affect readability;
- rerun requests;
- bibliography, index, and glossary failures.

Compilation proves syntactic and toolchain consistency. It does not prove that
the translation or mathematics is correct, and a clean build can still ship
wrong displayed numbers — verify theorem, definition, figure, algorithm, and
listing numbers against the source edition by inspecting the compiled PDF.
