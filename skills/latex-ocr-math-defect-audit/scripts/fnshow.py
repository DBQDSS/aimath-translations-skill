#!/usr/bin/env python3
"""Print complete footnotes selected by source file and start line.

Usage: python fnshow.py <file.tex> <line> [line ...]
"""
import argparse
from pathlib import Path
from fndump import find_footnotes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('file', type=Path)
    parser.add_argument('lines', nargs='+', type=int)
    args = parser.parse_args()
    notes = dict(find_footnotes(args.file.read_text(encoding='utf-8')))
    missing = False
    for line in args.lines:
        print('%s:%d' % (args.file, line))
        if line in notes:
            print(notes[line])
        else:
            print('NOT FOUND: use fndump.py to locate the actual start line')
            missing = True
    return int(missing)


if __name__ == '__main__':
    raise SystemExit(main())
