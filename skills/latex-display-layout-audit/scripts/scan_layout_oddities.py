#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Scan chapters/*.tex for display-math layout oddities.

Usage:
    python scan_layout_oddities.py [chapters_dir]
    (default: ./chapters relative to cwd)

Reports:
 (A) display env nested inside another display env   <-- most reliable "fake alignment" detector
 (B) numbered env (align/gather/multline/...) where EVERY top-level row is \\notag
     <-- usually legitimate unnumbered multi-line derivations; SPOT CHECK, do not batch-fix
"""
import re, sys, glob, os

ENVS = ['align','align*','aligned','alignat','alignat*','gather','gather*','gathered',
        'multline','multline*','eqnarray','eqnarray*','split','yoslines',
        'flalign','flalign*','displaylines']
NUMBERED = {'align','gather','multline','flalign','alignat','eqnarray'}


def scan_file(path):
    src = open(path, encoding='utf-8').read()
    toks = sorted(
        [(m.start(), m.group(1)) for m in re.finditer(r'\\begin\{(%s)\}' % '|'.join(map(re.escape, ENVS)), src)]
        + [(m.start(), m.group(1)) for m in re.finditer(r'\\end\{(%s)\}' % '|'.join(map(re.escape, ENVS)), src)],
        key=lambda t: t[0])
    stack, records = [], []
    for pos, name in toks:
        if src[pos:pos + 6] == '\\begin':
            stack.append((name, pos))
        else:
            if not stack:
                continue
            nm, bp = stack.pop()
            if nm != name:
                continue
            bs = bp + len('\\begin{%s}' % nm)
            records.append(dict(env=nm, begin=bp, body_start=bs, body_end=pos,
                                outer=[s[0] for s in stack]))
    return src, records


def top_level_rows(body):
    rows, depth, cur, i = [], 0, [], 0
    while i < len(body):
        c = body[i]
        if c == '\\' and i + 1 < len(body):
            if body[i + 1] == '\\' and depth == 0:
                rows.append(''.join(cur)); cur = []; i += 2; continue
            cur.append(body[i:i + 2]); i += 2; continue
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
        cur.append(c); i += 1
    rows.append(''.join(cur))
    return rows


def main(chapters_dir):
    nested, unnumbered = [], []
    for path in sorted(glob.glob(os.path.join(chapters_dir, '*.tex'))):
        base = os.path.basename(path)
        src, recs = scan_file(path)

        def lineno(p):
            return src.count('\n', 0, p) + 1

        for r in recs:
            if r['outer']:
                nested.append((base, lineno(r['begin']), r['env'], r['outer'][-1]))
            if r['env'] in NUMBERED:
                body = src[r['body_start']:r['body_end']]
                rows = [x for x in top_level_rows(body) if x.strip()]
                if len(rows) >= 2 and all('\\notag' in x or '\\nonumber' in x for x in rows):
                    unnumbered.append((base, lineno(r['begin']), r['env'], len(rows)))

    print('=== (A) NESTED display envs (%d) ===' % len(nested))
    for b, l, e, o in nested:
        print('  %-16s L%-6d %-12s  inside  %s' % (b, l, e, o))
    print()
    print('=== (B) numbered env with ALL rows \\notag (%d)  [spot-check only] ===' % len(unnumbered))
    for b, l, e, n in unnumbered:
        print('  %-16s L%-6d %-12s  rows=%d' % (b, l, e, n))


if __name__ == '__main__':
    d = sys.argv[1] if len(sys.argv) > 1 else 'chapters'
    main(d)
