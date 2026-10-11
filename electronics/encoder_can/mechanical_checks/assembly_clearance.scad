// Expected CGAL result: empty. Includes the PCB, placed parts and low M2 heads.
use <../../../output/reducer_cap_encoder_can.scad>
use <../../../output/encoder_can_pcb_layout.scad>
$fn = 96;
intersection() {
    union() { cap_encoder_carrier(); sensor_lid(); }
    union() {
        translate([0,0,11.8]) mirror([0,0,1])
            encoder_can_pcb(show_parts=true,show_points=false);
        encoder_pcb_mount_positions() translate([0,0,11.8]) cylinder(d=3.5,h=1.3);
    }
}
