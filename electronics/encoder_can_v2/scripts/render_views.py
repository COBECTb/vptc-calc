"""Render extracted exact copper; every view uses the same front coordinate frame."""
from pathlib import Path
import json,math,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon,Circle,Rectangle,PathPatch
from matplotlib.path import Path as MPath
from matplotlib.transforms import Affine2D
from shapely.geometry import LineString,box
from shapely.affinity import rotate as shape_rotate,translate as shape_translate
R=Path(__file__).resolve().parents[1];d=json.loads((R/'design/review_geometry.json').read_text());a=math.radians(9)
def local(q):
 x=q[0]-100;y=100-q[1];return [x*math.cos(a)+y*math.sin(a),-x*math.sin(a)+y*math.cos(a)]
def polygon(outer,holes):
 vv=[];cc=[]
 for i,ring in enumerate([outer]+holes):
  p=np.array([local(q) for q in ring]);signed=np.sum(p[:,0]*np.roll(p[:,1],-1)-np.roll(p[:,0],-1)*p[:,1])
  if (signed>0)!=(i==0):p=p[::-1]
  vv.extend(p);cc.extend([MPath.MOVETO]+[MPath.LINETO]*(len(p)-1));vv.append(p[0]);cc.append(MPath.CLOSEPOLY)
 return MPath(vv,cc)
colors={'F.Cu':'#cc5a61','B.Cu':'#4c86bf','In1.Cu':'#6f9a84','In2.Cu':'#c4a54c'}
boundary=np.array([local(q) for q in d['outline']])
xlim=(math.floor(boundary[:,0].min()-1),math.ceil(boundary[:,0].max()+1))
ylim=(math.floor(boundary[:,1].min()-1),math.ceil(boundary[:,1].max()+1))
def draw(ax,layer,assembly=False):
 ax.add_patch(PathPatch(polygon(d['outline'],d.get('outline_holes',[])),facecolor='#f4f7f6',edgecolor='#213d35',lw=1))
 if not assembly:
  for z in d['zones']:
   if z['layer']==layer:ax.add_patch(PathPatch(polygon(z['outer'],z['holes']),facecolor=colors[layer],edgecolor='none',alpha=.22))
  # Convert a physical track width to points at the chosen fixed plot scale.
  factor=72*12.1/45
  for t in d['tracks']:
   if not t['via'] and t['layer']==layer:
    q,z=local(t['a']),local(t['z']);copper=LineString([q,z]).buffer(t['width']/2);ax.add_patch(Polygon(copper.exterior.coords,facecolor=colors[layer],edgecolor='none'))
 for t in d['tracks']:
  if t['via']:
   ax.add_patch(Circle(local(t['a']),t['width']/2,facecolor='#b9a56e',edgecolor='#725c2b',lw=.25));ax.add_patch(Circle(local(t['a']),t['drill']/2,facecolor='white',edgecolor='none'))
 for pad in d['pads']:
  if layer not in ['F.Cu','B.Cu'] and not pad['hole']:continue
  if not pad['hole'] and pad['side']+'.Cu'!=layer:continue
  q=local(pad['xy']);w,h=pad['size'];c='#23382e' if pad['hole'] else '#d0ad61'
  if pad['round']:ax.add_patch(Circle(q,w/2,facecolor=c,edgecolor='none'))
  else:
   rad=pad.get('corner_mm',0)
   shape=box(-w/2+rad,-h/2+rad,w/2-rad,h/2-rad).buffer(rad,quad_segs=24) if rad else box(-w/2,-h/2,w/2,h/2)
   shape=shape_translate(shape_rotate(shape,pad['angle']-9,origin=(0,0)),*q)
   ax.add_patch(Polygon(shape.exterior.coords,facecolor=c,edgecolor='none'))
  if pad['hole'] and layer in ['F.Cu','B.Cu']:
   ax.add_patch(Circle(q,1.9,fill=False,ec='#465a56',lw=.45))
   ax.add_patch(Circle(q,2.2,fill=False,ec='#465a56',lw=.45,ls='--'))
 if assembly:
  for f in d['components']:
   if f['side']+'.Cu'!=layer:continue
   q=local(f['xy']);sz=f['size']
   if sz:
    w,h=sz[:2];patch=Rectangle((q[0]-w/2,q[1]-h/2),w,h,fill=False,ec='#485e56',lw=.8);patch.set_transform(Affine2D().rotate_deg_around(*q,f['angle']-9)+ax.transData);ax.add_patch(patch)
   ax.text(*q,f['ref']+(' DNP' if f['ref']=='R9' else ''),fontsize=7,ha='center',va='center',bbox=dict(facecolor='white',edgecolor='none',alpha=.85,pad=.3))
 ax.set(xlim=xlim,ylim=ylim,aspect='equal');ax.set_xlabel('Radial, mm');ax.set_ylabel('Tangent, mm');ax.set_xticks(range(5*math.ceil(xlim[0]/5),int(xlim[1])+1,5));ax.set_yticks(range(5*math.ceil(ylim[0]/5),int(ylim[1])+1,5));ax.grid(lw=.25,alpha=.25)
in1_signals=sorted({t['net'] for t in d['tracks'] if not t['via'] and t['layer']=='In1.Cu' and t['net']!='GND'})
fig,axs=plt.subplots(1,4,figsize=(18,11),constrained_layout=True)
for ax,layer in zip(axs,colors):draw(ax,layer);ax.set_title(layer+'\n'+{'F.Cu':'Hall / CAN / LDO','B.Cu':'MCU / crystal / SWD','In1.Cu':'GND'+(' + '+', '.join(in1_signals) if in1_signals else ' · no signal traces'),'In2.Cu':'3.3 V + routing'}[layer])
fig.suptitle('Encoder CAN V2.4 · 4 layers · 0.8 mm\nCopper-only views: solder mask omitted; vias are tented',fontsize=15)
fig.savefig(R/'design/layout_review.png',dpi=190);plt.close(fig)
fig,axs=plt.subplots(1,2,figsize=(9,12),constrained_layout=True)
for ax,layer in zip(axs,['F.Cu','B.Cu']):draw(ax,layer,True);ax.set_title(layer+' assembly · front coordinates')
fig.suptitle('Encoder CAN V2 · component placement',fontsize=15);fig.savefig(R/'design/assembly_review.png',dpi=190);plt.close(fig)
# Overlay the saved original profile and immutable Hall references.
reference=json.loads((R/'design/narrow_outline_reference.json').read_text())
hall_ref=json.loads((R/'design/hall_reference_v1.json').read_text())
fig,ax=plt.subplots(figsize=(7,10),constrained_layout=True)
ax.add_patch(PathPatch(polygon(d['outline'],d.get('outline_holes',[])),facecolor='#e6f0ea',edgecolor='#2b7b5f',lw=2,label='V2.4 narrow'))
for i,(aa,zz) in enumerate(reference['edge_lines_mm']):
 pp=np.array([local(list(map(float,aa))),local(list(map(float,zz)))]);ax.plot(pp[:,0],pp[:,1],color='#7e8890',ls='--',lw=1,label='Original outline' if i==0 else None)
for ref in ['U2','U3']:
 f=next(f for f in d['components'] if f['ref']==ref);old=hall_ref[ref]
 assert math.dist(f['xy'],old['position_mm'])<1e-6 and abs(f['angle']-old['angle_deg'])<1e-6
 q=local(f['xy']);ax.scatter(*local(old['position_mm']),s=120,facecolors='none',edgecolors='#1e5c86',zorder=5)
 ax.scatter(*q,s=25,c='#1e5c86',zorder=6);ax.annotate(ref+' · unchanged',q,xytext=(18 if ref=='U2' else 27,5 if ref=='U2' else -5),arrowprops=dict(arrowstyle='->',color='#1e5c86'),fontsize=11)
ax.set(aspect='equal',xlim=(14,36),ylim=(-25,25),xlabel='Radial, mm',ylabel='Tangent, mm',title='V2.4 · exact original narrow outline\nHall positions / 9° and J2 preserved')
ax.legend(loc='lower left');ax.grid(alpha=.18);fig.savefig(R/'design/hall_position_overlay.png',dpi=170);plt.close(fig)
