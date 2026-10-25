"""Synthetic evidence only; no network, user files or model calls."""
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / '.agents/skills/web-clipper-library-note/scripts/bilingual_transcript_tool.py'
spec = importlib.util.spec_from_file_location('transcript', TOOL)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class TranscriptTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'fixture.md'
        self.source.write_text('# Fixture\n\n' + module.DEFAULT_BODY_MARKER + '\n\n**00:00** · First fact.\n**00:10** · Second fact.\n', encoding='utf-8')
        self.table = self.root / 'translations.tsv'
        self.table.write_text('1\t00:00\tFirst fact.\t第一事实。\n2\t00:10\tSecond fact.\t第二事实。\n', encoding='utf-8')

    def run_tool(self, *args):
        return subprocess.run([sys.executable, '-B', str(TOOL), *map(str, args)], capture_output=True, text=True)

    def test_preview_preserves_source_and_each_evidence(self):
        before = self.source.read_bytes()
        result = self.run_tool('render', self.source, self.table)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.source.read_bytes(), before)
        self.assertEqual(result.stdout.count('First fact.'), 1)
        self.assertEqual(result.stdout.count('Second fact.'), 1)

    def test_changed_evidence_blocks_in_place_without_writes(self):
        self.table.write_text(self.table.read_text().replace('First fact.', 'Changed claim.'))
        before = self.source.read_bytes()
        result = self.run_tool('render', self.source, self.table, '--in-place')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.source.read_bytes(), before)

    def test_missing_translation_blocks_in_place_without_writes(self):
        self.table.write_text('1\t00:00\tFirst fact.\t\n')
        before = self.source.read_bytes()
        result = self.run_tool('render', self.source, self.table, '--in-place')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.source.read_bytes(), before)

    def test_missing_marker_blocks_in_place(self):
        before = self.source.read_bytes()
        result = self.run_tool('render', self.source, self.table, '--in-place', '--marker', 'missing marker')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.source.read_bytes(), before)

    def test_grouped_alignment_preserves_evidence_without_placeholders(self):
        events = [{'timestamp': '00:00', 'chinese': '第一。'}, {'timestamp': '00:05', 'chinese': '承接。'}, {'timestamp': '00:10', 'chinese': '第二。'}]
        evidence = [('00:00', 'First fact.'), ('00:10', 'Second fact.')]
        output = module.render_user_chinese_alignment(events, module.align_evidence_to_chinese(events, evidence), {})
        self.assertEqual(len(module.CN_TIMESTAMP_RE.findall(output)), 3)
        self.assertEqual(len(module.EN_EVIDENCE_RE.findall(output)), 2)
        self.assertNotIn(module.LEGACY_CONNECTIVE_NOTE, output)
        self.assertEqual(module.extract_bilingual_evidence_segments(output), evidence)

    def test_alignment_repeat_keeps_same_body(self):
        cn = self.root / 'cn.txt'
        cn.write_text('[00:00] 第一。\n[00:05] 承接。\n[00:10] 第二。\n')
        first = self.run_tool('align-generated-cn', self.source, cn)
        self.assertEqual(first.returncode, 0, first.stderr)
        self.source.write_text(first.stdout)
        second = self.run_tool('align-generated-cn', self.source, cn)
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(first.stdout, second.stdout)

    def bilingual_note(self, body):
        return ('---\ntitle: fixture\nsource_medium: article\nraw_format: bilingual_transcript\nlanguage: [en, zh]\n'
                'acquisition_method: user_supplied\ncompleteness: user_chinese_transcript_with_grouped_english_evidence_alignment\n'
                'translation_note: "Chinese transcript provided by the user"\n---\n# fixture\n\n' + body)

    def test_audit_accepts_user_provenance_with_grouped_rows(self):
        self.source.write_text(self.bilingual_note('【00:00】一。\n\n**English:** One.\n\n【00:05】承接。\n'))
        result = self.run_tool('audit', self.source)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_audit_rejects_fake_bilingual_metadata(self):
        self.source.write_text(self.bilingual_note('只有中文摘要。\n'))
        self.assertNotEqual(self.run_tool('audit', self.source).returncode, 0)

    def test_audit_rejects_placeholder_evidence(self):
        self.source.write_text(self.bilingual_note('【00:00】一。\n\n**English:** ' + module.LEGACY_CONNECTIVE_NOTE + '\n'))
        self.assertNotEqual(self.run_tool('audit', self.source).returncode, 0)


if __name__ == '__main__':
    unittest.main()
