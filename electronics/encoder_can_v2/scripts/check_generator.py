"""Run main-generator integration tests and bind their result to source hashes."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[1];REPO=R.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
files=[REPO/n for n in ['calc-vpts.py','encoder_scad.py','mechanical_package.py','tests/test_encoder_generator.py','tests/test_mechanical_package.py','output/vptc_roller.scad','output/foots.scad','output/foots_h.scad','output/foot/leg_motion.scad','output/foot/foot_kinematics.py']]+sorted((REPO/'cad').glob('*.scad'))
before={str(p.relative_to(REPO)):sha(p) for p in files};pcb=R/'encoder_can_v2.kicad_pcb';digest=sha(pcb)
q=subprocess.run([sys.executable,'-m','unittest','tests.test_encoder_generator','tests.test_mechanical_package'],cwd=REPO,capture_output=True,text=True)
log='design/mechanical_checks/integration-tests.log';(R/log).write_text('PCB SHA256: '+digest+'\n'+q.stdout+q.stderr)
assert sha(pcb)==digest and all(sha(REPO/n)==h for n,h in before.items()),'Sources changed during tests'
report=dict(source_pcb_sha256=digest,source_files_sha256=before,returncode=q.returncode,passed=q.returncode==0,log=log)
(R/'design/generator_release_audit.json').write_text(json.dumps(report,indent=2)+'\n');print(q.stdout+q.stderr,flush=True);assert report['passed']
