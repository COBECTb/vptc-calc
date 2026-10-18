"""Independent checks of exported native geometry, beyond standard DRC.
Run export_views.py first with KiCad Python. This script needs Shapely 2.x.
"""
from pathlib import Path
import json,math,hashlib
from shapely.geometry import box,Point,LineString,Polygon
from shapely.affinity import rotate,translate
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[1];d=json.loads((R/'design/review_geometry.json').read_text())
def pad_shape(p):
 w,h=p['size'];rad=p.get('corner_mm',0)
 shape=Point(0,0).buffer(w/2,quad_segs=48) if p['round'] else box(-w/2+rad,-h/2+rad,w/2-rad,h/2-rad).buffer(rad,quad_segs=32) if rad else box(-w/2,-h/2,w/2,h/2)
 return translate(rotate(shape,-p['angle'],origin=(0,0)),*p['xy'])
pads={(p['ref'],p['num']):p for p in d['pads']};can={}
for net,nums in [('CAN_H',('3','1','7','1')),('CAN_L',('4','2','6','2'))]:
 ts=[t for t in d['tracks'] if t['net']==net];assert all(not t['via'] and t['layer']=='F.Cu' for t in ts)
 copper=unary_union([LineString([t['a'],t['z']]).buffer(t['width']/2,quad_segs=32) for t in ts]+[pad_shape(p) for p in d['pads'] if p['net']==net]);j,tv,u,rr=[pads[(ref,n)] for ref,n in zip(['J1','D1','U4','R9'],nums)]
 assert any(g.covers(Point(j['xy'])) and g.covers(Point(u['xy'])) for g in getattr(copper,'geoms',[copper]))
 cut=copper.difference(pad_shape(tv).buffer(.001));parts=list(getattr(cut,'geoms',[cut]));bypass=any(g.covers(Point(j['xy'])) and g.covers(Point(u['xy'])) for g in parts)
 r9_on_output=any(g.covers(Point(rr['xy'])) and g.covers(Point(u['xy'])) for g in parts)
 can[net]=dict(only_front_copper=True,vias=0,transceiver_bypasses_tvs_pad=bypass,termination_branch_on_transceiver_side=r9_on_output)
 assert not bypass and r9_on_output,can[net]
body={}
for f in d['components']:
 if f['side']!='F' or not f['size']:continue
 w,h=f['size'][:2];body[f['ref']]=translate(rotate(box(-w/2,-h/2,w/2,h/2),-f['angle'],origin=(0,0)),*f['xy'])
hall={ref:dict(nearest_front_body=min((shape.distance(body[ref]),other) for other,shape in body.items() if other!=ref)) for ref in ['U2','U3']}
cap_pairs=[('U1','1','C1'),('U1','17','C2'),('U2','4','C6'),('U3','4','C7'),('U4','3','C8'),('U5','1','C10'),('U5','5','C11')]
cap_spacing=[dict(ic=ref,pin=pin,capacitor=c,between_pad_centres_mm=math.dist(pads[ref,pin]['xy'],pads[c,'1']['xy']),same_face=pads[ref,pin]['side']==pads[c,'1']['side']) for ref,pin,c in cap_pairs]
fids={side:[f['ref'] for f in d['components'] if f['side']==side and f['ref'].startswith('FID')] for side in ['F','B']};assert all(len(x)==3 for x in fids.values())
report=dict(source_pcb_sha256=hashlib.sha256((R/'encoder_can_v2.kicad_pcb').read_bytes()).hexdigest(),can_topology=can,hall_body_clearance=hall,bypass_capacitor_geometry=cap_spacing,fiducials=fids,clock_track_total_mm={net:sum(math.dist(t['a'],t['z']) for t in d['tracks'] if t['net']==net and not t['via']) for net in ['HSE_IN','HSE_OUT']},limits=['Geometry and topology checks do not simulate EMC, oscillator startup, thermal performance or magnetic angle accuracy.','Capacitor spacing is geometric pad-centre distance, not electrical loop inductance.'])
(R/'design/engineering_audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
