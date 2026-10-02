#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Render the right-margin equation-number band of original-book pages.

Layout:
  row  (default) -- one column per page, side by side:  compact, easy to read
  col            -- one row per page, stacked (older behaviour)

The band x in [x0,x1] contains only the flush-right "(n)" tags, so a whole section's
printed numbering can be read off with no OCR involved.

Usage: python tools/render_orig_strip.py <idx_from> <idx_to> <out.png>
              [--layout row|col] [--scale 3] [--band 335 400]
"""
import sys

import pymupdf
from PIL import Image, ImageDraw, ImageFont

ORIG = r'F:\大学\数字资源\数学\分析学\泛函分析\吉田耕作\functional analysis Yosida.pdf'
FOLIO_OFFSET = 16


def font():
    for p in (r'C:\Windows\Fonts\arialbd.ttf', r'C:\Windows\Fonts\arial.ttf'):
        try:
            return ImageFont.truetype(p, 22)
        except Exception:
            pass
    return ImageFont.load_default()


def main():
    if len(sys.argv) < 4:
        print(__doc__)
        return 1
    a, b, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    scale = 3.0
    layout = 'row'
    x0, x1 = 335, 400
    if '--scale' in sys.argv:
        scale = float(sys.argv[sys.argv.index('--scale') + 1])
    if '--layout' in sys.argv:
        layout = sys.argv[sys.argv.index('--layout') + 1]
    if '--band' in sys.argv:
        i = sys.argv.index('--band')
        x0, x1 = float(sys.argv[i + 1]), float(sys.argv[i + 2])

    d = pymupdf.open(ORIG)
    tiles = []
    for i in range(a, b + 1):
        pg = d[i]
        clip = pymupdf.Rect(x0, 40, x1, pg.rect.height - 40)
        pm = pg.get_pixmap(matrix=pymupdf.Matrix(scale, scale), clip=clip)
        tiles.append((i - FOLIO_OFFSET, Image.frombytes('RGB', (pm.width, pm.height), pm.samples)))

    f = font()
    if layout == 'row':
        w = sum(t[1].width + 14 for t in tiles) + 20
        h = max(t[1].height for t in tiles) + 42
        cv = Image.new('RGB', (w, h), 'white')
        dr = ImageDraw.Draw(cv)
        x = 12
        for folio, img in tiles:
            dr.text((x, 8), 'p%d' % folio, fill=(180, 0, 0), font=f)
            dr.line([(x - 4, 36), (x - 4, h)], fill=(215, 215, 215), width=2)
            cv.paste(img, (x, 40))
            x += img.width + 14
    else:
        w = max(t[1].width for t in tiles) + 80
        h = sum(t[1].height + 20 for t in tiles) + 20
        cv = Image.new('RGB', (w, h), 'white')
        dr = ImageDraw.Draw(cv)
        y = 12
        for folio, img in tiles:
            dr.text((8, y + 4), 'p%d' % folio, fill=(180, 0, 0), font=f)
            cv.paste(img, (78, y))
            y += img.height + 20
    cv.save(out)
    print('saved %s  %dx%d  (%d pages, %s layout)'
          % (out, cv.width, cv.height, len(tiles), layout))
    return 0


if __name__ == '__main__':
    sys.exit(main())
