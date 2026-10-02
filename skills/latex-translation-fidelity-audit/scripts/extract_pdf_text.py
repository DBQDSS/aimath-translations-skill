#!/usr/bin/env python3
"""Extract clean text from PDF pages for translation-fidelity spot checks.

Usage:
    python extract_pdf_text.py <pdf> <start_page_1based> <end_page_1based> [out.txt]

Page numbers are 1-based. PyMuPDF's get_text() sometimes emits stray control
bytes that make the Read tool treat the file as binary; we replace any char that
is neither printable, nor whitespace, nor a CJK ideograph with a space. Prints to
stdout when no out.txt is given.
"""
import sys, os, pymupdf

def clean(s):
    out = []
    for ch in s:
        if ch.isprintable() or ch.isspace() or '一' <= ch <= '鿿':
            out.append(ch)
        else:
            out.append(' ')
    return ''.join(out)

def main():
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)
    pdf = sys.argv[1]
    start = int(sys.argv[2]); end = int(sys.argv[3])
    out = sys.argv[4] if len(sys.argv) > 4 else None
    doc = pymupdf.open(pdf)
    chunks = []
    for i in range(start - 1, min(end, doc.page_count)):
        t = clean(doc[i].get_text())
        chunks.append("=== page %d ===\n%s" % (i + 1, t))
    s = "\n".join(chunks)
    if out:
        open(out, "w", encoding="utf-8").write(s)
        print("wrote", out, "(", len(chunks), "pages )")
    else:
        sys.stdout.write(s)

if __name__ == "__main__":
    main()
