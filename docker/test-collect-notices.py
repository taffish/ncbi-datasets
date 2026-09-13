#!/usr/bin/env python3
"""告知来源、清单漏项、损坏和路径安全的独立负向测试。"""
import base64
import copy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).parent
spec = importlib.util.spec_from_file_location('collector',ROOT/'collect-notices.py')
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)


class Notices(unittest.TestCase):
    def setUp(self):
        self.lock = json.loads((ROOT/'notices.lock.json').read_text())

    def test_public_source_matches(self):
        c.validate_lock(self.lock,ROOT/'public-source')

    def test_removed_module_rejected(self):
        self.lock['modules'].pop()
        with self.assertRaisesRegex(ValueError,'inventory'):
            c.validate_lock(self.lock,ROOT/'public-source')

    def test_duplicate_module_rejected(self):
        self.lock['modules'].append(copy.deepcopy(self.lock['modules'][0]))
        with self.assertRaisesRegex(ValueError,'inventory'):
            c.validate_lock(self.lock,ROOT/'public-source')

    def test_changed_version_rejected(self):
        self.lock['modules'][0]['source_version']='v99.0.0'
        with self.assertRaisesRegex(ValueError,'inventory'):
            c.validate_lock(self.lock,ROOT/'public-source')

    def test_false_complete_rejected(self):
        self.lock['binary_sbom_complete']=True
        with self.assertRaisesRegex(ValueError,'cannot claim'):
            c.validate_lock(self.lock,ROOT/'public-source')

    def test_dataformat_provider_removed(self):
        self.lock['dataformat_notice_references'].pop()
        with self.assertRaisesRegex(ValueError,'provider inventory'):
            c.validate_lock(self.lock,ROOT/'public-source')

    def test_dataformat_provider_duplicated(self):
        self.lock['dataformat_notice_references'][0]=self.lock['dataformat_notice_references'][1]
        with self.assertRaisesRegex(ValueError,'provider inventory'):
            c.validate_lock(self.lock,ROOT/'public-source')

    def test_no_invented_runtime_version(self):
        self.lock['dataformat_notice_references'][0]['runtime_version']='v1.14.6'
        with self.assertRaisesRegex(ValueError,'linked runtime version'):
            c.validate_lock(self.lock,ROOT/'public-source')

    def test_history_required(self):
        self.lock['dataformat_notice_references'][0]['license_history']=[]
        with self.assertRaisesRegex(ValueError,'history'):
            c.validate_lock(self.lock,ROOT/'public-source')

    def test_reference_only_not_allowed_for_unreviewed_license(self):
        self.lock['dataformat_notice_references'][0]['license_family']='GPL-3.0'
        with self.assertRaisesRegex(ValueError,'unreviewed license'):
            c.validate_lock(self.lock,ROOT/'public-source')

    def test_both_base_recipe_sources_required(self):
        self.lock['base_sources']=[x for x in self.lock['base_sources'] if 'arm64' not in x['archive']]
        with self.assertRaisesRegex(ValueError,'base source inventory'):
            c.validate_lock(self.lock,ROOT/'public-source')

    def test_copyright_fragments_keep_original_terms(self):
        files={'a.go':b'// Copyright Alice\n// Permission text\npackage a\n',
               'b.c':b'/* Copyright Bob\n * Terms here\n */\nint main() {}'}
        out=c.copyright_fragments(files).decode()
        self.assertIn('// Copyright Alice\n// Permission text\n',out)
        self.assertIn('/* Copyright Bob\n * Terms here\n */',out)

    def test_wrong_sum_rejected(self):
        self.lock['modules'][0]['go_sum']='h1:wrong'
        with self.assertRaisesRegex(ValueError,'go.sum'):
            c.validate_lock(self.lock,ROOT/'public-source')

    def test_changed_source_hash_rejected(self):
        self.lock['public_go_mod_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'source lock changed'):
            c.validate_lock(self.lock,ROOT/'public-source')

    def test_path_traversal(self):
        for name in ['../bad','/absolute','a/../../b','a\\b','a\nb']:
            with self.subTest(name=name), self.assertRaises(ValueError):
                c.safe_name(name)

    def test_notice_recognition(self):
        for name in ['LICENSE','a/LICENSE.txt','COPYING.LIB','NOTICE','PATENTS','COPYRIGHT','AUTHORS.md']:
            self.assertTrue(c.notice_name(name))
        self.assertFalse(c.notice_name('unrelated.go'))

    def test_good_zip(self):
        buf = io.BytesIO()
        name = 'example.org/a@v1.0.0/LICENSE'
        with zipfile.ZipFile(buf,'w') as z:
            z.writestr(name,b'license example\n')
        h = hashlib.sha256(b'license example\n').hexdigest()
        h1='h1:'+base64.b64encode(hashlib.sha256(f'{h}  {name}\n'.encode()).digest()).decode()
        self.assertEqual(c.zip_contents(buf.getvalue(),'example.org/a','v1.0.0',h1)[name],b'license example\n')

    def test_bad_zip_sum(self):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf,'w') as z:
            z.writestr('example.org/a@v1.0.0/LICENSE',b'x')
        with self.assertRaisesRegex(ValueError,'go.sum'):
            c.zip_contents(buf.getvalue(),'example.org/a','v1.0.0','h1:wrong')

    def test_wrong_zip_prefix(self):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf,'w') as z:
            z.writestr('another@v1.0.0/LICENSE',b'x')
        with self.assertRaisesRegex(ValueError,'prefix'):
            c.zip_contents(buf.getvalue(),'example.org/a','v1.0.0','h1:unused')

    def test_existing_output_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileExistsError):
                c.collect(ROOT/'notices.lock.json',ROOT/'public-source',Path(tmp)/'cache',Path(tmp),False)

    def test_missing_cache_refused_offline(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError,'missing cached'):
                c.collect(ROOT/'notices.lock.json',ROOT/'public-source',Path(tmp)/'cache',Path(tmp)/'out',False)

    def test_nonpermitted_module_not_fetched_or_copied(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)/'out'
            with self.assertRaisesRegex(ValueError,'missing cached'):
                c.collect(ROOT/'notices.lock.json',ROOT/'public-source',Path(tmp)/'cache',out,False)
            self.assertIn('included_in_notice_or_source_payload=false',
                          (out/'excluded/bou.ke__monkey.txt').read_text())
            self.assertFalse((out/'sources/bou.ke__monkey@v1.0.2.zip').exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)
