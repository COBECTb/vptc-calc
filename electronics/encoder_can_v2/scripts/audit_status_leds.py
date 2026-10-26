"""Verify indicator GPIOs, return-plane geometry and mechanical paths.

Requires fresh export_views.py / export_mechanics.py, Shapely and NumPy.
Optical brightness, fabrication tolerances and electrical function need hardware.
"""
import datetime
from pathlib import Path
import hashlib,json,math
from shapely.geometry import Point,LineString,Polygon,box
from shapely.affinity import rotate,translate
R=Path(__file__).resolve().parents[1];d=json.loads((R/'design/review_geometry.json').read_text());spec=json.loads((R/'design/electrical_spec.json').read_text());pads={(p['ref'],p['num']):p for p in d['pads']};components=json.loads((R/'design/component_envelopes_v2.json').read_text())
for c in spec['components']:
 for n,net in c['pins'].items():
  if net is not None:assert pads[c['ref'],n]['net']==net,(c['ref'],n,net,pads[c['ref'],n]['net'])
  else:assert pads[c['ref'],n]['net'].startswith('unconnected-'),(c['ref'],n)
assert pads['U1','9']['net']=='LED_CMD' and pads['U1','10']['net']=='LED_PHASE'
assert not any(q['ref']=='U1' and q['pin'] in ['9','10'] for q in spec['nc_pins'])
in1=[q for q in d['tracks'] if not q['via'] and q['layer']=='In1.Cu'];planes=[z for z in d['zones'] if z['layer']=='In1.Cu'];assert len(planes)==1 and planes[0]['net']=='GND'
assert all(t['net']=='LED_CMD' for t in in1)
critical=[t for t in d['tracks'] if not t['via'] and t['net'] in ['CAN_H','CAN_L','CAN_TX','CAN_RX','HSE_IN','HSE_OUT']]
separation=min((LineString([t['a'],t['z']]).buffer(t['width']/2).distance(LineString([q['a'],q['z']]).buffer(q['width']/2)) for t in in1 for q in critical),default=None)
assert separation is None or separation>1
xy=lambda r,a:[r*math.cos(math.radians(a)),r*math.sin(math.radians(a))]
def arc(r,a,b):
 n=max(1,math.ceil(abs(b-a)/4));return [xy(r,a+(b-a)*j/n) for j in range(n+1)]
paths=[];report=[]
for i,ref in enumerate(['D2','D3','D4']):
 led=next(q for q in components if q['ref']==ref);r,a=led['r'],led['a'];source=xy(r,a)
 if i<2:
  bend,outer,exit_a=[(50,34,32),(60,35.5,38)][i];pts=arc(r,a,bend)+arc(outer,bend,exit_a)+[xy(51,exit_a)]
 else:pts=[source]+arc(29.2,a,-30)+[xy(51,-30)]
 shape=LineString(pts).buffer(.4).union(Point(source).buffer(.7));paths.append(shape);nearest=[]
 for c in components:
  if c['front'] or c['ref']==ref:continue
  w,h,z=c['size_mm'];body=translate(rotate(box(-w/2,-h/2,w/2,h/2),c['angle']),*xy(c['r'],c['a']))
  assert not shape.intersects(body),(ref,c['ref']);nearest.append((shape.distance(body),c['ref']))
 actual_mounts=json.loads((R/'design/mechanics_v2.json').read_text())['mounts']
 mounts=[(math.hypot(*p),math.degrees(math.atan2(p[1],p[0])),1) for p in actual_mounts]+[(31.5,a,1.6) for a in range(39,360,60)]
 clearance=min((shape.distance(Point(xy(r,a)))-rad,r,a) for r,a,rad in mounts);assert clearance[0]>.2
 report.append(dict(ref=ref,path_xy_mm=pts,closest_other_body_mm=min(nearest),minimum_nominal_shank_clearance_mm=clearance,channel_floor_z_mm=10.2,bearing_stop_z_mm=10))
gaps=[paths[i].distance(paths[j]) for i in range(3) for j in range(i)];assert min(gaps)>.2
out=dict(date=datetime.date.today().isoformat(),source_pcb_sha256=hashlib.sha256((R/'encoder_can_v2.kicad_pcb').read_bytes()).hexdigest(),pin_and_net_consistency=True,in1_no_signal_tracks=not in1,in1_slow_gpio_length_mm=sum(math.dist(t['a'],t['z']) for t in in1),in1_ground_filled_polygon_count=len(planes),in1_to_can_clock_track_projection_clearance_mm=separation,light_paths=report,minimum_interchannel_gap_mm=min(gaps),limits=['Nominal geometric paths only; does not establish brightness, EMI, mechanical tolerance or lifetime.','Transparent 0.6 mm guide inserts are experimental; finish and installation must be qualified.','Holes and source bodies use model coordinates, not measured assembled boards.'])
(R/'design/status_led_review.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print('GPIO/net consistency and optical path checks passed;', 'In1 is signal-free' if separation is None else 'In1 critical track separation '+str(round(separation,3))+' mm')
