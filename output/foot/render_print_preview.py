"""Draw print orientation and the H section from native OpenSCAD STL exports."""
from pathlib import Path
import argparse,re
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--print-mesh',type=Path,required=True)
p.add_argument('--section-mesh',type=Path,required=True)
a=p.parse_args();root=Path(__file__).resolve().parent
def mesh(path):
 return np.asarray(re.findall(r'vertex\s+([-+\deE.]+)\s+([-+\deE.]+)\s+([-+\deE.]+)',path.read_text()),float).reshape(-1,3,3)
tri=mesh(a.print_mesh);section=mesh(a.section_mesh)
assert abs(tri[:,:,2].min())<1e-6
fig=plt.figure(figsize=(12,6),facecolor='#f4f5ef')
ax=fig.add_axes([.01,.08,.68,.77],projection='3d',facecolor='#f4f5ef',computed_zorder=False)
n=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);n/=np.maximum(np.linalg.norm(n,axis=1,keepdims=True),1e-12)
light=np.array([-.2,-.5,.8]);light/=np.linalg.norm(light)
rgba=np.tile([.33,.43,.48,1.],(len(tri),1));rgba[:,:3]*=(.45+.55*np.maximum(0,n@light))[:,None]
bed=np.array([[[0,0,-.2],[220,0,-.2],[220,140,-.2]],[[0,0,-.2],[220,140,-.2],[0,140,-.2]]])
ax.add_collection3d(Poly3DCollection(bed,facecolors='#dae2df',edgecolors='#b7c8c5',linewidths=.6,zorder=0))
ax.add_collection3d(Poly3DCollection(tri,facecolors=rgba,edgecolors='none',linewidths=0,zorder=2))
ax.set_xlim(0,220);ax.set_ylim(0,140);ax.set_zlim(0,35)
ax.set_box_aspect([220,140,35]);ax.view_init(elev=52,azim=-64);ax.set_proj_type('ortho');ax.axis('off')
sx=fig.add_axes([.72,.24,.24,.54],facecolor='#f4f5ef')
sx.add_collection(PolyCollection(section[:,:,:2],facecolors='#3e5661',edgecolors='none'))
sx.plot([-15,15],[-11.75,-11.75],color='#95aaa6',lw=1)
sx.set_xlim(-15,15);sx.set_ylim(-15,15);sx.set_aspect('equal');sx.axis('off')
sx.set_title('H-СЕЧЕНИЕ',fontsize=13,weight='bold',color='#273d48')
fig.text(.06,.93,'ПЕЧАТЬ ЦЕЛЬНОЙ СТОПЫ С КОННЕКТОРОМ',fontsize=17,weight='bold',color='#273d48')
fig.text(.06,.865,'PLA+ · плоские основания полок на Z=0 · длинная ось в плоскости слоёв',fontsize=10,color='#536a73')
fig.text(.73,.19,'24 × 23,5 мм\nПолки и перемычка: 3,2 мм\nСкосы под перемычкой: 45°',fontsize=10,color='#536a73',linespacing=1.6)
fig.text(.06,.07,'Поддержка — локально в исходном пазу коннектора. TPU-полусфера печатается отдельно.',fontsize=10,color='#536a73')
fig.savefig(root/'print_orientation.png',dpi=150,facecolor=fig.get_facecolor())
