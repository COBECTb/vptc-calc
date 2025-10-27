import numpy as np
import sys
import os

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
i = prompt_value("Передаточное число", 8, int)
d_roller = prompt_value("Диаметр роликов (мм)", 7.83)
h_roller = prompt_value("Высота роликов (мм)", 6.0)
Rout = prompt_value("Внешний радиус впадин жесткого колеса (мм)", 28.0)
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
ecc_spacer_h = 1.5    # проставка
ecc_shaft_h2 = 5.0    # эксцентриковая ступень под 6803ZZ в ECC
ecc_pin_h = 5.0       # шип под 688ZZ в сепараторе
eccentricity = e

# Общая высота корпуса с учётом вала (для справки, не влияет на сборку напрямую)
h_reducer = eccentric_h + 5 + 1 + 3

# === Выбор подшипника для сепаратора ===
if 2 * Rsep_out < 50:
    bearing_name = "16005-2RS"
    bearing_inner = 25.2 # а то болтается
    bearing_outer = 47.0   # добавлено
    bearing_width = 8.0
    flange_extra = 8.5
    cut_z_offset = 12.0
    chamfer_z_offset = 12.5
else:
    bearing_name = "6810-2RS"
    bearing_inner = 50.0
    bearing_outer = 65.0   # добавлено
    bearing_width = 7.0
    flange_extra = 7.5
    cut_z_offset = 11.0
    chamfer_z_offset = 11.5

# Толщина крышки
cap_thickness = bearing_width + 1 + 2  # подшипник + запас + возвышение

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
angles_A_deg = np.degrees(np.arctan2(hole_y, hole_x)) % 360
adjusted_motor_angles_deg = []
for ang in motor_angles_deg:
    min_diff = np.min(np.abs((angles_A_deg - ang + 180) % 360 - 180))
    if min_diff < 10.0:
        ang = (ang + 15.0) % 360
    adjusted_motor_angles_deg.append(ang)
motor_radius = R_out - 3.0
motor_x = [motor_radius * np.cos(np.deg2rad(a)) for a in adjusted_motor_angles_deg]
motor_y = [motor_radius * np.sin(np.deg2rad(a)) for a in adjusted_motor_angles_deg]

# === СПИСОК ДЕТАЛЕЙ, ОТВЕРСТИЙ, БОЛТОВ И ПОДШИПНИКОВ ===
print("\n=== СПИСОК ДЕТАЛЕЙ ===")
PARTS = {
    "HW": "Жёсткое колесо (корпус редуктора)",
    "SEP": "Сепаратор",
    "ROL": "Ролики",
    "ECC": "Эксцентрик",
    "MC": "Защитный кожух мотора",
    "CAP": "Крышка редуктора",
    "ECC_SHAFT": "Вал эксцентрика"  # <-- ДОБАВЛЕНО
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
        // === Группа B: отверстия под кожух мотора ===
        motor_angles = [{', '.join([f'{a:.1f}' for a in adjusted_motor_angles_deg])}];
        motor_radius = {motor_radius:.3f};
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

// === Вал эксцентрика ===
module eccentric_shaft() {{
    union() {{
        // Основание (в подшипник корпуса)
        cylinder(h = ecc_shaft_h1, r = 17/2, center = false);
        // Проставка 2 мм
        translate([0, 0, ecc_shaft_h1])
            cylinder(h = ecc_spacer_h, r = 17/2+1, center = false);
        // Эксцентриковая ступень (в подшипник эксцентрика)
        translate([eccentricity, 0, ecc_shaft_h1 + ecc_spacer_h])
            cylinder(h = ecc_shaft_h2, r = 17/2, center = false);
        // Шип по общей оси (в подшипник сепаратора)
        translate([0, 0, ecc_shaft_h1 + ecc_spacer_h + ecc_shaft_h2])
            cylinder(h = ecc_pin_h, r = 8/2, center = false);

    }}
}}

// === Сборка ===
rigid_gear();
// translate([0, 0, h_reducer]) cap();
translate([0, 0, 0]) eccentric_shaft();
// translate([0, 0, 0]) eccentric();
// translate([0, 0, ecc_shaft_h1 + ecc_spacer_h + ecc_shaft_h2]) separator();
// translate([0, 0, ecc_shaft_h1 + ecc_spacer_h + ecc_shaft_h2]) rollers();
"""

# === Сохранение ===
os.makedirs("./output", exist_ok=True)
output_file = "./output/vptc_roller.scad"
with open(output_file, "w") as f:
    f.write(openscad_code)

print(f"\n✅ OpenSCAD-модель сохранена в: {output_file}")
