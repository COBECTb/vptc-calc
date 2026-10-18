// Progressive native walking previews. Animate $t from 0 to 1.
// Coordinates: forward is LEFT (-X), Z up, ground Z=0. Units: mm and degrees.
use <../vptc_roller.scad>
use <../foots_h.scad>

/* [Step] */
scene="quadruped"; // [single:One leg,left_pair:Left front and rear,quadruped:Four legs and body]
mode="step"; // [step,manual]
step_length=200; // [40:5:300]
step_height=30; // TPU clearance during transfer [10:5:60]
hip_height=300; // hip axis above ground [260:5:340]
stance_fraction=.60; // [0.5:0.05:0.75]
forward_direction=-1; // [-1:Left,1:Right]
world_motion=true; // false: watch the cycle in the moving body frame
show_path=true;
show_ground=true;
/* [Multiple legs] */
walk_stance_fraction=.75; // [0.75:0.05:0.9]
show_mounts=true;
show_labels=true;
/* [Running] */
run_stance_fraction=.40; // [0.30:0.05:0.45]
run_lift=50; // [30:5:70]
run_bounce=8; // [0:1:12]
/* [Manual angles] */
hip_manual_deg=30; // [0:1:60]
servo_manual_deg=20; // [-55:1:70]
/* [Hidden] */
$fn=48;
assert(step_length>0 && step_height>=0 && hip_height>0,"Invalid step dimensions");
assert(stance_fraction>0 && stance_fraction<1,"Stance fraction must be between 0 and 1");
assert(abs(forward_direction)==1,"Direction must be -1 or +1");

function step_rot(p,a)=[p[0]*cos(a)-p[1]*sin(a),p[0]*sin(a)+p[1]*cos(a)];
function step_wrap(a)=a-360*floor((a+180)/360);
function step_smooth(u)=u*u*u*(10-15*u+6*u*u);
function step_phase(t)=t-floor(t);
function step_configuration()=[step_length,step_height,hip_height,stance_fraction,forward_direction,h_contact_geometry()[1]];
function step_stance(t,duty=stance_fraction)=step_phase(t)<duty;
function step_body_x(t)=world_motion && mode=="step" ? forward_direction*step_length*t : 0;
function step_target(t,duty=stance_fraction,lift=step_height)=let(p=step_phase(t),u=(p-duty)/(1-duty),
 span=step_length*duty,d=-step_length*(1-duty))
 p<duty ? [forward_direction*(span/2-step_length*p),h_contact_geometry()[1]] :
 [forward_direction*(-span/2+d*u+(span-d)*step_smooth(u)),
 h_contact_geometry()[1]+lift*64*u*u*u*pow(1-u,3)];
function step_knee(servo)=let(k=leg_kinematic_parameters(),
 result=calculate_rigid_linkage(servo,k[1],k[2],k[3],[0,0,0],k[0]))
 assert(get_value(result,"solution_exists"),"Four-bar linkage cannot reach this servo angle")
 get_value(result,"angle2");
function step_shin_ball()=let(p=h_contact_geometry()[0])[-47-p[0],-p[1]];
// Solve the two-link ball-center target, then invert the REAL four-bar linkage.
function step_angles(t,duty=stance_fraction,body_height=hip_height,lift=step_height)=let(k=leg_kinematic_parameters(),c=[k[0][0],k[0][1]],
 b=step_shin_ball(),target=step_target(t,duty,lift),v=[target[1]-body_height,target[0]],
 cosine=(v*v-c*c-b*b)/(2*norm(c)*norm(b)))
 assert(abs(cosine)<=1,"Step target outside leg reach: reduce height/stride")
 let(q=acos(cosine)-atan2(b[1],b[0])+atan2(c[1],c[0]),
 local=c+step_rot(b,q),hip=step_wrap(atan2(v[1],v[0])-atan2(local[1],local[0])),
 p2=c+step_rot([k[3],0],q),
 ca=(p2*p2+k[2]*k[2]-k[1]*k[1])/(2*norm(p2)*k[2]))
 assert(abs(ca)<=1,"Step target outside four-bar reach")
 let(servo=atan2(p2[1],p2[0])-acos(ca))
 assert(abs(step_wrap(step_knee(servo)-q))<.001,"Wrong four-bar assembly branch")
 assert(q>=-44.646 && q<=54.204,"Outside previously screened rod angle range")
 [hip,servo,q];
function step_ball_from_angles(a,body_height=hip_height)=let(k=leg_kinematic_parameters(),
 b=step_rot([k[0][0],k[0][1]]+step_rot(step_shin_ball(),a[2]),a[0]))
 [b[1],b[0]+body_height];
function step_ball(t,duty=stance_fraction)=step_ball_from_angles(step_angles(t,duty));

module step_line(a,b,r=.65){hull(){translate(a)sphere(r=r,$fn=12);translate(b)sphere(r=r,$fn=12);}}
module walking_step(t=$t){
angles=mode=="manual" ? [hip_manual_deg,servo_manual_deg,step_knee(servo_manual_deg)] : step_angles(t);
// These are the angle variables used to pose the native OpenSCAD leg.
leg_angle1=angles[0];
servo_angle=angles[1];
body_x=step_body_x(t);
echo(step_phase=step_phase(t),phase=step_stance(t) ? "stance" : "swing",
 hip_angle=leg_angle1,servo_angle=servo_angle,knee_angle=angles[2],body_x=body_x);

// Native XY -> world ZX, native Z -> world Y. A proper rotation, no mirroring.
translate([body_x,0,hip_height])multmatrix([[0,1,0,0],[0,0,1,0],[1,0,0,0],[0,0,0,1]])
 rotate([0,0,leg_angle1])leg(servo=servo_angle);
color([.4,.5,.6,.35])translate([body_x,0,hip_height])rotate([90,0,0])cylinder(r=38,h=14,center=true);
if(show_ground){
 color([.72,.76,.72,.65])translate([forward_direction*step_length/2,55,-3])cube([500,220,6],center=true);
 for(x=[-300:25:300])color([.48,.55,.49])translate([x,55,.05])cube([.6,220,.1],center=true);
}
if(show_path && mode=="step"){
 for(i=[0:79])let(a=step_target(i/80),b=step_target((i+1)/80))
 color([.2,.55,.75,.5])step_line([body_x+a[0],-23,a[1]],[body_x+b[0],-23,b[1]]);
 color(step_stance(t) ? "ForestGreen" : "DodgerBlue")
 translate([body_x+step_target(t)[0],-23,step_target(t)[1]])sphere(r=2.5);
}
}
// Leg IDs: 0 left front, 1 left rear, 2 right front, 3 right rear.
// Quarter-cycle offsets and 75% stance leave at least three feet supporting.
function robot_leg_ids(view=scene)=view=="single" ? [0] : view=="left_pair" ? [0,1] : [0,1,2,3];
function robot_phase_offset(id,gait="walk")=gait=="run" ? [0,.5,.5,0][id] : [0,.5,.25,.75][id];
function robot_walk_configuration()=[walk_stance_fraction,body_gait_parameters()];
function robot_run_configuration()=[run_stance_fraction,run_lift,run_bounce];
function robot_duty(gait)=gait=="run" ? run_stance_fraction : walk_stance_fraction;
function robot_lift(gait)=gait=="run" ? run_lift : step_height;
function robot_body_height(t,gait="walk")=hip_height+(gait=="run" ? run_bounce*cos(720*(step_phase(t)-.45)) : 0);
function robot_joint_angles(t,id,gait="walk")=mode=="manual" ?
 [hip_manual_deg,servo_manual_deg,step_knee(servo_manual_deg)] :
 step_angles(t+robot_phase_offset(id,gait),robot_duty(gait),robot_body_height(t,gait),robot_lift(gait));
function robot_support_ids(t,gait="walk")=[for(id=[0:3])if(step_stance(t+robot_phase_offset(id,gait),robot_duty(gait)))id];
function robot_body_center_y()=let(b=body_gait_parameters())b[1][1]+b[0]/2;
function robot_native_pitch(id)=let(b=body_gait_parameters(),
 p=b[1]+[0,(id%2)*b[0],b[2]])
 id<2 ? p : [p[0],p[1],2*b[3]-p[2]];
function robot_hip_world(t,id,gait="walk")=let(b=body_gait_parameters(),p=robot_native_pitch(id))
 [step_body_x(t)+p[1]-robot_body_center_y(),p[2]-b[3],robot_body_height(t,gait)+p[0]];
function robot_ball_world(t,id,gait="walk")=let(anchor=robot_hip_world(t,id,gait),height=robot_body_height(t,gait),
 p=step_ball_from_angles(robot_joint_angles(t,id,gait),height),k=leg_kinematic_parameters())
 anchor+[p[0],(id<2 ? 1 : -1)*k[4],p[1]-height];

module robot_body_frame(t,gait="walk"){
 b=body_gait_parameters();
 translate([step_body_x(t),0,robot_body_height(t,gait)])
 multmatrix([[0,1,0,-robot_body_center_y()],[0,0,1,-b[3]],[1,0,0,0],[0,0,0,1]])children();
}
module robot_mount_frame(t,id,gait="walk"){
 b=body_gait_parameters();
 robot_body_frame(t,gait){
  if(id<2)translate([0,(id%2)*b[0],0])translate(b[1])children();
  else translate([0,0,2*b[3]])mirror([0,0,1])
   translate([0,(id%2)*b[0],0])translate(b[1])children();
 }
}
module robot_leg(t,id,gait="walk"){
 b=body_gait_parameters();phase=t+robot_phase_offset(id,gait);duty=robot_duty(gait);
 a=robot_joint_angles(t,id,gait);
 echo(gait_leg=id,gait=gait,phase=step_phase(phase),support=step_stance(phase,duty),
  hip_angle=a[0],servo_angle=a[1],knee_angle=a[2],hip_world=robot_hip_world(t,id,gait),ball_world=robot_ball_world(t,id,gait));
 robot_mount_frame(t,id,gait){
  if(show_mounts)leg_left_front_union(a1=0,a2=0,with_leg=false);
  translate([0,0,b[2]])rotate([0,0,a[0]])leg(servo=a[1]);
 }
 if(show_labels){
  color("SlateGray")translate(robot_hip_world(t,id,gait)+[0,0,45])
   rotate([90,0,0])linear_extrude(height=.5)text(["ЛП","ЛЗ","ПП","ПЗ"][id],size=12,halign="center");
 }
 if(show_path && mode=="step"){
  anchor=robot_hip_world(t,id,gait);side=id<2 ? 1 : -1;k=leg_kinematic_parameters();height=robot_body_height(t,gait);
  for(i=[0:47])let(a=step_target(i/48,duty,robot_lift(gait)),b=step_target((i+1)/48,duty,robot_lift(gait)))
   color([.2,.55,.75,.4])step_line(anchor+[a[0],side*k[4],a[1]-height],anchor+[b[0],side*k[4],b[1]-height]);
 }
}
module walking_robot(t=$t,view=scene,gait="walk"){
 assert(gait=="walk" || gait=="run","Unknown gait");
 assert(gait=="run" ? (run_stance_fraction>0 && run_stance_fraction<.5) : (walk_stance_fraction>=.75 && walk_stance_fraction<1),"Review stance fraction");
 assert(view=="left_pair" || view=="quadruped","Unknown preview scene");
 if(view=="quadruped")robot_body_frame(t,gait)color("LightSlateGray")body(parts=false);
 for(id=robot_leg_ids(view))robot_leg(t,id,gait);
 if(show_ground){
  b=body_gait_parameters();length=b[0]+step_length+360;
  color([.72,.76,.72,.65])translate([step_body_x(t),0,-3])cube([length,650,6],center=true);
  for(x=[50*floor((step_body_x(t)-length/2)/50):50:step_body_x(t)+length/2])
   color([.48,.55,.49])translate([x,0,.05])cube([.6,650,.1],center=true);
 }
}
if(scene=="single")walking_step($t);else walking_robot($t);
