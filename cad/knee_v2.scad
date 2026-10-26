// Accepted D70 knee installation; generated package library.
use <base.scad>
use <foots.scad>
use <pcb.scad>
use <sensors.scad>
module knee_encoder_scene(view="assembly",assembly_step=4,knee_angle=0,animate=true,
    show_magnets=true,show_bearings=true,show_rod=true,show_lower_fork=true,time=0){
// Отдельная механическая сборка универсальной PCB V2.
// Колено: компактная общая плата и секторный магнитоноситель.
// Корпуса компонентов по фактическому размещению разведённой платы V2.
// Исходные hip()/hip_top()/shin() сохранены в оригинальном файле.
// Z=0 — плоскость вращения shin() в исходной leg(); ось колена — [0,0].
$fn=64;
eps=.01;
board_rotation=-81; // Hall при −72°: минимум добавленного бокового объёма у щеки.
// Края полукольца лежат на продольной оси шарнира (ось X голени).
sector_start=-180;
sector_end=0;
knee_min=-44.6458; // С учётом исходной тяги.
knee_max=54.2040;
rotor_top_z=12.7;
rotor_bottom_z=10.7;
rotor_stiffener_bottom_z=9.1; // Усиление вниз: торец магнитов остаётся прежним.
recess_depth=.4;
rotor_glue_z=rotor_top_z-recess_depth;
magnet_ring_h=.8;
magnet_front_z=rotor_top_z-recess_depth+1; //13.3
window_outer_z=13.7;
window_inner_z=14.1;
board_front_z=15.75; // PCB0.8, датчики вниз1.45мм ->14.3, внутренний зазор0.2.
board_rear_z=board_front_z+.8;
cavity_roof_z=18.2; // Задние корпуса до18.0; зазор0.2.
housing_top_z=23.5; // Наружный торец исходной неподвижной щеки.
cover_h=2;
cover_bottom_z=housing_top_z-cover_h; // Крышка заподлицо, а не над щекой.
lid_xy_gap=.2;
wall_h=1.2;
board_xy_gap=.25;
board_floor_z=board_front_z-.25;
wire_angle=board_rotation+compact_j1_angle();
wire_pad_r=compact_j1_radius();
wire_exit_r=compact_wire_exit_radius();
wire_tail_shift=max(0,wire_exit_r-35);
wire_d=1.0;
wire_front_z=board_front_z-.60;
wire_roof_z=cover_bottom_z-.75;
wire_knee=[wire_exit_r*cos(wire_angle),wire_exit_r*sin(wire_angle)];
wire_turn=[22,-35-wire_tail_shift];
wire_elbow=[22,-43-wire_tail_shift];
wire_exit=[40,-43-wire_tail_shift];
cover_screw_h=1.3;
cover_screw_d=3.8; // Низкая головка M2, габарит NBK SLH-M2-6 (DIN 7984).
cover_screw_seat_z=cover_bottom_z+.6;
cover_screw_l=6;

function knee_board_rotation()=board_rotation;
function knee_board_front_z()=board_front_z;
function knee_board_rear_z()=board_rear_z;
function knee_cover_face_z()=housing_top_z;
function knee_sensor_angle()=9+board_rotation;
function knee_wire_diameter()=wire_d;
function knee_source_pcb_sha256()=compact_source_pcb_sha256();
// Полный плавный цикл между проверенными границами; при time=0 — заданный угол.
function knee_animation_angle(t,start_angle=0)=let(
    middle=(knee_min+knee_max)/2,
    amplitude=(knee_max-knee_min)/2,
    bounded=max(knee_min,min(knee_max,start_angle)),
    phase=asin((bounded-middle)/amplitude))
    (t==0 || t==1)?bounded:middle+amplitude*sin(360*t+phase);
// Вычислять в момент вызова: специальная time не должна фиксироваться в глобальной переменной.
function knee_display_angle(t)=animate?knee_animation_angle(t,knee_angle):knee_angle;


assert(abs(window_outer_z-magnet_front_z-.4)<1e-6,"Магнитный зазор");
assert(abs(board_front_z-1.45-window_inner_z-.2)<1e-6,"Внутренний зазор датчика");

module annulus(ro,ri,h){difference(){cylinder(r=ro,h=h);translate([0,0,-eps]) cylinder(r=ri,h=h+2*eps);}}
module board_shape(clearance=0){rotate(board_rotation) compact_pcb_outline(clearance);}
module board_mounts(){rotate(board_rotation) compact_pcb_mounts() children();}
// Два крепления в свободных вырезах PCB; третье удерживает плоский кабельный хвост.
module cover_mounts(){
    rotate(board_rotation) for(a=[-21,39]) rotate(a) translate([31.5,0,0]) children();
    translate([27.2,-37.5-wire_tail_shift,0]) children();
}
module lid_outline(){
    // Кабельная часть целиком внутри исходной ширины детали; выход в боковую грань.
    intersection(){
        union(){
            board_shape(.7);
            cover_mounts() circle(r=2.9,$fn=48);
            rotate(board_rotation) for(a=[-21,39]) rotate(a)
                translate([27.5,-1.2]) square([4,2.4]);
            for(pair=[[wire_knee,wire_turn],[wire_turn,wire_elbow],[wire_elbow,wire_exit]])
                hull(){translate(pair[0])circle(r=3.6,$fn=48);translate(pair[1])circle(r=3.6,$fn=48);}
            hull(){translate(wire_turn)circle(r=3.6,$fn=48);translate([27.2,-37.5-wire_tail_shift])circle(r=2.9,$fn=48);}
        }
        translate([-60,-120])square([97.8,180]);
    }
}
module shell_outline(){
    intersection(){offset(delta=lid_xy_gap+wall_h)lid_outline();translate([-60,-120])square([98,180]);}
}
module original_hip_local(){translate([-12,-119,-9.5]) hip();}
module original_lower_fork_local(){translate([-12,-166,-20.5]) hip_top();}

module sector_gate(z,h){translate([0,0,z])linear_extrude(h)polygon(concat([[0,0]],[for(i=[0:180])let(a=sector_start+(sector_end-sector_start)*i/180)[100*cos(a),100*sin(a)]]));}
module knee_magnet_positions(){
 for(t=[0,1]) let(n=t==0?24:26,r=t==0?23.5:29.5)
  for(j=[0:n-1]) let(a=(j+.5)*360/n,sa=a>180?a-360:a)
   if(sa>=sector_start && sa<=sector_end) translate([r*cos(a),r*sin(a),rotor_top_z]) children();
}
module rotor_supports(){
 // Две разнесённые опоры на обоих плечах шарнира. Корни Ø10, верх Ø8.
 // Длинное плечо имеет верх Z=9, здесь опора заглублена до Z=7.
 hull(){
  translate([-25,-2,7]) cylinder(d=10,h=1);
  translate([-25,-10,rotor_stiffener_bottom_z]) cylinder(d=8,h=rotor_glue_z-rotor_stiffener_bottom_z);
 }
 // Короткое плечо ниже и наклонено: корень опущен до Z=-1.
 // Стойка сдвинута на +Y, в сторону от тяги; верхняя косынка выходит под сектор.
 hull(){
  translate([25,4,-1]) cylinder(d=10,h=1);
  translate([25,4,3]) cylinder(d=8,h=rotor_stiffener_bottom_z-3+eps);
 }
 hull(){
  translate([25,4,rotor_stiffener_bottom_z-.4]) cylinder(d=8,h=rotor_glue_z-rotor_stiffener_bottom_z+.4);
  translate([25,-3,rotor_bottom_z]) cylinder(d=8,h=rotor_glue_z-rotor_bottom_z);
 }
}
module rotor_blank(){
 // Внутренняя часть основания 3.2 мм вместо 1.6; скос сохраняет просвет у ушка тяги.
 intersection(){
  rotate_extrude() polygon([[20,rotor_stiffener_bottom_z],[28.4,rotor_stiffener_bottom_z],
   [30,rotor_bottom_z],[33,rotor_bottom_z],[33,rotor_glue_z],[20,rotor_glue_z]]);
  sector_gate(rotor_stiffener_bottom_z-eps,rotor_glue_z-rotor_stiffener_bottom_z+2*eps);
 }
 rotor_supports();
 // Один установочный штифт исключает ошибочный сдвиг сектора при приклейке.
 rotate(-150) translate([21.2,0,rotor_glue_z-eps]) cylinder(d=1.2,h=.4+eps,$fn=24);
}
module knee_magnet_ring(){
    // Печатается отдельно плашмя: все 25 ячеек сквозные, без тонких донышек.
    difference(){
        intersection(){
            translate([0,0,rotor_glue_z]) annulus(33,20,magnet_ring_h);
            sector_gate(rotor_glue_z-eps,magnet_ring_h+2*eps);
        }
        knee_magnet_positions() translate([0,0,-recess_depth-eps])
            cylinder(d=5.2,h=magnet_ring_h+2*eps);
        rotate(-150) translate([21.2,0,rotor_glue_z-eps]) cylinder(d=1.6,h=magnet_ring_h+2*eps,$fn=32);
    }
}
module knee_rotor(){union(){rotor_blank();knee_magnet_ring();}}
// Отдельный штатный зажим стопы, а не объединённая с голенью старая заглушка.
module printed_foot_connector(){foot_cuff();}
module foot_cuff_in_knee(){translate([-47,0,0])rotate([180,180,0])foot_cuff();}
module proposed_shin(){
    union(){shin(foot=false);rotor_blank();}
}
module magnets(){
 for(t=[0,1]) let(n=t==0?24:26,r=t==0?23.5:29.5)
  for(j=[0:n-1]) let(a=(j+.5)*360/n,sa=a>180?a-360:a)
   if(sa>=sector_start && sa<=sector_end) color(j%2==0?"Firebrick":"RoyalBlue")
    translate([r*cos(a),r*sin(a),rotor_top_z-recess_depth]) cylinder(d=5,h=1);
}
// Выборка заканчивается у наружной стороны окна: исходная щека не должна
// оставлять незапланированный слой пластика под защитной мембраной.
// По обоим краям 0.5 мм радиального зазора вместо 0.2:
// с учётом граней цилиндров при повороте остаётся не менее 0.4 мм.
module rotor_swept_clearance(){translate([0,0,6.8]) annulus(33.5,19.5,window_outer_z-6.8);}

module stationary_shell(){
    translate([0,0,window_outer_z])
        linear_extrude(housing_top_z-window_outer_z) shell_outline();
}
module front_component_pockets(){
    rotate(board_rotation){
        encoder_sensor_positions()
            translate([0,0,window_inner_z])
                linear_extrude(board_front_z-window_inner_z+eps)
                    encoder_sensor_body_outline(.2);
        for(c=compact_component_list()) if(c[3])
            rotate(c[1]) translate([c[0],0,board_front_z-c[4][2]-.2])
                rotate(c[2]-c[1])
                    linear_extrude(c[4][2]+.2+eps)
                        square([c[4][0]+.4,c[4][1]+.4],center=true);
    }
}
module pcb_cavity(){
    // Толстое дно между локальными карманами вместо общей мембраны 0.4 мм.
    translate([0,0,board_floor_z])
        linear_extrude(housing_top_z-board_floor_z+eps) board_shape(board_xy_gap);
    front_component_pockets();
    // Гнездо съёмной крышки: боковой зазор 0.2 мм, бортик 1.2 мм.
    translate([0,0,cover_bottom_z])
        linear_extrude(cover_h+eps) offset(delta=lid_xy_gap)lid_outline();
}
module pcb_supports(){board_mounts(){
    translate([0,0,board_floor_z-eps]) cylinder(d=3.8,h=board_front_z-board_floor_z+eps);
    translate([0,0,board_front_z-eps]) cylinder(d=1.8,h=.6+eps);
}}
module cable_channels(){
    // Нижний отрезок от J1 выходит радиально за край PCB.
    rotate(wire_angle) translate([wire_pad_r-.7,-2.5,wire_front_z-.7])
        cube([wire_exit_r+.9-wire_pad_r+.7,5,1.4]);
    // Вертикальная часть внутри стенки, открытая сверху под съёмную крышку.
    translate([wire_knee[0],wire_knee[1],wire_front_z-.7])
        linear_extrude(cover_bottom_z-wire_front_z+.7+eps)
            rotate(wire_angle) square([2.8,5],center=true);
    for(pair=[[wire_knee,wire_turn],[wire_turn,wire_elbow],[wire_elbow,wire_exit]])
        hull(){
            translate([pair[0][0],pair[0][1],wire_roof_z-.7]) cylinder(d=6.4,h=cover_bottom_z-wire_roof_z+.7+eps,$fn=32);
            translate([pair[1][0],pair[1][1],wire_roof_z-.7]) cylinder(d=6.4,h=cover_bottom_z-wire_roof_z+.7+eps,$fn=32);
        }
}
module proposed_hip(){
    difference(){
        union(){
            difference(){
                union(){original_hip_local();stationary_shell();}
                pcb_cavity();rotor_swept_clearance();
            }
            pcb_supports();
        }
        cover_mounts() translate([0,0,cover_bottom_z-6.2]) cylinder(d=1.6,h=6.2+eps);
        cable_channels();
    }
}
module protective_cover(){
    difference(){
        union(){
            translate([0,0,cover_bottom_z]) linear_extrude(cover_h) lid_outline();
            // Прижим только по штатным свободным кольцам PCB.
            board_mounts() translate([0,0,board_rear_z])
                cylinder(d=3.8,h=cover_bottom_z-board_rear_z+eps);
            // Низкие внутренние рёбра; корпуса деталей не задевают.
            for(a=[board_rotation+9-18,board_rotation+9+18]) rotate(a)
                translate([30.5,-.6,cavity_roof_z])
                    cube([2.8,1.2,cover_bottom_z-cavity_roof_z+eps]);
        }
        // Прямые световые окна; при желании закрыть прозрачными вставками.
        rotate(board_rotation) for(c=compact_led_points()) rotate(c[1])
            translate([c[0],0,cavity_roof_z-eps])
                cylinder(d=1.4,h=housing_top_z-cavity_roof_z+2*eps,$fn=32);
        cover_mounts(){
            translate([0,0,cover_bottom_z-eps]) cylinder(d=2.2,h=cover_h+2*eps);
            translate([0,0,cover_screw_seat_z]) cylinder(d=4.2,h=housing_top_z-cover_screw_seat_z+eps);
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
function unit2(v)=v/norm(v);
function left_normal(v)=let(u=unit2(v))[-u.y,u.x];
function xy_corner(a,p,b,t,r=3.4)=let(u=unit2(p-a),v=unit2(b-p),
    turn=atan2(u.x*v.y-u.y*v.x,u*v),sgn=turn>0?1:-1,
    distance=r*tan(abs(turn)/2),start=p-distance*u,
    center=start+sgn*r*left_normal(u),rad=r-sgn*t,
    angle=atan2(start.y-center.y,start.x-center.x))
    [for(k=[0:6])let(a=angle+turn*k/6)center+rad*[cos(a),sin(a)]];
function upper_wire(t)=concat(
    [wire_knee+t*left_normal(wire_turn-wire_knee)],
    xy_corner(wire_knee,wire_turn,wire_elbow,t),
    xy_corner(wire_turn,wire_elbow,wire_exit,t),
    [wire_exit+t*left_normal(wire_exit-wire_elbow)]);
function wire_start(t)=[wire_pad_r*cos(wire_angle)-t*sin(wire_angle),
    wire_pad_r*sin(wire_angle)+t*cos(wire_angle),wire_front_z];
function wire_vertical_start(t)=[wire_knee[0]-t*sin(wire_angle),
    wire_knee[1]+t*cos(wire_angle),wire_front_z];
function smooth_wire(points)=concat([points[0]],
    [for(i=[1:len(points)-2]) each let(p=points[i],a=points[i-1],b=points[i+1],
        r=min(1.1,norm(p-a)/3,norm(b-p)/3),
        start=p-r*(p-a)/norm(p-a),end=p+r*(b-p)/norm(b-p))
        [for(k=[0:4]) let(t=k/4) (1-t)*(1-t)*start+2*t*(1-t)*p+t*t*end]],
    [points[len(points)-1]]);
module wires(){
    for(t=[-1.8,-.6,.6,1.8]) let(upper=upper_wire(t),
        upper3=[for(p=upper)[p.x,p.y,wire_roof_z]],
        lower=smooth_wire([wire_start(t),wire_vertical_start(t),upper3[0],upper3[1]]),
        points=concat(lower,[for(i=[2:len(upper3)-1])upper3[i]]))
        color("DarkSlateGray") for(i=[0:len(points)-2]) hull(){
            translate(points[i]) sphere(d=wire_d,$fn=12);
            translate(points[i+1]) sphere(d=wire_d,$fn=12);
        }
}
module pcb_screws(){color("Silver") cover_mounts(){
    translate([0,0,cover_screw_seat_z]) cylinder(d=cover_screw_d,h=cover_screw_h);
    translate([0,0,cover_screw_seat_z-cover_screw_l]) cylinder(d=2,h=cover_screw_l);
}}
module bearings(){
    // По дну реальных посадок: leg() показывает оба подшипника примерно на2.5мм выше.
    // Здесь отображены правильные посадки, без изменения исходного leg().
    translate([0,0,10.5]) annulus(8,4,5);
    translate([0,0,-14.5]) annulus(8,4,5);
}
module cut_view(){if(view=="section") intersection(){children();translate([0,-200,-40])cube([100,250,100]);}else children();}

// Прижимы касаются только двух штатных колец PCB. Для объёмного контроля
// исключаем 0.001 мм у этих плоскостей, не весь крепёжный карман.
module pcb_without_mount_contact(){
    difference(){
        pcb();
        board_mounts(){
            translate([0,0,board_front_z-.001]) cylinder(d=3.82,h=.002,$fn=64);
            translate([0,0,board_rear_z-.001]) cylinder(d=3.82,h=.002,$fn=64);
        }
    }
}

if(view=="check_pcb_housing") intersection(){pcb_without_mount_contact();union(){proposed_hip();protective_cover();}}
else if(view=="lower_print") translate([0,0,20.5]) original_lower_fork_local();
else if(view=="shin_print") translate([0,0,9.5]) proposed_shin();
else if(view=="hip") proposed_hip();
else if(view=="shin") rotate(knee_display_angle(time)) proposed_shin();
else if(view=="rotor") rotate(knee_display_angle(time)) knee_rotor();
else if(view=="mount") rotate(knee_display_angle(time)) {color("LightGray")shin(foot=false);color("DarkOrange")rotor_blank();}
else if(view=="cover") protective_cover();
else if(view=="pcb") pcb();
else if(view=="magnet_ring") rotate(knee_display_angle(time)) knee_magnet_ring();
else if(view=="ring_print") translate([0,0,-rotor_glue_z]) knee_magnet_ring();
else if(view=="cover_print") translate([0,0,housing_top_z]) rotate([180,0,0]) protective_cover();
else if(view=="hip_print") translate([0,0,housing_top_z]) rotate([180,0,0]) proposed_hip();
else{
    ex=view=="exploded";
    step=view=="stage"?assembly_step:4;
    color("LightGray") translate([0,0,ex?16:0]) cut_view() proposed_hip();
    if(show_lower_fork && step>=2) color("Gainsboro") translate([0,0,ex?-18:0]) cut_view() original_lower_fork_local();
    if(step>=2) color("SlateGray") rotate(knee_display_angle(time)) cut_view() proposed_shin();
    if(step>=2) color("DarkSlateGray") rotate(knee_display_angle(time)) cut_view() knee_magnet_ring();
    if(step>=2) color("CadetBlue") rotate(knee_display_angle(time)) cut_view() foot_cuff_in_knee();
    if(show_magnets && step>=2) rotate(knee_display_angle(time)) cut_view() magnets();
    if(step>=3) translate([0,0,ex?20:0]) cut_view() pcb();
    if(step>=4) translate([0,0,ex?32:0]) cut_view() pcb_screws();
    if(step>=3) translate([0,0,ex?20:0]) cut_view() wires();
    if(step>=4) color("LightSteelBlue") translate([0,0,ex?32:0]) cut_view() protective_cover();
    if(show_bearings && step>=2) color("Silver") cut_view() bearings();
    if(step>=2) color("Silver") cut_view() axle();
    if(show_rod && step>=2){color("DarkGray") cut_view() knee_rod(knee_display_angle(time));color("Silver") cut_view() rod_head(knee_display_angle(time));}
}
echo("PCB front/rear Z:",board_front_z,board_rear_z);
echo("Magnet surface/window/Hall clearance:",magnet_front_z,window_outer_z,board_front_z-encoder_hall_height()-magnet_front_z);
echo("Flush cover and recessed screw top Z:",housing_top_z,cover_screw_seat_z+cover_screw_h);
echo("Board sensor azimuth:",9+board_rotation);
echo("PCB source SHA256:",compact_source_pcb_sha256());

echo("Knee angle / animation t:",knee_display_angle(time),time);

}
