import numpy as np
import sys
import os
import math

def prompt_value(prompt, default, value_type=float):
    user_input = input(f"{prompt} (по умолчанию: {default}): ")
    if user_input.strip() == "":
        return default
    try:
        return value_type(user_input)
    except ValueError:
        print("Ошибка: некорректное значение. Используем значение по умолчанию.")
        return default

# === Ввод параметров ===
RESOLUTION = prompt_value("Количество точек построения профиля жесткого колеса", 600, int)
i = prompt_value("Передаточное число", 19, int)
d_roller = prompt_value("Диаметр роликов (мм)", 4.0)
h_roller = prompt_value("Высота роликов (мм)", 5.0)
Rout = prompt_value("Внешний радиус впадин жесткого колеса (мм)", 29.0)
D = prompt_value("Внешний диаметр редуктора (мм)", 70.0)
u = 1

# === Расчёты ===
e = 0.2 * d_roller
zg = (i + 1) * u
z_rollers = i
Rin = Rout - 2 * e
r_roller = d_roller / 2
rd = Rin + e - d_roller
hc = 2.2 * e  # толщина сепаратора (для радиусов)

# Радиусы сепаратора
Rsep_m = rd + r_roller
Rsep_out = Rsep_m + hc / 2
Rsep_in = Rsep_m - hc / 2

# Высоты деталей
separator_h = h_roller + 4          # высота сепаратора
eccentric_h = h_roller + 2          # высота эксцентрика

# === Параметры вала эксцентрика ===
ecc_shaft_h1 = 5.0    # основание под 6803ZZ в корпусе (ширина подшипника)
ecc_spacer_h = 2.5    # проставка
ecc_shaft_h2 = 6.0    # эксцентриковая ступень под 6803ZZ в ECC
ecc_pin_h = 6.0       # шип под 688ZZ в сепараторе
eccentricity = e

# === Параметры защитного кожуха мотора ===
mc_motor_plate_d = 50.0   # диаметр площадки под двигатель
mc_base_thickness = 4.0   # толщина нижней плиты
mc_encoder_hole_d = 10.0  # центральное отверстие под магнит
mc_motor_hole_1 = 16.0    # расстояние между первой парой отверстий
mc_motor_hole_2 = 19.0    # расстояние между второй парой отверстий
mc_nut_pad_radius = 24.0  # радиус закладных площадок
mc_nut_pad_d = 6.0        # диаметр площадки под гайку
mc_nut_pad_h = 3.0        # высота выступа площадки
mc_ring_width = 4.0       # ширина кольца
mc_ring_height = 5.0      # высота кольца
mc_countersink_d = 6.0    # диаметр потайного отверстия
mc_countersink_h = 2.0    # глубина потайного отверстия

# Общая высота корпуса с учётом вала
h_reducer = eccentric_h + 5 + 1 + 2.5

# === Выбор подшипника для сепаратора ===
if 2 * Rsep_out < 80:
    bearing_name = "6808-2RS"
    bearing_inner = 40.0
    bearing_outer = 52.0
    bearing_width = 7.0
    flange_extra = 9.5
    cut_z_offset = 11.0
    chamfer_z_offset = 11.5
else:
    bearing_name = "6810-2RS"
    bearing_inner = 50.0
    bearing_outer = 65.0   # добавлено
    bearing_width = 7.0
    flange_extra = 9.5
    cut_z_offset = 11.0
    chamfer_z_offset = 11.5

# Толщина крышки
cap_thickness = bearing_width + 1 + 3  # подшипник + запас + возвышение

# === Вычисляем параметры бокового крепления ===
# Расстояние от центра до боковой поверхности
bracing_offset_y = D / 2 - 6  # 29 при диаметре 70
# Вертикальное смещение опор
bracing_offset_z =  D / 4  # 17.5 при диаметре 70
# Смещение по оси X для опор
bracing_offset_x = 2.25  # 2.25 при диаметре 70 и 90

# === Определение количества отверстий по диаметру ===
if D <= 60:
    n_holes = 4
elif D < 90:
    n_holes = 6
else:
    n_holes = 8

print("\nОсновные параметры ВПТК:")
print(f"- Передаточное число: {i}")
print(f"- Эксцентриситет: {e:.3f} мм")
print(f"- Радиус эксцентрика: {rd:.3f} мм")
print(f"- Внешний радиус впадин: {Rout} мм")
print(f"- Внутренний радиус: {Rin} мм")
print(f"- Число впадин: {zg}")
print(f"- Число роликов: {z_rollers}")
print(f"- Диаметр роликов: {d_roller} мм")
print(f"- Высота роликов: {h_roller} мм")
print(f"- Толщина сепаратора (расчётная): {hc:.3f} мм")
print(f"- Высота сепаратора: {separator_h:.3f} мм")
print(f"- Высота эксцентрика: {eccentric_h:.3f} мм")
print(f"- Высота корпуса редуктора: {h_reducer:.3f} мм")
print(f"- Подшипник на сепараторе: {bearing_name} (Øвнеш = {bearing_outer} мм)")
print(f"- Толщина крышки редуктора: {cap_thickness:.1f} мм")
print(f"- Параметры бокового крепления: смещение Y={bracing_offset_y:.1f} мм, смещение Z={bracing_offset_z:.1f} мм")

# Проверка геометрии
if Rin <= (1.03 * d_roller) / np.sin(np.pi / zg):
    print("Ошибка: Внутренний радиус впадин жесткого колеса Rin({0}мм) должен быть больше: {1}мм. Увеличьте Rout или уменьшите "
          "передаточное число (i)!".format(Rin, (1.03 * d_roller) / np.sin(np.pi / zg)))
    sys.exit(1)

# === Генерация профиля жёсткого колеса ===
theta = np.linspace(0, 2 * np.pi, RESOLUTION, endpoint=False)
S = np.sqrt((r_roller + rd) ** 2 - (e * np.sin(zg * theta)) ** 2)
l = e * np.cos(zg * theta) + S
Xi = np.arctan2(e * zg * np.sin(zg * theta), S)
x_rigid = l * np.sin(theta) + r_roller * np.sin(theta + Xi)
y_rigid = l * np.cos(theta) + r_roller * np.cos(theta + Xi)

# === Минимальная толщина стенки ===
R_out = D / 2
r_rigid = np.sqrt(x_rigid**2 + y_rigid**2)
min_thickness = np.min(R_out - r_rigid)

# === Генерация и поворот основных отверстий ===
angle_step = 2 * np.pi / n_holes
initial_angles = np.linspace(0, 2*np.pi - angle_step, n_holes)
initial_x = [R_out * 0.8 * np.cos(a) for a in initial_angles]
initial_y = [R_out * 0.8 * np.sin(a) for a in initial_angles]

# Поиск наилучшего угла чтобы расположить отверстия в широких местах лепестков
best_angle = 0
min_total_dist = float('inf')
for deg in range(0, 360, 1):
    angle_rad = np.deg2rad(deg)
    rotated_x = []
    rotated_y = []
    for i in range(n_holes):
        x = initial_x[i]
        y = initial_y[i]
        x_rot = x * np.cos(angle_rad) - y * np.sin(angle_rad)
        y_rot = x * np.sin(angle_rad) + y * np.cos(angle_rad)
        rotated_x.append(x_rot)
        rotated_y.append(y_rot)

    total_dist = 0
    r_rigid_orig = np.sqrt(x_rigid**2 + y_rigid**2)
    valleys_orig = []
    for j in range(1, len(r_rigid_orig)-1):
        if r_rigid_orig[j] < r_rigid_orig[j-1] and r_rigid_orig[j] < r_rigid_orig[j+1]:
            valleys_orig.append(j)
    valley_coords = np.array([(x_rigid[i], y_rigid[i]) for i in valleys_orig])

    for i in range(n_holes):
        point = np.array([rotated_x[i], rotated_y[i]])
        if len(valley_coords) > 0:
            dists = np.linalg.norm(valley_coords - point, axis=1)
            total_dist += np.min(dists)
        else:
            total_dist += 1e6

    if total_dist < min_total_dist:
        min_total_dist = total_dist
        best_angle = angle_rad

hole_x = []
hole_y = []
for i in range(n_holes):
    x = initial_x[i]
    y = initial_y[i]
    x_rot = x * np.cos(best_angle) - y * np.sin(best_angle)
    y_rot = x * np.sin(best_angle) + y * np.cos(best_angle)
    r_current = np.sqrt(x_rot**2 + y_rot**2)
    if r_current > 0:
        target_radius = R_out - min_thickness / 2
        scale = target_radius / r_current
        hole_x.append(x_rot * scale)
        hole_y.append(y_rot * scale)
    else:
        angle = best_angle + 2 * np.pi * i / n_holes
        hole_x.append((R_out - min_thickness / 2) * np.cos(angle))
        hole_y.append((R_out - min_thickness / 2) * np.sin(angle))

# === Отверстия B: 4 симметричных ===
base_motor_angles_deg = np.array([0.0, 90.0, 180.0, 270.0])
motor_angles_deg = (base_motor_angles_deg + np.degrees(best_angle)) % 360
# Проверяем, есть ли хотя бы одно отверстие B, слишком близкое к любому отверстию A
angles_A_deg = np.degrees(np.arctan2(hole_y, hole_x)) % 360
needs_shift = False
for ang_B in motor_angles_deg:
    min_diff = np.min(np.abs((angles_A_deg - ang_B + 180) % 360 - 180))
    if min_diff < 10.0:
        needs_shift = True
        break
# Если нужно — смещаем ВСЕ отверстия B на +15°
if needs_shift:
    adjusted_motor_angles_deg = (motor_angles_deg + 15.0) % 360
else:
    adjusted_motor_angles_deg = motor_angles_deg

motor_radius = R_out - 3.0
motor_x = [motor_radius * np.cos(np.deg2rad(a)) for a in adjusted_motor_angles_deg]
motor_y = [motor_radius * np.sin(np.deg2rad(a)) for a in adjusted_motor_angles_deg]

# Расчет расстояний между отверстиями в боковом креплении
side_short = (bearing_inner/2-4) * math.sqrt(2 - math.sqrt(2))
side_long = (bearing_inner/2-4) * math.sqrt(2 + math.sqrt(2))

# === СПИСОК ДЕТАЛЕЙ, ОТВЕРСТИЙ, БОЛТОВ И ПОДШИПНИКОВ ===
print("\n=== СПИСОК ДЕТАЛЕЙ ===")
PARTS = {
    "HW": "Жёсткое колесо (корпус редуктора)",
    "SEP": "Сепаратор",
    "ROL": "Ролики",
    "ECC": "Эксцентрик",
    "MC": "Защитный кожух мотора",
    "CAP": "Крышка редуктора",
    "ECC_SHAFT": "Вал эксцентрика",
    "HW_BRACE": "Корпус с боковым креплением",
    "CAP_BRACE": "Крышка с боковым креплением"
}
for code, name in PARTS.items():
    print(f"- {code}: {name}")

print("\n=== ОТВЕРСТИЯ В ДЕТАЛИ HW ===")
for i in range(n_holes):
    print(f"- A{i+1}: Крепёжное отверстие корпуса (M3), x={hole_x[i]:.2f}, y={hole_y[i]:.2f}")
for i in range(4):
    print(f"- B{i+1}: Отверстие под кожух мотора (M3), x={motor_x[i]:.2f}, y={motor_y[i]:.2f}")

print("\n=== КРЕПЁЖ И ПОДШИПНИКИ ===")
print("- Винты M3×10 мм: 4 шт. (для кожуха мотора)")
print("- Винты M3×15 мм: {} шт. (для корпуса)".format(n_holes))
print("- Гайки M3: {} шт.".format(n_holes + 4))
print("- Подшипники 6803ZZ (17×26×5 мм): 2 шт. (в корпусе и эксцентрике)")
print("- Подшипник 688ZZ (8×16×5 мм): 1 шт. (в сепараторе)")
print(f"- Подшипник {bearing_name}: 1 шт. (на сепараторе)")

# === Форматирование точек для OpenSCAD (по 5 в строке) ===
def format_points(x, y):
    points = [f"[{x[i]:.5f}, {y[i]:.5f}]" for i in range(len(x))]
    lines = []
    for i in range(0, len(points), 5):
        line = ", ".join(points[i:i+5])
        lines.append(line)
    return ",\n        ".join(lines)

rigid_points_str = format_points(x_rigid, y_rigid)

# Параметры потайных отверстий
countersink_dia = 6.0
countersink_depth = 2.0

# Общая высота кожуха мотора
mc_total_height = 23.5 + mc_base_thickness

# === Генерация OpenSCAD-кода ===
openscad_code = f"""// ВПТК редуктор с роликами (для 3D-печати)
$fn = 60;
// Параметры
d_roller = {d_roller:.3f};
h_roller = {h_roller:.3f};
separator_h = {separator_h:.3f};
eccentric_h = {eccentric_h:.3f};
Rsep_m = {Rsep_m:.3f};
Rsep_out = {Rsep_out:.3f};
Rsep_in = {Rsep_in:.3f};
D_out = {D:.3f};
h_reducer = {h_reducer:.3f};
bearing_inner = {bearing_inner:.1f};
// Высота профильного выреза
h_cut = h_roller + 5;
cap_thickness = {cap_thickness:.1f};
eccentricity = {eccentricity:.3f};
// --- Параметры вала эксцентрика ---
ecc_shaft_h1 = {ecc_shaft_h1:.3f};   // основание под 6803ZZ
ecc_spacer_h = {ecc_spacer_h:.3f};   // проставка
ecc_shaft_h2 = {ecc_shaft_h2:.3f};   // эксцентриковая ступень
ecc_pin_h = {ecc_pin_h:.3f};      // шип под 688ZZ
// --- Параметры кожуха мотора ---
mc_motor_plate_d = {mc_motor_plate_d:.1f};
mc_base_thickness = {mc_base_thickness:.1f};
mc_encoder_hole_d = {mc_encoder_hole_d:.1f};
mc_motor_hole_1 = {mc_motor_hole_1:.1f};
mc_motor_hole_2 = {mc_motor_hole_2:.1f};
mc_nut_pad_radius = {mc_nut_pad_radius:.1f};
mc_nut_pad_d = {mc_nut_pad_d:.1f};
mc_nut_pad_h = {mc_nut_pad_h:.1f};
mc_total_height = {mc_total_height:.1f};
mc_ring_width = {mc_ring_width:.1f};
mc_ring_height = {mc_ring_height:.1f};
mc_countersink_d = {mc_countersink_d:.1f};
mc_countersink_h = {mc_countersink_h:.1f};
// --- Параметры бокового крепления ---
bracing_offset_y = {bracing_offset_y:.1f};  // смещение по Y
bracing_offset_z = {bracing_offset_z:.1f};  // смещение по Z
bracing_offset_x = {bracing_offset_x:.1f};  // смещение по X

// === Группа B: отверстия под кожух мотора нужны в двух функциях===
motor_angles = [{', '.join([f'{a:.1f}' for a in adjusted_motor_angles_deg])}];
motor_radius = {motor_radius:.3f};

// Расстояния между отверстиями в боковом креплении
side_short = {side_short:.3f};
side_long = {side_long:.3f};

// === Вспомогательные модули для бокового крепления ===
module oval_cone(height, bottom_width, bottom_depth, top_width, top_depth, center = false) {{
    hull() {{
        // Нижнее основание
        translate([0, 0, center ? -height/2 : 0])
        scale([bottom_width/2, bottom_depth/2, 1])
        cylinder(h = 0.1, r = 1, center = true, $fn = 64);
        
        // Верхнее основание
        translate([0, 0, center ? height/2 : height])
        scale([top_width/2, top_depth/2, 1])
        cylinder(h = 0.1, r = 1, center = true, $fn = 64);
    }}
}}

module oval_cone_diff_half(height, bottom_width, bottom_depth, top_width, top_depth, center = false) {{
    difference() {{ 
        cube([height, height, height], center = center);
        // Вычитаем овальный конус
        oval_cone(height, bottom_width, bottom_depth, top_width, top_depth, center = center);
        translate([0, height/4, 0]) cube([height, height/2, height], center = center);
    }}
}}

// === Корпус (жёсткое колесо) ===
module rigid_gear() {{
    difference() {{
        cylinder(h = h_reducer, r = D_out / 2, center = false);
        translate([0, 0, h_reducer - h_cut])
            linear_extrude(height = h_cut, center = false)
                polygon(points = [
                {rigid_points_str}
            ]);
        // === Группа A: основные крепёжные отверстия ===
        for (i = [0 : {n_holes - 1}]) {{
            x_hole = [{', '.join([f'{x:.5f}' for x in hole_x])}][i];
            y_hole = [{', '.join([f'{y:.5f}' for y in hole_y])}][i];
            translate([x_hole, y_hole, 0])
                cylinder(h = h_reducer, r = 1.6, center = false);
            translate([x_hole, y_hole, 0])
                cylinder(h = 3.0, r = 3.0, center = false);
        }}
        // === Группа B: крепёжные отверстия кожуха===
        for (i = [0 : 3]) {{
            angle = motor_angles[i];
            rotate([0, 0, angle])
                translate([motor_radius, 0, 0])
                    cylinder(h = 8.0, r = 1.6, center = false);
            rotate([0, 0, angle])
                translate([motor_radius, 0, 5.0])
                    cube(size = [6.0, 6.0, 3.0], center = true);
        }}
        // === Посадка подшипника 6803ZZ в корпусе ===
        cylinder(h = 1, r = 24/2, center = false);
        translate([0, 0, 1])
            cylinder(h = 5.0, r = 26.0/2, center = false);
    }}
}}

// === Корпус с боковым креплением ===
module rigid_gear_with_bracing() {{
	difference(){{
    	union() {{
        	rigid_gear();
       
        	difference(){{
            	translate([-D_out/2, 0, 0]) cube([D_out, D_out/2, h_reducer]);
            	rotate([-90, 90, 0]) 
                	translate([-cap_thickness-bracing_offset_x, -bracing_offset_y, bracing_offset_z]) 
                	oval_cone_diff_half(D_out/2, h_reducer+cap_thickness, (h_reducer+cap_thickness)/2, h_reducer+cap_thickness, (h_reducer+cap_thickness)/2, true);
            	rotate([90, 90, 0]) 
                	translate([-cap_thickness-bracing_offset_x, -bracing_offset_y, -bracing_offset_z]) 
                	oval_cone_diff_half(D_out/2, h_reducer+cap_thickness, (h_reducer+cap_thickness)/2, h_reducer+cap_thickness, (h_reducer+cap_thickness)/2, true); 
            	translate([0, 0, 0]) cylinder(h = h_reducer, r = D_out / 2);
        	}}
    	}}
        // === Группа B: крепёжные отверстия кожуха===
        // Повторно вырезаем, боковое крепление может загородить
        for (i = [0 : 3]) {{
            angle = motor_angles[i];
            rotate([0, 0, angle])
                translate([motor_radius+4, 0, 5.0])
                    cube(size = [10.0, 6.0, 3.0], center = true);
        }}
        // Посадочные места под крепеж нагрузки m3
        translate([0,D_out/2,(h_reducer+cap_thickness)/2]) rotate([90,45/2,0]) {{
            for (i = [0, 5]) {{
                angle=45*i;
                rotate([0, 0, angle]) {{
                    translate([bearing_inner/2-4, 0, 0])
                        cylinder(h = 8, r = 1.6, center = false);
                }}
            }}
        }}
        translate([side_long/2-3, D_out/2-6, side_short/2-2]) cube([6,3,side_short],center=false);
        translate([-side_long/2-3, D_out/2-6, side_short/2-2]) cube([6,3,side_short],center=false);
	}}
}}

// === Сепаратор с фланцем под подшипник ===
module separator() {{
    difference() {{
        cylinder(h = separator_h + {flange_extra}, r = Rsep_out, center = false);
        // Фланец под основной подшипник (ступенчатая посадка)
        translate([0, 0, {cut_z_offset}])
            difference() {{
                cylinder(h = {flange_extra}, r = Rsep_out, center = false);
                cylinder(h = {flange_extra}, r = bearing_inner/2 + 2, center = false);  // +2 мм зазор
            }}
        translate([0, 0, {chamfer_z_offset}])
            difference() {{
                cylinder(h = {flange_extra}, r = Rsep_out, center = false);
                cylinder(h = {flange_extra}, r = bearing_inner/2, center = false);      // точный диаметр
            }}
        // Посадочное место под мини-подшипник 688ZZ (8x16x5)
        translate([0, 0, h_roller + 3])
            cylinder(h = 5, r = 8, center = false);
        translate([0, 0, h_roller + 3 + 0.5])
            cylinder(h = 5, r = 7, center = false);
        translate([0, 0, h_roller + 3 + 1])
            cylinder(h = 5, r = 5, center = false);
        cylinder(h = separator_h - 1, r = Rsep_in, center = false);
        for (angle = [0 : 360/{z_rollers} : 359]) {{
            rotate([0, 0, angle])
                translate([Rsep_m, 0, separator_h/2])
                    rotate([0, 90, 0])
                        cube([h_roller + 0.4, d_roller + 0.4, separator_h + 1], center = true);
        }}
        // Посадочные места под крепеж нагрузки m3
        for (i = [0 : 7]) {{
            angle=45*i;
            rotate([0, 0, angle]) {{
                translate([bearing_inner/2-4, 0, 0])
                    cylinder(h = separator_h  + 9.5, r = 1.6, center = false);
                translate([bearing_inner/2-4, 0, 0])
                    cylinder(h =separator_h+2, r = 3.0, center = false);
            }}
        }}
    }}
}}

// Соединитель редукторов
module reducer_connector(fitting=true) {{
    difference() {{
        union() {{
            cylinder(h = 4, r = D_out/2-9, center = false);
            translate([0,0,4]) cylinder(h = 4, r = bearing_inner/2, center = false);
        }}
        // Посадочные места под крепеж нагрузки m3
        for (i = [0 : 7]) {{
            angle=45*i;
            rotate([0, 0, angle]) {{
                translate([bearing_inner/2-4, 0, 0])
                    cylinder(h = 8, r = 1.6, center = false);
                if(fitting){{
                    translate([bearing_inner/2-4, 0, 0])
                        cylinder(h =3, r = 3.0, center = false);
                }}
            }}
        }}
    }}
}}

// Зажим соединителей 
module connector_clamp(){{
    intersection() {{
        difference() {{
            cylinder(h = 12, r = D_out/2-2, center = false);
            translate([0, 0, 2]) cylinder(h = 8.2, r = D_out/2-8.8, center = false);
            cylinder(h = 12, r = bearing_inner/2, center = false);
            rotate([0,90,90]) translate([-6, D_out/2-5, 3]) cylinder(h = 20, r =3, center = false);
            rotate([0,90,90]) translate([-6, D_out/2-5, 0]) cylinder(h = 20, r =1.6, center = false);
            rotate([0,-90,-90]) translate([6, D_out/2-5, 3]) cylinder(h = 20, r =3, center = false);
            rotate([0,-90,-90]) translate([6, D_out/2-5, 0]) cylinder(h = 20, r =1.6, center = false);
        }}
        // Отсекаем нижнюю часть - оставляем только верх
        translate([-D_out, 0, -1])
            cube([D_out*2, D_out, 14]);
    }}
}}


// === Ролики ===
module rollers() {{
    for (i = [0 : {z_rollers - 1}]) {{
        angle = i * 360 / {z_rollers};
        rotate([0, 0, angle])
            translate([Rsep_m, 0, 0])
                cylinder(r = d_roller/2, h = h_roller, center = true);
    }}
}}

// === Эксцентрик ===
module eccentric() {{
    difference() {{
        cylinder(r = {rd:.3f}, h = eccentric_h, center = false);
        // Посадка под подшипник 6803ZZ
        cylinder(h = 1, r = 24/2, center = false);
        translate([0, 0, 1])
            cylinder(h = eccentric_h, r = 26.0/2, center = false);
    }}
}}

// === Крышка редуктора ===
module cap() {{
    difference() {{
        cylinder(h = cap_thickness, r = D_out / 2, center = false);
        // Внутреннее отверстие под подшипник
        translate([0, 0, -1])
            cylinder(h = cap_thickness, r = {bearing_outer / 2:.1f}, center = false);
        // Внутреннее отверстие под упор подшипника
        cylinder(h = cap_thickness, r = {bearing_outer / 2:.1f} -2, center = false);
        // Внутреннее отверстие под сепаратор
        cylinder(h = 3, r = Rsep_out+1, center = false);
        // Отверстия под винты (группа A)
        for (i = [0 : {n_holes - 1}]) {{
            x_hole = [{', '.join([f'{x:.5f}' for x in hole_x])}][i];
            y_hole = [{', '.join([f'{y:.5f}' for y in hole_y])}][i];
            // Сквозное отверстие
            translate([x_hole, y_hole, 0])
                cylinder(h = cap_thickness, r = 1.6, center = false);
            // Потай под шляпку M3
            translate([x_hole, y_hole, cap_thickness - {countersink_depth:.1f}])
                cylinder(h = {countersink_depth:.1f}, r = {countersink_dia / 2:.1f}, center = false);
        }}
    }}
}}

// === Крышка с боковым креплением ===
module cap_with_bracing() {{
    difference(){{
        union() {{
            cap();
            difference(){{
                translate([-D_out/2, 0, 0]) cube([D_out, D_out/2, cap_thickness]);
                rotate([-90, 90, 0]) 
                    translate([+bracing_offset_x, -bracing_offset_y, bracing_offset_z]) 
                    oval_cone_diff_half(D_out/2, h_reducer+cap_thickness, (h_reducer+cap_thickness)/2, h_reducer+cap_thickness, (h_reducer+cap_thickness)/2, true);
                rotate([90, 90, 0]) 
                    translate([+bracing_offset_x, -bracing_offset_y, -bracing_offset_z]) 
                    oval_cone_diff_half(D_out/2, h_reducer+cap_thickness, (h_reducer+cap_thickness)/2, h_reducer+cap_thickness, (h_reducer+cap_thickness)/2, true);
                cylinder(h = h_reducer, r = D_out / 2, center = false);
            }}
        }}
        translate([0,D_out/2,-2.2]) rotate([90,45/2,0]) {{
            for (i = [1, 4]) {{
                angle=45*i;
                rotate([0, 0, angle]) {{
                    translate([bearing_inner/2-4, 0, 0])
                        cylinder(h = 8, r = 1.6, center = false);
                }}
            }}
        }}
        translate([side_long/2-3, D_out/2-6, 0]) cube([6,3,side_short/2+1],center=false);
        translate([-side_long/2-3, D_out/2-6, 0]) cube([6,3,side_short/2+1],center=false);
    }}
}}

// === Вал эксцентрика ===
module eccentric_shaft() {{
    difference() {{
        union() {{
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
        }}
        cylinder(h = 2.0, r = 2.0, center = false);
        pas_angles = [0.0, 180.0];
        for (angle = pas_angles) {{
            rotate([0, 0, angle]) {{
                translate([17/2-1.65, 0, 0])
                    cylinder(h = 3, r = 3, center = false);
                translate([17/2-1.65, -3, 0])
                   cube([3,6,3]);
            }}    
        }}
    }}
}}

// === Защитный кожух мотора ===
module motor_cover() {{
    difference() {{
        union() {{
            // --- Нижняя плита ---
            cylinder(h = mc_base_thickness, r = mc_motor_plate_d / 2, center = false);
            // --- Опоры и кольцо ---
            for (angle = motor_angles) {{
                rotate([0, 0, angle]) {{
                    // Наклонные стойки
                    hull() {{
                        translate([mc_motor_plate_d/2-3, 0, 0])
                            cylinder(h = 0.1, r1 = 4, center = false);
                        translate([D_out / 2+4, 0, mc_total_height-0.1])
                            cylinder(h = 0.1, r1 = 3, center = false);
                    }}
                }}
            }}
            // --- Стойки вертикальные у отверстий B для усиления ---
            for (angle = motor_angles) {{
                rotate([0, 0, angle]) {{
                    translate([motor_radius, 0, 0])
                        cylinder(h = mc_total_height, r = 6.5, center = false);
                }}
            }}
            // --- Верхнее кольцо ---
            translate([0, 0, mc_total_height - mc_ring_height])
                difference() {{
                    cylinder(h = mc_ring_height, r = D_out / 2, center = false);
                    cylinder(h = mc_ring_height, r = D_out / 2 - mc_ring_width, center = false);
                }}
        }}
        // --- Удаление выступающих за D_out деталей ---
        difference() {{
            cylinder(h = mc_total_height, r = D_out / 2+10, center = false);
            cylinder(h = mc_total_height, r = D_out / 2, center = false);
        }}
        // --- Удаление выступающих за стойки деталей пирамидой ---
        translate([0, 0, 0])
         difference() {{
            cylinder(h = mc_total_height, r1 = mc_motor_plate_d / 2+10, r2=D_out / 2+10, center = false);
            cylinder(h = mc_total_height, r1 = mc_motor_plate_d / 2, r2=D_out / 2+3, center = false);
        }}
        // --- Закладные площадки под гайки (внутри кожуха, на верхней стороне плиты) ---
        {{
            for (angle = motor_angles) {{
                rotate([0, 0, angle+45]){{
                    translate([mc_nut_pad_radius/2, 0, mc_base_thickness-2])
                        cylinder(h = mc_nut_pad_h, r = mc_nut_pad_d / 2, center = false);
                     translate([mc_nut_pad_radius/2, 0, 0])
                        cylinder(h = mc_base_thickness, r = 1.6, center = false);
                }}
            }}   
        }}
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
        for (angle = motor_angles) {{
            rotate([0, 0, angle]) {{
                // Сквозное отверстие через кольцо и стойку под м3
                translate([motor_radius, 0, 0])
                    cylinder(h = mc_total_height + 0.1, r = 1.6, center = false);
                // Сквозное отверстие через кольцо и стойку под шляпку м3
                translate([motor_radius, 0, 0])
                    cylinder(h = mc_total_height-4, r = 3.0, center = false);
            }}
        }}
    }}
}}

module bearing_simple(inner_d, outer_d, height) {{
    // Проверка параметров
    assert(inner_d > 0, "Внутренний диаметр должен быть > 0");
    assert(outer_d > inner_d, "Внешний диаметр должен быть больше внутреннего");
    assert(height > 0, "Высота должна быть > 0");
    // Радиусы
    inner_r = inner_d / 2;
    outer_r = outer_d / 2;
        // Цельный подшипник
    difference() {{
        cylinder(r=outer_r, h=height, center=true, $fn=32);
        cylinder(r=inner_r, h=height+1, center=true, $fn=32);
    }}
}}

module cutting_wedge(angle = 135, height = 20, center = false) {{
    // Создаем область вырезания на заданный угол
    rotate([0, 0, -angle/2])
    for(i = [0:5:angle]) {{ // Шаг 5 градусов для баланса качества и скорости
        rotate([0, 0, i])
        union() {{
            translate([bearing_inner/2-4, -15/2, -height/2]) 
            cube([15,15,height]);
            
            translate([shoulder_horn_r, 0, -height/2])  
            cylinder(h = height, r = 15/2, center = false);
        }}
    }}
}}

shoulder_bearing_od=37;
shoulder_bearing_id=25.05;
shoulder_bearing_h=7;
shoulder_horn_h1=7;
shoulder_horn_h2=8;
shoulder_h=shoulder_horn_h2+shoulder_horn_h1+shoulder_bearing_h+4.5;
shoulder_horn_r = bearing_inner/2+11;

module shoulder_horn() {{
    difference() {{
        union() {{
            color("red") translate([0, 0, -shoulder_bearing_h-shoulder_horn_h2]) cylinder(h = shoulder_bearing_h+shoulder_horn_h2, r = shoulder_bearing_id/2, center = false);
            color("blue") translate([0, 0, -shoulder_bearing_h-1]) cylinder(h = 2, r1 = shoulder_bearing_id/2+2,  r2 = shoulder_bearing_id/2, center = false);

            cylinder(h = shoulder_horn_h1+1.5, r = bearing_inner/2+2, center = false);
    		color("green") translate([bearing_inner/2-4, -15/2, 0]) cube([15,15,shoulder_horn_h1]);
            color("green") translate([shoulder_horn_r, 0, -2]) cylinder(h = shoulder_horn_h1+2, r = 15/2, center = false);
        }}
        // Посадочные места под крепеж нагрузки m3
        for (i = [0 : 7]) {{
            angle=45*i;
            rotate([0, 0, angle]) {{
                translate([bearing_inner/2-4, 0, 0])
                    cylinder(h =shoulder_horn_h2+1, r = 1.6, center = false);
                translate([bearing_inner/2-4, 0, -8])
                    cylinder(h = 11, r = 3.0, center = false);
            }}
        }}
        // Посадочные места под крепеж тяги m4
        translate([bearing_inner/2+11, 0, -2.01]) {{
            cylinder(h = shoulder_horn_h1+2.01, r = 2, center = false);
            translate([0, 0, 3.7]) cylinder(h = 3.4, r = 7.66/2, center = false);
        }}
    }}
}}

module shoulder_top(){{
    union(){{
        difference() {{
            union() {{
                cylinder(h=shoulder_h, r=D_out/2 );
                translate([-25,0,0]) cube([50,80,shoulder_h]);
            }}
            translate([4.7,19,-11.5]) cube([25.01,80.01,shoulder_h]);
            translate([4.7,19,-10.5]) cube([25.01,80.01,shoulder_h/2]);
            translate([-25.01,65,14.99]) cube([50.02,15.01,shoulder_h/2]);
            translate([0, 0, -0.01])cylinder(h=shoulder_horn_h2+shoulder_horn_h1+1, r = bearing_inner/2+2 );
            rotate([0,0,6]) translate([0, 0, 6.999]) cutting_wedge(height = shoulder_horn_h2+shoulder_horn_h1+1, angle = 135);
            cylinder(h=shoulder_horn_h2+shoulder_horn_h1+shoulder_bearing_h+1, r=shoulder_bearing_od/2 );
            cylinder(h=shoulder_horn_h2+shoulder_horn_h1+shoulder_bearing_h+1.5, r=shoulder_bearing_od/2-2 );
            //отверстия под штифты диаметр 6mm длинна 36mm  
            translate([-10, 61.01, 7.5]) rotate([90,0,180]) cylinder(h=19, r=3 );
            translate([0, 46.01, 20.5]) rotate([90,0,180]) cylinder(h=19, r=3 );
            // Отверстия под винты (группа A)
            rotate([0,0,-2])
            for (i = [0 : 5]) {{
                x_hole = [{', '.join([f'{x:.5f}' for x in hole_x])}][i];
                y_hole = [{', '.join([f'{y:.5f}' for y in hole_y])}][i];
                // Сквозное отверстие
                translate([x_hole, y_hole, 0]) cylinder(h = shoulder_h+0.01, r = 1.6, center = false);
                // Потай под шляпку M3
                translate([x_hole, y_hole, shoulder_h - 3.5]) cylinder(h = 3.51, r = 3.0, center = false);
            }}
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
            
        }}
        translate([0,0,shoulder_h+7.1]) rotate([180,0,0]) reducer_connector(fitting=false);
    }}
           
}}

hips_l = 170-75;
hips_l1 = hips_l-15;

module hip() {{
    union() {{
        difference() {{
            cube([50,hips_l1,shoulder_h]);
            translate([-0.01,-0.01,-0.01]) cube([50.01,15.01,shoulder_h/2+2]);
            translate([30,-0.01,-0.01]) cube([20.01,hips_l1+0.02,shoulder_h/2+2]);
            //отверстия под штифты диаметр 6mm длинна 36mm  
            translate([15, 14.99, 7.5]) rotate([90,0,180]) cylinder(h=19, r=3 );
            translate([35, -0.01, 20.5]) rotate([90,0,180]) cylinder(h=19, r=3 );
            //Отверстия под крепеж shoulder_bottom
            translate([5, 7, -0.01]) cylinder(h =shoulder_h+0.02, r = 1.6, center = false);
            translate([5, 7, 24]) cylinder(h =3.01, r = 3.0, center = false);
            translate([25, 7, -0.01]) cylinder(h =shoulder_h+0.02, r = 1.6, center = false);     
            translate([25, 7, 24]) cylinder(h =3.01, r = 3.0, center = false);
            translate([5, hips_l1-7, -0.01]) cylinder(h =shoulder_h+0.02, r = 1.6, center = false);
            translate([5, hips_l1-7, 24]) cylinder(h =3.01, r = 3.0, center = false);
            translate([25, hips_l1-7, -0.01]) cylinder(h =shoulder_h+0.02, r = 1.6, center = false);     
            translate([25, hips_l1-7, 24]) cylinder(h =3.01, r = 3.0, center = false);
        }}
    }}
}}

module simple_control_rod(center_distance, rod_diameter, hole_diameter) {{
    plate_thickness = 2;       // Толщина пластины
    plate_diameter = hole_diameter * 3; // Диаметр круглой пластины
    
    union() {{
        // Центральная тяга (вдоль оси Z)
        cylinder(
            h = center_distance-plate_diameter+2,
            d = rod_diameter,
            center = true
        );
        
        // Верхняя лопатка (параллельно оси тяги)
        translate([0, 0, center_distance/2])
            rotate([90, 0, 0]) // Поворот на 90° чтобы пластина легла вдоль оси
            difference() {{
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
            }};
        
        // Нижняя лопатка (такая же, на другом конце)
        translate([0, 0, -center_distance/2])
            rotate([90, 0, 0])
            difference() {{
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
            }};
    }}
}}

// Модуль для соединения двух точек цилиндром
module connect_points(p1, p2, diameter = 6) {{
    hole_diameter= 4;
    plate_thickness = 2;       // Толщина пластины
    plate_diameter = hole_diameter * 3; // Диаметр круглой пластины

    vec = p2 - p1;
    mid = (p1 + p2) / 2;
    length = norm(vec);
    
    // Угол в плоскости XY
    angle = atan2(vec.y, vec.x);
    
    translate(mid)
    rotate([0, 90, angle])  // Вот это правильный порядок!
        cylinder(h = length-8, d = diameter, center = true);
    translate(p1)
    difference() {{
                cylinder( h = plate_thickness, d = plate_diameter, center = true );
                // Отверстие для оси шарнира (перпендикулярно тяге)
                cylinder( h = plate_thickness * 2, d = hole_diameter, center = true );
            }};
    translate(p2)
    difference() {{
                cylinder( h = plate_thickness, d = plate_diameter, center = true );
                // Отверстие для оси шарнира (перпендикулярно тяге)
                cylinder( h = plate_thickness * 2, d = hole_diameter, center = true );
            }};
}}


foot_r=shoulder_horn_r+15;
point_foot_center=[-10,171,0];

module foot(){{
    difference() {{
        union() {{
            cylinder( h = 28, r = 5/2, center = true );
            translate([foot_r,0,-4]) cylinder( h = 5, r = 15/2, center = false );
            cube([foot_r*2-4,15,10], center = true );
        }}
        translate([foot_r,0,-4.01]) cylinder( h = 5.02, r = 2, center = false );
    }}
}}

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


module leg(){{
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
    union() {{
        rotate([0,0,servo_angle]) translate([0,0,h_reducer+2*zazor+cap_thickness+8]) rotate([180,0,0]) shoulder_horn();
        translate([0,0,h_reducer+cap_thickness+2*zazor]) shoulder_top();
        color("gray") translate([0, 0,ecc_shaft_h1 + ecc_spacer_h+separator_h+5 +26.5]) bearing_simple(25,37,7);
        translate([-25,65,h_reducer+cap_thickness+2*zazor]) hip();
        translate([0,0,39]) connect_points(p1=point1,p2=point2);
        translate(point_foot_center) translate([0,0 ,h_reducer+cap_thickness+2*zazor+9]) rotate([0,0,angle2]) foot();
        //translate([20,61.5,h_reducer+cap_thickness+2*zazor+shoulder_horn_h2+3]) rotate([90,0,0]) simple_control_rod(center_distance=170,rod_diameter = 6,hole_diameter = 4);
   }} 
}}



// === Сборка ===
zazor=1; //отступ для раздельной печати деталей, чтобы при импорте stl можно было разделить на отделтные детали
difference() {{
    union() {{
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
    }}
// Куб-«нож», отсекающий правую половину (x > 0)
//    translate([0, -100, -100]) 
//        cube([100, 200, 200]);
}}
"""

# === Сохранение ===
os.makedirs("./output", exist_ok=True)
output_file = "./output/vptc_roller.scad"
with open(output_file, "w") as f:
    f.write(openscad_code)
print(f"\n✅ OpenSCAD-модель сохранена в: {output_file}")
