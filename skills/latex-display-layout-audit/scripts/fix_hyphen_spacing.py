#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Close up spaced hyphens inside \\text{...} compound words (OCR artefact).

    \\text{ are of the Hilbert - Schmidt type }   ->   \\text{ are of the Hilbert-Schmidt type }

ALWAYS verify the closed form against the original book PDF first, e.g.
    sum(pdf[i].get_text().count('Hilbert-Schmidt') for i in range(pdf.page_count))  # > 0
    sum(pdf[i].get_text().count('Hilbert - Schmidt') ...)                           # == 0

Usage:
    python fix_hyphen_spacing.py [chapters_dir] [--apply]
Without --apply it is a dry run.  Backs up every touched file to
    <chapters_dir>/../archive/chapters_backup/<date>_before_hyphen_fix/
and preserves CRLF exactly.
"""
import re, os, sys, shutil, datetime, argparse

PAT = re.compile(r'(\\text\{[^}]*?) - ([^}]*?\})')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('chapters', nargs='?', default='chapters')
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--term', action='append', default=[], help='Exact spaced term verified in the source PDF, e.g. Hilbert - Schmidt')
    args = parser.parse_args()
    chapters, apply_ = args.chapters, args.apply
    if apply_ and not args.term:
        parser.error('--apply requires at least one source-verified --term')
    root = os.path.dirname(os.path.abspath(chapters))
    bk = os.path.join(root, 'archive', 'chapters_backup',
                      datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '_before_hyphen_fix')

    total = 0
    for name in sorted(os.listdir(chapters)):
        if not name.endswith('.tex'):
            continue
        path = os.path.join(chapters, name)
        raw = open(path, 'rb').read()
        if b' - ' not in raw:
            continue
        text = raw.decode('utf-8')
        n = 0
        protected = re.compile(r'(?<!\\)%[^\r\n]*|\\begin\{(?P<env>verbatim|Verbatim|lstlisting|minted|algorithm|algorithmic)\}.*?\\end\{(?P=env)\}', re.S)
        spans = [match.span() for match in protected.finditer(text)]
        new = text
        for match in reversed(list(PAT.finditer(text))):
            if any(start <= match.start() < end for start, end in spans):
                continue
            # Apply exact verified phrases only: never close a subtraction.
            if apply_ and not any(term in match.group(0) for term in args.term):
                continue
            candidate = match.group(0)
            replacement = candidate
            if apply_:
                for term in args.term:
                    replacement = replacement.replace(term, term.replace(' - ', '-'))
            else:
                replacement = match.group(1) + '-' + match.group(2)
            if replacement != candidate:
                n += 1
                new = new[:match.start()] + replacement + new[match.end():]
        if n == 0:
            continue
        for m in PAT.finditer(text):
            print('  %-16s %s' % (name, m.group(0)))
        if apply_:
            os.makedirs(bk, exist_ok=True)
            dst = os.path.join(bk, name)
            if not os.path.exists(dst):
                shutil.copy2(path, dst)
            open(path, 'wb').write(new.encode('utf-8'))
            print('%-16s fixed %d (backup: %s)' % (name, n, bk))
        else:
            print('%-16s would fix %d  [dry run]' % (name, n))
        total += n
    print('TOTAL %d%s' % (total, '' if apply_ else '  (dry run — pass --apply to write)'))


if __name__ == '__main__':
    main()
