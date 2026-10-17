// Connector / keyed shin fit. Units: mm, connector coordinate frame.
use <../foots.scad>
use <../vptc_roller.scad>
$fn=80;
view="section"; // section, assembly, exploded, fit_print, insertion_check
joint_angle=0;
module fitted_shin(){translate([-47,0,0])rotate([180,180,0])shin(foot=false);}
module local_joint(withdraw=0){
 color("Goldenrod")foot_cuff();
 color("SteelBlue")translate([-withdraw*cos(joint_angle),-withdraw*sin(joint_angle),0])fitted_shin();
}
if(view=="insertion_check"){
 // Empty result is expected at every sampled insertion / withdrawal position.
 for(i=[0:4])let(withdraw=[0,1,5,15,30][i])translate([0,0,60*i])
  intersection(){integrated_foot();translate([-withdraw*cos(joint_angle),-withdraw*sin(joint_angle),0])fitted_shin();}
}
else if(view=="fit_print"){
 // Short samples cut from the real parts; check printer clearance before full prints.
 translate([5,15,11.75])intersection(){foot_cuff();translate([-5,-25,-20])cube([29,50,40]);}
 translate([7,48,9])intersection(){foot_joint_tongue();translate([-7,-20,-20])cube([25,40,40]);}
}
else if(view=="section")intersection(){local_joint();translate([-24,-25,0])cube([55,50,20]);}
else if(view=="exploded")local_joint(38);
else local_joint();
