"""Small source-preserving helpers for reference conversions."""
import os
import re
import shutil
import tempfile
from pathlib import Path


LITERAL = re.compile(
    r'(?P<comment>(?<!\\)%[^\r\n]*)'
    r'|\\begin\s*\{(?P<env>verbatim\*?|Verbatim\*?|BVerbatim|LVerbatim|lstlisting|minted|algorithm\*?|algorithmic|algorithm2e\*?|procedure|function)\}'
    r'.*?\\end\s*\{(?P=env)\}'
    r'|\\(?:verb\*?|lstinline(?:\[[^\]]*\])?|mintinline(?:\[[^\]]*\])?\{[^{}]*\})(?P<delim>[^\s{])[^\r\n]*?(?P=delim)'
    r'|\\(?:lstinline(?:\[[^\]]*\])?|mintinline(?:\[[^\]]*\])?\{[^{}]*\}|texttt|url|path)\{[^{}\r\n]*\}', re.S)
MATH = re.compile(r'(?<!\\)\$\$.*?(?<!\\)\$\$|(?<!\\)\$[^$]*?(?<!\\)\$|\\\[.*?\\\]|\\\(.*?\\\)', re.S)
MATH_ENV = re.compile(r'\\begin\s*\{(?P<math_env>equation\*?|align\*?|alignat\*?|flalign\*?|gather\*?|multline\*?|eqnarray\*?|displaymath|math|aligned|alignedat|gathered|split|cases|array)\}.*?\\end\s*\{(?P=math_env)\}', re.S)


def mask_protected(text, *, math=False):
    """Mask comments, supported code and pseudocode, preserving every offset."""
    blank = lambda m: re.sub(r'[^\r\n]', ' ', m.group(0))
    masked = LITERAL.sub(blank, text)
    return MATH.sub(blank, MATH_ENV.sub(blank, masked)) if math else masked


def read_source(path):
    # Strict UTF-8 prevents destructive replacement of undecodable characters;
    # decode/encode also preserves a UTF-8 BOM and mixed newline sequences.
    return Path(path).read_bytes().decode('utf-8')


def write_source(path, text):
    """Back up once and atomically replace a changed source file."""
    path = Path(path)
    data = text.encode('utf-8')
    if path.read_bytes() == data:
        return
    backup = path.with_name(path.name + '.before-ref-conversion.bak')
    if not backup.exists():
        shutil.copy2(path, backup)
    fd, temporary = tempfile.mkstemp(prefix=path.name + '.', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as output:
            output.write(data)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
