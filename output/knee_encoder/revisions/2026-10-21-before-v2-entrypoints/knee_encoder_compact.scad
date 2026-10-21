// Колено: компактная общая плата и секторный магнитоноситель.
// Макет корпусов компонентов; новая электрическая разводка ещё не выполнена.
// Исходные hip()/hip_top()/shin() сохранены в оригинальном файле.
// Z=0 — плоскость вращения shin() в исходной leg(); ось колена — [0,0].
use <../../../vptc_roller_19_4_5_70.scad>
use <../../../encoder_can_pcb_layout.scad>
use <../../../connector_clamp_magnets_5mm.scad>
use <../../compact_encoder_pcb.scad>

view="assembly"; // [assembly,exploded,section,stage,hip,shin,cover,rotor,pcb]
assembly_step=4; // [1:Открытая вилка,2:Голень ось и съёмная щека,3:Плата с проводами,4:Наружная сервисная крышка]
knee_angle=0; // Угол shin(), не анатомический угол колена.
show_magnets=true;
show_bearings=true;
show_rod=true;
show_lower_fork=true;
$fn=64;
eps=.01;
board_rotation=-74; // Общая плата при9° -> Hall при−65°, к бедру.
sector_start=-153;
sector_end=31;
knee_min=-44.6458; // С учётом исходной тяги.
knee_max=54.2040;
rotor_top_z=12.7;
rotor_bottom_z=10.7;
recess_depth=.4;
magnet_front_z=rotor_top_z-recess_depth+1; //13.3
window_outer_z=13.7;
window_inner_z=14.1;
board_front_z=15.75; // PCB0.8, датчики вниз1.45мм ->14.3, внутренний зазор0.2.
board_rear_z=board_front_z+.8;
cavity_roof_z=18.2; // Задние корпуса до18.0; зазор0.2.
housing_top_z=23.5; // Наружный торец исходной неподвижной щеки.
cover_h=.8;
cover_bottom_z=housing_top_z;

assert(abs(window_outer_z-magnet_front_z-.4)<1e-6,"Магнитный зазор");
assert(abs(board_front_z-1.45-window_inner_z-.2)<1e-6,"Внутренний зазор датчика");

module annulus(ro,ri,h){difference(){cylinder(r=ro,h=h);translate([0,0,-eps]) cylinder(r=ri,h=h+2*eps);}}
module board_shape(clearance=0){rotate(board_rotation) compact_pcb_outline(clearance);}
module board_mounts(){rotate(board_rotation) compact_pcb_mounts() children();}
module cover_mounts(){for(a=[-100,-65,-30]) rotate(a) translate([36.5,0,0]) children();}
module original_hip_local(){translate([-12,-119,-9.5]) hip();}
module original_lower_fork_local(){translate([-12,-166,-20.5]) hip_top();}

module sector_gate(z,h){translate([0,0,z])linear_extrude(h)polygon(concat([[0,0]],[for(i=[0:184])let(a=sector_start+(sector_end-sector_start)*i/184)[100*cos(a),100*sin(a)]]));}
module knee_magnet_positions(){
 for(t=[0,1]) let(n=t==0?24:26,r=t==0?23.5:29.5)
  for(j=[0:n-1]) let(a=(j+.5)*360/n,sa=a>180?a-360:a)
   if(sa>=sector_start && sa<=sector_end) translate([r*cos(a),r*sin(a),rotor_top_z]) children();
}
module rotor_blank(){
 intersection(){translate([0,0,rotor_bottom_z]) annulus(33,20,rotor_top_z-rotor_bottom_z);sector_gate(rotor_bottom_z-.01,3);}
 // Поднятый сектор опирается на длинное плечо. Тяга проходит с другой стороны оси.
 translate([0,0,7]) hull(){translate([-24,-4,0])cylinder(r=3,h=rotor_top_z-7);translate([-24,-12,0])cylinder(r=3,h=rotor_top_z-7);}
}
module rotor_rims(){difference(){knee_magnet_positions()translate([0,0,-.02])cylinder(d=6.4,h=.42);knee_magnet_positions()translate([0,0,-.04])cylinder(d=5.2,h=.48);}}
module rotor_pockets(){
    knee_magnet_positions()
        translate([0,0,-recess_depth]) cylinder(d=5.2,h=recess_depth+.4+eps);
}
module knee_rotor(){difference(){union(){rotor_blank();rotor_rims();}rotor_pockets();}}
module printed_foot_connector(){
 // Печатная часть исходного foot_connector(), без отсутствующего STL стопы.
 difference(){
  translate([5,0,0])cube([40,24,23.5],center=true);
  cube([36.02,15.4,18.3],center=true);
  cylinder(h=25,r=2.1,center=true);
  translate([-30,11,0])rotate([0,0,38])cube([40,24,23.52],center=true);
 }
}
module proposed_shin(){
    difference(){union(){shin(foot=false);translate([-47,0,0])rotate([180,180,0])printed_foot_connector();rotor_blank();rotor_rims();}rotor_pockets();}
}
module magnets(){
 for(t=[0,1]) let(n=t==0?24:26,r=t==0?23.5:29.5)
  for(j=[0:n-1]) let(a=(j+.5)*360/n,sa=a>180?a-360:a)
   if(sa>=sector_start && sa<=sector_end) color(j%2==0?"Firebrick":"RoyalBlue")
    translate([r*cos(a),r*sin(a),rotor_top_z-recess_depth]) cylinder(d=5,h=1);
}
module rotor_swept_clearance(){translate([0,0,6.8]) annulus(33.2,19.8,magnet_front_z-6.8+.2);}

module stationary_shell(){
    union(){
        translate([0,0,window_outer_z]) linear_extrude(height=housing_top_z-window_outer_z) board_shape(1.2);
        cover_mounts() translate([0,0,window_outer_z]) cylinder(d=6,h=housing_top_z-window_outer_z);
        // Перемычки от крышечных винтов к стенке корпуса.
        for(a=[-100,-65,-30]) rotate(a) translate([32,-3,window_outer_z]) cube([4.5,6,housing_top_z-window_outer_z]);
    }
}
module pcb_cavity(){
    translate([0,0,window_inner_z]) linear_extrude(height=housing_top_z-window_inner_z+eps) board_shape(.25);
}
module pcb_supports(){board_mounts(){
 translate([0,0,window_inner_z]) cylinder(d=3.8,h=board_front_z-window_inner_z);
 translate([0,0,board_front_z-eps]) cylinder(d=1.8,h=.7+eps);
}}
module proposed_hip(){
    difference(){
        union(){
            difference(){union(){original_hip_local();stationary_shell();}pcb_cavity();rotor_swept_clearance();}
            pcb_supports();
        }
        cover_mounts() translate([0,0,housing_top_z-5]) cylinder(d=1.6,h=5+eps);
        // Провода идут от передних площадок наружу, затем вверх через неподвижную щеку.
        rotate(-55) translate([32.8,-2.4,14.6]) cube([5.7,4.8,1.3]);
        rotate(-55) translate([34.7,-2.4,14.6]) cube([3.8,4.8,10.3]);
    }
}
module protective_cover(){
    difference(){
        union(){
            translate([0,0,cover_bottom_z]) linear_extrude(height=cover_h) board_shape(1.15);
            cover_mounts() translate([0,0,cover_bottom_z]) cylinder(d=6,h=cover_h);
            for(a=[-100,-65,-30]) rotate(a) translate([32,-3,cover_bottom_z]) cube([4.5,6,cover_h]);
            // Прижимы опираются на свободные кольца вокруг монтажных отверстий PCB.
            board_mounts() translate([0,0,board_rear_z]) cylinder(d=3.8,h=cover_bottom_z+cover_h-board_rear_z);
            // Рёбра крышки выше всех корпусов компонентов.
            for(a=[-83,-47]) rotate(a) translate([30.5,-.7,cavity_roof_z])cube([2.8,1.4,cover_bottom_z+cover_h-cavity_roof_z]);
        }
        cover_mounts(){
            translate([0,0,cover_bottom_z-eps]) cylinder(d=2.2,h=cover_h+2*eps);
        }
    }
}
module pcb(){rotate(board_rotation) translate([0,0,board_front_z]) compact_pcb();}
// Обратная геометрия исходной тяги: межосевое 184, плечо привода 31.
function knee_rod_p1(a)=let(p=[37*cos(a),37*sin(a)],c=[13,-184],d=norm(p-c),b=atan2(p.y-c.y,p.x-c.x),al=acos((31*31+d*d-184*184)/(2*31*d))) [c.x+31*cos(b-al),c.y+31*sin(b-al),0];
module knee_rod(a){
 difference(){
  translate([0,0,5])connect_points_rod(knee_rod_p1(a),[37*cos(a),37*sin(a),0]);
  // Головка крепления утоплена в ушко, иначе она упирается в исходную щеку.
  translate([37*cos(a),37*sin(a),8.1])cylinder(d=8,h=2.4+eps);
 }
}
module rod_head(a){translate([37*cos(a),37*sin(a),8.3])cylinder(d=7.6,h=2.2);}
module axle(){translate([0,0,-14.5])cylinder(d=8,h=30);}
module wires(){
 for(y=[-1.8,-.6,.6,1.8]) color("DarkSlateGray") rotate(-55){
  hull(){translate([32,y,15.5])sphere(d=.5);translate([36.5,y,15.3])sphere(d=.5);}
  hull(){translate([36.5,y,15.3])sphere(d=.5);translate([36.5,y,25])sphere(d=.5);}
 }
}
module pcb_screws(){color("Silver") cover_mounts() translate([0,0,cover_bottom_z+cover_h]) cylinder(d=3.5,h=1.3);}
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
    step=view=="stage"?assembly_step:4;
    color("LightGray") translate([0,0,ex?16:0]) cut_view() proposed_hip();
    if(show_lower_fork && step>=2) color("Gainsboro") translate([0,0,ex?-18:0]) cut_view() original_lower_fork_local();
    if(step>=2) color("SlateGray") rotate(knee_angle) cut_view() proposed_shin();
    if(show_magnets && step>=2) rotate(knee_angle) cut_view() magnets();
    if(step>=3) translate([0,0,ex?20:0]) cut_view() pcb();
    if(step>=4) translate([0,0,ex?32:0]) cut_view() pcb_screws();
    if(step>=3) cut_view() wires();
    if(step>=4) color("LightSteelBlue") translate([0,0,ex?32:0]) cut_view() protective_cover();
    if(show_bearings && step>=2) color("Silver") cut_view() bearings();
    if(step>=2) color("Silver") cut_view() axle();
    if(show_rod && step>=2){color("DarkGray") cut_view() knee_rod(knee_angle);color("Silver") cut_view() rod_head(knee_angle);}
}
echo("PCB front/rear Z:",board_front_z,board_rear_z);
echo("Magnet surface/window/Hall clearance:",magnet_front_z,window_outer_z,board_front_z-encoder_hall_height()-magnet_front_z);
echo("Housing below original hip inner face10.5:",10.5-window_outer_z);
