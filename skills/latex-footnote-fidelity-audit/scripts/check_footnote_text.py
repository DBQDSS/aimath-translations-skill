#!/usr/bin/env python3
"""Compare OCR-note candidates with TeX footnotes in matching chapters.

Usage: python check_footnote_text.py <project-root> [chapter numbers...]
Inputs follow src/chN.blocks.md and chapters/ch0N.tex. Without explicit chapter
numbers, discover matching OCR files. Word overlap is supporting evidence only:
a Chinese translation generally does not share the English source's words.
Unmatched/empty/count candidates return 1 for review, not proof of note loss.
"""
import argparse
import re
from pathlib import Path

BLOCK = re.compile(r'^<<p(\d+)\|([a-z_]+)\|bbox=\[([^\]]*)\]>>(.*?)(?=^<<p|\Z)', re.S | re.M)
HEAD = re.compile(r'^\s*\$\s*\^\{?(\d+)\}?\s*\$\s*(\S.*)$', re.S)


def norm(text):
    text = re.sub(r'\\index\{[^{}]*\}', '', text)
    text = re.sub(r'\$[^$]*\$', ' ', text)
    text = re.sub(r'\\[a-zA-Z]+', ' ', text)
    return ' '.join(re.findall(r'[A-Za-z]+', text)).lower()


def footnote_bodies(text):
    # Bounded static extraction; custom macros and \footnotetext need review.
    text = re.sub(r'(?<!\\)%[^\r\n]*', '', text)
    bodies = []
    for match in re.finditer(r'\\footnote(?:\[[^\]]*\])?\s*\{', text):
        start, cursor, depth = match.end(), match.end(), 1
        while cursor < len(text) and depth:
            if text[cursor] == '\\':
                cursor += 2
                continue
            depth += (text[cursor] == '{') - (text[cursor] == '}')
            cursor += 1
        if depth:
            raise ValueError('Unclosed footnote; inspect the source before comparing')
        bodies.append(text[start:cursor - 1])
    return bodies


def ocr_notes(path):
    notes = {}
    for match in BLOCK.finditer(Path(path).read_text(encoding='utf-8')):
        if match.group(2) not in ('footnote', 'text'):
            continue
        head = HEAD.match(match.group(4))
        if head:
            # Notes can restart on each page; never discard a repeated number.
            key = (int(match.group(1)), int(head.group(1)))
            notes.setdefault(key, []).append(head.group(2))
    return notes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    parser.add_argument('chapters', nargs='*', type=int)
    args = parser.parse_args()
    chapters = args.chapters or sorted(int(match.group(1)) for path in (args.root / 'src').glob('ch*.blocks.md')
                                      if (match := re.fullmatch(r'ch(\d+)\.blocks\.md', path.name)))
    if not chapters:
        parser.error('No OCR chapter files found; provide the expected input layout.')
    bad = False
    for chapter in chapters:
        source = args.root / 'src' / ('ch%d.blocks.md' % chapter)
        target = args.root / 'chapters' / ('ch%02d.tex' % chapter)
        notes = ocr_notes(source)
        bodies = footnote_bodies(target.read_text(encoding='utf-8'))
        flat = [norm(body) for body in bodies]
        unmatched = []
        for key, alternatives in notes.items():
            matched = False
            for candidate in alternatives:
                words = norm(candidate).split()
                if not words:
                    continue
                size = min(3, len(words))
                matched |= any(' '.join(words[i:i + size]) in body
                               for i in range(len(words) - size + 1) for body in flat)
            if not matched:
                unmatched.append(key)
        count_mismatch = len(bodies) != len(notes)
        bad |= bool(unmatched) or count_mismatch
        print('ch%02d OCR note candidates=%d TeX footnotes=%d unmatched(page,note)=%s%s'
              % (chapter, len(notes), len(bodies), unmatched or '-', ' [count candidate]' if count_mismatch else ''))
    print('Footnote candidate check: %s; verify source pages and translated note bodies.'
          % ('REVIEW' if bad else 'NO CANDIDATES UNDER THESE HEURISTICS'))
    return int(bad)


if __name__ == '__main__':
    raise SystemExit(main())
