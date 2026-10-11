from __future__ import annotations

import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).parents[1]
HARDREF = ROOT / 'skills/mathtranslation-hardref/scripts'
FIDELITY = ROOT / 'skills/latex-translation-fidelity-audit/scripts'


def load_script(path):
    spec = importlib.util.spec_from_file_location(path.stem + '_test', path)
    module = importlib.util.module_from_spec(spec)
    with patch.object(sys, 'path', [str(path.parent), *sys.path]):
        spec.loader.exec_module(module)
    return module


def run_script(path, *args, environment=None):
    return subprocess.run([sys.executable, '-B', str(path), *map(str, args)],
                          capture_output=True, text=True, encoding='utf-8',
                          env={**os.environ, **(environment or {})})


class ReferenceSafetyTests(unittest.TestCase):
    def test_bare_map_uses_printed_number_and_retains_ambiguity(self):
        module = load_script(HARDREF / 'convert_bare_refs.py')
        aux = (r'\newlabel{thm:ii.99.99}{{2.3}{8}{x}{theorem.1}{}}' + '\n'
               + r'\newlabel{lem:ii.4.5}{{2.3}{9}{x}{theorem.2}{}}' + '\n'
               + r'\newlabel{prop:ii.7.7}{{2.3}{10}{x}{theorem.3}{}}')
        mapping = module.build_by_chap(aux)
        self.assertEqual({'2.3': None}, mapping['ii'])
        self.assertEqual('thm:ii.99.99', module.build_by_chap(aux.splitlines()[0])['ii']['2.3'])

    def test_exact_count_mismatch_refuses_all_writes(self):
        module = load_script(HARDREF / 'convert_bare_refs.py')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            original = b'old old\r\n'
            (root / 'main.tex').write_bytes(original)
            (root / 'main.aux').write_text('', encoding='utf-8')
            module.BASE = directory
            module.EXACT = {'main.tex': [('old', 'new', 1)]}
            with patch.object(sys, 'argv', ['convert_bare_refs.py', '--go']), patch('sys.stdout', io.StringIO()):
                with self.assertRaises(SystemExit):
                    module.main()
            self.assertEqual(original, (root / 'main.tex').read_bytes())

    def test_bare_conversion_protects_math_code_and_line_endings(self):
        module = load_script(HARDREF / 'convert_bare_refs.py')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            original = ('\ufeff见 (2.3)\r\n'
                        '\\begin{lstlisting}\n(2.3)\n\\end{lstlisting}\r\n'
                        '\\begin{align}(2.3)\\end{align}\n'
                        '$ (2.3) $\r\n% (2.3)\n').encode('utf-8')
            (root / 'main.tex').write_bytes(original)
            (root / 'main.aux').write_text(r'\newlabel{thm:any-name}{{2.3}{8}{x}{theorem.1}{}}', encoding='utf-8')
            module.BASE = directory
            with patch.object(sys, 'argv', ['convert_bare_refs.py', '--go']), patch('sys.stdout', io.StringIO()):
                module.main()
            result = (root / 'main.tex').read_bytes()
            self.assertEqual(original.replace(b'(2.3)', b'(\\ref{thm:any-name})', 1), result)
            self.assertEqual(original, (root / 'main.tex.before-ref-conversion.bak').read_bytes())

    def test_hardref_same_line_environment_and_protected_code(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            original = ('\\begin{theorem}\\label{thm:x}内容\\end{theorem}\r\n'
                        '由定理 2.3可知\n'
                        '\\begin{lstlisting}定理 2.3\\end{lstlisting}\r\n').encode('utf-8')
            (root / 'main.tex').write_bytes(original)
            (root / 'main.aux').write_text(r'\newlabel{thm:x}{{2.3}{8}{x}{theorem.1}{}}', encoding='utf-8')
            result = run_script(HARDREF / 'convert_hardrefs.py', '--apply', environment={'MT_ROOT': directory})
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual(original.replace('由定理 2.3'.encode(), '由定理~\\ref{thm:x}'.encode()), (root / 'main.tex').read_bytes())

    def test_xref_ambiguous_targets_refuse_writes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'chapters').mkdir()
            original = b'[VI.6.12]\n'
            source = root / 'chapters/ch06.tex'
            source.write_bytes(original)
            (root / '_auxmap.json').write_text(json.dumps({'sec': {}, 'subsec': {}, 'thm': {'VI.6.12': 'thm:x'}, 'prob': {'VI.6.12': 'ex:x'}}), encoding='utf-8')
            result = run_script(FIDELITY / 'xref_bare_scan.py', root, 'apply')
            self.assertNotEqual(0, result.returncode)
            self.assertEqual(original, source.read_bytes())

    def test_xref_retains_bom_mixed_newlines_and_code(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'chapters').mkdir()
            original = ('\ufeff定义~VI.6.12\r\n% VI.6.12\n'
                        '\\begin{equation}VI.6.12\\end{equation}\r\n'
                        '\\verb|VI.6.12|\n').encode('utf-8')
            source = root / 'chapters/ch06.tex'
            source.write_bytes(original)
            (root / '_auxmap.json').write_text(json.dumps({'sec': {}, 'subsec': {}, 'thm': {'VI.6.12': 'thm:x'}, 'prob': {}}), encoding='utf-8')
            result = run_script(FIDELITY / 'xref_bare_scan.py', root, 'apply')
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual(original.replace(b'VI.6.12', b'VI.\\ref{thm:x}', 1), source.read_bytes())

    def test_aux_collisions_are_null_and_nested_fields_stay_together(self):
        module = load_script(FIDELITY / 'aux_number_map.py')
        self.assertEqual(['{A}{B}', '9', 'title', 'theorem.6.4', ''], module.split_groups('{{A}{B}}{9}{title}{theorem.6.4}{}'))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'chapters').mkdir()
            (root / 'chapters/ch6.aux').write_text(
                r'\newlabel{first}{{7.4}{9}{\texorpdfstring{A}{B}}{theorem.6.4}{}}' + '\n'
                + r'\newlabel{second}{{7.4}{10}{x}{theorem.6.5}{}}', encoding='utf-8')
            result = run_script(FIDELITY / 'aux_number_map.py', root)
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIsNone(json.loads((root / '_auxmap.json').read_text())['thm']['VI.7.4'])


class CandidateScannerTests(unittest.TestCase):
    def test_section_heading_is_read_and_comments_do_not_inflate_counts(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'chapters').mkdir()
            (root / 'chapters/ch01.tex').write_text(
                '% \\section{not real}\n\\section{真实章节}\n'
                '\\subsection*{习题}\\phantomsection\n\\begin{problem}题目\\end{problem}\n', encoding='utf-8')
            result = run_script(FIDELITY / 'section_parity.py', root, '--expect', '1=1')
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn('expect=1 OK', result.stdout)
            self.assertNotIn('NO exercise heading', result.stdout)

    def test_operator_defaults_do_not_declare_valid_names_wrong(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'main.tex'
            source.write_text(r'\operatorname{Fr}+\operatorname{N}', encoding='utf-8')
            result = run_script(FIDELITY / 'operator_macro_scan.py', source)
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn('candidates found: 0', result.stdout)
            self.assertNotIn('WRONG', result.stdout)

    def test_hyphen_apply_uses_verified_terms_and_accepts_lf(self):
        script = ROOT / 'skills/latex-display-layout-audit/scripts/fix_hyphen_spacing.py'
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'chapters').mkdir()
            source = root / 'chapters/main.tex'
            original = (r'\text{Hilbert - Schmidt; a - b}' + '\n'
                        + r'\begin{lstlisting}\text{Hilbert - Schmidt}\end{lstlisting}' + '\n').encode()
            source.write_bytes(original)
            rejected = run_script(script, source.parent, '--apply')
            self.assertNotEqual(0, rejected.returncode)
            self.assertEqual(original, source.read_bytes())
            accepted = run_script(script, source.parent, '--apply', '--term', 'Hilbert - Schmidt')
            self.assertEqual(0, accepted.returncode, accepted.stderr)
            self.assertEqual(original.replace(b'Hilbert - Schmidt', b'Hilbert-Schmidt', 1), source.read_bytes())

    def test_math_clusters_do_not_erase_font_or_count_display_twice(self):
        module = load_script(FIDELITY / 'math_cluster_audit.py')
        self.assertEqual(['a', 'b'], module.extract_math('$$a$$ prose $$b$$'))
        self.assertNotEqual(module.normalize(r'\mathfrak{p}'), module.normalize(r'\mathrm{p}'))
        self.assertNotEqual(module.normalize(r'\Q'), module.normalize(r'\mathbb{Q}'))


class NumberEvidenceTests(unittest.TestCase):
    def test_three_component_number_is_not_a_two_component_reference(self):
        module = load_script(HARDREF / 'convert_hardrefs.py')
        self.assertIsNone(module.RE_THM.search('定理 1.2.3'))
        self.assertIsNone(module.RE_THM.search('引理 1.23.4'))
        self.assertEqual('1.23', module.RE_THM.search('定理 1.23 成立').group(2))

    def test_single_extraction_is_not_strong_conflict_and_layer_only_is_included(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data = {
                '_orig_struct.json': {'sections': [{'key': 'I.1', 'tags': [{'num': '3'}]}]},
                '_mineru_eqseq.json': [],
                '_ours_eqseq.json': [{'chap': 'I', 'sec': 1, 'num': '2'}],
                '_textlayer_eqseq.json': [{'key': 'I.2', 'max': 4}],
            }
            for name, value in data.items():
                (root / name).write_text(json.dumps(value), encoding='utf-8')
            script = ROOT / 'skills/latex-eq-numbering-audit/scripts/triangulate_eqnums.py'
            result = run_script(script, environment={'AIMATH_PROJECT_ROOT': directory, 'PYTHONIOENCODING': 'utf-8'})
            self.assertEqual(0, result.returncode, result.stderr)
            rows = json.loads((root / '_eq_triangulate.json').read_text(encoding='utf-8'))
            self.assertEqual({'I.1', 'I.2'}, {row['key'] for row in rows})
            self.assertNotIn('CONFLICT', [row['verdict'] for row in rows])
            data['_mineru_eqseq.json'] = [{'key': 'I.1', 'tags': ['3']}]
            (root / '_mineru_eqseq.json').write_text(json.dumps(data['_mineru_eqseq.json']), encoding='utf-8')
            result = run_script(script, environment={'AIMATH_PROJECT_ROOT': directory, 'PYTHONIOENCODING': 'utf-8'})
            self.assertEqual(0, result.returncode, result.stderr)
            rows = json.loads((root / '_eq_triangulate.json').read_text(encoding='utf-8'))
            self.assertEqual('CONFLICT', next(row['verdict'] for row in rows if row['key'] == 'I.1'))


if __name__ == '__main__':
    unittest.main()
