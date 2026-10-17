// Native FDM foot, revision 5. Units: mm; frame of foot_connector().
use <foots_h.scad>
design_variant="h"; // h: constant H section, box: previous tapered closed section
// 6 kg robot, 0.4 mm nozzle, PLA+ rigid part; soft contact pad is separate.
// Curved hollow profile with a flat print face, vaulted roof, raised edge walls,
// integral heel window, and local diaphragms. Load screening is not certification.
$fn=80;
part="foot"; // foot, core, integrated, print, sole, sole_print
blade_length=140;
blade_sweep=42;
curve_side=1; // Intrinsic blade shape, before mounting in the connector.
mount_roll=180; // Turn only the foot about connector X; preserve the original cuff cut.
distal_scale=1;
body_depth=18;
floor_thickness=3.2;
edge_wall=3.2;
roof_thickness=2.4;
recess_depth=1.6;
brace_width=4.8;
sole_gap=.30;
bed_z=-11.75;
root_x=25;
end_x=root_x+blade_length*distal_scale;
pad_y=blade_sweep+8;
pad_x=end_x+1;
pad_angle=48; // Mount orientation only: spherical ground contact has no fixed normal.
pad_front=-4.5;
sole_radius=18;
sole_open=-6;
pad_z=bed_z+body_depth/2;
eps=.02;

function bezier(p0,p1,p2,p3,t)=
 (1-t)*(1-t)*(1-t)*p0+3*(1-t)*(1-t)*t*p1+
 3*(1-t)*t*t*p2+t*t*t*p3;
function smoothstep(t)=let(u=min(1,max(0,t)))u*u*(3-2*u);
function centerline(t)=bezier([root_x,0],
 [root_x+blade_length*distal_scale*.32,0],
 [root_x+blade_length*distal_scale*.72,blade_sweep*.30],
 [end_x,blade_sweep],t);
function pad_xy(s,v)=[pad_x+s*cos(pad_angle)-v*sin(pad_angle),
                     pad_y+s*sin(pad_angle)+v*cos(pad_angle)];
function blade_width(t)=10.4+13.6*pow(1-t,1.4);
function blade_depth(t)=body_depth+(23.5-body_depth)*(1-smoothstep(t/.22));
function rounded_section(w,h,r=1.2,b=bed_z)=concat(
 [[-w/2,b],[w/2,b],[w/2,b+h-r]],
 [for(i=[1:4])let(a=90*i/4)[w/2-r+r*cos(a),b+h-r+r*sin(a)]],
 [[-w/2+r,b+h]],
 [for(i=[1:4])let(a=90+90*i/4)[-w/2+r+r*cos(a),b+h-r+r*sin(a)]]);
function pocket_section(w,b,top,r=1.6)=
 [[-w/2,b+min(r,w/3)],[-w/2+min(r,w/3),b],
 [w/2-min(r,w/3),b],[w/2,b+min(r,w/3)],
 [w/2,top],[-w/2,top]];
function vault_section(w,b,peak)=let(a=min(1.2,w/2),side=peak-(w-a)/2,
 r=min(1.6,w/4,(side-b)/3))
 [[-w/2,b+r],[-w/2+r,b],[w/2-r,b],[w/2,b+r],
 [w/2,side],[a/2,peak],[-a/2,peak],[-w/2,side]];

// Closed sweep of rings in constant-X planes; all flat back faces share bed_z.
module sweep_rings(rings){
 m=len(rings);n=len(rings[0]);
 sides=[for(i=[0:m-2])for(j=[0:n-1])
  each let(a=i*n+j,b=i*n+(j+1)%n,c=(i+1)*n+(j+1)%n,d=(i+1)*n+j)
  [[c,b,a],[d,c,a]]];
 caps=[[for(j=[0:n-1])j],[for(j=[n-1:-1:0])(m-1)*n+j]];
 polyhedron(points=[for(r=rings)each r],faces=concat(sides,caps),convexity=16);
}
module solid_blade(){
 sweep_rings([for(i=[0:72])let(t=i/72,p=centerline(t))
  [for(q=rounded_section(blade_width(t),blade_depth(t)))
   [p[0],p[1]+q[0],q[1]]]]);
}
module internal_void(){
 sweep_rings([for(i=[0:64])let(t=.13+.78*i/64,p=centerline(t),
  k=max(.015,smoothstep((t-.13)/.075)*smoothstep((.91-t)/.075)),
  w=max(.12,(blade_width(t)-2*edge_wall)*k),
  peak=bed_z+blade_depth(t)-recess_depth-roof_thickness,
  bottom=peak-k*(peak-bed_z-floor_thickness))
  [for(q=vault_section(w,bottom,peak)) [p[0],p[1]+q[0],q[1]]]]);
}
module visible_recess(){
 sweep_rings([for(i=[0:64])let(t=.13+.78*i/64,p=centerline(t),
  k=max(.015,smoothstep((t-.13)/.075)*smoothstep((.91-t)/.075)),
  w=max(.12,(blade_width(t)-2*edge_wall)*k),top=bed_z+blade_depth(t))
  [for(q=pocket_section(w,top-recess_depth*k,top+1,r=.4))
    [p[0],p[1]+q[0],q[1]]]]);
}
module curved_blade(){
 union(){
  difference(){solid_blade();internal_void();visible_recess();}
  // One internal diaphragm reinforces the heel-rib junction.
  for(t=[.76])let(p=centerline(t))intersection(){
   solid_blade();translate([p[0]-1.6,p[1]-20,bed_z])cube([3.2,40,24]);
  }
  // One continuous heel rib frames the ankle window.
  a=centerline(.76);b=pad_xy(pad_front-1,8.5);
  sweep_rings([for(i=[0:20])let(t=i/20,p=bezier(a,
   [a[0]+(b[0]-a[0])*.34,a[1]+.7],
   [a[0]+(b[0]-a[0])*.70,b[1]+.5],b,t))
   [for(q=rounded_section(brace_width,body_depth,r=1.2))
    [p[0],p[1]+q[0],q[1]]]]);
 }
}

// Flat-backed pad seat: the entire rigid assembly shares a real planar print face.
module pad_seat_local(stations,clearance=0){
 sweep_rings([for(s=stations)
  [for(q=rounded_section(s[1]+2*clearance,body_depth+2*clearance,
       r=1.6+clearance,b=bed_z-clearance)) [s[0],q[0],q[1]]]]);
}
module pad_seat(stations,clearance=0){
 translate([pad_x,pad_y,0])rotate([0,0,pad_angle])
  pad_seat_local(stations,clearance);
}
module rigid_foot_base(){
 union(){
  translate([root_x-eps,-12,bed_z])cube([eps+.12,24,23.5]);
  curved_blade();
  pad_seat([[pad_front-2.5,24],[pad_front+1,24]]);
  // A 45-degree retention ramp can also be printed inside the elastomer cup.
  pad_seat([[pad_front+1,18],[pad_front+3,22],[pad_front+4,22],[pad_front+4.8,20.4]]);
 }
}
module curve_frame(){
 rotate([mount_roll,0,0])
  if(curve_side<0)mirror([0,1,0])children();else children();
}
module rigid_foot(){if(design_variant=="h")h_rigid_foot();else curve_frame()rigid_foot_base();}
module foot_cuff(){
 if(design_variant=="h")h_foot_cuff();else
 // Original printed connector, preserved exactly; shin slot and M4 pin are unchanged.
 difference(){
  translate([5,0,0])cube([40,24,23.5],center=true);
  cube([36.02,15.4,18.3],center=true);
  cylinder(h=25,d=4.2,center=true);
  translate([-30,11,0])rotate([0,0,38])cube([40,24,23.52],center=true);
 }
}
module integrated_foot(){union(){foot_cuff();rigid_foot();}}
module foot_joint_socket(){if(design_variant=="h")h_joint_socket();else cube([36.02,15.4,18.3],center=true);}
module foot_joint_original_end_cut(){if(design_variant=="h")h_joint_original_end_cut();}
module foot_joint_tongue(){if(design_variant=="h")h_joint_tongue();}
module foot_joint_trim(){
 if(design_variant=="h")h_joint_flush_trim();
 else intersection(){
  translate([-15-eps,-40,-13])cube([33.04,80,26]);
  translate([-30,11,0])rotate([0,0,38])cube([40,24,23.52],center=true);
 }
}
module rigid_print(){
 if(design_variant=="h")h_rigid_print();else
 // Undo mounting roll for the whole print job: flat blade back lies on the bed.
 translate([15,blade_sweep+32,-bed_z])rotate([-mount_roll,0,0])integrated_foot();
}

module sole_local(){
 // Spherical working surface: contact stays on rubber as the whole shank tilts.
 // Open mounting face is printable on the bed; the internal void closes at 45 degrees.
 difference(){
  intersection(){
   translate([0,0,pad_z])sphere(r=sole_radius);
   translate([sole_open,-sole_radius-1,pad_z-sole_radius-1])
    cube([2*sole_radius+2,2*sole_radius+2,2*sole_radius+2]);
  }
  pad_seat_local([[sole_open-eps,24],[pad_front+1+sole_gap,24]],clearance=sole_gap);
  pad_seat_local([[pad_front+1-eps,18],[pad_front+3,22],[pad_front+4+sole_gap,22],
            [pad_front+4.8+sole_gap,20.4]],clearance=sole_gap);
  // Hollow extension beyond the mount: each wall advances <= one layer height.
  sweep_rings([for(i=[0:40])let(t=i/40,s=.6+9.9*t,
    w=max(1.2,21-19.8*t),h=max(1.2,18.6-19.8*t))
    [for(q=rounded_section(w,h,r=min(1.9,w/4,h/4),b=pad_z-h/2))
      [s,q[0],q[1]]]]);
 }
}
module soft_sole(){if(design_variant=="h")h_soft_sole();else
 curve_frame()translate([pad_x,pad_y,0])rotate([0,0,pad_angle])sole_local();}
module sole_print(){
 if(design_variant=="h")h_sole_print();else
 rotate([0,-90,0])translate([-sole_open,0,-pad_z])sole_local();
}
module robot_foot(with_sole=true){
 color([.20,.24,.27])rigid_foot();
 if(with_sole)color([.08,.09,.10])soft_sole();
}
assert(blade_length>80 && blade_sweep>0,"Review blade dimensions");
assert(mount_roll==0 || mount_roll==180,"Flat print placement supports a 0 or 180 degree mounting roll");
assert(floor_thickness>=2.4 && edge_wall>=2.4,"Review structural walls");
if(part=="core")rigid_foot();
else if(part=="sole")soft_sole();
else if(part=="integrated")integrated_foot();
else if(part=="print")rigid_print();
else if(part=="sole_print")sole_print();
else robot_foot();
