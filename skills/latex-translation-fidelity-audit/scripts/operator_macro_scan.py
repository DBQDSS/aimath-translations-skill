#!/usr/bin/env python3
"""Scan a LaTeX translation for WRONG operator-macro usage (the reader-caught class).

Usage:
    python operator_macro_scan.py <dir_or_file> [glob=*.tex]

The canonical error this catches: a translation that hand-writes
    \\operatorname{Fr}   (should be \\Frob)
    \\operatorname{N}    (should be \\Nm)
because the project defines \\Frob / \\Nm macros (in mycommand.sty; never edited)
and the translation must use them. These two are the documented reader-caught
errors in the Milne Class Field Theory translation.

IMPORTANT: \\operatorname{Hom}, \\operatorname{Aut}, \\operatorname{Res},
\\operatorname{ord}, \\operatorname{Tr}, \\operatorname{Art} are LEGITIMATE
operator names in normal maths usage and are NOT flagged. Only extend
ERROR_PATTERNS below when a specific project proves a given name should have been
a macro.

The script also prints the FULL inventory of every \\operatorname{X} token used,
so you can eyeball whether any other name should have been a project macro.

Scratch/backup dirs (_scratch, backup, *.bak) are skipped automatically.
"""
import sys, os, re, glob

# The genuinely-wrong operator names (should have been project macros). Extend
# per project ONLY with evidence; do not add Hom/Aut/Res/ord/Tr/Art here.
ERROR_PATTERNS = [r'\\operatorname\{(Fr|N)\}']

SKIP = ('_scratch', 'backup', '.bak')

def iter_files(target, g):
    if os.path.isdir(target):
        for f in glob.glob(os.path.join(target, "**", g), recursive=True):
            if any(s in f for s in SKIP):
                continue
            yield f
    else:
        yield target

def main():
    target = sys.argv[1]
    g = sys.argv[2] if len(sys.argv) > 2 else "*.tex"
    inventory = {}
    errors = []
    for f in iter_files(target, g):
        txt = open(f, encoding='utf-8', errors='replace').read()
        for m in re.finditer(r'\\operatorname\{([A-Za-z]+)\}', txt):
            inventory[m.group(1)] = inventory.get(m.group(1), 0) + 1
        for pat in ERROR_PATTERNS:
            for m in re.finditer(pat, txt):
                ln = txt[:m.start()].count("\n") + 1
                errors.append((f, ln, m.group(0)))
    print("=== \\operatorname{X} inventory (all files) ===")
    for name, c in sorted(inventory.items(), key=lambda kv: -kv[1]):
        flag = "  <-- WRONG (use project macro)" if name in ("Fr", "N") else ""
        print("  %-6s %4d%s" % (name, c, flag))
    print("\n=== ERROR-PATTERN hits (\\operatorname{Fr}/\\operatorname{N}) ===")
    if errors:
        for f, ln, s in errors:
            print("  %s:%d: %s" % (f, ln, s))
    else:
        print("  none  ->  OK")
    print("\nERROR-PATTERN operator macros found: %d" % len(errors))
    if len(errors) == 0:
        print("OK: no hand-written \\operatorname{Fr}/\\operatorname{N} (use \\Frob/\\Nm).")

if __name__ == "__main__":
    main()
