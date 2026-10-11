// Expected remaining wall: Z3...10.25. The relief does not reach the bearing at Z3...10.
// The probe is inside the MCU relief, outside the ordinary rear pocket R>=27.
use <../../../output/reducer_cap_encoder_can.scad>
use <../design/placed_components.scad>
intersection() {
    difference() {
        encoder_cap_base();
        encoder_can_mcu_clearance(pcb_bottom_z=11,xy_gap=.2,z_gap=.15,eps=.01);
    }
    translate([26.6,-1,-.1]) cylinder(r=.02,h=11.2,$fn=12);
}
