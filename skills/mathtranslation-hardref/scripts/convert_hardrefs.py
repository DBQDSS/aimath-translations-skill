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
import re, sys, os
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
# Default to the directory this script is run from; allow override via env if needed.
ROOT = os.environ.get("MT_ROOT", os.getcwd())
AUX = os.path.join(ROOT, "main.aux")
PARTS = sorted(f for f in os.listdir(ROOT) if re.match(r"part.*\.tex$", f))
GF = {"partgf1.tex", "partgf2.tex"}

label_num = {}
if os.path.exists(AUX):
    txt = open(AUX, encoding="utf-8", errors="ignore").read()
    for m in re.finditer(r"\\newlabel\{([^}]*)\}\{\{([^}]*)\}\{", txt):
        label_num[m.group(1)] = m.group(2).strip()

PREFIX_ENV = {"定理": "theorem", "命题": "proposition", "引理": "lemma",
              "推论": "corollary", "定义": "definition", "注": "remark",
              "例": "example", "问题": "problem"}
PREFIX_REFC = {"定理": r"\thmref", "命题": r"\propref", "引理": r"\lemref",
               "推论": r"\corref", "定义": r"\defref", "注": r"\remref",
               "例": r"\exref", "问题": r"\probref"}

RE_THM = re.compile(r"(定理|命题|引理|推论|定义|注|例|问题)\s+(\d+\.\d+)")
RE_EQ = re.compile(r"(公式|式|方程)\s*\((\d+)\)")
RE_CHAPTER = re.compile(r"章第\s+(\d+\.\d+)")

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
    with open(path, encoding="utf-8", errors="ignore") as fh:
        for lineno, raw in enumerate(fh, 1):
            line = strip_comment(raw)
            for bm in re.finditer(r"\\begin\{([^}]*)\}", line):
                stack.append(bm.group(1))
            for em in re.finditer(r"\\end\{([^}]*)\}", line):
                if stack and stack[-1] == em.group(1):
                    stack.pop()
            for lm in re.finditer(r"\\label\{([^}]*)\}", line):
                env = stack[-1] if stack else None
                labels.append((lm.group(1), env, label_num.get(lm.group(1), ""), lineno))
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
    apply = "--apply" in sys.argv
    per_file, gf_thm, gf_eq, mainbook_eq = build_indexes()
    total_conv = 0; total_skip = 0
    for part in PARTS:
        in_gf = part in GF
        local_thm = defaultdict(list)
        for (name, env, printed, ln) in per_file[part]:
            if printed and env != "equation":
                local_thm[(env, printed)].append(name)
        raw_lines = open(os.path.join(ROOT, part), encoding="utf-8", errors="ignore").read().split("\n")
        conversions = []; skip = []
        for lineno, raw in enumerate(raw_lines, 1):
            clean = strip_comment(raw)
            for m in RE_THM.finditer(clean):
                prefix, num = m.group(1), m.group(2)
                env = PREFIX_ENV[prefix]
                cands = (gf_thm if in_gf else local_thm).get((env, num), [])
                cands = [c for c in cands if c]
                if len(cands) == 1:
                    s, e = m.start(), m.end()
                    if raw[s:e] == clean[s:e]:
                        conversions.append((lineno, s, e, f"{PREFIX_REFC[prefix]}{{{cands[0]}}}"))
                    else:
                        skip.append((lineno, prefix+num, "pos-mismatch"))
                else:
                    skip.append((lineno, prefix+num, f"{len(cands)} cands"))
            for m in RE_EQ.finditer(clean):
                prefix, num = m.group(1), m.group(2)
                cands = (gf_eq if in_gf else mainbook_eq).get(num, [])
                cands = [c for c in cands if c]
                if len(cands) == 1:
                    s, e = m.start(), m.end()
                    if raw[s:e] == clean[s:e]:
                        conversions.append((lineno, s, e, f"\\eqref{{{cands[0]}}}"))
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
            with open(os.path.join(ROOT, part), "w", encoding="utf-8") as fh:
                fh.write("\n".join(new_lines))
            total_conv += len(conversions); total_skip += len(skip)
    print(f"\n##### TOTAL convert={total_conv}  skip={total_skip}  (apply={apply})")

if __name__ == "__main__":
    main()
