#!/usr/bin/env python3
"""Compare fraktur-letter usage between the original and the translation (whole-book).

Usage:
    python fraktur_audit.py <orig.md|orig.tex> <trans_dir_or_file>

The TRANSLATION argument should be the project DIRECTORY (it concatenates every
chapter .tex, skipping _scratch/backup). Comparing the whole original against the
whole translation is essential: a single chapter file would show false
"only-in-original" gaps simply because other chapters' fraktur lives elsewhere.

Counts every \\mathfrak{X} single letter in each source and prints
`letter | orig | trans`. Letters present in only one source are listed at the end.
High-count "only-translation" letters are real gaps to fix; single-occurrence
"only-original" letters are almost always OCR misreads (e.g. \\mathfrak{K}(s) is
really \\Re(s)) -- verify with show_context.py before flagging a translation error.
"""
import sys, os, re, glob

PAT = re.compile(r'\\mathfrak\{([A-Za-z])\}')
SKIP = ('_scratch', 'backup', '.bak')

def load(path):
    if os.path.isdir(path):
        parts = []
        for f in glob.glob(os.path.join(path, "**", "*.tex"), recursive=True):
            if any(s in f for s in SKIP):
                continue
            parts.append(open(f, encoding='utf-8', errors='replace').read())
        return "\n".join(parts)
    return open(path, encoding='utf-8', errors='replace').read()

def counts(text):
    d = {}
    for m in PAT.finditer(text):
        d[m.group(1)] = d.get(m.group(1), 0) + 1
    return d

def main():
    o = counts(load(sys.argv[1])); t = counts(load(sys.argv[2]))
    print("letter | orig | trans")
    print("-------+------+------")
    for L in sorted(set(o) | set(t)):
        print("   %s   |  %4d |  %4d" % (L, o.get(L, 0), t.get(L, 0)))
    only_o = {L: o[L] for L in o if L not in t}
    only_t = {L: t[L] for L in t if L not in o}
    print("\n-- only in original  (usually OCR artifact; verify) --", only_o)
    print("-- only in translation (real gap if high count) --------", only_t)
    print("\nNOTE: a single-occurrence 'only-original' letter is almost always an OCR")
    print("misread (\\mathfrak{K} -> \\Re(s)). Check context before flagging.")

if __name__ == "__main__":
    main()
