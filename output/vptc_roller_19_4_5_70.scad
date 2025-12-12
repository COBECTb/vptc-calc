// ВПТК редуктор с роликами (для 3D-печати)
$fn = 60;
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
        translate([0, height/4, 0]) cube([height, height/2, height], center = center);
    }
}

// === Корпус (жёсткое колесо) ===
module rigid_gear() {
    difference() {
        cylinder(h = h_reducer, r = D_out / 2, center = false);
        translate([0, 0, h_reducer - h_cut])
            linear_extrude(height = h_cut, center = false)
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
            translate([x_hole, y_hole, 0])
                cylinder(h = h_reducer, r = 1.6, center = false);
            translate([x_hole, y_hole, 0])
                cylinder(h = 3.0, r = 3.0, center = false);
        }
        // === Группа B: крепёжные отверстия кожуха===
        for (i = [0 : 3]) {
            angle = motor_angles[i];
            rotate([0, 0, angle])
                translate([motor_radius, 0, 0])
                    cylinder(h = 8.0, r = 1.6, center = false);
            rotate([0, 0, angle])
                translate([motor_radius, 0, 5.0])
                    cube(size = [6.0, 6.0, 3.0], center = true);
        }
        // === Посадка подшипника 6803ZZ в корпусе ===
        cylinder(h = 1, r = 24/2, center = false);
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
            	translate([0, 0, 0]) cylinder(h = h_reducer, r = D_out / 2);
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
                    translate([bearing_inner/2-4, 0, 0])
                        cylinder(h = 8, r = 1.6, center = false);
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
                cylinder(h = 9.5, r = Rsep_out, center = false);
                cylinder(h = 9.5, r = bearing_inner/2 + 2, center = false);  // +2 мм зазор
            }
        translate([0, 0, 11.5])
            difference() {
                cylinder(h = 9.5, r = Rsep_out, center = false);
                cylinder(h = 9.5, r = bearing_inner/2, center = false);      // точный диаметр
            }
        // Посадочное место под мини-подшипник 688ZZ (8x16x5)
        translate([0, 0, h_roller + 3])
            cylinder(h = 5, r = 8, center = false);
        translate([0, 0, h_roller + 3 + 0.5])
            cylinder(h = 5, r = 7, center = false);
        translate([0, 0, h_roller + 3 + 1])
            cylinder(h = 5, r = 5, center = false);
        cylinder(h = separator_h - 1, r = Rsep_in, center = false);
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
                translate([bearing_inner/2-4, 0, 0])
                    cylinder(h = separator_h  + 9.5, r = 1.6, center = false);
                translate([bearing_inner/2-4, 0, 0])
                    cylinder(h =separator_h+2, r = 3.0, center = false);
            }
        }
    }
}

// Соединитель редукторов
module reducer_connector(fitting=true,h1=4) {
    difference() {
        union() {
            cylinder(h = 4, r = D_out/2-9, center = false);
            translate([0,0,4]) cylinder(h = h1, r = bearing_inner/2, center = false);
        }
        // Посадочные места под крепеж нагрузки m3
        for (i = [0 : 7]) {
            angle=45*i;
            rotate([0, 0, angle]) {
                translate([bearing_inner/2-4, 0, 0])
                    cylinder(h = 8, r = 1.6, center = false);
                if(fitting){
                    translate([bearing_inner/2-4, 0, 0])
                        cylinder(h =3, r = 3.0, center = false);
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
            cylinder(h = 12, r = bearing_inner/2, center = false);
            rotate([0,90,90]) translate([-6, D_out/2-5, 3]) cylinder(h = 20, r =3, center = false);
            rotate([0,90,90]) translate([-6, D_out/2-5, 0]) cylinder(h = 20, r =1.6, center = false);
            rotate([0,-90,-90]) translate([6, D_out/2-5, 3]) cylinder(h = 20, r =3, center = false);
            rotate([0,-90,-90]) translate([6, D_out/2-5, 0]) cylinder(h = 20, r =1.6, center = false);
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
        cylinder(h = 1, r = 24/2, center = false);
        translate([0, 0, 1])
            cylinder(h = eccentric_h, r = 26.0/2, center = false);
    }
}

// === Крышка редуктора ===
module cap() {
    difference() {
        cylinder(h = cap_thickness, r = D_out / 2, center = false);
        // Внутреннее отверстие под подшипник
        translate([0, 0, -1])
            cylinder(h = cap_thickness, r = 26.0, center = false);
        // Внутреннее отверстие под упор подшипника
        cylinder(h = cap_thickness, r = 26.0 -2, center = false);
        // Внутреннее отверстие под сепаратор
        cylinder(h = 3, r = Rsep_out+1, center = false);
        // Отверстия под винты (группа A)
        for (i = [0 : 5]) {
            x_hole = [-29.40778, -24.48010, 4.92769, 29.40778, 24.48010, -4.92769][i];
            y_hole = [11.28859, -19.82359, -31.11218, -11.28859, 19.82359, 31.11218][i];
            // Сквозное отверстие
            translate([x_hole, y_hole, 0])
                cylinder(h = cap_thickness, r = 1.6, center = false);
            // Потай под шляпку M3
            translate([x_hole, y_hole, cap_thickness - 2.0])
                cylinder(h = 2.0, r = 3.0, center = false);
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
                cylinder(h = h_reducer, r = D_out / 2, center = false);
            }
        }
        translate([0,D_out/2,-2.2]) rotate([90,45/2,0]) {
            for (i = [1, 4]) {
                angle=45*i;
                rotate([0, 0, angle]) {
                    translate([bearing_inner/2-4, 0, 0])
                        cylinder(h = 8, r = 1.6, center = false);
                }
            }
        }
        translate([side_long/2-3, D_out/2-6, 0]) cube([6,3,side_short/2+1],center=false);
        translate([-side_long/2-3, D_out/2-6, 0]) cube([6,3,side_short/2+1],center=false);
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
        cylinder(h = 2.0, r = 2.0, center = false);
        pas_angles = [0.0, 180.0];
        for (angle = pas_angles) {
            rotate([0, 0, angle]) {
                translate([17/2-1.65, 0, 0])
                    cylinder(h = 3, r = 3, center = false);
                translate([17/2-1.65, -3, 0])
                   cube([3,6,3]);
            }    
        }
    }
}

// === Защитный кожух мотора ===
module motor_cover() {
    difference() {
        union() {
            // --- Нижняя плита ---
            cylinder(h = mc_base_thickness, r = mc_motor_plate_d / 2, center = false);
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
                    cylinder(h = mc_ring_height, r = D_out / 2, center = false);
                    cylinder(h = mc_ring_height, r = D_out / 2 - mc_ring_width, center = false);
                }
        }
        // --- Удаление выступающих за D_out деталей ---
        difference() {
            cylinder(h = mc_total_height, r = D_out / 2+10, center = false);
            cylinder(h = mc_total_height, r = D_out / 2, center = false);
        }
        // --- Удаление выступающих за стойки деталей пирамидой ---
        translate([0, 0, 0])
         difference() {
            cylinder(h = mc_total_height, r1 = mc_motor_plate_d / 2+10, r2=D_out / 2+10, center = false);
            cylinder(h = mc_total_height, r1 = mc_motor_plate_d / 2, r2=D_out / 2+3, center = false);
        }
        // --- Закладные площадки под гайки (внутри кожуха, на верхней стороне плиты) ---
        {
            for (angle = motor_angles) {
                rotate([0, 0, angle+45]){
                    translate([mc_nut_pad_radius/2, 0, mc_base_thickness-2])
                        cylinder(h = mc_nut_pad_h, r = mc_nut_pad_d / 2, center = false);
                     translate([mc_nut_pad_radius/2, 0, 0])
                        cylinder(h = mc_base_thickness, r = 1.6, center = false);
                }
            }   
        }
        // --- Отверстия в нижней плите ---
        // Центральное отверстие под магнит
        cylinder(h = mc_base_thickness + 0.1, r = mc_encoder_hole_d / 2, center = false);
        // Отверстия под крепление двигателя (по осям)
        // Пара 1: по X (16 мм)
        translate([ mc_motor_hole_1/2, 0, 0]) cylinder(h = mc_base_thickness + 0.1, r = 1.6, center = false);
        // Потайное отверстие под крепление двигателя под шляпку M3
        translate([ mc_motor_hole_1/2, 0, 0]) cylinder(h = mc_countersink_h, r1 = mc_countersink_d / 2, r2 = 1.6, center = false);
        translate([-mc_motor_hole_1/2, 0, 0]) cylinder(h = mc_base_thickness + 0.1, r = 1.6, center = false);
        // Потайное отверстие под крепление двигателя под шляпку M3
        translate([-mc_motor_hole_1/2, 0, 0]) cylinder(h = mc_countersink_h, r1 = mc_countersink_d / 2, r2 = 1.6, center = false);
        // Пара 2: по Y (19 мм)
        translate([0,  mc_motor_hole_2/2, 0]) cylinder(h = mc_base_thickness + 0.1, r = 1.6, center = false);
        // Потайное отверстие под крепление двигателя под шляпку M3
        translate([0,  mc_motor_hole_2/2, 0]) cylinder(h = mc_countersink_h, r1 = mc_countersink_d / 2, r2 = 1.6, center = false);
        translate([0, -mc_motor_hole_2/2, 0]) cylinder(h = mc_base_thickness + 0.1, r = 1.6, center = false);
        // Потайное отверстие под крепление двигателя под шляпку M3
        translate([0, -mc_motor_hole_2/2, 0]) cylinder(h = mc_countersink_h, r1 = mc_countersink_d / 2, r2 = 1.6, center = false);       
        // --- Отверстия в кольце и стойках под винты B ---
        for (angle = motor_angles) {
            rotate([0, 0, angle]) {
                // Сквозное отверстие через кольцо и стойку под м3
                translate([motor_radius, 0, 0])
                    cylinder(h = mc_total_height + 0.1, r = 1.6, center = false);
                // Сквозное отверстие через кольцо и стойку под шляпку м3
                translate([motor_radius, 0, 0])
                    cylinder(h = mc_total_height-4, r = 3.0, center = false);
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
                translate([bearing_inner/2-4, 0, 0])
                    cylinder(h =shoulder_horn_h2+1, r = 1.6, center = false);
                translate([bearing_inner/2-4, 0, -8])
                    cylinder(h = 11, r = 3.0, center = false);
            }
        }
        // Посадочные места под крепеж тяги m4
        translate([bearing_inner/2+11, 0, -2.01]) {
            cylinder(h = shoulder_horn_h1+2.01, r = 2, center = false);
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
            cylinder(h=shoulder_horn_h2+shoulder_horn_h1+shoulder_bearing_h+1, r=shoulder_bearing_od/2 );
            cylinder(h=shoulder_horn_h2+shoulder_horn_h1+shoulder_bearing_h+1.5, r=shoulder_bearing_od/2-2 );
            //отверстия под штифты диаметр 6mm длинна 36mm  
            translate([-10, 61.01, 7.5]) rotate([90,0,180]) cylinder(h=19, r=3 );
            translate([10, 46.01, 20.5]) rotate([90,0,180]) cylinder(h=19, r=3 );
            // Отверстия под винты (группа A)
            rotate([0,0,-2])
            for (i = [0 : 5]) {
                x_hole = [-29.40778, -24.48010, 4.92769, 29.40778, 24.48010, -4.92769][i];
                y_hole = [11.28859, -19.82359, -31.11218, -11.28859, 19.82359, 31.11218][i];
                // Сквозное отверстие
                translate([x_hole, y_hole, 0]) cylinder(h = shoulder_h+0.01, r = 1.6, center = false);
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
            translate([-0.01,-0.01,-0.01]) cube([50.01,15.01,shoulder_h/2+2]);
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
};


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
module shin(){
    difference() {
        union() {
            translate([0,0,-0.5]) cylinder( h = 25, r = 8/2, center = true );
            translate([0,0,-0.5]) cylinder( h = 15, r = 8/2+1, center = true );
            translate([foot_r,0,-7.5]) cylinder( h = 9.5, r = 15/2, center = false );
            difference() {
                translate([-14,0,-0.5]) cube([foot_r*2+27,15,shoulder_h/2+1], center = true );
                rotate([0,4,0]) rotate([0,90,-90]) translate([-14,13,0]) cot_surface(curve_length=15,curve_height=30);
            }
        }
        translate([foot_r,0,-8.01]) cylinder( h = 10.02, r = 2.1, center = false );
        translate([foot_r,0,-8.01]) cylinder( h = 3.4, r = 7.66/2, center = false );
        translate([-foot_r-10,0,-8.01]) cylinder( h = 15, r = 2.1, center = false );
    }
}

// соединитель для нижней части ноги
module foot_connector()
{
    difference() {
        translate([5,0,0]) cube([40,24,shoulder_h/2+7], center = true );
        translate([0,0,0]) cube([36.02,15.4,shoulder_h/2+1.4], center = true );        
        translate([0,0,0]) cylinder( h = 25, r = 2.1, center = true );
    }
    translate([74.5,1,-0.5])rotate([90,0,0]) import("/Users/sovest/Downloads/foots.stl");
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

module leg(){
    result = calculate_rigid_linkage(servo_angle, 170, shoulder_horn_r, foot_r, [0,0,0], point_foot_center);

    point1 = get_value(result, "point1");
    point2 = get_value(result, "point2");
    angle2 = get_value(result, "angle2");
    solution_exists = get_value(result, "solution_exists");
    min_possible = get_value(result, "min_possible");
    max_possible = get_value(result, "max_possible");

    echo("Точка 1: ", point1);
    echo("Точка 2: ", point2);
    echo("Угол колена: ", angle2, "° (", angle2 * 180 / 3.14159, "°)");
    echo("Длина тяги (расчетная): ", norm(point2 - point1), "мм");
    echo("Диапазон возможных длин: от ", min_possible, " до ", max_possible, "мм");
    echo("Решение существует: ", solution_exists);
    union() {
        rotate([0,0,servo_angle]) translate([0,0,h_reducer+2*zazor+cap_thickness+8]) rotate([180,0,0]) shoulder_horn();
        translate([0,0,h_reducer+cap_thickness+2*zazor]) shoulder_top();
        color("gray") translate([0, 0,ecc_shaft_h1 + ecc_spacer_h+separator_h+5 +26.5]) bearing_simple(25,37,7);
        translate([-25,65,h_reducer+cap_thickness+2*zazor]) hip();
        color("lightgray") translate(point_foot_center) translate([0,0 ,h_reducer+cap_thickness+2*zazor+17.7]) bearing_simple(8,16,5);
        color("lightgray") translate([0,0,39]) connect_points_rod(p1=point1,p2=point2);
        translate(point_foot_center) translate([0,0 ,h_reducer+cap_thickness+2*zazor+8]) rotate([0,0,angle2]) shin();
        color("gray") translate(point_foot_center) translate([0,0 ,h_reducer+cap_thickness+2*zazor-2.51]) bearing_simple(8,16,5);
        translate([-25,-32+50 ,h_reducer+1.7]) hip_top();
        translate([-55,166 ,36.5]) rotate([0,0,180]) rotate([0,0,angle2]) foot_connector();
   } 
}




// === Сборка ===
zazor=1; //отступ для раздельной печати деталей, чтобы при импорте stl можно было разделить на отделтные детали
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
        //translate([0,-47,-0.5]) rotate([0,0,-90])foot_connector();
        //rotate([0,0,90]) shin();
        //foot_connector();
         
        //shin();
        //hip();
        //hip_top();
        //shoulder_top();
        //shoulder_horn();
    }
// Куб-«нож», отсекающий правую половину (x > 0)
//    translate([0, -100, -100]) 
//        cube([100, 200, 200]);
}
