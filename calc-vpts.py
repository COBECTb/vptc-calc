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
i = prompt_value("Передаточное число", 12, int)
d_roller = prompt_value("Диаметр роликов (мм)", 8.0)
h_roller = prompt_value("Высота роликов (мм)", 6)
Rout = prompt_value("Внешний радиус впадин жесткого колеса (мм)", 38.0)
D = prompt_value("Внешний диаметр редуктора (мм)", 90.0)
h_reducer = prompt_value("Общая высота редуктора (мм)", 15.0)
u = 1  # число волн — не трогать

# === Расчёты  ===
e = 0.2 * d_roller
zg = (i + 1) * u          # число впадин жёсткого колеса
z_rollers = i             # число роликов
Rin = Rout - 2 * e
r_roller = d_roller / 2
rd = Rin + e - d_roller
hc = 2.2 * e              # толщина сепаратора

Rsep_m = rd + r_roller
Rsep_out = Rsep_m + hc / 2
Rsep_in = Rsep_m - hc / 2

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
print(f"- Толщина сепаратора: {hc:.3f} мм")

# Проверка геометрии
if Rin <= (1.03 * d_roller) / np.sin(np.pi / zg):
    print("Ошибка: внутренний радиус слишком мал. Увеличьте Rout или уменьшите передаточное число.")
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
    # Найдём впадины в оригинальном профиле
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

# === Отверстия B: 4 симметричных, с проверкой на 10° ===
base_motor_angles_deg = np.array([0.0, 90.0, 180.0, 270.0])
motor_angles_deg = (base_motor_angles_deg + np.degrees(best_angle)) % 360

# Углы отверстий A
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

# === Вывод списка деталей и отверстий ===
print("\n=== СПИСОК ДЕТАЛЕЙ И ОТВЕРСТИЙ ===")
PARTS = {
    "HW": "Жёсткое колесо (корпус редуктора)",
    "SEP": "Сепаратор",
    "ROL": "Ролики",
    "ECC": "Эксцентрик",
    "MC": "Защитный кожух мотора"
}
for code, name in PARTS.items():
    print(f"- {code}: {name}")

print("\n=== ОТВЕРСТИЯ В ДЕТАЛИ HW ===")
for i in range(n_holes):
    print(f"- A{i+1}: Крепёжное отверстие корпуса (M3), x={hole_x[i]:.2f}, y={hole_y[i]:.2f}")
for i in range(4):
    print(f"- B{i+1}: Отверстие под кожух мотора (M3), x={motor_x[i]:.2f}, y={motor_y[i]:.2f}")
print("- C1: Сквозное отверстие под вал (Ø25 мм)")
print("- D1: Глухое отверстие под наружное кольцо подшипника (Ø26 мм)")

# === Форматирование точек для OpenSCAD ===
def format_points(x, y):
    return ",\n        ".join([f"[{x[i]:.5f}, {y[i]:.5f}]" for i in range(len(x))])

rigid_points_str = format_points(x_rigid, y_rigid)

# === Генерация OpenSCAD-кода ===
openscad_code = f"""// ВПТК редуктор с роликами

$fn = 60;

// Параметры
d_roller = {d_roller:.3f};
h_roller = {h_roller:.3f};
hc = {hc:.3f};
Rsep_m = {Rsep_m:.3f};
Rsep_out = {Rsep_out:.3f};
Rsep_in = {Rsep_in:.3f};
D_out = {D:.3f};
h_reducer = {h_reducer:.3f};

// Высота профильного выреза (на 4 мм выше роликов)
h_cut = h_roller + 4;

// === Корпус (жёсткое колесо) ===
module rigid_gear() {{
    difference() {{
        // Гладкий внешний цилиндр
        cylinder(h = h_reducer, r = D_out / 2, center = false);
        
        // Профильная внутренняя поверхность (только сверху)
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
        for (i = [0 : 3]) {{
            x_hole = [{', '.join([f'{x:.5f}' for x in motor_x])}][i];
            y_hole = [{', '.join([f'{y:.5f}' for y in motor_y])}][i];
            translate([x_hole, y_hole, 0])
                cylinder(h = 8.0, r = 1.6, center = false);
            translate([x_hole, y_hole, 5.0])
                cube(size = [6.0, 6.0, 3.0], center = true);
        }}
        
        // === Группа C/D: подшипник ===
        cylinder(h = h_reducer, r = 25/2, center = false);
        translate([0, 0, 0.5])
            cylinder(h = h_reducer - 0.5, r = 26/2, center = false);
    }}
}}

// === Сепаратор ===
separator_h = h_roller + 4; // Высота сепаратора
slot_clearance = 0.1;       // Зазор по бокам паза
slot_w = d_roller + 2 * slot_clearance;  // Ширина паза
slot_h = h_roller + 2 * slot_clearance;  // Высота паза

module separator() {{
    difference() {{
        // Основное кольцо
        cylinder(h = separator_h, r = Rsep_out, center = true);
        cylinder(h = separator_h + 1, r = Rsep_in, center = true);

        // Вычитаем пазы под ролики
        for (angle = [0 : 360/{z_rollers} : 359]) {{
            rotate([0, 0, angle])
                translate([Rsep_m, 0, 0])
                    rotate([0, 90, 0])
                        cube([slot_h, slot_w, separator_h], center = true);
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
    translate([0, {e:.3f}, 0])
        cylinder(r = {rd:.3f}, h = hc, center = true);
}}

// === Сборка ===
rigid_gear();
//translate([0, 0, 10]) separator();
//rollers();
//eccentric();
"""

# === Сохранение ===
os.makedirs("./output", exist_ok=True)
output_file = "./output/vptc_roller.scad"
with open(output_file, "w") as f:
    f.write(openscad_code)

print(f"\n✅ OpenSCAD-модель сохранена в файл: {output_file}")
