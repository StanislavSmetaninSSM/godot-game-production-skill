"""Exercise resolver boundaries through real installed-layout subprocesses."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


SKILL = Path(__file__).resolve().parents[1] / 'godot-game-production'


class ProviderBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.skill = self.root / 'installed skill'
        shutil.copytree(SKILL, self.skill, ignore=shutil.ignore_patterns('__pycache__'))
        self.project = self.root / 'game project'
        self.project.mkdir()

    def run_resolver(self, kind, project=None, override=None):
        args = [sys.executable, '-B', str(self.skill / 'scripts' / f'{kind}_provider.py'),
                'resolve', '--runtime', 'kimi', '--project-root', str(project or self.project)]
        if override:
            args += ['--provider', override]
        return subprocess.run(args, capture_output=True, text=True, timeout=20)

    def register(self, kind, adapter):
        registry = self.skill / ('providers' if kind == 'image' else 'model-providers') / 'registry.json'
        data = json.loads(registry.read_text(encoding='utf-8'))
        data['providers']['custom'] = {'adapter_path': adapter, 'default_for_runtimes': [] if kind == 'model' else ['testhost']}
        registry.write_text(json.dumps(data), encoding='utf-8')

    def assert_schema_failure(self, result):
        self.assertEqual(3, result.returncode, result.stderr)
        self.assertEqual('', result.stdout)
        self.assertTrue(result.stderr.strip())
        self.assertNotIn('Traceback', result.stderr)

    def test_custom_model_id_cannot_select_real_image_adapter(self):
        self.register('model', 'references/providers/kimi.md')
        self.assert_schema_failure(self.run_resolver('model', override='custom'))

    def test_custom_image_id_cannot_select_real_model_adapter(self):
        self.register('image', 'references/model-providers/tripo.md')
        self.assert_schema_failure(self.run_resolver('image', override='custom'))

    def test_model_adapter_without_kind_cannot_be_selected(self):
        (self.skill / 'custom.md').write_text('# untyped adapter\n', encoding='utf-8')
        self.register('model', 'custom.md')
        self.assert_schema_failure(self.run_resolver('model', override='custom'))

    def test_custom_model_adapter_at_arbitrary_safe_path_works(self):
        (self.skill / 'custom.md').write_text('<!-- provider-kind: model -->\n# Custom\n', encoding='utf-8')
        self.register('model', 'custom.md')
        result = self.run_resolver('model', override='custom')
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual('custom.md', json.loads(result.stdout)['adapter_path'])

    def test_legacy_image_adapter_remains_supported(self):
        (self.skill / 'custom.md').write_text('# Legacy adapter\n', encoding='utf-8')
        self.register('image', 'custom.md')
        result = self.run_resolver('image', override='custom')
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual('custom', json.loads(result.stdout)['provider_id'])

    def test_ordinary_html_comment_mention_is_not_a_kind_declaration(self):
        note = '<!-- Maintenance note: provider-kind support is tracked separately. -->\n'
        for kind, prefix in (('image', ''), ('image', '<!-- provider-kind: image -->\n'),
                             ('model', '<!-- provider-kind: model -->\n')):
            with self.subTest(kind=kind, prefix=prefix):
                (self.skill / 'custom.md').write_text(prefix + note + '# Adapter\n', encoding='utf-8')
                self.register(kind, 'custom.md')
                result = self.run_resolver(kind, override='custom')
                self.assertEqual(0, result.returncode, result.stderr)
                self.assertEqual('custom', json.loads(result.stdout)['provider_id'])

    def test_duplicate_kind_is_not_accepted(self):
        for kind in ('image', 'model'):
            with self.subTest(kind=kind):
                (self.skill / 'custom.md').write_text(f'<!-- provider-kind: {kind} -->\n<!-- provider-kind: {kind} -->\n', encoding='utf-8')
                self.register(kind, 'custom.md')
                self.assert_schema_failure(self.run_resolver(kind, override='custom'))

    def test_malformed_kind_is_not_accepted(self):
        for kind in ('image', 'model'):
            with self.subTest(kind=kind):
                (self.skill / 'custom.md').write_text(f'<!-- provider-kind: {kind} trailing -->\n', encoding='utf-8')
                self.register(kind, 'custom.md')
                self.assert_schema_failure(self.run_resolver(kind, override='custom'))

    def test_multiline_or_unterminated_declaration_is_not_legacy_image_metadata(self):
        for text in ('<!--\nprovider-kind: model -->\n',
                     '<!-- provider-kind: image -->\n<!--\nprovider-kind: image -->\n',
                     '<!-- provider-kind: model',
                     '<!-- Provider-Kind: model -->\n'):
            with self.subTest(text=text):
                (self.skill / 'custom.md').write_text(text, encoding='utf-8')
                self.register('image', 'custom.md')
                self.assert_schema_failure(self.run_resolver('image', override='custom'))

    def test_existing_file_in_selection_directory_is_not_absent_configuration(self):
        for ancestor in ('docs', 'docs/visual-contract'):
            project = self.root / ancestor.replace('/', '-')
            project.mkdir()
            path = project / ancestor
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('ordinary file', encoding='utf-8')
            for kind in ('image', 'model'):
                with self.subTest(ancestor=ancestor, kind=kind):
                    self.assert_schema_failure(self.run_resolver(kind, project))

    def test_override_bypasses_bad_persisted_selection_but_requires_real_root(self):
        (self.project / 'docs').write_text('ordinary file', encoding='utf-8')
        for kind, provider in (('image', 'kimi'), ('model', 'tripo')):
            with self.subTest(kind=kind):
                result = self.run_resolver(kind, override=provider)
                self.assertEqual(0, result.returncode, result.stderr)
                self.assertEqual('override', json.loads(result.stdout)['source'])
                self.assert_schema_failure(self.run_resolver(kind, self.root / 'absent', provider))

    @unittest.skipUnless(sys.platform == 'win32', 'Windows junction regression')
    def test_root_junction_rejected_with_and_without_override(self):
        junction = self.root / 'junction'
        result = subprocess.run(['powershell.exe', '-NoProfile', '-Command',
                                 'New-Item -ItemType Junction -Path $env:EJA_TEST_LINK -Target $env:EJA_TEST_TARGET | Out-Null'],
                                env={**os.environ, 'EJA_TEST_LINK': str(junction), 'EJA_TEST_TARGET': str(self.project)},
                                capture_output=True, text=True, timeout=20)
        # Do not silently skip a failed platform setup: this test must exercise a real junction.
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertTrue(junction.exists(), result.stderr)
        self.addCleanup(os.rmdir, junction)
        for kind, provider in (('image', 'kimi'), ('model', 'tripo')):
            for override in (None, provider):
                with self.subTest(kind=kind, override=override):
                    self.assert_schema_failure(self.run_resolver(kind, junction, override))

    @unittest.skipUnless(sys.platform == 'win32', 'Windows junction regression')
    def test_dangling_selection_junction_is_unsafe_not_absent(self):
        junction = self.project / 'docs'
        target = self.root / 'junction-target'
        target.mkdir()
        result = subprocess.run(['powershell.exe', '-NoProfile', '-Command',
                                 'New-Item -ItemType Junction -Path $env:EJA_TEST_LINK -Target $env:EJA_TEST_TARGET | Out-Null'],
                                env={**os.environ, 'EJA_TEST_LINK': str(junction), 'EJA_TEST_TARGET': str(target)},
                                capture_output=True, text=True, timeout=20)
        self.assertEqual(0, result.returncode, result.stderr)
        self.addCleanup(os.rmdir, junction)
        self.assertTrue(junction.exists())
        target.rmdir()
        self.assertFalse(junction.exists())
        for kind, provider in (('image', 'kimi'), ('model', 'tripo')):
            with self.subTest(kind=kind):
                self.assert_schema_failure(self.run_resolver(kind))
                result = self.run_resolver(kind, override=provider)
                self.assertEqual(0, result.returncode, result.stderr)
                self.assertEqual('override', json.loads(result.stdout)['source'])


if __name__ == '__main__':
    unittest.main()
