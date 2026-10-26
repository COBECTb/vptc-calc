"""Check V2 enclosure intersections using a fresh main-generator CAD package.

Run with the normal project Python (NumPy required), not KiCad's Python.
OpenSCAD is required. Empty intersections are expected; no STL is shipped.
Requires the full vptc-calc repository, including calc-vpts.py and cad/.
"""
import datetime
from pathlib import Path
import argparse,concurrent.futures,hashlib,json,os,shutil,subprocess,sys,tempfile
R=Path(__file__).resolve().parents[1];REPO=R.parents[1]
CASES=[('reducer_pcb_cap','reducer','reducer_encoder_scene','check_pcb_cap'),('reducer_pcb_lid','reducer','reducer_encoder_scene','check_pcb_lid'),('reducer_m3_access','reducer','reducer_encoder_scene','check_m3_access'),('reducer_m3_heads','reducer','reducer_encoder_scene','check_body_screw_heads'),('guide_pcb','reducer','reducer_encoder_scene','check_light_guides'),('bearing_cap','reducer','reducer_encoder_scene','check_bearing'),('knee_pcb_housing','knee','knee_encoder_scene','check_pcb_housing')]
def main():
 if not (REPO/'calc-vpts.py').is_file():raise SystemExit('Mechanical checks require the full vptc-calc source checkout, not only the KiCad archive.')
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--openscad',default=os.getenv('OPENSCAD') or shutil.which('openscad') or '/Applications/OpenSCAD-2021.01.app/Contents/MacOS/OpenSCAD');args=ap.parse_args();logs=R/'design/mechanical_checks';logs.mkdir(exist_ok=True)
 digest=hashlib.sha256((R/'encoder_can_v2.kicad_pcb').read_bytes()).hexdigest()
 with tempfile.TemporaryDirectory(prefix='encoder-mechanics-') as td:
  work=Path(td);master=work/'robot.scad'
  q=subprocess.run([sys.executable,str(REPO/'calc-vpts.py'),'--output',str(master),'--diameter','70','--hole-angle','39','--resolution','600','--ratio','19','--roller-d','4','--roller-h','5','--rout','28','--part','encoder_lights'],capture_output=True,text=True,timeout=120)
  (logs/'generator.log').write_text(q.stdout+q.stderr);assert q.returncode==0,q.stderr
  def run(row):
   name,lib,module,view=row;f=work/(name+'.scad');f.write_text('use <'+str(work/'robot_assets'/lib)+'.scad>\n'+module+'(view="'+view+'");\n')
   p=subprocess.run([args.openscad,'--export-format','binstl','-o',str(f.with_suffix('.stl')),str(f)],capture_output=True,text=True,timeout=360);text=p.stdout+p.stderr;(logs/(name+'.log')).write_text(text)
   result=dict(name=name,empty=p.returncode==1 and 'Current top level object is empty.' in text and 'ERROR:' not in text and 'WARNING:' not in text,returncode=p.returncode,log='design/mechanical_checks/'+name+'.log');print(name,'empty' if result['empty'] else 'FAILED',flush=True);return result
  with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(run,CASES))
 assert hashlib.sha256((R/'encoder_can_v2.kicad_pcb').read_bytes()).hexdigest()==digest,'Board changed during mechanical validation'
 report=dict(date=datetime.date.today().isoformat(),source_pcb_sha256=digest,cad_sha256={str(p.relative_to(REPO)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [REPO/'cad/reducer_v2.scad',REPO/'cad/knee_v2.scad',REPO/'cad/pcb_v2.scad']},probes=results,knee_planar_contact_exclusion_mm=.001,bearing_seat_contact_exclusion_mm=.001,pcb_cap_excludes_threaded_fasteners=True,pcb_lid_includes_fasteners=True,limits=['Nominal solid envelopes only; solder, tolerance, strength and brightness require physical qualification.','The PCB-to-carrier probe excludes fasteners because their threads intentionally engage plastic pilot holes. The lid probe includes fasteners.'])
 (R/'design/mechanical_release_2026-10-25.json').write_text(json.dumps(report,indent=2)+'\n');assert all(p['empty'] for p in results),results
if __name__=='__main__':main()
