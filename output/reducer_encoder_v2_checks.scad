// Диагностические объёмы в координатах сборки. Не детали для печати.
use <reducer_cap_encoder_can.scad>
part = "pcb";
if (part == "pcb") pcb_in_cap();
else if (part == "carrier_collision") intersection() { pcb_in_cap(); cap_encoder_carrier(); }
else if (part == "lid_collision") intersection() { pcb_in_cap(); sensor_lid(); }
else if (part == "moving_collision") intersection() {
    union() { cap_encoder_carrier(); sensor_lid(); }
    union() { clamp_facing_cap(); output_connector_in_cap(); load_connector_in_clamp(); }
}
// Консервативная осесимметричная огибающая зажима, магнитов и двух соединителей.
// Включает все их положения за 360°, а не только несколько дискретных углов.
else if (part == "full_turn_collision") intersection() {
    union() { cap_encoder_carrier(); sensor_lid(); }
    rotor_envelope();
}
else if (part == "wire_collision") intersection() {
    encoder_wires();
    union() { cap_encoder_carrier(); sensor_lid(); pcb_in_cap(); rotor_envelope(); }
}

// Контактные поверхности исключены на 0.001 мм: это проверка пересечений,
// а не проверка плотности посадки Ø52. Дискретизация совпадает с основанием.
else if (part == "bearing_collision") intersection() {
    cap_encoder_carrier();
    translate([0,0,3.001]) difference() {
        cylinder(r=25.999,h=6.998,$fn=60);
        translate([0,0,-.01]) cylinder(r=20.001,h=7.018,$fn=60);
    }
}

// Радиусы описанных 180-гранников: они содержат круглые детали при любом угле.
// Сепаратор R26.08 до Z2.5, переход R22 до Z3, шейка R20 до Z16.75.
// Верхняя огибающая включает магниты, зажим и верхний соединитель до Z39.75.
module rotor_envelope() {
    translate([0,0,-8.5]) cylinder(r=26.08/cos(1),h=11,$fn=180);
    translate([0,0,2.5]) cylinder(r=22/cos(1),h=.5,$fn=180);
    translate([0,0,3]) cylinder(r=20/cos(1),h=13.75,$fn=180);
    translate([0,0,14.25]) cylinder(r=33/cos(1),h=25.5,$fn=180);
}
