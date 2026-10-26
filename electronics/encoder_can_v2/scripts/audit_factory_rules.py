"""Compare enforced CAD rules and printed markings with published factory limits.

This is not a factory approval of stack, assembly carrier or purchasing.
Run with KiCad Python after native full DRC including library comparison.
"""
from pathlib import Path
import json,hashlib
import pcbnew as p
R=Path(__file__).resolve().parents[1];source=R/'encoder_can_v2.kicad_pcb';b=p.LoadBoard(str(source));fs=list(b.GetFootprints());pads=[q for f in fs for q in f.Pads()]
rules=json.loads((R/'encoder_can_v2.kicad_pro').read_text())['board']['design_settings']['rules']
required=dict(min_track_width=.125,min_clearance=.125,min_copper_edge_clearance=.25,min_hole_clearance=.25,min_hole_to_hole=.2,min_via_annular_width=.1,min_text_height=1.,min_text_thickness=.15)
assert all(rules[k]>=v-1e-9 for k,v in required.items()),rules
markings=[]
for ref,items in [(f.GetReference(),[f.Reference(),f.Value()]+list(f.GraphicalItems())) for f in fs]+[('board',list(b.GetDrawings()))]:
 for item in items:
  if item.GetLayer() not in [p.F_SilkS,p.B_SilkS]:continue
  if isinstance(item,p.PCB_TEXT):
   if not item.IsVisible():continue
   height,stroke=p.ToMM(item.GetTextHeight()),p.ToMM(item.GetTextThickness());assert height>=1.-1e-6 and stroke>=.15-1e-6
   markings.append(dict(ref=ref,text=item.GetText(),height_mm=height,stroke_mm=stroke))
  elif isinstance(item,p.PCB_SHAPE):
   stroke=p.ToMM(item.GetWidth())
   if stroke:assert stroke>=.15-1e-6,(ref,stroke)
   else:
    # Solid pin-1 dots/triangle have no stroked line; check their printed feature envelope.
    assert item.IsSolidFill() and item.GetShape() in [p.SHAPE_T_CIRCLE,p.SHAPE_T_POLY],(ref,'unreviewed zero-stroke shape')
    bounds=item.GetBoundingBox();assert min(p.ToMM(bounds.GetWidth()),p.ToMM(bounds.GetHeight()))>=.15
    assert item.GetShape()==p.SHAPE_T_CIRCLE or ref=='U1','Only the reviewed solid MCU pin-1 triangle is allowed'
   markings.append(dict(ref=ref,shape=True,stroke_mm=stroke))
report=dict(source_pcb_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),published_limits_review_date='2026-10-26',required_rule_minima_mm=required,enforced_rule_values_mm={k:rules[k] for k in required},printed_markings=markings,base_copper_requested_um=18,finished_pcb_thickness_requested_mm=.8,factory_stackup_agreed=False,assembly_panel_agreed=False,passed=True,sources=['https://www.rezonit.ru/pcb/mnogosloynye-pechatnye-platy/serial/','https://www.rezonit.ru/assembly/prototyping/'],limits=['Published rules comparison; not manufacturer DFM approval.','Base18um advanced PCB class requested; actual stack and finished copper/tolerances need confirmation.','0.8mm assembly and 4-up carrier >=70x70mm, solder profile and EP X-ray are to be agreed.','Assembly page excludes wire soldering; J1 wires require a separate operation.'])
(R/'design/factory_rules_audit.json').write_text(json.dumps(report,indent=2)+'\n');print('Enforced factory CAD limits / printed silk checked; factory agreement still pending.')
