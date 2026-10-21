// Универсальная плата V2 в колене. Параметры управления для OpenSCAD.
// Геометрия и кинематика: knee_encoder_scene.scad

/* [Вид] */
view="assembly"; // [assembly,exploded,section,stage,mount,hip,shin,cover,rotor,pcb,magnet_ring,cover_print,hip_print,ring_print]
assembly_step=4; // [1:Открытая вилка,2:Голень ось и съёмная щека,3:Плата с проводами,4:Наружная сервисная крышка]

/* [Движение колена] */
// Угол рычага; при времени анимации 0 — начальное положение.
knee_angle=0; // [-44.6458:0.1:54.204]
// Использовать время $t из меню Вид → Анимировать. Отключить для ручного угла при любом времени.
animate=true;

/* [Отображение] */
show_magnets=true;
show_bearings=true;
show_rod=true;
show_lower_fork=true;

/* [Hidden] */
include <knee_encoder_scene.scad>
