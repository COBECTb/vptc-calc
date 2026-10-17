// Assembly and section views of the native foot. Units: mm.
use <../foots.scad>
use <../vptc_roller.scad>
$fn=64;
view="assembly"; // reference, assembly, foot, core, sole, print, sole_print, section, exploded
module connector_reference(){foot_cuff();}
module complete_assembly(){
 color("Goldenrod") connector_reference();
 color("LightGray") translate([-47,0,0])rotate([180,180,0])shin(foot=false);
 robot_foot();
}
if(view=="core") rigid_foot();
else if(view=="sole") soft_sole();
else if(view=="foot") robot_foot();
else if(view=="print") rigid_print();
else if(view=="sole_print") sole_print();
// Keep the native shin/connector relationship visible; no isolated posing of the foot.
else if(view=="reference")complete_assembly();
else if(view=="section") intersection(){complete_assembly();translate([-100,-50,0])cube([350,100,50]);}
else if(view=="exploded"){
 color("Goldenrod")connector_reference();
 color("DimGray")translate([15,0,0])rigid_foot();
 color("Black")translate([45,0,0])soft_sole();
}
else complete_assembly();
