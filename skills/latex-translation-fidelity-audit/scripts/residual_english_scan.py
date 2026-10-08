#!/usr/bin/env python3
"""Find English structural words and algorithm-prose candidates in Chinese LaTeX.

Usage:
    python residual_english_scan.py <dir_or_file> [glob=*.tex]

Scans .tex sources for English theorem-like structural words
(Theorem/Lemma/Proof/Remark/Corollary/Proposition/Definition/Example/Exercise/
Chapter/Section/Appendix/Note/Claim/Fact). Lines that are:
  - inside a LaTeX comment (%),
  - inside the bibliography (thebibliography block OR \\bibitem lines),
  - inside an intentional erratum note (\\erratum{...}),
  - inside supported literal code or inline code,
  - a reference/book title (a line containing \\emph{...} that looks like a
    citation, e.g. "Roquette, Peter: \\emph{The Brauer...}"),
are EXCLUDED (those carry English on purpose). Any REMAINING hit is a candidate
untranslated-prose location to inspect by eye.

NOTE for biblatex projects: references are pulled from a .bib via \\printbibliography
and never appear as a thebibliography environment; titles that are typeset inline
(e.g. inside \\footnote{...}) are caught by the \\emph{...} citation heuristic
above, not by the bibliography block strip.

Scratch/backup dirs (_scratch, backup, *.bak) and the bundled reference masters
under MathTranslations/templates/legacy/ are skipped automatically.
Algorithm environments are checked separately for English descriptions and prose
steps, with math, TeX commands, and syntax keywords ignored. This heuristic can
miss short/custom prose or flag identifiers: inspect every candidate against the
source. A zero count is not proof of complete translation or appendix coverage.
"""
import sys, os, re, glob

# Keep this helper self-contained so the focused skill can be used independently.
PROTECTED_RE = re.compile(
    r'\\begin\s*\{(?P<protected_env>verbatim\*?|Verbatim\*?|BVerbatim|LVerbatim|lstlisting|minted)\}'
    r'.*?\\end\s*\{(?P=protected_env)\}', re.S
)
ALGORITHM_RE = re.compile(
    r'\\begin\s*\{(?P<algorithm_env>algorithm\*?|algorithmic|algorithm2e\*?|procedure|function)\}'
    r'.*?\\end\s*\{(?P=algorithm_env)\}', re.S
)
MATH_RE = re.compile(
    r'(?<!\\)\$\$.*?(?<!\\)\$\$|(?<!\\)\$[^$]*?(?<!\\)\$'
    r'|\\\[.*?\\\]|\\\(.*?\\\)', re.S
)
KEYWORDS = re.compile(
    r'\b(?:Algorithm|Input|Output|Require|Ensure|Procedure|Function|for|while|do|'
    r'end|if|then|else|elseif|return|repeat|until|break|continue|to|true|false)\b', re.I
)
PROSE_CUES = re.compile(
    r'\b(?:Parameter|Gradient|Sample|Initialize|Compute|distribution|'
    r'independently|probability|supported)\b', re.I
)


def blank(match):
    """Keep character offsets and physical line numbers stable."""
    return re.sub(r'[^\r\n]', ' ', match.group(0))


def algorithm_prose_lines(text):
    """Return candidate line numbers, not an instruction to translate tokens.

    Whole executable listings remain masked by mask_protected. Only algorithm
    prose is considered here; custom wrappers still require rendered-page review.
    """
    candidates = set()
    for match in ALGORITHM_RE.finditer(text):
        body = MATH_RE.sub(blank, match.group(0))
        # Preserve explicit identifiers, URLs, and environment names as data.
        body = re.sub(r'\\(?:begin|end|label|ref|eqref|cite\w*|texttt|url|'
                      r'operatorname)\*?(?:\[[^\]]*\])?\{[^{}]*\}', blank, body)
        body = re.sub(r'\\[A-Za-z@]+\*?', blank, body)
        body = KEYWORDS.sub(blank, body)
        first_line = text.count('\n', 0, match.start()) + 1
        for offset, line in enumerate(body.splitlines()):
            words = re.findall(r'\b[A-Za-z][A-Za-z-]{2,}\b', line)
            if PROSE_CUES.search(line) or len(words) >= 3:
                candidates.add(first_line + offset)
    return candidates


INLINE_RE = re.compile(
    r'\\(?:verb\*?|lstinline(?:\[[^\]]*\])?|'
    r'mintinline(?:\[[^\]]*\])?\{[^{}]*\})(?P<delim>[^\s{])'
    r'[^\n]*?(?P=delim)'
    r'|\\(?:lstinline(?:\[[^\]]*\])?|'
    r'mintinline(?:\[[^\]]*\])?\{[^{}]*\})\{[^{}\n]*\}'
)


def mask_protected(text):
    """Mask supported regions without moving findings to the wrong line.

    Not a full TeX parser: custom environments and nested inline braces need review.
    """
    text = re.sub('|'.join([r'(?<!\\)%[^\r\n]*',
                           PROTECTED_RE.pattern, INLINE_RE.pattern]), blank, text, flags=re.S)
    text = re.sub(r'\\begin\{thebibliography\}.*?\\end\{thebibliography\}', blank, text, flags=re.S)
    return re.sub(r'\\erratum\{.*?\}', blank, text, flags=re.S)

WORDS = r'\b(Theorem|Lemma|Proof|Remark|Corollary|Proposition|Definition|Example|Exercise|Chapter|Section|Appendix|Note|Claim|Fact)\b'
SKIP = ('_scratch', 'backup', '.bak')

def iter_files(target, g):
    if os.path.isdir(target):
        for f in glob.glob(os.path.join(target, "**", g), recursive=True):
            if any(s in f for s in SKIP):
                continue
            if re.search(r'(?:^|/)MathTranslations/templates/legacy/',
                         f.replace('\\', '/'), re.I):
                continue
            yield f
    else:
        yield target

def main():
    target = sys.argv[1]
    g = sys.argv[2] if len(sys.argv) > 2 else "*.tex"
    found = 0
    for f in iter_files(target, g):
        txt = open(f, encoding='utf-8', errors='replace').read()
        txt = mask_protected(txt)
        algorithm_lines = algorithm_prose_lines(txt)
        body_txt = ALGORITHM_RE.sub(blank, txt)
        body_lines = body_txt.splitlines()
        for i, line in enumerate(txt.splitlines(), 1):
            if line.lstrip().startswith("%"):
                continue
            if i in algorithm_lines:
                print("%s:%d: [algorithm prose candidate] %s" % (f, i, line.strip()[:120]))
                found += 1
                continue
            # Outside algorithms, retain the existing structural-word scan.
            code = body_lines[i - 1].split("%", 1)[0]
            if re.search(WORDS, code):
                # skip \bibitem reference lines
                if re.search(r'\\bibitem', code):
                    continue
                # strip simple \emph{...} title spans (no nested braces) before matching,
                # so book/article titles inside footnotes don't look like untranslated prose
                code_noe = re.sub(r'\\emph\{[^{}]*\}', '', code)
                if re.search(WORDS, code_noe) is None:
                    continue
                # skip reference-list entries ("\noindent Author: \emph{Title}... Springer, pp.")
                # which legitimately carry English (book-series names like "...Sciences Section")
                if re.search(r'\\noindent', code) and re.search(r'\\emph\{|ISBN|pp\.|Springer|Soc\.', code):
                    continue
                print("%s:%d: %s" % (f, i, line.strip()[:120]))
                found += 1
    print("\nCandidate untranslated-prose lines (literal code/comments/bib/erratum/ref-titles excluded): %d" % found)
    if found == 0:
        print("No candidates under these heuristics; manually check prose and document coverage.")

if __name__ == "__main__":
    main()
