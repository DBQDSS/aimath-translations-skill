# -*- coding: utf-8 -*-
"""AJbook / book-class variant: convert BARE printed-number references into clickable
cross-references, and add anchors where no label exists.

This is the companion of ``convert_hardrefs.py`` for book classes whose theorem-like
environments (theorem/prop/lem/cor/def/rem/ex) share ONE counter printed as
"section.item" (e.g. \\counterwithin{theorem}{section}) and whose labels are named
``<type>:<chap_prefix><sec>.<item>`` (e.g. prop:ii.1.39, thm:iv.4.1, exc:v.5.11).
It carries NO project-specific data: you supply BASE / FILES / CHAP_OF / HAND / EXACT.

What it converts (in this order, most specific first):
  1. EXACT matches        — cross-chapter refs ("II, \\S 1"), page refs ("(p. 3)"),
                            anchors (\\phantomsection\\label / \\hypertarget), etc.
  2. MULTI  "(1.17, 1.22)" — several numbers in one parenthesis.
  3. JIANP  "(见 3.25)"    — "见/参见/参看 N.M" inside parens.
  4. JIANB  "见 3.25"      — same without parens.
  5. SINGLE "(2.3)", "(1.2e)" — the common case.

Resolution order for a bare number N in file F:
  a. an existing \\label in main.aux whose printed number == N in F's chapter -> \\ref{...};
  b. else a hand-typeset (unlabeled) item listed in HAND                -> \\hyperlink{item:...}{N};
  c. else leave untouched and record it in the UNRESOLVED list.

Mapping is DERIVED FROM main.aux (never hand-maintained), so printed numbers and labels
can never drift. Dry-run by default; pass --go to write files.
"""
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

# ---- configure per project -------------------------------------------------
BASE = r'.'                                    # working directory (cwd by default)
FILES = ['main.tex']                           # files to process
# chapter prefix -> Roman label used in section labels is not needed here; we only
# need, per FILE, which chapter's number-space it uses:
CHAP_OF = {'main.tex': 'i'}                    # e.g. {'chII.tex': 'ii', ...}
# Hand-typeset numbered items that have NO \label (so they are absent from main.aux).
# They must already carry \phantomsection\hypertarget{item:...}{} in the source.
HAND = {                                       # file -> {printed_number: target_name}
    # 'chII.tex': {'1.6': 'item:ii.1.6', ...},
}
# Explicit one-off replacements. Each item: (old_string, new_string, expected_count).
# used for cross-chapter refs, page refs, and *inserting* anchors.
EXACT = {
    # 'intro.tex': [
    #   ('(p. 3)', '(本书 p.\\pageref{pg:orig3})', 1),
    #   ('\\phantomsection\\label{pg:orig3}对一个数域', '...', 1),
    # ],
}
# ---------------------------------------------------------------------------

NUM = r'(?:[A-C]\.\d{1,3}|\d{1,2}\.\d{1,3})'
SINGLE = re.compile(r'\(\s*(' + NUM + r')([a-z]?)\s*\)')
MULTI = re.compile(r'\(\s*(' + NUM + r'[a-z]?(?:\s*,\s*' + NUM + r'[a-z]?)+)\s*\)')
JIANP = re.compile(r'\(\s*(见|参见|参看)\s*(' + NUM + r')([a-z]?)\s*\)')
JIANB = re.compile(r'(?<![\\(（])(见|参见|参看)\s*(' + NUM + r')([a-z]?)')


def build_by_chap(aux_text):
    """label -> chapter/item, keyed by chapter prefix taken from the label itself."""
    by_chap = {}
    for lab, num, page in re.findall(
            r'\\newlabel\{([^}]+)\}\{\{([^}]*)\}\{([^}]*)\}', aux_text):
        if lab.endswith('@cref'):
            continue
        m = re.match(r'^([A-Za-z]+):(.+)$', lab)
        if not m:
            continue
        rest = m.group(2)
        pm = re.match(r'^(viii|vii|vi|v|iv|iii|ii)\.(.+)$', rest)
        ch, item = (pm.group(1), pm.group(2)) if pm else ('i', rest)
        by_chap.setdefault(ch, {})[item] = lab
    return by_chap


def main():
    go = '--go' in sys.argv
    by_chap = build_by_chap(open(BASE + '/main.aux', encoding='utf-8', errors='replace').read())

    def resolve(fn, n, suf=''):
        lab = by_chap.get(CHAP_OF[fn], {}).get(n)
        if lab:
            return '\\ref{%s}%s' % (lab, suf)
        h = HAND.get(fn, {}).get(n)
        if h:
            return '\\hyperlink{%s}{%s}%s' % (h, n, suf)
        return None

    changelog, unresolved, report = [], [], []

    def single(fn, m):
        r = resolve(fn, m.group(1), m.group(2))
        if r is None:
            unresolved.append((fn, m.group(0)))
            return m.group(0)
        changelog.append((fn, 'single', m.group(0), '(' + r + ')'))
        return '(' + r + ')'

    def multi(fn, m):
        parts = [p.strip() for p in m.group(1).split(',')]
        out = []
        for p in parts:
            mm = re.match(r'^(' + NUM + r')([a-z]?)$', p)
            if not mm:
                return m.group(0)
            r = resolve(fn, mm.group(1), mm.group(2))
            if r is None:
                return m.group(0)
            out.append(r)
        res = '(' + ', '.join(out) + ')'
        changelog.append((fn, 'multi', m.group(0), res))
        return res

    def jian(fn, m, parens):
        r = resolve(fn, m.group(2), m.group(3))
        if r is None:
            return m.group(0)
        res = '(' + m.group(1) + ' ' + r + ')' if parens else m.group(1) + ' ' + r
        changelog.append((fn, 'jian', m.group(0), res))
        return res

    out_files = {}
    for fn in FILES:
        text = open(BASE + '/' + fn, encoding='utf-8', newline='').read()
        for old, new, cnt in EXACT.get(fn, []):
            c = text.count(old)
            if c != cnt:
                report.append('!! %s EXACT count %d (want %d): %r' % (fn, c, cnt, old))
            else:
                changelog.append((fn, 'exact', old, new))
            text = text.replace(old, new)
        text = MULTI.sub(lambda m: multi(fn, m), text)
        text = JIANP.sub(lambda m: jian(fn, m, True), text)
        text = JIANB.sub(lambda m: jian(fn, m, False), text)
        text = SINGLE.sub(lambda m: single(fn, m), text)
        out_files[fn] = text

    lines = list(report) + ['===== CHANGES =====']
    cur = None
    for fn, kind, old, new in changelog:
        if fn != cur:
            lines.append('\n---- %s ----' % fn)
            cur = fn
        lines.append('  [%s] %r -> %r' % (kind, old, new))
    lines.append('\n===== UNRESOLVED (left untouched) =====')
    lines += ['  %s %r' % (fn, s) for fn, s in unresolved]
    print('\n'.join(lines))
    print('\nchanges:', len(changelog), ' unresolved:', len(unresolved), ' warnings:', len(report))

    if go:
        for fn in FILES:
            open(BASE + '/' + fn, 'w', encoding='utf-8', newline='').write(out_files[fn])
        print('*** WROTE', len(FILES), 'files ***')
    else:
        print('(dry run; pass --go to write)')


if __name__ == '__main__':
    main()
