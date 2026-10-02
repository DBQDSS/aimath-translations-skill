# -*- coding: utf-8 -*-
"""Prove that every footnote the OCR recorded reached the delivered .tex.

    python check_footnote_text.py <project-root> [chapter numbers...]

``<project-root>`` must hold ``src/chN.blocks.md`` (OCR dump) and
``chapters/ch0N.tex`` (delivered book).  Default chapter range is 1..7.

Two independent checks per chapter, because they fail differently:

  * **count** -- number of ``\\footnote{`` in the .tex vs number of distinct
    notes in the OCR dump.  Fastest signal that something is missing.
  * **text**  -- for each OCR note, is a run of its words present in the .tex?
    Tells you *which* note went missing.

``norm`` keeps runs of alphabetic words only, so a symbol the OCR wrote as
plain text (``p > 2``) versus the same symbol in math (``$p > 2$``) does not
break the match; match any 3-word window rather than the opening words, for
the same reason.

Exit status is non-zero when a note is unaccounted for.
"""
import io
import os
import re
import sys

BLOCK = re.compile(r'^<<p(\d+)\|([a-z_]+)\|bbox=\[([^\]]*)\]>>(.*?)(?=^<<p|\Z)',
                   re.S | re.M)
HEAD = re.compile(r'^\s*\$\s*\^\{?(\d+)\}?\s*\$\s*(\S.*)$', re.S)

root = sys.argv[1] if len(sys.argv) > 1 else '.'
chapters = [int(x) for x in sys.argv[2:]] or list(range(1, 8))


def norm(s):
    s = re.sub(r'\\index\{[^{}]*\}', '', s)
    s = re.sub(r'\$[^$]*\$', ' ', s)
    s = re.sub(r'\\[a-zA-Z]+', ' ', s)
    s = re.sub(r'[^A-Za-z]+', ' ', s)
    return ' '.join(s.split()).lower()


def ocr_notes(ch):
    """``{number: (page, body)}`` -- first occurrence wins."""
    path = os.path.join(root, 'src', 'ch%d.blocks.md' % ch)
    text = io.open(path, encoding='utf-8').read()
    seen, dup = {}, []
    for m in BLOCK.finditer(text):
        if m.group(2) not in ('footnote', 'text'):
            continue
        h = HEAD.match(m.group(4))
        if not h:
            continue
        n = int(h.group(1))
        if n in seen:
            dup.append(n)
        else:
            seen[n] = (m.group(1), h.group(2))
    return seen, dup


bad = 0
for ch in chapters:
    tex_path = os.path.join(root, 'chapters', 'ch%02d.tex' % ch)
    tex = io.open(tex_path, encoding='utf-8').read()
    n_tex = len(re.findall(r'\\footnote\{', tex))
    notes, dup = ocr_notes(ch)
    flat = norm(tex)

    missing = []
    for num in sorted(notes):
        words = norm(notes[num][1]).split()
        n = min(3, len(words))
        if not any(' '.join(words[i:i + n]) in flat
                   for i in range(max(1, len(words) - n + 1))):
            missing.append(num)

    status = 'OK' if not missing else 'CHECK'
    print('ch%02d  OCR notes %2d  \\footnote{} in .tex %2d  %-5s  unmatched %s'
          % (ch, len(notes), n_tex, status, missing or '-'))
    if dup:
        print('        NOTE: OCR repeats number(s) %s -- the first one wins; '
              'check the original page' % sorted(set(dup)))
    for num in missing:
        print('        note %d (OCR p%s): %s'
              % (num, notes[num][0], re.sub(r'\s+', ' ', notes[num][1])[:90]))
        bad = 1
    # the .tex may legitimately hold MORE notes than the OCR (a misread
    # number); only fewer is a definite defect
    if n_tex < len(notes) - len(missing):
        print('        .tex has fewer notes than the OCR dump -- real loss')
        bad = 1

print()
print('footnote text check: %s' % ('FAIL' if bad else 'OK'))
sys.exit(bad)
