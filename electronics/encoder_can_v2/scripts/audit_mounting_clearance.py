"""Check exposed copper and nominal M2 screw envelope from saved native geometry."""
from pathlib import Path
import argparse, hashlib, json
from shapely.geometry import Point, LineString, Polygon, box
from shapely.affinity import rotate, translate
R=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('--output',type=Path,default=R/'design/mounting_clearance_audit.json')
args=ap.parse_args()
d=json.loads((R/'design/review_geometry.json').read_text())
sha=hashlib.sha256((R/'encoder_can_v2.kicad_pcb').read_bytes()).hexdigest()
assert sha==d['source_pcb_sha256'],'Refresh native geometry before checking'
outline=Polygon(d['outline'],d.get('outline_holes',[]));copper=[];front_bodies=[]
for c in d['components']:
 if c['side']=='F' and c['size']:
  w,h=c['size'][:2]
  front_bodies.append((c,translate(rotate(box(-w/2,-h/2,w/2,h/2),-c['angle'],origin=(0,0)),*c['xy'])))
for t in d['tracks']:
 if t['via'] or t['layer'] in ['F.Cu','B.Cu']:
  sh=Point(t['a']).buffer(t['width']/2,quad_segs=64) if t['via'] else LineString([t['a'],t['z']]).buffer(t['width']/2,quad_segs=32)
  copper.append((dict(kind='via' if t['via'] else 'track',net=t['net'],layer='both' if t['via'] else t['layer'],xy=t['a']),sh))
for p in d['pads']:
 if p['hole']:continue
 w,h=p['size'];r=p.get('corner_mm',0)
 sh=Point(p['xy']).buffer(w/2,quad_segs=64) if p['round'] else translate(rotate(box(-w/2+r,-h/2+r,w/2-r,h/2-r).buffer(r,quad_segs=32) if r else box(-w/2,-h/2,w/2,h/2),-p['angle'],origin=(0,0)),*p['xy'])
 copper.append((dict(kind='pad',ref=p['ref'],pad=p['num'],net=p['net'],layer=p['side']+'.Cu',xy=p['xy']),sh))
for z in d['zones']:
 if z['layer'] in ['F.Cu','B.Cu']:copper.append((dict(kind='filled_zone',net=z['net'],layer=z['layer']),Polygon(z['outer'],z['holes'])))
violations=[];mounts=[]
for p in d['pads']:
 if not p['hole']:continue
 pt=Point(p['xy']);edge=pt.distance(outline.boundary);head_radius=1.9;radial_play=(p['size'][0]-2.0)/2
 nearest=min(((pt.distance(sh),meta) for meta,sh in copper),key=lambda z:z[0])
 for meta,sh in copper:
  dist=pt.distance(sh)
  if dist<2.2-1e-5:violations.append(dict(hole=p['ref'],copper_radius_mm=dist,required_radius_mm=2.2,**meta))
 margin=edge-head_radius-radial_play
 if margin<0:violations.append(dict(hole=p['ref'],kind='head_outside_outline',margin_mm=margin))
 body_nearest=min(((pt.distance(sh)-head_radius-radial_play,c['ref']) for c,sh in front_bodies),default=(None,None))
 for c,sh in front_bodies:
  body_gap=pt.distance(sh)-head_radius-radial_play
  if body_gap<.2-1e-5:violations.append(dict(hole=p['ref'],kind='head_to_component',ref=c['ref'],gap_mm=body_gap,required_gap_mm=.2))
 mounts.append(dict(ref=p['ref'],center_mm=p['xy'],nearest_outline_mm=edge,head_diameter_mm=3.8,head_height_mm=1.3,shaft_diameter_mm=2.0,radial_play_mm=radial_play,head_to_outline_worst_nominal_mm=margin,nearest_front_body_gap_mm=body_nearest[0],nearest_front_body=body_nearest[1],nearest_exterior_copper_radius_mm=nearest[0],nearest_exterior_copper=nearest[1]))
report=dict(source_pcb_sha256=sha,required_exterior_copper_free_diameter_mm=4.4,mounts=mounts,violations=violations,passed=not violations,limits=['Geometry from the saved PCB. Includes both external filled zones, tracks, vias and pads.','Mask is not credited as insulation beneath a metal fastener.','Head envelope limited to diameter 3.8 mm, height 1.3 mm, no washer.','Radial shaft clearance included; head and PCB manufacturing tolerances need checking against purchased hardware.','Mechanical lid and pilot-depth checks are separate.'])
args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('Mounting copper/envelope issues:',len(violations))
if violations:raise SystemExit(1)
