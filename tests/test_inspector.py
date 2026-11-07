import contextlib
import io
import json
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch
import inspector as app

class InspectorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
    def capture(self, **updates):
        meta = dict(schema='qnx-probe-v1', sysname='QNX', release='8.0.0', machine='x86_64',
                    clock_api='clock_gettime_mon_ns', period_ns=100, clock_period_ns=1000, samples=3)
        meta.update(updates)
        path = self.root/'capture.csv'
        path.write_text(json.dumps(meta)+'\nsample,scheduled_ns,actual_ns\n0,100,110\n1,200,230\n2,300,350\n')
        return path
    def test_statistics(self):
        r = app.analyze(self.capture(), 30)
        self.assertEqual(r['lateness_ns'], dict(min=10, median=30, p99=50, max=50))
        self.assertEqual(r['over_budget'], 1)
    def test_wrong_os(self):
        with self.assertRaises(ValueError): app.analyze(self.capture(sysname='Linux'), 1)
    def test_wrong_release(self):
        for version in ('8.01', '7.1.0', '8.0<script>'):
            with self.assertRaises(ValueError): app.analyze(self.capture(release=version), 1)
    def test_truncated(self):
        with self.assertRaises(ValueError): app.analyze(self.capture(samples=4), 1)
    def test_bad_period(self):
        with self.assertRaises(ValueError): app.analyze(self.capture(period_ns=101), 1)
    def test_boolean_sample_count(self):
        with self.assertRaises(ValueError): app.analyze(self.capture(samples=True), 1)
    def test_duplicate_sequence(self):
        p = self.capture(); p.write_text(p.read_text().replace('2,300', '1,300'))
        with self.assertRaises(ValueError): app.analyze(p, 1)
    def test_early_wake(self):
        p = self.capture(); p.write_text(p.read_text().replace('300,350', '300,299'))
        with self.assertRaises(ValueError): app.analyze(p, 1)
    def test_elf(self):
        p = self.root/'elf'; b = bytearray(64); b[:7] = b'\x7fELF\x02\x01\x01'
        struct.pack_into('<HHI', b, 16, 2, 62, 1); p.write_bytes(b)
        self.assertEqual(app.elf_info(p, 'x86_64')['machine'], 62)
        with self.assertRaises(ValueError): app.elf_info(p, 'aarch64')
    def test_non_elf(self):
        p = self.root/'bad'; p.write_bytes(b'x'*64)
        with self.assertRaises(ValueError): app.elf_info(p, 'x86_64')
    def test_html_escape(self):
        app.write_report({'value':'<script>alert(1)</script>'}, self.root)
        self.assertNotIn('<script>', (self.root/'report.html').read_text())
    def test_missing_sdk(self):
        with patch('inspector.shutil.which', return_value=None), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(app.main(['build', '--out', str(self.root)]), 2)
        self.assertFalse(json.loads((self.root/'report.json').read_text())['build_verified'])
    def test_cli_budget_failure(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(app.main(['analyze', str(self.capture()), '--budget-ns', '30', '--out', str(self.root)]), 3)
    def test_compile_failure_not_verified(self):
        env = {'qcc':'qcc', 'ready_for_build_attempt':True}
        with patch('inspector.doctor', return_value=env), patch('inspector.run', return_value={'returncode':1}), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(app.main(['build', '--out', str(self.root)]), 2)
        self.assertFalse(json.loads((self.root/'report.json').read_text())['build_verified'])
    def test_compiler_success_without_binary(self):
        with patch('inspector.doctor', return_value={'qcc':'qcc', 'ready_for_build_attempt':True}), patch('inspector.run', return_value={'returncode':0}), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(app.main(['build', '--out', str(self.root)]), 2)

if __name__ == '__main__': unittest.main()
