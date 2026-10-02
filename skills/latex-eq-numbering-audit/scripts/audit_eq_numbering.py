#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Deterministic audit of OUR equation numbering, straight from main.aux.

Every numbered display in the transcription carries a label whose NAME encodes the
original book's own numbering:  eq:<ChapterRoman>.<Section>.<Number>[primes]

    \\label{eq:I.1.10}     -> should render as (10)
    \\label{eq:I.1.9'}     -> should render as (9')
    \\label{eq:I.8.12a}    -> tagged 12''  (suffix 'a' disambiguates duplicate names)

So we can check, with zero PDF guessing:
  1. rendered number (from \\newlabel) == integer in the label name
  2. within each (chapter, section) the integer sequence is non-decreasing and
     starts at 1  (the original numbers equations 1,2,3,... per section, with
     primed repeats such as 9, 9', 10 allowed)

Usage: python tools/audit_eq_numbering.py [--aux main.aux]
"""
import argparse
import collections
import re
import sys

LABEL = re.compile(r'^\\newlabel\{(?P<name>[^}]*)\}\{\{(?P<num>[^}]*)\}\{(?P<page>\d+)\}')
EQNAME = re.compile(r'^eq:(?P<ch>[IVX]+)\.(?P<sec>\d+)\.(?P<n>\d+)(?P<suf>[a-z]*)(?P<prime>\'*)$')


def parse_aux(path):
    out = []
    for line in open(path, encoding='utf-8'):
        m = LABEL.match(line.strip())
        if m:
            out.append((m.group('name'), m.group('num'), int(m.group('page'))))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--aux', default='main.aux')
    args = ap.parse_args()

    entries = parse_aux(args.aux)
    eqs = [(n, num, p) for (n, num, p) in entries if n.startswith('eq:')]
    print('total \\newlabel : %d' % len(entries))
    print('equation labels : %d' % len(eqs))

    unknown = [(n, num, p) for (n, num, p) in eqs if not EQNAME.match(n)]
    print('labels not matching eq:<Roman>.<sec>.<n> : %d' % len(unknown))
    for n, num, p in unknown[:40]:
        print('    %-34s -> %s   (p%d)' % (n, num, p))
    print()

    # ---- check 1: rendered integer == integer encoded in the label name ----
    bad1 = []
    for name, num, page in eqs:
        m = EQNAME.match(name)
        if not m:
            continue
        want = m.group('n')
        got = re.match(r'(\d+)', num)
        if not got or got.group(1) != want:
            bad1.append((name, num, want, page))
    print('CHECK 1  rendered number vs label-encoded number : %d mismatch' % len(bad1))
    for name, num, want, page in bad1[:60]:
        print('    %-34s rendered=%-8s label says %-5s (p%d)' % (name, num, want, page))
    print()

    # ---- check 2: per (chapter, section) the integers run 1,2,3,... non-decreasing ----
    groups = collections.OrderedDict()
    for name, num, page in eqs:
        m = EQNAME.match(name)
        if not m:
            continue
        key = (m.group('ch'), int(m.group('sec')))
        groups.setdefault(key, []).append((int(m.group('n')), name, num, page))

    bad2 = []
    for key, items in groups.items():
        it = sorted(items, key=lambda t: t[3])   # by page, then keep aux order
        seen = {}
        for n, name, num, page in it:
            seen.setdefault(n, []).append(name)
        ints = sorted(seen)
        if not ints or ints[0] != 1:
            bad2.append((key, 'does not start at 1', ints[:12]))
            continue
        for a, b in zip(ints, ints[1:]):
            if b != a + 1 and b != a:
                bad2.append((key, 'gap %d -> %d' % (a, b), ints[:20]))
                break
    print('CHECK 2  per-section integer sequence 1,2,3,... : %d anomalies' % len(bad2))
    for key, why, ints in bad2:
        print('    %-8s %-24s ints=%s' % ('%s.%d' % key, why, ints))
    print()

    # ---- check 3: duplicate rendered numbers within a section (unexpected) ----
    dup = []
    for key, items in groups.items():
        c = collections.Counter(n for n, _, _, _ in items)
        for n, k in c.items():
            if k > 1:
                dup.append((key, n, k))
    print('CHECK 3  duplicate integers inside a section : %d' % len(dup))
    for key, n, k in dup[:40]:
        print('    %s  integer %d appears %d times' % ('%s.%d' % key, n, k))
    return 0


if __name__ == '__main__':
    sys.exit(main())
