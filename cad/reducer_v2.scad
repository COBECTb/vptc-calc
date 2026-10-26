// Accepted universal V2 reducer installation; generated package library.
use <base.scad>
use <clamp.scad>
use <pcb.scad>
use <sensors.scad>
module reducer_encoder_scene(
    view="assembly",
    assembly_step=5,
    rotation_angle=0,
    animate_rotation=false,
    with_bracing=true,
    show_electronics=true,
    show_clamp=true,
    show_magnets=true,
    show_bearing=true,
    show_separator=true,
    show_connectors=true,
    show_wires=true,
    light_channels=true,
    show_existing_position=false,
    load_connector_stem_h=15,
    load_connector_skirt=true,
    existing_face_offset=1,
    separator_axial_lift=0.5,
    magnet_height=1,
    magnet_to_window_gap=0.4,
    sensor_internal_gap=0.2,
    sensor_window_h=0.4,
    roof_extra_h=0.4,
    pcb_to_lid_gap=0.25,
    pcb_clearance=0.25,
    rear_surface_clearance=0.25,
    pcb_support_d=4.4,
    mcu_xy_clearance=0.2,
    mcu_axial_clearance=0.15,
    shaft_clearance_r=20.6,
    pcb_screw_pilot_d=1.6,
    pcb_screw_pilot_depth=4.5,
    pcb_screw_length=5,
    pcb_screw_head_d=3.8,
    pcb_screw_head_h=1.3,
    pcb_screw_head_gap=0.2,
    body_screw_head_d=6.72,
    body_screw_head_h=1.86,
    body_screw_recess_d=7.1,
    wire_outer_d=1.1,
    wire_clearance=0.2,
    time=0){

$fn = 96;
eps = 0.01; // Выход вычитаемых объёмов за открытые поверхности для быстрого просмотра.
original_cap_h = 11;
clamp_h = 12;
pcb_bottom_z = original_cap_h;
pcb_top_z = pcb_bottom_z + encoder_pcb_thickness();
sensor_front_z = pcb_top_z + encoder_sensor_height();
hall_z = pcb_top_z + encoder_hall_height();
pocket_ceiling_z = sensor_front_z + sensor_internal_gap;
window_front_z = pocket_ceiling_z + sensor_window_h;
lid_top_z = window_front_z;
main_pocket_ceiling_z = pocket_ceiling_z - roof_extra_h;
pcb_screw_ceiling_z = pcb_top_z + pcb_screw_head_h + pcb_screw_head_gap;
lid_base_z = pcb_top_z + pcb_to_lid_gap;
magnet_bottom_z = window_front_z + magnet_to_window_gap;
magnet_glue_face_z = magnet_bottom_z + magnet_height;
// Магнит утоплен в зажим; его рабочая поверхность остаётся на прежней высоте.
clamp_face_z = magnet_glue_face_z - connector_clamp_magnet_recess_depth();
required_face_offset = clamp_face_z - original_cap_h;
axial_increase = required_face_offset - existing_face_offset;
// Исходная отметка сепаратора -9; подшипник поднимается вместе с ним.
separator_base_z = -9 + separator_axial_lift;
separator_top_z = separator_base_z + 18.5;
main_bearing_bottom_z = separator_base_z + 11.5;
connector_flange_h = 4;
// После отражения зажима канавка Z2...10.2 находится между +1.8 и +10 от магнитного торца.
clamp_groove_near_z = clamp_face_z + 1.8;
clamp_groove_far_z = clamp_face_z + 10;
connector_contact_z = (clamp_groove_near_z + clamp_groove_far_z)/2;
// Глубина посадок автоматически укорачивает шейку на 0.4 мм: 7.15 -> 6.75.
reducer_connector_stem_h = connector_contact_z-connector_flange_h-separator_top_z;
wire_channel_bottom_z = pcb_top_z-0.1;
wire_channel_h = wire_outer_d+2*wire_clearance;
wire_channel_w = 4*wire_outer_d+6*wire_clearance;
wire_angle = compact_j1_angle();
wire_pad_r = compact_j1_radius();
wire_exit_r = compact_wire_exit_radius();
rotor_angle = animate_rotation ? 360*time : rotation_angle;

assert(view == "exploded" || view == "assembly" || view == "section" ||
       view == "cap" || view == "lid" || view == "print" || view == "stage" ||
       view == "output_connector" || view == "load_connector" || view == "lights" ||
       view == "light_guides" || view == "light_paths" || view == "pcb" ||
       view == "check_pcb_cap" || view == "check_pcb_lid" ||
       view == "check_light_guides" || view == "check_bearing" ||
       view == "check_m3_access" || view == "check_body_screw_heads", "Неизвестный режим отображения.");
assert(assembly_step >= 1 && assembly_step <= 5 && floor(assembly_step) == assembly_step,
    "Этап сборки должен быть целым числом от 1 до 5.");
assert(magnet_bottom_z - lid_top_z >= 0.3, "Недостаточен зазор до вращающихся магнитов.");
assert(rear_surface_clearance > 0 && rear_surface_clearance < 0.5,
    "Под платой нужен неглубокий зазор, сохраняющий опору подшипника.");
assert(lid_top_z-wire_channel_bottom_z-wire_channel_h >= sensor_window_h,
    "Канал проводов оставляет слишком тонкую крышу.");
assert(roof_extra_h >= 0 && main_pocket_ceiling_z > lid_base_z,
    "Основной карман крышки должен быть открыт со стороны платы.");
assert(pcb_screw_ceiling_z <= lid_top_z-sensor_window_h,
    "Головка винта платы упирается в крышку.");
assert(pcb_screw_length > encoder_pcb_thickness() &&
       pcb_screw_length-encoder_pcb_thickness()+0.2 <= pcb_screw_pilot_depth,
    "Проверьте длину M2: под платой нужен запас глубины не менее 0.2 мм.");
assert(reducer_connector_stem_h > 0 && load_connector_stem_h >= 4,
    "Проверьте длины шеек соединителей.");
assert(main_bearing_bottom_z+7 <= original_cap_h-1,
    "Подшипник поднят выше упора в крышке.");
assert(pcb_bottom_z-compact_mcu_height()-mcu_axial_clearance >= original_cap_h-1+0.2,
    "Локальный карман MCU должен оставаться выше посадки подшипника.");
assert(clamp_groove_far_z-clamp_groove_near_z >= 2*connector_flange_h,
    "Два фланца не помещаются в канавке зажима.");
echo("Магнитный торец от исходной крышки, мм:", required_face_offset);
echo("Увеличение относительно измеренного зазора, мм:", axial_increase);
echo("Магнит — корпус датчика, мм:", magnet_bottom_z - sensor_front_z);
echo("Магнит — Hall-точка по модели корпуса TI, мм:", magnet_bottom_z - hall_z);
echo("Длина шейки соединителя редуктора, мм:", reducer_connector_stem_h);

module annulus(outer_r, inner_r, h, segments = $fn) {
    difference() {
        cylinder(r = outer_r, h = h, $fn = segments);
        translate([0,0,-eps]) cylinder(r = inner_r, h = h+2*eps, $fn = segments);
    }
}

// Геометрия cap() из исходной модели с припуском вычитателей на открытых торцах.
// Глухие посадки заканчиваются на исходных Z: 3, 9 и 10 мм.
module encoder_cap_base() {
    $fn = 60;
    difference() {
        cylinder(r = 35, h = original_cap_h);
        translate([0,0,-eps]) cylinder(r = 26, h = original_cap_h-1+eps);
        translate([0,0,-eps]) cylinder(r = 24, h = original_cap_h+2*eps);
        translate([0,0,-eps]) cylinder(r = 27.08, h = 3+eps);
        encoder_body_bolt_positions() {
            translate([0,0,-eps]) cylinder(r = 1.6, h = original_cap_h+2*eps);
            translate([0,0,original_cap_h-2]) cylinder(r = 3, h = 2+eps);
        }
    }
}

// Верхняя половина отсекающего куба выходит за его наружные грани; плоскость Y=0 сохранена.
module encoder_bracing_cut(height, bottom_width, bottom_depth, top_width, top_depth) {
    difference() {
        cube([height,height,height], center = true);
        oval_cone(height, bottom_width, bottom_depth, top_width, top_depth, center = true);
        translate([-height/2-eps,0,-height/2-eps])
            cube([height+2*eps,height/2+eps,height+2*eps]);
    }
}

// Внешняя форма усиления используется также для обрезки прозрачных вставок.
module encoder_bracing_solid() {
    source_gear_h = 15.5;
    total_h = source_gear_h + original_cap_h;
    difference() {
        translate([-35,0,0]) cube([70,35,original_cap_h]);
        rotate([-90,90,0]) translate([2.2,-29,17.5])
            encoder_bracing_cut(35,total_h,total_h/2,total_h,total_h/2);
        rotate([90,90,0]) translate([2.2,-29,-17.5])
            encoder_bracing_cut(35,total_h,total_h/2,total_h,total_h/2);
    }
}
module encoder_outer_envelope() {
    union() {
        cylinder(r=35,h=original_cap_h,$fn=60);
        if(with_bracing) encoder_bracing_solid();
        encoder_pcb_outer_extension(original_cap_h);
    }
}
// A local lobe supports an enlarged PCB without changing the bearing or shaft seat.
// It is empty when the PCB plus its wall fits inside the original R35 cap.
module encoder_pcb_outer_extension(top_z) {
    bottom_z=max(0,pcb_bottom_z-pcb_screw_pilot_depth-1);
    translate([0,0,bottom_z]) linear_extrude(top_z-bottom_z)
        difference(){
            compact_pcb_outline(clearance=pcb_clearance+1);
            circle(r=35-.2,$fn=96);
        }
}
// Локальная версия cap_with_bracing(): исходная наружная форма сохранена.
module encoder_cap_with_bracing() {
    $fn = 60;
    source_side_short = 12.246;
    source_side_long = 29.564;
    difference() {
        union() {
            encoder_cap_base();
            difference() {
                encoder_bracing_solid();
                translate([0,0,-eps]) cylinder(r=35-eps,h=original_cap_h+eps);
            }
        }
        translate([0,35,-2.2]) rotate([90,22.5,0])
            for (i = [1,4]) rotate([0,0,45*i]) translate([16,0,-eps])
                cylinder(r=1.6,h=8+eps);
        translate([source_side_long/2-3,29,-eps]) cube([6,3,source_side_short/2+1+eps]);
        translate([-source_side_long/2-3,29,-eps]) cube([6,3,source_side_short/2+1+eps]);
    }
}

module rear_surface_relief() {
    difference() {
        compact_pcb_outline(clearance = pcb_clearance);
        // Контролируемая опора PCB только на свободные зоны вокруг отверстий.
        compact_pcb_mounts() circle(d = pcb_support_d);
    }
}

module wire_channel() {
    rotate([0,0,wire_angle])
        translate([wire_pad_r-1.1,-wire_channel_w/2,wire_channel_bottom_z])
            cube([wire_exit_r-wire_pad_r+1.1+eps,wire_channel_w,wire_channel_h]);
}

module encoder_wires() {
    // Начало над площадками J1. Провод выходит радиально за неподвижный корпус.
    // Цвета служат для различения жил, не заменяют распиновку KiCad.
    colors = ["Crimson","DimGray","SeaGreen","Goldenrod"];
    for (i = [0:3]) color(colors[i]) rotate([0,0,wire_angle])
        translate([wire_pad_r,-1.8+1.2*i,wire_channel_bottom_z+wire_channel_h/2])
            rotate([0,90,0]) cylinder(d=wire_outer_d,h=8,$fn=32);
}

// ISO 10642 M3: maximum head 6.72 x 1.86 mm. A 90-degree recess
// continues into the carrier so the head clears the lid-to-carrier joint.
module body_screw_head_relief() {
    depth=(body_screw_recess_d-3.2)/2;
    encoder_body_bolt_positions() translate([0,0,lid_top_z-depth])
        cylinder(d1=3.2,d2=body_screw_recess_d+2*eps,h=depth+eps);
}
module body_screw_heads() {
    encoder_body_bolt_positions() translate([0,0,lid_top_z-body_screw_head_h])
        cylinder(d1=3,d2=body_screw_head_d,h=body_screw_head_h,$fn=96);
}

module cap_encoder_carrier() {
    difference() {
        union() {
            if (with_bracing) encoder_cap_with_bracing(); else encoder_cap_base();
            encoder_pcb_outer_extension(lid_base_z);
            // Надстройка опирается на исходный торец; упор подшипника не утончается.
            translate([0,0,original_cap_h-eps])
                annulus(35, 24, lid_base_z-original_cap_h+eps);
        }
        // Плата над исходным торцом, внутренняя часть нависает над подшипником.
        translate([0,0,pcb_bottom_z])
            linear_extrude(height = lid_base_z-pcb_bottom_z+eps)
                compact_pcb_outline(clearance = pcb_clearance);
        // Сохраняем материал: вместо общей глубокой выборки — зазор 0.25 мм
        // под пайку и отдельные карманы по высоте каждого обратного компонента.
        translate([0,0,pcb_bottom_z-rear_surface_clearance])
            linear_extrude(height = rear_surface_clearance+eps) rear_surface_relief();
        // Локальные карманы всех обратных компонентов по актуальному размещению PCB.
        // У MCU дно Z10.25; карманы у R26 проверяются вместе с подшипником Ø52.
        compact_rear_clearances();
        if(light_channels) status_light_channels();
        compact_pcb_mounts()
            translate([0,0,pcb_bottom_z-pcb_screw_pilot_depth])
                cylinder(d = pcb_screw_pilot_d, h = pcb_screw_pilot_depth+eps);
        // Штатные шесть отверстий M3 продолжаются через надстройку.
        encoder_body_bolt_positions()
            translate([0,0,original_cap_h-eps]) cylinder(d = 3.2, h = 5);
        body_screw_head_relief();
        // Четыре тонких провода выходят вбок, без высокой штыревой гребёнки.
        wire_channel();
    }
}


// Три независимых оптических пути обходят винты и корпуса компонентов.
// Вставки — экспериментальные прозрачные детали, не непрозрачный FDM-пластик.
function status_xy(r,a,z)=[r*cos(a),r*sin(a),z];
function status_arc(r,a,b,z)=let(n=max(1,ceil(abs(b-a)/4)))
    [for(j=[0:n]) status_xy(r,a+(b-a)*j/n,z)];
function status_light_exit_angle(i)=[32,38,-30][i];
function status_light_path(i)=let(c=compact_led_points()[i],r=c[0],a=c[1],z=pcb_bottom_z-.4,
    bend=i==0?50:60,outer=i==0?34:35.5,exit_a=status_light_exit_angle(i))
    i<2 ? concat(status_arc(r,a,bend,z),status_arc(outer,bend,exit_a,z),[status_xy(51,exit_a,z)])
        : concat([status_xy(r,a,z)],status_arc(29.2,a,exit_a,z),[status_xy(51,exit_a,z)]);
module status_path_tube(i,d){
    path=status_light_path(i);
    for(j=[0:len(path)-2]) hull(){
        translate(path[j]) sphere(d=d,$fn=20);
        translate(path[j+1]) sphere(d=d,$fn=20);
    }
}
module status_light_channels(){
    for(i=[0:len(compact_led_points())-1]) let(c=compact_led_points()[i]) {
        // Дно Z10.2: 0.2 мм материала над ступенью подшипника Z10.
        rotate(c[1]) translate([c[0],0,pcb_bottom_z-.8]) cylinder(d=1.4,h=.8+eps,$fn=32);
        status_path_tube(i,.8);
    }
}
module status_light_guide(i){
    difference(){
        intersection(){status_path_tube(i,.6);encoder_outer_envelope();}
        // Плоский вход под LED: верх Z10.65, корпус LED начинается на Z10.7.
        let(c=compact_led_points()[i]) rotate(c[1]) translate([c[0],0,pcb_bottom_z-.35])
            cylinder(d=2.2,h=2,$fn=32);
    }
}
module status_light_ports(){
    for(i=[0:len(compact_led_points())-1])
        color(["SeaGreen","Gold","Crimson"][i]) status_light_guide(i);
}
module status_light_guides_for_print(){
    // Сохраняем взаимное положение: три раздельных тела из прозрачной смолы.
    translate([0,0,-(pcb_bottom_z-.7)])
        for(i=[0:len(compact_led_points())-1]) status_light_guide(i);
}
module compact_rear_clearances(){
 for(c=compact_component_list()) if(!c[3]) rotate(c[1]) translate([c[0],0,pcb_bottom_z-c[4][2]-mcu_axial_clearance]) rotate(c[2]-c[1])
  translate([-c[4][0]/2-mcu_xy_clearance,-c[4][1]/2-mcu_xy_clearance,0])
   cube([c[4][0]+2*mcu_xy_clearance,c[4][1]+2*mcu_xy_clearance,c[4][2]+mcu_axial_clearance+eps]);
}
module compact_front_clearances(){
 for(c=compact_component_list()) if(c[3] && c[4][2]>1.0) rotate(c[1]) translate([c[0],0,lid_base_z-eps]) rotate(c[2]-c[1])
  translate([-c[4][0]/2-.25,-c[4][1]/2-.25,0]) cube([c[4][0]+.5,c[4][1]+.5,pcb_top_z+c[4][2]+.2-lid_base_z+eps]);
}

module sensor_lid() {
    difference() {
        // Выход проводов с лицевой стороны платы.

        union(){
            translate([0,0,lid_base_z])
                annulus(35, shaft_clearance_r, lid_top_z-lid_base_z);
            translate([0,0,lid_base_z]) linear_extrude(lid_top_z-lid_base_z)
                difference(){
                    compact_pcb_outline(clearance=pcb_clearance+1);
                    circle(r=35-.2,$fn=96);
                }
        }
        translate([0,0,lid_base_z-eps])
            linear_extrude(height = main_pocket_ceiling_z-lid_base_z+eps)
                compact_pcb_outline(clearance = pcb_clearance);
        compact_front_clearances();
        wire_channel();
        // Карманы открыты изнутри. Снаружи единый ровный торец, над датчиками 0.4 мм пластика.
        encoder_sensor_positions()
            translate([0,0,lid_base_z-eps])
                linear_extrude(height = pocket_ceiling_z-lid_base_z+eps)
                    encoder_sensor_body_outline(clearance = pcb_clearance);
        // Головкам M2 оставлен свой зазор; основная крыша между карманами толще.
        compact_pcb_mounts()
            translate([0,0,lid_base_z-eps])
                cylinder(d = pcb_screw_head_d+2*pcb_clearance,
                    h = pcb_screw_ceiling_z-lid_base_z+eps);
        body_screw_head_relief();
        // M3 ISO 10642: длину винта подобрать по полной толщине сборки.
        encoder_body_bolt_positions() {
            translate([0,0,lid_base_z-eps]) cylinder(d = 3.2, h = lid_top_z-lid_base_z+2*eps);

        }
    }
}

// Повернуть физическую деталь, а не зеркалить: наружный ровный торец на столе,
// карманы компонентов открыты вверх и не требуют мостов над платой.
module sensor_lid_for_print() {
    translate([0,0,lid_top_z]) rotate([180,0,0]) sensor_lid();
}

module pcb_in_cap(with_fasteners=true) {
    // Исходный макет платы направляет датчики вниз; здесь они смотрят к магнитам вверх.
    translate([0,0,pcb_top_z]) mirror([0,0,1])
        compact_pcb();
    // M2x5 с низкой головкой Ø3.8 x 1.3 мм; размер SLH-M2 по чертежу NBK.
    // Длина измеряется от опорной поверхности головки, без самой головки.
    if(with_fasteners) color("Silver") compact_pcb_mounts() {
        translate([0,0,pcb_top_z]) cylinder(d = pcb_screw_head_d, h = pcb_screw_head_h);
        translate([0,0,pcb_top_z-pcb_screw_length])
            cylinder(d = 2, h = pcb_screw_length+eps);
    }
}

module clamp_facing_cap(face_z = clamp_face_z) {
    translate([0,0,face_z+clamp_h]) mirror([0,0,1]) {
        for (half = [0,1]) rotate([0,0,180*half]) {
            color("SlateGray") {
                connector_clamp_base();
                magnet_rims();
            }
            // Отдельный вызов сохраняет цвет магнитов и показывает их также при F6.
            if (show_magnets) magnet_preview(second_half = half == 1);
        }
    }
}

module main_bearing_in_cap() {
    // Подшипник 40 x 52 x 7; при подъёме 0.5 мм торцы находятся на Z3 и Z10.
    translate([0,0,main_bearing_bottom_z]) annulus(26,20,7,segments = 60);
}

module separator_in_cap() {
    translate([0,0,separator_base_z]) separator();
}

module output_connector_in_cap() {
    // Торец шейки опирается на сепаратор, фланец расположен внутри канавки зажима.
    translate([0,0,connector_contact_z]) mirror([0,0,1])
        output_connector_for_print();
}

module output_connector_for_print() {
    reducer_connector(h1 = reducer_connector_stem_h, skirt = false);
}

module load_connector_in_clamp() {
    // Соединитель другой детали смотрит от редуктора; юбка начинается выше зажима.
    translate([0,0,connector_contact_z])
        load_connector_for_print();
}

module load_connector_for_print() {
    reducer_connector(h1 = load_connector_stem_h, skirt = load_connector_skirt,
        holes = [1,0,1,0,1,0,1,0]);
}

module section_space() {
    rotate([0,0,9]) translate([-45,0,-40]) cube([90,60,140]);
}

module visible_cut() {
    if (view == "section") intersection() { children(); section_space(); }
    else children();
}

if (view == "check_pcb_cap") {
    // Резьба винтов намеренно входит в пилоты пластика; проверяем здесь PCB.
    intersection(){pcb_in_cap(with_fasteners=false);cap_encoder_carrier();}
} else if (view == "check_pcb_lid") {
    intersection(){pcb_in_cap();sensor_lid();}
} else if (view == "check_m3_access") {
    // Сохраняем сборочные окна и в PCB-модели, включая замкнутые внутренние контуры.
    // 0.01 мм исключают только аппроксимацию окружности в экспортированном контуре.
    intersection(){
        pcb_in_cap(with_fasteners=false);
        encoder_body_bolt_positions() translate([0,0,-eps])
            cylinder(r=3.4-.01,h=lid_top_z+2*eps,$fn=128);
    }
} else if (view == "check_body_screw_heads") {
    intersection(){
        body_screw_heads();
        union(){pcb_in_cap();cap_encoder_carrier();sensor_lid();}
    }
} else if (view == "check_light_guides") {
    intersection(){pcb_in_cap();for(i=[0:len(compact_led_points())-1]) status_light_guide(i);}
} else if (view == "check_bearing") {
    // Исключаем только 0.001 мм штатного контакта наружного кольца с посадкой.
    // Размеры самого подшипника и посадки не меняются.
    intersection(){
        translate([0,0,main_bearing_bottom_z+.001])
            annulus(26-.001,20+.001,7-.002,segments=60);
        cap_encoder_carrier();
    }
} else if (view == "pcb") {
    pcb_in_cap();
} else if (view == "light_paths") {
    status_light_channels();
} else if (view == "light_guides") {
    status_light_guides_for_print();
} else if (view == "cap") {
    cap_encoder_carrier();
} else if (view == "lid") {
    sensor_lid_for_print();
} else if (view == "output_connector") {
    output_connector_for_print();
} else if (view == "load_connector") {
    load_connector_for_print();
} else if (view == "print") {
    translate([-39,0,0]) cap_encoder_carrier();
    translate([39,0,0]) sensor_lid_for_print();
} else {
    pcb_lift = view == "exploded" ? 5 : 0;
    lid_lift = view == "exploded" ? 12 : 0;
    bearing_lift = view == "exploded" ? -10 : 0;
    separator_lift = view == "exploded" ? -25 : 0;
    output_lift = view == "exploded" ? 20 : 0;
    load_lift = view == "exploded" ? 32 : 0;
    color("LightGray") visible_cut() cap_encoder_carrier();
    if (view != "stage" || assembly_step >= 3)
        color("Gainsboro") translate([0,0,lid_lift]) visible_cut() sensor_lid();
    // В сборочных режимах показаны все включённые детали, включая полный рендер F6.
    // Для отдельных печатных деталей использовать cap, lid или print.
    if (show_electronics && (view != "stage" || assembly_step >= 2))
        translate([0,0,pcb_lift]) visible_cut() pcb_in_cap();
    if (show_wires && (view != "stage" || assembly_step >= 2))
        translate([0,0,pcb_lift]) visible_cut() encoder_wires();
    if (show_bearing)
        color("Silver") translate([0,0,bearing_lift]) visible_cut() main_bearing_in_cap();
    if (show_separator)
        color("DarkSalmon") translate([0,0,separator_lift]) visible_cut() rotate([0,0,rotor_angle]) separator_in_cap();
    if (show_connectors && (view != "stage" || assembly_step >= 4)) {
        color("LightSteelBlue") translate([0,0,output_lift]) visible_cut() rotate([0,0,rotor_angle]) output_connector_in_cap();
        color("SteelBlue") translate([0,0,load_lift]) visible_cut() rotate([0,0,rotor_angle]) load_connector_in_clamp();
    }
    if (show_clamp && (view != "stage" || assembly_step >= 5))
        translate([0,0,output_lift]) visible_cut() rotate([0,0,rotor_angle]) clamp_facing_cap();
    if ($preview && show_existing_position)
        %color("DarkOrange", 0.45)
            visible_cut() clamp_facing_cap(original_cap_h+existing_face_offset);
    if(view=="lights") status_light_ports();
}

}
