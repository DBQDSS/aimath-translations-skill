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
import re, os, sys, shutil, datetime

PAT = re.compile(r'(\\text\{[^}]*?) - ([^}]*?\})')


def main():
    chapters = 'chapters'
    apply_ = '--apply' in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if args:
        chapters = args[0]
    root = os.path.dirname(os.path.abspath(chapters))
    bk = os.path.join(root, 'archive', 'chapters_backup',
                      datetime.date.today().isoformat() + '_before_hyphen_fix')

    total = 0
    for name in sorted(os.listdir(chapters)):
        if not name.endswith('.tex'):
            continue
        path = os.path.join(chapters, name)
        raw = open(path, 'rb').read()
        if b' - ' not in raw:
            continue
        assert raw.count(b'\n') - raw.count(b'\r\n') == 0, '%s is not pure CRLF' % name
        text = raw.decode('utf-8')
        new, n = PAT.subn(r'\1-\2', text)
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
