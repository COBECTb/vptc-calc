// Колено: компоновочное предложение с существующей CAN-платой.
// Исходные hip()/hip_top()/shin() сохранены в оригинальном файле.
// Z=0 — плоскость вращения shin() в исходной leg(); ось колена — [0,0].
use <../../../vptc_roller_19_4_5_70.scad>
use <../../../encoder_can_pcb_layout.scad>
use <../../../connector_clamp_magnets_5mm.scad>

view="assembly"; // [assembly,exploded,section,hip,shin,cover,rotor,pcb]
knee_angle=0; // Угол shin(), не анатомический угол колена.
show_magnets=true;
show_bearings=true;
show_lower_fork=true;
$fn=64;
eps=.01;
board_rotation=-99; // Датчики исходной платы при9° становятся при−90°, к бедру.
rotor_top_z=9;
rotor_bottom_z=7;
recess_depth=.4;
magnet_front_z=rotor_top_z-recess_depth+1; //9.6
window_outer_z=10;
window_inner_z=10.4;
board_front_z=12.05; // PCB0.8, датчики вниз1.45мм ->10.6, внутренний зазор0.2.
board_rear_z=board_front_z+.8;
cavity_roof_z=14.5; // Задние корпуса до14.3; зазор0.2.
housing_top_z=15.3;
cover_h=.4;

assert(abs(window_outer_z-magnet_front_z-.4)<1e-6,"Магнитный зазор");
assert(abs(board_front_z-1.45-window_inner_z-.2)<1e-6,"Внутренний зазор датчика");

module annulus(ro,ri,h){difference(){cylinder(r=ro,h=h);translate([0,0,-eps]) cylinder(r=ri,h=h+2*eps);}}
module board_shape(clearance=0){rotate(board_rotation) encoder_pcb_outline(clearance);}
module board_mounts(){rotate(board_rotation) encoder_pcb_mount_positions() children();}
module cover_mounts(){for(a=[-160,-90,-20]) rotate(a) translate([36.5,0,0]) children();}
module original_hip_local(){translate([-12,-119,-9.5]) hip();}
module original_lower_fork_local(){translate([-12,-166,-20.5]) hip_top();}

module rotor_blank(){translate([0,0,rotor_bottom_z]) annulus(33,20,rotor_top_z-rotor_bottom_z);}
module rotor_rims(){translate([0,0,rotor_top_z-12]) for(half=[0,1]) rotate(180*half) magnet_rims();}
module rotor_pockets(){
    translate([0,0,rotor_top_z-12]) track_positions(true)
        translate([0,0,-recess_depth]) cylinder(d=5.2,h=recess_depth+.4+eps);
}
module knee_rotor(){difference(){union(){rotor_blank();rotor_rims();}rotor_pockets();}}
module proposed_shin(){
    difference(){union(){shin(foot=false);rotor_blank();rotor_rims();}rotor_pockets();}
}
module magnets(){translate([0,0,rotor_top_z-12]) for(half=[0,1]) rotate(180*half) magnet_preview(half==1);}
module rotor_swept_clearance(){translate([0,0,rotor_bottom_z-.2]) annulus(33.2,19.8,magnet_front_z-rotor_bottom_z+.4);}

module stationary_shell(){
    union(){
        translate([0,0,window_outer_z]) linear_extrude(height=housing_top_z-window_outer_z) board_shape(1.2);
        cover_mounts() translate([0,0,11.6]) cylinder(d=6,h=housing_top_z-11.6);
        // Перемычки от крышечных винтов к стенке корпуса.
        for(a=[-160,-90,-20]) rotate(a) translate([32,-3,11.6]) cube([4.5,6,housing_top_z-11.6]);
    }
}
module pcb_cavity(){
    translate([0,0,window_outer_z-eps]) linear_extrude(height=cavity_roof_z-window_outer_z+eps) board_shape(.25);
}
module pcb_supports(){board_mounts() translate([0,0,board_rear_z]) cylinder(d=3.8,h=housing_top_z-board_rear_z);}
module proposed_hip(){
    difference(){
        union(){
            difference(){union(){original_hip_local();stationary_shell();}pcb_cavity();rotor_swept_clearance();}
            pcb_supports();
        }
        board_mounts() translate([0,0,board_rear_z-eps]) cylinder(d=1.6,h=housing_top_z-board_rear_z+2*eps);
        cover_mounts() translate([0,0,11.6-eps]) cylinder(d=1.6,h=housing_top_z-11.6+2*eps);
    }
}
module protective_cover(){
    difference(){
        union(){
            translate([0,0,window_outer_z]) linear_extrude(height=cover_h) board_shape(.2);
            cover_mounts() translate([0,0,window_outer_z]) cylinder(d=6,h=1.6);
            for(a=[-160,-90,-20]) rotate(a) translate([32,-3,window_outer_z]) cube([4.5,6,cover_h]);
        }
        cover_mounts(){
            translate([0,0,window_outer_z-eps]) cylinder(d=2.2,h=1.6+2*eps);
            // Потайные M2: головки не выступают к вращающемуся кольцу.
            translate([0,0,window_outer_z-eps]) cylinder(d1=4+2*eps,d2=2.2,h=1.1+eps);
        }
    }
}
module pcb(){rotate(board_rotation) translate([0,0,board_front_z]) encoder_can_pcb(true,true);}
module pcb_screws(){color("Silver") board_mounts() translate([0,0,board_front_z-1.3]) cylinder(d=3.5,h=1.3);}
module bearings(){
    // По дну реальных посадок: leg() показывает оба подшипника примерно на2.5мм выше.
    // Здесь отображены правильные посадки, без изменения исходного leg().
    translate([0,0,10.5]) annulus(8,4,5);
    translate([0,0,-14.5]) annulus(8,4,5);
}
module cut_view(){if(view=="section") intersection(){children();translate([0,-200,-40])cube([100,250,100]);}else children();}

if(view=="hip") proposed_hip();
else if(view=="shin") proposed_shin();
else if(view=="rotor") knee_rotor();
else if(view=="cover") protective_cover();
else if(view=="pcb") pcb();
else{
    ex=view=="exploded";
    color("LightGray") translate([0,0,ex?16:0]) cut_view() proposed_hip();
    if(show_lower_fork) color("Gainsboro") translate([0,0,ex?-18:0]) cut_view() original_lower_fork_local();
    color("SlateGray") rotate(knee_angle) cut_view() proposed_shin();
    if(show_magnets) rotate(knee_angle) cut_view() magnets();
    translate([0,0,ex?7:0]) cut_view() pcb();
    translate([0,0,ex?7:0]) cut_view() pcb_screws();
    color("LightSteelBlue",.7) translate([0,0,ex?3:0]) cut_view() protective_cover();
    if(show_bearings) color("Silver") cut_view() bearings();
}
echo("PCB front/rear Z:",board_front_z,board_rear_z);
echo("Magnet surface/window/Hall clearance:",magnet_front_z,window_outer_z,board_front_z-encoder_hall_height()-magnet_front_z);
echo("Housing below original hip inner face10.5:",10.5-window_outer_z);
