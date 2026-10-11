// Компоновочный вариант верхней крышки для одной платы: 2 x TMAG5273 + CAN.
// Магниты обращены к крышке; штатный зажим импортируется без изменения.
// В сборке шейка выходного соединителя удлинена под новую крышку.
// Это вариант для согласования компоновки, не готовая замена в существующей сборке.
// Плата является макетом габаритов, электрическая схема и трассировка пока не сделаны.
use <vptc_roller_19_4_5_70.scad>
use <connector_clamp_magnets_5mm.scad>
use <encoder_can_pcb_layout.scad>
use <../electronics/encoder_can/design/placed_components.scad>

/* [Отображение] */
view = "assembly"; // [exploded:Разнесённая сборка, assembly:Сборка, section:Разрез, cap:Основание, lid:Крышка, print:Две детали для печати]
with_bracing = true;
show_electronics = true;
show_clamp = true;
show_magnets = true;
show_bearing = true;
show_separator = true;
show_connectors = true;
show_existing_position = false; // Оранжевым: магнитный торец на текущем расстоянии 1 мм.

/* [Соединитель другой детали] */
load_connector_stem_h = 15; // Как у соединителя корпуса в исходной модели.
load_connector_skirt = true;

/* [Осевые зазоры] */
existing_face_offset = 1; // Измеренное расстояние от исходной крышки до торца под клей.
separator_axial_lift = 0.5; // Подъём сепаратора и его подшипника относительно исходной сборки.
magnet_height = 1;
magnet_to_window_gap = 0.4; // Воздух от магнита до ровного наружного торца крышки.
sensor_internal_gap = 0.2;
sensor_window_h = 0.4;
roof_extra_h = 0.4; // Дополнительная толщина крыши вне локальных внутренних карманов.
pcb_to_lid_gap = 0.25;

/* [Посадки и крепёж] */
pcb_clearance = 0.25;
rear_pocket_inner_r = 27;
rear_pocket_outer_r = 33.7;
rear_pocket_depth = 2.3;
mcu_xy_clearance = 0.2;
mcu_axial_clearance = 0.15;
shaft_clearance_r = 20.6;
pcb_screw_pilot_d = 1.6;
pcb_screw_head_d = 3.5;
pcb_screw_head_h = 1.3; // Низкая головка M2; стандартная высокая головка не помещается.
pcb_screw_head_gap = 0.2;

/* [Hidden] */
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
required_face_offset = magnet_glue_face_z - original_cap_h;
axial_increase = required_face_offset - existing_face_offset;
// Исходная отметка сепаратора -9; подшипник поднимается вместе с ним.
separator_base_z = -9 + separator_axial_lift;
separator_top_z = separator_base_z + 18.5;
main_bearing_bottom_z = separator_base_z + 11.5;
connector_flange_h = 4;
// После отражения зажима канавка Z2...10.2 находится между +1.8 и +10 от магнитного торца.
clamp_groove_near_z = magnet_glue_face_z + 1.8;
clamp_groove_far_z = magnet_glue_face_z + 10;
connector_contact_z = (clamp_groove_near_z + clamp_groove_far_z)/2;
reducer_connector_stem_h = connector_contact_z-connector_flange_h-separator_top_z;

assert(view == "exploded" || view == "assembly" || view == "section" ||
       view == "cap" || view == "lid" || view == "print", "Неизвестный режим отображения.");
assert(magnet_bottom_z - lid_top_z >= 0.3, "Недостаточен зазор до вращающихся магнитов.");
assert(rear_pocket_inner_r >= 27 && rear_pocket_outer_r <= 33.7,
    "Нужно сохранить стенки у подшипника и снаружи корпуса.");
assert(roof_extra_h >= 0 && main_pocket_ceiling_z > lid_base_z,
    "Основной карман крышки должен быть открыт со стороны платы.");
assert(pcb_screw_ceiling_z <= lid_top_z-sensor_window_h,
    "Головка винта платы упирается в крышку.");
assert(reducer_connector_stem_h > 0 && load_connector_stem_h >= 4,
    "Проверьте длины шеек соединителей.");
assert(main_bearing_bottom_z+7 <= original_cap_h-1,
    "Подшипник поднят выше упора в крышке.");
assert(pcb_bottom_z-encoder_can_mcu_height()-mcu_axial_clearance >= original_cap_h-1+0.2,
    "Локальный карман MCU должен оставаться выше посадки подшипника.");
assert(clamp_groove_far_z-clamp_groove_near_z >= 2*connector_flange_h,
    "Два фланца не помещаются в канавке зажима.");
echo("Магнитный торец от исходной крышки, мм:", required_face_offset);
echo("Увеличение относительно измеренного зазора, мм:", axial_increase);
echo("Магнит — корпус датчика, мм:", magnet_bottom_z - sensor_front_z);
echo("Магнит — Hall-точка по модели корпуса TI, мм:", magnet_bottom_z - hall_z);
echo("Длина шейки соединителя редуктора, мм:", reducer_connector_stem_h);

module annulus(outer_r, inner_r, h) {
    difference() {
        cylinder(r = outer_r, h = h);
        translate([0,0,-eps]) cylinder(r = inner_r, h = h+2*eps);
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

// Локальная версия cap_with_bracing(): исходный сгенерированный файл не изменяется.
module encoder_cap_with_bracing() {
    $fn = 60;
    source_gear_h = 15.5;
    total_h = source_gear_h + original_cap_h;
    source_side_short = 12.246;
    source_side_long = 29.564;
    difference() {
        union() {
            encoder_cap_base();
            difference() {
                translate([-35,0,0]) cube([70,35,original_cap_h]);
                rotate([-90,90,0]) translate([2.2,-29,17.5])
                    encoder_bracing_cut(35,total_h,total_h/2,total_h,total_h/2);
                rotate([90,90,0]) translate([2.2,-29,-17.5])
                    encoder_bracing_cut(35,total_h,total_h/2,total_h,total_h/2);
                // Перекрытие с кольцом исключает касание двух объёмов по одной грани.
                translate([0,0,-eps]) cylinder(r = 35-eps, h = source_gear_h+eps);
            }
        }
        translate([0,35,-2.2]) rotate([90,22.5,0])
            for (i = [1,4]) rotate([0,0,45*i]) translate([16,0,-eps])
                cylinder(r = 1.6, h = 8+eps);
        translate([source_side_long/2-3,29,-eps])
            cube([6,3,source_side_short/2+1+eps]);
        translate([-source_side_long/2-3,29,-eps])
            cube([6,3,source_side_short/2+1+eps]);
    }
}

module rear_pocket_profile() {
    difference() {
        intersection() {
            encoder_pcb_outline(clearance = pcb_clearance);
            difference() {
                circle(r = rear_pocket_outer_r);
                circle(r = rear_pocket_inner_r);
            }
        }
        // Стойки под два винта M2 крепления платы остаются сплошными.
        encoder_pcb_mount_positions() circle(d = 4.4);
    }
}

module cap_encoder_carrier() {
    difference() {
        union() {
            if (with_bracing) encoder_cap_with_bracing(); else encoder_cap_base();
            // Надстройка опирается на исходный торец; упор подшипника не утончается.
            translate([0,0,original_cap_h-eps])
                annulus(35, 24, lid_base_z-original_cap_h+eps);
        }
        // Плата над исходным торцом, внутренняя часть нависает над подшипником.
        translate([0,0,pcb_bottom_z])
            linear_extrude(height = lid_base_z-pcb_bottom_z+eps)
                encoder_pcb_outline(clearance = pcb_clearance);
        // Обратная сторона: только наружная зона, вне посадки подшипника Ø52.
        translate([0,0,pcb_bottom_z-rear_pocket_depth])
            linear_extrude(height = rear_pocket_depth+eps) rear_pocket_profile();
        // Только верх стенки: дно Z10.25, посадка подшипника и упор Z10 сохранены.
        encoder_can_mcu_clearance(pcb_bottom_z, mcu_xy_clearance, mcu_axial_clearance, eps);
        encoder_pcb_mount_positions()
            translate([0,0,pcb_bottom_z-2]) cylinder(d = pcb_screw_pilot_d, h = 2+eps);
        // Штатные шесть отверстий M3 продолжаются через надстройку.
        encoder_body_bolt_positions()
            translate([0,0,original_cap_h-eps]) cylinder(d = 3.2, h = 5);
        // Четыре тонких провода выходят вбок, без высокой штыревой гребёнки.
        rotate([0,0,68]) translate([32,-2,pcb_bottom_z-1.2]) cube([9,4,1.1]);
    }
}

module sensor_lid() {
    difference() {
        translate([0,0,lid_base_z])
            annulus(35, shaft_clearance_r, lid_top_z-lid_base_z);
        translate([0,0,lid_base_z-eps])
            linear_extrude(height = main_pocket_ceiling_z-lid_base_z+eps)
                encoder_pcb_outline(clearance = pcb_clearance);
        // Карманы открыты изнутри. Снаружи единый ровный торец, над датчиками 0.4 мм пластика.
        encoder_sensor_positions()
            translate([0,0,lid_base_z-eps])
                linear_extrude(height = pocket_ceiling_z-lid_base_z+eps)
                    encoder_sensor_body_outline(clearance = pcb_clearance);
        // Головкам M2 оставлен свой зазор; основная крыша между карманами толще.
        encoder_pcb_mount_positions()
            translate([0,0,lid_base_z-eps])
                cylinder(d = pcb_screw_head_d+2*pcb_clearance,
                    h = pcb_screw_ceiling_z-lid_base_z+eps);
        // M3 с потайной головкой: потребуются более длинные винты сборки.
        encoder_body_bolt_positions() {
            translate([0,0,lid_base_z-eps]) cylinder(d = 3.2, h = lid_top_z-lid_base_z+2*eps);
            translate([0,0,lid_top_z-1.4]) cylinder(d1 = 3.2, d2 = 6+2*eps, h = 1.4+eps);
        }
    }
}

module pcb_in_cap() {
    // Исходный макет платы направляет датчики вниз; здесь они смотрят к магнитам вверх.
    translate([0,0,pcb_top_z]) mirror([0,0,1])
        encoder_can_pcb(show_parts = true, show_points = true);
    color("Silver") encoder_pcb_mount_positions()
        translate([0,0,pcb_top_z]) cylinder(d = pcb_screw_head_d, h = pcb_screw_head_h);
}

module clamp_facing_cap(glue_face_z = magnet_glue_face_z) {
    translate([0,0,glue_face_z+clamp_h]) mirror([0,0,1]) {
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
    translate([0,0,main_bearing_bottom_z]) annulus(26,20,7);
}

module separator_in_cap() {
    translate([0,0,separator_base_z]) separator();
}

module output_connector_in_cap() {
    // Торец шейки опирается на сепаратор, фланец расположен внутри канавки зажима.
    translate([0,0,connector_contact_z]) mirror([0,0,1])
        reducer_connector(h1 = reducer_connector_stem_h, skirt = false);
}

module load_connector_in_clamp() {
    // Соединитель другой детали смотрит от редуктора; юбка начинается выше зажима.
    translate([0,0,connector_contact_z])
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

if (view == "cap") {
    cap_encoder_carrier();
} else if (view == "lid") {
    translate([0,0,-lid_base_z]) sensor_lid();
} else if (view == "print") {
    translate([-39,0,0]) cap_encoder_carrier();
    translate([39,0,-lid_base_z]) sensor_lid();
} else {
    pcb_lift = view == "exploded" ? 5 : 0;
    lid_lift = view == "exploded" ? 12 : 0;
    bearing_lift = view == "exploded" ? -10 : 0;
    separator_lift = view == "exploded" ? -25 : 0;
    output_lift = view == "exploded" ? 20 : 0;
    load_lift = view == "exploded" ? 32 : 0;
    color("LightGray") visible_cut() cap_encoder_carrier();
    color("Gainsboro") translate([0,0,lid_lift]) visible_cut() sensor_lid();
    // В сборочных режимах показаны все включённые детали, включая полный рендер F6.
    // Для отдельных печатных деталей использовать cap, lid или print.
    if (show_electronics)
        translate([0,0,pcb_lift]) visible_cut() pcb_in_cap();
    if (show_bearing)
        color("Silver") translate([0,0,bearing_lift]) visible_cut() main_bearing_in_cap();
    if (show_separator)
        color("DarkSalmon") translate([0,0,separator_lift]) visible_cut() separator_in_cap();
    if (show_connectors) {
        color("LightSteelBlue") translate([0,0,output_lift]) visible_cut() output_connector_in_cap();
        color("SteelBlue") translate([0,0,load_lift]) visible_cut() load_connector_in_clamp();
    }
    if (show_clamp)
        translate([0,0,output_lift]) visible_cut() clamp_facing_cap();
    if ($preview && show_existing_position)
        %color("DarkOrange", 0.45)
            visible_cut() clamp_facing_cap(original_cap_h+existing_face_offset);
}
