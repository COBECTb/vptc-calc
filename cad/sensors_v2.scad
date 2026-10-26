// Hall package and reference frames; no V1 placement dependency.
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
module encoder_body_bolt_positions() {
    for (a = body_bolt_angles)
        translate([body_bolt_r*cos(a), body_bolt_r*sin(a), 0]) children();
}

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

