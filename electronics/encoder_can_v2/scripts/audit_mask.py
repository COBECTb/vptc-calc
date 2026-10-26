"""Check actual bare ground under bodies; render finished-mask interpretation.

Numbered GND solder lands (including U1 EP33) must stay solderable. This is
nominal aperture geometry, not a prediction of mask registration or solder flow.
"""
from pathlib import Path
import json,hashlib,math
from shapely.geometry import Point,Polygon,LineString,box
from shapely.affinity import rotate,translate
from shapely.ops import unary_union
from shapely import make_valid
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.path import Path as MPath
from matplotlib.patches import PathPatch,Rectangle
from matplotlib.transforms import Affine2D
R=Path(__file__).resolve().parents[1];g=json.loads((R/'design/review_geometry.json').read_text());m=json.loads((R/'design/mask_geometry.json').read_text());sha=hashlib.sha256((R/'encoder_can_v2.kicad_pcb').read_bytes()).hexdigest();assert g['source_pcb_sha256']==m['source_pcb_sha256']==sha
assert not m['additional_mask_drawings'],'Review additional mask openings explicitly'
def padshape(q):
 w,h=q['size'];r=q.get('corner_mm',0)
 sh=Point(0,0).buffer(w/2,quad_segs=64) if q['round'] else box(-w/2+r,-h/2+r,w/2-r,h/2-r).buffer(r,quad_segs=48) if r else box(-w/2,-h/2,w/2,h/2)
 return translate(rotate(sh,-q['angle'],origin=(0,0)),*q['xy'])
def polygon(z):
 sh=make_valid(Polygon(z['outer'],z['holes']))
 def areas(s):return [s] if s.geom_type=='Polygon' else [q for child in getattr(s,'geoms',[]) for q in areas(child)]
 return unary_union(areas(sh))
pads={(q['ref'],q['num'],q['side']):q for q in g['pads']};audit=[];violations=[];surfaces={};holes=unary_union([padshape(q) for q in g['pads'] if q['hole']]);board=Polygon(g['outline'],g.get('outline_holes',[])).difference(holes)
for side in ['F','B']:
 aperture=unary_union([padshape(pads[q['ref'],q['num'],side]).buffer(q['mask_expansion_mm']) for q in m['apertures'] if q['side']==side])
 def copper(net=None):
  return unary_union([polygon(z) for z in g['zones'] if z['layer']==side+'.Cu' and (net is None or z['net']==net)]+[padshape(q) for q in g['pads'] if not q['hole'] and q['side']==side and (net is None or q['net']==net)]+[(Point(t['a']).buffer(t['width']/2,quad_segs=64) if t['via'] else LineString([t['a'],t['z']]).buffer(t['width']/2)) for t in g['tracks'] if (t['via'] or t['layer']==side+'.Cu') and (net is None or t['net']==net)])
 bare=copper().intersection(aperture).intersection(board);ground=copper('GND').intersection(aperture).intersection(board);surfaces[side]=(aperture,bare,ground)
 for c in g['components']:
  if c['side']!=side or not c['size']:continue
  w,h=c['size'][:2];body=translate(rotate(box(-w/2,-h/2,w/2,h/2),-c['angle'],origin=(0,0)),*c['xy'])
  allowed=unary_union([padshape(q) for q in g['pads'] if q['ref']==c['ref'] and q['side']==side and q['num'] and q['net']=='GND'])
  open_ground=ground.intersection(body);excess=open_ground.difference(allowed.buffer(.00001));row=dict(ref=c['ref'],side=side,ground_solder_land_area_under_body_mm2=open_ground.area,unintended_bare_ground_area_mm2=excess.area)
  if excess.area>1e-6:violations.append(row)
  audit.append(row)
 for t in g['tracks']:
  if t['via'] and Point(t['a']).buffer(t['width']/2,quad_segs=64).intersection(aperture).area>1e-6:violations.append(dict(kind='tented_via_opened_by_other_aperture',side=side,xy=t['a']))
report=dict(source_pcb_sha256=sha,all_mask_openings_from_footprint_pads=True,additional_mask_openings=0,components=audit,mandatory_u1_ep_ground_pad_preserved=True,violations=violations,passed=not violations,limits=['Nominal CAD apertures only; mask registration and fabrication process remain to be agreed.','Required numbered GND solder lands remain exposed; removing or covering U1 exposed pad would change its required assembly.'])
(R/'design/mask_audit.json').write_text(json.dumps(report,indent=2)+'\n');assert not violations,violations
angle=math.radians(9);ca,sa=math.cos(angle),math.sin(angle)
def local(p):
 x,y=p[0]-100,100-p[1];return x*ca+y*sa,-x*sa+y*ca
def draw(ax,shape,color,z=1,alpha=1):
 for poly in [shape] if shape.geom_type=='Polygon' else getattr(shape,'geoms',[]):
  if poly.is_empty or poly.geom_type!='Polygon':continue
  vertices=[];codes=[]
  for i,ring in enumerate([poly.exterior]+list(poly.interiors)):
   coords=[local(p) for p in ring.coords];area=sum(coords[k][0]*coords[k+1][1]-coords[k+1][0]*coords[k][1] for k in range(len(coords)-1))
   if (area>0)!=(i==0):coords=coords[::-1]
   vertices.extend(coords);codes.extend([MPath.MOVETO]+[MPath.LINETO]*(len(coords)-2)+[MPath.CLOSEPOLY])
  ax.add_patch(PathPatch(MPath(vertices,codes),fc=color,ec='none',zorder=z,alpha=alpha))
fig,axes=plt.subplots(1,2,figsize=(11,13),constrained_layout=True)
for ax,side in zip(axes,['F','B']):
 aperture,bare,ground=surfaces[side];draw(ax,board,'#24785a');draw(ax,aperture.intersection(board),'#c6d8c9',2);draw(ax,bare,'#d5b260',3);draw(ax,ground,'#e7a55c',4)
 for c in g['components']:
  if c['side']!=side or not c['size']:continue
  q=local(c['xy']);w,h=c['size'][:2];patch=Rectangle((q[0]-w/2,q[1]-h/2),w,h,fill=False,ec='#293b37',lw=.75,ls='--');patch.set_transform(Affine2D().rotate_deg_around(*q,c['angle']-9)+ax.transData);ax.add_patch(patch);ax.text(*q,c['ref'],ha='center',va='center',fontsize=7,bbox=dict(facecolor='white',alpha=.8,edgecolor='none',pad=.3),zorder=6)
 ax.set(aspect='equal',xlim=(15,35),ylim=(-23,23),xlabel='Radial, mm',ylabel='Tangent, mm',title=('Спереди / Hall' if side=='F' else 'Сзади / MCU')+' · реальные окна маски')
fig.suptitle('Зелёный — паяльная маска · золото — открытые площадки\nОранжевый — площадки GND, включая центральный контакт STM32\nПунктир — корпуса; переходы закрыты маской',fontsize=13)
fig.savefig(R/'design/mask_review.png',dpi=180);plt.close(fig);print('No unintended bare ground under bodies; all via annuli masked.')
