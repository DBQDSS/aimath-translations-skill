#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Probe equation-tag geometry AND the "gap before tag" signature.

A genuine display-equation tag is flush right while the equation itself is centred,
so there is usually a LARGE horizontal gap between the last math span and the tag.
An in-text reference such as "... by (2)." ends a justified line with only an
interword space (~3 pt) in front of the "(2)".  Measuring that gap lets us reject
the in-text false positives.
"""
import collections
import re
import sys

import pymupdf

ORIG = r'F:\大学\数字资源\数学\分析学\泛函分析\吉田耕作\functional analysis Yosida.pdf'
OURS = 'main.pdf'

TAG = re.compile(r'^\(\s*\d+\s*(?:[\u2032\u2019\']*)\s*\)$')


def spans_of_line(line):
    return [s for s in line['spans'] if s['text'].strip()]


def analyse(path, label, xmin, pages):
    d = pymupdf.open(path)
    print('#' * 72)
    print(label, '| page0 =', d[0].rect)
    gaps = []
    samples = []
    for i in pages:
        pg = d[i]
        for b in pg.get_text('dict')['blocks']:
            for l in b.get('lines', []):
                ss = spans_of_line(l)
                for k, s in enumerate(ss):
                    t = s['text'].strip()
                    if s['bbox'][2] >= xmin and TAG.match(t):
                        if k > 0:
                            gap = s['bbox'][0] - ss[k - 1]['bbox'][2]
                            prev = ss[k - 1]['text'].strip()[-24:]
                        else:
                            gap = -1.0
                            prev = '(line start)'
                        gaps.append(gap)
                        samples.append((i + 1, round(gap, 1), t, prev))
    hist = collections.Counter()
    for g in gaps:
        if g < 0:
            hist['<0 (line start)'] += 1
        elif g < 4:
            hist['0-4'] += 1
        elif g < 8:
            hist['4-8'] += 1
        elif g < 15:
            hist['8-15'] += 1
        elif g < 30:
            hist['15-30'] += 1
        elif g < 60:
            hist['30-60'] += 1
        else:
            hist['>=60'] += 1
    print('candidates:', len(gaps))
    for k in ['<0 (line start)', '0-4', '4-8', '8-15', '15-30', '30-60', '>=60']:
        if hist[k]:
            print('   gap %-16s %d' % (k, hist[k]))
    print('   -- smallest-gap samples (likely in-text refs):')
    for s in sorted([x for x in samples if x[1] >= 0])[:12]:
        print('      p%-4d gap=%-6s %-6s after %r' % s)
    print()


if __name__ == '__main__':
    rng_o = list(range(20, 120))
    rng_m = list(range(15, 115))
    analyse(ORIG, 'ORIGINAL', 365.0, rng_o)
    analyse(OURS, 'OURS', 505.0, rng_m)
