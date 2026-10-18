// Native static geometry for render_robot_walk.py. Export each part to STL.
use <../vptc_roller.scad>
part="body"; // [body,upper]
k=leg_kinematic_parameters();
if(part=="body")body(parts=false);
else if(part=="upper")union(){
 translate([0,0,k[4]-9.5])shoulder_top();
 translate([-25,65,k[4]-9.5])hip();
 translate([-25,18,k[4]-22.5])hip_top();
}
