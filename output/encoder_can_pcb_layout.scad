// Макет компоновки собственной платы абсолютного энкодера; это не разводка PCB.
// Две дорожки: 24 / 26 магнитов (12 / 13 пар полюсов).
// Датчики на стороне магнитов; MCU, CAN-трансивер и питание на обратной стороне.
// Контуры корпусов служат для проверки места, выводы и пассивные элементы условны.
// Источники: https://www.ti.com/lit/ds/symlink/tmag5273.pdf
// https://www.st.com/resource/en/datasheet/stm32g431kb.pdf
// https://www.ti.com/lit/ds/symlink/tcan332g.pdf
use <../electronics/encoder_can/design/placed_components.scad>

/* [Отображение] */
show_components = true;
show_hall_points = true;

/* [Плата] */
pcb_inner_r = 21.6;
pcb_sensor_inner_r = 21.3; // Локальное расширение под рекомендованные площадки TI.
pcb_sensor_relief_half_span = 10;
pcb_sensor_relief_transition = 2;
pcb_outer_r = 33.4;
pcb_span = 160;
pcb_center_angle = 9;
pcb_h = 0.8;
pcb_mount_r = 30.5;
pcb_mount_angles = [-59, 77];
pcb_mount_d = 2.2;
body_bolt_r = 31.5;
body_bolt_angles = [39,99,159,219,279,339];
body_bolt_keepout = 4.5;

/* [Датчики] */
inner_track_r = 23.5;
outer_track_r = 29.5;
sensor_body_h = 1.45; // Механический резерв: DBV0006A-C02 Amax=1.40 + 0.05 мм.
sensor_package_h_min = 0.9; // Пределы A от плоскости посадки, чертёж TI DBV0006A-C02.
sensor_package_h_max = 1.4;
hall_depth_from_top = 0.73; // Рис. 6-2: глубина Hall-точки от ВЕРХА корпуса.
hall_seating_height = sensor_package_h_max - hall_depth_from_top;
// Смещение Hall-точки от центра корпуса, вид сверху из документации TI.
hall_xy_offset = [-0.12, -0.4];

/* [Hidden] */
$fn = 96;
eps = 0.01; // Сквозные вычитатели выступают с обеих сторон платы.

function encoder_pcb_thickness() = pcb_h;
function encoder_sensor_height() = sensor_body_h;
// Маркер показывает верхнее положение Hall при Amax; фактическая высота зависит от A.
function encoder_hall_height() = hall_seating_height;
function encoder_hall_height_min() = sensor_package_h_min - hall_depth_from_top;
// Профиль совпадает с electronics/encoder_can/design/mechanics.json.
function encoder_pcb_inner_radius(a) =
    let(d = abs(a-pcb_center_angle))
    d <= pcb_sensor_relief_half_span ? pcb_sensor_inner_r :
    d >= pcb_sensor_relief_half_span+pcb_sensor_relief_transition ? pcb_inner_r :
    pcb_sensor_inner_r + (pcb_inner_r-pcb_sensor_inner_r)*
        (d-pcb_sensor_relief_half_span)/pcb_sensor_relief_transition;

module encoder_body_bolt_positions() {
    for (a = body_bolt_angles)
        translate([body_bolt_r*cos(a), body_bolt_r*sin(a), 0]) children();
}

assert(pcb_inner_r < inner_track_r && outer_track_r < pcb_outer_r,
    "Датчики должны находиться внутри контура платы.");

module encoder_pcb_outline(clearance = 0) {
    offset(delta = clearance) difference() {
        polygon(points = concat(
            [for (i = [0:120])
                let(a = pcb_center_angle - pcb_span/2 + pcb_span*i/120)
                [pcb_outer_r*cos(a), pcb_outer_r*sin(a)]],
            [for (i = [640:-1:0])
                let(a = pcb_center_angle - pcb_span/2 + pcb_span*i/640,
                    r = encoder_pcb_inner_radius(a))
                [r*cos(a), r*sin(a)]]
        ));
        // Выемки сохраняют доступ к штатным винтам корпуса и место под их стойки.
        for (a = body_bolt_angles)
            translate([body_bolt_r*cos(a), body_bolt_r*sin(a)])
                circle(r = body_bolt_keepout);
    }
}

module encoder_pcb_mount_positions() {
    for (a = pcb_mount_angles)
        translate([pcb_mount_r*cos(a), pcb_mount_r*sin(a), 0]) children();
}

module encoder_pcb_bare() {
    difference() {
        linear_extrude(height = pcb_h) encoder_pcb_outline();
        encoder_pcb_mount_positions()
            translate([0,0,-eps]) cylinder(d = pcb_mount_d, h = pcb_h+2*eps);
    }
}

// Локальная X направлена по радиусу, Y по касательной; Hall-точки точно над дорожками.
module encoder_sensor_positions() {
    for (r = [inner_track_r, outer_track_r])
        rotate([0,0,pcb_center_angle]) translate([r,0,0]) children();
}

// Контур корпуса относительно Hall-точки; используется также для внутренних карманов крышки.
module encoder_sensor_body_outline(clearance = 0) {
    translate([-hall_xy_offset[0], -hall_xy_offset[1]])
        offset(delta = clearance) square([2.8, 2.9], center = true);
}

module tmag5273_envelope() {
    translate([0,0,-sensor_body_h]) linear_extrude(height = sensor_body_h)
        encoder_sensor_body_outline();
}

module rear_component(r, a, size) {
    rotate([0,0,a]) translate([r,0,pcb_h+size[2]/2]) cube(size, center = true);
}

module encoder_can_pcb(show_parts = true, show_points = false) {
    color("SeaGreen") encoder_pcb_bare();
    if (show_parts) {
        color("DimGray") encoder_sensor_positions() tmag5273_envelope();
        // Положения MCU/CAN/LDO, кварца, пассивов и площадок из KiCad placements.json.
        encoder_can_placed_components(pcb_h);
    }
    if (show_points)
        color("OrangeRed") encoder_sensor_positions()
            translate([0,0,-hall_seating_height]) sphere(d = 0.35);
}

encoder_can_pcb(show_parts = show_components, show_points = show_hall_points);
