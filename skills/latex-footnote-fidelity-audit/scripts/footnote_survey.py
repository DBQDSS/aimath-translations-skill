# -*- coding: utf-8 -*-
"""List every footnote-looking block of an OCR block dump.

    python footnote_survey.py <block-file> [FN_TOP]

``<block-file>`` is an OCR dump whose blocks are delimited by
``<<pPAGE|label|bbox=[x0,y0,x1,y1]>>`` headers (edit ``BLOCK`` if your dump
differs).  For each block that opens with a footnote reference it prints the
page, the label, ``y0``, the note number and the opening words, so you can see:

  * notes whose ``y0`` is **below** the collection threshold ``FN_TOP``
    (default 950) -- those are the ones a naive ``y0 > FN_TOP`` test misses;
  * note numbers that appear on more than one page -- those silently
    overwrite each other in a ``{number: text}`` dict.

Also flags every reference *written inside a block* that the seven known
footnote-marker forms do **not** cover, which is where the notes get lost.
"""
import io
import os
import re
import sys
from collections import defaultdict

BLOCK = re.compile(r'^<<p(\d+)\|([a-z_]+)\|bbox=\[([^\]]*)\]>>(.*?)(?=^<<p|\Z)',
                   re.S | re.M)
HEAD = re.compile(r'^\s*\$\s*\^\{?(\d+)\}?\s*\$\s*(\S.*)$', re.S)

# the seven reference forms that are understood (see SKILL.md)
KNOWN = (
    r'\$\s*\^\{?(\d+)\}?\s*\$',                       # $ ^3 $
    r'\{\s*~\s*\}\s*\^\{?(\d+)\}?',                   # {~}^2
    r'\^\{\s*\\mathrm\{\s*~?\s*(\d+)\s*~?\s*\}\s*\}',  # ^{\mathrm{5}}
    r'\{\}\^\{?(\d+)\}?',                             # {}^{2}
    r'\\ldots\s*\^\{?(\d+)\}?',                       # \ldots^{7}
    r'(?<=[.,;:!?])\s*~?\s*\^\{?(\d+)\}?',            # .^4  ,^1  .~^9
)
SUP = {'\u00b9': '1', '\u00b2': '2', '\u00b3': '3', '\u2070': '0',
       '\u2074': '4', '\u2075': '5', '\u2076': '6', '\u2077': '7',
       '\u2078': '8', '\u2079': '9'}

path = sys.argv[1]
fn_top = float(sys.argv[2]) if len(sys.argv) > 2 else 950.0


def y0_of(bbox):
    try:
        return float(bbox.split(',')[1])
    except (IndexError, ValueError):
        return 0.0


text = io.open(path, encoding='utf-8').read()
blocks = [(m.group(1), m.group(2), m.group(3), m.group(4))
          for m in BLOCK.finditer(text)]

notes = defaultdict(list)          # number -> [(page, label, y0)]
for pg, lab, bb, c in blocks:
    h = HEAD.match(c)
    if not h:
        continue
    if lab == 'footnote' or re.match(r'^\S', h.group(2)):
        notes[int(h.group(1))].append((pg, lab, y0_of(bb)))

print('== footnote heads (%s) ==' % os.path.basename(path))
print('   %-5s %-8s %-6s %-6s %s' % ('note', 'page', 'label', 'y0', 'flag'))
for num in sorted(notes):
    for pg, lab, y0 in notes[num]:
        flags = []
        if y0 <= fn_top:
            flags.append('y0<=%g: NOT collected by a naive test' % fn_top)
        if len(notes[num]) > 1:
            flags.append('number repeats: dict key collides')
        print('   %-5d %-8s %-6s %-6g %s' % (num, pg, lab, y0, '; '.join(flags)))

# Ordinary exponents (`x^{2}`, `e^{a|x|}`) are far too common to report.  The
# distinguishing feature of a footnote mark is its POSITION: it follows
# sentence punctuation, a dollar (end of a math span) or starts the block.
# Anything left there after blanking the known forms is a real outlier.
print()
print('== superscripts in a footnote position that no known pattern covers ==')
found = {}
for pg, lab, bb, c in blocks:
    if lab not in ('text', 'display_formula', 'inline_formula',
                   'footnote', 'paragraph_title'):
        continue
    flat = re.sub(r'\s+', ' ', c)
    probe = flat                       # blank what the known patterns cover
    for pat in KNOWN:
        probe = re.sub(pat, ' ', probe)
    probe = re.sub('[%s]+' % ''.join(SUP), ' ', probe)
    for m in re.finditer(r'(?<=[.,;:!?$])\s*~?\s*\^\s*\{?\s*[^}\s]{0,10}\s*\}?',
                         probe):
        found.setdefault((pg, m.group(0).strip()),
                         flat[max(0, m.start() - 45):m.start() + 25])
if not found:
    print('   (none -- every reference matches one of the seven forms)')
for (pg, tok), ctx in sorted(found.items()):
    print('   p%-5s %-14s ...%s' % (pg, tok, ctx))
print()
print('   reminder: a reference need not contain a caret at all -- the book')
print('   used ``$\\theta$`` for a 6 and ``^{\\S}`` for a 9.  Read the original')
print('   page text layer (pdftotext -layout) when a note is still missing.')

print()
print('== footnote numbers that repeat (a {number: text} dict would collide) ==')
rep = {n: v for n, v in notes.items() if len(v) > 1}
if not rep:
    print('   (none)')
for n in sorted(rep):
    print('   note %-4d on pages %s' % (n, ', '.join(p for p, _, _ in rep[n])))
