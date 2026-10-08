#!/usr/bin/env python3
"""Audit a LaTeX translation project for common structural defects."""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path


EXCLUDED_DIRS = {
    ".git",
    ".svn",
    "_build",
    "build",
    "dist",
    "node_modules",
    "out",
    "mathtranslations-skill",
    "aimath-translations-skill",
}

COMMAND_PATTERNS = {
    "label": re.compile(r"\\label\s*\{([^{}]+)\}"),
    "reference": re.compile(
        r"\\(?:ref|eqref|pageref|autoref|cref|Cref|vref)\*?\s*\{([^{}]+)\}"
    ),
    "citation": re.compile(
        r"\\(?:cite|citep|citet|parencite|textcite|autocite|footcite)"
        r"\*?(?:\[[^\]]*\]){0,2}\s*\{([^{}]+)\}"
    ),
    "bibitem": re.compile(r"\\bibitem(?:\[[^\]]*\])?\s*\{([^{}]+)\}"),
    "bibliography": re.compile(r"\\bibliography\s*\{([^{}]+)\}"),
    "addbibresource": re.compile(r"\\addbibresource(?:\[[^\]]*\])?\s*\{([^{}]+)\}"),
    "includegraphics": re.compile(
        r"\\includegraphics(?:\[[^\]]*\])?\s*\{([^{}]+)\}"
    ),
}

BIB_ENTRY_RE = re.compile(r"@\w+\s*\{\s*([^,\s]+)\s*,", re.IGNORECASE)
TODO_RE = re.compile(r"\b(?:TODO|FIXME|XXX)\b|待译|待确认|待校", re.IGNORECASE)
HARDCODED_REFERENCE_RE = re.compile(
    r"(?:定理|引理|命题|推论|定义|公式|方程|式|图|表|章节?|附录)"
    r"\s*[~ ]*(?:第\s*)?\(?\d+(?:\.\d+){0,3}\)?"
)
LOG_PATTERNS = (
    ("error", re.compile(r"^! (?:LaTeX|Package|Class)? ?Error", re.IGNORECASE)),
    ("error", re.compile(r"Undefined control sequence", re.IGNORECASE)),
    ("error", re.compile(r"Emergency stop", re.IGNORECASE)),
    ("error", re.compile(r"Fatal error", re.IGNORECASE)),
    ("warning", re.compile(r"undefined references?", re.IGNORECASE)),
    ("warning", re.compile(r"Citation .+ undefined", re.IGNORECASE)),
    ("warning", re.compile(r"multiply defined", re.IGNORECASE)),
    ("warning", re.compile(r"Rerun to get cross-references right", re.IGNORECASE)),
    ("warning", re.compile(r"Overfull \\\\hbox", re.IGNORECASE)),
)
NEWTERM_RE = re.compile(
    r"\\newterm\s*\{([^{}]+)\}\s*\{([^{}]+)\}\s*\{([^{}]+)\}"
)
LONGPROOF_LINK_RE = re.compile(r"\\longprooflink\s*\{([^{}]+)\}\s*\{")
LONGPROOF_ENV_RE = re.compile(r"\\begin\s*\{longproof\}\s*\{([^{}]+)\}\s*\{")
COMMAND_DEFINITION_RE = re.compile(
    r"\\(?:newcommand|renewcommand|providecommand)\s*\{\\([A-Za-z@]+)\}"
)
CURLY_QUOTE_RE = re.compile("[“”]")
CONSECUTIVE_DISPLAY_MATH_RE = re.compile(r"\\\]\s*\\\[")
MANUAL_NUMBERING_LINE_RE = re.compile(r"^\s*\d+[.、)]\s+\S")
METADATA_DEFAULTS = {
    "BookTitleCN": "代数学",
    "BookTitleEN": "Algebra",
    "OriginalAuthor": "Serge Lang",
    "OriginalEdition": "3rd edition",
    "OriginalPublisher": "Springer",
    "OriginalYear": "2002",
    "Translator": "数译",
    "ModelUsed": "GPT-5.6 Sol",
    "TranslationDate": "17 Aug 2026",
}
TEMPLATE_MARKERS = {
    "term introduction command": r"\newcommand{\newterm}",
    "terminology index command": r"\newcommand{\printterminology}",
    "long-proof source link": r"\newcommand{\longprooflink}",
    "long-proof environment": r"\newenvironment{longproof}",
    "exercise environment": r"\newenvironment{exercises}",
    "answer environment": r"\newenvironment{answers}",
    "Song CJK font": "FandolSong",
    "Kai terminology font": "FandolKai",
    "Fang theorem font": "FandolFang",
    "CMU Serif font": "cmunrm.otf",
    "tikz-cd package": "tikz-cd",
    "internal-link color": "linkcolor=MidnightBlue",
    "citation color": "citecolor=BrickRed",
    "URL color": "urlcolor=MidnightBlue",
    "clickable TOC entries": "linktoc=all",
    "cover translator credit": r"\Translator\ 翻译及重排",
}

LITERAL_CODE_RE = re.compile(
    r"\\begin\s*\{(?P<literal_env>verbatim\*?|Verbatim\*?|BVerbatim|LVerbatim|lstlisting|minted)\}"
    r".*?\\end\s*\{(?P=literal_env)\}", re.DOTALL
)
INLINE_CODE_RE = re.compile(
    r"\\(?:verb\*?|lstinline(?:\[[^\]]*\])?|"
    r"mintinline(?:\[[^\]]*\])?\{[^{}]*\})(?P<delim>[^\s{])"
    r"[^\n]*?(?P=delim)"
    r"|\\(?:lstinline(?:\[[^\]]*\])?|"
    r"mintinline(?:\[[^\]]*\])?\{[^{}]*\})\{[^{}\n]*\}"
)
ALGORITHM_RE = re.compile(
    r"\\begin\s*\{(?P<algorithm_env>algorithm\*?|algorithmic|algorithm2e\*?|procedure|function)\}"
    r".*?\\end\s*\{(?P=algorithm_env)\}", re.DOTALL
)


def mask_code(text: str, *, algorithms: bool = False) -> str:
    """Hide supported literal regions while preserving offsets and line numbers.

    This is a bounded static filter, not a TeX parser. Custom environments,
    macro-generated listings, and listing escape-to-TeX need source review.
    """
    def blank(match: re.Match[str]) -> str:
        if match.group("comment") is not None:
            return match.group(0)
        return re.sub(r"[^\r\n]", " ", match.group(0))

    # Match in source order: an inline '%' stays code, while delimiters in
    # actual comments cannot swallow later content. Retain comments for TODOs.
    patterns = [r"(?P<comment>(?<!\\)%[^\r\n]*)",
                LITERAL_CODE_RE.pattern, INLINE_CODE_RE.pattern]
    if algorithms:
        patterns.append(ALGORITHM_RE.pattern)
    return re.sub("|".join(patterns), blank, text, flags=re.DOTALL)

# Markers expected in a project built on the current `mathtranslation.cls`
# (ctexbook-based) template. The class file supplies most of them, so the audit
# scans the whole project (including the .cls) for their presence.
CLS_MARKERS = {
    "terminology command": r"\newcommand{\newterm}",
    "terminology index command": r"\newcommand{\printterminology}",
    "long-proof source link": r"\newcommand{\longprooflink}",
    "long-proof environment": r"\newenvironment{longproof}",
    "exercise environment": r"\newenvironment{exercises}",
    "answer environment": r"\newenvironment{answers}",
    "Song CJK font": "FandolSong",
    "Kai terminology font": "FandolKai",
    "Fang theorem font": "FandolFang",
    "tikz-cd package": "tikz-cd",
    "cover translator credit": r"\Translator\ 翻译及重排",
    "public makecover": r"\newcommand{\makecover}",
    "public makecontents": r"\newcommand{\makecontents}",
    "public makebibliography": r"\newcommand{\makebibliography}",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit TeX sources, bibliography keys, assets, and LaTeX logs."
    )
    parser.add_argument("path", type=Path, help="A .tex file or project directory")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return a nonzero exit status when warnings are found",
    )
    parser.add_argument(
        "--profile",
        choices=("mathtranslations",),
        help="Apply checks for a named translation template profile",
    )
    return parser.parse_args()


def is_excluded(path: Path) -> bool:
    return any(part.lower() in EXCLUDED_DIRS for part in path.parts)


def collect_files(root: Path, suffix: str) -> list[Path]:
    if root.is_file():
        return [root] if root.suffix.lower() == suffix else []
    return sorted(
        path
        for path in root.rglob(f"*{suffix}")
        if path.is_file() and not is_excluded(path.relative_to(root))
    )


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8-sig", errors="replace")


def strip_comments(text: str) -> str:
    return re.sub(r"(?<!\\)%.*$", "", text, flags=re.MULTILINE)


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def split_keys(value: str) -> list[str]:
    return [key.strip() for key in value.split(",") if key.strip()]


def resolve_asset(project_root: Path, tex_file: Path, target: str) -> bool:
    asset = Path(target)
    bases = (tex_file.parent, project_root)
    extensions = ("", ".pdf", ".png", ".jpg", ".jpeg", ".eps", ".svg")
    for base in bases:
        for extension in extensions:
            candidate = base / Path(f"{asset}{extension}")
            if candidate.is_file():
                return True
    return False


def resolve_bib(project_root: Path, tex_file: Path, target: str) -> list[Path]:
    result: list[Path] = []
    for key in split_keys(target):
        candidate = Path(key)
        if candidate.suffix.lower() != ".bib":
            candidate = candidate.with_suffix(".bib")
        for base in (tex_file.parent, project_root):
            resolved = base / candidate
            if resolved.is_file() and resolved not in result:
                result.append(resolved)
    return result


def command_calls(text: str, command: str) -> list[re.Match[str]]:
    definition_occurrences = {
        match.start(1) - 1
        for match in COMMAND_DEFINITION_RE.finditer(text)
        if match.group(1) == command
    }
    return [
        match
        for match in re.finditer(rf"\\{re.escape(command)}\b", text)
        if match.start() not in definition_occurrences
    ]


def audit_mathtranslations_profile(
    project_root: Path, source_files: list[Path]
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    raw_parts: list[str] = []
    active_parts: list[str] = []

    for source_file in source_files:
        text = read_text(source_file)
        raw_parts.append(text)
        active = strip_comments(mask_code(text))
        active_parts.append(active)
        display = source_file.relative_to(project_root)
        manual_numbering_run = 0
        prose = mask_code(active, algorithms=True)
        for number, line in enumerate(prose.splitlines(), start=1):
            if "。" in line:
                warnings.append(
                    f"{display}:{number}: MathTranslations prose uses ASCII '.' "
                    "for sentence endings; found '。'"
                )
            for quote_match in CURLY_QUOTE_RE.finditer(line):
                warnings.append(
                    f"{display}:{number}: MathTranslations quotes use TeX "
                    f"`` and '' markers; found {quote_match.group(0)!r}"
                )
                break
            if MANUAL_NUMBERING_LINE_RE.match(line):
                manual_numbering_run += 1
                if manual_numbering_run == 2:
                    warnings.append(
                        f"{display}:{number}: manually numbered list found; "
                        "use the enumerate environment instead"
                    )
            else:
                manual_numbering_run = 0

        for match in CONSECUTIVE_DISPLAY_MATH_RE.finditer(prose):
            warnings.append(
                f"{display}:{line_number(active, match.start())}: consecutive "
                "display-math blocks; use a single align/aligned/align* "
                "environment instead"
            )

    raw_text = "\n".join(raw_parts)
    active_text = "\n".join(active_parts)
    # The user's own \printterminology call lives in a .tex file; counting it
    # across .cls/.sty would also catch class definitions and backup samples.
    tex_active = "\n".join(
        strip_comments(mask_code(read_text(sf)))
        for sf in source_files
        if sf.suffix.lower() == ".tex"
    )

    if not re.search(
        r"(?im)^%\s*!\s*TeX\s+program\s*=\s*xelatex\s*$", raw_text
    ):
        warnings.append("MathTranslations profile: missing XeLaTeX editor directive")

    uses_cls = bool(
        re.search(
            r"\\documentclass\s*(?:\[[^\]]*\]\s*)?\{mathtranslation\}", active_text
        )
    ) or any(
        sf.suffix.lower() == ".cls" and sf.name.lower() == "mathtranslation.cls"
        for sf in source_files
    )
    uses_ctexart = bool(
        re.search(r"\\documentclass\s*(?:\[[^\]]*\]\s*)?\{ctexart\}", active_text)
    )
    if not (uses_cls or uses_ctexart):
        warnings.append(
            "MathTranslations profile: expected a 'mathtranslation' (ctexbook) "
            "document class or the legacy 'ctexart' template"
        )

    if uses_ctexart and not uses_cls:
        document_class = re.search(
            r"\\documentclass\s*\[([^\]]*)\]\s*\{ctexart\}", active_text
        )
        if document_class:
            options = {item.strip() for item in document_class.group(1).split(",")}
            for option in ("UTF8", "12pt", "fontset=none"):
                if option not in options:
                    warnings.append(
                        f"MathTranslations profile: ctexart option {option!r} is missing"
                    )
        else:
            warnings.append(
                "MathTranslations profile: ctexart used without options; "
                "expected [UTF8,12pt,fontset=none]"
            )

    markers = CLS_MARKERS if uses_cls else TEMPLATE_MARKERS
    for description, marker in markers.items():
        if marker not in active_text:
            warnings.append(
                f"MathTranslations profile: missing {description} marker {marker!r}"
            )

    if uses_cls:
        for cmd in ("makecover", "makecontents", "makebibliography"):
            if not command_calls(active_text, cmd):
                warnings.append(
                    f"MathTranslations profile: mathtranslation.cls project should "
                    f"call \\{cmd}"
                )
        if re.search(
            r"\\usepackage\s*(?:\[[^\]]*\]\s*)?\{biblatex\}", active_text
        ):
            warnings.append(
                "MathTranslations profile: biblatex is loaded by mathtranslation.cls; "
                "remove the manual \\usepackage{biblatex} from main.tex"
            )
        if not re.search(r"\\addbibresource", active_text):
            warnings.append(
                "MathTranslations profile: add your bibliography with "
                "\\addbibresource{...}"
            )
        if not re.search(
            r"\\documentclass\s*(?:\[[^\]]*\]\s*)?\{mathtranslation\}", active_text
        ) and not re.search(
            r"\\(?:renewcommand|newcommand)\s*\{\\BookTitleCN\}", active_text
        ):
            warnings.append(
                "MathTranslations profile: set cover metadata via the documentclass "
                "options or \\renewcommand{\\BookTitleCN}{...} etc."
            )
        if not (project_root / "tools" / "build.sh").is_file() and not (
            project_root / "build.sh"
        ).is_file():
            warnings.append(
                "MathTranslations profile: no build.sh found; run the full build "
                "(xelatex x2 -> biber -> xelatex x2) to resolve ToC, references, "
                "and the terminology index"
            )
    else:
        for command, sample_value in METADATA_DEFAULTS.items():
            match = re.search(
                rf"\\(?:newcommand|renewcommand)\s*\{{\\{command}\}}\s*"
                r"\{([^{}]*)\}",
                active_text,
            )
            if not match:
                warnings.append(
                    f"MathTranslations profile: missing cover metadata \\{command}"
                )
            elif not match.group(1).strip():
                warnings.append(
                    f"MathTranslations profile: empty cover metadata \\{command}"
                )
            elif match.group(1).strip() == sample_value:
                warnings.append(
                    f"MathTranslations profile: sample metadata \\{command} still "
                    f"contains {sample_value!r}"
                )

    term_locations: dict[str, list[str]] = {}
    for source_file in source_files:
        text = strip_comments(mask_code(read_text(source_file)))
        display = source_file.relative_to(project_root)
        for match in NEWTERM_RE.finditer(text):
            key = match.group(1).strip()
            location = f"{display}:{line_number(text, match.start())}"
            term_locations.setdefault(key, []).append(location)
            if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9:._-]*", key):
                warnings.append(
                    f"{location}: terminology key {key!r} should be stable and "
                    "label-safe"
                )

    for key, locations in sorted(term_locations.items()):
        if len(locations) > 1:
            errors.append(
                f"duplicate MathTranslations terminology key {key!r}: "
                f"{', '.join(locations)}"
            )

    link_keys = Counter(LONGPROOF_LINK_RE.findall(active_text))
    proof_keys = Counter(LONGPROOF_ENV_RE.findall(active_text))
    for key in sorted(set(link_keys) | set(proof_keys)):
        if link_keys[key] != 1 or proof_keys[key] != 1:
            errors.append(
                f"MathTranslations long-proof key {key!r} has "
                f"{link_keys[key]} link(s) and {proof_keys[key]} proof environment(s)"
            )

    terminology_calls = command_calls(tex_active, "printterminology")
    if len(terminology_calls) != 1:
        warnings.append(
            "MathTranslations profile: expected exactly one final "
            f"\\printterminology call, found {len(terminology_calls)}"
        )
    else:
        trailing = tex_active[terminology_calls[0].end() :]
        end_doc = trailing.find(r"\end{document}")
        if end_doc != -1:
            trailing = trailing[:end_doc]
        trailing = trailing.strip()
        if trailing:
            warnings.append(
                "MathTranslations profile: \\printterminology is not the final "
                "document content"
            )

    return errors, warnings


def audit(
    root: Path, profile: str | None = None
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    if not root.exists():
        return [f"Path does not exist: {root}"], warnings

    project_root = root if root.is_dir() else root.parent
    tex_files = collect_files(root, ".tex")
    if not tex_files:
        return [f"No TeX files found under: {root}"], warnings

    label_locations: dict[str, list[str]] = {}
    reference_locations: dict[str, list[str]] = {}
    citation_locations: dict[str, list[str]] = {}
    bibliography_keys: set[str] = set()
    bibliography_files: set[Path] = set(collect_files(project_root, ".bib"))

    for tex_file in tex_files:
        text = read_text(tex_file)
        active_text = strip_comments(mask_code(text))
        display = tex_file.relative_to(project_root)

        for name, pattern in COMMAND_PATTERNS.items():
            for match in pattern.finditer(active_text):
                value = match.group(1).strip()
                if "#" in value:
                    continue
                location = f"{display}:{line_number(active_text, match.start())}"
                if name == "label":
                    label_locations.setdefault(value, []).append(location)
                elif name == "reference":
                    for key in split_keys(value):
                        reference_locations.setdefault(key, []).append(location)
                elif name == "citation":
                    for key in split_keys(value):
                        citation_locations.setdefault(key, []).append(location)
                elif name == "bibitem":
                    bibliography_keys.add(value)
                elif name in {"bibliography", "addbibresource"}:
                    bibliography_files.update(
                        resolve_bib(project_root, tex_file, value)
                    )
                elif name == "includegraphics":
                    if not resolve_asset(project_root, tex_file, value):
                        errors.append(f"{location}: missing graphic asset {value!r}")

        # Literal example tokens such as TODO or \ref are not project defects.
        for match in TODO_RE.finditer(mask_code(text)):
            warnings.append(
                f"{display}:{line_number(text, match.start())}: unresolved marker "
                f"{match.group(0)!r}"
            )

        for match in HARDCODED_REFERENCE_RE.finditer(active_text):
            line_start = active_text.rfind("\n", 0, match.start()) + 1
            line_end = active_text.find("\n", match.end())
            if line_end == -1:
                line_end = len(active_text)
            line = active_text[line_start:line_end]
            if "\\ref{" not in line and "\\eqref{" not in line:
                warnings.append(
                    f"{display}:{line_number(active_text, match.start())}: possible "
                    f"hard-coded reference {match.group(0)!r}"
                )

    for bib_file in bibliography_files:
        for match in BIB_ENTRY_RE.finditer(read_text(bib_file)):
            bibliography_keys.add(match.group(1).strip())

    for label, locations in sorted(label_locations.items()):
        if len(locations) > 1:
            errors.append(f"duplicate label {label!r}: {', '.join(locations)}")

    for label, locations in sorted(reference_locations.items()):
        if label not in label_locations:
            errors.append(f"undefined reference {label!r}: {', '.join(locations)}")

    for key, locations in sorted(citation_locations.items()):
        if key not in bibliography_keys:
            errors.append(f"undefined citation {key!r}: {', '.join(locations)}")

    for log_file in collect_files(project_root, ".log"):
        text = read_text(log_file)
        display = log_file.relative_to(project_root)
        seen: Counter[tuple[str, str]] = Counter()
        for number, line in enumerate(text.splitlines(), start=1):
            for severity, pattern in LOG_PATTERNS:
                if pattern.search(line):
                    normalized = line.strip()
                    key = (severity, normalized)
                    seen[key] += 1
                    if seen[key] == 1:
                        message = f"{display}:{number}: {normalized}"
                        (errors if severity == "error" else warnings).append(message)

    if profile == "mathtranslations":
        profile_files = sorted(
            set(
                tex_files
                + collect_files(project_root, ".sty")
                + collect_files(project_root, ".cls")
            )
        )
        profile_errors, profile_warnings = audit_mathtranslations_profile(
            project_root, profile_files
        )
        errors.extend(profile_errors)
        warnings.extend(profile_warnings)

    return errors, warnings


def main() -> int:
    args = parse_args()
    errors, warnings = audit(args.path.resolve(), profile=args.profile)

    for message in errors:
        print(f"ERROR: {message}")
    for message in warnings:
        print(f"WARNING: {message}")

    print(
        f"Audit complete: {len(errors)} error(s), {len(warnings)} warning(s)."
    )
    if errors or (args.strict and warnings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
