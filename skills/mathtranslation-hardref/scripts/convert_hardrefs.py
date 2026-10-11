#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Convert hard-coded theorem/equation references to clickable \\ref/\\eqref.

Safe mapping rule: a reference is converted only when a UNIQUE label matches on
(1) same file scope (the appended paper partgf1+partgf2 is one continuous scope),
(2) exact printed number (read from main.aux), (3) matching environment type.

Counter model (mathtranslation.cls): theorem-like envs share one counter displayed
as "subsection.theorem"; the counter RESETS per subsection; counters CARRY across
\\input files, so simulate the full chapter chain in main.tex order. Equations are
globally sequential in the main book and reset+continuous across the appended paper.

Dry-run by default; use --apply to rewrite the .tex files in place.
Usage:  python convert_hardrefs.py [--apply]   (run from the translated/ directory)
"""
import re, sys, os, argparse, glob
from collections import defaultdict
from source_guard import mask_protected, read_source, write_source

HERE = os.path.dirname(os.path.abspath(__file__))
# Default to the directory this script is run from; allow override via env if needed.
ROOT = os.environ.get("MT_ROOT", os.getcwd())
AUX = os.path.join(ROOT, "main.aux")
PARTS = []
GF = set()  # Optional, explicitly configured continuous reference scope.

label_num = {}
if os.path.exists(AUX):
    for aux_path in glob.glob(os.path.join(ROOT, '**', '*.aux'), recursive=True):
        txt = read_source(aux_path)
        for m in re.finditer(r"\\newlabel\{([^}]*)\}\{\{([^}]*)\}\{", txt):
            key, number = m.group(1), m.group(2).strip()
            if key in label_num and label_num[key] != number:
                label_num[key] = ''  # conflicting aux data is unresolved
            else:
                label_num.setdefault(key, number)

PREFIX_ENV = {"定理": "theorem", "命题": "proposition", "引理": "lemma",
              "推论": "corollary", "定义": "definition", "注": "remark",
              "例": "example", "问题": "problem"}
PREFIX_REFC = {"定理": r"\thmref", "命题": r"\propref", "引理": r"\lemref",
               "推论": r"\corref", "定义": r"\defref", "注": r"\remref",
               "例": r"\exref", "问题": r"\probref"}

RE_THM = re.compile(r"(定理|命题|引理|推论|定义|注|例|问题)\s+(\d+\.\d+)(?![\d.])")
RE_EQ = re.compile(r"(公式|式|方程)\s*\((\d+)\)")
RE_CHAPTER = re.compile(r"章第\s+(\d+\.\d+)(?![\d.])")

def strip_comment(line):
    out = []; i = 0
    while i < len(line):
        c = line[i]
        if c == "\\" and i + 1 < len(line):
            out += [c, line[i+1]]; i += 2; continue
        if c == "%":
            break
        out.append(c); i += 1
    return "".join(out)

def parse_file(path):
    labels = []; stack = []
    if True:
        for lineno, raw in enumerate(mask_protected(read_source(path)).splitlines(), 1):
            line = strip_comment(raw)
            for token in re.finditer(r"\\(begin|end|label)\{([^}]*)\}", line):
                kind, value = token.groups()
                if kind == 'begin':
                    stack.append(value)
                elif kind == 'end':
                    if stack and stack[-1] == value:
                        stack.pop()
                else:
                    env = stack[-1] if stack else None
                    labels.append((value, env, label_num.get(value, ""), lineno))
    return labels

def build_indexes():
    per_file = {}
    gf_thm = defaultdict(list); gf_eq = defaultdict(list)
    mainbook_eq = defaultdict(list)
    for part in PARTS:
        labs = parse_file(os.path.join(ROOT, part))
        per_file[part] = labs
        for (name, env, printed, ln) in labs:
            if not printed:
                continue
            if part in GF:
                (gf_eq if env == "equation" else gf_thm)[printed if env == "equation" else (env, printed)].append(name)
            else:
                if env == "equation":
                    mainbook_eq[printed].append(name)
    return per_file, gf_thm, gf_eq, mainbook_eq

def main():
    global PARTS, GF
    parser = argparse.ArgumentParser(description='Preview source-scoped references using aux printed numbers.')
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--files', default='*.tex', help='Project-relative file glob; review the preview before applying')
    parser.add_argument('--scope-group', default='', help='Comma-separated files sharing one continuous reference scope')
    args = parser.parse_args()
    apply = args.apply
    PARTS = sorted(os.path.relpath(f, ROOT) for f in glob.glob(os.path.join(ROOT, args.files), recursive=True))
    GF = set(filter(None, args.scope_group.split(',')))
    if not PARTS or not label_num:
        parser.error('No source files or aux labels found; build the project and check --files.')
    if not GF <= set(PARTS):
        parser.error('--scope-group contains a file outside --files')
    per_file, gf_thm, gf_eq, mainbook_eq = build_indexes()
    total_conv = 0; total_skip = 0
    prepared = {}
    for part in PARTS:
        in_gf = part in GF
        local_thm = defaultdict(list)
        for (name, env, printed, ln) in per_file[part]:
            if printed and env != "equation":
                local_thm[(env, printed)].append(name)
        source = read_source(os.path.join(ROOT, part))
        raw_lines = source.splitlines(keepends=True)
        clean_lines = mask_protected(source, math=True).splitlines(keepends=True)
        conversions = []; skip = []
        for lineno, raw in enumerate(raw_lines, 1):
            clean = strip_comment(clean_lines[lineno - 1])
            for m in RE_THM.finditer(clean):
                prefix, num = m.group(1), m.group(2)
                env = PREFIX_ENV[prefix]
                cands = (gf_thm if in_gf else local_thm).get((env, num), [])
                cands = [c for c in cands if c]
                if len(cands) == 1:
                    s, e = m.start(), m.end()
                    if raw[s:e] == clean[s:e]:
                        conversions.append((lineno, s, e, prefix + rf"~\ref{{{cands[0]}}}"))
                    else:
                        skip.append((lineno, prefix+num, "pos-mismatch"))
                else:
                    skip.append((lineno, prefix+num, f"{len(cands)} cands"))
            for m in RE_EQ.finditer(clean):
                prefix, num = m.group(1), m.group(2)
                # Numbers often reset per section/file. Never borrow a unique
                # target from a different file without an explicit shared scope.
                local_eq = defaultdict(list)
                for name, env, printed, ln in per_file[part]:
                    if env == 'equation':
                        local_eq[printed].append(name)
                cands = (gf_eq if in_gf else local_eq).get(num, [])
                cands = [c for c in cands if c]
                if len(cands) == 1:
                    s, e = m.start(), m.end()
                    if raw[s:e] == clean[s:e]:
                        conversions.append((lineno, s, e, prefix + rf"~\eqref{{{cands[0]}}}"))
                    else:
                        skip.append((lineno, prefix+"("+num+")", "pos-mismatch"))
                else:
                    skip.append((lineno, prefix+"("+num+")", f"{len(cands)} cands"))
            for m in RE_CHAPTER.finditer(clean):
                skip.append((lineno, "章第"+m.group(1), "chapter-ref(skip)"))
        if not apply:
            if conversions or skip:
                print(f"\n=== {part} ===")
                print(f"  CONVERT ({len(conversions)}):")
                for (ln, s, e, rep) in conversions:
                    print(f"    L{ln}: ...{raw_lines[ln-1][s:e]}... -> {rep}")
                print(f"  SKIP ({len(skip)}):")
                for (ln, tok, why) in skip:
                    print(f"    L{ln}: {tok}  [{why}]")
            total_conv += len(conversions); total_skip += len(skip)
        else:
            if skip:
                raise SystemExit(f'Refusing writes to {part}: unresolved or ambiguous references remain; review the preview.')
            by_line = defaultdict(list)
            for (ln, s, e, rep) in conversions:
                by_line[ln].append((s, e, rep))
            new_lines = []
            for lineno, raw in enumerate(raw_lines, 1):
                if lineno in by_line:
                    r = raw
                    for (s, e, rep) in sorted(by_line[lineno], reverse=True):
                        r = r[:s] + rep + r[e:]
                    new_lines.append(r)
                else:
                    new_lines.append(raw)
            prepared[part] = "".join(new_lines)
            total_conv += len(conversions); total_skip += len(skip)
    for part, text in prepared.items():
        write_source(os.path.join(ROOT, part), text)
    print(f"\n##### TOTAL convert={total_conv}  skip={total_skip}  (apply={apply})")

if __name__ == "__main__":
    main()
