"""Generator regression checks: count uniqueness, file safety and real SCAD geometry."""
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from encoder_scad import EncoderDimensions, encoder_metrics, max_even_count

OPENSCAD=os.environ.get('OPENSCAD') or shutil.which('openscad')
if not OPENSCAD:
    app='/Applications/OpenSCAD-2021.01.app/Contents/MacOS/OpenSCAD'
    OPENSCAD=app if Path(app).exists() else None


class EncoderSizingTests(unittest.TestCase):
    def dimensions(self,diameter=70):
        holes=tuple((31.5*math.cos(math.radians(a)),31.5*math.sin(math.radians(a)))
                    for a in range(39,399,60))
        return EncoderDimensions(diameter,40,52,7,9,9.5,11.5,11,holes)

    def test_current_assembly_matches_agreed_stack(self):
        m=encoder_metrics(self.dimensions())
        self.assertEqual((m['inner_magnet_count'],m['outer_magnet_count']),(24,26))
        self.assertAlmostEqual(m['inner_track_r'],23.5)
        self.assertAlmostEqual(m['outer_track_r'],29.5)
        self.assertAlmostEqual(m['bearing_bottom_z'],3)
        self.assertAlmostEqual(m['separator_base_z'],-8.5)
        self.assertAlmostEqual(m['separator_top_z'],10)
        self.assertAlmostEqual(m['glue_face_z'],15.25)
        self.assertAlmostEqual(m['clamp_face_z'],14.85)
        self.assertAlmostEqual(m['connector_stem_h'],6.75)
        self.assertAlmostEqual(m['sensor_angle'],9)
        self.assertAlmostEqual(m['clamp_body_h'],11.6)
        self.assertAlmostEqual(m['magnet_ring_thickness'],.8)

    def test_largest_feasible_pair_at_multiple_diameters(self):
        for diameter in [70,75,80,90]:
            with self.subTest(diameter=diameter):
                m=encoder_metrics(self.dimensions(diameter))
                counts=[m['inner_magnet_count'],m['outer_magnet_count']]
                radii=[m['inner_track_r'],m['outer_track_r']]
                self.assertEqual(counts[1]-counts[0],2)
                self.assertEqual(math.gcd(counts[0]//2,counts[1]//2),1)
                for r,n in zip(radii,counts):
                    self.assertEqual(n%2,0)
                    self.assertGreaterEqual(2*r*math.sin(math.pi/n),5.8)
                # Increasing both rings by one pole pair must violate a pocket web.
                self.assertTrue(any(2*r*math.sin(math.pi/(n+2))<5.8 for r,n in zip(radii,counts)))

    def test_small_clamp_cannot_silently_accept_magnets(self):
        with self.assertRaises(ValueError):
            encoder_metrics(self.dimensions(60))
        self.assertEqual(max_even_count(1,5.8),0)


class GeneratorIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory(prefix='vptc-encoder-test-')
        cls.work=Path(cls.tmp.name)
        cls.models={}
        for diameter in [70,80]:
            path=cls.work/f'gear{diameter}.scad'
            result=cls.generate(path,diameter)
            if result.returncode:
                raise RuntimeError(result.stdout+result.stderr)
            cls.models[diameter]=path

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    @classmethod
    def generate(cls,path,diameter=70,extra=()):
        return subprocess.run([sys.executable,str(ROOT/'calc-vpts.py'),
            '--resolution','600','--ratio','19','--roller-d','4','--roller-h','5',
            '--rout','28','--diameter',str(diameter),'--part','encoder_assembly',
            '--output',str(path),*extra],capture_output=True,text=True,timeout=30,cwd=ROOT)

    def test_existing_files_are_protected(self):
        path=self.work/'manual.scad'
        original='// user saved model\n'
        path.write_text(original)
        result=self.generate(path)
        self.assertNotEqual(result.returncode,0)
        self.assertEqual(path.read_text(),original)
        self.assertFalse(path.with_suffix('.encoder.json').exists())

    def test_manifests_match_board_compatibility(self):
        current=json.loads(self.models[70].with_suffix('.encoder.json').read_text())
        larger=json.loads(self.models[80].with_suffix('.encoder.json').read_text())
        self.assertTrue(current['native_pcb_compatible'])
        self.assertFalse(larger['native_pcb_compatible'])
        carrier=current['magnet_carrier']
        self.assertEqual((carrier['rings'],carrier['ring_halves']),(1,2))
        self.assertEqual(carrier['through_holes_per_half'],25)
        self.assertEqual(carrier['through_holes'],50)
        self.assertAlmostEqual(current['pcb']['local_inner_relief_r_mm'],21.3)
        self.assertEqual(current['pcb']['mcu_relief']['body_size_mm'],[5.1,5.1,.6])
        self.assertAlmostEqual(current['pcb']['mcu_relief']['bottom_z_mm'],10.25)
        self.assertAlmostEqual(current['pcb']['mcu_relief']['center_r_mm'],math.hypot(28.65,-.6),places=5)
        self.assertEqual(current['native_components']['revision'],'V2')
        self.assertEqual(current['pcb']['span_deg'],80)
        mount_points=[(26.92,-9.605),(29.5*math.cos(math.radians(19))+.3,29.5*math.sin(math.radians(19)))]
        expected_angles=sorted(9+math.degrees(math.atan2(y,x)) for x,y in mount_points)
        for actual,expected in zip(sorted(current['pcb']['mount_angles_deg']),expected_angles):
            self.assertAlmostEqual(actual,expected,places=5)
        self.assertEqual((larger['derived']['inner_magnet_count'],larger['derived']['outer_magnet_count']),(30,32))
        instructions=(self.models[80].parent/(self.models[80].stem+'_print')/'README.md').read_text()
        self.assertIn('30 внутренних и 32 наружных',instructions)
        self.assertIn('внутреннего ряда — противоположна',instructions)
        self.assertIn('внешнего ряда — та же',instructions)

    def test_explicit_hole_phase_is_honoured(self):
        path=self.work/'phase.scad'
        result=self.generate(path,extra=['--hole-angle','9'])
        self.assertEqual(result.returncode,0,result.stderr)
        data=json.loads(path.with_suffix('.encoder.json').read_text())
        self.assertFalse(data['native_pcb_compatible'])
        angles=[math.degrees(math.atan2(y,x))%60 for x,y in data['dimensions']['holes']]
        self.assertTrue(all(abs(a-9)<1e-7 for a in angles))

    @unittest.skipUnless(OPENSCAD,'OpenSCAD CLI is not installed')
    def test_all_new_variants_compile_at_two_diameters(self):
        parts=['encoder_assembly','encoder_exploded','encoder_section','encoder_cap',
               'encoder_lid','encoder_print','encoder_clamp','encoder_clamp_half',
               'encoder_magnet_ring','encoder_clamp_print',
               'encoder_connector','encoder_load_connector','encoder_pcb']
        for diameter,model in self.models.items():
            for part in parts:
                with self.subTest(diameter=diameter,part=part):
                    result=subprocess.run([OPENSCAD,'-o',str(self.work/f'{diameter}_{part}.csg'),
                        '-D',f'generated_part="{part}"',str(model)],capture_output=True,text=True,timeout=30)
                    self.assertEqual(result.returncode,0,result.stderr)
                    self.assertNotIn('WARNING:',result.stderr)
                    self.assertNotIn('ERROR:',result.stderr)

    @unittest.skipUnless(OPENSCAD,'OpenSCAD CLI is not installed')
    def test_motor_adapter_holes_leave_solid_webs(self):
        # Probe the actual solids: both mating parts need four diagonal bores,
        # and material must remain between them and the motor mounting bores.
        models=[self.models[70],self.models[80],ROOT/'docs/parts/reference_model.scad']
        probes={
            'cover_holes': ('motor_cover();',
                'for(a=[45:90:315]) rotate(a) translate([12,0,-.9]) cylinder(r=1.3,h=4.8,$fn=16);', True),
            'adapter_holes': ('encoder_adapter();',
                'for(a=[45:90:315]) rotate(a) translate([12,0,.1]) cylinder(r=1.3,h=3,$fn=16);', True),
            'cover_webs': ('motor_cover();',
                'for(x=[-1,1],y=[-1,1]) translate([x*(8+12/sqrt(2))/2,y*6/sqrt(2),2.2]) cylinder(r=.15,h=1,$fn=16);', False),
        }
        for index,model in enumerate(models):
            for name,(part,probe,empty) in probes.items():
                with self.subTest(model=model,name=name):
                    source=self.work/f'motor_{index}_{name}.scad'
                    source.write_text(f'use <{model}>\nintersection(){{ {part} union(){{ {probe} }} }}\n')
                    stl=source.with_suffix('.stl')
                    run=subprocess.run([OPENSCAD,'-o',str(stl),str(source)],capture_output=True,text=True,timeout=90)
                    self.assertNotIn('WARNING:',run.stderr)
                    self.assertNotIn('ERROR:',run.stderr)
                    self.assertEqual(run.returncode,1 if empty else 0,run.stderr)
                    if empty:
                        self.assertIn('Current top level object is empty.',run.stderr)
                    else:
                        vertices=re.findall(r'vertex\s+([-\d.eE+]+)\s+([-\d.eE+]+)\s+([-\d.eE+]+)',stl.read_text())
                        self.assertTrue(vertices)
                        self.assertEqual({(float(x)>0,float(y)>0) for x,y,z in vertices},
                                         {(False,False),(False,True),(True,False),(True,True)})

    @unittest.skipUnless(OPENSCAD,'OpenSCAD CLI is not installed')
    def test_base_parts_remain_available(self):
        parts=['rigid_gear','rigid_gear_with_bracing','separator','reducer_connector',
               'connector_clamp','eccentric','cap','cap_with_bracing','eccentric_shaft',
               'motor_cover','shoulder_horn','shoulder_top','hip','hip_top','foot_connector','shin']
        for part in parts:
            with self.subTest(part=part):
                source=self.work/f'base_{part}.scad'
                source.write_text(f'use <{self.models[70]}>\n{part}();\n')
                result=subprocess.run([OPENSCAD,'-o',str(source.with_suffix('.csg')),str(source)],
                    capture_output=True,text=True,timeout=30)
                self.assertEqual(result.returncode,0,result.stderr)
                self.assertNotIn('WARNING:',result.stderr)
                self.assertNotIn('ERROR:',result.stderr)

    @unittest.skipUnless(OPENSCAD,'OpenSCAD CLI is not installed')
    def test_foot_preview_transform_matches_native_shin_mount(self):
        import importlib.util
        spec=importlib.util.spec_from_file_location('foot_kinematics',ROOT/'output/foot/foot_kinematics.py')
        preview=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(preview)
        native=(ROOT/'output/vptc_roller.scad').read_text()
        shin=native.split('module shin(foot=true){',1)[1].split('module foot_connector()',1)[0]
        mount=re.search(r'(translate\(\[[-\d.,]+\]\)\s*rotate\(\[[-\d.,]+\]\))foot_connector\(\);',shin)
        self.assertIsNotNone(mount)
        point=(101,13,7)  # Nonzero Y and Z distinguish the two 180-degree rotations.
        source=self.work/'native_foot_mount_probe.scad'
        source.write_text(mount.group(1)+f'translate({list(point)}) cube([.2,.2,.2],center=true);\n')
        result=subprocess.run([OPENSCAD,'-o',str(source.with_suffix('.stl')),str(source)],
            capture_output=True,text=True,timeout=30)
        self.assertEqual(result.returncode,0,result.stderr)
        vertices=[tuple(map(float,v)) for v in re.findall(
            r'vertex\s+([-\d.eE+]+)\s+([-\d.eE+]+)\s+([-\d.eE+]+)',source.with_suffix('.stl').read_text())]
        center=tuple((min(v[i] for v in vertices)+max(v[i] for v in vertices))/2 for i in range(3))
        for actual,expected in zip(center,preview.connector_point_to_shin(point)):
            self.assertAlmostEqual(actual,expected,places=5)

    @unittest.skipUnless(OPENSCAD,'OpenSCAD CLI is not installed')
    def test_native_leg_motion_follows_animation_time(self):
        angles=[]
        for t in [0,.5,1]:
            result=subprocess.run([OPENSCAD,'-o',str(self.work/f'leg_time_{t}.csg'),
                '-D',f'$t={t}',str(ROOT/'output/foot/leg_motion.scad')],
                capture_output=True,text=True,timeout=30)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertNotIn('WARNING:',result.stderr)
            self.assertNotIn('ERROR:',result.stderr)
            angle=re.search(r'Угол колена: ", ([-\d.]+)',result.stderr)
            self.assertIsNotNone(angle,result.stderr)
            angles.append(float(angle.group(1)))
        self.assertLess(angles[0],angles[1])
        self.assertLess(angles[1],angles[2])
        self.assertAlmostEqual(angles[1],5.656194,places=4)

    @unittest.skipUnless(OPENSCAD,'OpenSCAD CLI is not installed')
    def test_real_bearing_stop_and_blind_counterbore_depth(self):
        # Independent thin probes intersect the generated cap. The bearing stop
        # must start at Z10; the M3 counterbore must end at its unchanged floor Z9.
        probes=[('bearing_stop',[25,0],10,11),
                ('counterbore_floor',[(31.5+2.5)*math.cos(math.radians(39)),
                                     (31.5+2.5)*math.sin(math.radians(39))],0,9)]
        for name,xy,zmin,zmax in probes:
            source=self.work/f'{name}.scad'
            source.write_text(f'use <{self.models[70]}>\nintersection() {{ cap(); '
                f'translate([{xy[0]},{xy[1]},-0.1]) cylinder(r=.05,h=11.2,$fn=12); }}\n')
            stl=source.with_suffix('.stl')
            result=subprocess.run([OPENSCAD,'-o',str(stl),str(source)],capture_output=True,text=True,timeout=60)
            self.assertEqual(result.returncode,0,result.stderr)
            values=[float(z) for z in re.findall(r'vertex\s+[-\d.eE+]+\s+[-\d.eE+]+\s+([-\d.eE+]+)',stl.read_text())]
            self.assertTrue(values,name)
            self.assertAlmostEqual(min(values),zmin,places=5)
            self.assertAlmostEqual(max(values),zmax,places=5)

    @unittest.skipUnless(OPENSCAD,'OpenSCAD CLI is not installed')
    def test_lid_prints_hall_windows_directly_from_bed(self):
        # Sample the two real windows after turning the lid over for printing.
        # They must be the first 0.4 mm on the bed, with cavities open upward.
        source=self.work/'lid_bed_windows.scad'
        source.write_text(f'use <{self.models[70]}>\n'
            'intersection() { encoder_lid_for_print(); union() {'
            'for(r=[23.5,29.5]) translate([r*cos(9),-r*sin(9),-.1]) '
            'cylinder(r=.02,h=2.1,$fn=8); } }\n')
        result=subprocess.run([OPENSCAD,'-o',str(source.with_suffix('.stl')),str(source)],
            capture_output=True,text=True,timeout=90)
        self.assertEqual(result.returncode,0,result.stderr)
        values=[float(z) for z in re.findall(r'vertex\s+[-\d.eE+]+\s+[-\d.eE+]+\s+([-\d.eE+]+)',
            source.with_suffix('.stl').read_text())]
        self.assertTrue(values)
        self.assertAlmostEqual(min(values),0,places=5)
        self.assertAlmostEqual(max(values),.4,places=5)

    @unittest.skipUnless(OPENSCAD,'OpenSCAD CLI is not installed')
    def test_mcu_relief_preserves_its_floor_and_bearing_stop(self):
        # The new shallow MCU relief cuts only the top of the outer wall.
        # One probe crosses the actual V2 MCU pocket; another crosses the bearing lip.
        manifest=json.loads(self.models[70].with_suffix('.encoder.json').read_text())
        relief=manifest['pcb']['mcu_relief']
        # Probe the actual pocket centre outside the R27.08 underside counterbore.
        probe_r=relief['center_r_mm']
        probe_a=math.radians(relief['center_angle_deg'])
        mcu_probe=[probe_r*math.cos(probe_a),probe_r*math.sin(probe_a)]
        for name,xy,zmin,zmax in [('mcu_relief_floor',mcu_probe,0,10.25),
                                  ('encoder_bearing_stop',[25,0],10,10.75)]:
            source=self.work/f'{name}.scad'
            source.write_text(f'use <{self.models[70]}>\nintersection() {{ cap_encoder(with_bracing=false); '
                f'translate([{xy[0]},{xy[1]},-0.1]) cylinder(r=.02,h=11.2,$fn=12); }}\n')
            stl=source.with_suffix('.stl')
            result=subprocess.run([OPENSCAD,'-o',str(stl),str(source)],capture_output=True,text=True,timeout=90)
            self.assertEqual(result.returncode,0,result.stderr)
            values=[float(z) for z in re.findall(r'vertex\s+[-\d.eE+]+\s+[-\d.eE+]+\s+([-\d.eE+]+)',stl.read_text())]
            self.assertTrue(values,name)
            self.assertAlmostEqual(min(values),zmin,places=5)
            self.assertAlmostEqual(max(values),zmax,places=5)


if __name__=='__main__':
    unittest.main()
