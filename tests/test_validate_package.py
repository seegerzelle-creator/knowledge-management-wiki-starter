"""Exercise real link validation in disposable copies; no user files or network."""
import hashlib
import importlib.util
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('package_validator', ROOT / 'scripts/validate_package.py')
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class PackageLinkTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'vault'
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        self.probe = self.root / 'Probe.md'

    def test_accepts_dotted_note_name_with_alias(self):
        self.probe.write_text('[[ThinkDesk.example|审批台模板]]\n', encoding='utf-8')
        self.assertEqual(validator.validate(self.root), [])

    def test_accepts_relative_note_name_with_multiple_dots(self):
        folder = self.root / 'notes'
        folder.mkdir()
        (folder / 'meeting.v2.draft.md').write_text('# Meeting\n', encoding='utf-8')
        (folder / 'Probe.md').write_text('[[meeting.v2.draft]]\n', encoding='utf-8')
        self.assertEqual(validator.validate(self.root), [])

    def test_accepts_heading_and_alias_on_dotted_note(self):
        self.probe.write_text('[[ThinkDesk.example#当前待审批|查看模板]]\n', encoding='utf-8')
        self.assertEqual(validator.validate(self.root), [])

    def test_reports_missing_dotted_note(self):
        self.probe.write_text('[[absent.example]]\n', encoding='utf-8')
        self.assertEqual(validator.validate(self.root), ['Probe.md: broken wiki link absent.example'])

    def test_does_not_replace_part_of_the_note_name(self):
        (self.root / 'proposal.md').write_text('# Different note\n', encoding='utf-8')
        self.probe.write_text('[[proposal.v2]]\n', encoding='utf-8')
        self.assertEqual(validator.validate(self.root), ['Probe.md: broken wiki link proposal.v2'])

    def test_accepts_explicit_markdown_extension(self):
        self.probe.write_text('[[ThinkDesk.example.md]]\n', encoding='utf-8')
        self.assertEqual(validator.validate(self.root), [])

    def test_explicit_markdown_extension_does_not_match_double_extension(self):
        (self.root / 'absent.md.md').write_text('# Different note\n', encoding='utf-8')
        self.probe.write_text('[[absent.md]]\n', encoding='utf-8')
        self.assertEqual(validator.validate(self.root), ['Probe.md: broken wiki link absent.md'])

    def test_accepts_exact_attachment_filename(self):
        (self.root / 'record.v2.txt').write_text('attachment fixture\n', encoding='utf-8')
        self.probe.write_text('[[record.v2.txt]]\n', encoding='utf-8')
        self.assertEqual(validator.validate(self.root), [])

    def test_cli_accepts_dotted_note_without_writing_files(self):
        self.probe.write_text('[[ThinkDesk.example]]\n', encoding='utf-8')
        def snapshot():
            return {str(p.relative_to(self.root)): hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in self.root.rglob('*') if p.is_file()}
        before = snapshot()
        result = subprocess.run([sys.executable, '-B', str(self.root / 'scripts/validate_package.py')],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('structural_issues=0', result.stdout)
        self.assertEqual(snapshot(), before)

    def test_cli_rejects_a_missing_target(self):
        self.probe.write_text('[[absent.example]]\n', encoding='utf-8')
        result = subprocess.run([sys.executable, '-B', str(self.root / 'scripts/validate_package.py')],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn('broken wiki link absent.example', result.stdout)


if __name__ == '__main__':
    unittest.main()
