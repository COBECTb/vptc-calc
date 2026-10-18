"""Portable, curated V2 review package; archive copy changes 3D references only."""
from pathlib import Path
import re,json,hashlib,zipfile
R=Path(__file__).resolve().parents[1];models=Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/3dmodels');files={};sources={}
def localize(s):
 def replace(m):
  old=m[1];assert old.startswith('${KISYS3DMOD}/'),old
  rel=Path(old.split('/',1)[1]);source=models/rel
  if not source.is_file():rel=rel.with_suffix('.step');source=models/rel
  assert source.is_file(),source
  dest='3dmodels/'+rel.as_posix();files[dest]=source.read_bytes();sources[dest]={'source':'KiCad 10.0.7 bundled official library','original_reference':old,'sha256':hashlib.sha256(files[dest]).hexdigest()}
  return '(model "${KIPRJMOD}/'+dest+'"'
 return re.sub(r'\(model "([^"]+)"',replace,s)
for name in ['encoder_can_v2.kicad_pro','encoder_can_v2.kicad_sch','encoder_can_v2.kicad_pcb','Encoder_CAN.kicad_sym','fp-lib-table','sym-lib-table','README.md','PROGRAMMING.md']:
 data=(R/name).read_bytes();files[name]=localize(data.decode()).encode() if name.endswith('.kicad_pcb') else data
for folder in ['Encoder_CAN.pretty','vendor','fabrication','assembly','simulation']:
 for f in sorted((R/folder).rglob('*')):
  if not f.is_file():continue
  if '__pycache__' in f.parts or f.suffix in ['.pyc','.raw','.lck','.kicad_prl']:continue
  if folder=='simulation' and f.suffix=='.csv' and f.name not in ['summary.csv','load_step_gui.csv']:continue
  name=f.relative_to(R).as_posix();data=f.read_bytes();files[name]=localize(data.decode()).encode() if f.suffix=='.kicad_mod' else data
for name in ['engineering_audit.json','engineering_review.md','review_geometry_fixes.json','pcb_front_3d.png','hall_detail_3d.png','drc-final.json','erc.json','portable_drc.json','portable_erc.json','package_verification.json','layout_audit.json','mechanical_fit_report.json','layout_review.png','assembly_review.png','pcb_front.svg','pcb_back.svg','schematic.pdf','electrical_spec.json','placement.json','component_envelopes.json','component_envelopes_v2.json','hall_reference_v1.json','knee-fit-final.log','reducer-fit-final.log','lid-fit-final.log','review_geometry.json','signal_route_audit.json','screenshot_fixes.json','screenshot_centering.json','screenshot_review.md','screenshot_review_signals.png','screenshot_review_power.png']:
 files['design/'+name]=(R/'design'/name).read_bytes()
for name in ['swd_clip_audit.json','swd_revision_verification.json','mechanics_v2.json']:
 files['design/'+name]=(R/'design'/name).read_bytes()
for name in ['audit_swd_clip.py','audit_final.py','audit_engineering.py','audit_signal_routes.py','export_views.py','render_views.py']:files['scripts/'+name]=(R/'scripts'/name).read_bytes()
files['3dmodels/LICENSE-KiCad.md']=(R/'vendor/LICENSE-KiCad.md').read_bytes();files['3dmodels/SOURCES.json']=(json.dumps(sources,indent=2)+'\n').encode()
for table in ['fp-lib-table','sym-lib-table']:
 for rel in re.findall(r'\(uri "\$\{KIPRJMOD\}/([^"]+)"',files[table].decode()):assert rel in files or any(n.startswith(rel+'/') for n in files),rel
libs=dict(re.findall(r'\(lib \(name "([^"]+)"\).*?\(uri "\$\{KIPRJMOD\}/([^"]+)"',files['fp-lib-table'].decode()))
for lib,fp in re.findall(r'\(footprint "([^:"]+):([^"]+)"',files['encoder_can_v2.kicad_pcb'].decode()):assert libs[lib]+'/'+fp+'.kicad_mod' in files
for name,data in list(files.items()):
 if name.endswith(('.kicad_mod','.kicad_pcb')):
  for rel in re.findall(r'\(model "\$\{KIPRJMOD\}/([^"]+)"',data.decode()):assert rel in files,rel
manifest={'date':'2026-10-18','kicad_version':'10.0.7','entrypoint':'encoder_can_v2.kicad_pro','source_pcb_sha256':hashlib.sha256((R/'encoder_can_v2.kicad_pcb').read_bytes()).hexdigest(),'archive_copy_changes':'Only standard 3D references localized to included STEP models; no electrical/geometry changes.','files_sha256':{n:hashlib.sha256(v).hexdigest() for n,v in sorted(files.items())}}
files['archive_manifest.json']=(json.dumps(manifest,indent=2)+'\n').encode();dest=R/'encoder_can_v2_kicad.zip'
with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
 for n,v in sorted(files.items()):z.writestr('encoder_can_v2/'+n,v)
with zipfile.ZipFile(R/'encoder_can_v2_fabrication.zip','w',zipfile.ZIP_DEFLATED) as z:
 for f in sorted((R/'fabrication').rglob('*')):
  if f.is_file():z.write(f,f.relative_to(R/'fabrication').as_posix())
print(dest,len(files),'files',round(dest.stat().st_size/1048576,2),'MiB')
