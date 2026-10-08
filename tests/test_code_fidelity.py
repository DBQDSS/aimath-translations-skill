from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
SPEC = importlib.util.spec_from_file_location("audit_code", ROOT / "scripts/audit_latex.py")
assert SPEC and SPEC.loader
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)
SCANNER = ROOT / "skills/latex-translation-fidelity-audit/scripts/residual_english_scan.py"


class CodeFidelityTests(unittest.TestCase):
    def test_literal_code_is_not_a_project_reference_or_prose_defect(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "main.tex").write_text(
                "\\begin{lstlisting}\n"
                "TODO = 'Theorem 2.3'\n"
                "\\ref{not-a-project-label}\\includegraphics{example-only}\n"
                "\\end{lstlisting}\n"
                "\\verb|TODO \\ref{literal}|\n"
                "\\label{real}\\ref{real}\n",
                encoding="utf-8",
            )
            self.assertEqual(([], []), AUDIT.audit(root))

    def test_algorithms_keep_real_references_but_skip_prose_policies(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "main.tex").write_text(
                "\\begin{algorithm}\n\\label{alg:one}\n"
                "1. Input: Example。\n2. Output: “Example”\n"
                "\\ref{missing}\n\\end{algorithm}\n",
                encoding="utf-8",
            )
            errors, warnings = AUDIT.audit(root, profile="mathtranslations")
            self.assertTrue(any("undefined reference" in e for e in errors))
            self.assertFalse(any("sentence endings" in w or "quotes use TeX" in w
                                 or "manually numbered" in w for w in warnings))

    def test_supported_code_masks_preserve_offsets_and_line_numbers(self):
        for environment in ("verbatim", "verbatim*", "Verbatim", "BVerbatim",
                            "LVerbatim", "lstlisting", "minted"):
            with self.subTest(environment=environment):
                source = (f"\\begin{{{environment}}}\r\n"
                          "TODO Example\r\n"
                          f"\\end{{{environment}}}\r\nTheorem remains\r\n")
                masked = AUDIT.mask_code(source)
                self.assertEqual(len(source), len(masked))
                self.assertEqual(source.count("\r\n"), masked.count("\r\n"))
                self.assertNotIn("TODO", masked)
                self.assertIn("Theorem remains", masked)

    def test_inline_percent_and_commented_delimiters_do_not_hide_prose(self):
        source = (
            "% \\begin{lstlisting}\n"
            "Theorem should be reviewed\n"
            "\\verb|100% Example| and \\lstinline{Proof}\n"
            "\\mintinline{python}|return 'Note'|\n"
            "\\mintinline{python}{return 'Claim'}\n"
            "% TODO review this\n"
        )
        masked = AUDIT.mask_code(source)
        self.assertIn("Theorem should be reviewed", masked)
        self.assertNotIn("100% Example", masked)
        self.assertNotIn("Proof", masked)
        self.assertNotIn("return", masked)
        self.assertIn("TODO review this", masked)

    def test_residual_english_scan_exempts_code_but_reports_real_prose(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "main.tex"
            source.write_text(
                "% \\begin{algorithm}\n"
                "\\begin{lstlisting}\nreturn 'Example'\n\\end{lstlisting}\n"
                "\\begin{algorithm}\nInput: Example\nOutput: Note\n\\end{algorithm}\n"
                "\\verb|100% Proof| and \\mintinline{python}{return 'Claim'}\n"
                "Theorem needs prose translation\n",
                encoding="utf-8",
            )
            result = subprocess.run([sys.executable, "-B", str(SCANNER), str(source)],
                                    capture_output=True, text=True, check=True)
            self.assertIn("main.tex:10: Theorem needs prose translation", result.stdout)
            self.assertIn("excluded): 1", result.stdout)
            self.assertNotIn("Input: Example", result.stdout)


if __name__ == "__main__":
    unittest.main()
