// Универсальная PCB V2: контур, крепления и корпуса из сохранённой KiCad PCB.
// Габаритные модели компонентов; номинальные положения без деформаций пайки.
use <sensors.scad>
function compact_mcu_height() = 0.6;
// compact_outline is injected from KiCad mechanics_v2.json.
// compact_mounts is injected from KiCad mechanics_v2.json.
// compact_swd_pads is injected from KiCad mechanics_v2.json.
// compact_components is injected from KiCad mechanics_v2.json.
function compact_component_list() = compact_components;
// [radius, azimuth, maximum package height], D2 power / D3 command / D4 phase.
function compact_led_points() = compact_leds;
function compact_boundary_points() = compact_outline;
function compact_mount_points() = compact_mounts;
function compact_j1_center() = [
    (compact_j1_pads[0].x+compact_j1_pads[1].x+compact_j1_pads[2].x+compact_j1_pads[3].x)/4,
    (compact_j1_pads[0].y+compact_j1_pads[1].y+compact_j1_pads[2].y+compact_j1_pads[3].y)/4];
function compact_j1_radius() = norm(compact_j1_center());
function compact_j1_angle() = atan2(compact_j1_center().y,compact_j1_center().x);
function compact_pcb_max_radius() = max([for(p=compact_outline)norm(p)]);
function compact_wire_exit_radius() = max(35,compact_pcb_max_radius()+1.5);
module compact_pcb_outline(clearance=0) {
    offset(delta=clearance) difference() {
        polygon(compact_outline);
        for(h=compact_holes) polygon(h);
    }
}
module compact_pcb_mounts() {
    for(p=compact_mounts) translate([p[0],p[1],0]) children();
}
module compact_pcb() {
    color("SeaGreen") difference() {
        linear_extrude(.8) compact_pcb_outline();
        compact_pcb_mounts() translate([0,0,-.01]) cylinder(d=2.2,h=.82,$fn=48);
    }
    color("DimGray") encoder_sensor_positions() tmag5273_envelope();
    for(c=compact_components) rotate(c[1]) translate([c[0],0,0]) rotate(c[2]-c[1])
        color("DimGray") translate([0,0,c[3] ? -c[4][2]/2 : .8+c[4][2]/2])
            cube(c[4],center=true);
    color("Goldenrod") for(p=compact_j1_pads)
        translate([p.x,p.y,-.025]) rotate(compact_j1_angle()) cube([1.2,.8,.05],center=true);
    // J2 on B.Cu: +5V input, GND, SWDIO, SWCLK, NRST; pitch 2.54 mm.
    color("Goldenrod") for(i=[0:4])
        translate([compact_swd_pads[i][0],compact_swd_pads[i][1],.8])
            if(i==0) rotate(46.8) linear_extrude(.025)
                offset(r=.25) square([.5,.5],center=true);
            else cylinder(d=1,h=.025,$fn=32);
    color("OrangeRed") encoder_sensor_positions()
        translate([0,0,-encoder_hall_height()]) sphere(d=.35,$fn=16);
}
