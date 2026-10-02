#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verify flagged (chapter.section) numbering against the ORIGINAL book, section-bounded.

For each flagged section we print our rendered sequence (from main.aux) next to the
original book's extracted tag sequence for exactly that section (bounded by the next
section's heading).

Usage: python tools/verify_sections.py [CH.SEC ...]
"""
import glob
import re
import sys

import pymupdf

import compare_eq_numbers as C

FO = chr(92)
FOLIO_OFFSET = 16
DEFAULT_KEYS = ['III.8', 'VII.4', 'VIII.5', 'VIII.7', 'IX.7', 'XI.0',
                'XI.10', 'XIII.2', 'XIII.7', 'XIV.0', 'XIV.4', 'XIV.7']


def latex_cmd(name):
    return re.escape(FO + name)


def norm(s):
    return re.sub(r'[^a-z0-9]+', '', s.lower())


def plain(s):
    s = re.sub(FO + FO + r'[a-zA-Z]+\s*', ' ', s)
    s = re.sub(r'[{}$^_\\]', ' ', s)
    s = s.replace('*', '')
    return re.sub(r'\s+', ' ', s).strip()


def aux_map():
    out = {}
    for line in open('main.aux', encoding='utf-8'):
        m = re.match(r'\\newlabel\{(eq:[^}]*)\}\{\{([^}]*)\}\{(\d+)\}', line.strip())
        if m:
            out[m.group(1)] = (m.group(2), int(m.group(3)))
    return out


def find_file(ch):
    for p in sorted(glob.glob('chapters/chap*.tex')):
        if 'eq:' + ch + '.' in open(p, encoding='utf-8').read():
            return p
    return None


def headings(path):
    """{section_int_or_0: title}, in source order."""
    txt = open(path, encoding='utf-8').read()
    out = {}
    for m in re.finditer(latex_cmd('yossection') + r'(?:\[[^\]]*\])?\s*\{(\d+)\}\{(.*?)\}',
                         txt, re.S):
        out[int(m.group(1))] = m.group(2)
    return out


def main():
    keys = sys.argv[1:] or DEFAULT_KEYS
    A = aux_map()
    od = pymupdf.open(C.ORIG)
    pages_txt = [norm(od[i].get_text()) for i in range(od.page_count)]

    def first_hit(title, frm=20):
        t = norm(plain(title))
        if not t:
            return None
        for i in range(frm, od.page_count):
            if t in pages_txt[i]:
                return i
        return None

    for key in keys:
        ch, sec = key.split('.')
        path = find_file(ch)
        print('=' * 74)
        if not path:
            print('%s   (no source file)' % key)
            continue
        HS = headings(path)
        chap = re.search(latex_cmd('yoschapter') + r'\s*\{' + ch + r'\}\{(.*?)\}', 
                         open(path, encoding='utf-8').read())
        cur_title = HS.get(int(sec)) if sec.isdigit() and int(sec) > 0 else chap.group(1)
        nxt = None
        if sec.isdigit():
            cands = sorted(k for k in HS if k > int(sec))
            if cands:
                nxt = HS[cands[0]]
        print('%s   file=%s   "%s"' % (key, path, plain(cur_title or '?')[:58]))
        if nxt:
            print('   next section: "%s"' % plain(nxt)[:58])

        start = first_hit(cur_title)
        end = first_hit(nxt) if nxt else None
        if end is None:
            end = (start + 5) if start is not None else None
        if start is None:
            print('   !! section start not found in original')
            continue
        print('   orig pages: idx %d..%d   (folio %d..%d)'
              % (start, end - 1, start - FOLIO_OFFSET, end - 1 - FOLIO_OFFSET))

        src = open(path, encoding='utf-8').read()
        names = ['eq:' + key + '.' + n for n in
                 re.findall(re.escape('label{eq:' + key + '.') + r'([^}]*)\}', src)]
        ours = [(n.split('.')[-1], A.get(n, ('?', -1))[0]) for n in names]

        rows = C.extract(C.ORIG, C.ORIG_XMIN, list(range(start, end)))
        bypage = {}
        for r in rows:
            bypage.setdefault(r['page'], []).append(r['num'])
        ostr = ' | '.join('f%d:%s' % (p - 1 - FOLIO_OFFSET, ','.join(bypage[p]))
                          for p in sorted(bypage))
        print('   OURS n=%-3d %s' % (len(ours), ' '.join('%s=%s' % o for o in ours)))
        print('   ORIG n=%-3d %s' % (len(rows), ostr))
        print('   -> OURS %d vs ORIG %d   delta %+d'
              % (len(ours), len(rows), len(ours) - len(rows)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
