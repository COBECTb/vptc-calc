// Expected CGAL result: empty (OpenSCAD 2021.01 reports exit code 1 for an empty STL).
// Checks the real bearing against the MCU relief and every placed component body.
use <../../../output/reducer_cap_encoder_can.scad>
use <../design/placed_components.scad>
$fn = 96;
intersection() {
    main_bearing_in_cap();
    union() {
        encoder_can_mcu_clearance(pcb_bottom_z=11,xy_gap=.2,z_gap=.15,eps=.01);
        translate([0,0,11.8]) mirror([0,0,1]) encoder_can_placed_components(pcb_h=.8);
    }
}
