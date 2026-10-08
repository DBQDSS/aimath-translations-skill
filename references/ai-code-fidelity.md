# AI, Code, And Algorithm Fidelity

Read this reference for AI/ML sources, or whenever a technical source contains
code, pseudocode, experiments, model diagrams, or computational examples.

## Code And Pseudocode Are Protected Content

Translation changes human-language explanation, not the program or algorithm.
Preserve the source's language and syntax even when the surrounding book is Chinese.

| Content | Treatment |
|---|---|
| Language and pseudocode keywords | Preserve `for`, `while`, `do`, `end for`, `if`, `else`, `return`, etc. exactly as used in the source. |
| Algorithm structural labels | Preserve source labels such as `Algorithm`, `Input`, `Output`, `Require`, `Ensure`, and `Procedure`; translate the descriptive title or explanation following them. |
| Identifiers and API names | Preserve spelling, case, scopes, function names, variable names, package names, and command-line flags. |
| Literals and executable examples | Preserve strings, numbers, booleans, paths, regexes, data keys, shell commands, configuration values, prompts used as model inputs, and expected outputs. |
| Structure | Preserve indentation, block boundaries, iteration limits, conditions, update order, assignment/comparison operators, return values, and numbered lines. |
| Comments and docstrings | Translate only explanatory natural language when doing so cannot change behavior. Preserve pragmas, type annotations, doctests, encoding declarations, machine-readable directives, and license notices. |
| Captions and surrounding prose | Translate naturally while keeping references to the original identifiers and line numbers exact. |

Do not replace ASCII syntax with full-width punctuation, curly quotes, or
Chinese token equivalents. Do not modernize deprecated APIs, fix a suspected bug,
change hyperparameters, or execute training/download examples as part of translation.
Record source defects separately; apply fixes or run examples only when requested.
An English token inside a listing is not evidence that translation is unfinished.

## Rendered Algorithm Keywords

LaTeX source commands can remain English while their rendered keywords become
Chinese. Inspect both the definitions and the compiled page. Preserve the defaults
of the project's chosen algorithm package unless source keywords require an exact
match; do not add Chinese keyword redefinitions such as
`\algrenewcommand{\algorithmicfor}{对于}` or
`\SetKw{KwRet}{返回}`. Check custom wrappers and class-level overrides as well.

For a source algorithm headed `Algorithm 1 Annealed Langevin Dynamics`, a
Chinese descriptive caption can be `Algorithm 1 退火朗之万动力学`. Its body must
retain `Input:`, `for ... do`, `end for`, and `Output:`. Explanatory comments may
be Chinese, while every symbol, loop bound, assignment, and update remains faithful.
Never render `for ... do` as Chinese control-flow prose.

Use an existing `algorithmic`, `algorithmicx`/`algpseudocode`, `algorithm2e`,
`listings`, `minted`, or verbatim setup rather than converting algorithms to
`enumerate` or screenshots. Do not load conflicting algorithm packages. Listing
support that needs external tools or shell escape must follow the project's
existing build configuration; do not enable unrestricted execution merely to
translate a book. Preserve line-reference labels and algorithm/listing counters.

## AI Mathematics And Terminology

- Preserve tensor shapes, index ranges, broadcasting, axis order, transpose vs.
  conjugate transpose, scalar/vector distinctions, and batch/sample notation.
- Compare expectation distributions, conditioning, loss signs, normalization
  factors, gradient targets, stop-gradient operators, update schedules, and
  optimizer states directly with the source. Do not silently standardize notation.
- Distinguish related terms by their definitions: likelihood vs. probability,
  score vs. scoring function, inference vs. prediction, policy vs. strategy,
  training vs. evaluation, and mathematical convergence vs. empirical performance.
- Keep model, dataset, benchmark, library, hardware, and metric names stable
  (including capitalization, version, and acronym). Translate generic concepts
  consistently; expand acronyms only when supported by the source.
- Preserve uncertainty and evidence strength: an empirical observation, heuristic,
  approximation, or assumption must not become a theorem or performance guarantee.
- Preserve literal prompt templates, input/output examples, and model-generated
  examples as source data. If a translated explanation is needed, put it outside
  the literal example and label it as a translation.

## Figures, Experiments, And References

Use `tikz-cd` for mathematical commutative diagrams. Neural-network architectures,
computational graphs, decision trees, attention maps, and pipeline diagrams may
need ordinary TikZ or a faithful source asset. Preserve tensor dimensions, edge
direction, shared weights, repeated blocks, and parameter labels.

Preserve experimental values, units, dataset splits, seeds, sample sizes, error
bars, baselines, ablations, metric direction, plot scales, and table emphasis.
Never regenerate missing results or replace a measured plot with invented data.
Translate captions, legends, and table headings when feasible; when labels are
embedded in an image and cannot be safely edited, provide translated context and
record the limitation. Never relabel a dataset/model identifier as ordinary prose.

Keep citations, DOIs, URLs, software versions, and access dates tied to the source
edition. A live documentation page does not authorize updating source code or
substituting a newer result. Translator explanations and verified errata must be
distinguished from the author's text.

## Verification

1. Inventory code listings, algorithms, prompts, diagrams, and experimental tables
   by chapter; align them with the original source.
2. Compare protected tokens and mathematical operations before and after translation.
   Separate safe comment translation from token changes. For OCR-only code, inspect
   the page image for lost indentation, `=`/`==`, `-`/`−`, `1`/`l`, and missing delimiters.
3. Compile and inspect every changed algorithm/listing page. Verify that keywords
   still render in the source language and that line numbers, indentation, wrapping,
   symbols, and comment placement remain readable.
4. Treat prose scanners as candidate generators. Code, pseudocode, identifiers,
   bibliography titles, dataset names, and intentional bilingual terms are allowed
   English. Do not apply a global "remove residual English" rewrite.
5. Report the scope and evidence of code/algorithm review, any custom environments
   requiring manual inspection, untranslated embedded image labels, and unresolved
   source defects. Static scans alone do not prove algorithmic equivalence.
