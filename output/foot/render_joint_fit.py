"""Draw mating sections from the actual native verification mesh."""
from pathlib import Path
import argparse,re
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--mesh',type=Path,required=True);a=p.parse_args()
t=np.array(re.findall(r'vertex\s+([-+\deE.]+)\s+([-+\deE.]+)\s+([-+\deE.]+)',a.mesh.read_text()),float).reshape(-1,3,3)
z=t[:,:,2].mean(1)
parts={name:t[np.abs(z-i*60)<29]-[0,0,i*60] for name,i in [('core',0),('cuff',2),('shin',3)]}
def section(mesh,axis,level):
 axes=[j for j in range(3) if j!=axis];segments=[]
 for f in mesh:
  d=f[:,axis]-level;q=[]
  for i,j in [(0,1),(1,2),(2,0)]:
   if d[i]*d[j]<0:q.append(tuple(np.round((f[i]+(f[j]-f[i])*(-d[i]/(d[j]-d[i])))[axes],5)))
  if len(q)==2 and q[0]!=q[1]:segments.append(q)
 adj={}
 for u,v in segments:adj.setdefault(u,[]).append(v);adj.setdefault(v,[]).append(u)
 unused={tuple(sorted([u,v])) for u,v in segments};loops=[]
 while unused:
  u,v=next(iter(unused));loop=[u];start=u
  while True:
   unused.remove(tuple(sorted([u,v])));loop.append(v)
   if v==start:break
   ns=[w for w in adj[v] if tuple(sorted([v,w])) in unused]
   if not ns:raise RuntimeError(('Open section',v))
   u,v=v,ns[0]
  loops.append(np.array(loop))
 return sorted(loops,key=lambda q:abs((q[:-1,0]*q[1:,1]-q[:-1,1]*q[1:,0]).sum()),reverse=True)
src=Path(__file__).resolve().parents[1].joinpath('foots_h.scad').read_text()
def parameter(name):return float(re.search(r'^'+name+r'=([-+0-9.]+);',src,re.M).group(1))
a_j=np.radians(parameter('h_joint_angle'));c_j,s_j=np.cos(a_j),np.sin(a_j)
rot_j=np.array([[c_j,-s_j,0],[s_j,c_j,0],[0,0,1.]])
local_parts={name:(mesh-[0,parameter('h_joint_offset'),0])@rot_j for name,mesh in parts.items()}
bg='#f4f5ef';colors={'core':'#384a53','cuff':'#d9a724','shin':'#5384a1'}
fig,axes=plt.subplots(1,2,figsize=(12,5.3),facecolor=bg,gridspec_kw={'width_ratios':[1.7,1]})
for ax,axis,level in [(axes[0],2,.123),(axes[1],0,7.19)]:
 ax.set_facecolor(bg)
 for name in (['core','cuff','shin'] if axis==2 else ['cuff','shin']):
  loops=section(parts[name] if axis==2 else local_parts[name],axis,level)
  for i,loop in enumerate(loops):
   # Each part has an outer section and, where enclosed, its bore/socket.
   ax.add_patch(Polygon(loop,closed=True,facecolor=colors[name] if i==0 else bg,edgecolor=colors[name],lw=.55))
 ax.set_aspect('equal');ax.axis('off')
axes[0].set_xlim(-23,31);axes[0].set_ylim(21,-17)
axes[1].set_xlim(-15,15);axes[1].set_ylim(-14,14)
axes[0].set_title('Продольный разрез · ось крепежа М4 сохранена',fontsize=11,color='#38515e')
axes[1].set_title('Поперечный разрез посадки',fontsize=11,color='#38515e')
fig.suptitle('КОННЕКТОР И ШАРНИР · ПОСАДКА ПО РЕАЛЬНОМУ МЕШУ',fontsize=15,weight='bold',color='#273d48',y=.97)
fig.text(.06,.12,'Жёлтый — коннектор · синий — шарнир\nПрямое продолжение шарнира · без выемки',fontsize=10,color='#536a73',linespacing=1.5)
fig.text(.64,.12,'Паз повторяет профиль шарнира\nЗазор: 0,15 мм на грань · сечение 15 × 18 мм',fontsize=10,color='#536a73',linespacing=1.5)
fig.subplots_adjust(top=.82,bottom=.21,left=.03,right=.97,wspace=.20)
fig.savefig(Path(__file__).with_name('joint_fit.png'),dpi=170,facecolor=bg)
