"""Verify the native SCAD step and render its actual exported geometry."""
from pathlib import Path
import argparse,json,re,subprocess,tempfile
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from PIL import Image
from foot_kinematics import CONNECTOR_TO_SHIN_LINEAR,CONNECTOR_TO_SHIN_TRANSLATION

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--mesh',type=Path,required=True,help='check_fit.scad, check="all"')
p.add_argument('--thigh',type=Path,required=True,help='Native fixed upper geometry in knee coordinates')
p.add_argument('--openscad',default='/Applications/OpenSCAD-2021.01.app/Contents/MacOS/OpenSCAD')
a=p.parse_args();root=Path(__file__).resolve().parent
with tempfile.TemporaryDirectory(prefix='native-step-') as tmp:
 probe=Path(tmp)/'probe.scad'
 probe.write_text(f'use <{root / "step_motion.scad"}>\n'
  f'use <{root.parent / "vptc_roller.scad"}>\n'
  'echo(dimensions=leg_kinematic_parameters());\n'
  'echo(configuration=step_configuration());\n'
  'for(i=[0:100])let(t=i/100)echo(sample=[t,step_angles(t),step_target(t),step_ball(t),step_body_x(t)]);\n'
  'cube(.1);\n')
 run=subprocess.run([a.openscad,'-o',str(probe.with_suffix('.csg')),str(probe)],capture_output=True,text=True,check=True)
 assert not any(x in run.stderr for x in ['WARNING:','ERROR:']),run.stderr
 dims=json.loads(re.search(r'ECHO: dimensions = (.+)',run.stderr)[1]);C=np.array(dims[0][:2])
 cfg=json.loads(re.search(r'ECHO: configuration = (.+)',run.stderr)[1])
 length,lift,height,duty,direction,radius=cfg
 contact_x=direction*length*duty/2
 samples=[json.loads(s) for s in re.findall(r'ECHO: sample = (.+)',run.stderr)]
assert len(samples)==101
rows=[]
for t,angles,target,ball,body_x in samples:
 assert np.allclose(ball,target,atol=.001),(t,ball,target)
 assert abs(body_x-direction*length*t)<.001
 if t<duty:assert np.allclose([ball[0]+body_x,ball[1]],[contact_x,radius],atol=.001)
 assert ball[1]>=radius-.001
 rows.append({'t':t,'body_X_mm':body_x,'hip_deg':angles[0],'servo_deg':angles[1],'knee_deg':angles[2],
              'target_center_XZ_mm':target,'actual_center_XZ_mm':ball})
assert all(np.allclose(x,y,atol=.001) for x,y in zip(samples[0][1:4],samples[-1][1:4]))
assert abs(max(s[3][1] for s in samples)-(radius+lift))<.02
def mesh(path):
 return np.asarray(re.findall(r'vertex\s+([-+\deE.]+)\s+([-+\deE.]+)\s+([-+\deE.]+)',path.read_text()),float).reshape(-1,3,3)
tri=mesh(a.mesh);z=tri[:,:,2].mean(1)
parts={name:tri[np.abs(z-i*60)<29]-[0,0,i*60] for name,i in [('core',0),('sole',1),('connector',2),('shin',3)]}
local={k:v@np.asarray(CONNECTOR_TO_SHIN_LINEAR).T+CONNECTOR_TO_SHIN_TRANSLATION for k,v in parts.items()}
thigh=mesh(a.thigh)
def rot(angle):
 c,s=np.cos(np.radians(angle)),np.sin(np.radians(angle));return np.array([[c,-s],[s,c]])
def pose(row):
 A=rot(row['hip_deg']);Q=rot(row['knee_deg'])
 world=lambda v:(v@A.T)[...,::-1]+[row['body_X_mm'],height]
 scene={'thigh':world(thigh[:,:,:2]+C)}
 scene.update({k:world(v[:,:,:2]@Q.T+C) for k,v in local.items()})
 servo=row['servo_deg'];p1=dims[2]*np.array([np.cos(np.radians(servo)),np.sin(np.radians(servo))])
 p2=C+rot(row['knee_deg'])@np.array([dims[3],0])
 return scene,world(np.array([p1,p2]))
clearance=[];pole=[]
for row in rows:
 scene,rod=pose(row)
 hard=np.concatenate([scene[k].reshape(-1,2) for k in ['thigh','core','connector','shin']]+[rod])
 clearance.append(float(hard[:,1].min()))
 # Native TPU hemisphere outward direction is 180-35 degrees before the two joints.
 pole.append(abs((row['hip_deg']+row['knee_deg']+145-180+180)%360-180))
assert min(clearance)>0,min(clearance)
assert max(pole)<90,max(pole)
report={'scope':'One-leg kinematic step using native dimensions and forward-checked four-bar angles; no balance, dynamics, torque or full 3D collision certification.',
 'step_length_mm':length,'clearance_mm':lift,'hip_height_mm':height,'stance_fraction':duty,
 'native_ball_target_error_mm':max(float(np.linalg.norm(np.array(r['actual_center_XZ_mm'])-r['target_center_XZ_mm'])) for r in rows),
 'direction':'left (-X)','body_displacement_X_mm':direction*length,'stance_world_contact_X_mm':contact_x,'loop_pose_continuous':True,
 'rigid_ground_clearance_mm':min(clearance),'hemisphere_pole_margin_deg':90-max(pole),
 'angle_ranges_deg':{k:[min(r[k] for r in rows),max(r[k] for r in rows)] for k in ['hip_deg','servo_deg','knee_deg']},'samples':rows}
(root/'step_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
colors={'thigh':'#dbac26','shin':'#dbac26','connector':'#dbac26','core':'#384a53','sole':'#172026'}
def draw(ax,row):
 scene,rod=pose(row)
 for k in ['thigh','shin','connector','core','sole']:
  ax.add_collection(PolyCollection(scene[k],facecolors=colors[k],edgecolors='none',linewidths=0))
 ax.plot(rod[:,0],rod[:,1],color='#a6b1b6',lw=2.5)
 ax.add_patch(plt.Circle((row['body_X_mm'],height),35,facecolor='#b6bdc2',edgecolor='#87939b'))
 ax.axhline(0,color='#91a197',lw=1.5)
 for x in range(-240,241,20):ax.plot([x,x-6],[0,-6],color='#c1ccc4',lw=.6)
 ax.plot(contact_x if row['t']<duty else row['actual_center_XZ_mm'][0]+row['body_X_mm'],0,'o',color='#47a379' if row['t']<duty else '#7d9eab',ms=4)
 ax.set_xlim(direction*length-100,230);ax.set_ylim(-15,355);ax.set_aspect('equal');ax.axis('off')
 ax.set_title(f"$t={row['t']:.2f} · "+('опора' if row['t']<duty else 'перенос'),fontsize=11,color='#50626c')
fig,axes=plt.subplots(1,4,figsize=(13,5.4),facecolor='#f4f5ef')
for ax,i in zip(axes,[0,30,60,80]):draw(ax,rows[i])
fig.suptitle('ШАГ ТЕКУЩЕЙ НОГОЙ · OpenSCAD $t = 0…1',fontsize=17,color='#273d48',weight='bold')
fig.text(.04,.07,f'Вперёд ← влево на {length:g} мм · подъём стопы: {lift:g} мм · опора: {100*duty:g}% цикла',fontsize=11,color='#536a73')
fig.text(.04,.025,'Кинематика одной ноги. Устойчивость и нагрузки этим прогоном не проверяются.',fontsize=10,color='#536a73')
fig.subplots_adjust(top=.85,bottom=.15,wspace=.08)
fig.savefig(root/'step_positions.png',dpi=160);plt.close(fig)
frames=[]
for i in range(0,101,4):
 fig,ax=plt.subplots(figsize=(5,6),facecolor='#f4f5ef');draw(ax,rows[i])
 fig.text(.09,.94,'Вперёд ← влево',fontsize=15,color='#273d48')
 fig.text(.09,.03,'Движение бедра и реального привода колена',fontsize=10,color='#536a73')
 fig.subplots_adjust(top=.85,bottom=.08,left=.02,right=.98)
 fig.canvas.draw();frames.append(Image.fromarray(np.asarray(fig.canvas.buffer_rgba())[:,:,:3].copy()));plt.close(fig)
frames[0].save(root/'walking_step.gif',save_all=True,append_images=frames[1:],duration=80,loop=0,optimize=True)
print(json.dumps({k:v for k,v in report.items() if k!='samples'},ensure_ascii=False,indent=2))
