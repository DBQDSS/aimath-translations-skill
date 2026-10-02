#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
aux_number_map.py — build the AUTHORITATIVE "printed number -> label" map from
the per-chapter .aux files, then dump it to `_auxmap.json`.

WHY THIS EXISTS (the trap that cost a whole afternoon):
    hyperref's anchor for a theorem in chapter VI is  `theorem.6.4` — the 6 is the
    CHAPTER number. The number PRINTED in the book is `7.4` — the counter is reset
    per SECTION. Any map built from the anchor (field 4 of \newlabel, or the
    `<label>@cref` entry) is therefore WRONG, and it looks right only while
    chapter == section (e.g. §VI.6, where section 6 == chapter 6). It silently
    breaks everywhere else.
    => Always take the printed number from FIELD 1 of \newlabel, never the anchor.

Usage:
    python aux_number_map.py <project_dir> [--out _auxmap.json]
                             [--exercise-counters probctr,exercise]
                             [--theorem-counters theorem,claim,joke,...]

Output JSON keys:  sec / subsec / thm / prob
    'VI.7'    -> label   (printed '6.7')
    'VI.7.2'  -> label   (printed '6.7.2')
    'VI.6.12' -> label   (printed '6.12',  anchor starts with a theorem counter)
    'VI.7.11' -> label   (printed '7.11',  anchor starts with the exercise counter)
"""
import argparse
import collections
import glob
import json
import os
import re
import sys

DEFAULT_EX = ['probctr', 'exercise', 'exercises', 'prob']
DEFAULT_THM = ['theorem', 'claim', 'joke', 'lemma', 'proposition', 'definition',
               'corollary', 'remark', 'example', 'notation', 'conjecture']
# anchors that are legitimately never referenced by "VI.sec.item" prose — expected,
# not a configuration error, so they are not reported as unclassified.
DEFAULT_IGNORE = ['chapter', 'figure', 'table', 'equation', 'AMS', 'subsubsection*',
                  'Item', 'footnote', 'lstlisting', 'algorithm']

ROMAN = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X',
         'XI', 'XII', 'XIII', 'XIV', 'XV']


def grab_group(text, i):
    """text[i] == '{' -> (inner, index_after_matching_brace), brace-balanced and
    backslash-aware (a \\{ does not open a group)."""
    assert text[i] == '{'
    depth = 0
    j = i
    while j < len(text):
        c = text[j]
        if c == '\\':
            j += 2
            continue
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                return text[i + 1:j], j + 1
        j += 1
    return None, j


def split_groups(inner):
    """Split the body of a \\newlabel second argument into its top-level groups.
    Needed because field 3 may itself contain \\texorpdfstring{a}{b}."""
    out, i = [], 0
    while i < len(inner):
        if inner[i] == '{':
            content, i = grab_group(inner, i)
            if content is None:
                break
            if content.startswith('{'):
                out.extend(split_groups(content))
            else:
                out.append(content)
        else:
            i += 1
    return out


def chapter_roman(fname, override=None):
    """chapters/ch6-foo.tex -> 'VI'  (override: dict {'6': 'VI'})"""
    m = re.search(r'ch(?:apter)?[_-]?(\d+)', os.path.basename(fname))
    if not m:
        return None
    n = int(m.group(1))
    if override and m.group(1) in override:
        return override[m.group(1)]
    return ROMAN[n - 1] if 1 <= n <= len(ROMAN) else 'CH%d' % n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('project_dir')
    ap.add_argument('--out', default='_auxmap.json')
    ap.add_argument('--aux-glob', default='chapters/*.aux')
    ap.add_argument('--exercise-counters', default=','.join(DEFAULT_EX))
    ap.add_argument('--theorem-counters', default=','.join(DEFAULT_THM))
    ap.add_argument('--ignore-counters', default=','.join(DEFAULT_IGNORE))
    a = ap.parse_args()

    root = os.path.abspath(a.project_dir)
    ex_ctr = set(x.strip() for x in a.exercise_counters.split(',') if x.strip())
    thm_ctr = set(x.strip() for x in a.theorem_counters.split(',') if x.strip())
    ign_ctr = set(x.strip() for x in a.ignore_counters.split(',') if x.strip())

    sec, subsec, thm, prob = {}, {}, {}, {}
    kinds = collections.Counter()
    unknown = collections.Counter()

    files = sorted(glob.glob(os.path.join(root, a.aux_glob)))
    if not files:
        sys.exit('no .aux files matched %s under %s' % (a.aux_glob, root))

    for f in files:
        ch = chapter_roman(f)
        if ch is None:
            continue
        text = open(f, encoding='utf-8', errors='replace').read()
        for mm in re.finditer(r'\\newlabel\{([^}]*)\}\{', text):
            key = mm.group(1)
            if key.endswith('@cref'):
                continue
            inner, _ = grab_group(text, mm.end() - 1)
            if inner is None:
                continue
            fields = split_groups(inner)
            if len(fields) < 4:
                continue
            num, anchor = fields[0].strip(), fields[3]
            ctr = anchor.split('.')[0]
            kinds[ctr] += 1
            nums = num.split('.')
            if ctr == 'section' and len(nums) == 2:
                sec['%s.%s' % (ch, nums[1])] = key
            elif ctr == 'subsection' and len(nums) == 3:
                subsec['%s.%s.%s' % (ch, nums[1], nums[2])] = key
            elif ctr in ex_ctr and len(nums) == 2:
                prob['%s.%s.%s' % (ch, nums[0], nums[1])] = key
            elif ctr in thm_ctr and len(nums) == 2:
                thm['%s.%s.%s' % (ch, nums[0], nums[1])] = key
            elif ctr not in ign_ctr:
                unknown[ctr] += 1

    out = os.path.join(root, a.out)
    json.dump({'sec': sec, 'subsec': subsec, 'thm': thm, 'prob': prob},
              open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    print('anchor kinds : %s' % dict(kinds))
    if unknown:
        print('!! UNCLASSIFIED counters (their entries were DROPPED): %s' % dict(unknown))
        print('   -> re-run with --theorem-counters / --exercise-counters extended.')
    print('sections     %d' % len(sec))
    print('subsections  %d' % len(subsec))
    print('theorem-like %d' % len(thm))
    print('exercises    %d' % len(prob))
    print('written      %s' % out)


if __name__ == '__main__':
    main()
