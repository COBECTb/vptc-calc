"""Native OpenSCAD step targets and the angles actually passed to leg()."""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
OPENSCAD=os.environ.get('OPENSCAD') or shutil.which('openscad')
if not OPENSCAD:
    app=Path('/Applications/OpenSCAD-2021.01.app/Contents/MacOS/OpenSCAD')
    OPENSCAD=str(app) if app.exists() else None


@unittest.skipUnless(OPENSCAD,'OpenSCAD CLI is not installed')
class NativeStepTests(unittest.TestCase):
    def run_scad(self,source,output,*definitions,allow_camera=False):
        run=subprocess.run([OPENSCAD,'-o',str(output),*definitions,str(source)],
                           capture_output=True,text=True,timeout=30)
        self.assertEqual(run.returncode,0,run.stderr)
        warnings=run.stderr.replace('WARNING: Viewall and autocenter disabled in favor of $vp*','') if allow_camera else run.stderr
        self.assertNotIn('WARNING:',warnings)
        self.assertNotIn('ERROR:',run.stderr)
        return run.stderr

    def test_step_tracks_ground_and_closes_cycle(self):
        with tempfile.TemporaryDirectory() as tmp:
            probe=Path(tmp)/'targets.scad'
            probe.write_text(f'use <{ROOT / "output/foot/step_motion.scad"}>\n'
                             'for(i=[0:100])let(t=i/100)\n'
                             ' echo(sample=[t,step_angles(t),step_target(t),step_ball(t),step_body_x(t)]);\n'
                             'cube(.1);\n')
            stderr=self.run_scad(probe,probe.with_suffix('.csg'))
            rows=[json.loads(s) for s in re.findall(r'ECHO: sample = (.+)',stderr)]
            self.assertEqual(len(rows),101)
            for t,angles,target,ball,body_x in rows:
                for actual,expected in zip(ball,target):self.assertAlmostEqual(actual,expected,places=3)
                self.assertAlmostEqual(body_x,-200*t,places=3)
                if t<.6:
                    self.assertAlmostEqual(ball[0]+body_x,-60,places=3)
                    self.assertAlmostEqual(ball[1],20,places=3)
                self.assertGreaterEqual(ball[1],20-.001)
                self.assertGreaterEqual(angles[2],-44.646)
                self.assertLessEqual(angles[2],54.204)
            self.assertEqual(rows[0][1:4],rows[-1][1:4])
            self.assertGreater(rows[0][4],rows[-1][4])
            self.assertAlmostEqual(rows[80][3][1],50,places=3)

    def test_animation_time_reaches_the_native_leg(self):
        poses=[]
        with tempfile.TemporaryDirectory() as tmp:
            for t in [0,.3,.8,1]:
                stderr=self.run_scad(ROOT/'output/foot/step_motion.scad',
                                     Path(tmp)/f'pose_{t}.csg','-D',f'$t={t}','-D','scene="single"')
                match=re.search(r'hip_angle = ([-\d.]+), servo_angle = ([-\d.]+), knee_angle = ([-\d.]+)',stderr)
                self.assertIsNotNone(match,stderr)
                hip,servo,knee=map(float,match.groups())
                native_servo=float(re.search(r'Угол толкателя: ", ([-\d.]+)',stderr)[1])
                native_knee=float(re.search(r'Угол колена: ", ([-\d.]+)',stderr)[1])
                self.assertAlmostEqual(servo,native_servo,places=3)
                self.assertAlmostEqual(knee,native_knee,places=3)
                poses.append((hip,servo,knee))
        self.assertEqual(poses[0],poses[-1])
        self.assertGreater(abs(poses[1][0]-poses[0][0]),5)
        self.assertGreater(poses[2][2]-poses[0][2],10)

    def test_left_pair_and_four_leg_walk_keep_planted_feet_fixed(self):
        with tempfile.TemporaryDirectory() as tmp:
            probe=Path(tmp)/'robot.scad'
            probe.write_text(f'use <{ROOT / "output/foot/step_motion.scad"}>\n'
                'echo(left_ids=robot_leg_ids("left_pair"));\n'
                'for(i=[0:200])let(t=i/200){\n'
                ' echo(supports=[t,robot_support_ids(t)]);\n'
                ' for(id=[0:3])echo(foot=[t,id,robot_joint_angles(t,id),robot_hip_world(t,id),robot_ball_world(t,id)]);\n'
                '}\ncube(.1);\n')
            stderr=self.run_scad(probe,probe.with_suffix('.csg'))
            left=json.loads(re.search(r'ECHO: left_ids = (.+)',stderr)[1])
            self.assertEqual(left,[0,1])
            supports=[json.loads(s) for s in re.findall(r'ECHO: supports = (.+)',stderr)]
            feet=[json.loads(s) for s in re.findall(r'ECHO: foot = (.+)',stderr)]
            self.assertEqual(len(feet),804)
            previous={}
            for t,ids in supports:
                self.assertGreaterEqual(len(ids),3)
                for row in feet[int(round(t*200))*4:int(round(t*200))*4+4]:
                    _,id,angles,hip,ball=row
                    self.assertGreaterEqual(ball[2],20-.001)
                    self.assertLess(hip[1],0) if id<2 else self.assertGreater(hip[1],0)
                    if id in ids:
                        self.assertAlmostEqual(ball[2],20,places=3)
                        if id in previous:
                            for x,y in zip(previous[id],ball):self.assertAlmostEqual(x,y,places=2)
                        previous[id]=ball
                    else:previous.pop(id,None)
            for id in range(4):
                first,last=feet[id],feet[-4+id]
                self.assertAlmostEqual(last[3][0]-first[3][0],-200,places=3)
                self.assertEqual(first[2],last[2])
            self.assertAlmostEqual(feet[1][3][0]-feet[0][3][0],320,places=3)

    def test_each_native_scene_renders_the_expected_legs(self):
        with tempfile.TemporaryDirectory() as tmp:
            for filename,ids in [('step_single.scad',[]),('step_left_pair.scad',[0,1]),('step_quadruped.scad',[0,1,2,3])]:
                stderr=self.run_scad(ROOT/'output/foot'/filename,Path(tmp)/(filename+'.csg'),'-D','$t=.15')
                actual=[int(v) for v in re.findall(r'ECHO: gait_leg = (\d)',stderr)]
                self.assertEqual(actual,ids)
                self.assertEqual(len(re.findall(r'Угол колена: ",',stderr)),len(ids) or 1)

    def test_run_alternates_diagonals_and_has_flight_without_ground_penetration(self):
        with tempfile.TemporaryDirectory() as tmp:
            probe=Path(tmp)/'run.scad'
            probe.write_text(f'use <{ROOT / "output/foot/step_motion.scad"}>\n'
                'for(i=[0:200])let(t=i/200){\n'
                'echo(supports=[t,robot_support_ids(t,"run")]);\n'
                'for(id=[0:3])echo(foot=[t,id,robot_joint_angles(t,id,"run"),robot_hip_world(t,id,"run"),robot_ball_world(t,id,"run")]);\n'
                '}\ncube(.1);\n')
            stderr=self.run_scad(probe,probe.with_suffix('.csg'))
            supports=[json.loads(s) for s in re.findall(r'ECHO: supports = (.+)',stderr)]
            feet=[json.loads(s) for s in re.findall(r'ECHO: foot = (.+)',stderr)]
            self.assertIn([], [ids for _,ids in supports])
            self.assertIn([0,3], [ids for _,ids in supports])
            self.assertIn([1,2], [ids for _,ids in supports])
            previous={}
            for i,(_,ids) in enumerate(supports):
                self.assertIn(ids,[[],[0,3],[1,2]])
                for _,id,angles,hip,ball in feet[i*4:i*4+4]:
                    self.assertGreaterEqual(ball[2],20-.001)
                    if id in ids:
                        self.assertAlmostEqual(ball[2],20,places=3)
                        if id in previous:
                            for x,y in zip(previous[id],ball):self.assertAlmostEqual(x,y,places=2)
                        previous[id]=ball
                    else:previous.pop(id,None)
            self.assertAlmostEqual(max(r[4][2] for r in feet),70,places=3)
            self.assertAlmostEqual(max(r[3][2] for r in feet)-min(r[3][2] for r in feet),16,places=3)

    def test_orbit_tracks_body_through_four_running_cycles(self):
        rotations=[];targets=[]
        with tempfile.TemporaryDirectory() as tmp:
            for t in [0,.25,.5,.75,1]:
                stderr=self.run_scad(ROOT/'output/foot/step_run_orbit.scad',Path(tmp)/f'camera_{t}.csg',
                                     '-D',f'orbit_time={t}',allow_camera=True)
                target=json.loads(re.search(r'camera_target = (\[[^\]]+\])',stderr)[1])
                rotation=json.loads(re.search(r'camera_rotation = (\[[^\]]+\])',stderr)[1])
                self.assertEqual(target,[-800*t,0,170])
                self.assertEqual(rotation,[68,0,25+360*t])
                self.assertEqual(len(re.findall(r'ECHO: gait_leg = ',stderr)),4)
                rotations.append(rotation);targets.append(target)
        self.assertEqual(rotations[-1][2]-rotations[0][2],360)
        self.assertEqual(targets[-1][0]-targets[0][0],-800)


if __name__=='__main__':unittest.main()
