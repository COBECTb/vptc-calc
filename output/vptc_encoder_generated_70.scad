use <foots.scad>
// ВПТК редуктор с роликами (для 3D-печати)
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
motor_angles = [54.0, 144.0, 234.0, 324.0];
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
            x_hole = [24.48010, -4.92769, -29.40778, -24.48010, 4.92769, 29.40778][i];
            y_hole = [19.82359, 31.11218, 11.28859, -19.82359, -31.11218, -11.28859][i];
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
            x_hole = [24.48010, -4.92769, -29.40778, -24.48010, 4.92769, 29.40778][i];
            y_hole = [19.82359, 31.11218, 11.28859, -19.82359, -31.11218, -11.28859][i];
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
            for (angle = motor_angles) {
                rotate([0, 0, angle+45]){
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
shoulder_horn_h1=7;
shoulder_horn_h2=8;
shoulder_h=shoulder_horn_h2+shoulder_horn_h1+shoulder_bearing_h+4.5;
shoulder_horn_r = bearing_inner/2+11;

module shoulder_horn() {
    difference() {
        union() {
            color("red") translate([0, 0, -shoulder_bearing_h-shoulder_horn_h2]) cylinder(h = shoulder_bearing_h+shoulder_horn_h2, r = shoulder_bearing_id/2, center = false);
            color("blue") translate([0, 0, -shoulder_bearing_h-1]) cylinder(h = 2, r1 = shoulder_bearing_id/2+2,  r2 = shoulder_bearing_id/2, center = false);

            cylinder(h = shoulder_horn_h1+1.5, r = bearing_inner/2+2, center = false);
    		color("green") translate([bearing_inner/2-4, -15/2, 0]) cube([15,15,shoulder_horn_h1]);
            color("lightgreen") translate([shoulder_horn_r, 0, -2]) cylinder(h = shoulder_horn_h1+2, r = 15/2, center = false);
        }
        // Посадочные места под крепеж нагрузки m3
        for (i = [0 : 7]) {
            angle=45*i;
            rotate([0, 0, angle]) {
                translate([bearing_inner/2-4, 0, -eps])
                    cylinder(h =shoulder_horn_h2+1+eps, r = 1.6, center = false);
                translate([bearing_inner/2-4, 0, -8])
                    cylinder(h = 11, r = 3.0, center = false);
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
            translate([4.7,19,-11.5]) cube([25.01,80.01,shoulder_h]);
            translate([4.7,19,-10.5]) cube([25.01,80.01,shoulder_h/2]);
            translate([-25.01,65,14.99]) cube([50.02,15.01,shoulder_h/2]);
            translate([0, 0, -0.01])cylinder(h=shoulder_horn_h2+shoulder_horn_h1+1, r = bearing_inner/2+2 );
            rotate([0,0,6]) translate([0, 0, 6.999]) cutting_wedge(height = shoulder_horn_h2+shoulder_horn_h1+1, angle = 135);
            translate([0,0,-eps]) cylinder(h=shoulder_horn_h2+shoulder_horn_h1+shoulder_bearing_h+1+eps, r=shoulder_bearing_od/2 );
            translate([0,0,-eps]) cylinder(h=shoulder_horn_h2+shoulder_horn_h1+shoulder_bearing_h+1.5+eps, r=shoulder_bearing_od/2-2 );
            //отверстия под штифты диаметр 6mm длинна 36mm  
            translate([-10, 61.01, 7.5]) rotate([90,0,180]) cylinder(h=19, r=3 );
            translate([10, 46.01, 20.5]) rotate([90,0,180]) cylinder(h=19, r=3 );
            // Отверстия под винты (группа A)
            rotate([0,0,-2])
            for (i = [0 : 5]) {
                x_hole = [24.48010, -4.92769, -29.40778, -24.48010, 4.92769, 29.40778][i];
                y_hole = [19.82359, 31.11218, 11.28859, -19.82359, -31.11218, -11.28859][i];
                // Сквозное отверстие
                translate([x_hole, y_hole, -eps]) cylinder(h = shoulder_h+2*eps, r = 1.6, center = false);
                // Потай под шляпку M3
                translate([x_hole, y_hole, shoulder_h - 3.5]) cylinder(h = 3.51, r = 3.0, center = false);
            }
            //Отверстия под крепеж shoulder_bottom
            translate([0, 40, -0.01])
                cylinder(h =shoulder_h+0.02, r = 1.6, center = false);
            translate([0, 40, 23.5])
                cylinder(h =3.01, r = 3.0, center = false);
            //Отверстия под крепеж shoulder_bottom
            translate([0, 72, -0.01])
                cylinder(h =shoulder_h+0.02, r = 1.6, center = false);
            //Отверстия под крепеж shoulder_bottom
            translate([-20, 72, -0.01])
                cylinder(h =shoulder_h+0.02, r = 1.6, center = false);
            
        }
        translate([0,0,shoulder_h+16.1]) rotate([180,0,0]) reducer_connector(fitting=false,h1=12);
        translate([0,0,shoulder_h]) cylinder(h = 9, r2 = D_out/2-13, r1 = D_out/2-7, center = false);
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
module connect_points_rod(p1, p2, diameter = 6) {
    hole_diameter= 4;
    plate_thickness = 2;       // Толщина пластины
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

foot_r=shoulder_horn_r+6;
point_foot_center=[-13,170,0];
hips_l = 170-75;
hips_l1 = hips_l-22;

module hip() {
    point_foot_center_in_hip =[12, hips_l+10,15.3]; 
    union() {
        difference() {
            union() {
                cube([50,hips_l1,shoulder_h]);
                translate([0, hips_l1,15.3]) trapezoidal_prism(depth = 11.2,left_offset = 28,height = 37,bottom_width = 50,top_width=30);   
                color("blue") translate([0, hips_l1,0]) trapezoidal_prism(depth = 20,left_offset = 15,height = 16,bottom_width = 30,top_width=26);   
                translate(point_foot_center_in_hip) cylinder(h =11.2, r = 22/2, center = false);
           }
            translate([-0.01,-0.01,-0.01]) cube([50.02,15.01,shoulder_h/2+2]);
            translate([30,-0.01,-0.01]) cube([20.01,hips_l1+0.02,shoulder_h/2+2]);
            //отверстия под штифты диаметр 6mm длинна 36mm  
            translate([15, 14.99, 7.5]) rotate([90,0,180]) cylinder(h=19, r=3 );
            translate([35, -0.01, 20.5]) rotate([90,0,180]) cylinder(h=19, r=3 );
            //Отверстия под крепеж hip_top
            translate([5, 7, -0.01]) cylinder(h =shoulder_h+0.02, r = 1.6, center = false);
            translate([5, 7, 24]) cylinder(h =3.01, r = 3.0, center = false);
            translate([25, 7, -0.01]) cylinder(h =shoulder_h+0.02, r = 1.6, center = false);     
            translate([25, 7, 24]) cylinder(h =3.01, r = 3.0, center = false);
            translate([5, hips_l1-7, -0.01]) cylinder(h =shoulder_h+0.02, r = 1.6, center = false);
            translate([5, hips_l1-7, 24]) cylinder(h =3.01, r = 3, center = false);
            translate([25, hips_l1-7, -0.01]) cylinder(h =shoulder_h+0.02, r = 1.6, center = false);     
            translate([25, hips_l1-7, 24]) cylinder(h =3.01, r = 3, center = false);
            

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
            for (angle = motor_angles) {
                rotate([0, 0, angle+45]){
                    translate([mc_nut_pad_radius/2, 0, h])
                        cylinder(h = 2, r = 3);
                }
            }
        }
        for (angle = motor_angles) {
            rotate([0, 0, angle+45]){
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

servo_angle=$t*135-135/2+7;


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
encoder_body_bolts = [[24.480097786,19.823592318], [-4.927685649,31.112182729], [-29.407783435,11.288590411], [-24.480097786,-19.823592318], [4.927685649,-31.112182729], [29.407783435,-11.288590411]];
encoder_separator_total_h = 18.500000000;
encoder_separator_bearing_step = 11.5;
// Native PCB body envelopes; source SHA256: 47f620a4afcaf855fb9fe4f9b037aa41ffb146d775b7bcd35ffbf51e1659cf29
encoder_native_components = [[23.324021549010048, 25.181598798266474, 9.0, true, [1, 0.5, 0.55]], [26.663551408203393, 7.1731756000784435, -81.0, true, [1, 0.5, 0.55]], [23.279390209360468, 20.647816817984914, 9.0, true, [1.6, 0.8, 0.95]], [22.94558705291821, -2.3099323772774545, 9.0, true, [1, 0.5, 0.4]], [25.279684766775272, 37.33913352591807, 9.0, true, [1.6, 0.8, 0.55]], [31.66970071147225, 5.197960476424253, 9.0, true, [1, 0.5, 0.55]], [25.90680397238849, 3.7955605127752445, 9.0, true, [1, 0.5, 0.55]], [23.769727796365373, -13.24902207410184, 99.0, true, [1.6, 0.8, 0.95]], [25.45412443264614, -4.981650250343179, 9.0, true, [1.6, 0.8, 0.95]], [23.39999942950959, 31.619867216367666, 99.0, true, [1, 0.5, 0.55]], [29.738642991247904, 20.895605218579668, 9.0, true, [3, 3, 1.1]], [25.86624249196982, 29.361603659734833, 9.0, true, [3, 3, 1.45]], [26.672691734880306, 11.363588174163953, 99.0, true, [1, 0.5, 0.55]], [31.607751523383904, 0.9980776408592369, 9.0, true, [1, 0.5, 0.4]], [26.288590337835018, -11.020346258602213, 99.0, true, [3, 3, 1.45]], [26.978000024658982, -7.2517088962365674, 9.0, false, [1, 0.5, 0.55]], [30.07444861799481, -2.216525586617059, 9.0, false, [1, 0.5, 0.55]], [31.98652253819139, 2.1771475742020465, 9.0, false, [1, 0.5, 0.55]], [29.93730859923533, -0.22634309180421663, 9.0, false, [1, 0.5, 0.55]], [29.499999997036024, 9.000000554097277, 99.0, false, [5.1, 5.1, 0.6]], [30.427495207509086, 20.18068063037946, -81.0, false, [1, 0.5, 0.4]], [26.820887097594753, 26.354027251067638, 9.0, false, [1, 0.5, 0.4]], [27.06011823689487, 18.35789522423886, 9.0, false, [1, 0.5, 0.55]], [27.411363423250677, -2.0844718204068626, -81.0, false, [2.5, 2, 0.7]], [29.23234470295932, 24.272311361797147, 9.0, false, [1, 0.5, 0.4]], [27.344103453239576, 21.46062692405697, -81.0, false, [1, 0.5, 0.4]], [29.398128451346622, 20.577490158880085, -81.0, false, [1, 0.5, 0.4]], [31.458226189157667, 19.809858962755225, -81.0, false, [1, 0.5, 0.4]]];
encoder_native_boundary = [[22.022149999999996, 25.111450000000005], [22.131508999999994, 25.015122000000005], [22.240447000000003, 24.918317000000002], [22.348962, 24.821038], [22.457051000000007, 24.723286], [22.564712, 24.625063999999995], [22.671943999999996, 24.526371999999995], [22.778745, 24.427214000000006], [22.885110999999995, 24.327590999999998], [22.991041999999993, 24.227503999999996], [23.096536, 24.126957000000004], [23.201589, 24.025949999999995], [23.306201, 23.924485000000004], [23.410369000000003, 23.822565999999995], [23.514090999999993, 23.720191999999997], [23.617366000000004, 23.617367], [23.720191, 23.514092000000005], [23.822564999999997, 23.41037], [23.924484000000007, 23.306202], [24.025948999999997, 23.201589999999996], [24.033434999999997, 23.193804], [23.948220000000006, 23.181732999999994], [23.838629999999995, 23.162532999999996], [23.729726, 23.139757000000003], [23.621626000000006, 23.113429999999994], [23.514444999999995, 23.083579999999998], [23.408298000000002, 23.050239000000005], [23.303298999999996, 23.013442999999995], [23.199560000000005, 22.973231999999996], [23.097193000000004, 22.929647000000003], [22.996306000000004, 22.882737000000006], [22.897008, 22.832550999999995], [22.799404999999993, 22.779143000000005], [22.703602000000004, 22.722568999999993], [22.609701, 22.662892], [22.517803999999998, 22.600173999999996], [22.428006999999994, 22.534482999999994], [22.340407999999996, 22.465889000000004], [22.2551, 22.394465999999994], [22.172174999999996, 22.320289000000002], [22.091721000000007, 22.243438999999995], [22.013824, 22.163998000000007], [21.938569, 22.082051000000007], [21.866034999999997, 21.997685000000004], [21.796300000000002, 21.910991999999993], [21.729439999999997, 21.822063], [21.665524000000005, 21.730993999999995], [21.604623000000004, 21.637882000000005], [21.546800000000005, 21.542828], [21.492119000000002, 21.445932999999997], [21.440636999999995, 21.347300000000004], [21.392409999999998, 21.247035999999994], [21.347489999999993, 21.145247999999995], [21.305924000000005, 21.042044000000004], [21.267757000000003, 20.937534999999997], [21.233029000000002, 20.831834], [21.201779000000002, 20.725053000000003], [21.174040000000005, 20.617306999999997], [21.149839999999998, 20.508711000000005], [21.129206999999994, 20.399381000000005], [21.112161999999998, 20.289434999999997], [21.098723000000007, 20.17899], [21.088904999999997, 20.068163999999996], [21.082718999999997, 19.957076], [21.080169999999995, 19.845845999999995], [21.081261999999995, 19.734590999999995], [21.085994, 19.623431999999994], [21.094361000000006, 19.512486999999993], [21.106352, 19.401876], [21.121956999999995, 19.291715999999994], [21.141157000000007, 19.182125], [21.163933, 19.073222], [21.190259999999995, 18.965120999999996], [21.220110000000005, 18.857940999999997], [21.253451, 18.751794000000004], [21.290246999999994, 18.646794999999997], [21.330457999999993, 18.543056000000007], [21.374043, 18.440687999999994], [21.420952999999997, 18.339800999999994], [21.471138999999994, 18.240503000000004], [21.524547999999996, 18.142900999999995], [21.581120999999996, 18.047098000000005], [21.640798000000004, 17.953197000000003], [21.703515999999993, 17.861299000000002], [21.769206999999994, 17.771502999999996], [21.837801, 17.683903], [21.909223999999995, 17.598596], [21.983401, 17.51567], [22.060250999999994, 17.435215999999997], [22.139691999999997, 17.35732], [22.221638999999996, 17.282065000000003], [22.306005, 17.209531], [22.392697999999996, 17.139796000000004], [22.481627000000003, 17.072935], [22.572695999999993, 17.009020000000007], [22.665808, 16.948117999999994], [22.760862000000003, 16.890296000000006], [22.857758000000004, 16.835615000000004], [22.95639, 16.784132999999997], [23.056653999999995, 16.735906], [23.158443000000005, 16.690984999999998], [23.261646, 16.649418999999995], [23.366155000000006, 16.611251999999993], [23.471856000000002, 16.576525000000004], [23.578637, 16.545275000000004], [23.686383000000006, 16.517534999999995], [23.794978999999998, 16.493336], [23.904308999999998, 16.472701999999998], [24.014255000000006, 16.455657000000002], [24.124701, 16.442217999999997], [24.235525999999993, 16.432401], [24.346614000000002, 16.426214], [24.457843999999994, 16.423665999999997], [24.569098999999994, 16.424757999999997], [24.680257999999995, 16.42949], [24.791202999999996, 16.437855999999996], [24.901814, 16.449848000000003], [25.011973999999995, 16.465452], [25.121565000000004, 16.484652999999994], [25.230469, 16.507429000000002], [25.338569000000007, 16.533755999999997], [25.445749000000006, 16.563605999999993], [25.551896, 16.596946000000003], [25.656895000000006, 16.633741999999998], [25.760633999999996, 16.673953999999995], [25.863001999999994, 16.717538000000005], [25.963888999999995, 16.764449], [26.063187, 16.814634999999996], [26.160788999999994, 16.868043], [26.256591999999998, 16.924616], [26.350493, 16.984294000000006], [26.442391, 17.047011999999995], [26.532186999999993, 17.112702999999996], [26.619787000000002, 17.181297], [26.705095, 17.252719999999997], [26.788020000000003, 17.326896000000005], [26.868474000000006, 17.403745999999998], [26.94637, 17.483187], [27.021625999999998, 17.565134999999998], [27.094160000000002, 17.649500000000003], [27.163894, 17.736193999999998], [27.230755000000002, 17.825123000000005], [27.294669999999996, 17.916191999999995], [27.355571999999995, 18.009303000000003], [27.413393999999997, 18.104358000000005], [27.468075, 18.201252999999994], [27.519557000000006, 18.299886], [27.567784000000003, 18.400149999999996], [27.612705000000005, 18.501937999999996], [27.654270999999994, 18.605142], [27.683795000000003, 18.685985000000002], [27.689853999999997, 18.677042999999998], [27.771085, 18.556045999999995], [27.851786000000004, 18.434696000000002], [27.931956999999997, 18.312994000000003], [28.011595999999997, 18.190944000000002], [28.09070299999999, 18.068548000000007], [28.169274, 17.945807000000002], [28.247309, 17.822725000000005], [28.324805999999995, 17.699303999999998], [28.401763999999986, 17.575546000000003], [28.478181000000006, 17.451453], [28.554056000000003, 17.327027], [28.62938700000001, 17.202271999999994], [28.704173999999995, 17.07719], [28.778413, 16.951781999999994], [28.852104999999995, 16.826051000000007], [28.92524800000001, 16.700000000000003], [28.997839999999997, 16.573632000000003], [29.069880000000012, 16.446946999999994], [29.141366000000005, 16.319950000000006], [29.212298000000004, 16.192642000000006], [29.28267299999999, 16.065025000000006], [29.352490999999986, 15.937102999999993], [29.421750000000003, 15.808876999999995], [29.490449000000012, 15.680351000000002], [29.55858699999999, 15.551524999999998], [29.626160999999996, 15.422404], [29.693172000000004, 15.292989000000006], [29.75961699999999, 15.163283000000007], [29.825495999999987, 15.033287999999999], [29.890806999999995, 14.903007000000002], [29.95554899999999, 14.772442999999996], [30.019721000000004, 14.641597000000004], [30.083321000000012, 14.510471999999993], [30.14634799999999, 14.379070999999996], [30.208800999999994, 14.247395999999995], [30.27068, 14.115449999999996], [30.33198200000001, 13.983236000000005], [30.392706000000004, 13.850755000000007], [30.452852000000007, 13.718010000000007], [30.512417999999997, 13.585003999999998], [30.571403000000004, 13.451740000000001], [30.629806000000002, 13.318219], [30.687625999999995, 13.184444999999997], [30.744862000000012, 13.050420000000003], [30.801512000000002, 12.916146999999995], [30.857575999999995, 12.781627], [30.913051999999993, 12.646863999999994], [30.96794, 12.511860999999996], [31.022239000000013, 12.376619000000005], [31.075945999999988, 12.241140999999999], [31.129062000000005, 12.105430999999996], [31.18158600000001, 11.969489999999993], [31.23351600000001, 11.833320999999998], [31.284851000000003, 11.696927000000002], [31.335589999999996, 11.560310000000001], [31.385732999999988, 11.423473000000001], [31.43527800000001, 11.286418999999995], [31.48422500000001, 11.149150000000006], [31.532573000000014, 11.011668], [31.58032, 10.873976999999996], [31.627466, 10.736079000000004], [31.67401000000001, 10.597976000000003], [31.71995000000001, 10.459671999999998], [31.765287, 10.321168], [31.81001900000001, 10.182468], [31.854145999999986, 10.043574000000007], [31.897665999999987, 9.904488999999998], [31.940577999999988, 9.765214999999998], [31.982882999999987, 9.625755999999996], [32.02457899999999, 9.486113000000003], [32.065664999999996, 9.346289999999996], [32.10614000000001, 9.206288], [32.146004000000005, 9.066112000000004], [32.18525700000001, 8.925762000000006], [32.223895999999996, 8.785242999999994], [32.261922, 8.644557000000006], [32.29933399999999, 8.503705999999994], [32.336130999999995, 8.362692999999993], [32.372311999999994, 8.221519999999998], [32.40787700000001, 8.080191999999997], [32.442825, 7.938709000000003], [32.47715500000001, 7.797076000000004], [32.51086699999999, 7.655293999999998], [32.54396, 7.513366000000005], [32.57643300000001, 7.3712950000000035], [32.60828599999999, 7.229084], [32.63951800000001, 7.0867350000000044], [32.670129, 6.944250999999994], [32.700118, 6.8016350000000045], [32.72948500000001, 6.6588899999999995], [32.758228, 6.516017000000005], [32.786347000000006, 6.373020999999994], [32.81384299999999, 6.229902999999993], [32.840712999999994, 6.086667000000006], [32.86695900000001, 5.943314999999998], [32.892577999999986, 5.799850000000006], [32.91757200000001, 5.656273999999996], [32.94193899999999, 5.5125910000000005], [32.965678, 5.368802000000002], [32.988789999999995, 5.224912000000003], [33.011273999999986, 5.080922000000001], [33.033129, 4.936835000000002], [33.05435600000001, 4.792653999999999], [33.074952999999994, 4.648381999999998], [33.09492, 4.504022000000006], [33.11425800000001, 4.359575000000007], [33.13296500000001, 4.215046000000001], [33.15104099999999, 4.070436999999998], [33.168486, 3.9257499999999936], [33.185298999999986, 3.7809879999999936], [33.201481, 3.6361540000000048], [33.21703099999999, 3.4912510000000054], [33.23194799999999, 3.346282000000002], [33.24623299999999, 3.2012490000000042], [33.259884, 3.056155000000004], [33.27290199999999, 2.9110019999999963], [33.28528700000001, 2.765794999999997], [33.297037999999986, 2.6205340000000064], [33.308156, 2.475223999999997], [33.31863899999999, 2.329866999999993], [33.32848799999999, 2.184465000000003], [33.33770200000001, 2.0390220000000028], [33.346281000000005, 1.8935400000000016], [33.35422600000001, 1.7480209999999943], [33.361536, 1.6024699999999967], [33.368210000000005, 1.4568880000000064], [33.37424899999999, 1.3112780000000015], [33.37965299999999, 1.1656440000000003], [33.384421, 1.0199870000000004], [33.388554, 0.8743110000000058], [33.39205100000001, 0.7286179999999973], [33.394913, 0.5829109999999957], [33.39713800000001, 0.4371929999999935], [33.398728000000006, 0.29146699999999726], [33.39968200000001, 0.14573500000000195], [33.400000000000006, 0.0], [33.39968200000001, -0.14573400000000447], [33.398728000000006, -0.2914659999999998], [33.39713800000001, -0.43719199999999603], [33.394913, -0.5829099999999983], [33.39205100000001, -0.7286169999999998], [33.388554, -0.8743099999999941], [33.384421, -1.019986000000003], [33.37965299999999, -1.1656430000000029], [33.37424899999999, -1.311277000000004], [33.368210000000005, -1.4568869999999947], [33.361536, -1.6024689999999993], [33.35422600000001, -1.7480199999999968], [33.346281000000005, -1.893539000000004], [33.33770200000001, -2.0390210000000053], [33.32848799999999, -2.1844640000000055], [33.31863899999999, -2.3298659999999956], [33.308156, -2.4752229999999997], [33.297037999999986, -2.6205329999999947], [33.28528700000001, -2.7657939999999996], [33.27290199999999, -2.911000999999999], [33.259884, -3.0561540000000065], [33.24623299999999, -3.2012480000000068], [33.23194799999999, -3.3462810000000047], [33.21703099999999, -3.4912499999999937], [33.201481, -3.636152999999993], [33.185298999999986, -3.780986999999996], [33.168486, -3.925748999999996], [33.15104099999999, -4.070436000000001], [33.13296500000001, -4.2150450000000035], [33.11425800000001, -4.359573999999995], [33.09492, -4.5040209999999945], [33.074952999999994, -4.6483810000000005], [33.05435600000001, -4.792653000000001], [33.033129, -4.936834000000005], [33.011273999999986, -5.080921000000004], [32.988789999999995, -5.224911000000006], [32.965678, -5.368801000000005], [32.94193899999999, -5.512590000000003], [32.91757200000001, -5.656272999999999], [32.892577999999986, -5.799848999999995], [32.86695900000001, -5.943314000000001], [32.840712999999994, -6.086665999999994], [32.81384299999999, -6.229901999999996], [32.786347000000006, -6.373019999999997], [32.758228, -6.516015999999993], [32.72948500000001, -6.658889000000002], [32.700118, -6.801634000000007], [32.670129, -6.944249999999997], [32.63951800000001, -7.086734000000007], [32.60828599999999, -7.229083000000003], [32.57643300000001, -7.371294000000006], [32.54396, -7.513364999999993], [32.51086699999999, -7.655293], [32.47715500000001, -7.797075000000007], [32.442825, -7.938708000000005], [32.40787700000001, -8.080191], [32.372311999999994, -8.221519], [32.336130999999995, -8.362691999999996], [32.29933399999999, -8.503704999999997], [32.261922, -8.644555999999994], [32.223895999999996, -8.785241999999997], [32.18525700000001, -8.925760999999994], [32.146004000000005, -9.066111000000006], [32.10614000000001, -9.206287000000003], [32.103139999999996, -9.216662999999997], [32.05007900000001, -9.148900999999995], [31.978656, -9.063592999999997], [31.90447900000001, -8.980666999999997], [31.82763, -8.900212999999994], [31.748188, -8.822316999999998], [31.666241000000014, -8.747062], [31.581875999999994, -8.674527999999995], [31.495182, -8.604793], [31.406252999999992, -8.537931999999998], [31.315183999999988, -8.474017000000003], [31.222071999999997, -8.413115000000005], [31.127017999999993, -8.355293000000003], [31.030123000000003, -8.300612000000001], [30.931489999999997, -8.249129999999994], [30.831225999999987, -8.200902999999997], [30.729437999999988, -8.155983000000006], [30.62623400000001, -8.114416000000006], [30.521726, -8.076249000000004], [30.416023999999993, -8.041522], [30.30924300000001, -8.010272], [30.20149699999999, -7.982532000000006], [30.092901000000012, -7.958332999999996], [29.983571000000012, -7.937698999999995], [29.873625000000004, -7.920653999999999], [29.763180000000006, -7.907214999999994], [29.652354000000003, -7.8973979999999955], [29.541266000000007, -7.891210999999998], [29.430036, -7.888662999999994], [29.318781, -7.889754999999994], [29.207621999999986, -7.894486999999998], [29.096677, -7.902852999999993], [28.986065999999994, -7.914845], [28.875905999999986, -7.930449999999993], [28.76631499999999, -7.949650000000005], [28.657411999999994, -7.972425999999999], [28.549311999999986, -7.998752999999994], [28.44213099999999, -8.028603000000004], [28.335983999999996, -8.061943999999997], [28.230985000000004, -8.098738999999995], [28.127246000000014, -8.138951000000006], [28.024878, -8.182535000000001], [27.923992, -8.229445999999996], [27.824693999999994, -8.279632000000007], [27.727091, -8.333039999999997], [27.631287999999998, -8.389612999999997], [27.537386999999995, -8.449291000000002], [27.445488999999995, -8.512009000000006], [27.355693000000002, -8.577699999999993], [27.268094000000005, -8.646293999999997], [27.182785999999993, -8.717716999999993], [27.099860000000007, -8.791893000000002], [27.019406000000004, -8.868742999999995], [26.941509999999994, -8.948183999999998], [26.866254999999995, -9.030131999999995], [26.793721000000005, -9.114497], [26.723985999999996, -9.201190999999994], [26.657124999999994, -9.290120000000002], [26.59321, -9.381189000000006], [26.532308, -9.474300999999997], [26.474486, -9.569355000000002], [26.419804999999997, -9.666250000000005], [26.368323000000004, -9.764882999999998], [26.320096000000007, -9.865146999999993], [26.275176000000002, -9.966935000000007], [26.233609, -10.070138999999998], [26.195442, -10.174646999999993], [26.160714999999996, -10.280349000000001], [26.129464999999996, -10.387129000000002], [26.101725000000002, -10.494876000000005], [26.077526000000006, -10.603471999999996], [26.056892000000005, -10.712801999999996], [26.039846999999995, -10.822748000000004], [26.026408000000004, -10.933193000000003], [26.016591000000005, -11.044019000000006], [26.010403999999994, -11.155107000000001], [26.007856000000004, -11.266336999999993], [26.008948000000004, -11.377592000000007], [26.013679999999994, -11.488750999999993], [26.022046000000003, -11.599694999999997], [26.034037999999995, -11.710307], [26.049643000000003, -11.820466999999994], [26.068843, -11.930058000000002], [26.091618999999994, -12.038961], [26.117946000000003, -12.147060999999994], [26.147796, -12.254242000000005], [26.181137000000007, -12.360388999999998], [26.217932000000005, -12.465388000000004], [26.258144, -12.569126999999995], [26.301727999999997, -12.671493999999996], [26.348639000000006, -12.772380999999996], [26.398825000000002, -12.871679], [26.452233000000007, -12.969282000000007], [26.508806000000007, -13.065084999999996], [26.568483999999998, -13.158985999999999], [26.631202000000002, -13.250884], [26.696893000000003, -13.340680000000006], [26.765486999999993, -13.428279000000003], [26.836910000000003, -13.513587000000001], [26.911085999999997, -13.596512000000004], [26.987936000000005, -13.676965999999993], [27.067376999999993, -13.754863], [27.149325000000005, -13.830117999999999], [27.233689999999996, -13.902652000000003], [27.320384000000004, -13.972386999999998], [27.409312999999997, -14.039248], [27.500382000000002, -14.103162999999995], [27.593494000000007, -14.164064999999994], [27.688547999999997, -14.221886999999995], [27.785443, -14.276567999999997], [27.884075999999993, -14.328050000000005], [27.984340000000003, -14.376277000000002], [28.086128000000002, -14.421197000000006], [28.189332000000007, -14.462762999999995], [28.29383999999999, -14.500929999999997], [28.399541999999997, -14.535657999999998], [28.50632200000001, -14.566907999999998], [28.614069, -14.594648000000007], [28.722665000000006, -14.618847000000002], [28.831995000000006, -14.639481000000004], [28.941941000000014, -14.656526], [29.052386000000013, -14.669963999999993], [29.163211999999987, -14.679782000000003], [29.27430000000001, -14.685969], [29.38552999999999, -14.688517000000004], [29.49678499999999, -14.687425000000005], [29.607944000000003, -14.682693], [29.718887999999993, -14.674327000000005], [29.829499999999996, -14.662334999999999], [29.939660000000003, -14.646730000000005], [30.024434000000014, -14.631878], [30.019721000000004, -14.641596000000007], [29.95554899999999, -14.772441999999998], [29.890806999999995, -14.903006000000005], [29.825495999999987, -15.033287000000001], [29.75961699999999, -15.163281999999995], [29.693172000000004, -15.292987999999994], [29.626160999999996, -15.422403000000003], [29.55858699999999, -15.551524], [29.490449000000012, -15.680350000000004], [29.421750000000003, -15.808875999999998], [29.352490999999986, -15.937101999999996], [29.28267299999999, -16.065023999999994], [29.212298000000004, -16.192640999999995], [29.141366000000005, -16.319948999999994], [29.069880000000012, -16.446945999999997], [28.997839999999997, -16.573631000000006], [28.92524800000001, -16.700000000000003], [28.852104999999995, -16.826049999999995], [28.778413, -16.951780999999997], [28.704173999999995, -17.077189000000004], [28.62938700000001, -17.202270999999996], [18.514813000000004, -11.124821999999995], [18.563177999999994, -11.043930000000003], [18.611188999999996, -10.962828000000002], [18.658845999999997, -10.881517000000002], [18.706148, -10.799999999999997], [18.753094000000004, -10.718276000000003], [18.799683, -10.636347999999998], [18.845912999999996, -10.554218000000006], [18.891785, -10.471886999999995], [18.937297, -10.389357000000004], [18.982449000000003, -10.306629000000001], [19.027238999999994, -10.223703999999998], [19.071668000000003, -10.140585000000002], [19.115731999999994, -10.057272999999995], [19.159433000000007, -9.973770000000002], [19.20277, -9.890075999999993], [19.245739999999998, -9.806194000000005], [19.288345000000007, -9.722126000000003], [19.330582000000007, -9.637872000000002], [19.372450999999998, -9.553434999999993], [19.413950999999997, -9.468816000000004], [19.455081000000007, -9.384017], [19.495841999999996, -9.299038999999993], [19.536231, -9.213883999999993], [19.576248000000007, -9.128553999999994], [19.615892000000002, -9.043049999999994], [19.655163, -8.957374000000002], [19.694059999999993, -8.871527], [19.732580999999996, -8.785511], [19.770726999999994, -8.699327999999994], [19.808497000000003, -8.612978999999996], [19.845889999999997, -8.526466999999997], [19.882903999999996, -8.439791999999997], [19.919539999999998, -8.352956000000006], [19.955797000000004, -8.265962000000002], [19.991674000000003, -8.178809999999999], [20.027170999999996, -8.091502000000006], [20.062286, -8.004040000000003], [20.097019000000003, -7.916426000000001], [20.131369000000007, -7.828660999999997], [20.165336999999994, -7.740746999999999], [20.19892, -7.652686000000003], [20.232118999999997, -7.564479000000006], [20.264932, -7.476128000000003], [20.297359999999998, -7.387635000000003], [20.329401000000004, -7.299001000000004], [20.361056000000005, -7.210228000000001], [20.392321999999993, -7.121317000000005], [20.423201000000006, -7.032272000000006], [20.453689999999995, -6.943091999999993], [20.48379, -6.85378], [20.513501000000005, -6.764337999999995], [20.542820000000006, -6.674767000000003], [20.571748999999997, -6.585068000000007], [20.600285999999997, -6.495244999999997], [20.628429999999994, -6.405298000000002], [20.656182, -6.315228000000005], [20.683541000000005, -6.225038999999995], [20.710505999999995, -6.134731000000002], [20.737076000000002, -6.044306000000006], [20.763251999999994, -5.953766000000002], [20.789033000000003, -5.8631129999999985], [20.814417000000006, -5.772347999999994], [20.839405999999997, -5.681473999999994], [20.863996999999998, -5.590491], [20.888192000000004, -5.4994020000000035], [20.911989000000005, -5.408208000000002], [20.935387000000006, -5.316911000000005], [20.958387000000002, -5.225511999999995], [20.980987999999996, -5.134015000000005], [21.003190000000004, -5.042418999999995], [21.024991, -4.950727999999998], [21.046392999999995, -4.858941999999999], [21.067393999999993, -4.767064000000005], [21.087992999999997, -4.675094999999999], [21.108191000000005, -4.5830370000000045], [21.127988000000002, -4.490892000000002], [21.147381999999993, -4.398661000000004], [21.166372999999993, -4.306347000000002], [21.184962, -4.213949999999997], [21.203147, -4.121474000000006], [21.220928, -4.028919000000002], [21.238305999999994, -3.936286999999993], [21.255279, -3.843580000000003], [21.271846999999994, -3.750799999999998], [21.28801, -3.657949000000002], [21.303768000000005, -3.565027999999998], [21.319120999999996, -3.472038999999995], [21.334068000000002, -3.3789840000000027], [21.348608, -3.285865000000001], [21.362741999999997, -3.1926830000000024], [21.376469, -3.0994400000000013], [21.389790000000005, -3.006138000000007], [21.402703000000002, -2.912779999999998], [21.415209000000004, -2.819365000000005], [21.427306, -2.7258970000000033], [21.438996000000003, -2.6323770000000053], [21.450277999999997, -2.5388070000000056], [21.461152, -2.445188999999999], [21.471615999999997, -2.3515239999999977], [21.481672000000003, -2.257813999999996], [21.491319000000004, -2.1640620000000013], [21.500557, -2.0702679999999987], [21.509386000000006, -1.9764339999999976], [21.517804999999996, -1.8825640000000021], [21.525813999999997, -1.7886570000000006], [21.533413999999993, -1.6947159999999997], [21.540603000000004, -1.6007429999999943], [21.547382999999996, -1.506738999999996], [21.553752000000003, -1.4127069999999975], [21.559710999999993, -1.318647999999996], [21.565259999999995, -1.2245640000000009], [21.570397, -1.1304559999999952], [21.537667999999996, -1.0345279999999946], [21.504512000000005, -0.9389070000000004], [21.470933000000002, -0.8435949999999934], [21.436932999999996, -0.7485939999999971], [21.402513, -0.6539049999999946], [21.367675000000006, -0.5595320000000044], [21.332421999999994, -0.46547499999999786], [21.296755000000005, -0.3717359999999985], [21.298175, -0.27880799999999795], [21.299188, -0.1858749999999958], [21.299796999999998, -0.09293800000000374], [21.299999999999997, 0.0], [21.299796999999998, 0.09293900000000122], [21.299188, 0.18587599999999327], [21.298175, 0.2788089999999954], [21.296755000000005, 0.371736999999996], [21.294931000000005, 0.464658], [21.292700999999994, 0.5575690000000009], [21.290065, 0.650470999999996], [21.287024000000002, 0.7433599999999956], [21.283578000000006, 0.8362350000000021], [21.279726999999994, 0.9290929999999946], [21.27547, 1.0219349999999991], [21.270809, 1.1147559999999999], [21.265742000000003, 1.2075569999999942], [21.260271000000003, 1.3003340000000065], [21.254395000000002, 1.3930869999999942], [21.248114, 1.4858129999999932], [21.241428, 1.578511000000006], [21.234339000000006, 1.671178999999995], [21.226844999999997, 1.763814999999994], [21.218947, 1.856418000000005], [21.210644000000002, 1.9489849999999933], [21.201938999999996, 2.041515000000004], [21.192829000000003, 2.1340059999999994], [21.183316000000005, 2.2264569999999964], [21.1734, 2.3188650000000024], [21.163079999999994, 2.411229000000006], [21.152358000000007, 2.5035469999999975], [21.141233, 2.595817999999994], [21.129705, 2.6880390000000034], [21.117774999999995, 2.780208000000002], [21.105442999999994, 2.8723250000000036], [21.092709, 2.9643879999999996], [21.079573999999994, 3.056393], [21.066036999999994, 3.148341000000002], [21.052099999999996, 3.2402289999999994], [21.037761000000003, 3.332054999999997], [21.023021999999997, 3.4238169999999997], [21.007883000000007, 3.5155149999999935], [20.992344000000003, 3.6071450000000027], [20.976405, 3.698706999999999], [20.960065999999998, 3.7901980000000037], [20.943329000000006, 3.8816170000000056], [20.926192999999998, 3.9729619999999954], [20.908659, 4.064232000000004], [20.890726, 4.1554239999999965], [20.872395999999995, 4.246538000000001], [20.853668, 4.3375699999999995], [20.834542999999996, 4.428520000000006], [20.815022, 4.519385], [20.795103999999995, 4.6101639999999975], [20.774790999999993, 4.700856000000002], [20.754081999999997, 4.791458000000006], [20.732978000000003, 4.881968999999998], [20.711478999999997, 4.972386999999998], [20.689586000000006, 5.062709999999996], [20.667298000000002, 5.152936999999994], [20.644617999999994, 5.243065999999999], [20.621544, 5.333095], [20.598078, 5.423022000000003], [20.574219999999997, 5.512845999999996], [20.549969000000004, 5.6025649999999985], [20.525328000000002, 5.692177999999998], [20.500296000000006, 5.7816820000000035], [20.474874, 5.871076000000002], [20.449061, 5.960357999999999], [20.42286, 6.049526999999998], [20.396269000000004, 6.138581000000002], [20.369291000000004, 6.227518000000003], [20.341924000000006, 6.316336000000007], [20.314171, 6.405034000000001], [20.286029999999997, 6.493610000000004], [20.257503, 6.582061999999993], [20.228590999999994, 6.670389999999998], [20.199292999999997, 6.758589999999998], [20.169611000000003, 6.846660999999997], [20.139545, 6.934601999999998], [20.144498999999996, 7.034774999999996], [20.148961, 7.1351219999999955], [20.152930999999995, 7.235641999999999], [20.156406000000004, 7.336332999999996], [20.159385999999998, 7.4371909999999986], [20.161868, 7.538213999999996], [20.163852000000006, 7.6394010000000065], [20.165336999999994, 7.740747999999996], [20.131369000000007, 7.828661999999994], [20.097019000000003, 7.916426999999999], [20.062286, 8.004041], [20.027170999999996, 8.091503000000003], [19.991674000000003, 8.178810999999996], [19.955797000000004, 8.265963], [19.919539999999998, 8.352957000000004], [19.882903999999996, 8.439792999999995], [19.845889999999997, 8.526467999999994], [19.808497000000003, 8.612979999999993], [19.770726999999994, 8.699329000000006], [19.732580999999996, 8.785511999999997], [19.694059999999993, 8.871527999999998], [19.655163, 8.957374999999999], [19.615892000000002, 9.043051000000006], [19.576248000000007, 9.128555000000006], [19.536231, 9.213885000000005], [19.495841999999996, 9.299040000000005], [19.455081000000007, 9.384017999999998], [19.413950999999997, 9.468817000000001], [19.372450999999998, 9.553436000000005], [19.330582000000007, 9.637872999999999], [19.288345000000007, 9.722127], [19.245739999999998, 9.806195000000002], [19.20277, 9.890077000000005], [19.159433000000007, 9.973771], [19.115731999999994, 10.057274000000007], [19.071668000000003, 10.140585999999999], [19.027238999999994, 10.223704999999995], [18.982449000000003, 10.306629999999998], [18.937297, 10.389358000000001], [18.891785, 10.471888000000007], [18.845912999999996, 10.554219000000003], [18.799683, 10.636348999999996], [18.753094000000004, 10.718277], [18.706148, 10.799999999999997], [18.658845999999997, 10.881518], [18.611188999999996, 10.962829], [18.563177999999994, 11.043931], [18.514813000000004, 11.124823000000006], [18.466095999999993, 11.205502999999993], [18.417027000000004, 11.285968999999994], [18.367608000000004, 11.366220999999996], [18.317837999999995, 11.446257000000003], [18.267719999999997, 11.526073999999994], [18.217254999999994, 11.605671999999998], [18.166442000000004, 11.685049000000006], [18.115284000000003, 11.764204000000007], [18.063779999999994, 11.843134000000006], [18.011933, 11.921839000000006], [17.959743000000003, 12.000317999999993], [17.907211000000004, 12.078567000000007], [17.854338, 12.156587000000002], [17.801125, 12.234375], [17.747573000000003, 12.311931000000001], [17.693684000000005, 12.389251999999999], [17.639456999999993, 12.466336999999996], [17.584895000000003, 12.543183999999997], [17.529998000000006, 12.619793000000001], [17.474767, 12.696162000000001], [17.419202999999996, 12.772289], [17.363308000000004, 12.848173000000003], [17.307081999999994, 12.923811999999998], [17.250527000000005, 12.999205000000003], [17.193642999999994, 13.074350999999993], [17.136432, 13.149247000000003], [17.078894000000005, 13.223894000000001], [17.021032000000005, 13.298288], [16.962845, 13.372429999999994], [16.904336, 13.446316999999993], [16.845504000000005, 13.519947000000002], [16.786351999999994, 13.593321000000003], [16.726881000000006, 13.666436000000004], [16.667091, 13.739289999999997], [16.606983, 13.811882999999995], [16.546559000000002, 13.884213000000003], [16.485821, 13.956277999999998], [16.424768, 14.028077999999994], [16.363403000000005, 14.099610999999996], [16.301726000000002, 14.170876000000007], [16.239739, 14.241870000000006], [16.177442999999997, 14.312594000000004], [16.114839000000003, 14.383043999999998], [16.051928000000004, 14.453221999999997], [15.988710999999995, 14.523123999999996], [15.92519, 14.592748999999998], [15.861366000000004, 14.662097000000003], [15.797239000000005, 14.731165000000004], [15.732811999999996, 14.799953000000002], [15.668086000000002, 14.868459000000001], [15.603060999999997, 14.936683000000002], [15.537739000000002, 15.004621], [15.472121000000001, 15.072273999999993], [15.406209000000004, 15.139640999999997], [15.340003999999993, 15.206719000000007], [15.273505999999998, 15.273506999999995], [15.206717999999995, 15.340005000000005], [15.13964, 15.406210000000002], [15.072272999999996, 15.472121999999999], [15.004620000000003, 15.53774], [14.936682000000005, 15.603061999999994], [14.868458000000004, 15.668087], [14.799952000000005, 15.732812999999993], [14.731164000000007, 15.797240000000002], [14.662096000000005, 15.861367000000001], [14.592748, 15.925190999999998], [14.523122999999998, 15.988712000000007], [14.453221, 16.051929], [14.383043, 16.11484], [14.312593000000007, 16.177443999999994], [14.241868999999994, 16.239739999999998], [14.170874999999995, 16.301727], [21.912370999999993, 25.207300000000004]];
encoder_native_mounts = [[26.675900999999996, 14.786693999999997], [29.939628999999996, -5.819674000000006]];

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
encoder_pcb_span = len(encoder_native_boundary)>0 ? 80 : 160;
encoder_pcb_mount_r = encoder_outer_track_r+1;
encoder_pcb_mount_angles = [encoder_sensor_angle-68,encoder_sensor_angle+68];
encoder_pcb_clearance = 0.25;
encoder_body_bolt_keepout = 4.5;
encoder_rear_inner_r = bearing_outer/2+1;
encoder_rear_outer_r = D_out/2-1.3;
encoder_rear_depth = len(encoder_native_boundary)>0 ? 0.25 : 2.3;
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
    if(len(encoder_native_mounts)>0)
        for(p=encoder_native_mounts) translate([p[0],p[1],0]) children();
    else for(a=encoder_pcb_mount_angles)
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
    if(len(encoder_native_boundary)>0) offset(delta=clearance) polygon(encoder_native_boundary);
    else offset(delta=clearance) difference() {
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
// Print flat half rings: one identical half per clamp half.
module encoder_magnet_ring_half_for_print() {
    translate([0,0,-encoder_clamp_body_h]) encoder_magnet_carrier_ring(full_circle=false);
}
module encoder_magnet_ring_for_print() {
    translate([-(D_out/2+3), 0, 0]) encoder_magnet_ring_half_for_print();
    translate([ D_out/2+3, 0, 0]) encoder_magnet_ring_half_for_print();
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
        if(len(encoder_native_boundary)>0) encoder_pcb_outline(encoder_pcb_clearance);
        else intersection() {
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
module encoder_native_front_clearances() {
    for(c=encoder_native_components) if(c[3] && c[4][2]>1)
        rotate([0,0,c[1]]) translate([c[0],0,encoder_lid_base_z-eps])
            rotate([0,0,c[2]-c[1]])
                translate([-c[4][0]/2-.25,-c[4][1]/2-.25,0])
                    cube([c[4][0]+.5,c[4][1]+.5,
                        encoder_pcb_top_z+c[4][2]+.2-encoder_lid_base_z+eps]);
}
module encoder_wire_channel() {
    if(len(encoder_native_boundary)>0)
        rotate([0,0,encoder_sensor_angle+11])
            translate([31.3,-2.8,encoder_pcb_top_z-.1]) cube([3.7+eps,5.6,1.5]);
    else rotate([0,0,encoder_sensor_angle+59])
        translate([encoder_pcb_outer_r-1.4,-2,encoder_pcb_bottom_z-1.2]) cube([9,4,1.1]);
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
        encoder_mount_positions() translate([0,0,encoder_pcb_bottom_z-2.5]) cylinder(d=1.6,h=2.5+eps);
        encoder_body_bolt_positions() translate([0,0,cap_thickness-eps]) cylinder(d=3.2,h=5);
        encoder_wire_channel();
    }
}
module lid_encoder() {
    encoder_validate() difference() {
        translate([0,0,encoder_lid_base_z])
            encoder_annulus(D_out/2,bearing_inner/2+0.6,encoder_lid_top_z-encoder_lid_base_z);
        translate([0,0,encoder_lid_base_z-eps])
            linear_extrude(height=encoder_main_ceiling_z-encoder_lid_base_z+eps)
                encoder_pcb_outline(encoder_pcb_clearance);
        encoder_native_front_clearances();
        if(len(encoder_native_boundary)>0) encoder_wire_channel();
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
module encoder_lid_for_print() {
    translate([0,0,encoder_lid_top_z]) rotate([180,0,0]) lid_encoder();
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
    else if(part=="encoder_lid") encoder_lid_for_print();
    else if(part=="encoder_print") {
        translate([-D_out/2-4,0,0]) cap_encoder();
        translate([D_out/2+4,0,0]) encoder_lid_for_print();
    }
    else if(part=="encoder_clamp") connector_clamp_encoder(show_magnets=true);
    else if(part=="encoder_clamp_half") connector_clamp_encoder_body_half();
    else if(part=="encoder_magnet_ring") encoder_magnet_ring_for_print();
    else if(part=="encoder_clamp_print") {
        translate([-D_out/2-4,0,0]) encoder_clamp_body_for_print();
        translate([D_out/2+4,0,0]) encoder_clamp_body_for_print();
        translate([0,encoder_clamp_body_h+7,0]) encoder_magnet_ring_for_print();
    }
    else if(part=="encoder_connector") reducer_connector_encoder();
    else if(part=="encoder_load_connector") load_connector_encoder();
    else if(part=="encoder_pcb") encoder_pcb_bare();
    else assert(false,str("Неизвестный вариант: ",part));
}

// Выбор можно поменять через -D 'generated_part="encoder_cap"' в OpenSCAD.
generated_part = "encoder_assembly";
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
        //translate([0, 0, -mc_total_height-1]) motor_cover(); // кожух снизу
        //translate([0,D_out/2+8+zazor,(h_reducer+cap_thickness)/2]) rotate([90,45/2,0]) reducer_connector();
        //translate([0,0,h_reducer+zazor+cap_thickness+6.5]) rotate([180,0,0])reducer_connector();
        //rotate([0,0,-135/2+18]) translate([0,0,h_reducer+2*zazor+cap_thickness+8]) rotate([180,0,0]) shoulder_horn();
        //translate([0,0,h_reducer+cap_thickness+2*zazor]) shoulder_top();
        //color("gray") translate([0, 0,ecc_shaft_h1 + ecc_spacer_h+separator_h+5 +26.5]) bearing_simple(25,37,7);
        //translate([-25,65,h_reducer+cap_thickness+2*zazor])hip();
            leg();
    }
// Куб-«нож», отсекающий правую половину (x > 0)
//    translate([0, -100, -100]) 
//        cube([100, 200, 200]);
}
