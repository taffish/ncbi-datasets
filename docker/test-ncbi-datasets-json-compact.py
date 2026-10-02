#!/usr/bin/env python3
"""词法比较器回归；可用 JSON argv 环境变量验证镜像内同一脚本，不增加 runtime Python。"""
import json
import os
from pathlib import Path
import subprocess
import unittest

COMMAND = json.loads(os.environ.get('NCBI_COMPACT_TEST_COMMAND', 'null')) or [
    'awk', '-f', str(Path(__file__).with_name('ncbi-datasets-json-compact.awk'))]


class Compact(unittest.TestCase):
    def run_compact(self, value, valid=True):
        result = subprocess.run(COMMAND, input=value.encode(), stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, timeout=30,
                                env=dict(os.environ, LC_ALL='C'))
        if valid:
            self.assertEqual(result.returncode, 0, result.stderr.decode(errors='replace'))
        else:
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(b'json-compact:', result.stderr)
        return result.stdout.decode()

    def test_formatting_only(self):
        payload = {'organism': 'synthetic organism', 'tax_id': 9606, 'null': None,
                   'items': [True, False, {}, [], '', 0, -0.1]}
        raw = json.dumps(payload, separators=(',', ':'))
        self.assertEqual(self.run_compact(json.dumps(payload, indent=2)), raw+'\n')
        self.assertEqual(self.run_compact(raw), raw+'\n')

    def test_string_space_corruption_rejected(self):
        raw = '{"name":"synthetic organism"}'
        wrong = '{\n "name": "syntheticorganism"\n}'
        self.assertNotEqual(self.run_compact(raw), self.run_compact(wrong))

    def test_key_space_corruption_rejected(self):
        self.assertNotEqual(self.run_compact('{"a b":1}'), self.run_compact('{"ab":1}'))

    def test_string_edge_spaces_preserved(self):
        for value in [' leading', 'trailing ', '  two  spaces  ', ' ', '']:
            with self.subTest(value=value):
                raw = json.dumps({'name': value}, separators=(',', ':'))
                self.assertEqual(self.run_compact(json.dumps({'name': value}, indent=2)), raw+'\n')

    def test_quotes_backslashes_and_escapes(self):
        values = ['a "quoted value" b', 'a\\" b', 'a\\\\" b', 'end\\', '\t\r\n', '\b\f', '\\n']
        for value in values:
            with self.subTest(value=value):
                raw = json.dumps({'text': value}, separators=(',', ':'))
                self.assertEqual(self.run_compact(json.dumps({'text': value}, indent=2)), raw+'\n')

    def test_escape_corruption_rejected(self):
        for original, changed in [('a\\b', 'ab'), ('a" b', 'a"b'), ('a\tb', 'ab')]:
            with self.subTest(original=original):
                self.assertNotEqual(self.run_compact(json.dumps({'v': original})),
                                    self.run_compact(json.dumps({'v': changed})))

    def test_unicode_bytes_preserved(self):
        raw = json.dumps({'text': '物种 α 🙂'}, ensure_ascii=False, separators=(',', ':'))
        self.assertEqual(self.run_compact(' \r\n\t'+raw+'\r\n'), raw+'\n')
        # 不做 unescape；两种合法编码仍按原字节分别保留。
        escaped = json.dumps({'text': '物种 α 🙂'}, separators=(',', ':'))
        self.assertEqual(self.run_compact(escaped), escaped+'\n')

    def test_jsonl_records(self):
        rows = [{'text': 'one record'}, {'text': 'two " records\\'}]
        raw = '\n'.join(json.dumps(row, separators=(',', ':')) for row in rows)
        pretty = '\n'.join(json.dumps(row, indent=2) for row in rows)
        self.assertEqual(self.run_compact(raw), self.run_compact(pretty))

    def test_unterminated_or_control_string_rejected(self):
        for text in ['{"x":"unfinished', '{"x":"end\\', '{"x":"a\nb"}', '{"x":"a\tb"}']:
            with self.subTest(text=text):
                self.run_compact(text, valid=False)

    def test_empty_input_rejected(self):
        for text in ['', ' \t\r\n']:
            with self.subTest(text=text):
                self.run_compact(text, valid=False)


if __name__ == '__main__':
    unittest.main(verbosity=2)
