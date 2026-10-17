"""Reproducible CAD checks and approximate axial/bending screening of native foot variants.
The heel frame, local joints, torsion and material strength are not validated.
"""
from pathlib import Path
import re,json
import numpy as np
import argparse,subprocess,tempfile,shutil
parser=argparse.ArgumentParser(description="Geometry verification and preliminary beam screening; not strength certification.")
parser.add_argument('--mesh',type=Path,help='Reuse the all-checks STL instead of rendering it again')
parser.add_argument('--openscad',default=shutil.which('openscad') or '/Applications/OpenSCAD-2021.01.app/Contents/MacOS/OpenSCAD')
args=parser.parse_args()
R=Path(__file__).resolve().parent
source=(R.parent/'foots.scad').read_text()
h_active='design_variant="h";' in source
if h_active:source=(R.parent/'foots_h.scad').read_text()
if args.mesh:
 raw=args.mesh.read_text()
else:
 with tempfile.TemporaryDirectory(prefix='vptc-foot-check-') as d:
  mesh=Path(d)/'verification.stl'
  run=subprocess.run([args.openscad,'-o',str(mesh),'-D','check="all"',str(R/'check_fit.scad')],capture_output=True,text=True)
  if run.returncode or 'WARNING:' in run.stderr or 'ERROR:' in run.stderr:
   raise RuntimeError(run.stderr)
  raw=mesh.read_text()
alltri=np.array(re.findall(r'vertex\s+([-+\deE.]+)\s+([-+\deE.]+)\s+([-+\deE.]+)',raw),dtype=float).reshape(-1,3,3)
names=['core','sole','connector','shin','connector_and_core','abutment_overlap','core_shin_overlap','core_sole_overlap','integrated_shin_overlap','socket_obstruction','pin_obstruction','joint_trim_residue','socket_geometry']
centers=alltri[:,:,2].mean(axis=1)
parts={name:alltri[np.abs(centers-i*60)<29].copy()-[0,0,i*60] for i,name in enumerate(names)}
report={'revision':7 if h_active else 5,'variant':'constant_H' if h_active else 'tapered_box','units':'mm','robot_mass_kg':6,'nozzle_mm':.4,'material':'PLA+ (manufacturer and print strength unspecified)','parts':{}}
for name,tri in parts.items():
 if not len(tri):report['parts'][name]={'triangles':0,'volume_mm3':0};continue
 pts,indices=np.unique(tri.reshape(-1,3),axis=0,return_inverse=True);faces=indices.reshape(-1,3)
 edges=np.concatenate([faces[:,[0,1]],faces[:,[1,2]],faces[:,[2,0]]]);_,cnt=np.unique(np.sort(edges,axis=1),axis=0,return_counts=True)
 parents=np.arange(len(pts))
 def find(a):
  while parents[a]!=a:parents[a]=parents[parents[a]];a=parents[a]
  return a
 for a,b in edges:
  a,b=find(a),find(b)
  if a!=b:parents[b]=a
 roots=np.array([find(i) for i in faces[:,0]])
 count=len(set(roots))
 component_volumes=[float(np.einsum('ij,ij->i',tri[roots==r,0],np.cross(tri[roots==r,1],tri[roots==r,2])).sum()/6) for r in set(roots)]
 solid_components=sum(v>1e-6 for v in component_volumes)
 void_components=sum(v < -1e-6 for v in component_volumes)
 vol=float(np.einsum('ij,ij->i',tri[:,0],np.cross(tri[:,1],tri[:,2])).sum()/6)
 report['parts'][name]={'triangles':len(tri),'volume_mm3':round(vol,4),'watertight':bool(np.all(cnt==2)),'surface_components':count,'solid_components':solid_components,'enclosed_void_shells':void_components,'bounds_mm':np.round([pts.min(0),pts.max(0)],4).tolist()}
 assert np.all(cnt==2),(name,'nonmanifold')
 assert vol>0,(name,vol)
for name in ['core','sole','shin','connector_and_core']:assert report['parts'][name]['solid_components']==1,name
for name in ['core_shin_overlap','core_sole_overlap','integrated_shin_overlap','socket_obstruction','pin_obstruction','joint_trim_residue']:assert report['parts'][name]['volume_mm3']==0,(name,report['parts'][name])
if h_active:assert report['parts']['abutment_overlap']['volume_mm3']>0
else:assert abs(report['parts']['abutment_overlap']['volume_mm3']-11.28)<.01
assert abs(report['parts']['connector_and_core']['bounds_mm'][0][2]+11.75)<1e-5
report['mass_estimate']={'assumed_density_g_cm3':1.24,'solid_geometry_rigid_with_connector_g':round(report['parts']['connector_and_core']['volume_mm3']*.00124,1),'sole_volume_cm3':round(report['parts']['sole']['volume_mm3']/1000,2),'note':'CAD solid-volume estimate; excludes hardware, slicer voids, support, brim. Density assumption, not measured filament.'}
# Signed void surfaces are retained during integration and subtracted from volume.
# Independent cut-plane integration on actual rendered mesh; no nominal beam sections.
tri=parts['core']
def value(name):return float(re.search(r'^'+name+r'=([-+0-9.]+);',source,re.M).group(1))
L=value('h_length') if h_active else value('blade_length')*value('distal_scale')
S=0 if h_active else value('blade_sweep')
end_x=25+L;pad_x=end_x+(4 if h_active else 1)
pad_y=value('h_pad_sweep') if h_active else S+8
pad_z=0 if h_active else value('bed_z')+value('body_depth')/2
roll=value('h_mount_roll' if h_active else 'mount_roll');roll_cos=round(float(np.cos(np.radians(roll))))
side=(1 if h_active else value('curve_side'))*roll_cos
pad_z*=roll_cos
report['mounting']={'roll_about_connector_X_deg':roll,'cuff_transformed':False,'cuff_exterior_reshaped':h_active,'rigid_print_roll_deg':-roll}
P=np.array([[25,0],[25+.40*L,0],[25+.82*L,8],[25+L,42]] if h_active else
 [[25,0],[25+.32*L,0],[25+.72*L,.30*S],[25+L,S]],float)
reference_shape=h_active and 'h_shape="base";' not in source
if reference_shape:
 y=-value('h_connector_bend');drop=value('h_reverse_drop')
 P=np.array([[25,y],[25+.16*L,y+.16*L*np.tan(np.radians(value('h_root_angle')))],
  [25+.32*L,y-drop],[25+.48*L,y-drop/2]],float)
 Q=np.array([P[3],2*P[3]-P[2],[25+.80*L,value('h_arc_control')],[25+L,value('h_toe_rise')]])
 Q[:,1]*=side
P[:,1]*=side
def bezier(a,t):
 a=np.array(a,copy=True)
 while len(a)>1:a=(1-t)*a[:-1]+t*a[1:]
 return a[0]
def derivative(a,t,order=1):
 for _ in range(order):a=(len(a)-1)*np.diff(a,axis=0)
 return bezier(a,t)
if reference_shape:
 cp=np.array([[-15,0],[-2,0],[12,value('h_connector_bend')-13*np.tan(np.radians(-value('h_root_angle')))],[25,value('h_connector_bend')]],float)
 ratio=3*L*.16/39
 v0=ratio*derivative(cp,1);a0=ratio**2*derivative(cp,1,2)
 v1=derivative(Q,0);a1=derivative(Q,0,2)
 p0,p5=P[0],P[3];p1=p0+v0/5;p4=p5-v1/5
 P=np.array([p0,p1,2*p1-p0+a0/20,2*p4-p5+a1/20,p4,p5])
 def curvature(a,t):
  v=derivative(a,t);acc=derivative(a,t,2)
  return float((v[0]*acc[1]-v[1]*acc[0])/np.linalg.norm(v)**3)
 join_error=abs(curvature(cp,1)-curvature(P,0))
 assert join_error<1e-10,join_error
 assert np.allclose(derivative(cp,1)/np.linalg.norm(derivative(cp,1)),derivative(P,0)/np.linalg.norm(derivative(P,0)))
 assert np.allclose(derivative(P,1),derivative(Q,0))
 assert np.allclose(derivative(P,1,2),derivative(Q,0,2))
 report['curve_continuity']={'cuff_beam_signed_curvature_per_mm':[curvature(cp,1),curvature(P,0)],'cuff_beam_tangent_and_curvature_matched':True,'beam_middle_C2':True,'distal_cubic_and_pad_unchanged':True}
def controls(t):
 if not reference_shape:return P,t
 return (P,2*t) if t<=.5 else (Q,2*t-1)
def curve(t):
 a,s=controls(t);return bezier(a,s)
def tangent(t):
 a,s=controls(t);v=derivative(a,s);return v/np.linalg.norm(v)
angle=np.radians(value('h_pad_angle' if h_active else 'pad_angle'));u=np.array([np.cos(angle),side*np.sin(angle),0]);pad=np.array([pad_x,side*pad_y,pad_z]);contact=pad+(value('h_pad_radius')+value('h_sole_lift') if h_active else value('sole_radius'))*u
neutral=(contact-np.array([-47,0,0]));neutral/=np.linalg.norm(neutral)
cases={'two_feet_static':-6*9.81/2*u,'one_foot_static':-6*9.81*u,'150N_reference_mount_direction':-150*u,'150N_connector_axis':np.array([-150.,0,0]),'150N_reference_plus_45N_lateral':-150*u+np.array([0,0,45.])}
rows=[]
for t in np.linspace(.035,.64 if h_active else .72,37):
 c2=curve(t);tv=tangent(t);frame=np.array([[tv[0],tv[1],0],[-tv[1],tv[0],0],[0,0,1.]])
 origin=np.r_[c2,0.];local=(tri-origin)@frame.T
 normals=np.cross(local[:,1]-local[:,0],local[:,2]-local[:,0])
 seg=[]
 for k,tv3 in enumerate(local):
  xs=tv3[:,0]
  if xs.min()>=0 or xs.max()<=0:continue
  q=[]
  for i,j in [(0,1),(1,2),(2,0)]:
   if xs[i]*xs[j]<0:q.append(tv3[i]+(tv3[j]-tv3[i])*(-xs[i]/(xs[j]-xs[i])))
  if len(q)!=2:continue
  a,b=q;direction=np.cross([1,0,0],normals[k])
  if np.dot(b-a,direction)<0:a,b=b,a
  seg.append([a[1:],b[1:]])
 seg=np.array(seg);a,b=seg[:,0],seg[:,1];cr=a[:,0]*b[:,1]-b[:,0]*a[:,1];A=cr.sum()/2
 assert A>0,(t,A)
 cy=((a[:,0]+b[:,0])*cr).sum()/(6*A);cz=((a[:,1]+b[:,1])*cr).sum()/(6*A)
 iz=((a[:,0]**2+a[:,0]*b[:,0]+b[:,0]**2)*cr).sum()/12-A*cy*cy
 iy=((a[:,1]**2+a[:,1]*b[:,1]+b[:,1]**2)*cr).sum()/12-A*cz*cz
 izy=((2*a[:,0]*a[:,1]+a[:,0]*b[:,1]+b[:,0]*a[:,1]+2*b[:,0]*b[:,1])*cr).sum()/24-A*cy*cz
 moment_matrix=np.array([[iz,izy],[izy,iy]])
 boundary=np.concatenate([a,b]);boundary-=np.array([cy,cz])
 width=float(np.ptp(boundary[:,0]));depth=float(np.ptp(boundary[:,1]))
 if h_active:
  assert abs(width-value('h_width'))<.035,(t,'width',width)
  assert abs(depth-value('h_depth'))<.001,(t,'depth',depth)
 row={'t':round(float(t),4),'width_mm':round(width,4),'depth_mm':round(depth,4),'area_mm2':round(float(A),2),'I_z_mm4':round(float(iz),1),'I_y_mm4':round(float(iy),1),'normal_stress_MPa':{}}
 for name,force in cases.items():
  f=frame@force;r=frame@(contact-origin)-np.array([0,cy,cz]);m=np.cross(r,f)
  coeff=np.linalg.solve(moment_matrix,[-m[2],m[1]])
  stress=f[0]/A+boundary@coeff
  row['normal_stress_MPa'][name]=round(float(abs(stress).max()),3)
 rows.append(row)
report['load_screen']={'method':'Variable tangent-plane sections integrated from the actual CAD mesh; linear axial plus biaxial bending equilibrium only. NOT FEA, fatigue analysis or capacity certification. Long main beam only; excludes heel frame and connector/pin.','peak_abs_longitudinal_normal_stress_MPa':{name:max(r['normal_stress_MPa'][name] for r in rows) for name in cases},'forces_N':{name:np.round(force,3).tolist() for name,force in cases.items()},'reference_contact_point_mm':contact.round(3).tolist(),'contact_model_note':'Reference direction is a load case, not a fixed spherical contact normal. Actual surface contact varies with hip and knee pose.','nominal_150N_is_6kg_on_one_foot_at_g_factor':round(150/(6*9.81),3),'connector_knee_axis_moment_Nm_150N_reference':round(float(np.linalg.norm(np.cross(contact-np.array([-47,0,0]),cases['150N_reference_mount_direction']))/1000),2),'sections':rows,'missing':['local stress concentrations and curved-beam correction','shear and open-channel torsion','heel frame, retention and M4 bearing stresses','FDM layer adhesion and specimen strength','fatigue, impact time history, contact and full gait collisions'],'material_safety_factor':'NOT assigned; actual PLA+ manufacturer, print quality and joint proof tests are required.'}
# Check the actual rendered slot and the full native shin, including the new tongue.
if h_active:
 assert report['parts']['socket_geometry']['volume_mm3']>0
 def section_points(mesh,origin,axis,frame):
  found=[]
  for a,b in [(0,1),(1,2),(2,0)]:
   v,w=mesh[:,a],mesh[:,b];dv=(v-origin)@axis;dw=(w-origin)@axis
   keep=dv*dw<0
   points=v[keep]+(w[keep]-v[keep])*(-dv[keep]/(dw[keep]-dv[keep]))[:,None]
   found.append((points-origin)@frame.T)
  return np.concatenate(found)
 angle_j=np.radians(value('h_joint_angle'));axis_j=np.array([np.cos(angle_j),np.sin(angle_j),0.])
 frame_j=np.array([[-np.sin(angle_j),np.cos(angle_j),0.],[0,0,1.]])
 origin_j=np.array([0,value('h_joint_offset'),0.])
 directions=np.array([[1,0],[-1,0],[0,1],[0,-1],[1,1],[1,-1],[-1,1],[-1,-1]],float)
 directions/=np.linalg.norm(directions,axis=1)[:,None]
 mating=[]
 for x in [-12.13,-7.17,.13,7.19,14.11]:
  origin=origin_j+x*axis_j
  pocket=section_points(parts['socket_geometry'],origin,axis_j,frame_j)
  tongue=section_points(parts['shin'],origin,axis_j,frame_j)
  slope=(value('h_joint_tip_low')-value('h_joint_low'))/(value('h_joint_end')-value('h_joint_break')) if x>value('h_joint_break') else 0
  face_normals=np.array([[0,1,0],[slope,-1,0],[0,0,1],[0,0,-1],
   [0,1,1],[0,1,-1],[slope,-1,1],[slope,-1,-1]],float)
  face_normals/=np.linalg.norm(face_normals,axis=1)[:,None]
  face_directions=face_normals@frame_j.T
  face_gaps=(pocket@face_directions.T).max(0)-(tongue@face_directions.T).max(0)
  assert np.all(abs(face_gaps-value('h_joint_clearance'))<.002),(x,face_gaps)
  mating.append({'along_insertion_axis_mm':x,'gaps_normal_to_eight_faces_mm':face_gaps.round(5).tolist()})
 end_gap=parts['socket_geometry'][:,:,0].max()-parts['shin'][:,:,0].max()
 assert abs(end_gap-value('h_joint_end_gap'))<.001,end_gap
 # The inserted end continues the native 15 x 18 rectangle at the old interface.
 for x in [-16.31,-16.01,-15.99,-15.71,-12.13]:
  section=section_points(parts['shin'],np.array([x,0.,0.]),np.array([1.,0.,0.]),np.array([[0.,1.,0.],[0.,0.,1.]]))
  assert np.allclose(section.min(0),[-7.5,-9],atol=.002),(x,section.min(0))
  assert np.allclose(section.max(0),[7.5,9],atol=.002),(x,section.max(0))
 walls=[]
 for position in [-4.13,.17,3.51,4.11,8.19,12.13,15.17,20.11]:
  origin=origin_j+position*axis_j
  pocket=section_points(parts['socket_geometry'],origin,axis_j,frame_j)
  cuff=section_points(parts['connector'],origin,axis_j,frame_j)
  d=(cuff@directions[:4].T).max(0)-(pocket@directions[:4].T).max(0)
  assert min(d[:2])>=value('h_connector_wall')-.01,(position,'wall',d)
  walls.append({'along_insertion_axis_mm':position,'lateral_walls_mm':d[:2].round(4).tolist(),'cheeks_mm':d[2:].round(4).tolist()})
 cuff_sections=[]
 cp=np.array([[-15,0],[-2,0],[12,value('h_connector_bend')-13*np.tan(np.radians(-value('h_root_angle')))],[25,value('h_connector_bend')]],float)
 for t in [.3,.5,.7,.9]:
  p=(1-t)**3*cp[0]+3*(1-t)**2*t*cp[1]+3*(1-t)*t*t*cp[2]+t**3*cp[3]
  v=3*(1-t)**2*(cp[1]-cp[0])+6*(1-t)*t*(cp[2]-cp[1])+3*t*t*(cp[3]-cp[2]);v/=np.linalg.norm(v)
  points=section_points(parts['connector'],np.r_[p,0],np.r_[v,0],np.array([[-v[1],v[0],0],[0,0,1.]]))
  width,depth=np.ptp(points,axis=0)
  assert abs(width-value('h_width'))<.01 and abs(depth-value('h_depth'))<.001,(t,width,depth)
  cuff_sections.append({'t':t,'width_mm':round(float(width),5),'depth_mm':round(float(depth),5)})
 report['connector_outer_section']={'checks':cuff_sections,'added_external_reinforcement':False}
 report['joint_fit']={'type':'native square 15 x 18 bar continues straight; only the drawn distal XY chamfer is removed',
  'insertion_angle_deg':value('h_joint_angle'),'insertion_axis_Y_offset_mm':value('h_joint_offset'),
  'housing_walls':walls,'housing_wall_scope':'Load-bearing socket region beyond the open mouth bevel.',
  'tongue_root_section_mm':[value('h_joint_width'),value('h_joint_depth')],
  'longitudinal_profile_XY_mm':[[-16.3,value('h_joint_low')],[value('h_joint_break'),value('h_joint_low')],[value('h_joint_end'),value('h_joint_tip_low')],[value('h_joint_end'),value('h_joint_high')],[-16.3,value('h_joint_high')]],
  'socket_root_section_mm':[value('h_joint_width')+2*value('h_joint_clearance'),value('h_joint_depth')+2*value('h_joint_clearance')],
  'nominal_face_clearance_mm':value('h_joint_clearance'),'measured_cross_sections':mating,
  'end_clearance_mm':round(float(end_gap),5),'old_corner_notch_removed':True,'straight_bar_continuation_verified':True,
  'full_shin_one_connected_solid':True,'pin_axis_connector_mm':[0,0],
  'retention':'M4 through bolt and nut with washers; clamp the mating cheeks. Fit clearance alone does not lock the connection.',
  'print_fit_note':'CAD clearances only. Actual fit depends on extrusion calibration and shrinkage.'}
report['geometry_checks']={'rigid_print_face_after_placement_z_mm':0,'connector_and_blade_one_solid':True,'sole_one_solid':True,'unintended_core_shin_overlap':False,'unintended_core_sole_overlap':False,'intentional_abutment_overlap_mm':.02,'body_supports':'Print job undoes mounting roll for the whole integrated part. Hollow section has a 45-degree vaulted ceiling with only a 1.2 mm apex bridge, and a flat back on the bed. Original connector ceiling retains a 15.4 mm bridge and needs bridge qualification or local slicer support.'}
if h_active:
 report['constant_section']={'normal_width_mm':value('h_width'),'depth_mm':value('h_depth'),'flange_mm':value('h_flange'),'web_mm':value('h_web'),'checked_cut_planes':len(rows),'width_range_mm':[min(r['width_mm'] for r in rows),max(r['width_mm'] for r in rows)],'depth_range_mm':[min(r['depth_mm'] for r in rows),max(r['depth_mm'] for r in rows)],'scope':'Uniform main beam only; the distal fork widens into two branches and a TPU mounting plate.'}
 report['shape']={'preset':'base' if 'h_shape="base";' in source else 's_curve','root_angle_deg':value('h_root_angle'),'arc_control_mm':value('h_arc_control'),'connector_bend_mm':value('h_connector_bend'),'connector_lateral_wall_min_mm':value('h_connector_wall'),'curve':'Quintic reverse arc matches cuff tangent and signed curvature, then joins the unchanged forward cubic with C2 continuity. Straight socket and pin axis retained.','socket_matches_drawn_longitudinal_profile':True,'original_pin_axis_and_mouth_cut_retained':True,'pad_location_relative_to_accepted_reference_variant_unchanged':True,'pad_sweep_mm':value('h_pad_sweep'),'pad_angle_deg':value('h_pad_angle'),'reverse_drop_mm':value('h_reverse_drop'),'toe_rise_mm':value('h_toe_rise')}
 report['geometry_checks']['integrated_shin_overlap']=False
 report['geometry_checks']['socket_obstruction']=False
 report['geometry_checks']['pin_obstruction']=False
 report['geometry_checks']['joint_trim_residue']=False
 report['geometry_checks'].pop('intentional_abutment_overlap_mm')
 report['geometry_checks']['body_supports']='Open H section with 45 degree haunches below its central web and a 1.2 mm bridge. Two flanges lie on Z=0. No trapped support. The socket ceiling may need accessible local slicer support.'
(R/'fit_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({k:report[k] for k in ['mass_estimate','geometry_checks']},ensure_ascii=False,indent=2))
print(json.dumps(report['load_screen']['peak_abs_longitudinal_normal_stress_MPa'],indent=2))
