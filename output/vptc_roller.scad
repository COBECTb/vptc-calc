// ВПТК редуктор с роликами (для 3D-печати)
use <foots.scad>
$fn = 60;
eps = 0.01; // Выход вычитателей за открытые поверхности; глухие глубины сохранены.
// Параметры
d_roller = 4.000;
h_roller = 5.000;
separator_h = 9.000;
eccentric_h = 7.000;
Rsep_m = 25.200;
Rsep_out = 26.080;
Rsep_in = 24.320;
D_out = 70.000;
h_reducer = 15.500;
bearing_inner = 40.0;
bearing_outer = 52.0;
bearing_width = 7.0;
// Высота профильного выреза
h_cut = h_roller + 5;
cap_thickness = 11.0;
eccentricity = 0.800;
// --- Параметры вала эксцентрика ---
ecc_shaft_h1 = 5.000;   // основание под 6803ZZ
ecc_spacer_h = 2.500;   // проставка
ecc_shaft_h2 = 6.000;   // эксцентриковая ступень
ecc_pin_h = 6.000;      // шип под 688ZZ
// --- Параметры кожуха мотора ---
mc_motor_plate_d = 50.0;
mc_base_thickness = 4.0;
mc_encoder_hole_d = 10.0;
mc_motor_hole_1 = 16.0;
mc_motor_hole_2 = 19.0;
mc_adapter_angle = 45.0;
mc_adapter_angles = [for (i = [0:3]) mc_adapter_angle + 90*i];
mc_nut_pad_radius = 24.0;
mc_nut_pad_d = 6.0;
mc_nut_pad_h = 3.0;
mc_total_height = 27.5;
mc_ring_width = 4.0;
mc_ring_height = 5.0;
mc_countersink_d = 6.0;
mc_countersink_h = 2.0;
// --- Параметры бокового крепления ---
bracing_offset_y = 29.0;  // смещение по Y
bracing_offset_z = 17.5;  // смещение по Z
bracing_offset_x = 2.2;  // смещение по X

// === Группа B: отверстия под кожух мотора нужны в двух функциях===
motor_angles = [174.0, 264.0, 354.0, 84.0];
motor_radius = 32.000;

// Расстояния между отверстиями в боковом креплении
side_short = 12.246;
side_long = 29.564;

// === Вспомогательные модули для бокового крепления ===
module oval_cone(height, bottom_width, bottom_depth, top_width, top_depth, center = false) {
    hull() {
        // Нижнее основание
        translate([0, 0, center ? -height/2 : 0])
        scale([bottom_width/2, bottom_depth/2, 1])
        cylinder(h = 0.1, r = 1, center = true, $fn = 64);
        
        // Верхнее основание
        translate([0, 0, center ? height/2 : height])
        scale([top_width/2, top_depth/2, 1])
        cylinder(h = 0.1, r = 1, center = true, $fn = 64);
    }
}

module oval_cone_diff_half(height, bottom_width, bottom_depth, top_width, top_depth, center = false) {
    difference() { 
        cube([height, height, height], center = center);
        // Вычитаем овальный конус
        oval_cone(height, bottom_width, bottom_depth, top_width, top_depth, center = center);
        if (center)
            translate([-height/2-eps,0,-height/2-eps])
                cube([height+2*eps,height/2+eps,height+2*eps]);
        else
            translate([-eps,height/4,-eps]) cube([height+2*eps,height/2,height+2*eps]);
    }
}

// === Корпус (жёсткое колесо) ===
module rigid_gear() {
    difference() {
        cylinder(h = h_reducer, r = D_out / 2, center = false);
        translate([0, 0, h_reducer - h_cut])
            linear_extrude(height = h_cut+eps, center = false)
                polygon(points = [
                [0.00000, 28.00000], [0.55458, 27.96049], [1.08358, 27.84861], [1.56964, 27.68091], [2.00602, 27.47706],
        [2.39362, 27.25494], [2.73674, 27.02909], [3.03997, 26.81126], [3.30657, 26.61130], [3.53787, 26.43755],
        [3.73313, 26.29670], [3.88995, 26.19284], [4.00545, 26.12612], [4.07887, 26.09136], [4.11549, 26.07829],
        [4.12987, 26.07497], [4.14457, 26.07368], [4.18344, 26.07480], [4.26401, 26.08517], [4.39447, 26.11293],
        [4.57571, 26.16324], [4.80494, 26.23687], [5.07860, 26.33064], [5.39395, 26.43843], [5.74965, 26.55189],
        [6.14577, 26.66065], [6.58304, 26.75213], [7.06105, 26.81115], [7.57515, 26.82045], [8.11283, 26.76338],
        [8.65248, 26.62958], [9.16770, 26.42064], [9.63624, 26.15076], [10.04669, 25.84106], [10.39872, 25.51235],
        [10.69871, 25.18132], [10.95525, 24.86049], [11.17632, 24.55962], [11.36808, 24.28706], [11.53437, 24.05034],
        [11.67654, 23.85604], [11.79359, 23.70881], [11.88282, 23.60967], [11.94190, 23.55392], [11.97270, 23.53017],
        [11.98535, 23.52257], [11.99893, 23.51680], [12.03624, 23.50585], [12.11608, 23.49082], [12.24873, 23.47691],
        [12.43665, 23.46875], [12.67741, 23.46794], [12.96665, 23.47255], [13.29987, 23.47762], [13.67322, 23.47561],
        [14.08357, 23.45664], [14.52771, 23.40852], [15.00056, 23.31694], [15.49237, 23.16691], [15.98610, 22.94649],
        [16.45799, 22.65248], [16.88343, 22.29454], [17.24564, 21.89309], [17.54030, 21.47171], [17.77352, 21.05030],
        [17.95653, 20.64277], [18.10137, 20.25837], [18.21865, 19.90391], [18.31680, 19.58544], [18.40180, 19.30892],
        [18.47697, 19.08020], [18.54280, 18.90400], [18.59702, 18.78213], [18.63599, 18.71086], [18.65794, 18.67875],
        [18.66762, 18.66762], [18.67875, 18.65794], [18.71086, 18.63599], [18.78213, 18.59702], [18.90400, 18.54280],
        [19.08020, 18.47697], [19.30892, 18.40180], [19.58544, 18.31680], [19.90391, 18.21865], [20.25837, 18.10137],
        [20.64277, 17.95653], [21.05030, 17.77352], [21.47171, 17.54030], [21.89309, 17.24564], [22.29454, 16.88343],
        [22.65248, 16.45799], [22.94649, 15.98610], [23.16691, 15.49237], [23.31694, 15.00056], [23.40852, 14.52771],
        [23.45664, 14.08357], [23.47561, 13.67322], [23.47762, 13.29987], [23.47255, 12.96665], [23.46794, 12.67741],
        [23.46875, 12.43665], [23.47691, 12.24873], [23.49082, 12.11608], [23.50585, 12.03624], [23.51680, 11.99893],
        [23.52257, 11.98535], [23.53017, 11.97270], [23.55392, 11.94190], [23.60967, 11.88282], [23.70881, 11.79359],
        [23.85604, 11.67654], [24.05034, 11.53437], [24.28706, 11.36808], [24.55962, 11.17632], [24.86049, 10.95525],
        [25.18132, 10.69871], [25.51235, 10.39872], [25.84106, 10.04669], [26.15076, 9.63624], [26.42064, 9.16770],
        [26.62958, 8.65248], [26.76338, 8.11283], [26.82045, 7.57515], [26.81115, 7.06105], [26.75213, 6.58304],
        [26.66065, 6.14577], [26.55189, 5.74965], [26.43843, 5.39395], [26.33064, 5.07860], [26.23687, 4.80494],
        [26.16324, 4.57571], [26.11293, 4.39447], [26.08517, 4.26401], [26.07480, 4.18344], [26.07368, 4.14457],
        [26.07497, 4.12987], [26.07829, 4.11549], [26.09136, 4.07887], [26.12612, 4.00545], [26.19284, 3.88995],
        [26.29670, 3.73313], [26.43755, 3.53787], [26.61130, 3.30657], [26.81126, 3.03997], [27.02909, 2.73674],
        [27.25494, 2.39362], [27.47706, 2.00602], [27.68091, 1.56964], [27.84861, 1.08358], [27.96049, 0.55458],
        [28.00000, 0.00000], [27.96049, -0.55458], [27.84861, -1.08358], [27.68091, -1.56964], [27.47706, -2.00602],
        [27.25494, -2.39362], [27.02909, -2.73674], [26.81126, -3.03997], [26.61130, -3.30657], [26.43755, -3.53787],
        [26.29670, -3.73313], [26.19284, -3.88995], [26.12612, -4.00545], [26.09136, -4.07887], [26.07829, -4.11549],
        [26.07497, -4.12987], [26.07368, -4.14457], [26.07480, -4.18344], [26.08517, -4.26401], [26.11293, -4.39447],
        [26.16324, -4.57571], [26.23687, -4.80494], [26.33064, -5.07860], [26.43843, -5.39395], [26.55189, -5.74965],
        [26.66065, -6.14577], [26.75213, -6.58304], [26.81115, -7.06105], [26.82045, -7.57515], [26.76338, -8.11283],
        [26.62958, -8.65248], [26.42064, -9.16770], [26.15076, -9.63624], [25.84106, -10.04669], [25.51235, -10.39872],
        [25.18132, -10.69871], [24.86049, -10.95525], [24.55962, -11.17632], [24.28706, -11.36808], [24.05034, -11.53437],
        [23.85604, -11.67654], [23.70881, -11.79359], [23.60967, -11.88282], [23.55392, -11.94190], [23.53017, -11.97270],
        [23.52257, -11.98535], [23.51680, -11.99893], [23.50585, -12.03624], [23.49082, -12.11608], [23.47691, -12.24873],
        [23.46875, -12.43665], [23.46794, -12.67741], [23.47255, -12.96665], [23.47762, -13.29987], [23.47561, -13.67322],
        [23.45664, -14.08357], [23.40852, -14.52771], [23.31694, -15.00056], [23.16691, -15.49237], [22.94649, -15.98610],
        [22.65248, -16.45799], [22.29454, -16.88343], [21.89309, -17.24564], [21.47171, -17.54030], [21.05030, -17.77352],
        [20.64277, -17.95653], [20.25837, -18.10137], [19.90391, -18.21865], [19.58544, -18.31680], [19.30892, -18.40180],
        [19.08020, -18.47697], [18.90400, -18.54280], [18.78213, -18.59702], [18.71086, -18.63599], [18.67875, -18.65794],
        [18.66762, -18.66762], [18.65794, -18.67875], [18.63599, -18.71086], [18.59702, -18.78213], [18.54280, -18.90400],
        [18.47697, -19.08020], [18.40180, -19.30892], [18.31680, -19.58544], [18.21865, -19.90391], [18.10137, -20.25837],
        [17.95653, -20.64277], [17.77352, -21.05030], [17.54030, -21.47171], [17.24564, -21.89309], [16.88343, -22.29454],
        [16.45799, -22.65248], [15.98610, -22.94649], [15.49237, -23.16691], [15.00056, -23.31694], [14.52771, -23.40852],
        [14.08357, -23.45664], [13.67322, -23.47561], [13.29987, -23.47762], [12.96665, -23.47255], [12.67741, -23.46794],
        [12.43665, -23.46875], [12.24873, -23.47691], [12.11608, -23.49082], [12.03624, -23.50585], [11.99893, -23.51680],
        [11.98535, -23.52257], [11.97270, -23.53017], [11.94190, -23.55392], [11.88282, -23.60967], [11.79359, -23.70881],
        [11.67654, -23.85604], [11.53437, -24.05034], [11.36808, -24.28706], [11.17632, -24.55962], [10.95525, -24.86049],
        [10.69871, -25.18132], [10.39872, -25.51235], [10.04669, -25.84106], [9.63624, -26.15076], [9.16770, -26.42064],
        [8.65248, -26.62958], [8.11283, -26.76338], [7.57515, -26.82045], [7.06105, -26.81115], [6.58304, -26.75213],
        [6.14577, -26.66065], [5.74965, -26.55189], [5.39395, -26.43843], [5.07860, -26.33064], [4.80494, -26.23687],
        [4.57571, -26.16324], [4.39447, -26.11293], [4.26401, -26.08517], [4.18344, -26.07480], [4.14457, -26.07368],
        [4.12987, -26.07497], [4.11549, -26.07829], [4.07887, -26.09136], [4.00545, -26.12612], [3.88995, -26.19284],
        [3.73313, -26.29670], [3.53787, -26.43755], [3.30657, -26.61130], [3.03997, -26.81126], [2.73674, -27.02909],
        [2.39362, -27.25494], [2.00602, -27.47706], [1.56964, -27.68091], [1.08358, -27.84861], [0.55458, -27.96049],
        [0.00000, -28.00000], [-0.55458, -27.96049], [-1.08358, -27.84861], [-1.56964, -27.68091], [-2.00602, -27.47706],
        [-2.39362, -27.25494], [-2.73674, -27.02909], [-3.03997, -26.81126], [-3.30657, -26.61130], [-3.53787, -26.43755],
        [-3.73313, -26.29670], [-3.88995, -26.19284], [-4.00545, -26.12612], [-4.07887, -26.09136], [-4.11549, -26.07829],
        [-4.12987, -26.07497], [-4.14457, -26.07368], [-4.18344, -26.07480], [-4.26401, -26.08517], [-4.39447, -26.11293],
        [-4.57571, -26.16324], [-4.80494, -26.23687], [-5.07860, -26.33064], [-5.39395, -26.43843], [-5.74965, -26.55189],
        [-6.14577, -26.66065], [-6.58304, -26.75213], [-7.06105, -26.81115], [-7.57515, -26.82045], [-8.11283, -26.76338],
        [-8.65248, -26.62958], [-9.16770, -26.42064], [-9.63624, -26.15076], [-10.04669, -25.84106], [-10.39872, -25.51235],
        [-10.69871, -25.18132], [-10.95525, -24.86049], [-11.17632, -24.55962], [-11.36808, -24.28706], [-11.53437, -24.05034],
        [-11.67654, -23.85604], [-11.79359, -23.70881], [-11.88282, -23.60967], [-11.94190, -23.55392], [-11.97270, -23.53017],
        [-11.98535, -23.52257], [-11.99893, -23.51680], [-12.03624, -23.50585], [-12.11608, -23.49082], [-12.24873, -23.47691],
        [-12.43665, -23.46875], [-12.67741, -23.46794], [-12.96665, -23.47255], [-13.29987, -23.47762], [-13.67322, -23.47561],
        [-14.08357, -23.45664], [-14.52771, -23.40852], [-15.00056, -23.31694], [-15.49237, -23.16691], [-15.98610, -22.94649],
        [-16.45799, -22.65248], [-16.88343, -22.29454], [-17.24564, -21.89309], [-17.54030, -21.47171], [-17.77352, -21.05030],
        [-17.95653, -20.64277], [-18.10137, -20.25837], [-18.21865, -19.90391], [-18.31680, -19.58544], [-18.40180, -19.30892],
        [-18.47697, -19.08020], [-18.54280, -18.90400], [-18.59702, -18.78213], [-18.63599, -18.71086], [-18.65794, -18.67875],
        [-18.66762, -18.66762], [-18.67875, -18.65794], [-18.71086, -18.63599], [-18.78213, -18.59702], [-18.90400, -18.54280],
        [-19.08020, -18.47697], [-19.30892, -18.40180], [-19.58544, -18.31680], [-19.90391, -18.21865], [-20.25837, -18.10137],
        [-20.64277, -17.95653], [-21.05030, -17.77352], [-21.47171, -17.54030], [-21.89309, -17.24564], [-22.29454, -16.88343],
        [-22.65248, -16.45799], [-22.94649, -15.98610], [-23.16691, -15.49237], [-23.31694, -15.00056], [-23.40852, -14.52771],
        [-23.45664, -14.08357], [-23.47561, -13.67322], [-23.47762, -13.29987], [-23.47255, -12.96665], [-23.46794, -12.67741],
        [-23.46875, -12.43665], [-23.47691, -12.24873], [-23.49082, -12.11608], [-23.50585, -12.03624], [-23.51680, -11.99893],
        [-23.52257, -11.98535], [-23.53017, -11.97270], [-23.55392, -11.94190], [-23.60967, -11.88282], [-23.70881, -11.79359],
        [-23.85604, -11.67654], [-24.05034, -11.53437], [-24.28706, -11.36808], [-24.55962, -11.17632], [-24.86049, -10.95525],
        [-25.18132, -10.69871], [-25.51235, -10.39872], [-25.84106, -10.04669], [-26.15076, -9.63624], [-26.42064, -9.16770],
        [-26.62958, -8.65248], [-26.76338, -8.11283], [-26.82045, -7.57515], [-26.81115, -7.06105], [-26.75213, -6.58304],
        [-26.66065, -6.14577], [-26.55189, -5.74965], [-26.43843, -5.39395], [-26.33064, -5.07860], [-26.23687, -4.80494],
        [-26.16324, -4.57571], [-26.11293, -4.39447], [-26.08517, -4.26401], [-26.07480, -4.18344], [-26.07368, -4.14457],
        [-26.07497, -4.12987], [-26.07829, -4.11549], [-26.09136, -4.07887], [-26.12612, -4.00545], [-26.19284, -3.88995],
        [-26.29670, -3.73313], [-26.43755, -3.53787], [-26.61130, -3.30657], [-26.81126, -3.03997], [-27.02909, -2.73674],
        [-27.25494, -2.39362], [-27.47706, -2.00602], [-27.68091, -1.56964], [-27.84861, -1.08358], [-27.96049, -0.55458],
        [-28.00000, -0.00000], [-27.96049, 0.55458], [-27.84861, 1.08358], [-27.68091, 1.56964], [-27.47706, 2.00602],
        [-27.25494, 2.39362], [-27.02909, 2.73674], [-26.81126, 3.03997], [-26.61130, 3.30657], [-26.43755, 3.53787],
        [-26.29670, 3.73313], [-26.19284, 3.88995], [-26.12612, 4.00545], [-26.09136, 4.07887], [-26.07829, 4.11549],
        [-26.07497, 4.12987], [-26.07368, 4.14457], [-26.07480, 4.18344], [-26.08517, 4.26401], [-26.11293, 4.39447],
        [-26.16324, 4.57571], [-26.23687, 4.80494], [-26.33064, 5.07860], [-26.43843, 5.39395], [-26.55189, 5.74965],
        [-26.66065, 6.14577], [-26.75213, 6.58304], [-26.81115, 7.06105], [-26.82045, 7.57515], [-26.76338, 8.11283],
        [-26.62958, 8.65248], [-26.42064, 9.16770], [-26.15076, 9.63624], [-25.84106, 10.04669], [-25.51235, 10.39872],
        [-25.18132, 10.69871], [-24.86049, 10.95525], [-24.55962, 11.17632], [-24.28706, 11.36808], [-24.05034, 11.53437],
        [-23.85604, 11.67654], [-23.70881, 11.79359], [-23.60967, 11.88282], [-23.55392, 11.94190], [-23.53017, 11.97270],
        [-23.52257, 11.98535], [-23.51680, 11.99893], [-23.50585, 12.03624], [-23.49082, 12.11608], [-23.47691, 12.24873],
        [-23.46875, 12.43665], [-23.46794, 12.67741], [-23.47255, 12.96665], [-23.47762, 13.29987], [-23.47561, 13.67322],
        [-23.45664, 14.08357], [-23.40852, 14.52771], [-23.31694, 15.00056], [-23.16691, 15.49237], [-22.94649, 15.98610],
        [-22.65248, 16.45799], [-22.29454, 16.88343], [-21.89309, 17.24564], [-21.47171, 17.54030], [-21.05030, 17.77352],
        [-20.64277, 17.95653], [-20.25837, 18.10137], [-19.90391, 18.21865], [-19.58544, 18.31680], [-19.30892, 18.40180],
        [-19.08020, 18.47697], [-18.90400, 18.54280], [-18.78213, 18.59702], [-18.71086, 18.63599], [-18.67875, 18.65794],
        [-18.66762, 18.66762], [-18.65794, 18.67875], [-18.63599, 18.71086], [-18.59702, 18.78213], [-18.54280, 18.90400],
        [-18.47697, 19.08020], [-18.40180, 19.30892], [-18.31680, 19.58544], [-18.21865, 19.90391], [-18.10137, 20.25837],
        [-17.95653, 20.64277], [-17.77352, 21.05030], [-17.54030, 21.47171], [-17.24564, 21.89309], [-16.88343, 22.29454],
        [-16.45799, 22.65248], [-15.98610, 22.94649], [-15.49237, 23.16691], [-15.00056, 23.31694], [-14.52771, 23.40852],
        [-14.08357, 23.45664], [-13.67322, 23.47561], [-13.29987, 23.47762], [-12.96665, 23.47255], [-12.67741, 23.46794],
        [-12.43665, 23.46875], [-12.24873, 23.47691], [-12.11608, 23.49082], [-12.03624, 23.50585], [-11.99893, 23.51680],
        [-11.98535, 23.52257], [-11.97270, 23.53017], [-11.94190, 23.55392], [-11.88282, 23.60967], [-11.79359, 23.70881],
        [-11.67654, 23.85604], [-11.53437, 24.05034], [-11.36808, 24.28706], [-11.17632, 24.55962], [-10.95525, 24.86049],
        [-10.69871, 25.18132], [-10.39872, 25.51235], [-10.04669, 25.84106], [-9.63624, 26.15076], [-9.16770, 26.42064],
        [-8.65248, 26.62958], [-8.11283, 26.76338], [-7.57515, 26.82045], [-7.06105, 26.81115], [-6.58304, 26.75213],
        [-6.14577, 26.66065], [-5.74965, 26.55189], [-5.39395, 26.43843], [-5.07860, 26.33064], [-4.80494, 26.23687],
        [-4.57571, 26.16324], [-4.39447, 26.11293], [-4.26401, 26.08517], [-4.18344, 26.07480], [-4.14457, 26.07368],
        [-4.12987, 26.07497], [-4.11549, 26.07829], [-4.07887, 26.09136], [-4.00545, 26.12612], [-3.88995, 26.19284],
        [-3.73313, 26.29670], [-3.53787, 26.43755], [-3.30657, 26.61130], [-3.03997, 26.81126], [-2.73674, 27.02909],
        [-2.39362, 27.25494], [-2.00602, 27.47706], [-1.56964, 27.68091], [-1.08358, 27.84861], [-0.55458, 27.96049]
            ]);
        // === Группа A: основные крепёжные отверстия ===
        for (i = [0 : 5]) {
            x_hole = [-29.40778, -24.48010, 4.92769, 29.40778, 24.48010, -4.92769][i];
            y_hole = [11.28859, -19.82359, -31.11218, -11.28859, 19.82359, 31.11218][i];
            translate([x_hole, y_hole, -eps])
                cylinder(h = h_reducer+2*eps, r = 1.6, center = false);
            translate([x_hole, y_hole, -eps])
                cylinder(h = 3.0+eps, r = 3.0, center = false);
        }
        // === Группа B: крепёжные отверстия кожуха===
        for (i = [0 : 3]) {
            angle = motor_angles[i];
            rotate([0, 0, angle])
                translate([motor_radius, 0, -eps])
                    cylinder(h = 8.0+eps, r = 1.6, center = false);
            rotate([0, 0, angle])
                translate([motor_radius, 0, 5.0])
                    cube(size = [6.0, 6.0, 3.0], center = true);
        }
        // === Посадка подшипника 6803ZZ в корпусе ===
        translate([0,0,-eps]) cylinder(h = 1+eps, r = 24/2, center = false);
        translate([0, 0, 1])
            cylinder(h = 5.0, r = 26.0/2, center = false);
    }
}

// === Корпус с боковым креплением ===
module rigid_gear_with_bracing() {
	difference(){
    	union() {
        	rigid_gear();
       
        	difference(){
            	translate([-D_out/2, 0, 0]) cube([D_out, D_out/2, h_reducer]);
            	rotate([-90, 90, 0]) 
                	translate([-cap_thickness-bracing_offset_x, -bracing_offset_y, bracing_offset_z]) 
                	oval_cone_diff_half(D_out/2, h_reducer+cap_thickness, (h_reducer+cap_thickness)/2, h_reducer+cap_thickness, (h_reducer+cap_thickness)/2, true);
            	rotate([90, 90, 0]) 
                	translate([-cap_thickness-bracing_offset_x, -bracing_offset_y, -bracing_offset_z]) 
                	oval_cone_diff_half(D_out/2, h_reducer+cap_thickness, (h_reducer+cap_thickness)/2, h_reducer+cap_thickness, (h_reducer+cap_thickness)/2, true); 
                translate([0,0,-eps]) cylinder(h = h_reducer+2*eps, r = D_out/2-eps);
        	}
    	}
        // === Группа B: крепёжные отверстия кожуха===
        // Повторно вырезаем, боковое крепление может загородить
        for (i = [0 : 3]) {
            angle = motor_angles[i];
            rotate([0, 0, angle])
                translate([motor_radius+4, 0, 5.0])
                    cube(size = [10.0, 6.0, 3.0], center = true);
        }
        // Посадочные места под крепеж нагрузки m3
        translate([0,D_out/2,(h_reducer+cap_thickness)/2]) rotate([90,45/2,0]) {
            for (i = [0, 5]) {
                angle=45*i;
                rotate([0, 0, angle]) {
                    translate([bearing_inner/2-4, 0, -eps])
                        cylinder(h = 8+eps, r = 1.6, center = false);
                }
            }
        }
        translate([side_long/2-3, D_out/2-6, side_short/2-2]) cube([6,3,side_short],center=false);
        translate([-side_long/2-3, D_out/2-6, side_short/2-2]) cube([6,3,side_short],center=false);
	}
}

// === Сепаратор с фланцем под подшипник ===
module separator() {
    difference() {
        cylinder(h = separator_h + 9.5, r = Rsep_out, center = false);
        // Фланец под основной подшипник (ступенчатая посадка)
        translate([0, 0, 11.0])
            difference() {
                cylinder(h = 9.5, r = Rsep_out+eps, center = false);
                translate([0,0,-eps]) cylinder(h = 9.5+2*eps, r = bearing_inner/2 + 2, center = false);  // +2 мм зазор
            }
        translate([0, 0, 11.5])
            difference() {
                cylinder(h = 9.5, r = Rsep_out+eps, center = false);
                translate([0,0,-eps]) cylinder(h = 9.5+2*eps, r = bearing_inner/2, center = false);      // точный диаметр
            }
        // Посадочное место под мини-подшипник 688ZZ (8x16x5)
        translate([0, 0, h_roller + 3])
            cylinder(h = 5, r = 8, center = false);
        translate([0, 0, h_roller + 3 + 0.5])
            cylinder(h = 5, r = 7, center = false);
        translate([0, 0, h_roller + 3 + 1])
            cylinder(h = 5, r = 5, center = false);
        translate([0,0,-eps]) cylinder(h = separator_h-1+eps, r = Rsep_in, center = false);
        for (angle = [0 : 360/19 : 359]) {
            rotate([0, 0, angle])
                translate([Rsep_m, 0, separator_h/2])
                    rotate([0, 90, 0])
                        cube([h_roller + 0.4, d_roller + 0.4, separator_h + 1], center = true);
        }
        // Посадочные места под крепеж нагрузки m3
        for (i = [0 : 7]) {
            angle=45*i;
            rotate([0, 0, angle]) {
                translate([bearing_inner/2-4, 0, -eps])
                    cylinder(h = separator_h+9.5+2*eps, r = 1.6, center = false);
                translate([bearing_inner/2-4, 0, -eps])
                    cylinder(h =separator_h+2+eps, r = 3.0, center = false);
            }
        }
    }
}

// Соединитель редукторов
module reducer_connector(fitting=true,h1=4,skirt=false,holes=undef) {
    assert(h1>0 && (!skirt || h1>3), "Проверьте высоту соединителя и юбки");
    difference() {
        union() {
            cylinder(h = 4, r = D_out/2-9, center = false);
            translate([0,0,4]) cylinder(h = h1, r = bearing_inner/2, center = false);
            if(skirt) translate([0,0,7])
                cylinder(h=h1-3,r1=D_out/2-13,r2=D_out/2-7,center=false);
        }
        // Посадочные места под крепеж нагрузки m3
        for (i = [0 : 7]) {
            angle=45*i;
            rotate([0, 0, angle]) {
                translate([bearing_inner/2-4, 0, -eps])
                    cylinder(h = h1+4+2*eps, r = 1.6, center = false);
                if(is_undef(holes) ? fitting : holes[i]){
                    translate([bearing_inner/2-4, 0, -eps])
                        cylinder(h =3+eps, r = 3.0, center = false);
                }
            }
        }
    }
}

// Зажим соединителей 
module connector_clamp(){
    intersection() {
        difference() {
            cylinder(h = 12, r = D_out/2-2, center = false);
            translate([0, 0, 2]) cylinder(h = 8.2, r = D_out/2-8.8, center = false);
            translate([0,0,-eps]) cylinder(h = 12+2*eps, r = bearing_inner/2, center = false);
            rotate([0,90,90]) translate([-6, D_out/2-5, 3]) cylinder(h = 20, r =3, center = false);
            rotate([0,90,90]) translate([-6, D_out/2-5, -eps]) cylinder(h = 20+eps, r =1.6, center = false);
            rotate([0,-90,-90]) translate([6, D_out/2-5, 3]) cylinder(h = 20, r =3, center = false);
            rotate([0,-90,-90]) translate([6, D_out/2-5, -eps]) cylinder(h = 20+eps, r =1.6, center = false);
        }
        // Отсекаем нижнюю часть - оставляем только верх
        translate([-D_out, 0, -1])
            cube([D_out*2, D_out, 14]);
    }
}


// === Ролики ===
module rollers() {
    for (i = [0 : 18]) {
        angle = i * 360 / 19;
        rotate([0, 0, angle])
            translate([Rsep_m, 0, 0])
                cylinder(r = d_roller/2, h = h_roller, center = true);
    }
}

// === Эксцентрик ===
module eccentric() {
    difference() {
        cylinder(r = 23.200, h = eccentric_h, center = false);
        // Посадка под подшипник 6803ZZ
        translate([0,0,-eps]) cylinder(h = 1+eps, r = 24/2, center = false);
        translate([0, 0, 1])
            cylinder(h = eccentric_h, r = 26.0/2, center = false);
    }
}

// === Крышка редуктора ===
module cap() {
    difference() {
        cylinder(h = cap_thickness, r = D_out / 2, center = false);
        // Внутреннее отверстие под подшипник
        translate([0, 0, -eps])
            cylinder(h = cap_thickness-1+eps, r = 26.0, center = false);
        // Внутреннее отверстие под упор подшипника
        translate([0,0,-eps]) cylinder(h = cap_thickness+2*eps, r = 26.0 -2, center = false);
        // Внутреннее отверстие под сепаратор
        translate([0,0,-eps]) cylinder(h = 3+eps, r = Rsep_out+1, center = false);
        // Отверстия под винты (группа A)
        for (i = [0 : 5]) {
            x_hole = [-29.40778, -24.48010, 4.92769, 29.40778, 24.48010, -4.92769][i];
            y_hole = [11.28859, -19.82359, -31.11218, -11.28859, 19.82359, 31.11218][i];
            // Сквозное отверстие
            translate([x_hole, y_hole, -eps])
                cylinder(h = cap_thickness+2*eps, r = 1.6, center = false);
            // Потай под шляпку M3
            translate([x_hole, y_hole, cap_thickness - 2.0])
                cylinder(h = 2.0+eps, r = 3.0, center = false);
        }
    }
}

// === Крышка с боковым креплением ===
module cap_with_bracing() {
    difference(){
        union() {
            cap();
            difference(){
                translate([-D_out/2, 0, 0]) cube([D_out, D_out/2, cap_thickness]);
                rotate([-90, 90, 0]) 
                    translate([+bracing_offset_x, -bracing_offset_y, bracing_offset_z]) 
                    oval_cone_diff_half(D_out/2, h_reducer+cap_thickness, (h_reducer+cap_thickness)/2, h_reducer+cap_thickness, (h_reducer+cap_thickness)/2, true);
                rotate([90, 90, 0]) 
                    translate([+bracing_offset_x, -bracing_offset_y, -bracing_offset_z]) 
                    oval_cone_diff_half(D_out/2, h_reducer+cap_thickness, (h_reducer+cap_thickness)/2, h_reducer+cap_thickness, (h_reducer+cap_thickness)/2, true);
                translate([0,0,-eps]) cylinder(h = h_reducer+2*eps, r = D_out/2-eps, center = false);
            }
        }
        translate([0,D_out/2,-2.2]) rotate([90,45/2,0]) {
            for (i = [1, 4]) {
                angle=45*i;
                rotate([0, 0, angle]) {
                    translate([bearing_inner/2-4, 0, -eps])
                        cylinder(h = 8+eps, r = 1.6, center = false);
                }
            }
        }
        translate([side_long/2-3, D_out/2-6, -eps]) cube([6,3,side_short/2+1+eps],center=false);
        translate([-side_long/2-3, D_out/2-6, -eps]) cube([6,3,side_short/2+1+eps],center=false);
    }
}

// === Вал эксцентрика ===
module eccentric_shaft() {
    difference() {
        union() {
            // Основание (в подшипник корпуса)
            cylinder(h = ecc_shaft_h1, r = 17/2+0.07, center = false);
            // Проставка ecc_spacer_h мм
            translate([0, 0, ecc_shaft_h1])
                cylinder(h = ecc_spacer_h, r = 17/2+2, center = false);
            // Пподставка под подшипник в эксцентрике
            translate([eccentricity, 0, ecc_shaft_h1+ecc_spacer_h])
                cylinder(h = 0.5, r = 17/2+1, center = false);
            // Эксцентриковая ступень (в подшипник эксцентрика)
            translate([eccentricity, 0, ecc_shaft_h1 + ecc_spacer_h])
                cylinder(h = ecc_shaft_h2, r = 17/2, center = false);
            // Подставка под подшипник сепаратора)
            translate([0, 0, ecc_shaft_h1 + ecc_spacer_h + ecc_shaft_h2])
                cylinder(h = 0.5, r = 5, center = false);
            // Шип по общей оси (в подшипник сепаратора)
            translate([0, 0, ecc_shaft_h1 + ecc_spacer_h + ecc_shaft_h2])
                cylinder(h = ecc_pin_h, r = 8/2, center = false);
        }
        translate([0,0,-eps]) cylinder(h = 2.0+eps, r = 2.0, center = false);
        pas_angles = [0.0, 180.0];
        for (angle = pas_angles) {
            rotate([0, 0, angle]) {
                translate([17/2-1.65, 0, -eps])
                    cylinder(h = 3+eps, r = 3, center = false);
                translate([17/2-1.65, -3, -eps])
                   cube([3,6,3+eps]);
            }    
        }
    }
}

// === Защитный кожух мотора ===
module motor_cover() {
    difference() {
        union() {
            // --- Нижняя плита ---
            translate([0, 0, -1])
                cylinder(h = mc_base_thickness+1, r = mc_motor_plate_d / 2, center = false);
            // --- Опоры и кольцо ---
            for (angle = motor_angles) {
                rotate([0, 0, angle]) {
                    // Наклонные стойки
                    hull() {
                        translate([mc_motor_plate_d/2-3, 0, 0])
                            cylinder(h = 0.1, r1 = 4, center = false);
                        translate([D_out / 2+4, 0, mc_total_height-0.1])
                            cylinder(h = 0.1, r1 = 3, center = false);
                    }
                }
            }
            // --- Стойки вертикальные у отверстий B для усиления ---
            for (angle = motor_angles) {
                rotate([0, 0, angle]) {
                    translate([motor_radius, 0, 0])
                        cylinder(h = mc_total_height, r = 6.5, center = false);
                }
            }
            // --- Верхнее кольцо ---
            translate([0, 0, mc_total_height - mc_ring_height])
                difference() {
                    cylinder(h = mc_ring_height-0.01, r = D_out / 2, center = false);
                    translate([0, 0,-0.01]) 
                        cylinder(h = mc_ring_height+0.01, r = D_out / 2 - mc_ring_width, center = false);
                }
        }
        // --- Удаление выступающих за D_out деталей ---
        difference() {
            translate([0,0,-eps]) cylinder(h = mc_total_height+1+2*eps, r = D_out / 2+10, center = false);
            translate([0,0,-2*eps]) cylinder(h = mc_total_height+1+4*eps, r = D_out / 2, center = false);
        }
        // --- Удаление выступающих за стойки деталей пирамидой ---
        translate([0, 0, -2])
         difference() {
            cylinder(h = mc_total_height+1, r1 = mc_motor_plate_d / 2+10, r2=D_out / 2+10, center = false);
            cylinder(h = mc_total_height+1, r1 = mc_motor_plate_d / 2-1, r2=D_out / 2+3, center = false);
        }
        // --- Закладные площадки под гайки (внутри кожуха, на верхней стороне плиты) ---
        {
            for (angle = mc_adapter_angles) {
                rotate([0, 0, angle]){
                    translate([mc_nut_pad_radius/2, 0, mc_base_thickness-2.49])
                        cylinder(h = mc_nut_pad_h, r = mc_nut_pad_d / 2, center = false);
                     translate([mc_nut_pad_radius/2, 0, 0])
                        cylinder(h = mc_base_thickness+10, r = 1.6, center = true);
                }
            }   
        }
        // --- Отверстия в нижней плите ---
        // Центральное отверстие под магнит
        translate([0, 0, -1.01])
            cylinder(h = mc_base_thickness + 1.1, r = mc_encoder_hole_d / 2, center = false);
        // Отверстия под крепление двигателя (по осям)
        // Пара 1: по X (16 мм) Пара 2: по Y (19 мм)
        // Потайное отверстие под крепление двигателя под шляпку M3
        translate([ mc_motor_hole_1/2, 0, -1-eps]) cylinder(h = mc_base_thickness+1+2*eps, r = 1.6, center = false);
        translate([0,  mc_motor_hole_2/2, -1-eps]) cylinder(h = mc_base_thickness+1+2*eps, r = 1.6, center = false);
        translate([0, -mc_motor_hole_2/2, -1-eps]) cylinder(h = mc_base_thickness+1+2*eps, r = 1.6, center = false);
        translate([-mc_motor_hole_1/2, 0, -1-eps]) cylinder(h = mc_base_thickness+1+2*eps, r = 1.6, center = false);

        translate([ mc_motor_hole_1/2, 0, -1.01]) cylinder(h = mc_countersink_h, r1 = mc_countersink_d / 2, r2 = 1.6, center = false);
        translate([-mc_motor_hole_1/2, 0, -1.01]) cylinder(h = mc_countersink_h, r1 = mc_countersink_d / 2, r2 = 1.6, center = false);
        translate([0,  mc_motor_hole_2/2, -1.01]) cylinder(h = mc_countersink_h, r1 = mc_countersink_d / 2, r2 = 1.6, center = false);
        translate([0, -mc_motor_hole_2/2, -1.01]) cylinder(h = mc_countersink_h, r1 = mc_countersink_d / 2, r2 = 1.6, center = false);
      
        // --- Отверстия в кольце и стойках под винты B ---
        for (angle = motor_angles) {
            rotate([0, 0, angle]) {
                // Сквозное отверстие через кольцо и стойку под м3
                translate([motor_radius, 0, -1-eps])
                    cylinder(h = mc_total_height+1+2*eps, r = 1.6, center = false);
                // Сквозное отверстие через кольцо и стойку под шляпку м3
                translate([motor_radius, 0, -1-eps])
                    cylinder(h = mc_total_height-3+eps, r = 3.0, center = false);
            }
        }
    }
}

module bearing_simple(inner_d, outer_d, height) {
    // Проверка параметров
    assert(inner_d > 0, "Внутренний диаметр должен быть > 0");
    assert(outer_d > inner_d, "Внешний диаметр должен быть больше внутреннего");
    assert(height > 0, "Высота должна быть > 0");
    // Радиусы
    inner_r = inner_d / 2;
    outer_r = outer_d / 2;
        // Цельный подшипник
    difference() {
        cylinder(r=outer_r, h=height, center=true, $fn=32);
        cylinder(r=inner_r, h=height+1, center=true, $fn=32);
    }
}

module cutting_wedge(angle = 135, height = 20, center = false) {
    // Создаем область вырезания на заданный угол
    rotate([0, 0, -angle/2])
    for(i = [0:5:angle]) { // Шаг 5 градусов для баланса качества и скорости
        rotate([0, 0, i])
        union() {
            translate([bearing_inner/2-4, -15/2, -height/2]) 
            cube([15,15,height]);
            
            translate([shoulder_horn_r, 0, -height/2])  
            cylinder(h = height, r = 15/2, center = false);
        }
    }
}

shoulder_bearing_od=37;
shoulder_bearing_id=25.05;
shoulder_bearing_h=7;
shoulder_horn_h1=7; // Высота основания
shoulder_horn_h2=12; // толщина шарнира + выступ крепления
shoulder_h=shoulder_horn_h2+shoulder_horn_h1+shoulder_bearing_h+7;
shoulder_horn_r = bearing_inner/2+11;

module shoulder_horn() {
    difference() {
        union() {
            color("red") translate([0, 0, -shoulder_bearing_h-shoulder_horn_h2]) cylinder(h = shoulder_bearing_h+shoulder_horn_h2, r = shoulder_bearing_id/2, center = false);
            color("blue") translate([0, 0, -shoulder_horn_h2]) cylinder(h = 2, r1 = shoulder_bearing_id/2+2,  r2 = shoulder_bearing_id/2, center = false);

            cylinder(h = shoulder_horn_h1+1.5, r = bearing_inner/2+2, center = false);
            color("green") translate([bearing_inner/2-4, -15/2, -0.01]) cube([15,15,shoulder_horn_h1]);
            color("lightgreen") translate([shoulder_horn_r, 0, -1]) cylinder(h = shoulder_horn_h1+1, r = 15/2, center = false);
        }
        // Посадочные места под крепеж нагрузки m3
        for (i = [0 : 7]) {
            angle=45*i;
            rotate([0, 0, angle]) {
                translate([bearing_inner/2-4, 0, -eps])
                    cylinder(h =shoulder_horn_h2+1+eps, r = 1.6, center = false);
                translate([bearing_inner/2-4, 0, -shoulder_horn_h2-0.01])
                    cylinder(h = shoulder_horn_h2+3, r = 3.0, center = false);
            }
        }
        // Посадочные места под крепеж тяги m4
        translate([bearing_inner/2+11, 0, -2.01]) {
            cylinder(h = shoulder_horn_h1+2.01+eps, r = 2, center = false);
            translate([0, 0, shoulder_horn_h1-1.39]) cylinder(h = 3.41, r = 7.66/2, center = false);
        }
    }
}

module shoulder_top(){
    union(){
        difference() {
            union() {
                cylinder(h=shoulder_h, r=D_out/2 );
                translate([-25,0,0]) cube([50,80,shoulder_h]);
            }
            translate([5,19,-0.01]) cube([25.01,80.01,shoulder_horn_h2+shoulder_horn_h1+1]);
 //           translate([4.7,19,-0.01]) cube([25.01,80.01,shoulder_h/2+0.01]);
            translate([-25.01,65,shoulder_h/2+3.38]) cube([50.02,15.01,shoulder_h/2]);
            translate([0, 0, -0.01])cylinder(h=shoulder_horn_h2+shoulder_horn_h1+1, r = bearing_inner/2+2.5 );
            rotate([0,0,6]) translate([0, 0, 6.999]) cutting_wedge(height = shoulder_horn_h2+shoulder_horn_h1+7, angle = 135);
            translate([0,0,-eps]) cylinder(h=shoulder_horn_h2+shoulder_horn_h1+shoulder_bearing_h+1+eps, r=shoulder_bearing_od/2 );
            translate([0,0,-eps]) cylinder(h=shoulder_horn_h2+shoulder_horn_h1+shoulder_bearing_h+1.5+eps, r=shoulder_bearing_od/2-2 );
            //отверстия под штифты диаметр 6mm длинна 36mm  
            translate([-10, 61.01, 7.5]) rotate([90,0,180]) cylinder(h=19, r=3 );
            translate([10, 46.01, 26.5]) rotate([90,0,180]) cylinder(h=19, r=3 );
            // Отверстия под винты (группа A)
            rotate([0,0,-2])
            for (i = [0 : 5]) {
                x_hole = [-29.40778, -24.48010, 4.92769, 29.40778, 24.48010, -4.92769][i];
                y_hole = [11.28859, -19.82359, -31.11218, -11.28859, 19.82359, 31.11218][i];
                // Сквозное отверстие
                translate([x_hole, y_hole, -eps]) cylinder(h = shoulder_h+2*eps, r = 1.6, center = false);
                // Потай под шляпку M3
                translate([x_hole, y_hole, shoulder_h - 3.5]) cylinder(h = 3.51, r = 3.0, center = false);
            }
            //Отверстия под крепеж shoulder_bottom
            translate([0, 40, -0.01])
                cylinder(h =shoulder_h+0.02, r = 1.6, center = false);
            translate([0, 40, shoulder_h-3])
                cylinder(h =3.01, r = 3.0, center = false);
            //Отверстия под крепеж shoulder_bottom
            translate([0, 72, -0.01])
                cylinder(h =shoulder_h+0.02, r = 1.6, center = false);
            //Отверстия под крепеж shoulder_bottom
            translate([-20, 72, -0.01])
                cylinder(h =shoulder_h+0.02, r = 1.6, center = false);
            
        }
        translate([0,0,shoulder_h+16.1]) rotate([180,0,0]) reducer_connector(holes=[0,0,0,0,0,0,0,0],h1=12,skirt=true);
        //translate([0,0,shoulder_h]) cylinder(h = 9, r2 = D_out/2-13, r1 = D_out/2-7, center = false);
    }
           
}

module simple_control_rod(center_distance, rod_diameter, hole_diameter) {
    plate_thickness = 2;       // Толщина пластины
    plate_diameter = hole_diameter * 3; // Диаметр круглой пластины
    
    union() {
        // Центральная тяга (вдоль оси Z)
        cylinder(
            h = center_distance-plate_diameter+2,
            d = rod_diameter,
            center = true
        );
        
        // Верхняя лопатка (параллельно оси тяги)
        translate([0, 0, center_distance/2])
            rotate([90, 0, 0]) // Поворот на 90° чтобы пластина легла вдоль оси
            difference() {
                cylinder(
                    h = plate_thickness,
                    d = plate_diameter,
                    center = true
                );
                // Отверстие для оси шарнира (перпендикулярно тяге)
                cylinder(
                    h = plate_thickness * 2,
                    d = hole_diameter,
                    center = true
                );
            };
        
        // Нижняя лопатка (такая же, на другом конце)
        translate([0, 0, -center_distance/2])
            rotate([90, 0, 0])
            difference() {
                cylinder(
                    h = plate_thickness,
                    d = plate_diameter,
                    center = true
                );
                cylinder(
                    h = plate_thickness * 2,
                    d = hole_diameter,
                    center = true
                );
            };
    }
}

// Модуль для соединения двух точек цилиндром
module connect_points_rod(p1, p2, diameter = 6,plate_thickness=11) {
    hole_diameter= 4;
    plate_diameter = hole_diameter * 3; // Диаметр круглой пластины

    vec = p2 - p1;
    mid = (p1 + p2) / 2;
    length = norm(vec);
    
    // Угол в плоскости XY
    angle = atan2(vec.y, vec.x);
    
    translate(mid)
    rotate([0, 90, angle])
        cylinder(h = length-8, d = diameter, center = true);
    translate(p1)
    difference() {
                cylinder( h = plate_thickness, d = plate_diameter, center = true );
                // Отверстие для оси шарнира (перпендикулярно тяге)
                cylinder( h = plate_thickness * 2, d = hole_diameter, center = true );
            };
    translate(p2)
    difference() {
                cylinder( h = plate_thickness, d = plate_diameter, center = true );
                // Отверстие для оси шарнира (перпендикулярно тяге)
                cylinder( h = plate_thickness * 2, d = hole_diameter, center = true );
            };
}


// 3D-модель трапециоида
module trapezoidal_prism(bottom_width = 50,   // ширина нижнего основания
top_width = 30,      // ширина верхнего основания
height = 20,         // высота трапеции (в плоскости XY)
depth = 10,          // глубина призмы (по оси Z)
left_offset = 8     // смещение для неравнобокости
) {
    // Берём 2D-трапецию и выдавливаем вдоль оси Z
    linear_extrude(height = depth) {
        polygon([
            [0, 0],                    // A — нижний левый
            [bottom_width, 0],         // B — нижний правый
            [bottom_width - left_offset, height],  // C — верхний правый
            [top_width - left_offset, height]      // D — верхний левый
        ]);
    }
}

connect_rod_l=184;
foot_r=shoulder_horn_r+6;
point_foot_center=[-13,connect_rod_l,0];
hips_l = connect_rod_l-75;
hips_l1 = hips_l-22;

module hip() {
    point_foot_center_in_hip =[12, hips_l+10,shoulder_h/2+3.5];
    union() {
        difference() {
            union() {
                cube([50,hips_l1,shoulder_h]);
                translate([0, hips_l1,shoulder_h/2+3.5]) trapezoidal_prism(depth = shoulder_h/2-3.5,left_offset = 28,height = 37,bottom_width = 50,top_width=30);
                color("blue") translate([0, hips_l1,0]) trapezoidal_prism(depth = 20,left_offset = 15,height = 16,bottom_width = 30,top_width=26);   
                translate(point_foot_center_in_hip) cylinder(h =shoulder_h/2-3.5, r = 22/2, center = false);
           }
            translate([-0.01,-0.01,-0.01]) cube([50.01,15.01,shoulder_h/2+3.5]);
            translate([30,-0.01,-0.01]) cube([20.01,hips_l1+0.02,shoulder_h/2+3.5]);
            //отверстия под штифты диаметр 6mm длинна 36mm  
            translate([15, 14.99, 7.5]) rotate([90,0,180]) cylinder(h=19, r=3 );
            translate([35, -0.01, 26.5]) rotate([90,0,180]) cylinder(h=19, r=3 );
            //Отверстия под крепеж hip_top
            translate([5, 7, -0.01]) cylinder(h =shoulder_h+0.02, r = 1.6, center = false);
            translate([5, 7, shoulder_h-3]) cylinder(h =3.01, r = 3.0, center = false);
            translate([25, 7, -0.01]) cylinder(h =shoulder_h+0.02, r = 1.6, center = false);
            translate([25, 7, shoulder_h-3]) cylinder(h =3.01, r = 3.0, center = false);
            translate([5, hips_l1-7, -0.01]) cylinder(h =shoulder_h+0.02, r = 1.6, center = false);
            translate([5, hips_l1-7, shoulder_h-3]) cylinder(h =3.01, r = 3, center = false);
            translate([25, hips_l1-7, -0.01]) cylinder(h =shoulder_h+0.02, r = 1.6, center = false);
            translate([25, hips_l1-7, shoulder_h-3]) cylinder(h =3.01, r = 3, center = false);
            

                    // Посадочное место под мини-подшипник 688ZZ (8x16x5)
        translate(point_foot_center_in_hip) translate([0,0,-0.01])
            cylinder(h = 5.2, r = 16/2, center = false);
        translate(point_foot_center_in_hip)
            cylinder(h = 5.7, r = 14/2, center = false);
        translate(point_foot_center_in_hip)
            cylinder(h = 6, r = 9/2, center = false);
        }

    }
               
}

module hip_top(){
    point_foot_center_in_hip =[12, hips_l+47+10,0];
    difference() {
        union() {
            cube([50,hips_l+25,11.2]);
            translate([0, hips_l+25,0]) trapezoidal_prism(depth = 11.2,left_offset = 28,height = 37,bottom_width = 50,top_width=30);   
            translate(point_foot_center_in_hip) cylinder(h =11.2, r = 22/2, center = false);
        }
        translate([25,-18.3,-0.01]) cylinder(h=shoulder_h, r=D_out/2+1 );
        // Посадочное место под мини-подшипник 688ZZ (8x16x5)
        translate(point_foot_center_in_hip) translate([0,0,6.01])
            cylinder(h = 5.2, r = 16/2, center = false);
        translate(point_foot_center_in_hip) translate([0,0,5.3])
            cylinder(h = 5.7, r = 14/2, center = false);
        translate(point_foot_center_in_hip) translate([0,0,5])
            cylinder(h = 6, r = 9/2, center = false);
            //Отверстия под крепеж hip_top
            translate([25, 22, -0.01]) cylinder(h =shoulder_h+0.02, r = 1.6, center = false);     
            translate([25, 22, -0.01]) cylinder(h =3.01, r = 3.0, center = false);        
            translate([5, 50+4, -0.01]) cylinder(h =shoulder_h+0.02, r = 1.6, center = false);
            translate([5, 50+4, -0.01]) cylinder(h =3.01, r = 3.0, center = false);
            translate([25, 50+4, -0.01]) cylinder(h =shoulder_h+0.02, r = 1.6, center = false);     
            translate([25, 50+4, -0.01]) cylinder(h =3.01, r = 3.0, center = false);
            translate([5, hips_l+25-7, -0.01]) cylinder(h =shoulder_h+0.02, r = 1.6, center = false);
            translate([5, hips_l+25-7, -0.01]) cylinder(h =3.01, r = 3, center = false);
            translate([25, hips_l+25-7, -0.01]) cylinder(h =shoulder_h+0.02, r = 1.6, center = false);     
            translate([25, hips_l+25-7,-0.01]) cylinder(h =3.01, r = 3, center = false);
    }
}

module cot_surface(prism_depth = 25, curve_length = 30, curve_height = 25) {
    // Предопределённые точки для котангенса (ручной расчёт)
    // Диапазон: 0.3 до 2.84 радиан (избегаем асимптот)
    samples = 10;      // количество точек

    points = [
        [0, 10], [-4,-10], 
        [9.0, -10.153], [10.5, -3.232], [12.0, -1.176],
        [13.5, -0.364], [15.0, 0.364], [16.5, 1.176],
        [18.0, 3.232], [19.5, 10.153]
    ];
    
    // Масштабируем и позиционируем точки
    scaled_points = [
        for (p = points) [
            p[0] * (curve_length/20),        // масштаб по X
            p[1] * (curve_height/10)         // масштаб по Z
        ]
    ];
    
    // Создаём поверхность
    linear_extrude(height = prism_depth, center = true) {
        polygon(scaled_points);
    }
}

// шарнир колена
module shin(foot=true){
    difference() {
        union() {
//            translate([0,0,0.5]) cylinder( h = 30, r = 8/2, center = true );
            translate([0,0,0.5]) cylinder( h = shoulder_h/2+3.5, r = 8/2+1, center = true );
            color("lightgreen") translate([foot_r,0,-9]) cylinder( h = shoulder_horn_h1+2, r = 15/2, center = false );
            difference() {
                translate([-14,0,0]) cube([foot_r*2+27,15,shoulder_horn_h2+shoulder_horn_h1-1], center = true );
                rotate([0,4,0]) rotate([0,90,-90]) translate([-15,20,0]) cot_surface(curve_length=15,curve_height=30);
                translate([-47,0,0])rotate([180,180,0])foot_joint_original_end_cut();
            }
            translate([-47,0,0])rotate([180,180,0])foot_joint_tongue();
            if(foot==true){
                translate([-47,0,0])rotate([180,180,0])foot_connector();
            }
        }
        // Вычитаем чтобы вставить штифт
        translate([0,0,0.5]) cylinder( h = 30, r = 8/2, center = true );
        translate([foot_r,0,-9.01]) cylinder( h = 10.02, r = 2.1, center = false );
        translate([foot_r,0,-9.01]) cylinder( h = 3.4, r = 7.66/2, center = false );
        translate([-foot_r-10,0,-9.01]) cylinder( h = 25, r = 2.1, center = false );
    }
}

// соединитель для нижней части ноги
module foot_connector()
{
    foot_cuff();
    robot_foot();
}

// Держатель-бочонок для датчика MT6816 / XJX-135
module rsgl_magnet_spacer(
    val_dia = 3.97,       // диаметр вала
    magnet_dia = 4.01,    // диаметр магнита
    magnet_height = 1.5,  // высота магнита
    val_height =1,
    val_clearance = 0.13,    // натяг на вал: -0.03 мм → отверстие 3.94 мм
    mag_clearance = 0.1,    // натяг под магнит: -0.01 мм → отверстие 4.00 мм
    bottom_thickness = 1,   // минимальная толщина дна (развязка от вала)
    d = 9.0          // внешний диаметр бочонка (для жёсткости)
    )
{
    mag_pocket_depth = magnet_height + 0.05;  // глубина гнезда
    total_height = bottom_thickness + mag_pocket_depth+val_height; // ≈2.45 мм
  difference() {
    // Основной цилиндр
    cylinder(d = d, h = total_height, $fn = 64);
    
    // Отверстие под вал (с натягом)
    translate([0, 0, -0.1])
      cylinder(d = val_dia + val_clearance, h = 1, $fn = 64);
    
    // Гнездо под магнит (с натягом, глубже на 0.05 мм)
    translate([0, 0, bottom_thickness+1])
      cylinder(d = magnet_dia + mag_clearance, h = mag_pocket_depth + 0.1, $fn = 64);
  }
}

// Адаптер для энкодера MT6816 / XJX-135
module encoder_adapter(h=1.2){
    difference() {
        union() {
            cylinder(h = h, r = mc_motor_plate_d / 2-5, center = false);
            for (angle = mc_adapter_angles) {
                rotate([0, 0, angle]){
                    translate([mc_nut_pad_radius/2, 0, h])
                        cylinder(h = 2, r = 3);
                }
            }
        }
        for (angle = mc_adapter_angles) {
            rotate([0, 0, angle]){
                translate([mc_nut_pad_radius/2, 0, -0.01])
                    cylinder(h = h+2.02, r = 1.6);
            }
        }
        // Центральное отверстие под магнит
        translate([0, 0, -0.01]) cylinder(h = h+0.02, r = mc_encoder_hole_d / 2, center = false);
    }
}

// ========== Функция расчета кинематики сервопривода ноги ==========
function calculate_rigid_linkage(
    angle1, rod_length, radius1, radius2, center1, center2
) = 
let(
    a1 = angle1,
    P1 = [center1.x + radius1 * cos(a1), center1.y + radius1 * sin(a1), center1.z],
    dx = center2.x - P1.x,
    dy = center2.y - P1.y,
    d = sqrt(dx*dx + dy*dy),
    min_length = abs(d - radius2),
    max_length = d + radius2,
    solution_exists = (rod_length >= min_length) && (rod_length <= max_length),
    P2 = solution_exists ? 
        let(
            cos_phi = (d*d + radius2*radius2 - rod_length*rod_length) / (2 * d * radius2),
            theta = atan2(P1.y - center2.y, P1.x - center2.x),
            alpha = acos(cos_phi),
            angle2 = theta + alpha,
            point2 = [center2.x + radius2 * cos(angle2), center2.y + radius2 * sin(angle2), center2.z]
        )
        point2
        : [0, 0, 0],
    angle2_result = solution_exists ? atan2(P2.y - center2.y, P2.x - center2.x) : 0
)
[
    ["point1", P1], ["point2", P2], ["angle1", angle1], ["angle2", angle2_result],
    ["solution_exists", solution_exists], ["distance", rod_length],
    ["min_possible", min_length], ["max_possible", max_length]
];

function get_value(data, key) = 
    let(idx = search([key], data, num_returns_per_match=1)[0])
    data[idx][1];

// Public dimensions for previews; use the actual model variables.
function leg_kinematic_parameters()=[point_foot_center,connect_rod_l,shoulder_horn_r,foot_r,h_reducer+cap_thickness+2*zazor+9.5];
// Native body placement: fore/aft spacing, left mount frame, pitch-axis offset, symmetry plane.
function body_gait_parameters()=[320,[0,-63,-h_reducer-14.5],-109,(24+133)/2];

servo_angle=$t*135-135/2+7;
leg_angle1=$t*360;


module leg(servo=servo_angle){
    result = calculate_rigid_linkage(servo, connect_rod_l, shoulder_horn_r, foot_r, [0,0,0], point_foot_center);

    point1 = get_value(result, "point1");
    point2 = get_value(result, "point2");
    angle2 = get_value(result, "angle2");
    solution_exists = get_value(result, "solution_exists");
    min_possible = get_value(result, "min_possible");
    max_possible = get_value(result, "max_possible");

    echo("Точка 1: ", point1);
    echo("Точка 2: ", point2);
    echo("Угол толкателя: ", servo, "°");
    echo("Угол колена: ", angle2, "°");
    echo("Длина тяги (расчетная): ", norm(point2 - point1), "мм");
    echo("Радиус плеча толкателя:", shoulder_horn_r, "мм");
    echo("Радиус плеча колена:", foot_r, "мм");

    echo("Ширина ноги: ",shoulder_h/2+7);
    echo("Диапазон возможных длин: от ", min_possible, " до ", max_possible, "мм");
    echo("Решение существует: ", solution_exists);
    union() {
        rotate([0,0,servo]) translate([0,0,h_reducer+2*zazor+cap_thickness+8]) rotate([180,0,0]) shoulder_horn();
        translate([0,0,h_reducer+cap_thickness+2*zazor]) shoulder_top();
        color("gray") translate([0, 0,ecc_shaft_h1 + ecc_spacer_h+separator_h+5 +h_reducer+2*zazor+cap_thickness+1.99]) bearing_simple(25,37,7);
        translate([-25,65,h_reducer+cap_thickness+2*zazor]) hip();
        color("gray") translate(point_foot_center) translate([0,0 ,h_reducer+cap_thickness+2*zazor+22.5]) bearing_simple(8,16,5);
        color("lightgray") translate([0,0,41]) connect_points_rod(p1=point1,p2=point2);
        translate(point_foot_center) translate([0,0 ,h_reducer+cap_thickness+2*zazor+9.5]) rotate([0,0,angle2]) shin();
        color("gray") translate(point_foot_center) translate([0,0 ,h_reducer+cap_thickness+2*zazor-2.51]) bearing_simple(8,16,5);
        translate([-25,-32+50 ,h_reducer]) hip_top();
        //translate([-55,183 ,36.5]) rotate([0,0,180]) rotate([0,0,angle2]) foot_connector();
        color("lightgray") import("vptc_roller_19_4_5_70_reducer.stl");
   }
}

// Модуль для поворота вокруг точки
module rotate_around_point(angle, axis, point) {
    translate(point) {
        rotate(angle, axis) {
            translate(-point) {
                children();
            }
        }
    }
}

module leg_left_front1(a=0){
    color("lightgray") translate([0,0 ,0]) rotate([0,0,a]) import("vptc_roller_19_4_5_70_leg_left_front.stl");
    color("lightgray") rotate([0,0,a]) import("vptc_roller_19_4_5_70_reducer.stl");
}

module leg_left_front2(a=0,with_leg=true){
    color("lightgray") rotate([0,180,0]) import("vptc_roller_19_4_5_70_reducer_with_bracing_and_connector.stl",center=true);
    if(with_leg) translate([0,0 ,-109]) leg_left_front1(a=a);
}

module leg_left_front_union(a1=0,a2=0,with_leg=true){
        color("lightgray") translate([0,76 ,-13]) rotate([90,0,0]) import("vptc_roller_19_4_5_70_reducer_with_bracing_and_connector.stl");
        rotate_around_point(a1,[0,1,0],[0,0,-13])  leg_left_front2(a=a2,with_leg=with_leg);

}

module angle_cut(h=100,l=20){
    difference() {
        cube([l,l,h]);
        translate([0,0,-0.01])
            cylinder(h=h+0.02,r=l);
    }
}

module body_cut_wall_with_holes(h=100,w=180,l=32,r=15,holes=[0,0,0,0,0,0,0,0],holes2=[1,1,1,1,1,1,1,1],m=[1,1,1]){
    difference(){
        cube([h,w,l], true);
        if(m[0])
            translate([5,0,l-10]) minkowski(){
                cube([h-2*r+10,w-2*r+1,1], true);
                sphere(r, $fn=50);
            }
        if(m[1])
            translate([5,0,-l+10]) minkowski(){
                cube([h-2*r+10,w-2*r+1,l-2*r+1], true);
                sphere(r, $fn=50);
            }
        // Посадочные места под крепеж нагрузки m3
        translate([0,+30 ,-24]) {
            for (i = [0 : 7]) {
                angle=45*i;
                rotate([0, 0, angle]) {
                    if(holes2[i]) translate([bearing_inner/2-4, 0, 18.01])
                        cylinder(h = 12, r = 1.6, center = false);
                    if(holes[i]){
                        translate([bearing_inner/2-4, 0, 26.61])
                            cylinder(h =3.01, r = 3.0, center = false);
                    }
                }
            }
        }
        if(m[2])
            translate([0,-35 ,0]) cylinder(h=12, r=35, center=true);
    }
}

module body_wall_with_holes(h=10,w=100,d=210,center=true){
    difference(){
        cube([w,d,h],center=center);
        translate([0,0,-0.01]) cylinder(h=d+0.02, r=35, center=true);
        x=[w/2-15,-w/2+15,w/2-15,-w/2+15,w/2-10,-w/2+10,w/2-10,-w/2+10];
        y=[25,25,-25,-25,75,75,-75,-75];
        for (i = [0 : 7]) {
            translate([x[i], y[i], -0.01])
            cylinder(h = d+0.02, r = 1.6, center = true);
            translate([x[i], y[i], h/2-1.49])
            cylinder(h =3.01, r = 3.0, center = true);
        }
    }
}

module body_wall_for_legs(h=100,w=180,d=210,l=31,
    h_move=10, // Смещение отверситий odrive
    w_move=0  // смещение стен для задних ног
){
    holes=[1,0,1,0,1,0,1,0];
    difference(){
        union() {
            translate([5,-30 ,24+w_move]) body_cut_wall_with_holes(h=h,w=w,l=l,r=15,holes=holes);
            translate([5,-30 ,133-w_move]) mirror([0,0,1]) body_cut_wall_with_holes(h=h,w=w,l=l,r=15,holes=holes);
            translate([2.5,65 ,78]) rotate([90,0,0]) body_wall_with_holes(h=10,d=d,w=h+5,center=true);
            translate([2.5,-125 ,78])rotate([90,0,180]) body_wall_with_holes(h=10,d=d,w=h+5,center=true);
            translate([-h/2,-130 ,8.5+w_move]) cube([5,w+20,h+l+9-2*w_move]);
        }
        x=[0, 0, 43.5 , 43.5];
        y=[0,135.5,0,135.5];
        rotate([0,90,0]) translate([-100,-100-h_move,-48])for (i = [0 : 3]) {
            translate([x[i], y[i], -0.01])
                cylinder(h = 7+0.02, r = 1.6, center = true);
            translate([x[i], y[i], -1])
                cylinder(h =3.01, r = 3.0, center = true);
        }
    }
}

module body_centr_for_bat(h=100,w=180,d=210,l=31){
    holes=[0,0,0,0,0,0,0,0];
    difference(){
        union() {
            translate([2.5,-70 ,-14.5]) body_cut_wall_with_holes(h=h-5,w=w,l=l,r=15,holes=holes,holes2=holes,m=[1,0,0]);
            translate([2.5,-70 ,d-39.5]) mirror([0,0,1]) body_cut_wall_with_holes(h=h-5,w=w,l=l,r=15,holes=holes,holes2=holes,m=[1,0,0]);
            translate([0,-15 ,78]) rotate([90,0,0]) body_wall_with_holes(h=10,d=d,w=h,center=true);
            translate([0,-125 ,78])rotate([90,0,180]) body_wall_with_holes(h=10,d=d,w=h,center=true);
            translate([-h/2,-130 ,-27]) cube([5,w+20,d]);
        }
    }
}


module body(a1=0,a2=0,parts=false){
    holes=[1,0,1,0,1,0,1,0];
        body_wall_for_legs();
        translate([2.5,200 ,0]) body_centr_for_bat(h=105,w=100,d=210,l=25);
        translate([0,320 ,0]) body_wall_for_legs(h_move=-10,w_move=10);
        reducer_connector(h1=15,skirt=true,holes=holes);
        if(parts)
            translate([0,-63 ,-h_reducer-14.5]) leg_left_front_union(a1=a1,a2=a2);
}




// === Абсолютный off-axis энкодер: два магнитных кольца и одна CAN-плата ===
// Самостоятельные параметрические варианты; ручные output/*.scad не используются.
// Для других габаритов платы нужна отдельная электрическая разводка.
encoder_magnet_d = 5;
encoder_magnet_h = 1;
encoder_magnet_recess_depth = 0.4;
encoder_magnet_clearance = 0.2;
encoder_rim_wall = 0.6;
encoder_rim_h = 0.4;
encoder_separator_lift = 0.5;
encoder_sensor_angle = 9.000000000;
encoder_body_bolts = [[-29.407783435,11.288590411], [-24.480097786,-19.823592318], [4.927685649,-31.112182729], [29.407783435,-11.288590411], [24.480097786,19.823592318], [-4.927685649,31.112182729]];
encoder_separator_total_h = 18.500000000;
encoder_separator_bearing_step = 11.5;
// Native PCB body envelopes; source SHA256: 06bff4c53965bdceb5cb1050a268093edc0ef2067780bc5193bdcda59fa44f3d
encoder_native_components = [[29.29999857, -5.00007236, -90.0, false, [5.1, 5.1, 0.6]], [30.00003342, 23.99997306, 0.0, false, [3, 3, 1.45]], [28.60017482, 57.42125341, 90.0, false, [3, 3, 1.45]], [31.41854548, 62.82327335, 0.0, false, [3, 3, 1.1]], [29.49660997, 6.61905332, 45.0, false, [2.5, 2, 0.7]], [22.7178344, 20.34941528, -90.0, true, [1, 0.5, 0.4]], [25.64702712, 17.94042293, -90.0, true, [1, 0.5, 0.4]], [28.93872838, 17.49575788, -90.0, true, [1, 0.5, 0.4]], [31.8127333, 15.87117861, -90.0, true, [1, 0.5, 0.4]], [24.85819784, -3.92139889, 180.0, true, [1, 0.5, 0.4]], [27.80287755, 0.82434282, 0.0, true, [1, 0.5, 0.4]], [26.73667893, 12.52880771, -90.0, true, [1, 0.5, 0.4]], [32.55614381, 12.77696379, -90.0, true, [1, 0.5, 0.4]], [30.62972319, 20.44657757, 0.0, true, [1.6, 0.8, 0.55]], [27.1207227, 2.23994767, 180.0, false, [1, 0.5, 0.55]], [32.30061821, -11.06641852, 0.0, false, [1, 0.5, 0.55]], [24.68299009, -6.98105741, 0.0, true, [1.6, 0.8, 0.95]], [31.89043744, -4.31602752, 90.0, true, [1, 0.5, 0.55]], [29.59746611, -4.65110804, 90.0, true, [1, 0.5, 0.55]], [26.03766503, 3.08218082, 0.0, true, [1, 0.5, 0.55]], [32.15960199, 5.71059314, -90.0, true, [1, 0.5, 0.55]], [27.41550656, 27.12584025, 180.0, false, [1, 0.5, 0.55]], [27.98303057, 29.31313936, 180.0, false, [1, 0.5, 0.55]], [29.39459984, 52.11646857, 90.0, false, [1.6, 0.8, 0.95]], [31.94526569, 54.17042484, 0.0, false, [1.6, 0.8, 0.95]], [23.91024885, 1.67763947, 90.0, true, [1, 0.5, 0.55]], [26.87905504, 4.39543561, 180.0, false, [1, 0.5, 0.55]], [31.85671044, 3.41926782, 0.0, false, [1, 0.5, 0.55]]];

encoder_clamp_h = 12;
encoder_clamp_body_h = encoder_clamp_h-encoder_magnet_recess_depth;
encoder_magnet_ring_h = encoder_magnet_recess_depth+encoder_rim_h;
encoder_pocket_d = encoder_magnet_d+encoder_magnet_clearance;
encoder_rim_d = encoder_pocket_d+2*encoder_rim_wall;
encoder_outer_track_r = D_out/2-2-encoder_rim_d/2-0.3;
encoder_track_pitch = encoder_pocket_d+encoder_rim_wall+0.2;
encoder_inner_track_r = encoder_outer_track_r-encoder_track_pitch;
function encoder_max_even(r,s) = 2*floor((180/asin(s/(2*r)))/2);
encoder_outer_count = min(
    encoder_max_even(encoder_outer_track_r,encoder_pocket_d+encoder_rim_wall),
    encoder_max_even(encoder_inner_track_r,encoder_pocket_d+encoder_rim_wall)+2);
encoder_inner_count = encoder_outer_count-2;
encoder_track_radii = [encoder_inner_track_r,encoder_outer_track_r];
encoder_track_counts = [encoder_inner_count,encoder_outer_count];

encoder_pcb_h = 0.8;
encoder_pcb_inner_r = encoder_inner_track_r-1.9;
encoder_pcb_relief_r = encoder_pcb_inner_r-0.3;
encoder_pcb_outer_r = encoder_outer_track_r+3.9;
encoder_pcb_span = 160;
encoder_pcb_mount_r = encoder_outer_track_r+1;
encoder_pcb_mount_angles = [encoder_sensor_angle-68,encoder_sensor_angle+68];
encoder_pcb_clearance = 0.25;
encoder_body_bolt_keepout = 4.5;
encoder_rear_inner_r = bearing_outer/2+1;
encoder_rear_outer_r = D_out/2-1.3;
encoder_rear_depth = 2.3;
encoder_mcu_r = encoder_outer_track_r-0.2;
encoder_mcu_angle = encoder_sensor_angle-14;
encoder_mcu_rotation = len(encoder_native_components)>0 ? -90 : encoder_sensor_angle-9;
encoder_mcu_body = [5.1,5.1,0.6];
encoder_mcu_xy_clearance = 0.2;
encoder_mcu_axial_clearance = 0.15;
encoder_sensor_envelope_h = 1.45; // TI DBV Amax1.4 plus0.05 mechanical reserve.
encoder_sensor_max_h = 1.4;
encoder_hall_depth_from_top = 0.73;
encoder_hall_height = encoder_sensor_max_h-encoder_hall_depth_from_top;
encoder_sensor_gap = 0.2;
encoder_window_h = 0.4;
encoder_magnet_air_gap = 0.4;
encoder_roof_extra_h = 0.4;
encoder_pcb_bottom_z = cap_thickness;
encoder_pcb_top_z = encoder_pcb_bottom_z+encoder_pcb_h;
encoder_sensor_front_z = encoder_pcb_top_z+encoder_sensor_envelope_h;
encoder_pocket_ceiling_z = encoder_sensor_front_z+encoder_sensor_gap;
encoder_lid_base_z = encoder_pcb_top_z+0.25;
encoder_lid_top_z = encoder_pocket_ceiling_z+encoder_window_h;
encoder_main_ceiling_z = encoder_pocket_ceiling_z-encoder_roof_extra_h;
encoder_magnet_bottom_z = encoder_lid_top_z+encoder_magnet_air_gap;
encoder_glue_face_z = encoder_magnet_bottom_z+encoder_magnet_h;
encoder_clamp_face_z = encoder_glue_face_z-encoder_magnet_recess_depth;
encoder_bearing_bottom_z = cap_thickness-1-bearing_width-0.5+encoder_separator_lift;
encoder_separator_base_z = encoder_bearing_bottom_z-encoder_separator_bearing_step;
encoder_separator_top_z = encoder_separator_base_z+encoder_separator_total_h;
encoder_connector_contact_z = encoder_clamp_face_z+5.9;
// Recessed magnets shorten the output stem by0.4mm while preserving the sensor gap.
encoder_connector_stem_h = encoder_connector_contact_z-4-encoder_separator_top_z;
encoder_load_connector_h = 15;
encoder_screw_head_h = 1.3;
encoder_screw_ceiling_z = encoder_pcb_top_z+encoder_screw_head_h+0.2;

module encoder_validate() {
    assert(encoder_magnet_d>0 && encoder_magnet_h>0 && encoder_rim_wall>0 && encoder_rim_h>0,
        "Проверьте размеры магнитов и бортиков");
    assert(encoder_inner_track_r-encoder_rim_d/2>=bearing_inner/2,
        "Два кольца магнитов не помещаются на торце зажима");
    assert(encoder_outer_count>=6 && encoder_outer_count%2==0,
        "Нужно чётное число магнитов");
    for(t=[0:1]) assert(2*encoder_track_radii[t]*sin(180/encoder_track_counts[t])
        >=encoder_pocket_d+encoder_rim_wall,"Недостаточна перемычка между магнитами");
    assert(encoder_connector_stem_h>0,"Неположительная длина соединителя");
    assert(encoder_magnet_recess_depth>=0 && encoder_magnet_recess_depth<encoder_clamp_h,
        "Недопустимая глубина посадок магнитов");
    assert(encoder_clamp_body_h>10.2,"Под отдельным кольцом не остаётся верхней стенки зажима");
    assert(encoder_separator_lift<=0.5,"Подшипник поднят выше сохранённого упора крышки");
    assert(encoder_screw_ceiling_z<=encoder_lid_top_z-encoder_window_h,
        "Головка M2 не помещается под крышкой");
    assert(encoder_pcb_bottom_z-encoder_mcu_body[2]-encoder_mcu_axial_clearance>=cap_thickness-1+0.2,
        "Локальный карман MCU затрагивает посадку подшипника");
    children();
}

module encoder_body_bolt_positions() {
    for(p=encoder_body_bolts) translate([p[0],p[1],0]) children();
}
module encoder_mount_positions() {
    for(a=encoder_pcb_mount_angles)
        rotate([0,0,a]) translate([encoder_pcb_mount_r,0,0]) children();
}
module encoder_sensor_positions() {
    for(r=encoder_track_radii) rotate([0,0,encoder_sensor_angle]) translate([r,0,0]) children();
}
module encoder_annulus(ro,ri,h) {
    difference() {
        cylinder(r=ro,h=h);
        translate([0,0,-eps]) cylinder(r=ri,h=h+2*eps);
    }
}
function encoder_board_inner_radius(a) = let(d=abs(a-encoder_sensor_angle))
    d<=10 ? encoder_pcb_relief_r : d>=12 ? encoder_pcb_inner_r :
    encoder_pcb_relief_r+(encoder_pcb_inner_r-encoder_pcb_relief_r)*(d-10)/2;
module encoder_pcb_outline(clearance=0) {
    offset(delta=clearance) difference() {
        polygon(concat(
            [for(i=[0:640]) let(a=encoder_sensor_angle-80+i/4)
                [encoder_pcb_outer_r*cos(a),encoder_pcb_outer_r*sin(a)]],
            [for(i=[640:-1:0]) let(a=encoder_sensor_angle-80+i/4,r=encoder_board_inner_radius(a))
                [r*cos(a),r*sin(a)]]));
        encoder_body_bolt_positions() circle(r=encoder_body_bolt_keepout);
    }
}
module encoder_sensor_outline(clearance=0) {
    // Center of the package is +.12 radial and +.40 tangential from the Hall point.
    translate([0.12,0.4]) offset(delta=clearance) square([2.8,2.9],center=true);
}
module encoder_pcb_bare() {
    difference() {
        linear_extrude(height=encoder_pcb_h) encoder_pcb_outline();
        encoder_mount_positions() translate([0,0,-eps]) cylinder(d=2.2,h=encoder_pcb_h+2*eps);
    }
}
module encoder_pcb_model() {
    color("SeaGreen") translate([0,0,encoder_pcb_bottom_z]) encoder_pcb_bare();
    color("DimGray") encoder_sensor_positions()
        translate([0,0,encoder_pcb_top_z]) linear_extrude(height=encoder_sensor_envelope_h)
            encoder_sensor_outline();
    if(len(encoder_native_components)>0) {
        for(c=encoder_native_components)
            rotate([0,0,c[1]]) translate([c[0],0,c[3] ? encoder_pcb_top_z+c[4][2]/2 : encoder_pcb_bottom_z-c[4][2]/2])
                rotate([0,0,c[2]-c[1]]) color("DimGray") cube(c[4],center=true);
    } else {
      // Other diameters retain a mechanical budget pending a new PCB layout.
      rotate([0,0,encoder_mcu_angle])
        translate([encoder_mcu_r,0,encoder_pcb_bottom_z-encoder_mcu_body[2]/2])
            rotate([0,0,encoder_mcu_rotation-encoder_mcu_angle])
                color("DimGray") cube(encoder_mcu_body,center=true);
    for(c=[[encoder_sensor_angle+15,3,3,1.45],[encoder_sensor_angle+49,3,3,1.45]])
        rotate([0,0,c[0]]) translate([encoder_outer_track_r+0.5,0,encoder_pcb_bottom_z-c[3]/2])
            color("DimGray") cube([c[1],c[2],c[3]],center=true);
    }
    color("Silver") encoder_mount_positions() translate([0,0,encoder_pcb_top_z])
        cylinder(d=3.5,h=encoder_screw_head_h);
}

module encoder_track_positions(full_circle=false) {
    for(t=[0:1]) let(n=encoder_track_counts[t],r=encoder_track_radii[t])
        for(j=[0:(full_circle ? n-1 : n/2-1)]) let(a=(j+.5)*360/n)
            translate([r*cos(a),r*sin(a),encoder_clamp_h]) children();
}
module encoder_magnet_carrier_ring(full_circle=true) {
    intersection() {
        difference() {
            translate([0,0,encoder_clamp_body_h])
                cylinder(r=D_out/2-2,h=encoder_magnet_ring_h);
            translate([0,0,encoder_clamp_body_h-eps])
                cylinder(r=bearing_inner/2,h=encoder_magnet_ring_h+2*eps);
            encoder_track_positions(true) translate([0,0,-encoder_magnet_recess_depth-eps])
                cylinder(d=encoder_pocket_d,h=encoder_magnet_ring_h+2*eps);
        }
        translate([-D_out,full_circle ? -D_out : 0,encoder_clamp_body_h-eps])
            cube([2*D_out,full_circle ? 2*D_out : D_out,encoder_magnet_ring_h+2*eps]);
    }
}
// Compatibility view: two half rings appear as one full ring in the assembly.
module encoder_magnet_rims() { encoder_magnet_carrier_ring(full_circle=false); }
module encoder_magnet_ring_for_print() {
    translate([0,0,-encoder_clamp_body_h]) encoder_magnet_carrier_ring();
}
module encoder_magnets(second_half=false) {
    for(t=[0:1]) let(n=encoder_track_counts[t],r=encoder_track_radii[t])
        for(j=[0:n/2-1]) let(a=(j+.5)*360/n,index=j+(second_half ? n/2 : 0))
            color(index%2==0 ? "Firebrick" : "RoyalBlue")
                translate([r*cos(a),r*sin(a),encoder_clamp_h-encoder_magnet_recess_depth])
                    cylinder(d=encoder_magnet_d,h=encoder_magnet_h);
}
module connector_clamp_encoder_body_half() {
    encoder_validate() difference() {
        connector_clamp();
        if(encoder_magnet_recess_depth>0)
            translate([-D_out,-eps,encoder_clamp_body_h])
                cube([2*D_out,D_out+2*eps,encoder_magnet_recess_depth+eps]);
    }
}
module connector_clamp_encoder_half() {
    union() {
        connector_clamp_encoder_body_half();
        encoder_magnet_rims();
    }
}
module encoder_clamp_body_for_print() {
    translate([0,encoder_clamp_body_h,0]) rotate([90,0,0]) connector_clamp_encoder_body_half();
}
module connector_clamp_encoder(show_magnets=false) {
    for(half=[0:1]) rotate([0,0,180*half]) {
        connector_clamp_encoder_half();
        // Magnets are always background objects for printable clamp exports.
        if(show_magnets) %encoder_magnets(second_half=half==1);
    }
}
module reducer_connector_encoder() {
    reducer_connector(h1=encoder_connector_stem_h,skirt=false);
}
module load_connector_encoder() {
    reducer_connector(h1=encoder_load_connector_h,skirt=true,holes=[1,0,1,0,1,0,1,0]);
}
module encoder_rear_pocket() {
    difference() {
        intersection() {
            encoder_pcb_outline(encoder_pcb_clearance);
            difference() { circle(r=encoder_rear_outer_r); circle(r=encoder_rear_inner_r); }
        }
        encoder_mount_positions() circle(d=4.4);
    }
}
module encoder_mcu_clearance() {
    rotate([0,0,encoder_mcu_angle])
        translate([encoder_mcu_r,0,encoder_pcb_bottom_z-encoder_mcu_body[2]-encoder_mcu_axial_clearance])
            rotate([0,0,encoder_mcu_rotation-encoder_mcu_angle])
                translate([-encoder_mcu_body[0]/2-encoder_mcu_xy_clearance,
                           -encoder_mcu_body[1]/2-encoder_mcu_xy_clearance,0])
                    cube([encoder_mcu_body[0]+2*encoder_mcu_xy_clearance,
                          encoder_mcu_body[1]+2*encoder_mcu_xy_clearance,
                          encoder_mcu_body[2]+encoder_mcu_axial_clearance+eps]);
}
module encoder_native_rear_clearances() {
    for(c=encoder_native_components) if(!c[3])
        rotate([0,0,c[1]]) translate([c[0],0,encoder_pcb_bottom_z-c[4][2]-encoder_mcu_axial_clearance])
            rotate([0,0,c[2]-c[1]])
                translate([-c[4][0]/2-encoder_mcu_xy_clearance,-c[4][1]/2-encoder_mcu_xy_clearance,0])
                    cube([c[4][0]+2*encoder_mcu_xy_clearance,c[4][1]+2*encoder_mcu_xy_clearance,
                          c[4][2]+encoder_mcu_axial_clearance+eps]);
}
module cap_encoder(with_bracing=true) {
    encoder_validate() difference() {
        union() {
            if(with_bracing) cap_with_bracing(); else cap();
            translate([0,0,cap_thickness-eps])
                encoder_annulus(D_out/2,bearing_outer/2-2,encoder_lid_base_z-cap_thickness+eps);
        }
        translate([0,0,encoder_pcb_bottom_z])
            linear_extrude(height=encoder_lid_base_z-encoder_pcb_bottom_z+eps)
                encoder_pcb_outline(encoder_pcb_clearance);
        translate([0,0,encoder_pcb_bottom_z-encoder_rear_depth])
            linear_extrude(height=encoder_rear_depth+eps) encoder_rear_pocket();
        if(len(encoder_native_components)>0) encoder_native_rear_clearances();
        else encoder_mcu_clearance();
        encoder_mount_positions() translate([0,0,encoder_pcb_bottom_z-2]) cylinder(d=1.6,h=2+eps);
        encoder_body_bolt_positions() translate([0,0,cap_thickness-eps]) cylinder(d=3.2,h=5);
        rotate([0,0,encoder_sensor_angle+59])
            translate([encoder_pcb_outer_r-1.4,-2,encoder_pcb_bottom_z-1.2]) cube([9,4,1.1]);
    }
}
module lid_encoder() {
    encoder_validate() difference() {
        translate([0,0,encoder_lid_base_z])
            encoder_annulus(D_out/2,bearing_inner/2+0.6,encoder_lid_top_z-encoder_lid_base_z);
        translate([0,0,encoder_lid_base_z-eps])
            linear_extrude(height=encoder_main_ceiling_z-encoder_lid_base_z+eps)
                encoder_pcb_outline(encoder_pcb_clearance);
        encoder_sensor_positions() translate([0,0,encoder_lid_base_z-eps])
            linear_extrude(height=encoder_pocket_ceiling_z-encoder_lid_base_z+eps)
                encoder_sensor_outline(encoder_pcb_clearance);
        encoder_mount_positions() translate([0,0,encoder_lid_base_z-eps])
            cylinder(d=4,h=encoder_screw_ceiling_z-encoder_lid_base_z+eps);
        encoder_body_bolt_positions() {
            translate([0,0,encoder_lid_base_z-eps]) cylinder(d=3.2,h=encoder_lid_top_z-encoder_lid_base_z+2*eps);
            // The90degree countersink remains exactly6mm at the real top face.
            translate([0,0,encoder_lid_top_z-1.4]) cylinder(d1=3.2,d2=6+2*eps,h=1.4+eps);
        }
    }
}
module encoder_assembly(exploded=false,section=false,with_bracing=true,show_electronics=true,show_magnets=true) {
    encoder_validate() intersection() {
        union() {
            color("LightGray") cap_encoder(with_bracing);
            color("Gainsboro") translate([0,0,exploded ? 12 : 0]) lid_encoder();
            if(show_electronics) translate([0,0,exploded ? 5 : 0]) encoder_pcb_model();
            color("Silver") translate([0,0,encoder_bearing_bottom_z+(exploded ? -10 : 0)])
                encoder_annulus(bearing_outer/2,bearing_inner/2,bearing_width);
            color("DarkSalmon") translate([0,0,encoder_separator_base_z+(exploded ? -25 : 0)]) separator();
            color("LightSteelBlue") translate([0,0,encoder_connector_contact_z+(exploded ? 20 : 0)])
                mirror([0,0,1]) reducer_connector_encoder();
            color("SteelBlue") translate([0,0,encoder_connector_contact_z+(exploded ? 32 : 0)]) load_connector_encoder();
            translate([0,0,encoder_clamp_face_z+encoder_clamp_h+(exploded ? 20 : 0)]) mirror([0,0,1])
                for(half=[0:1]) rotate([0,0,180*half]) {
                    color("SlateGray") connector_clamp_encoder_half();
                    if(show_magnets) encoder_magnets(half==1);
                }
        }
        if(section) rotate([0,0,encoder_sensor_angle]) translate([-D_out,0,-D_out]) cube([2*D_out,D_out,3*D_out]);
        else translate([-D_out,-D_out,-D_out]) cube([2*D_out,2*D_out,3*D_out]);
    }
}
module encoder_selected_part(part) {
    echo("Encoder magnets inner/outer:",encoder_inner_count,encoder_outer_count);
    echo("Encoder output connector stem, mm:",encoder_connector_stem_h);
    if(part=="encoder_assembly") encoder_assembly();
    else if(part=="encoder_exploded") encoder_assembly(exploded=true);
    else if(part=="encoder_section") encoder_assembly(section=true);
    else if(part=="encoder_cap") cap_encoder();
    else if(part=="encoder_lid") translate([0,0,-encoder_lid_base_z]) lid_encoder();
    else if(part=="encoder_print") {
        translate([-D_out/2-4,0,0]) cap_encoder();
        translate([D_out/2+4,0,-encoder_lid_base_z]) lid_encoder();
    }
    else if(part=="encoder_clamp") connector_clamp_encoder(show_magnets=true);
    else if(part=="encoder_clamp_half") connector_clamp_encoder_body_half();
    else if(part=="encoder_magnet_ring") encoder_magnet_ring_for_print();
    else if(part=="encoder_clamp_print") {
        translate([-D_out/2-4,0,0]) encoder_clamp_body_for_print();
        translate([D_out/2+4,0,0]) encoder_clamp_body_for_print();
        translate([0,encoder_clamp_body_h+D_out/2+7,0]) encoder_magnet_ring_for_print();
    }
    else if(part=="encoder_connector") reducer_connector_encoder();
    else if(part=="encoder_load_connector") load_connector_encoder();
    else if(part=="encoder_pcb") encoder_pcb_bare();
    else assert(false,str("Неизвестный вариант: ",part));
}


// === Сборка ===
// Выбор можно поменять через -D 'generated_part="encoder_cap"' в OpenSCAD.
generated_part = "legacy";
zazor=1; // Зазор исходного печатного расположения деталей собаки.
if(generated_part != "legacy") encoder_selected_part(generated_part);
else
difference() {
    union() {
        //rigid_gear();
        //rigid_gear_with_bracing();  // Корпус с боковым креплением
        //color("gray") translate([0, 0, 3]) bearing_simple(17,26,5);
        //translate([0, 0, h_reducer+zazor]) cap();
        //translate([0, 0, h_reducer+zazor]) cap_with_bracing();  // Крышка с боковым креплением
        //translate([0, 0, 0.5]) eccentric_shaft();
        //color("gray") translate([0, 0, 3.5+5+ecc_spacer_h]) bearing_simple(17,26,5);
        //translate([0, 0, 14]) rotate([180,0,0]) eccentric();
        //color("gray") translate([0, 0, ecc_shaft_h1 + ecc_spacer_h + ecc_shaft_h2+3.5]) bearing_simple(8,16,5);
        //translate([0, 0, ecc_shaft_h1 + ecc_spacer_h-1]) separator();
        //color("gray") translate([0, 0,ecc_shaft_h1 + ecc_spacer_h+separator_h+5]) bearing_simple(40,52,7);
        // translate([0, 0, ecc_shaft_h1 + ecc_spacer_h + ecc_shaft_h2]) rollers();
        //translate([0, 0, -mc_total_height]) motor_cover(); // кожух снизу
        //translate([0,D_out/2+8+zazor,(h_reducer+cap_thickness)/2]) rotate([90,45/2,0]) reducer_connector();
        //translate([0,0,h_reducer+zazor+cap_thickness+6.5]) rotate([180,0,0])reducer_connector();
        //leg();
        body(a1=0,a2=leg_angle1,parts=true);
        //shin();
        //import("vptc_roller_19_4_5_70_reducer_with_bracing_and_connector.stl");
        //color("lightgray")import("vptc_roller_19_4_5_70_reducer.stl");
    }
// Куб-«нож», отсекающий правую половину (x > 0)
//    rotate([0,0,90])translate([0, -100, -100])
//        cube([100, 200, 200]);
}
