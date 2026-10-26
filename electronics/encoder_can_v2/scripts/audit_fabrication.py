"""Check exported profile paths and drill coordinates against the saved PCB.

KiCad Gerber 4.6 mm absolute linear profile and decimal mm Excellon only.
This validates profile transfer including all M3 notches/cutouts, not a factory DFM approval.
"""
from pathlib import Path
from collections import Counter,defaultdict
import hashlib,json,re,math
from schematic_sexpr import parse,get,nodes
R=Path(__file__).resolve().parents[1]
source=R/'encoder_can_v2.kicad_pcb';digest=hashlib.sha256(source.read_bytes()).hexdigest()
manifest=json.loads((R/'fabrication/export_manifest.json').read_text())
assert manifest['source_pcb_sha256']==digest,'Re-export manufacturing files'
b=parse(source.read_text());profile=R/'fabrication/gerbers/encoder_can_v2-Edge_Cuts.gm1';s=profile.read_text()
assert '%FSLAX46Y46*%' in s and '%MOMM*%' in s
expected=[]
def edge(a,z):return tuple(sorted((a,z)))
for q in nodes(b,'gr_line'):
 if get(q,'layer')[1]!='Edge.Cuts':continue
 aa,zz=[tuple(round(float(v)*1e6) for v in get(q,k)[1:3]) for k in ['start','end']]
 expected.append(edge(aa,zz))
assert not any(get(q,'layer')[1]=='Edge.Cuts' for q in nodes(b,'gr_arc'))
actual=[];pos=None
for x,y,op in re.findall(r'X(-?\d+)Y(-?\d+)D0([12])\*',s):
 new=(int(x),-int(y))
 if op=='1':
  assert pos is not None;actual.append(edge(pos,new))
 pos=new
assert Counter(actual)==Counter(expected),'Gerber profile differs from saved Edge.Cuts'
adj=defaultdict(set)
for a,z in actual:adj[a].add(z);adj[z].add(a)
assert all(len(v)==2 for v in adj.values()),'Open or branched profile'
seen=set();loops=0
for root in adj:
 if root in seen:continue
 loops+=1;todo=[root]
 while todo:
  q=todo.pop()
  if q in seen:continue
  seen.add(q);todo.extend(adj[q]-seen)
g=json.loads((R/'design/review_geometry.json').read_text());assert g['source_pcb_sha256']==digest
assert loops==1+len(g.get('outline_holes',[])),'Exported profile loop count differs from saved PCB'

def drill(path):
 s=path.read_text();assert 'METRIC' in s and 'G90' in s
 tools={int(n):float(v) for n,v in re.findall(r'^T(\d+)C([\d.]+)$',s,re.M)}
 active=None;out=[]
 for line in s.splitlines():
  m=re.fullmatch(r'T(\d+)',line)
  if m:active=int(m[1]);continue
  m=re.fullmatch(r'X(-?[\d.]+)Y(-?[\d.]+)',line)
  if m:assert active in tools;out.append((float(m[1]),-float(m[2]),tools[active]))
 return out
expected_vias=[(t['a'][0],t['a'][1],t['drill']) for t in g['tracks'] if t['via']]
expected_npth=[(p['xy'][0],p['xy'][1],p['size'][0]) for p in g['pads'] if p['hole']]
for name,expected in [('PTH',expected_vias),('NPTH',expected_npth)]:
 actual=drill(R/f'fabrication/drills/encoder_can_v2-{name}.drl')
 assert len(actual)==len(expected),(name,len(actual),len(expected))
 for x,y,dia in expected:
  hits=[i for i,(xx,yy,dd) in enumerate(actual) if math.hypot(x-xx,y-yy)<=.00072 and abs(dia-dd)<.000001]
  assert len(hits)==1,(name,x,y,dia,hits);actual.pop(hits[0])
report=dict(source_pcb_sha256=digest,profile_segments=len([q for q in nodes(b,'gr_line') if get(q,'layer')[1]=='Edge.Cuts']),closed_profile_loops=loops,closed_internal_cutouts=loops-1,gerber_profile_matches_saved_pcb=True,pth_holes=len(expected_vias),npth_holes=len(expected_npth),drill_rounding_allowance_mm=.00072,drill_coordinates_and_diameters_match=True,passed=True,limits=['Checks profile and drills, not assembly-process qualification or factory DFM.'])
(R/'design/fabrication_geometry_audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
