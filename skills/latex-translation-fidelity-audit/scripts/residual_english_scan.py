#!/usr/bin/env python3
"""Find untranslated English structural words in a Chinese LaTeX translation.

Usage:
    python residual_english_scan.py <dir_or_file> [glob=*.tex]

Scans .tex sources for English theorem-like structural words
(Theorem/Lemma/Proof/Remark/Corollary/Proposition/Definition/Example/Exercise/
Chapter/Section/Appendix/Note/Claim/Fact). Lines that are:
  - inside a LaTeX comment (%),
  - inside the bibliography (thebibliography block OR \\bibitem lines),
  - inside an intentional erratum note (\\erratum{...}),
  - a reference/book title (a line containing \\emph{...} that looks like a
    citation, e.g. "Roquette, Peter: \\emph{The Brauer...}"),
are EXCLUDED (those carry English on purpose). Any REMAINING hit is a candidate
untranslated-prose location to inspect by eye.

NOTE for biblatex projects: references are pulled from a .bib via \\printbibliography
and never appear as a thebibliography environment; titles that are typeset inline
(e.g. inside \\footnote{...}) are caught by the \\emph{...} citation heuristic
above, not by the bibliography block strip.

Scratch/backup dirs (_scratch, backup, *.bak) are skipped automatically.
"""
import sys, os, re, glob

WORDS = r'\b(Theorem|Lemma|Proof|Remark|Corollary|Proposition|Definition|Example|Exercise|Chapter|Section|Appendix|Note|Claim|Fact)\b'
SKIP = ('_scratch', 'backup', '.bak')

def iter_files(target, g):
    if os.path.isdir(target):
        for f in glob.glob(os.path.join(target, "**", g), recursive=True):
            if any(s in f for s in SKIP):
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
        txt = re.sub(r'\\begin\{thebibliography\}.*?\\end\{thebibliography\}', '', txt, flags=re.S)
        txt = re.sub(r'\\erratum\{.*?\}', '', txt, flags=re.S)
        for i, line in enumerate(txt.splitlines(), 1):
            if line.lstrip().startswith("%"):
                continue
            code = line.split("%", 1)[0]
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
    print("\nCandidate untranslated-prose lines (comments/bib/erratum/ref-titles excluded): %d" % found)
    if found == 0:
        print("OK: no stray English structural words in the body.")

if __name__ == "__main__":
    main()
