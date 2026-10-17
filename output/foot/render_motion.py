"""Render the actual exported foot meshes using the native four-bar poses.

The lateral camera uses screen X=world Y, screen Y=world X. The CAD mount
comes from foot_kinematics and is independently checked against OpenSCAD.
"""
from pathlib import Path
import argparse,re,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from PIL import Image
from foot_kinematics import CONNECTOR_TO_SHIN_LINEAR,CONNECTOR_TO_SHIN_TRANSLATION
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--mesh',type=Path,required=True,help='STL exported from check_fit.scad with check="all"')
parser.add_argument('--thigh',type=Path,required=True,help='Fixed thigh union exported in native knee coordinates')
args=parser.parse_args()
R=Path(__file__).resolve().parent
def mesh(path):return np.array(re.findall(r'vertex\s+([-+\deE.]+)\s+([-+\deE.]+)\s+([-+\deE.]+)',Path(path).read_text()),float).reshape(-1,3,3)
alltri=mesh(args.mesh);mean=alltri[:,:,2].mean(1)
names=['core','sole','connector','shin','joined','abut','clash_shin','clash_sole']
parts={name:alltri[np.abs(mean-i*60)<29]-np.array([0,0,i*60]) for i,name in enumerate(names)}
source=(R.parent/'foots.scad').read_text()
h_active='design_variant="h";' in source
if h_active:source=(R.parent/'foots_h.scad').read_text()
def value(name):return float(re.search(r'^'+name+r'=([-+0-9.]+);',source,re.M).group(1))
intrinsic_side=1 if h_active else value('curve_side')
mount_roll=value('h_mount_roll' if h_active else 'mount_roll')
side=intrinsic_side*round(float(np.cos(np.radians(mount_roll))))
radius=value('h_pad_radius' if h_active else 'sole_radius')
pad_angle=value('h_pad_angle' if h_active else 'pad_angle')
pad_x=25+value('h_length')+4 if h_active else 25+value('blade_length')*value('distal_scale')+1
pad_y=value('h_pad_sweep') if h_active else value('blade_sweep')+8
lift=value('h_sole_lift') if h_active else 0
thigh=mesh(args.thigh);C=np.array([-13.,184.]);B=np.array([
 -47-pad_x-lift*np.cos(np.radians(pad_angle)),
 -side*(pad_y+lift*np.sin(np.radians(pad_angle)))])
def rot(a):
 c,s=np.cos(np.radians(a)),np.sin(np.radians(a));return np.array([[c,-s],[s,c]])
def linkage(t):
 servo=135*t-60.5;p=31*np.array([np.cos(np.radians(servo)),np.sin(np.radians(servo))]);d=np.linalg.norm(p-C)
 a=np.degrees(np.arctan2((p-C)[1],(p-C)[0]));q=a+np.degrees(np.arccos((d*d+37**2-184**2)/(2*d*37)))
 return servo,q,p,C+rot(q)@np.array([37.,0])
def source_to_shin(v):
 return v@np.asarray(CONNECTOR_TO_SHIN_LINEAR).T+CONNECTOR_TO_SHIN_TRANSLATION
# Shin mesh from the verification is in connector coordinates, so the same inverse map applies.
local={k:source_to_shin(v) for k,v in parts.items() if k in ['core','sole','connector','shin']}
def xy_to_screen(xy):return xy[...,::-1]
def pose(t):
 servo,q,p1,p2=linkage(t);A=rot(q)
 scene={'thigh':xy_to_screen(thigh[:,:,:2]+C)}
 for k,v in local.items():scene[k]=xy_to_screen(v[:,:,:2]@A.T+C)
 return scene,servo,q,xy_to_screen(A@B+C),xy_to_screen(p1),xy_to_screen(p2)
rows=[]
for t in np.linspace(0,1,101):
 scene,s,q,ball,p1,p2=pose(t)
 rigid=np.concatenate([scene[k].reshape(-1,2) for k in ['core','connector','shin']])
 ground=ball[1]-radius
 clearance=float(rigid[:,1].min()-ground)
 error=abs(q+side*pad_angle);limit=90 if h_active else np.degrees(np.arccos(value('sole_open')/radius))
 rows.append({'t':round(float(t),3),'servo_deg':round(s,3),'shin_deg':round(q,3),'spherical_pole_angle_deg':round(error,3),'pole_margin_to_opening_deg':round(limit-error,3),'hard_part_clearance_above_ball_tangent_mm':round(clearance,3)})
report={'scope':'Exact original 4-bar time law, fixed hip; 2D projection of rendered CAD. This is an articulation sweep, not a walking controller or dynamic simulation.','t_range':[0,1],'curve_side':side,'contact_model':'Sphere R18, mounting opening at -6 mm; varying ground pole stays within the spherical working surface in this camera plane.','min_pole_margin_deg':min(x['pole_margin_to_opening_deg'] for x in rows),'min_hard_part_clearance_mm':min(x['hard_part_clearance_above_ball_tangent_mm'] for x in rows),'historical_rod_limit_deg':[-44.646,54.204],'historical_limit_note':'The original t=0 pose is below the previously checked rod limit; no new rod-stop or complete 3D collision validation is claimed.','samples':rows}
report['mount_roll_deg']=mount_roll
report['variant']='constant_H' if h_active else 'tapered_box'
report['contact_model']=f'Hemisphere R{radius:g}, open mounting plane at sphere center; pole check in the lateral camera plane.' if h_active else report['contact_model']
report['curve_side']=intrinsic_side
report['connector_to_shin_matrix']=[[-1,0,0,-47],[0,-1,0,0],[0,0,1,0],[0,0,0,1]]
(R/'motion_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print({k:report[k] for k in ['min_pole_margin_deg','min_hard_part_clearance_mm']})
colors={'thigh':'#dbac26','shin':'#dbac26','connector':'#dbac26','core':'#384a53','sole':'#172026'}
def draw(ax,t):
 scene,s,q,ball,p1,p2=pose(t)
 for name in ['thigh','shin','connector','core','sole']:
  ax.add_collection(PolyCollection(scene[name],facecolors=colors[name],edgecolors='none',linewidths=0))
 ax.plot([p1[0],p2[0]],[p1[1],p2[1]],color='#a6b1b6',lw=3,zorder=5)
 ax.add_patch(plt.Circle((0,0),35,facecolor='#b6bdc2',edgecolor='#87939b',lw=.8,zorder=6))
 ax.add_patch(plt.Circle((0,0),4,facecolor='#f4f5ef',zorder=7))
 ax.set_xlim(-65,420);ax.set_ylim(-300,65);ax.set_aspect('equal');ax.axis('off')
 ax.set_title(f'$t = {t:.2f}   ·   колено {q:.1f}°',fontsize=11,color='#50626c',pad=8)
fig,axes=plt.subplots(1,3,figsize=(15,5.5),facecolor='#f4f5ef')
for ax,t in zip(axes,[0,.5,1]):ax.set_facecolor('#f4f5ef');draw(ax,t)
fig.suptitle('ДУГА ПО РЕФЕРЕНСУ · ВРЕМЯ 0…1',fontsize=19,weight='bold',color='#273d48',y=.96)
fig.text(.035,.06,'Три положения существующего механизма: $t от 0 до 1. Контактная поверхность теперь сферическая.',fontsize=11,color='#5c6e78')
fig.text(.035,.02,'Бедро здесь неподвижно: это проверка движения колена, а не готовый цикл ходьбы.',fontsize=10,color='#5c6e78')
fig.subplots_adjust(top=.80,bottom=.14,wspace=.12)
fig.savefig(R/'motion_positions.png',dpi=170,facecolor=fig.get_facecolor());plt.close(fig)
frames=[]
for t in np.linspace(0,1,31):
 fig,ax=plt.subplots(figsize=(7.4,6.4),facecolor='#f4f5ef');ax.set_facecolor('#f4f5ef');draw(ax,float(t))
 fig.text(.09,.94,'Прогон полной ноги · $t = 0…1',fontsize=16,weight='bold',color='#273d48')
 fig.text(.09,.04,'Исправленный изгиб и сферическая опора',fontsize=11,color='#5c6e78')
 fig.subplots_adjust(top=.84,bottom=.10,left=.03,right=.97)
 fig.canvas.draw();im=Image.fromarray(np.asarray(fig.canvas.buffer_rgba())[:,:,:3].copy());frames.append(im);plt.close(fig)
sequence=frames+frames[-2:0:-1]
sequence[0].save(R/'leg_sweep.gif',save_all=True,append_images=sequence[1:],duration=65,loop=0,optimize=True)
