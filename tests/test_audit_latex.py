from __future__ import annotations

import hashlib
import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "audit_latex.py"
SPEC = importlib.util.spec_from_file_location("audit_latex", SCRIPT)
assert SPEC and SPEC.loader
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


class AuditLatexTests(unittest.TestCase):
    def test_bundled_assets_match_authorized_template(self) -> None:
        assets = Path(__file__).parents[1] / "assets"
        expected = {
            "mathtranslations-translation-template.tex": (
                "b2cc106209969e77878f3ba6dfe0bf050d4d38da0c68e558a96241350827531e"
            ),
            "logo.pdf": (
                "8b3839adbf870a8c5e825c9f004125816835bbb321617e619e5f589b672fc8d5"
            ),
        }

        for name, digest in expected.items():
            with self.subTest(asset=name):
                content = (assets / name).read_bytes()
                self.assertEqual(digest, hashlib.sha256(content).hexdigest())

    def test_clean_project(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "main.tex").write_text(
                "\\label{thm:one}\n"
                "由定理~\\ref{thm:one}可知。\\cite{sample}\n"
                "\\includegraphics{plot}\n",
                encoding="utf-8",
            )
            (root / "refs.bib").write_text(
                "@book{sample, title={Example}}\n", encoding="utf-8"
            )
            (root / "plot.png").write_bytes(b"not-a-real-png")

            errors, warnings = AUDIT.audit(root)

            self.assertEqual([], errors)
            self.assertEqual([], warnings)

    def test_reports_structural_problems(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "main.tex").write_text(
                "\\label{dup}\\label{dup}\n"
                "\\ref{missing}\\cite{unknown}\n"
                "见定理 2.3。TODO\n"
                "\\includegraphics{absent}\n",
                encoding="utf-8",
            )

            errors, warnings = AUDIT.audit(root)

            self.assertTrue(any("duplicate label" in item for item in errors))
            self.assertTrue(any("undefined reference" in item for item in errors))
            self.assertTrue(any("undefined citation" in item for item in errors))
            self.assertTrue(any("missing graphic" in item for item in errors))
            self.assertTrue(any("hard-coded reference" in item for item in warnings))
            self.assertTrue(any("unresolved marker" in item for item in warnings))

    def test_ignores_macro_parameter_references(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "main.tex").write_text(
                "\\newcommand{\\row}[1]{\\pageref*{#1}}\n",
                encoding="utf-8",
            )

            errors, warnings = AUDIT.audit(root)

            self.assertEqual([], errors)
            self.assertEqual([], warnings)

    def test_mathtranslations_profile_accepts_core_contract(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            metadata = {
                "BookTitleCN": "拓扑学",
                "BookTitleEN": "Topology",
                "OriginalAuthor": "Example Author",
                "OriginalEdition": "2nd edition",
                "OriginalPublisher": "Example Press",
                "OriginalYear": "2025",
                "Translator": "Example Translator",
                "ModelUsed": "Example Model",
                "TranslationDate": "22 Aug 2026",
            }
            metadata_tex = "\n".join(
                f"\\newcommand{{\\{key}}}{{{value}}}"
                for key, value in metadata.items()
            )
            (root / "main.tex").write_text(
                "% !TeX program = xelatex\n"
                "\\documentclass[UTF8,12pt,fontset=none]{ctexart}\n"
                "\\newcommand{\\newterm}[3]{#2（#3）}\n"
                "\\newcommand{\\printterminology}{}\n"
                "\\newcommand{\\longprooflink}[2]{#2}\n"
                "\\newenvironment{longproof}[2]{}{}\n"
                "\\newenvironment{exercises}{}{}\n"
                "\\newenvironment{answers}[1]{}{}\n"
                "\\usepackage{tikz-cd}\n"
                "\\def\\fonts{FandolSong FandolKai FandolFang cmunrm.otf}\n"
                "\\def\\links{linkcolor=MidnightBlue,citecolor=BrickRed,"
                "urlcolor=MidnightBlue,linktoc=all}\n"
                f"{metadata_tex}\n"
                "\\begin{document}\n"
                "\\newterm{topology}{拓扑}{topology}.\n"
                "封面：\\Translator\\ 翻译及重排.\n"
                "\\longprooflink{main-proof}{查看证明}\n"
                "\\begin{longproof}{main-proof}{主定理}证明.\\end{longproof}\n"
                "\\printterminology\n"
                "\\end{document}\n",
                encoding="utf-8",
            )

            errors, warnings = AUDIT.audit(root, profile="mathtranslations")

            self.assertEqual([], errors)
            self.assertEqual([], warnings)

    def test_mathtranslations_profile_flags_typesetting_rules(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "main.tex").write_text(
                "% !TeX program = xelatex\n"
                "\\documentclass[UTF8,12pt,fontset=none]{ctexart}\n"
                "\\begin{document}\n"
                "\\[ a+b \\]\n"
                "\\[ c+d \\]\n"
                "中文“引号”示例.\n"
                "1. 手动编号第一条\n"
                "2. 手动编号第二条\n"
                "\\end{document}\n",
                encoding="utf-8",
            )

            _, warnings = AUDIT.audit(root, profile="mathtranslations")

            self.assertTrue(
                any("consecutive display-math" in item for item in warnings)
            )
            self.assertTrue(any("TeX `` and ''" in item for item in warnings))
            self.assertTrue(any("enumerate" in item for item in warnings))

    def test_mathtranslations_profile_reports_drift(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "main.tex").write_text(
                "\\documentclass{article}\n"
                "\\newcommand{\\newterm}[3]{#2}\n"
                "\\newcommand{\\printterminology}{}\n"
                "\\begin{document}\n"
                "\\newterm{bad key}{术语}{term}。\n"
                "\\newterm{bad key}{术语}{term}。\n"
                "\\longprooflink{missing-proof}{查看证明}\n"
                "\\end{document}\n",
                encoding="utf-8",
            )

            errors, warnings = AUDIT.audit(root, profile="mathtranslations")

            self.assertTrue(any("terminology key" in item for item in errors))
            self.assertTrue(any("long-proof key" in item for item in errors))
            self.assertTrue(any("ASCII '.'" in item for item in warnings))
            self.assertTrue(any("XeLaTeX" in item for item in warnings))
            self.assertTrue(any("printterminology" in item for item in warnings))

    def test_mathtranslations_profile_accepts_cls_project(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "mathtranslation.cls").write_text(
                "\\newcommand{\\newterm}[3]{#2（#3）}\n"
                "\\newcommand{\\printterminology}{}\n"
                "\\newcommand{\\longprooflink}[2]{#2}\n"
                "\\newenvironment{longproof}[2]{}{}\n"
                "\\newenvironment{exercises}{}{}\n"
                "\\newenvironment{answers}[1]{}{}\n"
                "\\def\\fonts{FandolSong FandolKai FandolFang}\n"
                "\\usepackage{tikz-cd}\n"
                "\\newcommand{\\makecover}{}\n"
                "\\newcommand{\\makecontents}{}\n"
                "\\newcommand{\\makebibliography}{}\n"
                "\\def\\cover{\\Translator\\ 翻译及重排}\n",
                encoding="utf-8",
            )
            (root / "refs.bib").write_text(
                "@book{sample, title={Example}}\n", encoding="utf-8"
            )
            (root / "tools").mkdir()
            (root / "tools" / "build.sh").write_text(
                "#!/usr/bin/env bash\nxelatex main && biber main && xelatex main\n",
                encoding="utf-8",
            )
            (root / "main.tex").write_text(
                "% !TeX program = xelatex\n"
                "\\documentclass[BookTitleCN={示例},BookTitleEN={Example},"
                "OriginalAuthor={A},OriginalEdition={1st},OriginalPublisher={P},"
                "OriginalYear={2024},Translator={T},ModelUsed={M},"
                "TranslationDate={2026}]{mathtranslation}\n"
                "\\addbibresource{refs.bib}\n"
                "\\begin{document}\n"
                "\\makecover\n"
                "\\frontmatter\n"
                "\\makecontents\n"
                "\\mainmatter\n"
                "\\chapter{引言}\n"
                "正文内容.\\newterm{example}{示例}{example}.\n"
                "\\makebibliography\n"
                "\\printterminology\n"
                "\\end{document}\n",
                encoding="utf-8",
            )

            errors, warnings = AUDIT.audit(root, profile="mathtranslations")

            self.assertEqual([], errors)
            self.assertEqual([], warnings)


if __name__ == "__main__":
    unittest.main()
