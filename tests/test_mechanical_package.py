"""The main entry point must reproduce a portable, complete CAD package."""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
OPENSCAD = os.environ.get('OPENSCAD') or shutil.which('openscad')
if not OPENSCAD:
    app = Path('/Applications/OpenSCAD-2021.01.app/Contents/MacOS/OpenSCAD')
    OPENSCAD = str(app) if app.exists() else None


class MechanicalPackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix='vptc-package-')
        cls.work = Path(cls.tmp.name)
        cls.source = cls.work / 'source'
        cls.source.mkdir()
        # Deliberately omit output/: no saved model or STL is a generator input.
        for name in ['calc-vpts.py', 'encoder_scad.py', 'mechanical_package.py']:
            shutil.copy2(ROOT / name, cls.source / name)
        shutil.copytree(ROOT / 'cad', cls.source / 'cad')
        board = cls.source / 'electronics/encoder_can_v2'
        (board / 'design').mkdir(parents=True)
        for name in ['encoder_can_v2.kicad_pcb', 'design/mechanics_v2.json',
                     'design/component_envelopes_v2.json']:
            shutil.copy2(ROOT / 'electronics/encoder_can_v2' / name, board / name)
        initial = cls.work / 'initial/robot.scad'
        run = cls.generate(initial)
        if run.returncode:
            raise RuntimeError(run.stdout + run.stderr)
        cls.package = cls.work / 'portable'
        shutil.move(str(initial.parent), cls.package)
        cls.model = cls.package / 'robot.scad'
        cls.manifest = json.loads(cls.model.with_suffix('.encoder.json').read_text())

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    @classmethod
    def generate(cls, path, diameter=70, part='knee_assembly', extra=()):
        return subprocess.run([sys.executable, str(cls.source / 'calc-vpts.py'),
            '--resolution', '600', '--ratio', '19', '--roller-d', '4',
            '--roller-h', '5', '--rout', '28', '--diameter', str(diameter),
            '--part', part, '--output', str(path), *extra],
            capture_output=True, text=True, timeout=120, cwd=cls.work)

    def scad(self, source, output, *definitions):
        run = subprocess.run([OPENSCAD, '-o', str(output), *definitions, str(source)],
                             capture_output=True, text=True, timeout=60, cwd=self.work)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertNotIn('ERROR:', run.stderr)
        self.assertNotIn('WARNING:', run.stderr)
        return run.stderr

    def test_package_has_all_current_mechanical_parts(self):
        catalog = self.manifest['print_package']
        parts = {part['name']: part for part in catalog['parts']}
        required = {'encoder_cap', 'encoder_lid', 'encoder_connector',
                    'encoder_load_connector', 'encoder_clamp_half',
                    'encoder_magnet_ring_half', 'knee_hip', 'knee_lower',
                    'knee_shin', 'knee_cover', 'knee_magnet_ring', 'foot_rigid',
                    'foot_sole', 'body_front', 'body_rear', 'body_battery',
                    'separator', 'rollers', 'eccentric', 'eccentric_shaft',
                    'motor_cover', 'control_rod', 'shoulder_top', 'shoulder_horn'}
        self.assertTrue(required <= parts.keys(), required - parts.keys())
        for name in ['encoder_clamp_half', 'encoder_magnet_ring_half']:
            self.assertEqual(parts[name]['quantity'], 2)
        self.assertEqual(parts['foot_sole']['material'], 'TPU')
        self.assertTrue(catalog['native_v2_compatible'])
        self.assertEqual(len(catalog['parts']), len(parts))
        self.assertFalse((self.source / 'output').exists())

    @unittest.skipUnless(OPENSCAD, 'OpenSCAD CLI is not installed')
    def test_closed_pcb_cutouts_preserve_reducer_screw_access(self):
        probe=self.work/'pcb_m3_access.scad'
        probe.write_text(f'use <{self.package / "robot_assets/pcb.scad"}>\n'
            'intersection(){ linear_extrude(.8) compact_pcb_outline(); '
            'for(a=[39:60:339]) rotate(a) translate([31.5,0,-.01]) '
            'cylinder(r=3.39,h=.82,$fn=128); }\n')
        run=subprocess.run([OPENSCAD,'-o',str(probe.with_suffix('.stl')),str(probe)],
                           capture_output=True,text=True,timeout=60)
        self.assertEqual(run.returncode,1,run.stderr)
        self.assertIn('Current top level object is empty.',run.stderr)
        self.assertNotIn('ERROR:',run.stderr)
        self.assertNotIn('WARNING:',run.stderr)

    def test_all_references_and_hashes_are_portable(self):
        for path in self.package.rglob('*.scad'):
            source = path.read_text()
            self.assertNotRegex(source, r'\bimport\s*\(')
            for ref in re.findall(r'^\s*(?:use|include)\s*<([^>]+)>', source, re.M):
                target = (path.parent / ref).resolve()
                self.assertTrue(target.is_relative_to(self.package.resolve()), (path, ref))
                self.assertTrue(target.is_file(), (path, ref))
        for name, digest in self.manifest['print_package']['generated_files_sha256'].items():
            self.assertEqual(hashlib.sha256((self.package / name).read_bytes()).hexdigest(), digest)

    def test_existing_asset_prevents_partial_overwrite(self):
        output = self.work / 'protected/robot.scad'
        asset = output.parent / 'robot_assets/base.scad'
        asset.parent.mkdir(parents=True)
        asset.write_text('// manual changes\n')
        run = self.generate(output)
        self.assertNotEqual(run.returncode, 0)
        self.assertFalse(output.exists())
        self.assertFalse(output.with_suffix('.encoder.json').exists())
        self.assertEqual(asset.read_text(), '// manual changes\n')

    def test_small_legacy_reducer_remains_available(self):
        output = self.work / 'small/robot.scad'
        run = self.generate(output, diameter=60, part='legacy')
        self.assertEqual(run.returncode, 0, run.stderr)
        manifest = json.loads(output.with_suffix('.encoder.json').read_text())
        self.assertFalse(manifest['available'])
        self.assertFalse(any(p['name'].startswith(('encoder_cap', 'knee_'))
                             for p in manifest['print_package']['parts']))
        if OPENSCAD:
            self.scad(output, output.with_suffix('.csg'))

    @unittest.skipUnless(OPENSCAD, 'OpenSCAD is not installed')
    def test_all_print_jobs_compile_after_package_move(self):
        for part in self.manifest['print_package']['parts']:
            with self.subTest(part=part['name']):
                source = self.package / part['file']
                self.scad(source, source.with_suffix('.csg'))
        for name in ['reducer_complete', 'leg_assembly', 'knee_assembly',
                     'knee_section', 'knee_exploded', 'knee_mount', 'knee_stage']:
            with self.subTest(scene=name):
                self.scad(self.model, self.work / (name + '.csg'),
                          '-D', f'generated_part="{name}"')

    @unittest.skipUnless(OPENSCAD, 'OpenSCAD is not installed')
    def test_knee_animation_and_manual_angle(self):
        def geometry(time, animate, angle=0):
            path = self.work / 'pose.scad'
            path.write_text(f'use <{self.model}>\n'
                'generated_selected_part("knee_mount",'
                f'time={time},animate={str(animate).lower()},knee_angle={angle});\n')
            self.scad(path, path.with_suffix('.csg'))
            return path.with_suffix('.csg').read_text()
        self.assertEqual(geometry(0, False, 12), geometry(.27, False, 12))
        self.assertEqual(geometry(0, True, 12), geometry(0, False, 12))
        self.assertNotEqual(geometry(0, True), geometry(.27, True))
        self.assertEqual(geometry(.27, True), geometry(0, False, 54.18347799075))

    @unittest.skipUnless(OPENSCAD, 'OpenSCAD is not installed')
    def test_complete_leg_uses_same_angle_and_closed_linkage(self):
        path = self.work / 'linkage.scad'
        path.write_text(f'use <{self.model}>\n'
            'for(i=[0:200]) let(t=i/200,k=package_knee_angle(t),s=package_servo_angle(k),'
            'r=calculate_rigid_linkage(s,184,31,37,[0,0,0],[-13,184,0]))'
            'echo(sample=[k,get_value(r,"angle2"),norm(get_value(r,"point1")-get_value(r,"point2"))]);'
            'cube(.1);')
        log = self.scad(path, path.with_suffix('.csg'))
        rows = [json.loads(row) for row in re.findall(r'ECHO: sample = (.+)', log)]
        self.assertEqual(len(rows), 201)
        for desired, actual, length in rows:
            self.assertGreaterEqual(desired, -44.6459)
            self.assertLessEqual(desired, 54.2041)
            self.assertAlmostEqual(desired, actual, places=4)
            self.assertAlmostEqual(length, 184, places=4)

    @unittest.skipUnless(OPENSCAD, 'OpenSCAD is not installed')
    def test_main_cli_exports_selected_print_job_only(self):
        output = self.work / 'stl/robot.scad'
        run = self.generate(output, extra=['--export-stl', '--stl-part',
                            'foot_rigid', '--openscad', OPENSCAD])
        self.assertEqual(run.returncode, 0, run.stderr)
        exports = list(output.parent.rglob('*.stl'))
        self.assertEqual([p.stem for p in exports], ['foot_rigid'])
        data = exports[0].read_bytes()
        triangles = struct.unpack_from('<I', data, 80)[0]
        self.assertGreater(triangles, 0)
        self.assertEqual(len(data), 84 + 50 * triangles)
        # Regression: float32 export of the curved foot used to leave collapsed
        # triangles and an edge shared by four faces. Check actual exported data.
        import numpy as np
        dtype = np.dtype([('normal', '<f4', (3,)), ('vertices', '<f4', (3, 3)), ('attr', '<u2')])
        vertices = np.frombuffer(data, dtype=dtype, offset=84)['vertices']
        _, inverse = np.unique(vertices.reshape(-1, 3), axis=0, return_inverse=True)
        faces = inverse.reshape(-1, 3)
        edges = np.concatenate([faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]])
        _, counts = np.unique(np.sort(edges, axis=1), axis=0, return_counts=True)
        self.assertTrue(np.all(counts == 2))

    def test_stale_board_data_cannot_silently_use_legacy_fallback(self):
        board = self.source / 'electronics/encoder_can_v2/encoder_can_v2.kicad_pcb'
        original = board.read_bytes()
        try:
            board.write_bytes(original + b'\n')
            output = self.work / 'stale/robot.scad'
            run = self.generate(output, part='legacy')
            self.assertNotEqual(run.returncode, 0)
            self.assertIn('export_mechanics.py', run.stderr)
            self.assertFalse(output.exists())
        finally:
            board.write_bytes(original)


if __name__ == '__main__':
    unittest.main()
