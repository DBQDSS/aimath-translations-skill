#!/usr/bin/env python3
"""Print +-window chars around every regex match in a file (verify OCR artifacts).

Usage:
    python show_context.py <file> <regex> [window=120]
"""
import sys, re

def main():
    path = sys.argv[1]; pat = sys.argv[2]
    win = int(sys.argv[3]) if len(sys.argv) > 3 else 120
    txt = open(path, encoding='utf-8', errors='replace').read()
    n = 0
    for m in re.finditer(pat, txt):
        s = max(0, m.start() - win); e = min(len(txt), m.end() + win)
        print("..." + txt[s:e].replace("\n", " ") + "...")
        print("-" * 80)
        n += 1
    print("matches:", n)

if __name__ == "__main__":
    main()
