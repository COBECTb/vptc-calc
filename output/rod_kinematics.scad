// ========== ФУНКЦИИ РАСЧЕТА (ваши) ==========
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

// ========== МОДУЛИ ДЛЯ ОТРИСОВКИ ==========

// Модуль для соединения двух точек цилиндром
module connect_points(p1, p2, diameter = 3) {
    hole_diameter= 3;
    plate_thickness = 2;       // Толщина пластины
    plate_diameter = hole_diameter * 3; // Диаметр круглой пластины

    vec = p2 - p1;
    length = norm(vec);
    
    // Угол в плоскости XY
    angle = atan2(vec.y, vec.x);
    
    translate(p1)
    rotate([0, 90, angle])  // Вот это правильный порядок!
        cylinder(h = length, d = diameter, center = false);
    translate(p1)
    difference() {
                cylinder( h = plate_thickness, d = plate_diameter, center = true );
                // Отверстие для оси шарнира (перпендикулярно тяге)
                cylinder( h = plate_thickness * 2, d = hole_diameter, center = true );
            };
    translate(p2)
    difference() {
                cylinder( h = plate_thickness+10, d = plate_diameter, center = true );
                // Отверстие для оси шарнира (перпендикулярно тяге)
                cylinder( h = plate_thickness * 2, d = hole_diameter, center = true );
            };
}

// Модуль для отрисовки качалки (рычага)
module draw_arm(center, radius, angle, width = 6, thickness = 4, color = "red") {
    color(color) {
        // Центральная ступица
        translate(center)
            cylinder(h = thickness + 2, d = 10, center = true);
        
        // Рычаг
        translate(center)
        rotate([0, 0, angle]) {
            // Основание рычага
            cylinder(h = thickness, d = width, center = true);
            
            // Длина рычага до точки крепления
            translate([radius, 0, 0])
                cylinder(h = thickness, d = width, center = true);
            
            // Соединяющая часть
            hull() {
                cylinder(h = thickness, d = width, center = true);
                translate([radius, 0, 0])
                    cylinder(h = thickness, d = width, center = true);
            }
            
            // Точка крепления (усиленная)
            translate([radius, 0, 0])
                cylinder(h = thickness + 4, d = 8, center = true);
        }
    }
}

// Модуль для отрисовки основания
module draw_base(position, size = [40, 40, 5], color = "gray") {
    color(color, 0.5)
    translate(position - [0, 0, size.z/2])
        cube(size, center = true);
}

// Модуль для отрисовки всей системы
module draw_linkage_system(
    servo_angle, rod_length, radius1, radius2, center1, center2,
    show_trajectory = true
) {
    // Выполняем расчет
    result = calculate_rigid_linkage(
        servo_angle, rod_length, radius1, radius2, center1, center2
    );
    
    // Извлекаем результаты
    point1 = get_value(result, "point1");
    point2 = get_value(result, "point2");
    angle2 = get_value(result, "angle2");
    solution_exists = get_value(result, "solution_exists");
    
    // Если решение существует - рисуем механизм
    if (solution_exists) {
        // 1. ОСНОВАНИЯ
        draw_base(center1, [50, 50, 8], "lightgray");
        draw_base(center2, [50, 50, 8], "lightgray");
        
        // 2. ПЕРВАЯ КАЧАЛКА (сервопривод)
        draw_arm(center1, radius1, servo_angle, 6, 4, "red");
        
        // 3. ВТОРАЯ КАЧАЛКА (колено)
        draw_arm(center2, radius2, angle2, 6, 4, "blue");
        
        // 4. ТЯГА (стержень)
        color("silver") {
            connect_points(point1, point2, 5);
            
            // Шарнирные шарики на концах
            translate(point1) sphere(d = 10);
            translate(point2) sphere(d = 10);
        }
        
        // 5. ЦЕНТРЫ ВРАЩЕНИЯ (оси)
        color("black") {
            // Ось сервопривода
            translate(center1)
                cylinder(h = 15, d = 4, center = true);
            
            // Ось колена
            translate(center2)
                cylinder(h = 15, d = 4, center = true);
        }
        
        // 6. ТРАЕКТОРИИ ДВИЖЕНИЯ (полупрозрачные)
        if (show_trajectory) {
            // Траектория точки P1
            color("red", 0.2)
            translate(center1)
                cylinder(h = 0.5, r = radius1, center = true);
            
            // Траектория точки P2 для всех углов
            color("blue", 0.2) 
            for(ang = [0:10:360]) {
                test_result = calculate_rigid_linkage(
                    ang, rod_length, radius1, radius2, center1, center2
                );
                if (get_value(test_result, "solution_exists")) {
                    test_p2 = get_value(test_result, "point2");
                    translate(test_p2)
                        sphere(r = 1);
                }
            }
        }
        
        // 7. ИНФОРМАЦИОННАЯ ПАНЕЛЬ
        color("black")
        translate([0, -50, 20])
        linear_extrude(1) {
            text(str("Сервопривод: ", round(servo_angle), "°"), 
                 size = 5, halign = "center");
            
            translate([0, -7, 0])
            text(str("Колено: ", round(angle2), "°"), 
                 size = 5, halign = "center");
            
            translate([0, -14, 0])
            text(str("Длина тяги: ", rod_length, "мм"), 
                 size = 5, halign = "center");
        }
        
    } else {
        // Если решения нет - показываем сообщение об ошибке
        color("red")
        translate([0, 0, 30])
        linear_extrude(2)
            text("НЕТ РЕШЕНИЯ!", size = 10, halign = "center");
    }
}

// ========== ПАРАМЕТРЫ И ВЫЗОВ ==========

// Параметры механизма
rod_length = 90;
radius1 = 20;
radius2 = 25;
center1 = [0, 0, 0];
center2 = [80, 30, 0];

// Для анимации используем $t (от 0 до 1)
servo_angle = $t * 270 - 135;  // От -135° до +135°

// Отрисовываем систему
draw_linkage_system(
    servo_angle = servo_angle,
    rod_length = rod_length,
    radius1 = radius1,
    radius2 = radius2,
    center1 = center1,
    center2 = center2,
    show_trajectory = true
);

// ========== ДОПОЛНИТЕЛЬНАЯ ВИЗУАЛИЗАЦИЯ ==========

// Ради удобства - рисуем сетку координат
%color("gray", 0.2) {
    // Оси координат
    cylinder(h = 100, r = 0.5, center = true); // Z
    rotate([90, 0, 0]) cylinder(h = 100, r = 0.5, center = true); // Y
    rotate([0, 90, 0]) cylinder(h = 100, r = 0.5, center = true); // X
    
    // Подписи осей
    translate([105, 0, 0]) text("X", size = 5);
    translate([0, 105, 0]) text("Y", size = 5);
    translate([0, 0, 105]) text("Z", size = 5);
}

// ========== ПРОВЕРОЧНЫЙ РАСЧЕТ ==========

// Выводим значения в консоль для текущего угла
echo(" ");
echo("=== РАСЧЕТ ДЛЯ УГЛА ", servo_angle, "° ===");

result = calculate_rigid_linkage(
    servo_angle, rod_length, radius1, radius2, center1, center2
);

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