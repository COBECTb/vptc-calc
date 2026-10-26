"""Export the accepted native V2 prototype after full KiCad checks.

This exports a single board for quoting/prototyping, not an agreed factory
stackup/panel. Supplier stock and prototype qualification remain separate.
"""
from pathlib import Path
import csv,hashlib,json,subprocess,tempfile,datetime
ROOT=Path(__file__).resolve().parents[1]
CLI='/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'
PCB=ROOT/'encoder_can_v2.kicad_pcb';SCH=ROOT/'encoder_can_v2.kicad_sch'
LAYERS='F.Cu,In1.Cu,In2.Cu,B.Cu,F.Mask,B.Mask,F.SilkS,B.SilkS,Edge.Cuts,F.Paste,B.Paste'
spec=json.loads((ROOT/'design/electrical_spec.json').read_text());fit={c['ref'] for c in spec['components'] if c.get('mpn') and not c.get('dnp',False)}
settings=json.loads((ROOT/'encoder_can_v2.kicad_pro').read_text())['board']['design_settings']
assert settings['rules']['min_connection']>=.125,'Refuse export with disabled/insufficient copper-joint width check'
assert settings['rule_severities']['connection_width']=='error','Copper-joint width violations must block export'
clearance_report=ROOT/'design/solder_clearance_audit.json'
assert clearance_report.is_file(),'Run the new 0.5 mm solder-clearance audit before export'
clearance=json.loads(clearance_report.read_text())
assert clearance.get('passed') and clearance.get('required_via_to_land_mm',0)>=0.5,'New solder-clearance requirement has not been met'
assert clearance['source_pcb_sha256']==hashlib.sha256(PCB.read_bytes()).hexdigest(),'Solder-clearance audit is stale'
mounting_report=ROOT/'design/mounting_clearance_audit.json'
assert mounting_report.is_file(),'Run the mounting-head copper/envelope audit before export'
mounting=json.loads(mounting_report.read_text())
assert mounting.get('passed') and mounting.get('required_exterior_copper_free_diameter_mm',0)>=4.4,'Mounting-head clearance has not been met'
assert mounting['source_pcb_sha256']==hashlib.sha256(PCB.read_bytes()).hexdigest(),'Mounting-head audit is stale'
geometry=json.loads((ROOT/'design/review_geometry.json').read_text())
assert geometry['source_pcb_sha256']==hashlib.sha256(PCB.read_bytes()).hexdigest(),'Native geometry export is stale'
decoupling=json.loads((ROOT/'design/local_decoupling_audit.json').read_text())
assert decoupling['passed'] and decoupling['source_pcb_sha256']==geometry['source_pcb_sha256'],'Local bypass audit is missing or stale'
m3=json.loads((ROOT/'design/m3_access_audit.json').read_text())
assert m3['passed'] and m3['source_pcb_sha256']==geometry['source_pcb_sha256'],'M3 assembly access is blocked or its audit is stale'
fanout=json.loads((ROOT/'design/fanout_audit.json').read_text())
assert fanout['passed'] and fanout['source_pcb_sha256']==geometry['source_pcb_sha256'],'Straight/staggered escapes audit missing or stale'
for name in ['ground_return_audit','narrow_outline_audit','factory_rules_audit','mask_audit','cleanup_audit']:
 report=json.loads((ROOT/'design'/(name+'.json')).read_text())
 assert report['passed'] and report['source_pcb_sha256']==geometry['source_pcb_sha256'],name+' failed or stale'
def run(*args):
 r=subprocess.run([CLI,*map(str,args)],capture_output=True,text=True)
 if r.returncode:raise RuntimeError(r.stdout+r.stderr)
 return r.stdout

def write(path,fields,rows):
 with path.open('w',newline='',encoding='utf-8-sig') as f:
  w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(rows)

def requirements(component):
 notes=list(component.get('notes',[]))
 for key,label in [('dielectric','dielectric'),('voltage_v','rated voltage V'),
                   ('tolerance_percent','tolerance %'),('power_w','rated power W'),
                   ('max_height_mm','maximum body height mm')]:
  if key in component:notes.append(label+': '+str(component[key]))
 if component['ref'] in ['C13','C14']:notes.append('Initial HSE load value; characterize startup/frequency/drive on prototype')
 if component['ref']=='Y1':notes.append('Exact R80 version; 16MHz, CL12pF, ESR<=80ohm; ESR150 is not an approved substitution')
 return '; '.join(notes)
with tempfile.TemporaryDirectory(prefix='encoder-v2-export-') as t:
 stage=Path(t);g=stage/'gerbers';g.mkdir();dr=stage/'drills';dr.mkdir()
 for kind,src in [('drc',PCB),('erc',SCH)]:
  out=stage/(kind+'.json')
  args=['pcb','drc','--schematic-parity','--refill-zones'] if kind=='drc' else ['sch','erc']
  run(*args,'--severity-all','--exit-code-violations','--format','json','-o',out,src)
  q=json.loads(out.read_text());assert not q.get('violations',[]) and not any(s.get('violations') for s in q.get('sheets',[])) and not q.get('unconnected_items') and not q.get('schematic_parity')
 run('pcb','export','gerbers','-o',str(g)+'/','--layers',LAYERS,'--subtract-soldermask','--check-zones',PCB)
 # The automatic job uses an unagreed default copper stack. Do not ship it as a fabrication specification.
 for f in g.glob('*.gbrjob'):f.unlink()
 run('pcb','export','drill','-o',str(dr)+'/','--format','excellon','--drill-origin','absolute','--excellon-units','mm','--excellon-zeros-format','decimal','--excellon-separate-th','--generate-report',PCB)
 pos=stage/'positions.csv';run('pcb','export','pos','-o',pos,'--format','csv','--units','mm','--side','both','--smd-only','--exclude-dnp',PCB)
 with pos.open(encoding='utf-8-sig') as f:reader=csv.DictReader(f);fields=reader.fieldnames;rows=list(reader)
 rows=[r for r in rows if r['Ref'] in fit];assert {r['Ref'] for r in rows}==fit;assert len(rows)==len(fit)==35
 groups={}
 oldfields=list(next(csv.reader((ROOT/'assembly/BOM.csv').open(encoding='utf-8-sig'))))
 for c in spec['components']:
  ref=c['ref'];fitted=ref in fit;key=(c.get('mpn',''),c['footprint'],fitted,c['value']);groups.setdefault(key,[]).append(c)
 bom=[]
 for parts in groups.values():
  c=parts[0];fitted=c['ref'] in fit
  bom.append(dict(References=', '.join(q['ref'] for q in parts),Quantity_per_board=len(parts),Fitted_quantity_per_board=len(parts) if fitted else 0,Value=c['value'],Footprint=c['footprint'],Manufacturer=c.get('manufacturer',''),MPN=c.get('mpn',''),Populate='Yes' if fitted else 'No',Supplier_stock_code=c.get('supplier_stock_code',''),Supplier=c.get('supplier',''),Procurement_status=c.get('procurement_status','Exact MPN; availability/reservation to confirm') if c.get('mpn') else 'PCB only; do not order',Requirements=' | '.join(dict.fromkeys(requirements(q) for q in parts))))
 assert sum(q['Fitted_quantity_per_board'] for q in bom)==35
 run('sch','export','pdf','-o',stage/'schematic.pdf',SCH)
 run('pcb','export','svg','-o',stage/'front.svg','--mode-single','--fit-page-to-board','--exclude-drawing-sheet','--layers','F.Cu,F.Mask,F.Silkscreen,Edge.Cuts',PCB)
 run('pcb','export','svg','-o',stage/'back.svg','--mode-single','--fit-page-to-board','--exclude-drawing-sheet','--layers','B.Cu,B.Mask,B.Silkscreen,Edge.Cuts','--mirror',PCB)
 # Only publish after all exports and reference checks have passed.
 import shutil
 for folder in ['gerbers','drills']:
  dest=ROOT/'fabrication'/folder
  for f in dest.iterdir():
   if f.is_file():f.unlink()
  for f in (stage/folder).iterdir():shutil.copy2(f,dest/f.name)
 shutil.copy2(ROOT/'fabrication/drills/encoder_can_v2-drill.rpt',ROOT/'fabrication/drill_report.txt')
 write(ROOT/'assembly/positions_kicad.csv',fields,rows);write(ROOT/'assembly/BOM.csv',oldfields,bom)
 fiducials=[dict(Ref=c['ref'],PosX_mm=c['xy'][0],PosY_mm_KiCad_CPL=-c['xy'][1],Side='top' if c['side']=='F' else 'bottom',Copper_diameter_mm=1,Mask_aperture_mm=2) for c in geometry['components'] if c['ref'].startswith('FID')]
 assert len(fiducials)==6
 write(ROOT/'assembly/fiducials.csv',list(fiducials[0]),sorted(fiducials,key=lambda c:c['Ref']))
 for kind in ['drc','erc']:shutil.copy2(stage/(kind+'.json'),ROOT/'design'/('drc-final.json' if kind=='drc' else 'erc.json'))
 shutil.copy2(stage/'schematic.pdf',ROOT/'design/schematic.pdf')
 for name in ['front','back']:
  shutil.copy2(stage/(name+'.svg'),ROOT/'design'/('pcb_'+name+'.svg'))
 report=dict(date=datetime.date.today().isoformat(),source_pcb_sha256=hashlib.sha256(PCB.read_bytes()).hexdigest(),fitted_reference_count=len(fit),bom_cpl_references_match=True,factory_stackup_agreed=False,panelization='Single-board files; four-up assembly carrier to be designed by assembler',procurement_reserved=False,qualification='Prototype; hardware, optical brightness and production assembly not qualified')
 paths=[p for folder in ['fabrication','assembly'] for p in (ROOT/folder).rglob('*') if p.is_file() and p.name!='export_manifest.json'];report['files_sha256']={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}
 (ROOT/'fabrication/export_manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('Exported prototype:',len(fit),'fitted components; ERC/DRC/parity clean.')
