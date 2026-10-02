#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Locate text in the ORIGINAL Yosida book by fuzzy phrase search over its OCR layer.

Usage:  python tools/find_orig_page.py "Cayley transform" ["another phrase" ...]
Prints candidate page indices (0-based), printed folio, and the OCR snippet.
"""
import re
import sys

import pymupdf

ORIG = r'F:\大学\数字资源\数学\分析学\泛函分析\吉田耕作\functional analysis Yosida.pdf'
FOLIO_OFFSET = 16          # page_index 322 -> printed folio 306


def norm(s):
    return re.sub(r'[^a-z0-9]+', '', s.lower())


def main():
    d = pymupdf.open(ORIG)
    pages = [norm(d[i].get_text()) for i in range(d.page_count)]
    for phrase in sys.argv[1:]:
        n = norm(phrase)
        print('=' * 70)
        print('PHRASE: %r   (normalised len=%d)' % (phrase, len(n)))
        hits = []
        for i, t in enumerate(pages):
            k = t.find(n)
            if k >= 0:
                raw = d[i].get_text()
                # recover a readable snippet from the raw text
                pos = max(0, raw.lower().find(phrase.split()[0].lower()))
                snip = re.sub(r'\s+', ' ', raw[pos:pos + 110])
                hits.append((i, snip))
        if not hits:
            print('  no match')
        for i, snip in hits[:8]:
            print('  idx=%-4d folio=%-4d  %s' % (i, i - FOLIO_OFFSET, snip))
    return 0


if __name__ == '__main__':
    sys.exit(main())
