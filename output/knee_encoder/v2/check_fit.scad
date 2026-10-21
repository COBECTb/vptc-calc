use <knee_encoder_compact.scad>
use <reducer_compact_layout.scad>
part="knee";
if(part=="knee") intersection(){pcb();union(){proposed_hip();protective_cover();}}
if(part=="reducer_pcb") intersection(){pcb_in_cap();cap_encoder_carrier();}

if(part=="reducer_lid") intersection(){pcb_in_cap();sensor_lid();}

// Прижимы намеренно касаются только плоскостей PCB; исключаем 0.001 мм контакта.
module pcb_without_mount_contact(){difference(){pcb();board_mounts(){translate([0,0,knee_board_front_z()-.001])cylinder(d=3.82,h=.002,$fn=64);translate([0,0,knee_board_rear_z()-.001])cylinder(d=3.82,h=.002,$fn=64);}}}
if(part=="knee_volume") intersection(){pcb_without_mount_contact();union(){proposed_hip();protective_cover();}}
if(part=="cover_body") intersection(){protective_cover();proposed_hip();}
if(part=="wire_body") intersection(){wires();union(){proposed_hip();protective_cover();pcb();}}
if(part=="screws_pcb") intersection(){pcb_screws();pcb();}

// Проверка выбранного кадра анимации; начальный knee_angle=0.
if(part=="supports_body_at_time") intersection(){
    rotate(knee_animation_angle($t,0)) rotor_supports();
    union(){proposed_hip();original_lower_fork_local();protective_cover();}
}
