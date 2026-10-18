"""Verify phased native poses and draw 1 / 2 / 4 legs from CAD meshes.

The side-view animation uses the actual body and leg meshes, with the rods
shown by their native joint center lines. Imported mounting STL surfaces are
read directly: this preview does not require them to be boolean solids.
"""
from pathlib import Path
import argparse,json,re,struct,subprocess,tempfile
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from PIL import Image
from foot_kinematics import CONNECTOR_TO_SHIN_LINEAR,CONNECTOR_TO_SHIN_TRANSLATION

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--mesh',type=Path,required=True)
p.add_argument('--body',type=Path,required=True)
p.add_argument('--upper',type=Path,required=True)
p.add_argument('--openscad',default='/Applications/OpenSCAD-2021.01.app/Contents/MacOS/OpenSCAD')
p.add_argument('--gait',choices=['walk','run'],default='walk')
a=p.parse_args();R=Path(__file__).resolve().parent
with tempfile.TemporaryDirectory(prefix='robot-walk-') as tmp:
 probe=Path(tmp)/'poses.scad'
 probe.write_text(f'use <{R/"step_motion.scad"}>\nuse <{R.parent/"vptc_roller.scad"}>\n'
  'echo(dimensions=leg_kinematic_parameters());echo(config=step_configuration());echo(walk=robot_walk_configuration());echo(run=robot_run_configuration());\n'
  f'for(i=[0:200])let(t=i/200){{echo(supports=[t,robot_support_ids(t,"{a.gait}")]);\n'
  f'for(id=[0:3])echo(sample=[t,id,robot_joint_angles(t,id,"{a.gait}"),robot_hip_world(t,id,"{a.gait}"),robot_ball_world(t,id,"{a.gait}")]);}}\ncube(.1);\n')
 run=subprocess.run([a.openscad,'-o',str(probe.with_suffix('.csg')),str(probe)],capture_output=True,text=True,check=True)
 assert not any(w in run.stderr for w in ['WARNING:','ERROR:']),run.stderr
 def values(tag):return [json.loads(s) for s in re.findall(r'ECHO: '+tag+r' = (.+)',run.stderr)]
 dims=values('dimensions')[0];cfg=values('config')[0];duty,bp=values('walk')[0]
 run_cfg=values('run')[0]
 rows=values('sample');supports=values('supports')
length,lift,height,_,direction,radius=cfg;C=np.array(dims[0][:2]);body_cx=bp[1][1]+bp[0]/2
if a.gait=='run':duty,lift,bounce=run_cfg
assert len(rows)==804 and len(supports)==201
previous={};max_drift=0
for i,(t,ids) in enumerate(supports):
 assert len(ids)>=3 if a.gait=='walk' else (ids in [[],[0,3],[1,2]])
 for _,id,angles,hip,ball in rows[i*4:i*4+4]:
  assert ball[2]>=radius-.001
  if id in ids:
   assert abs(ball[2]-radius)<.001
   if id in previous:max_drift=max(max_drift,float(np.linalg.norm(np.array(ball)-previous[id])))
   previous[id]=ball
  else:previous.pop(id,None)
assert max_drift<.002,max_drift
for id in range(4):
 assert np.allclose(rows[id][2],rows[-4+id][2])
 assert abs(rows[-4+id][3][0]-rows[id][3][0]-direction*length)<.001

def mesh(path):
 b=path.read_bytes()
 if len(b)>=84 and 84+50*struct.unpack_from('<I',b,80)[0]==len(b):
  dt=np.dtype([('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')])
  return np.frombuffer(b,dt,offset=84)['v'].astype(float)
 return np.array(re.findall(rb'vertex\s+([-+\deE.]+)\s+([-+\deE.]+)\s+([-+\deE.]+)',b),float).reshape(-1,3,3)
tri=mesh(a.mesh);z=tri[:,:,2].mean(1)
parts={name:tri[np.abs(z-i*60)<29]-[0,0,i*60] for name,i in [('core',0),('sole',1),('connector',2),('shin',3)]}
parts={k:v@np.asarray(CONNECTOR_TO_SHIN_LINEAR).T+CONNECTOR_TO_SHIN_TRANSLATION for k,v in parts.items()}
body=mesh(a.body);upper=mesh(a.upper)
motor=mesh(R.parent/'vptc_roller_19_4_5_70_reducer.stl')
mount=mesh(R.parent/'vptc_roller_19_4_5_70_reducer_with_bracing_and_connector.stl')
mount_a=mount[:,:,[0,2,1]]*np.array([1,-1,1])+[0,76,-13]
mount_b=mount*np.array([-1,1,-1])
mount=np.concatenate([mount_a,mount_b])+[0,0,-bp[2]]
def rotate(v,angle):
 c,s=np.cos(np.radians(angle)),np.sin(np.radians(angle))
 return v@np.array([[c,s,0],[-s,c,0],[0,0,1.]])
def leg_scene(row):
 t,id,(hip,servo,q),anchor,ball=row;side=1 if id<2 else -1
 def world(v,angle=hip):return rotate(v,angle)[:,:,[1,2,0]]*np.array([1,side,1])+anchor
 result={'upper':world(upper),'motor':world(motor),'mount':world(mount,0)}
 for k,v in parts.items():result[k]=world(rotate(v,q)+np.r_[C,dims[4]])
 p1=dims[2]*np.array([np.cos(np.radians(servo)),np.sin(np.radians(servo))])
 p2=C+rotate(np.array([[[dims[3],0.,0.]]]),q)[0,0,:2]
 rod=world(np.array([[np.r_[p1,41],np.r_[p2,41]]]))[0]
 return result,rod
def body_scene(t):return body[:,:,[1,2,0]]+[direction*length*t-body_cx,-bp[3],rows[int(round(t*200))*4][3][2]]
ground_clearance=[];separation=[];bounds=[]
for i in range(201):
 boxes=[]
 for row in rows[i*4:i*4+4]:
  scene,rod=leg_scene(row)
  pts=np.concatenate([v.reshape(-1,3) for k,v in scene.items() if k!='sole']+[rod])
  ground_clearance.append(float(pts[:,2].min()));boxes.append([pts.min(0),pts.max(0)])
 for j in range(4):
  for k in range(j+1,4):
   # Positive separation on any coordinate plane proves these two bounding boxes disjoint.
   separation.append(float(np.maximum(np.array(boxes[k][0])-boxes[j][1],np.array(boxes[j][0])-boxes[k][1]).max()))
assert min(ground_clearance)>0
body_ground=float(body[:,:,0].min()+min(r[3][2] for r in rows));assert body_ground>0
report={'scope':'Kinematic 1/2/4-leg previews using native body/leg placement and four-bar closure. No balance, actuator torque, fatigue or full assembly collision certification.',
 'gait':a.gait,'step_length_mm':length,'direction':'left (-X)','lift_mm':lift,'hip_height_mm':height,
 'body_height_range_mm':[min(r[3][2] for r in rows),max(r[3][2] for r in rows)],
 'stance_fraction_multiple_legs':duty,'phase_offsets_FL_RL_FR_RR':[0,.5,.25,.75] if a.gait=='walk' else [0,.5,.5,0],
 'min_supported_feet':min(len(x[1]) for x in supports),'sampled_cycle_positions':len(supports),
 'max_geometric_contact_drift_mm':max_drift,'rigid_mesh_ground_clearance_mm':min(ground_clearance),
 'body_ground_clearance_mm':body_ground,'interleg_bounding_box_separation_min_mm':min(separation),
 'native_body_axle_spacing_mm':bp[0],'native_body_mounts_retained':True,
 'imported_mount_STL_note':'Original open-surface STL imports are used for preview; CGAL union export of these imports fails. They are not newly designed printable solids.',
 'internal_joint_contacts':'Not certified; existing axial rod/shin overlaps are documented separately in knee_travel_check/README.md.',
 'samples':[{'t':t,'id':id,'angles_deg':angles,'hip_world_mm':hip,'ball_world_mm':ball} for t,id,angles,hip,ball in rows]}
(R/f'robot_{a.gait}_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))

colors={'upper':'#d5ad27','motor':'#adb8c0','mount':'#b5bfc4','core':'#384a53','sole':'#172026','connector':'#d5ad27','shin':'#d5ad27'}
def add(ax,v,color,alpha=1):
 xy=v[:,:,[0,2]]
 u=xy[:,1]-xy[:,0];w=xy[:,2]-xy[:,0];area=u[:,0]*w[:,1]-u[:,1]*w[:,0]
 xy=xy[np.abs(area)>1e-5]
 ax.add_collection(PolyCollection(xy,facecolors=color,edgecolors='none',linewidths=0,alpha=alpha))
def draw_leg(ax,row,far=False):
 scene,rod=leg_scene(row)
 for k in ['mount','upper','connector','core','sole','shin','motor']:add(ax,scene[k],colors[k],.50 if far else 1)
 ax.plot(rod[:,0],rod[:,2],color='#a1abb0',lw=2,alpha=.5 if far else 1)
def draw(ax,index,view):
 batch=rows[index*4:index*4+4];t=batch[0][0]
 if view=='quadruped':
  for row in batch[2:]:draw_leg(ax,row,True)
  add(ax,body_scene(t),'#718794')
 for row in batch[:1 if view=='single' else 2]:draw_leg(ax,row)
 ax.axhline(0,color='#91a197',lw=1.2)
 for x in range(-700,401,40):ax.plot([x,x-8],[0,-8],color='#c1ccc4',lw=.6)
 ax.set_xlim(-550,330);ax.set_ylim(-15,390);ax.set_aspect('equal');ax.axis('off')
 ax.set_title({'single':'1 · Одна нога','left_pair':'2 · Левые передняя и задняя','quadruped':'3 · Четыре ноги с корпусом'}[view],fontsize=11,color='#50626c')
fig,axes=plt.subplots(3,1,figsize=(10,10),facecolor='#f4f5ef')
for ax,view in zip(axes,['single','left_pair','quadruped']):draw(ax,30,view)
fig.suptitle('ВПЕРЁД ← · '+('ШАГ' if a.gait=='walk' else 'БЕГ')+' 200 ММ',fontsize=18,color='#273d48',weight='bold')
fig.text(.06,.025,'Поэтапная кинематическая сборка · текущая стопа · исходный корпус',fontsize=10,color='#536a73')
fig.subplots_adjust(top=.92,bottom=.06,hspace=.15)
fig.savefig(R/('walking_stages.png' if a.gait=='walk' else 'running_stages.png'),dpi=130);plt.close(fig)
frames=[]
for i in range(0,201,10):
 fig,ax=plt.subplots(figsize=(9,5.1),facecolor='#f4f5ef');draw(ax,i,'quadruped')
 fig.text(.07,.92,'Вперёд ← · 200 мм за цикл',fontsize=16,color='#273d48')
 fig.text(.07,.05,f'$t={i/200:.2f} · опорных стоп: {len(supports[i][1])} · подъём {lift:g} мм',fontsize=11,color='#536a73')
 fig.subplots_adjust(top=.82,bottom=.13,left=.02,right=.98)
 fig.canvas.draw();frames.append(Image.fromarray(np.asarray(fig.canvas.buffer_rgba())[:,:,:3].copy()));plt.close(fig)
frames[0].save(R/f'quadruped_{a.gait}.gif',save_all=True,append_images=frames[1:],duration=120,loop=0,optimize=True)
print(json.dumps({k:v for k,v in report.items() if k!='samples'},ensure_ascii=False,indent=2))
