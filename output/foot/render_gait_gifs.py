"""Five slow GIF previews from native OpenSCAD joint angles and STL triangles.

Requires numpy and Pillow, plus clang++ for the small portable depth renderer.
Input STL exports: check_fit.scad(check="all"), gait_geometry.scad(part="body"
/"upper"). The camera follows translation while the ground stays in world space.
The orbit exactly spans four run cycles and one camera revolution.
"""
from pathlib import Path
import argparse, ctypes, json, re, struct, subprocess, tempfile
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from foot_kinematics import CONNECTOR_TO_SHIN_LINEAR, CONNECTOR_TO_SHIN_TRANSLATION

R=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--mesh',type=Path,required=True)
p.add_argument('--body',type=Path,required=True)
p.add_argument('--upper',type=Path,required=True)
p.add_argument('--frames',type=int,default=80,help='Frames per 12-second gait cycle; multiple of 20')
p.add_argument('--only',choices=['single','left_pair','walk','run','orbit'])
p.add_argument('--openscad',default='/Applications/OpenSCAD-2021.01.app/Contents/MacOS/OpenSCAD')
a=p.parse_args();N=a.frames
assert N>=20 and N%20==0
W,H=960,720
GRID=list(range(-800,801,50));GROUND_TRIANGLES=2*len(GRID)**2
font=lambda s:ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',s)
F={s:font(s) for s in [15,17,19,24,28]}

with tempfile.TemporaryDirectory(prefix='gait-gifs-') as tmp:
 tmp=Path(tmp)
 subprocess.run(['clang++','-O3','-std=c++17','-dynamiclib',str(R/'gait_raster.cpp'),'-o',str(tmp/'raster.dylib')],check=True)
 lib=ctypes.CDLL(str(tmp/'raster.dylib'));fp=ctypes.POINTER(ctypes.c_float)
 lib.raster.argtypes=[ctypes.c_int]*3+[fp]*3+[ctypes.c_float]*3+[ctypes.POINTER(ctypes.c_uint8),fp]
 probe=tmp/'poses.scad'
 probe.write_text(f'use <{R/"step_motion.scad"}>\nuse <{R.parent/"vptc_roller.scad"}>\n'
  'echo(dimensions=leg_kinematic_parameters());echo(config=step_configuration());echo(walk=robot_walk_configuration());echo(run=robot_run_configuration());\n'
  f'for(i=[0:{N-1}])let(t=i/{N}){{\n'
  'echo(single=[t,0,step_angles(t),[step_body_x(t),0,step_configuration()[2]],concat([step_ball(t)[0]+step_body_x(t),38],[step_ball(t)[1]])]);\n'
  'for(id=[0:3]){echo(walkpose=[t,id,robot_joint_angles(t,id,"walk"),robot_hip_world(t,id,"walk"),robot_ball_world(t,id,"walk")]);\n'
  'echo(runpose=[t,id,robot_joint_angles(t,id,"run"),robot_hip_world(t,id,"run"),robot_ball_world(t,id,"run")]);}}\ncube(.1);')
 proc=subprocess.run([a.openscad,'-o',str(tmp/'poses.csg'),str(probe)],capture_output=True,text=True,check=True)
 assert not any(s in proc.stderr for s in ['WARNING:','ERROR:']),proc.stderr
 values=lambda tag:[json.loads(s) for s in re.findall(r'ECHO: '+tag+r' = (.+)',proc.stderr)]
 dims=values('dimensions')[0];cfg=values('config')[0];duty,bp=values('walk')[0];rcfg=values('run')[0]
 poses={k:values(v) for k,v in [('single','single'),('walk','walkpose'),('run','runpose')]}
 length,lift,height,single_duty,direction,radius=cfg
 assert len(poses['single'])==N and len(poses['walk'])==4*N and len(poses['run'])==4*N
 assert direction==-1 and length==200
 def mesh(path):
  b=path.read_bytes()
  if len(b)>=84 and 84+50*struct.unpack_from('<I',b,80)[0]==len(b):
   return np.frombuffer(b,np.dtype([('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')]),offset=84)['v'].astype(float)
  return np.array(re.findall(rb'vertex\s+([-+\deE.]+)\s+([-+\deE.]+)\s+([-+\deE.]+)',b),float).reshape(-1,3,3)
 tri=mesh(a.mesh);z=tri[:,:,2].mean(1)
 parts={name:tri[np.abs(z-i*60)<29]-[0,0,i*60] for name,i in [('core',0),('sole',1),('connector',2),('shin',3)]}
 parts={k:v@np.asarray(CONNECTOR_TO_SHIN_LINEAR).T+CONNECTOR_TO_SHIN_TRANSLATION for k,v in parts.items()}
 body=mesh(a.body);upper=mesh(a.upper);motor=mesh(R.parent/'vptc_roller_19_4_5_70_reducer.stl')
 mount=mesh(R.parent/'vptc_roller_19_4_5_70_reducer_with_bracing_and_connector.stl')
 mount=np.concatenate([mount[:,:,[0,2,1]]*[1,-1,1]+[0,76,-13],mount*[-1,1,-1]])+[0,0,-bp[2]]
 C=np.array(dims[0][:2]);body_cx=bp[1][1]+bp[0]/2
 def rotate(v,angle):
  c,s=np.cos(np.radians(angle)),np.sin(np.radians(angle))
  return v@np.array([[c,s,0],[-s,c,0],[0,0,1.]])
 def cylinder(start,end,r=2,segments=10):
  start,end=np.array(start),np.array(end);axis=end-start;axis=axis/np.linalg.norm(axis)
  v=np.cross(axis,[0,0,1] if abs(axis[2])<.9 else [0,1,0]);v=v/np.linalg.norm(v);u=np.cross(axis,v)
  ring=np.array([r*(v*np.cos(th)+u*np.sin(th)) for th in np.arange(segments)*2*np.pi/segments])
  return np.array([t for i in range(segments) for t in [[start+ring[i],end+ring[i],end+ring[(i+1)%segments]],[start+ring[i],end+ring[(i+1)%segments],start+ring[(i+1)%segments]]]])
 def leg_scene(row):
  t,id,(hip,servo,q),anchor,ball=row;side=1 if id<2 else -1
  def world(v,angle=hip):return rotate(v,angle)[...,[1,2,0]]*[1,side,1]+anchor
  scene={'upper':world(upper),'motor':world(motor),'mount':world(mount,0)}
  for k,v in parts.items():scene[k]=world(rotate(v,q)+np.r_[C,dims[4]])
  p1=dims[2]*np.array([np.cos(np.radians(servo)),np.sin(np.radians(servo))]);p2=C+rotate(np.array([dims[3],0.,0.]),q)[:2]
  rod=world(np.array([np.r_[p1,41],np.r_[p2,41]]));scene['rod']=cylinder(*rod)
  return scene
 colors={'body':(133,155,166),'upper':(229,184,44),'motor':(188,198,205),'mount':(177,190,198),'core':(61,82,94),'sole':(28,38,46),'connector':(229,184,44),'shin':(229,184,44),'rod':(212,221,224)}
 accents=['#c47720','#267caa','#bd4f63','#7b61ad'];names=['ЛП','ЛЗ','ПП','ПЗ']
 def ground(dx):
  v=[];c=[]
  for x in GRID:
   for y in GRID:
    # World grid translates past the following camera.
    xx=x-dx%100;col=(220,227,220) if ((x+y)//50)%2 else (228,234,227)
    v.extend([[[xx,y,-1],[xx+50,y,-1],[xx+50,y+50,-1]],[[xx,y,-1],[xx+50,y+50,-1],[xx,y+50,-1]]]);c.extend([col,col])
  return np.asarray(v),np.asarray(c)
 def scene_for(kind,index):
  t=index/N;gait='run' if kind in ['run','orbit'] else 'walk';idx=index%N
  if kind=='single':batch=[poses['single'][idx]]
  else:batch=poses[gait][4*idx:4*idx+(2 if kind=='left_pair' else 4)]
  # Rows repeat exactly each cycle; the camera follows the accumulated body advance.
  center_x=direction*length*batch[0][0]
  scenes=[];tints=[];balls=[]
  def add(key,v):scenes.append(v-[center_x,0,0]);tints.append(np.tile(colors[key],(len(v),1)))
  for row in batch:
   for key,v in leg_scene(row).items():
    if kind!='single' or key!='mount':add(key,v)
   balls.append(np.array(row[4])-[center_x,0,0])
  if kind in ['walk','run','orbit']:
   add('body',body[:,:,[1,2,0]]+[center_x-body_cx,-bp[3],batch[0][3][2]])
  # The 2-leg views are centered between the hips; single stays at its own hip.
  gv,gc=ground(direction*length*t);scenes.insert(0,gv);tints.insert(0,gc)
  return np.concatenate(scenes).astype('f4'),np.concatenate(tints).astype('f4'),balls,batch
 def camera(kind,index):
  orbit=kind=='orbit';az=np.radians(-65+360*index/(4*N) if orbit else (-90 if kind in ['single','left_pair'] else -74))
  el=np.radians(22 if orbit else (7 if kind in ['single','left_pair'] else 16))
  eye=np.array([np.cos(az)*np.cos(el),np.sin(az)*np.cos(el),np.sin(el)])
  right=np.array([-np.sin(az),np.cos(az),0]);up=np.cross(eye,right)
  basis=np.array([right,up,eye],dtype='f4')
  return basis,el
 def render(kind,index):
  tri,col,balls,batch=scene_for(kind,index);t=index/N;orbit=kind=='orbit'
  basis,el=camera(kind,index);right,up,eye=basis
  scale=scales[kind]
  # Fixed framing: target follows body X, with the original 170-mm target Z.
  cx,cy=W/2,379.5+170*scale*np.cos(el)
  model=tri[GROUND_TRIANGLES:]
  proj=model@basis[:2].T
  assert cx+scale*proj[:,:,0].min()>20 and cx+scale*proj[:,:,0].max()<W-20,(kind,index,'horizontal clipping')
  assert cy-scale*proj[:,:,1].max()>116 and cy-scale*proj[:,:,1].min()<H-74,(kind,index,'vertical clipping')
  img=np.empty((H,W,3),np.uint8);img[:]=[245,247,242];depth=np.full((H,W),-np.inf,'f4')
  lib.raster(W,H,len(tri),tri.ctypes.data_as(fp),col.ctypes.data_as(fp),basis.ctypes.data_as(fp),scale,cx,cy,img.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8)),depth.ctypes.data_as(fp))
  image=Image.fromarray(img);d=ImageDraw.Draw(image)
  d.rectangle((0,0,W,112),fill='#f5f7f2');d.rectangle((0,H-73,W,H),fill='#f5f7f2')
  title={'single':'1 · Одна нога','left_pair':'2 · Левые передняя и задняя','walk':'3 · Четыре ноги с корпусом','run':'4 · Бег: диагональные пары','orbit':'5 · Бег: круговой облёт'}[kind]
  d.text((32,17),title,font=F[28],fill='#263d49')
  d.text((32,59),('ВПЕРЁД (−X)' if orbit else 'ВПЕРЁД ←')+'   ·   200 мм за цикл   ·   замедленный показ',font=F[19],fill='#526975')
  if orbit:d.text((32,88),f'Облёт {360*index/(4*N):.0f}° / 360°   ·   4 цикла за 48 с',font=F[15],fill='#526975')
  else:d.text((32,88),'Один цикл за 12 с',font=F[15],fill='#526975')
  if kind!='single':
   for j,row in enumerate(batch):
    b=balls[j];screen=(cx+scale*np.dot(b,right),cy-scale*np.dot(b,up));x,y=screen
    assert 10<x<W-10 and 120<y<H-75,(kind,index,screen)
    d.ellipse((x-12,y-12,x+12,y+12),fill=accents[row[1]],outline='#ffffff',width=2)
    d.text((x,y),str(row[1]+1),font=F[15],fill='white',anchor='mm')
   legend='   '.join(f'{row[1]+1} — {names[row[1]]}' for row in batch)
   d.text((32,H-62),legend+'   (Л/П: сторона, П/З: перед/зад)',font=F[17],fill='#405966')
  else:d.text((32,H-62),'Текущая форма голени · реальный привод колена',font=F[17],fill='#405966')
  duty_now=single_duty if kind=='single' else (rcfg[0] if kind in ['run','orbit'] else duty)
  offsets=[0,.5,.5,0] if kind in ['run','orbit'] else [0,.5,.25,.75]
  contacts=sum((row[0]+(0 if kind=='single' else offsets[row[1]]))%1<duty_now for row in batch)
  d.text((32,H-33),f'Фаза цикла: {t%1:.2f}   ·   на опоре: {contacts}   ·   кинематическая модель',font=F[17],fill='#526975')
  return image
 variants=[('single','walking_step.gif'),('left_pair','left_pair_walk.gif'),('walk','quadruped_walk.gif'),('run','quadruped_run.gif'),('orbit','quadruped_run_orbit.gif')]
 qa=[];scales={}
 for kind,name in variants:
  if a.only and kind!=a.only:continue
  total=N*(4 if kind=='orbit' else 1);frames=[];thumbs=[]
  extents=np.zeros(2)
  for i in range(0,total,max(1,N//20)):
   tri,_,_,_=scene_for(kind,i);basis,el=camera(kind,i)
   xy=tri[GROUND_TRIANGLES:]@basis[:2].T;xy[:,:,1]-=170*np.cos(el)
   extents=np.maximum(extents,np.abs(xy).max(axis=(0,1)))
  scales[kind]=min(442/extents[0],244/extents[1])*.94
  print(f'{kind}: fixed camera scale {scales[kind]:.3f}',flush=True)
  for i in range(total):
   frame=render(kind,i);frames.append(frame)
   if i in [0,total//4,total//2,3*total//4]:thumbs.append(frame.resize((480,360)))
   if i%20==0:print(f'{kind}: {i}/{total}',flush=True)
  # One palette across all frames avoids distracting color flicker.
  palette=frames[0].quantize(colors=240)
  converted=[f.quantize(palette=palette,dither=Image.Dither.NONE) for f in frames]
  duration=round(12000/N/10)*10
  frames[0].save(R/(name.replace('.gif','_preview.png')))
  converted[0].save(R/name,save_all=True,append_images=converted[1:],duration=duration,loop=0,optimize=False,disposal=2)
  sheet=Image.new('RGB',(960,720),'white')
  for j,im in enumerate(thumbs):sheet.paste(im,((j%2)*480,(j//2)*360))
  sheet.save(R/(name.replace('.gif','_contact_sheet.png')))
  with Image.open(R/name) as gif:
   assert gif.n_frames==total
   dur=sum((gif.seek(j) or gif.info['duration']) for j in range(gif.n_frames))
   assert dur==total*duration
   qa.append({'file':name,'frames':total,'duration_ms':dur,'size':list(gif.size),'loops':gif.info.get('loop'),'gait_cycles':4 if kind=='orbit' else 1,'source':'native OpenSCAD angle probes and STL geometry'})
  print(f'Saved {name}: {dur/1000:g} s',flush=True)
 (R/('gait_gifs_manifest'+('_'+a.only if a.only else '')+'.json')).write_text(json.dumps(qa,ensure_ascii=False,indent=2))
