"""Export isolated native CAD parts and render a two-view PNG catalog.

Run with a Python having NumPy and Pillow, OpenSCAD CLI and clang++.
The reference model is a saved generator result; changing generator inputs
requires regenerating it first (see README). Export caches live in the system temporary folder.
"""
from pathlib import Path
import argparse,concurrent.futures,ctypes,hashlib,json,re,struct,subprocess,tempfile,platform,shutil,os
import numpy as np
from PIL import Image,ImageDraw,ImageFont

D=Path(__file__).resolve().parent;ROOT=D.parents[1];OUT=ROOT/'images/parts'
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--only',nargs='*');p.add_argument('--jobs',type=int,default=3)
p.add_argument('--openscad',default=shutil.which('openscad') or '/Applications/OpenSCAD-2021.01.app/Contents/MacOS/OpenSCAD')
p.add_argument('--cache',type=Path,default=Path(tempfile.gettempdir())/'vptc-parts-catalog')
a=p.parse_args();a.cache.mkdir(exist_ok=True);OUT.mkdir(parents=True,exist_ok=True)
items=json.loads((D/'catalog.json').read_text());selected=[i for i in items if not a.only or i['id'] in a.only]
assert selected
# Imported foot files also affect shin() and all foot exports.
sources=[D/'reference_model.scad',ROOT/'output/foots.scad',ROOT/'output/foots_h.scad']
source_hash=hashlib.sha256(b''.join(f.read_bytes() for f in sources)).hexdigest()
font_path=next((str(p) for p in [Path(os.environ.get('CATALOG_FONT','/nonexistent')),Path('/System/Library/Fonts/Supplemental/Arial.ttf'),Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')] if p.is_file()),None)
if not font_path:raise RuntimeError('Set CATALOG_FONT to a Cyrillic-capable TrueType font')
font=lambda size:ImageFont.truetype(font_path,size)
F={size:font(size) for size in [15,18,20,23]}
cpp=ROOT/'output/foot/gait_raster.cpp';mac=platform.system()=='Darwin'
libpath=a.cache/('raster.dylib' if mac else 'raster.so')
compiler=shutil.which('clang++') or shutil.which('c++')
if not compiler:raise RuntimeError('Install clang++ or a C++17 compiler')
subprocess.run([compiler,'-O3','-std=c++17',*(['-dynamiclib'] if mac else ['-shared','-fPIC']),str(cpp),'-o',str(libpath)],check=True)
lib=ctypes.CDLL(str(libpath));fp=ctypes.POINTER(ctypes.c_float)
lib.raster.argtypes=[ctypes.c_int]*3+[fp]*3+[ctypes.c_float]*3+[ctypes.POINTER(ctypes.c_uint8),fp]
def mesh(path):
 b=path.read_bytes()
 if len(b)>=84 and len(b)==84+50*struct.unpack_from('<I',b,80)[0]:
  dt=np.dtype([('n','<f4',3),('v','<f4',(3,3)),('a','<u2')]);return np.frombuffer(b,dt,offset=84)['v'].astype('f4')
 return np.array(re.findall(rb'vertex\s+([-+\deE.]+)\s+([-+\deE.]+)\s+([-+\deE.]+)',b),dtype='f4').reshape(-1,3,3)
def export(item):
 id=item['id'];wrapper=D/(id+'.scad')
 text=f'// {item["title"]}. Open this file, F5 preview, F6 render, export STL.\nuse <{item["source"]}>\n$fn=60;\n'+item['call']+'\n'
 wrapper.write_text(text)
 geometry_text=f'use <{item["source"]}>\n$fn=60;\n'+item['call']+'\n'
 signature=hashlib.sha256((source_hash+geometry_text).encode()).hexdigest()
 cache=a.cache/signature;cache.mkdir(exist_ok=True);stl=cache/(id+'.stl');log=cache/(id+'.log')
 if not stl.exists():
  result=subprocess.run([a.openscad,'-o',str(stl),str(wrapper)],text=True,capture_output=True,timeout=600)
  log.write_text(result.stderr)
  if result.returncode or not stl.exists() or 'ERROR:' in result.stderr:raise RuntimeError(id+'\n'+result.stderr)
 tri=mesh(stl);assert len(tri)>0,id
 print(id+': exported '+str(len(tri))+' triangles',flush=True)
 return item,tri,signature,log.read_text()
def basis(elev,azim):
 e,b=np.radians([elev,azim]);eye=np.array([np.cos(b)*np.cos(e),np.sin(b)*np.cos(e),np.sin(e)])
 right=np.array([-np.sin(b),np.cos(b),0]);up=np.cross(eye,right)
 return np.array([right,up,eye],dtype='f4')
def panel(tri,rotation,color):
 W,H=600,500;xyz=tri@rotation.T
 low,high=xyz.reshape(-1,3).min(0),xyz.reshape(-1,3).max(0);center=(low+high)/2
 scale=min((W-85)/max(high[0]-low[0],.01),(H-85)/max(high[1]-low[1],.01))
 rgb=np.tile(color,(len(tri),1)).astype('f4');frame=np.full((H,W,3),[246,248,245],dtype='u1');depth=np.full((H,W),-np.inf,'f4')
 cx=W/2-scale*center[0];cy=H/2+scale*center[1]
 assert cx+scale*low[0]>20 and cx+scale*high[0]<W-20
 assert cy-scale*high[1]>20 and cy-scale*low[1]<H-20
 lib.raster(W,H,len(tri),tri.ctypes.data_as(fp),rgb.ctypes.data_as(fp),rotation.ctypes.data_as(fp),scale,cx,cy,frame.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8)),depth.ctypes.data_as(fp))
 # Depth contours make pockets visible even when parallel faces share lighting.
 edges=np.zeros((H,W),dtype=bool);threshold=max(.12,float(high[2]-low[2])*.012)
 for shift,axis in [(1,0),(1,1)]:
  other=np.roll(depth,shift,axis=axis);valid=np.isfinite(depth)&np.isfinite(other)
  diff=np.zeros_like(depth);np.subtract(depth,other,out=diff,where=valid)
  edges|=valid&(np.abs(diff)>threshold)
 frame[edges]=(frame[edges].astype(float)*.60).astype('u1')
 return Image.fromarray(frame)
reports=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=a.jobs) as pool:
 futures=[pool.submit(export,item) for item in selected]
 for future in concurrent.futures.as_completed(futures):
  item,tri,signature,log=future.result();id=item['id']
  color=(195,158,66) if item['group']=='Детали ноги и корпуса' else ((95,145,171) if item['group']=='Редуктор с установленным энкодером' else (148,171,184))
  if id=='foot_sole':color=(62,78,87)
  if id=='encoder_pcb':color=(58,143,106)
  image=Image.new('RGB',(1200,640),'#f6f8f5');draw=ImageDraw.Draw(image)
  draw.text((32,15),item['title'],font=F[23],fill='#263d49')
  image.paste(panel(tri,basis(38,-55),color),(0,60));image.paste(panel(tri,basis(90,-90),color),(600,60))
  draw=ImageDraw.Draw(image);draw.text((32,54),'Объёмный вид',font=F[18],fill='#58717b');draw.text((630,54),'Вид вдоль Z',font=F[18],fill='#58717b')
  bounds=tri.reshape(-1,3);span=bounds.max(0)-bounds.min(0)
  draw.text((32,581),'Габарит XYZ: '+' × '.join(f'{v:.2f}' for v in span)+' мм',font=F[18],fill='#405966')
  draw.text((32,611),id+'.scad   ·   из геометрии OpenSCAD   ·   размер двух видов подобран отдельно',font=F[15],fill='#58717b')
  image.save(OUT/(id+'.png'))
  warnings=[l for l in log.splitlines() if 'WARNING:' in l or 'ERROR:' in l]
  reports.append(dict(id=id,triangles=len(tri),bounds_xyz_mm=[bounds.min(0).tolist(),bounds.max(0).tolist()],export_signature=signature,warnings=warnings,image='images/parts/'+id+'.png',wrapper='docs/parts/'+id+'.scad'))
  print(id+': PNG saved'+(' · '+str(warnings) if warnings else ''),flush=True)
manifest=D/'render_manifest.json'
previous=json.loads(manifest.read_text())['parts'] if manifest.exists() else []
merged={r['id']:r for r in previous};merged.update({r['id']:r for r in reports})
manifest.write_text(json.dumps(dict(source_sha256=source_hash,reference_inputs=dict(resolution=600,ratio=19,roller_d=4,roller_h=5,rout=28,diameter=70,hole_angle=39),parts=[merged[i['id']] for i in items if i['id'] in merged]),ensure_ascii=False,indent=2)+'\n')
thumbs=Image.new('RGB',(1200,160*((len(items)+3)//4)),'white')
for n,item in enumerate(items):
 path=OUT/(item['id']+'.png')
 if path.exists():
  thumb=Image.open(path).resize((300,160));thumbs.paste(thumb,((n%4)*300,(n//4)*160))
thumbs.save(OUT/'contact_sheet.png')
print('Catalog ready: '+str(len(reports))+' images',flush=True)
