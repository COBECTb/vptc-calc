// Generated from design/placements.json by scripts/update_scad_components.py.
// Mechanical envelopes, not manufacturing models.
module placed_component(r,a,rotation,front,size,pcb_h,c) {
  rotate([0,0,a]) translate([r,0,0]) rotate([0,0,rotation-a])
    color(c) translate([0,0,front ? -size[2]/2 : pcb_h+size[2]/2]) cube(size,center=true);
}
module placed_pad(r,a,rotation,local_xy,size,pcb_h) {
  rotate([0,0,a]) translate([r,0,pcb_h+size[2]/2]) rotate([0,0,rotation-a])
    color("Goldenrod") translate([local_xy[0],-local_xy[1],0]) cube(size,center=true);
}
module encoder_can_placed_components(pcb_h=.8) {
  placed_component(29.3,-5,0,false,[5.1, 5.1, 0.6],pcb_h,"DimGray"); // U1
  placed_component(30,24,0,false,[3, 3, 1.45],pcb_h,"DimGray"); // U4
  placed_component(30.5,62,90,false,[3, 3, 1.45],pcb_h,"DimGray"); // U5
  placed_component(29.3,51,90,false,[3, 3, 1.1],pcb_h,"DimGray"); // D1
  placed_component(25,-5,-5,true,[2.5, 2, 0.5],pcb_h,"Silver"); // Y1
  placed_component(23.8,1,1,true,[1, 0.5, 0.8],pcb_h,"DimGray"); // R1
  placed_component(22.8,-15,-15,true,[1, 0.5, 0.8],pcb_h,"DimGray"); // R2
  placed_component(30,18,18,true,[1, 0.5, 0.8],pcb_h,"DimGray"); // R3
  placed_component(32,18,18,true,[1, 0.5, 0.8],pcb_h,"DimGray"); // R4
  placed_component(31.8,-10,-10,true,[1, 0.5, 0.8],pcb_h,"DimGray"); // R5
  placed_component(28,-10,-10,true,[1, 0.5, 0.8],pcb_h,"DimGray"); // R6
  placed_component(25.6,18,18,true,[1, 0.5, 0.8],pcb_h,"DimGray"); // R7
  placed_component(29.9,3,3,true,[1, 0.5, 0.8],pcb_h,"DimGray"); // R8
  placed_component(28,57,57,true,[1.6, 0.8, 0.95],pcb_h,"DimGray"); // R9
  placed_component(28,-6,-6,true,[1, 0.5, 0.8],pcb_h,"BurlyWood"); // C1
  placed_component(31.8,-1.5,-1.5,true,[1, 0.5, 0.8],pcb_h,"BurlyWood"); // C2
  placed_component(30.5,-6,-6,true,[1.6, 0.8, 0.95],pcb_h,"BurlyWood"); // C3
  placed_component(28,-2,-2,true,[1, 0.5, 0.8],pcb_h,"BurlyWood"); // C4
  placed_component(27.7,2,2,true,[1, 0.5, 0.8],pcb_h,"BurlyWood"); // C5
  placed_component(25.8,3,3,true,[1, 0.5, 0.8],pcb_h,"BurlyWood"); // C6
  placed_component(31.8,3,3,true,[1, 0.5, 0.8],pcb_h,"BurlyWood"); // C7
  placed_component(28.2,24,24,true,[1, 0.5, 0.8],pcb_h,"BurlyWood"); // C8
  placed_component(31.8,24,24,true,[1, 0.5, 0.8],pcb_h,"BurlyWood"); // C9
  placed_component(30,54,54,true,[1.6, 0.8, 0.95],pcb_h,"BurlyWood"); // C10
  placed_component(30,62,62,true,[1.6, 0.8, 0.95],pcb_h,"BurlyWood"); // C11
  placed_component(25,-14,-14,true,[1, 0.5, 0.8],pcb_h,"BurlyWood"); // C12
  placed_component(25.8,-10.5,-10.5,true,[1, 0.5, 0.8],pcb_h,"BurlyWood"); // C13
  placed_component(25.8,-0.5,-0.5,true,[1, 0.5, 0.8],pcb_h,"BurlyWood"); // C14
  placed_pad(30.1,68,90,[-2.25,0],[1,2,.08],pcb_h); // J1
  placed_pad(30.1,68,90,[-0.75,0],[1,2,.08],pcb_h); // J1
  placed_pad(30.1,68,90,[0.75,0],[1,2,.08],pcb_h); // J1
  placed_pad(30.1,68,90,[2.25,0],[1,2,.08],pcb_h); // J1
  placed_pad(30,-44,-44,[0,-2.54],[1,1,.08],pcb_h); // J2
  placed_pad(30,-44,-44,[0,-1.27],[1,1,.08],pcb_h); // J2
  placed_pad(30,-44,-44,[0,0],[1,1,.08],pcb_h); // J2
  placed_pad(30,-44,-44,[0,1.27],[1,1,.08],pcb_h); // J2
  placed_pad(30,-44,-44,[0,2.54],[1,1,.08],pcb_h); // J2
  placed_pad(30,-33,-33,[0,0],[1,1,.08],pcb_h); // TP1
}

function encoder_can_mcu_height() = .6;
module encoder_can_mcu_clearance(pcb_bottom_z=11,xy_gap=.2,z_gap=.15,eps=.01) {
  rotate([0,0,-5]) translate([29.3,0,pcb_bottom_z-encoder_can_mcu_height()-z_gap])
    rotate([0,0,5]) translate([-5.1/2-xy_gap,-5.1/2-xy_gap,0])
      cube([5.1+2*xy_gap,5.1+2*xy_gap,encoder_can_mcu_height()+z_gap+eps]);
}
