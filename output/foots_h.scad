// Constant-section H foot. Units: mm, original foot_connector() coordinates.
// Rigid part: PLA+, 0.4 mm nozzle. Contact hemisphere: separate TPU print.
$fn=80;
h_part="assembly"; // assembly, core, integrated, print, sole, sole_print, section, tongue, socket
h_shape="s_curve"; // s_curve or base (accepted shape, also saved in foots_h_base.scad)
h_root_angle=-8; // degrees before mount roll: common tangent through cuff and beam
h_connector_bend=4; // mm: curved exterior, straight slide-in mating tongue
h_connector_wall=2.6; // required minimum side wall around the tilted slide-in socket
h_joint_angle=0; // straight insertion, retained by the joint inspection tools
h_joint_offset=0; // inspection frame; M4 pin stays at [0,0]
h_joint_clearance=.15; // normal clearance per mating face, adjustable for the printer
h_joint_setback=0; // obsolete corner cut disabled; original straight bar continues
h_joint_width=15; // original shin bar section
h_joint_low=-7.5; // continue the original bar edge without a step
h_joint_high=7.5; // the opposite edge remains straight
h_joint_break=3.5; // start of the drawn distal chamfer
h_joint_tip_low=-3;
h_joint_depth=18;
h_joint_bevel=0; // keep the original square 15 x 18 section; only the drawn end cut
h_joint_end=22;
h_joint_end_gap=.2;
h_arc_control=8; // mm: distal Bezier control; broad arc rather than a hooked tip
h_length=145;
h_reverse_drop=6; // mm: shallow reverse arc extends over the first half
h_toe_rise=26; // mm: tangent-matched forward arc toward the foot
h_width=24;
h_depth=23.5;
h_flange=3.2;
h_web=3.2;
h_bridge=1.2;
h_fork_width=6.4;
h_fork_t=.68;
h_body_end=.72;
h_pad_radius=20;
h_pad_angle=35;
h_pad_sweep=30;
h_gap=.30;
h_sole_lift=.30; // Rubber lip stands off the rigid plate; no coincident contact faces.
h_mount_roll=180;
h_root=25;
h_pad_x=h_root+h_length+4;
h_steps=96;
h_eps=.02;

function h_bezier(a,b,c,d,t)=(1-t)*(1-t)*(1-t)*a+
 3*(1-t)*(1-t)*t*b+3*(1-t)*t*t*c+t*t*t*d;
// Same family of silhouette as all references: shallow at the knee, steeper at the toe.
function h_base_path(t)=h_bezier([h_root,0],[h_root+h_length*.40,0],
 [h_root+h_length*.82,8],[h_root+h_length,42],t);
// A quintic reverse arc continues the cuff's tangent AND signed curvature,
// then joins the unchanged distal cubic with matching first/second derivatives.
function h_root_y()=h_shape=="base" ? 0 : -h_connector_bend;
function h_reverse_points()=let(y=h_root_y())[
 [h_root,y],[h_root+h_length*.16,y+h_length*.16*tan(h_root_angle)],
 [h_root+h_length*.32,y-h_reverse_drop],
 [h_root+h_length*.48,y-h_reverse_drop/2]];
function h_forward_points()=let(a=h_reverse_points())[
 a[3],2*a[3]-a[2],[h_root+h_length*.80,h_arc_control],
 [h_root+h_length,h_toe_rise]];
function h_reverse_smooth_points()=let(a=h_reverse_points(),b=h_forward_points(),
 // Reflect the cuff derivatives into the foot's pre-mount frame.
 cv=[39,39*tan(h_root_angle)],
 ca=[6*(24-h_root),6*(h_connector_bend+26*tan(h_root_angle))],
 ratio=3*h_length*.16/39,v0=ratio*cv,a0=ratio*ratio*ca,
 v1=3*(b[1]-b[0]),a1=6*(b[2]-2*b[1]+b[0]),
 p1=a[0]+v0/5,p4=a[3]-v1/5)
 [a[0],p1,2*p1-a[0]+a0/20,2*p4-a[3]+a1/20,p4,a[3]];
function h_bezier_points(a,t)=len(a)==1 ? a[0] :
 h_bezier_points([for(i=[0:len(a)-2])(1-t)*a[i]+t*a[i+1]],t);
function h_bezier_velocity(a,t)=h_bezier_points(
 [for(i=[0:len(a)-2])(len(a)-1)*(a[i+1]-a[i])],t);
function h_curve_points(t)=h_shape=="base" ?
 [[h_root,0],[h_root+h_length*.40,0],[h_root+h_length*.82,8],[h_root+h_length,42]] :
 (t<=.5 ? h_reverse_smooth_points() : h_forward_points());
function h_curve_time(t)=h_shape=="base" ? t : (t<=.5 ? 2*t : 2*t-1);
function h_path(t)=let(a=h_curve_points(t),s=h_curve_time(t))
 h_bezier_points(a,s);
function h_tangent(t)=let(a=h_curve_points(t),s=h_curve_time(t),
 v=h_bezier_velocity(a,s))v/norm(v);
function h_normal(t)=let(v=h_tangent(t))[-v[1],v[0]];
function h_pad_xy(s,v)=[h_pad_x+s*cos(h_pad_angle)-v*sin(h_pad_angle),
 h_pad_sweep+s*sin(h_pad_angle)+v*cos(h_pad_angle)];

// Y/Z section. Full width and depth are CONSTANT, measured normal to the path.
// Two flanges and a central web form H. Lower internal corners have 45-degree
// haunches; the underside closes with a 1.2 mm bridge, avoiding trapped support.
function h_section()=let(w=h_width/2,d=h_depth/2,a=w-h_flange,
 z=-h_web/2-(2*a-h_bridge)/2)
 [[-w,-d],[-a,-d],[-a,z],[-h_bridge/2,-h_web/2],
  [h_bridge/2,-h_web/2],[a,z],[a,-d],[w,-d],
  [w,d],[a,d],[a,h_web/2],[-a,h_web/2],[-a,d],[-w,d]];
function h_rect(w,d,r=1.2)=r==0 ? [[-w/2,-d/2],[w/2,-d/2],[w/2,d/2],[-w/2,d/2]] : [
 [-w/2,-d/2],[w/2,-d/2],[w/2,d/2-r],
 for(i=[1:4])let(a=90*i/4)[w/2-r+r*cos(a),d/2-r+r*sin(a)],
 [-w/2+r,d/2],
 for(i=[1:4])let(a=90+90*i/4)[-w/2+r+r*cos(a),d/2-r+r*sin(a)]
 ];
module h_sweep(rings,cap_triangles=[]){
 m=len(rings);n=len(rings[0]);
 caps=len(cap_triangles)>0 ? cap_triangles : [for(j=[1:n-2])[0,j,j+1]];
 polyhedron(points=[for(r=rings)each r],faces=concat(
 [for(f=caps)f],
 [for(f=caps)[for(j=[2:-1:0])(m-1)*n+f[j]]],
 [for(i=[0:m-2])for(j=[0:n-1])each let(
 a=i*n+j,b=i*n+(j+1)%n,c=(i+1)*n+(j+1)%n,d=(i+1)*n+j)
 [[c,b,a],[d,c,a]]]),convexity=20);
}
module h_beam(){
 h_sweep([for(i=[0:h_steps])let(t=h_body_end*i/h_steps,p=h_path(t),n=h_normal(t))
 [for(q=h_section())[p[0]+n[0]*q[0],p[1]+n[1]*q[0],q[1]]]],
 // Explicit ears of the concave H polygon; all faces remain triangles after sweep.
 [[13,0,1],[13,1,2],[5,6,7],[4,5,7],[7,8,9],[7,9,10],
  [4,7,10],[3,4,10],[3,10,11],[2,3,11],[13,2,11],[11,12,13]]);
}
module h_fork(){
 a=h_path(h_fork_t);u=h_tangent(h_fork_t);
 b=h_pad_xy(-2,0);
 c1=a+u*14;c2=b-[12*cos(h_pad_angle),12*sin(h_pad_angle)];
 difference(){
 h_sweep([for(i=[0:48])let(t=i/48,p=h_bezier(a,c1,c2,b,t),
 v=3*(1-t)*(1-t)*(c1-a)+6*(1-t)*t*(c2-c1)+3*t*t*(b-c2),
 n=[-v[1]/norm(v),v[0]/norm(v)],w=h_width+(36-h_width)*t*t*(3-2*t))
 [for(q=h_rect(w,h_depth))
 [p[0]+n[0]*q[0],p[1]+n[1]*q[0],q[1]]]]);
 // The rounded triangular opening follows the distal curve; no separate straight strut.
 linear_extrude(height=h_depth+2,center=true)hull(){
  for(p=[h_path(.79),h_pad_xy(-5,10),h_pad_xy(-5,-10)])
   translate(p)circle(r=1.6,$fn=32);
 }
 }
}
module h_seat_local(stations,clearance=0){
 h_sweep([for(s=stations)[for(q=h_rect(s[1]+2*clearance,
 h_depth+2*clearance,r=1.2+clearance))[s[0],q[0],q[1]]]]);
}
module h_seat(){
 translate([h_pad_x,h_pad_sweep,0])rotate([0,0,h_pad_angle]){
  h_seat_local([[-4,36],[0,36]]);
  h_seat_local([[-h_eps,24],[2,24],[3.6,26],[4.4,26],[6,22.8]]);
 }
}
module h_mount(){rotate([h_mount_roll,0,0])children();}
module h_rigid_foot(){h_mount()union(){
 h_beam();h_fork();h_seat();}}
function h_cuff_path(t)=h_bezier([-15,0],[-2,0],
 [h_root-13,h_connector_bend-13*tan(-h_root_angle)],
 [h_root,h_connector_bend],t);
function h_cuff_tangent(t)=let(a=[-15,0],b=[-2,0],
 c=[h_root-13,h_connector_bend-13*tan(-h_root_angle)],d=[h_root,h_connector_bend],
 v=3*(1-t)*(1-t)*(b-a)+6*(1-t)*t*(c-b)+3*t*t*(d-c))v/norm(v);
// The socket and replacement tongue share a straight insertion axis and a custom longitudinal profile.
function h_joint_section(w,d,b)=[[-w/2+b,-d/2],[w/2-b,-d/2],
 [w/2,-d/2+b],[w/2,d/2-b],[w/2-b,d/2],[-w/2+b,d/2],
 [-w/2,d/2-b],[-w/2,-d/2+b]];
// Offset the real planar faces, including the inclined face and 45-degree edges.
// Both mating parts share the drawn straight-then-chamfered longitudinal profile.
function h_joint_profile(x,c=0)=let(
 m=(h_joint_tip_low-h_joint_low)/(h_joint_end-h_joint_break),
 lo=h_joint_low+m*(x-h_joint_break),d=h_joint_depth/2,b=h_joint_bevel,
 ymin=max(h_joint_low-c,lo-c*sqrt(1+m*m)),
 cut=max(h_joint_low-d+b-c*sqrt(2),lo-d+b-c*sqrt(2+m*m)),
 z=d+c,yn=cut+z,zn=ymin-cut,
 ymax=h_joint_high+c,yp=h_joint_high-b+c*(sqrt(2)-1),zp=d-b+c*(sqrt(2)-1))
 h_joint_bevel==0 && c==0 ? [[ymin,-z],[ymax,-z],[ymax,z],[ymin,z]] :
 [[yn,-z],[yp,-z],[ymax,-zp],[ymax,zp],[yp,z],[yn,z],[ymin,zn],[ymin,-zn]];
module h_joint_sweep(clearance=0,end_gap=0){
 m=(h_joint_tip_low-h_joint_low)/(h_joint_end-h_joint_break);
 xb=h_joint_break+clearance*(sqrt(2+m*m)-sqrt(2))/m;
 xv=h_joint_break+clearance*(sqrt(1+m*m)-1)/m;
 stations=clearance==0 ? [-16.3,h_joint_break,h_joint_end] :
  [-16.3,xb,xv,h_joint_end+end_gap];
 h_sweep([for(x=stations)[for(q=h_joint_profile(x,clearance))[x,q[0],q[1]]]]);
}
module h_joint_socket(){h_joint_sweep(h_joint_clearance,h_joint_end_gap);}
module h_joint_original_end_cut(){
 // Applied only to the original bar, before adding the replacement tongue.
 translate([-16,-40,-20])cube([65,80,40]);
}
// Compatibility hook. The old slanted corner cutter is intentionally empty.
module h_joint_flush_trim(){}
module h_joint_tongue(){
 difference(){
  h_joint_sweep();
  cylinder(h=25,d=4.2,center=true,$fn=80);
 }
}
module h_cuff_cutouts(){
 h_joint_socket();
 cylinder(h=25,d=4.2,center=true,$fn=80);
 translate([-30,11,0])rotate([0,0,38])cube([40,24,23.52],center=true);
}
module h_cuff_outer(){
 if(h_shape=="base")translate([5,0,0])cube([40,24,23.5],center=true);
 else
  // The socket follows the mean direction of this housing. No added side bulge.
  h_sweep([for(i=[0:41])let(t=min(i,40)/40,
   // Follow the SAME arc for the small boolean overlap; no tangent stub.
   f=h_path(.3/(6*h_length*.16)),fv=h_tangent(.3/(6*h_length*.16)),
   p=i==41 ? [f[0],-f[1]] : h_cuff_path(t),
   u=i==41 ? [fv[0],-fv[1]] : h_cuff_tangent(t),n=[-u[1],u[0]])
   [for(q=h_rect(h_width,h_depth,r=0))
    [p[0]+n[0]*q[0],p[1]+n[1]*q[0],q[1]]]]);
}
module h_foot_cuff(){difference(){h_cuff_outer();h_cuff_cutouts();}}
module h_integrated_foot(){union(){h_foot_cuff();h_rigid_foot();}}
module h_rigid_print(){
 translate([15,32,h_depth/2])rotate([-h_mount_roll,0,0])h_integrated_foot();
}
module h_sole_local(){
 difference(){
  intersection(){translate([h_sole_lift,0,0])sphere(r=h_pad_radius);
   translate([h_sole_lift,-h_pad_radius-1,-h_pad_radius-1])
    cube([h_pad_radius+1,2*h_pad_radius+2,2*h_pad_radius+2]);}
  h_seat_local([[-h_eps,24],[2,24],[3.6,26],[4.4,26],[6+h_gap,22.8]],clearance=h_gap);
  // Accessible opening on the bed; the inner roof closes at 45 degrees.
  h_sweep([for(i=[0:48])let(t=i/48,s=6.2+11.1*t,
   w=23.4-22.2*t,d=24.1-22.2*t)
   [for(q=h_rect(w,d,r=min(.9,w/4,d/4)))[s,q[0],q[1]]]]);
 }
}
module h_soft_sole(){h_mount()translate([h_pad_x,h_pad_sweep,0])
 rotate([0,0,h_pad_angle])h_sole_local();}
module h_sole_print(){rotate([0,-90,0])translate([-h_sole_lift,0,0])h_sole_local();}
module h_robot_foot(with_sole=true){
 color([.20,.24,.27])h_rigid_foot();
 if(with_sole)color([.08,.09,.10])h_soft_sole();
}
module h_cross_section(){
 linear_extrude(height=.8)polygon(h_section());
}
assert(h_width==24 && h_depth==23.5,"Review the constant section / cuff interface");
assert(h_root_angle>=-20 && h_root_angle<=10 && h_arc_control>=-50 && h_arc_control<=8,
 "Review the continuous reverse-to-forward curve");
assert(h_connector_bend>=0 && h_connector_bend<=6 && h_connector_wall>=2.6,
 "Review the curved connector / straight socket walls");
assert(h_joint_clearance>=.1 && h_joint_clearance<=.3,
 "Review the mating clearance");
assert((h_width-h_joint_width)/2-h_joint_clearance>=h_connector_wall,
 "Insufficient lateral socket wall");
assert(h_flange>=3.2 && h_web>=3.2,"Review PLA+ walls");
assert(h_depth/2-h_web/2-(h_width-2*h_flange-h_bridge)/2>=0,
 "45 degree haunches extend below the print bed");
if(h_part=="core")h_rigid_foot();
else if(h_part=="integrated")h_integrated_foot();
else if(h_part=="print")h_rigid_print();
else if(h_part=="sole")h_soft_sole();
else if(h_part=="sole_print")h_sole_print();
else if(h_part=="tongue")h_joint_tongue();
else if(h_part=="socket")h_joint_socket();
else if(h_part=="section")h_cross_section();
else {color("Goldenrod")h_foot_cuff();h_robot_foot();}
