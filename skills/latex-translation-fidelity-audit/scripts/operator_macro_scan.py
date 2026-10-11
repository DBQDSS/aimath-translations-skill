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
import sys, os, re, glob, argparse
from source_guard import mask_protected

# The genuinely-wrong operator names (should have been project macros). Extend
# per project ONLY with evidence; do not add Hom/Aut/Res/ord/Tr/Art here.
ERROR_PATTERNS = []  # No operator spelling is intrinsically wrong.

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
    parser = argparse.ArgumentParser(description='Inventory operators and report explicitly configured macro candidates.')
    parser.add_argument('target')
    parser.add_argument('glob', nargs='?', default='*.tex')
    parser.add_argument('--expect', action='append', default=[], metavar='NAME=MACRO')
    args = parser.parse_args()
    expected = {}
    for entry in args.expect:
        name, separator, macro = entry.partition('=')
        if not separator or not name or not macro:
            parser.error('--expect requires NAME=MACRO')
        expected[name] = macro
    target, g = args.target, args.glob
    inventory = {}
    errors = []
    for f in iter_files(target, g):
        txt = mask_protected(open(f, encoding='utf-8').read())
        for m in re.finditer(r'\\operatorname\{([A-Za-z]+)\}', txt):
            inventory[m.group(1)] = inventory.get(m.group(1), 0) + 1
        for m in re.finditer(r'\\operatorname\{([A-Za-z]+)\}', txt):
            if m.group(1) in expected:
                ln = txt[:m.start()].count("\n") + 1
                errors.append((f, ln, m.group(0)))
    print("=== \\operatorname{X} inventory (all files) ===")
    for name, c in sorted(inventory.items(), key=lambda kv: -kv[1]):
        flag = "  <-- verify configured macro %s" % expected[name] if name in expected else ""
        print("  %-6s %4d%s" % (name, c, flag))
    print("\n=== Configured macro candidates ===")
    if errors:
        for f, ln, s in errors:
            print("  %s:%d: %s" % (f, ln, s))
    else:
        print("  none  ->  OK")
    print("\nConfigured macro candidates found: %d" % len(errors))
    if len(errors) == 0:
        print("No configured candidates; verify notation against the source and project macros.")

if __name__ == "__main__":
    main()
