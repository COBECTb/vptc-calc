use <../foots.scad>
use <robot_foot.scad>
use <../vptc_roller.scad>
$fn=64;
check="cuff";
module verification_layout(){
 rigid_foot();
 translate([0,0,60])soft_sole();
 translate([0,0,120])connector_reference();
 translate([0,0,180])translate([-47,0,0])rotate([180,180,0])shin(foot=false);
 translate([0,0,240])integrated_foot();
 translate([0,0,300])intersection(){connector_reference();rigid_foot();}
 translate([0,0,360])intersection(){rigid_foot();translate([-47,0,0])rotate([180,180,0])shin(foot=false);}
 translate([0,0,420])intersection(){rigid_foot();soft_sole();}
 translate([0,0,480])intersection(){integrated_foot();translate([-47,0,0])rotate([180,180,0])shin(foot=false);}
 translate([0,0,540])intersection(){integrated_foot();foot_joint_socket();}
 translate([0,0,600])intersection(){integrated_foot();cylinder(h=25,d=4.2,center=true,$fn=80);}
 translate([0,0,660])intersection(){translate([-47,0,0])rotate([180,180,0])shin(foot=false);foot_joint_trim();}
 translate([0,0,720])foot_joint_socket();
}
if(check=="all")verification_layout();
else if(check=="cuff") intersection(){rigid_foot();connector_reference();}
else if(check=="shin") intersection(){rigid_foot();translate([-47,0,0])rotate([180,180,0])shin(foot=false);}
else if(check=="sole") intersection(){rigid_foot();soft_sole();}
else if(check=="reference") connector_reference();
else if(check=="original_shin") translate([-47,0,0])rotate([180,180,0])shin(foot=false);
else if(check=="joined") union(){connector_reference();rigid_foot();}
