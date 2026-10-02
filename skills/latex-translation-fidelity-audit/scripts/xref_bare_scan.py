#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
xref_bare_scan.py — find (and optionally hyperlink) cross-chapter references that
were typed as PLAIN TEXT instead of \ref.

WHY THIS EXISTS:
    A hand-made translation routinely writes things like
        \\S V.3      §VI.7.2     习题~VI.6.5     [VI.6.16]
        定义~VI.6.12    定理~6.11     [8.8, 9.1, III.1.4, VI.6.16]
    The compiled PDF looks perfect — the numbers are right — but they are dead
    text: no hyperlink, and they do not follow renumbering. On a 600-page book
    this is typically 50-100 spots, and per-exercise hint blocks ("[§2.4.3, 4.15
    4.16, §IV.6.3]") are the densest source. Nothing in a normal build log flags it.

    This script resolves each bare number against `_auxmap.json` (built by
    aux_number_map.py from the PRINTED numbers — see that script's docstring) and
    rewrites it as \ref.

Usage:
    python aux_number_map.py <project_dir>          # first: build the map
    python xref_bare_scan.py <project_dir> report   # default: dry run, prints a table
    python xref_bare_scan.py <project_dir> apply    # rewrite in place (CRLF preserved)

Resolution order for a bare  ROMAN.sec.item :
    * written with § / \\S          -> subsection, else section
    * preceded by 习题/Exercise(s)  -> exercise
    * preceded by 定义/定理/...      -> theorem-like
    * inside a [...] hint block     -> exercise        (book convention)
    * near an existing \\ref{ex:...} -> exercise
    * otherwise                     -> subsection, theorem, exercise (first hit)
Anything that still does not resolve is printed as  ??未解析  — do NOT paper over
it; it usually means (a) a whole section is missing from the translation, or
(b) the number is not a reference at all (e.g. an equation number, "5.4" as data).
"""
import argparse
import glob
import json
import os
import re
import sys

NUM = r'(?:XIII|XIV|XV|VIII|III|XII|VII|IX|XI|VI|IV|V|II|X|I)'
PAT = re.compile(r'(?P<pre>§\s*|\\S~?\s*)?'
                 r'(?P<num>(?<![A-Za-z0-9.\\.])' + NUM + r'\.\d+(?:\.\d+)?)')

# never touch these: their braces contain labels/keys, not prose
MASK = re.compile(r'\\(?:index|label|ref|cref|Cref|eqref|cite|citeauthor|citeyear'
                  r'|pageref|hyperref|bibitem)\b\*?(?:\[[^\]]*\])?\{')

MARK_EX = re.compile(r'(?:习题|练习|题目|题|Exercise|Exercises|Prob\.?|Problem)\s*~?\s*$')
MARK_THM = re.compile(r'(?:定义|定理|命题|引理|推论|例|注记|断言|玩笑'
                      r'|Definition|Theorem|Proposition|Lemma|Corollary|'
                      r'Remark|Example|Claim|Notation)\s*~?\s*$')
NEAR_EX = re.compile(r'(?:习题|练习|Exercises?)\s*~?|\\ref\{[a-z]*ex:')


def mask_regions(text):
    n = len(text)
    m = [False] * n
    for mm in MASK.finditer(text):
        i = text.find('{', mm.start())
        if i < 0:
            continue
        depth, j = 0, i
        while j < n:
            c = text[j]
            if c == '\\':
                j += 2
                continue
            if c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    break
            j += 1
        for k in range(mm.start(), min(j + 1, n)):
            m[k] = True
    return m


def inside_bracket(text, pos):
    ls = text.rfind('\n', 0, pos) + 1
    seg = text[ls:pos]
    lb, rb = seg.rfind('['), seg.rfind(']')
    return lb >= 0 and rb < lb


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('project_dir')
    ap.add_argument('mode', nargs='?', default='report', choices=['report', 'apply'])
    ap.add_argument('--map', default='_auxmap.json')
    ap.add_argument('--tex-glob', default='chapters/ch*.tex')
    a = ap.parse_args()

    root = os.path.abspath(a.project_dir)
    mp = json.load(open(os.path.join(root, a.map), encoding='utf-8'))
    SEC, SUB, THM, PROB = mp['sec'], mp['subsec'], mp['thm'], mp['prob']

    def resolve(num, pre, before, in_br):
        roman, *rest = num.split('.')
        if len(rest) == 1:
            key = '%s.%s' % (roman, rest[0])
            return ('sec', key, SEC[key]) if key in SEC else (None, None, None)
        key = '%s.%s.%s' % (roman, rest[0], rest[1])
        if pre:
            if key in SUB:
                return 'subsec', key, SUB[key]
            if key in SEC:
                return 'sec', key, SEC[key]
            return None, None, None
        if MARK_THM.search(before):
            return ('thm', key, THM[key]) if key in THM else (None, None, None)
        if MARK_EX.search(before):
            return ('prob', key, PROB[key]) if key in PROB else (None, None, None)
        if in_br:
            return ('prob', key, PROB[key]) if key in PROB else (None, None, None)
        if NEAR_EX.search(before[-80:]):
            return ('prob', key, PROB[key]) if key in PROB else (None, None, None)
        for kind, m in (('subsec', SUB), ('thm', THM), ('prob', PROB)):
            if key in m:
                return kind, key, m[key]
        return None, None, None

    report = []
    for f in sorted(glob.glob(os.path.join(root, a.tex_glob))):
        text = open(f, encoding='utf-8').read()
        mask = mask_regions(text)
        for mm in PAT.finditer(text):
            if mask[mm.start('num')]:
                continue
            if re.match(r'\s*~?\s*\\ref', text[mm.end():mm.end() + 16]):
                continue
            pre = mm.group('pre') or ''
            num = mm.group('num')
            before = text[max(0, mm.start() - 30):mm.start()]
            kind, key, lab = resolve(num, pre, before,
                                     inside_bracket(text, mm.start('num')))
            if lab is None:
                new = ''
            elif kind in ('sec', 'subsec'):
                new = r'\ref{' + lab + '}'           # \ref carries the chapter number
            else:
                new = num.split('.')[0] + r'.\ref{' + lab + '}'   # keep literal chapter
            report.append((os.path.relpath(f, root),
                           text[:mm.start()].count('\n') + 1,
                           mm.start('num'), mm.end('num'), num, pre,
                           'OK' if lab else '??UNRESOLVED', kind, lab, new))

    print('=' * 96)
    print('bare cross-chapter references: %d   (mode=%s)' % (len(report), a.mode))
    print('=' * 96)
    bad = 0
    for r in report:
        if r[6] != 'OK':
            bad += 1
        print('[%-13s] %s:%d  %s%s -> %s' % (r[6], r[0], r[1], r[5], r[4], r[9] or '-'))
    print('\nunresolved: %d   (a cluster of them usually means a MISSING SECTION)'
          % bad)

    if a.mode != 'apply':
        return

    by_file = {}
    for r in report:
        if r[6] == 'OK':
            by_file.setdefault(r[0], []).append(r)
    changed = 0
    for fn, items in by_file.items():
        path = os.path.join(root, fn)
        text = open(path, encoding='utf-8').read()
        for r in sorted(items, key=lambda x: -x[2]):
            text = text[:r[2]] + r[9] + text[r[3]:]
            changed += 1
        # keep CRLF (a plain open(...,'w') would flatten it)
        b = text.replace('\r\n', '\n').replace('\r', '\n').replace('\n', '\r\n')
        open(path, 'wb').write(b.encode('utf-8'))
    print('\nrewrote %d reference(s)' % changed)
    for f in sorted(glob.glob(os.path.join(root, a.tex_glob))):
        b = open(f, 'rb').read()
        c = b.count(b'\r\n')
        if b.count(b'\n') - c:
            print('  !! %s: LF-only lines present' % os.path.basename(f))


if __name__ == '__main__':
    main()
