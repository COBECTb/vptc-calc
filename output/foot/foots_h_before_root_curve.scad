// Constant-section H foot. Units: mm, original foot_connector() coordinates.
// Rigid part: PLA+, 0.4 mm nozzle. Contact hemisphere: separate TPU print.
$fn=80;
h_part="assembly"; // assembly, core, integrated, print, sole, sole_print, section
h_shape="s_curve"; // s_curve or base (accepted shape, also saved in foots_h_base.scad)
h_reverse=4.3; // mm, elongated reverse deflection near the connector
h_reverse_span=.66; // reverse-to-forward transition reaches almost to the distal fork
h_length=145;
h_width=24;
h_depth=23.5;
h_flange=3.2;
h_web=3.2;
h_bridge=1.2;
h_fork_width=6.4;
h_fork_t=.68;
h_body_end=.72;
h_pad_radius=20;
h_pad_angle=55;
h_pad_sweep=50;
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
// A local bump keeps position/tangent at the cuff and rejoins the base curve C2.
function h_reverse_y(t)=h_shape=="base" || t>=h_reverse_span ? 0 :
 let(u=max(0,t/h_reverse_span)) -h_reverse*(3125/108)*u*u*pow(1-u,3);
function h_reverse_dy(t)=h_shape=="base" || t>=h_reverse_span ? 0 :
 let(u=max(0,t/h_reverse_span))
 -h_reverse/h_reverse_span*(3125/108)*u*pow(1-u,2)*(2-5*u);
function h_path(t)=h_base_path(t)+[0,h_reverse_y(t)];
function h_tangent(t)=let(
 a=[h_root,0],b=[h_root+h_length*.40,0],
 c=[h_root+h_length*.82,8],d=[h_root+h_length,42],
 v=3*(1-t)*(1-t)*(b-a)+6*(1-t)*t*(c-b)+3*t*t*(d-c)+[0,h_reverse_dy(t)])v/norm(v);
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
function h_rect(w,d,r=1.2)=[
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
 translate([h_root-h_eps,-h_width/2,-h_depth/2])cube([h_eps+.12,h_width,h_depth]);
 h_beam();h_fork();h_seat();}}
module h_foot_cuff(){
 // Exact original cuff. It is NOT rotated with the foot.
 difference(){
  translate([5,0,0])cube([40,24,23.5],center=true);
  cube([36.02,15.4,18.3],center=true);
  cylinder(h=25,d=4.2,center=true);
  translate([-30,11,0])rotate([0,0,38])cube([40,24,23.52],center=true);
 }
}
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
assert(h_reverse>=0 && h_reverse<=8 && h_reverse_span>0 && h_reverse_span<h_fork_t,
 "Reverse bend must rejoin before the distal fork");
assert(h_flange>=3.2 && h_web>=3.2,"Review PLA+ walls");
assert(h_depth/2-h_web/2-(h_width-2*h_flange-h_bridge)/2>=0,
 "45 degree haunches extend below the print bed");
if(h_part=="core")h_rigid_foot();
else if(h_part=="integrated")h_integrated_foot();
else if(h_part=="print")h_rigid_print();
else if(h_part=="sole")h_soft_sole();
else if(h_part=="sole_print")h_sole_print();
else if(h_part=="section")h_cross_section();
else {color("Goldenrod")h_foot_cuff();h_robot_foot();}
