# Terminology Decisions And Person Names

Read this policy before creating, enforcing, or revising a project glossary.
It governs translated prose and indexes independently of the chosen template.

## Candidate Data Is Not Authority

[terminology/terms.tsv](terminology/terms.tsv) is a small editorial candidate
list, not a verified dictionary, community export, or assertion of consensus.
Its `source_term`, `candidate_zh`, `sense`, `status`, `evidence`, and `note`
fields help locate a possible
choice; neither a populated row nor a confident note validates that choice.
All bundled entries remain candidates; a status or evidence field describes
recorded information, not an endorsement of every use of the entry.
An imported dictionary, previous translation, or existing project glossary can
also contain errors. Do not trust any of them without checking the actual sense.

Use this decision order:

1. Honor the user's explicit terminology requirements within the task scope.
   If a requested wording would alter a source definition, show the conflict and
   preserve the mathematical claim rather than concealing the mismatch.
2. Read the source definition, surrounding usage, field, notation, and edition
   to determine the concept. The source fixes meaning, even when a familiar
   English spelling is used differently in another field.
3. Consider deliberate project decisions with recorded evidence for that same
   sense. Recheck inherited decisions when evidence is absent or conflicts arise.
4. Compare actually inspected, relevant Chinese references or specialist
   terminology resources. Record the specific page, section, or entry and its
   applicability; competing references do not establish a universal preference.
5. Use bundled or external glossary entries only as candidates. Familiarity
   and memory can suggest wording but cannot substantiate a verification claim.

Project consistency follows validation; it does not make an incorrect choice
authoritative. Template commands determine how to print and index a term, not
which translation is correct. Do not mechanically apply the TSV or perform
global replacements across prose, mathematics, citations, or protected tokens.

## Record Evidence And Uncertainty

Maintain a project-local glossary separate from the bundled candidate data.
At minimum, each adopted or disputed term records:

| Field | Required information |
|---|---|
| Source form and sense | Exact spelling; field, definition, and relevant exception |
| Source location | Edition and actual PDF page/section or supplied-source location |
| Proposed rendering | Chinese wording with any preserved name component |
| Supporting evidence | Inspected reference and pinpoint location, or explicitly none |
| Decision status | Adopted with evidence, provisional, or unresolved |
| Alternatives and scope | Rejected variants, contextual exceptions, and affected files |

For a new or disputed entry, inspect nearby definitions and at least the uses
that distinguish plausible senses. Validate a candidate against those passages
before checking consistency through the project. Use targeted changes only after
identifying which occurrences share that sense; then review the changed passages
and rendered index. The same English word may legitimately have several Chinese
renderings in one book.

If evidence is insufficient, retain the English form at introduction and use a
clearly provisional Chinese description where it preserves meaning. Record the
uncertainty and continue independent work; do not invent a consensus or hide the
issue behind a glossary entry. An English term retained for this reason must be
distinguishable from untranslated prose during review.

Local source pages and supplied references suffice to make progress. Online
corroboration can help when accessible or requested; network access, a login, or
a paid database is not a prerequisite. Record what was actually inspected and
what remains unverified. An inaccessible URL, search snippet, or remembered
spelling is not a completed reference check. Resource refresh or redistribution
requires an explicit maintenance scope and provenance/license review.

## Preserve Every Person-Name Component

Keep the original source spelling of person names and person-derived terms.
Do not transliterate them into Chinese, even if a candidate glossary or an old
translation supplies a familiar Chinese transliteration. Translate surrounding
generic words as appropriate to the source definition:

| Source term | Rendering pattern |
|---|---|
| Cauchy sequence | Cauchy 序列 |
| Fréchet derivative | Fréchet 导数 |
| Hahn–Banach theorem | Hahn–Banach 定理 |
| Annealed Langevin Dynamics | 退火 Langevin 动力学 |

These illustrate name preservation, not verification of a term's mathematical
sense. Apply the rule to standalone author names and named theorems, lemmas,
spaces, operators, transforms, distributions, methods, algorithms, optimizers,
equations, and other named concepts. It covers body text, titles and headings,
captions and labels, tables, footnotes, exercises, covers, bibliography author
fields, and terminology/index entries. An acronym stays as printed; do not
invent its expansion or a person's full name.

Identify person-name components from the source context or inspected evidence;
this is not a demand to trace the historical etymology of every ordinary word.
Terms such as `algorithm` and `algebra` remain ordinary concepts to translate.
If the source itself gives a person's name in Chinese or another script, preserve
that source form; do not reconstruct an unprinted Latin spelling or replace it
with a different name form. The rule forbids introducing a transliteration in
place of the printed name, not retaining a name already printed that way.

Preserve capitalization, accents and other diacritics, initials, name particles,
compound surnames, and source spelling variants. For a person-derived form such
as `Gaussian` or `Bayesian`, keep that printed form instead of replacing it with
a Chinese transliteration or reconstructing `Gauss` or `Bayes`. Do not expand,
shorten, anglicize, or normalize a name from memory. If the source prints
`Frechet`, do not silently add an accent; if OCR gives `Frechet` but the source
page prints `Fréchet`, recover `Fréchet` from the page and record the OCR repair.
Handle genuine source spelling conflicts in the issue log before normalization.

Use Unicode or equivalent LaTeX accent markup that renders the same name in the
project's actual engine; check accents and compound names in the generated PDF.
For example, a terminology entry may use
`\newterm{frechet-derivative}{Fréchet 导数}{Fréchet derivative}` when the inspected
template supports that command. Never rename an existing stable key merely to
make it resemble the displayed name.

Code identifiers, API names, macros, labels, citation keys, paths, URLs, and
literal strings/prompts remain exact, including their ASCII spellings. Thus
`frechet_distance` stays unchanged even when prose prints `Fréchet`. Do not add
diacritics or translate a string inside protected data. Preserve required legal
notices and verbatim source quotations; provide a separated explanation when
needed rather than altering the quoted artifact.

## Review And Claims

Check named terms against the source spelling, then check generic terms against
the recorded sense and evidence. A residual-English scan must allow deliberate
name preservation, syntax, identifiers, bibliography data, and documented
bilingual/provisional terms. Scanner hits require contextual review, not blanket
translation or deletion.

Report the glossary scope, evidence inspected, provisional/unresolved decisions,
and any source spelling conflict. Say a choice is project-specific when that is
what the evidence supports. Do not claim every entry has been verified unless
each entry in that stated scope has a traceable completed check.
