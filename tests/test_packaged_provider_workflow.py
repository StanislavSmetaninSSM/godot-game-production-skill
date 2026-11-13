"""Execute documented commands from an installed skill without a repository wrapper."""

import json
from pathlib import Path
import re
import shlex
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest


SKILL = Path(__file__).resolve().parents[1] / 'godot-game-production'


class PackagedProviderWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.skill = self.root / 'installed skill with spaces'
        shutil.copytree(SKILL, self.skill, ignore=shutil.ignore_patterns('__pycache__'))
        self.project = self.root / 'separate game project'
        self.project.mkdir()
        document = {'asset': {'version': '2.0'}, 'buffers': [{'byteLength': 36}],
                    'bufferViews': [{'buffer': 0, 'byteLength': 36}],
                    'accessors': [{'bufferView': 0, 'componentType': 5126, 'count': 3,
                                   'type': 'VEC3', 'min': [0, 0, 0], 'max': [1, 1, 0]}],
                    'meshes': [{'primitives': [{'attributes': {'POSITION': 0}}]}]}
        data = json.dumps(document).encode('utf-8')
        data += b' ' * (-len(data) % 4)
        vertices = struct.pack('<9f', 0, 0, 0, 1, 0, 0, 0, 1, 0)
        payload = struct.pack('<II', len(data), 0x4E4F534A) + data + struct.pack('<II', len(vertices), 0x004E4942) + vertices
        (self.project / 'my triangle.glb').write_bytes(struct.pack('<4sII', b'glTF', 2, 12 + len(payload)) + payload)

    def commands(self, relative):
        text = (self.skill / relative).read_text(encoding='utf-8')
        commands = re.findall(r'python ([^\n`]+(?:\.py[^\n`]*))', text)
        commands = [command for command in commands if re.search(r'\.py (?:resolve|inspect)\b', command)]
        self.assertTrue(commands, f'No executable workflow commands found in {relative}')
        substitutions = {'<project-root>': self.project.as_posix(), '<runtime-id>': 'kimi',
                         '<portable-relative.glb>': 'my triangle.glb'}
        expanded = []
        for command in commands:
            for placeholder, value in substitutions.items():
                command = command.replace(placeholder, value)
            # Expand before shell tokenization so missing quotes actually split a path.
            expanded.append(shlex.split(command))
        return expanded

    def run_documented(self, args):
        return subprocess.run([sys.executable, '-B', *args], cwd=self.skill, capture_output=True, text=True, timeout=20)

    def test_kimi_runtime_commands_work_in_package(self):
        for command in self.commands('references/runtimes/kimi.md'):
            with self.subTest(command=command):
                result = self.run_documented(command)
                self.assertEqual(0, result.returncode, result.stderr)
                self.assertIn(json.loads(result.stdout)['provider_id'], ('kimi', 'tripo'))

    def test_codex_runtime_commands_preserve_default_rules(self):
        for command in self.commands('references/runtimes/codex.md'):
            with self.subTest(command=command):
                result = self.run_documented(command)
                if command[0].endswith('model_provider.py'):
                    self.assertEqual(2, result.returncode, result.stderr)
                    self.assertEqual('', result.stdout)
                    self.assertIn('default', result.stderr)
                    result = self.run_documented(command + ['--provider', 'tripo'])
                self.assertEqual(0, result.returncode, result.stderr)
                self.assertIn(json.loads(result.stdout)['provider_id'], ('codex', 'tripo'))

    def test_neutral_model_selection_and_inspection_commands_work(self):
        for command in self.commands('references/model-generation.md'):
            with self.subTest(command=command):
                result = self.run_documented(command)
                self.assertEqual(0, result.returncode, result.stderr)
                output = json.loads(result.stdout)
                if command[1] == 'inspect':
                    self.assertEqual('verified', output['triangle_count_status'])
                    self.assertEqual(1, output['triangle_count'])
                else:
                    self.assertEqual('tripo', output['provider_id'])

    def test_production_asset_inspection_command_works_in_package(self):
        for command in self.commands('references/production-assets.md'):
            result = self.run_documented(command)
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual(1, json.loads(result.stdout)['triangle_count'])


if __name__ == '__main__':
    unittest.main()
