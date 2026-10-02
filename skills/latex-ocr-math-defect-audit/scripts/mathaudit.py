"""Scan chapters/*.tex for OCR-inherited math defects -- inline AND display.

Checks (high signal, tuned against this book):
    SEMIBR   "\\}" immediately followed by ";" inside math -- a closing brace
             misplaced in set-builder notation ("\\{z ... \\}; |z| < r\\}").
    SUPINT   a big operator stolen into an exponent
             ("(1/\\pi)^{\\int_{-\\infty}^{\\infty}} ...").
    LIMIT    a big operator whose subscript is a bare digit followed by a
             relation ("\\int_0 < \\varepsilon") -- the set of integration
             printed in the main line instead of the subscript.
    ROMAND   a roman differential (" dt", " dx", ...) left OUTSIDE math,
             i.e. text right after a closing $ or \\].

Usage:
    python ocr/mathaudit.py [file ...]      (default: chapters/ch0*.tex)
"""
import io
import glob
import re
import sys

BS = chr(92)
D = chr(36)

ENVS = ('equation', 'equation*', 'align', 'align*', 'gather', 'gather*',
        'multline', 'multline*', 'eqnarray', 'eqnarray*', 'alignat',
        'alignat*', 'flalign', 'flalign*', 'displaymath', 'math',
        'split', 'aligned', 'gathered', 'cases')


def skip_math(a, b, body):
    """Yield (tag, snippet) for the structural checks that apply to any math."""
    if BS + '}' + ';' in body:
        yield ('SEMIBR', body[:100])
    if re.search(r'\^\s*\{?\s*' + BS + BS + r'(int|sum|oint|iint|prod)', body):
        yield ('SUPINT', body[:100])
    if re.search(BS + BS + r'(int|sum|oint)[_^]?\s*[0-9]?\s*(<|>|' + BS + BS + r'leq|'
                 + BS + BS + r'geq)', body):
        yield ('LIMIT', body[:100])
    if re.search(re.escape('\\]') + r'\s*d[tsxyzruvwnm]\b', body):
        yield ('ROMAND', body[-90:])


def blocks(text):
    """Yield (lineno, body) for every inline $...$ group and display block."""
    # --- inline $...$ ---
    line = 1
    cur = []
    inmath = False
    start = 1
    i = 0
    while i < len(text):
        c = text[i]
        if c == chr(10):
            line += 1
        if c == BS and i + 1 < len(text):
            if inmath:
                cur.append(text[i:i + 2])
            i += 2
            continue
        if c == D:
            if inmath:
                yield (start, ''.join(cur))
                cur = []
            else:
                start = line
            cur = []
            inmath = not inmath
            i += 1
            continue
        if inmath:
            cur.append(c)
        i += 1
    if inmath:
        yield (start, ''.join(cur))
    # --- \[ ... \] and \begin{env} ... \end{env} ---
    for m in re.finditer(re.escape(BS + '[') + r'(.*?)' + re.escape(BS + ']'),
                         text, re.S):
        yield (text[:m.start()].count(chr(10)) + 1, m.group(1))
    for env in ENVS:
        pat = (re.escape(BS + 'begin{' + env + '}') + r'(.*?)'
               + re.escape(BS + 'end{' + env + '}'))
        for m in re.finditer(pat, text, re.S):
            yield (text[:m.start()].count(chr(10)) + 1, m.group(1))


def scan(path):
    text = io.open(path, encoding='utf-8').read()
    hits = set()
    for ln, body in blocks(text):
        for tag, snip in skip_math(ln, body, body):
            hits.add((ln, tag, re.sub(r'\s+', ' ', snip)))
    # roman differential right after a closing $ (tracked, so "$dx$" is fine)
    inmath = False
    i = 0
    while i < len(text):
        c = text[i]
        if c == BS and i + 1 < len(text):
            i += 2
            continue
        if c == D:
            if inmath and re.match(r'\s*d[tsxyzruvwnm]\b', text[i + 1:i + 10]):
                ln = text[:i].count(chr(10)) + 1
                hits.add((ln, 'ROMAND',
                          re.sub(r'\s+', ' ', text[max(0, i - 60):i + 9])))
            inmath = not inmath
        i += 1
    return sorted(hits)


def main():
    files = sys.argv[1:] or sorted(glob.glob('chapters/*.tex'))
    total = 0
    for f in files:
        hs = scan(f)
        if hs:
            print('### %s  (%d)' % (f, len(hs)))
            for ln, tag, ctx in hs:
                print('   L%-5d %-8s %s' % (ln, tag, ctx))
            total += len(hs)
    print(chr(10) + '--- %d findings ---' % total)


if __name__ == '__main__':
    main()
