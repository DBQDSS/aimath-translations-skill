#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
section_parity.py — per-chapter structural census of a translation, to be compared
against the ORIGINAL book's table of contents.

WHY THIS EXISTS:
    The single most expensive defect found in a full-book translation audit was not
    a mistranslation — it was a WHOLE SECTION that had never been translated at all
    (Chapter VI stopped at §5 while the original has §6 and §7; ~26 printed pages).
    No page-by-page diff notices this: both PDFs look complete, page counts differ
    plausibly, and the translation's *own* cross-references to the missing section
    render as dead numbers because the labels were never defined.
    The cheap, decisive check is: count sections per chapter in the translation and
    compare with the original ToC. Do it FIRST.

Also reports, per section: the number of exercise items and whether an exercise
heading exists — because a section whose exercise block lost its heading (or never
had one) is invisible to both the ToC and the reader.

Usage:
    python section_parity.py <project_dir> [--chapters-dir chapters]
                             [--expect "I=6,II=5,III=8,..."]

`--expect` comes from reading the original ToC; without it the script just prints
the census for you to compare by eye.
"""
import argparse
import glob
import os
import re
import sys

SECTION = re.compile(r'\\section\*?\{')
SUBSECTION = re.compile(r'\\subsection\*?\{')
ANY_HEADING = re.compile(r'\\(?:chapter|section|subsection)\*?\{')
PROB = re.compile(r'\\begin\{(?:prob|problem|exercise)\}')
ADD_TOC = re.compile(r'\\addcontentsline\{toc\}\{(?:section|subsection)\}\{(?:习题|练习|[Ee]xercises?)\}')
HEAD_TEXT = re.compile(r'习题|练习|Exercises?')
PHANTOM = re.compile(r'\\phantomsection')


def title_of(text, m):
    b = text.find('{', m.start())
    depth, j = 0, b
    while j < len(text):
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
    return text[b + 1:j]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('project_dir')
    ap.add_argument('--chapters-dir', default='chapters')
    ap.add_argument('--tex-glob', default='ch*.tex')
    ap.add_argument('--expect', default='')
    a = ap.parse_args()

    root = os.path.abspath(a.project_dir)
    files = sorted(glob.glob(os.path.join(root, a.chapters_dir, a.tex_glob)))
    if not files:
        sys.exit('no chapter .tex found')

    expect = {}
    for part in filter(None, a.expect.split(',')):
        k, _, v = part.partition('=')
        expect[k.strip()] = int(v)

    grand = {'sec': 0, 'subsec': 0, 'ex_blocks': 0, 'probs': 0, 'headingless': 0}
    problems = []
    print('%-46s %4s %5s %5s %6s %7s' %
          ('file', 'sec', 'sub', 'ExBlk', 'probs', 'noHead'))
    print('-' * 82)

    for f in files:
        text = open(f, encoding='utf-8', errors='replace').read()
        name = os.path.basename(f)
        # split the file at every real \section, keep the title for reporting
        marks = []
        for m in SECTION.finditer(text):
            if text[m.start():m.start() + 9] == '\\section*':
                continue                        # starred = unnumbered, not a section
            marks.append((m.start(), title_of(text, m)))
        marks.append((len(text), None))

        n_sub = n_blk = n_prob = n_headless = 0
        for i in range(len(marks) - 1):
            s, title = marks[i]
            body = text[s:marks[i + 1][0]]
            n_sub += len([1 for m in SUBSECTION.finditer(body)])
            probs = len(PROB.findall(body))
            n_prob += probs
            if probs == 0:
                continue
            has_head = bool(ADD_TOC.search(body)) or bool(HEAD_TEXT.search(
                ''.join(m.group(0) for m in ANY_HEADING.finditer(body))))
            n_blk += 1
            if not has_head:
                n_headless += 1
                problems.append('%s  §"%s"  has %d exercise(s) but NO exercise heading'
                                % (name, (title or '?')[:34], probs))
            elif not PHANTOM.search(body):
                problems.append('%s  §"%s"  exercise heading without \\phantomsection '
                                '(bookmark/TOC anchor will be wrong)'
                                % (name, (title or '?')[:34]))

        key = re.search(r'ch(\d+)', name)
        key = key.group(1) if key else '?'
        flag = ''
        if key in expect:
            flag = '  expect=%d %s' % (expect[key],
                                       'OK' if expect[key] == len(marks) - 1 else '<<< MISMATCH')
        print('%-46s %4d %5d %5d %6d %7d%s' %
              (name[:46], len(marks) - 1, n_sub, n_blk, n_prob, n_headless, flag))
        grand['sec'] += len(marks) - 1
        grand['subsec'] += n_sub
        grand['ex_blocks'] += n_blk
        grand['probs'] += n_prob
        grand['headingless'] += n_headless

    print('-' * 82)
    print('%-46s %4d %5d %5d %6d %7d' % ('TOTAL', grand['sec'], grand['subsec'],
                                         grand['ex_blocks'], grand['probs'],
                                         grand['headingless']))

    if problems:
        print('\n!! %d structural problem(s):' % len(problems))
        for p in problems:
            print('   ' + p)
    else:
        print('\nno structural problem found.')


if __name__ == '__main__':
    main()
