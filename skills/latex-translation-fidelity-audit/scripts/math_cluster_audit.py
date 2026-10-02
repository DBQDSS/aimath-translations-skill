#!/usr/bin/env python3
"""Best-effort per-source math-cluster comparison for translation fidelity.

Usage:
    python math_cluster_audit.py <orig.md> <trans.tex>

Why local extraction (not global balance): the translation .tex has a globally
unbalanced $ count because \\erratum{} embeds $ and \\[...\\] nests $. A global
balance loop would swallow whole paragraphs as "math". So we extract math LOCALLY,
per delimiter, with findall on each pattern in turn.

Pipeline per cluster:
  - keep only if is_math() double-gate passes (math signal OR Greek; AND not >=3
    English words of length >=3, which means prose);
  - normalize (strip \\, \\; \\: \\!, ~, font cmds, single-letter macros, braces,
    all whitespace) so \\mathbb{Q}_p == \\Q_p.
Then report clusters unique to each source.

CAVEAT: PaddleOCR wraps very little math in $...$, so the "orig-only" set is
mostly noise (naming diffs, \\frac->frac residue, superscript fragments, custom
macros). Use this as a SPOT-CHECK, not a verdict: the translation's clusters
normalizing to expected forms is the real signal.
"""
import sys, os, re, glob

MATH_SIGNALS = set(r"\ _ ^ 0123456789+-*/|<>.~=()[]")
GREEK = set("αβγδεζηθικλμνξοπρστυφχψωΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ")
ENGLISH = re.compile(r'\b[a-zA-Z]{3,}\b')
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

def extract_math(text):
    clusters = []
    for p in [r'\$\$(.+?)\$\$', r'\$(.+?)\$', r'\\\[(.+?)\\\]', r'\\\((.+?)\\\)']:
        for m in re.finditer(p, text, re.S):
            clusters.append(m.group(1))
    return clusters

def is_math(seg):
    has_signal = any(c in MATH_SIGNALS for c in seg) or any(g in seg for g in GREEK)
    if not has_signal:
        return False
    if len(ENGLISH.findall(seg)) >= 3:
        return False
    return True

def normalize(s):
    s = re.sub(r'\\[,;:!]', '', s)
    s = s.replace('~', ' ')
    s = re.sub(r'\\(mathbb|mathfrak|mathrm|mathbf|mathcal|operatorname|text|textbf|mathit|mathsf|mathscr)\b', '', s)
    s = re.sub(r'\\([A-Za-z])', r'\1', s)      # \Q -> Q, \C -> C
    s = s.replace('{', '').replace('}', '')
    s = re.sub(r'\s+', '', s)
    return s

def clusters_of(text):
    return {normalize(c) for c in extract_math(text) if is_math(c)}

def main():
    orig = load(sys.argv[1])
    trans = load(sys.argv[2])
    co = clusters_of(orig); ct = clusters_of(trans)
    only_o = co - ct; only_t = ct - co
    print("orig clusters: %d | trans clusters: %d" % (len(co), len(ct)))
    print("\n=== ORIG-only (%d) — mostly OCR noise, verify before flagging ===" % len(only_o))
    for c in sorted(only_o):
        print("  ", c[:90])
    print("\n=== TRANS-only (%d) ===" % len(only_t))
    for c in sorted(only_t):
        print("  ", c[:90])

if __name__ == "__main__":
    main()
