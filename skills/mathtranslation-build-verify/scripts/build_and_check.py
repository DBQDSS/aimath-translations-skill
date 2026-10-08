# -*- coding: utf-8 -*-
"""Full build + log verdict for a LaTeX book project (Windows / WorkBuddy).

Usage:  python build_and_check.py [project_dir]
        (defaults to the current working directory; MUST contain main.tex)

Order:  xelatex -> biber -> xelatex -> texindy(C locale) -> xelatex.
Never passes -output-directory (fatal on non-ASCII project paths).
cwd is set to the project dir, so every tool writes there by default.

Verdict is printed and also written to _build_report.txt in the project dir.
Exit code 0 iff every counter below is zero.
"""
import os
import re
import shutil
import subprocess
import sys
import time

BASE = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.getcwd()
TL = os.environ.get('TEXLIVE_BIN')
os.chdir(BASE)

def tool(name):
    if TL:
        return os.path.join(TL, name + ('.exe' if os.name == 'nt' else ''))
    return shutil.which(name) or name


XL, BI, IX = tool('xelatex'), tool('biber'), tool('texindy')

if not os.path.isfile('main.tex'):
    sys.exit('Project must contain main.tex; use the project driver for other layouts.')


def run(name, args, env=None):
    e = dict(os.environ)
    if env:
        e.update(env)
    t0 = time.time()
    r = subprocess.run(args, cwd=BASE, env=e, capture_output=True)
    print('[%s] rc=%d  %.1fs' % (name, r.returncode, time.time() - t0))
    if r.returncode != 0:
        tail = (r.stdout or b'').decode('utf-8', 'replace').splitlines()[-25:]
        print('  --- tail ---')
        for l in tail:
            print('   ', l[:160])
    if r.returncode != 0:
        # Stop before stale logs or PDFs can be reported as a clean build.
        sys.exit(r.returncode)
    return r.returncode


rcs = []
rcs.append(run('xelatex-1', [XL, '-interaction=nonstopmode', '-file-line-error', 'main.tex']))
if os.path.exists(os.path.join(BASE, 'main.bcf')):
    rcs.append(run('biber', [BI, 'main']))
rcs.append(run('xelatex-2', [XL, '-interaction=nonstopmode', '-file-line-error', 'main.tex']))
if os.path.exists(os.path.join(BASE, 'main.idx')):
    # texindy is Perl: it dies on a UTF-8 locale, so force the C locale for this step only.
    rcs.append(run('texindy', [IX, '-M', 'texindy', '-I', 'xelatex', '-C', 'utf8', 'main.idx'],
                   env={'LC_ALL': 'C', 'LANG': 'C', 'LC_CTYPE': 'C'}))
rcs.append(run('xelatex-3', [XL, '-interaction=nonstopmode', '-file-line-error', 'main.tex']))

log = open('main.log', encoding='utf-8', errors='replace').read()
# Under -file-line-error most errors are `./file.tex:NN: msg` with NO leading `!`,
# so BOTH patterns must be counted (see SKILL.md).
checks = [
    ('! errors',           r'^! ',                                    re.M),
    ('file:line errors',   r'\.tex:[0-9]+:',                          0),
    ('Undefined control',  r'Undefined control sequence',             0),
    ('Missing character',  r'Missing character',                      0),
    ('Font shape undefined', r'Font shape .* undefined',              0),
    ('multiply-defined',   r'multiply[ -]defined',                    0),
    ('undefined ref',      r'LaTeX Warning: Reference .* undefined',  0),
    ('undefined citation', r'Citation .* undefined',                  0),
    ('Overfull \\hbox',    r'Overfull \\hbox',                        0),
    ('Overfull \\vbox',    r'Overfull \\vbox',                        0),
]
lines = ['=' * 60, 'BUILD VERDICT  %s' % BASE, '=' * 60]
bad = 0
for nm, pat, fl in checks:
    n = len(re.findall(pat, log, fl))
    bad += n
    lines.append('  %-22s: %d' % (nm, n))
pages = re.findall(r'Output written on .*?\((\d+) pages', log)
lines.append('  %-22s: %s' % ('pages', pages))
lines.append('  %-22s: %s' % ('return codes', rcs))
lines.append('  %-22s: %s' % ('VERDICT', 'CLEAN' if bad == 0 else 'PROBLEMS (%d)' % bad))
out = '\n'.join(lines)
print('\n' + out)
open('_build_report.txt', 'w', encoding='utf-8').write(out + '\n')
sys.exit(0 if bad == 0 else 1)
