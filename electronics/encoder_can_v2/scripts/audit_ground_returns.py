"""Check filled ground connectivity and report reference-plane interruptions.

Uses exact exported fills, lands, tracks and plated through-vias. Geometric
connectivity is not an electromagnetic or impedance model of the stackup.
"""
from pathlib import Path
import hashlib,json,math
from shapely.geometry import Point,LineString,Polygon,box
from shapely.affinity import rotate,translate
from shapely.ops import unary_union
from shapely import make_valid
R=Path(__file__).resolve().parents[1]
digest=hashlib.sha256((R/'encoder_can_v2.kicad_pcb').read_bytes()).hexdigest()
d=json.loads((R/'design/review_geometry.json').read_text());assert d['source_pcb_sha256']==digest
layers=['F.Cu','In1.Cu','In2.Cu','B.Cu']
assert not any(not t['via'] and t['layer']=='In1.Cu' and t['net']!='GND' for t in d['tracks'])
# KiCad exports stitched hole rings with zero-area retraced bridges.
# Decompose those rings without adding/removing copper area.
def polygon(z):
 raw=Polygon(z['outer'],z['holes']);valid=make_valid(raw)
 def areas(s):
  if s.geom_type=='Polygon':return [s]
  return [q for child in getattr(s,'geoms',[]) for q in areas(child)]
 result=unary_union(areas(valid));assert abs(result.area-raw.area)<1e-7
 return result
planes=[polygon(z) for z in d['zones'] if z['layer']=='In1.Cu' and z['net']=='GND']
assert len(planes)==1 and planes[0].geom_type=='Polygon' and planes[0].is_valid,'In1 ground must be a single filled connected polygon'
def land(q):
 if q['round']:return Point(q['xy']).buffer(q['size'][0]/2,quad_segs=64)
 w,h=q['size'];r=q.get('corner_mm',0)
 body=box(-w/2+r,-h/2+r,w/2-r,h/2-r).buffer(r,quad_segs=32) if r else box(-w/2,-h/2,w/2,h/2)
 return translate(rotate(body,-q['angle'],origin=(0,0)),*q['xy'])
via=[t for t in d['tracks'] if t['via'] and t['net']=='GND']
nodes=[];by_layer={}
for layer in layers:
 parts=[polygon(z) for z in d['zones'] if z['layer']==layer and z['net']=='GND']
 parts += [LineString([t['a'],t['z']]).buffer(t['width']/2) for t in d['tracks'] if not t['via'] and t['layer']==layer and t['net']=='GND']
 parts += [land(q) for q in d['pads'] if q['num'] and not q['hole'] and q['net']=='GND' and q['side']+'.Cu'==layer]
 parts += [Point(t['a']).buffer(t['width']/2) for t in via]
 shape=unary_union([s.buffer(.000003) for s in parts]);pieces=list(shape.geoms) if shape.geom_type=='MultiPolygon' else [shape]
 by_layer[layer]=[]
 for s in pieces:
  if s.is_empty:continue
  i=len(nodes);nodes.append((layer,s));by_layer[layer].append(i)
links={i:set() for i in range(len(nodes))}
for v in via:
 hits=[i for i,(layer,shape) in enumerate(nodes) if shape.covers(Point(v['a']))]
 assert len(hits)==4,('Missing ground via annulus',v['a'],hits)
 for i in hits:links[i].update(set(hits)-{i})
start=next(i for i in by_layer['In1.Cu'] if nodes[i][1].covers(planes[0].representative_point()))
seen=set();todo=[start]
while todo:
 i=todo.pop()
 if i in seen:continue
 seen.add(i);todo.extend(links[i]-seen)
orphans=[dict(layer=layer,area_mm2=shape.area) for i,(layer,shape) in enumerate(nodes) if i not in seen]
assert not orphans,('Ground copper disconnected from In1',orphans)
pad_checks=[]
for q in d['pads']:
 if not q['num'] or q['hole'] or q['net']!='GND':continue
 hits=[i for i in by_layer[q['side']+'.Cu'] if nodes[i][1].covers(Point(q['xy']))]
 assert hits and all(i in seen for i in hits),(q['ref'],q['num'])
 pad_checks.append([q['ref'],q['num']])
# Trace both supply rails back to their physical source, including each fill island.
supplies=[]
for net,source_ref,source_pin in [('+3V3','U5','5'),('+5V','J1','1')]:
 vv=[t for t in d['tracks'] if t['via'] and t['net']==net]
 pp=[q for q in d['pads'] if q['num'] and not q['hole'] and q['net']==net]
 nn=[];ll={}
 for layer in layers:
  parts=[polygon(z) for z in d['zones'] if z['layer']==layer and z['net']==net]
  parts += [LineString([t['a'],t['z']]).buffer(t['width']/2) for t in d['tracks'] if not t['via'] and t['layer']==layer and t['net']==net]
  parts += [land(q) for q in pp if q['side']+'.Cu'==layer]
  parts += [Point(t['a']).buffer(t['width']/2) for t in vv]
  merged=unary_union([sh.buffer(.000003) for sh in parts])
  for sh in getattr(merged,'geoms',[merged]):
   if sh.is_empty:continue
   i=len(nn);nn.append((layer,sh));ll[i]=set()
 for v in vv:
  hits=[i for i,(layer,sh) in enumerate(nn) if sh.covers(Point(v['a']))]
  assert len(hits)==4,(net,'missing via annulus',v['a'])
  for i in hits:ll[i].update(set(hits)-{i})
 src=next(q for q in pp if q['ref']==source_ref and q['num']==source_pin)
 start=next(i for i,(layer,sh) in enumerate(nn) if layer==src['side']+'.Cu' and sh.covers(Point(src['xy'])))
 reached=set();pending=[start]
 while pending:
  i=pending.pop()
  if i in reached:continue
  reached.add(i);pending.extend(ll[i]-reached)
 assert len(reached)==len(nn),(net,'copper not connected to source',[(layer,sh.area) for i,(layer,sh) in enumerate(nn) if i not in reached])
 for q in pp:assert any(i in reached and layer==q['side']+'.Cu' and sh.covers(Point(q['xy'])) for i,(layer,sh) in enumerate(nn)),(net,q['ref'],q['num'])
 supplies.append(dict(net=net,source=[source_ref,source_pin],lands_checked=len(pp),fill_polygons=sum(z['net']==net for z in d['zones']),all_copper_connected_to_source=True))
projection=[]
for net in ['HSE_IN','HSE_OUT','CAN_H','CAN_L','CAN_TX','CAN_RX','SWCLK','SWDIO']:
 worst=0.;length=0.;uncovered=0.
 for t in d['tracks']:
  if t['via'] or t['net']!=net:continue
  line=LineString([t['a'],t['z']]);length+=line.length;uncovered+=line.difference(planes[0]).length
  for j in range(max(2,math.ceil(line.length/.025)+1)):
   n=max(2,math.ceil(line.length/.025)+1);worst=max(worst,planes[0].distance(line.interpolate(j/(n-1),normalized=True)))
 projection.append(dict(net=net,track_length_mm=length,centerline_not_directly_above_in1_mm=uncovered,max_sampled_distance_to_in1_mm=worst))
out=dict(source_pcb_sha256=digest,in1_signal_free=True,in1_connected_filled_polygons=1,in1_ground_area_mm2=planes[0].area,ground_vias=len(via),ground_lands_checked=pad_checks,all_ground_copper_connected_to_in1=True,orphan_ground_copper=orphans,supply_connectivity=supplies,reference_projection=projection,passed=True,limits=['Two-dimensional nominal connectivity through plated vias, not impedance/EMC or current-density simulation.','Reference interruptions include antipads at signal vias and NPTH holes; sampled maximum distance does not qualify signal integrity.','B.Cu faces the fragmented +3V3 layer before In1; actual layer spacing and high-frequency return impedance require the factory stack and hardware tests.'])
(R/'design/ground_return_audit.json').write_text(json.dumps(out,indent=2)+'\n');print('All ground copper and',len(pad_checks),'lands connected to single In1 ground; projection reviewed.')
