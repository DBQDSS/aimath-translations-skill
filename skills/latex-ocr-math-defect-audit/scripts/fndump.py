"""Dump every footnote that contains math, with its source line.

Usage:
    python ocr/fndump.py            # only math-bearing footnotes
    python ocr/fndump.py --all      # every footnote
"""
import io
import glob
import sys

BS = chr(92)  # one backslash


def find_footnotes(text):
    """Return [(lineno, body)] for every balanced-footnote in text."""
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
        out.append((text[:p].count(chr(10)) + 1, text[i:j - 1]))
        k = j
    return out


def has_math(body):
    return ('$' in body) or (BS + 'begin{' in body) or (BS + '[' in body)


def main():
    show_all = '--all' in sys.argv
    total = maths = 0
    for f in sorted(glob.glob('chapters/ch0*.tex')):
        for ln, body in find_footnotes(io.open(f, encoding='utf-8').read()):
            total += 1
            hm = has_math(body)
            maths += hm
            if not (show_all or hm):
                continue
            print('%-12s L%-5d %s' % (f.split('/')[-1], ln, body[:260].replace(chr(10), ' ')))
    print(chr(10) + '--- footnotes: %d total, %d with math ---' % (total, maths))


if __name__ == '__main__':
    main()
