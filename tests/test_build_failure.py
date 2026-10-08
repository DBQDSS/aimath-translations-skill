from __future__ import annotations

import os
import runpy
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT = (Path(__file__).parents[1] / "skills/mathtranslation-build-verify"
          / "scripts/build_and_check.py")


class BuildFailureTests(unittest.TestCase):
    def test_failed_build_step_cannot_report_stale_success(self):
        # The old driver continued after a failed engine and could trust a stale
        # clean main.log. An actual failing return code must stop the pipeline.
        failed = subprocess.CompletedProcess(["xelatex"], 7, b"engine failed", b"")
        with patch.object(sys, "argv", [str(SCRIPT)]), \
             patch.dict(os.environ, {}, clear=False), \
             patch("os.chdir"), patch("os.path.isfile", return_value=True), \
             patch("subprocess.run", return_value=failed) as run:
            with self.assertRaises(SystemExit) as result:
                runpy.run_path(str(SCRIPT), run_name="__main__")
        self.assertEqual(7, result.exception.code)
        self.assertEqual(1, run.call_count)


if __name__ == "__main__":
    unittest.main()
