# Bundled Legacy Template

Use this guide for the locally supplied ctexart template. It is a fixed,
authorized snapshot, not a claim to include the website's latest release.
For a user-supplied `mathtranslation.cls`, use [template-profile.md](template-profile.md)
and inspect that exact file instead.

## Files And Preparation

Copy the following from `MathTranslations/templates/legacy/` to a new project's
root when this template is selected and no template was supplied:

- `mathtranslations-translation-template.tex`
- `logo.pdf`
- `LICENSE` (retain the upstream MIT attribution when redistributing these assets)

Keep the bundled originals unchanged. Edit the project copy, replacing the sample
metadata and sample Algebra text with the requested translation. Preserve a user's
existing files; inspect their template before using these resources.

## Actual Interface

The source declares `\documentclass[UTF8,12pt,fontset=none]{ctexart}`. It is an
article with chapter-like `\section` headings, not a ctexbook class:

- Use `\section` for its chapter-like level and `\subsection` below it.
  Do not assume native `\chapter`, `\frontmatter`, or `\mainmatter` commands exist.
- The cover is an explicit `titlepage`, followed by translator notes and a TOC.
  There are no class-level `\makecover`, `\makecontents`, or `\makebibliography`
  commands. Preserve the source's cover block and replace its metadata macros:
  `\BookTitleCN`, `\BookTitleEN`, `\OriginalAuthor`, `\OriginalEdition`,
  `\OriginalPublisher`, `\OriginalYear`, `\Translator`, `\ModelUsed`,
  and `\TranslationDate`.
- The first formal term introduction uses `\newterm{key}{中文术语}{English term}`;
  `\termcn{...}` emphasizes a term without adding an index entry.
  Keep one `\printterminology` at the end, after all translated material.
- The theorem-like counters are initially keyed to subsections. Adjust numbering
  in the project copy to match the source; never infer correctness from labels alone.
- `\longprooflink{key}{description}` pairs with `longproof` using the same key.
  `exercises` pairs with `answers` and its source subsection prefix.
- Bibliography entries use `mybibliography` and `\bibitem`, not biblatex by default.
  Do not add biber or texindy stages unless the actual project requires them.

## Build And Fidelity

Compile with XeLaTeX, normally at least twice and until references/TOC/index page
numbers stabilize. The template registers terminology with its own macros;
there is no default external terminology-index tool. Its Fandol CJK fonts and
CMU Serif font files must be installed along with the used TeX packages.
The resource bundle supplies files and instructions, not a TeX distribution.

Retain its link colors, cover credit placement, font roles, and chosen punctuation
conventions. Use real references and compare rendered counters with the source.
Translate all in-scope appendices and algorithm descriptions. Preserve pseudocode
syntax and literal code; template prose rules do not authorize rewriting them.
Read [AI/code rules](../references/ai-code-fidelity.md) and the
[review checklist](../references/review-checklist.md) for these shared constraints.
