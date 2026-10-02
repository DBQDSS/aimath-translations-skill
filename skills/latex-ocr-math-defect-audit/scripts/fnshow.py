"""Print the full text of selected footnotes (by chapter + line number)."""
import io
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
        out.append((text[:p].count(chr(10)) + 1, text[i:j - 1]))
        k = j
    return out


targets = [('ch01', 38), ('ch02', 161), ('ch03', 45), ('ch03', 978), ('ch03', 1190),
           ('ch04', 579), ('ch06', 125), ('ch06', 486), ('ch07', 138), ('ch07', 1369),
           ('ch02', 1342)]

for ch, ln in targets:
    for l, body in find_footnotes(io.open('chapters/%s.tex' % ch, encoding='utf-8').read()):
        if l == ln:
            print('=' * 78)
            print('%s:%d' % (ch, ln))
            print(body)
            break
    else:
        print('=' * 78)
        print('%s:%d  NOT FOUND' % (ch, ln))
