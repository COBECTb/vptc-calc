// Зажим с двумя магнитными дорожками: 24 / 26 магнитов диаметром 5 мм.
// Основа: connector_clamp() из output/vptc_roller_19_4_5_70.scad.
// Штатные посадки, полки и отверстия сохранены. Бортики добавлены на торец Z=12.
// Для печати нужны две одинаковые половины.
// Крайние магниты наружного ряда у сборочного крепежа вклеивать после затяжки зажима.
// Остальные магниты можно установить заранее. Соблюдать чередование N/S через стыки.

/* [Отображение] */
view = "assembly"; // [print:Две половины для печати, half:Одна половина, assembly:Собранный зажим]
show_magnets = true; // Магниты показаны только как справочная геометрия и не входят в STL.
assembly_stage = "complete"; // [before_tightening:До затяжки - крайние магниты сняты, complete:После затяжки - все магниты]

/* [Магниты и бортики] */
magnet_d = 5;
magnet_h = 1; // Только для предварительного просмотра; задайте фактическую высоту.
magnet_d_clearance = 0.2; // Прибавка к диаметру посадочного отверстия.
rim_wall = 0.6;
rim_h = 0.4;
inner_track_r = 23.5;
outer_track_r = 29.5;
inner_magnet_count = 24;
outer_magnet_count = 26;

/* [Hidden] */
$fn = 96;
D_out = 70;
bearing_inner = 40;
clamp_h = 12;
overlap = 0.02;
track_radii = [inner_track_r, outer_track_r];
track_counts = [inner_magnet_count, outer_magnet_count];
pocket_d = magnet_d + magnet_d_clearance;
rim_d = pocket_d + 2 * rim_wall;

assert(view == "print" || view == "half" || view == "assembly",
    "Допустимые режимы: print, half, assembly.");
assert(assembly_stage == "before_tightening" || assembly_stage == "complete",
    "Допустимые этапы: before_tightening, complete.");
assert(magnet_d > 0 && magnet_h > 0 && magnet_d_clearance >= 0,
    "Проверьте размеры магнитов и зазор.");
assert(rim_wall > 0 && rim_h > 0, "Бортики должны иметь положительную толщину и высоту.");
assert(outer_track_r > inner_track_r, "Наружная дорожка должна быть дальше от оси.");
assert(outer_magnet_count == inner_magnet_count + 2,
    "Во внутреннем ряду должно быть на одну пару полюсов меньше.");
// Допускается объединение внешних стенок соседних бортиков; отверстия остаются свободными.
assert(outer_track_r - inner_track_r >= pocket_d + rim_wall,
    "Дорожки слишком близко: стенка одного бортика перекрывает соседнее отверстие.");
for (t = [0 : 1]) {
    n = track_counts[t];
    r = track_radii[t];
    assert(n >= 4 && n == floor(n) && n % 2 == 0,
        "В каждом полном ряду должно быть четное целое число магнитов.");
    assert(r - rim_d/2 >= bearing_inner/2 && r + rim_d/2 <= D_out/2-2,
        "Бортики выходят за пределы торца зажима.");
    assert(2*r*sin(180/n) >= pocket_d + rim_wall,
        "Между соседними посадочными отверстиями недостаточно места для стенки.");
}

// Штатная геометрия полузажима из готовой модели редуктора.
module connector_clamp_base() {
    intersection() {
        difference() {
            cylinder(h = 12, r = D_out/2-2, center = false);
            translate([0, 0, 2]) cylinder(h = 8.2, r = D_out/2-8.8, center = false);
            translate([0, 0, -0.1]) cylinder(h = 12.2, r = bearing_inner/2, center = false);
            rotate([0,90,90]) translate([-6, D_out/2-5, 3]) cylinder(h = 20, r = 3, center = false);
            rotate([0,90,90]) translate([-6, D_out/2-5, -0.1]) cylinder(h = 20.2, r = 1.6, center = false);
            rotate([0,-90,-90]) translate([6, D_out/2-5, 3]) cylinder(h = 20, r = 3, center = false);
            rotate([0,-90,-90]) translate([6, D_out/2-5, -0.1]) cylinder(h = 20.2, r = 1.6, center = false);
        }
        translate([-D_out, 0, -1])
            cube([D_out*2, D_out, 14]);
    }
}

// Половина шага от линии разъема; стенки бортиков могут соединяться через стык.
module track_positions(full_circle = false) {
    for (t = [0 : 1]) {
        n = track_counts[t];
        r = track_radii[t];
        last_index = full_circle ? n-1 : n/2-1;
        for (j = [0 : last_index]) {
            angle = (j + 0.5) * 360/n;
            translate([r*cos(angle), r*sin(angle), clamp_h])
                children();
        }
    }
}

module magnet_rims() {
    // Общий вырез всех посадок оставляет отверстия свободными при слиянии бортиков.
    intersection() {
        difference() {
            union() {
                track_positions(full_circle = true)
                    translate([0, 0, -overlap])
                        cylinder(d = rim_d, h = rim_h + overlap);
            }
            union() {
                track_positions(full_circle = true)
                    translate([0, 0, -2*overlap])
                        cylinder(d = pocket_d, h = rim_h + 4*overlap);
            }
        }
        // Общие стенки разрезаются по плоскости разъема, без наложения половин.
        translate([-D_out, 0, clamp_h - 2*overlap])
            cube([D_out*2, D_out, rim_h + 4*overlap]);
    }
}

// Красный: N наружу, синий: S наружу. Полярность чередуется по всему кругу.
// На второй половине ряд меняет полярность, если число магнитов в полуряде нечетное.
// Крайние магниты наружного ряда возле крепежа устанавливать после затяжки половин.
module magnet_preview(second_half = false) {
    for (t = [0 : 1]) {
        n = track_counts[t];
        r = track_radii[t];
        for (j = [0 : n/2-1]) {
            angle = (j + 0.5) * 360/n;
            global_index = j + (second_half ? n/2 : 0);
            north_out = global_index % 2 == 0;
            install_last = t == 1 && (j == 0 || j == n/2-1);
            if (!install_last || assembly_stage == "complete") {
               color(north_out ? "Firebrick" : "RoyalBlue", 0.85)
                    translate([r*cos(angle), r*sin(angle), clamp_h])
                        cylinder(d = magnet_d, h = magnet_h);

            }
        }
    }
}

module connector_clamp_with_magnet_rims(second_half = false) {
    union() {
        connector_clamp_base();
        magnet_rims();
    }
    if (show_magnets)
        %magnet_preview(second_half);
}

if (view == "half") {
    connector_clamp_with_magnet_rims();
} else if (view == "assembly") {
    connector_clamp_with_magnet_rims();
    rotate([0, 0, 180]) connector_clamp_with_magnet_rims(second_half = true);
} else {
    translate([-D_out/2-4, 0, 0]) connector_clamp_with_magnet_rims();
    translate([ D_out/2+4, 0, 0]) connector_clamp_with_magnet_rims(second_half = true);
}
