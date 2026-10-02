"""Audit the math inside every footnote for structural defects.

Usage:
    python ocr/fnaudit.py [--verbose]

Flags reported per footnote:
    ODD$      odd number of $ (unbalanced inline math)
    LR        \\left / \\right count mismatch
    BRACE     unbalanced { } inside a math group
    DISPLAY   a display env (\\[ \\], equation, align) inside a footnote
    WORD      math group holding a single plain word, e.g. $norm$ -> likely \\emph
    INTSUB    \\int_ / \\sum_ immediately followed by a relation (<, <=, \\leq)
    ROMAND    a roman differential (dt, dx, ...) left OUTSIDE math
    HARDC     hard-coded theorem/equation number (not via \\ref)
"""
import io
import glob
import re
import sys

BS = chr(92)
D = '$'


def find_footnotes(text):
    needle = BS + 'footnote{'
    out = []
    k = 0
    while True:
        p = text.find(needle, k)
        if p < 0:
            break
        i = p + len(needle)
        depth = 1
        j = i
        while j < len(text) and depth:
            c = text[j]
            if c == BS:
                j += 2
                continue
            if c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
            j += 1
        out.append((p, text[:p].count(chr(10)) + 1, text[i:j - 1]))
        k = j
    return out


def math_groups(body):
    """Split body on unescaped $ into groups; return list of (kind, text)."""
    parts = []
    cur = []
    i = 0
    inmath = False
    while i < len(body):
        c = body[i]
        if c == BS:
            cur.append(body[i:i + 2])
            i += 2
            continue
        if c == D:
            parts.append((inmath, ''.join(cur)))
            cur = []
            inmath = not inmath
            i += 1
            continue
        cur.append(c)
        i += 1
    parts.append((inmath, ''.join(cur)))
    return parts, inmath  # inmath True at end == unbalanced


def brace_ok(s):
    depth = 0
    i = 0
    while i < len(s):
        c = s[i]
        if c == BS:
            i += 2
            continue
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth < 0:
                return False
        i += 1
    return depth == 0


def audit(body):
    flags = []
    parts, unbalanced = math_groups(body)
    if unbalanced:
        flags.append('ODD$')
    maths = [t for m, t in parts if m]
    joined = ' '.join(maths)
    if joined.count(BS + 'left') != joined.count(BS + 'right'):
        flags.append('LR')
    if joined.count(BS + 'left.') != joined.count(BS + 'right.'):
        pass  # \left. / \right. partials are legitimate
    for t in maths:
        if not brace_ok(t):
            flags.append('BRACE')
            break
    if (BS + '[' in body) or (BS + 'begin{equation}' in body) or (BS + 'begin{align' in body):
        flags.append('DISPLAY')
    for t in maths:
        # a lone multi-letter word in math is almost always meant as \emph text
        if re.fullmatch(r'[A-Za-z]{2,}', t.strip()):
            flags.append('WORD(%s)' % t.strip())
    # a big operator whose SUBSCRIPT is a bare digit then a relation:
    #   \int_0 < \varepsilon   (the braced form \int_{0<\varepsilon} is fine)
    if re.search(re.escape(BS) + r'(int|sum|oint)_[0-9]\s*[<>]', joined):
        flags.append('INTSUB')
    # roman differential sitting right after a closing $ (i.e. outside math)
    for m, t in parts:
        if not m:
            if re.search(r'^\s*d[a-z]\b', t):
                flags.append('ROMAND')
                break
    # a bare "Theorem 2.16" / "Corollaries 2.16 and 2.17" that is NOT a \ref.
    # "Section 3 of Chapter II" is prose and stays literal (the book has no
    # section labels), so Section/Chapter are deliberately excluded.
    if re.search(r'(Theorem|Theorems|Corollary|Corollaries|Lemma|Lemmas|'
                 r'Proposition|Propositions|Inequality|Eq\.)\s*~?\s*'
                 r'[0-9]+(\.[0-9]+)?', body):
        if BS + 'ref' not in body:
            flags.append('HARDC')
    elif BS + 'ref' in body and re.search(r'(and|,)\s+[0-9]+\.[0-9]+', body):
        flags.append('HARDC')
    return flags


def main():
    verbose = '--verbose' in sys.argv
    n = 0
    bad = 0
    for f in sorted(glob.glob('chapters/ch0*.tex')):
        src = io.open(f, encoding='utf-8').read()
        for pos, ln, body in find_footnotes(src):
            n += 1
            has_math = (D in body) or (BS + 'begin{' in body) or (BS + '[' in body)
            if not has_math and not verbose:
                continue
            fl = audit(body)
            if fl:
                bad += 1
                print('%-12s L%-5d  %-14s  %s'
                      % (f.split('/')[-1], ln, ','.join(fl), body[:150].replace(chr(10), ' ')))
    print(chr(10) + '--- %d footnotes scanned, %d flagged ---' % (n, bad))


if __name__ == '__main__':
    main()
