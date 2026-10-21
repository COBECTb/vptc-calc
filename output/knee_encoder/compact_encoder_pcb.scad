// Эскиз компактной общей платы. НЕ РАЗВОДКА И НЕ ФАЙЛ ДЛЯ ЗАКАЗА.
use <../encoder_can_pcb_layout.scad>
compact_components = [[29.2, 5.0, 9.0, false, [5.1, 5.1, 0.6]], [25.0, -14.0, 9.0, true, [3, 3, 1.45]], [25.0, 28.0, 9.0, true, [3, 3, 1.45]], [28.45, 20.0, 9.0, false, [3, 3, 1.1]], [29.5, -2.0, 9.0, true, [2.5, 2, 0.7]], [24.75, -7.0, 9.0, true, [1.6, 0.8, 0.95]], [27.7, 31.0, 9.0, false, [1.6, 0.8, 0.95]], [31.95, 21.0, 9.0, false, [1.6, 0.8, 0.95]], [22.75, 20.0, 9.0, true, [1, 0.5, 0.4]], [25.75, 18.0, 9.0, true, [1, 0.5, 0.4]], [29.0, 17.0, 9.0, true, [1, 0.5, 0.4]], [30.25, 19.0, 9.0, true, [1, 0.5, 0.4]], [24.75, -4.0, 9.0, true, [1, 0.5, 0.4]], [27.75, 1.0, 9.0, true, [1, 0.5, 0.4]], [26.75, 14.0, 9.0, true, [1, 0.5, 0.4]], [29.0, 15.0, 9.0, true, [1, 0.5, 0.4]], [28.2, -2.0, 9.0, false, [1, 0.5, 0.55]], [32.2, -4.0, 9.0, false, [1, 0.5, 0.55]], [32.25, -4.0, 9.0, true, [1, 0.5, 0.55]], [27.5, -5.0, 9.0, true, [1, 0.5, 0.55]], [26.0, 3.0, 9.0, true, [1, 0.5, 0.55]], [32.25, 5.0, 9.0, true, [1, 0.5, 0.55]], [30.95, 19.0, 9.0, false, [1, 0.5, 0.55]], [30.95, 17.0, 9.0, false, [1, 0.5, 0.55]], [24.0, 2.0, 9.0, true, [1, 0.5, 0.55]], [27.7, 12.0, 9.0, false, [1, 0.5, 0.55]], [31.95, -1.0, 9.0, false, [1, 0.5, 0.55]]];

function compact_component_list()=compact_components;
module compact_pcb_outline(clearance=0){
 offset(delta=clearance) difference(){
  polygon(concat([for(i=[0:160]) let(a=9-40+80*i/160) [33.4*cos(a),33.4*sin(a)]],
   [for(i=[640:-1:0]) let(a=9-40+80*i/640,d=abs(a-9),r=d<=10?21.3:d>=12?21.6:21.3+.3*(d-10)/2) [r*cos(a),r*sin(a)]]));
  for(a=[-21,39]) translate([31.5*cos(a),31.5*sin(a)]) circle(r=4.5,$fn=96);
 }
}
module compact_pcb_mounts(){for(a=[-9,27]) rotate(a) translate([30.5,0,0]) children();}
module compact_pcb(){
 color("SeaGreen") difference(){linear_extrude(.8)compact_pcb_outline();compact_pcb_mounts()translate([0,0,-.01])cylinder(d=2.2,h=.82,$fn=32);}
 color("DimGray") encoder_sensor_positions() tmag5273_envelope();
 for(c=compact_components) rotate(c[1]) translate([c[0],0,0]) rotate(c[2]-c[1])
  color("DimGray") translate([0,0,c[3]?-c[4][2]/2:.8+c[4][2]/2]) cube(c[4],center=true);
 color("Goldenrod") rotate(19) for(y=[-1.8,-.6,.6,1.8]) translate([32,y,-.025]) cube([1.2,.8,.05],center=true);
 color("OrangeRed") encoder_sensor_positions() translate([0,0,-encoder_hall_height()]) sphere(d=.35,$fn=16);
}
