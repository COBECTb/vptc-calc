// Геометрия для независимой проверки и воспроизводимого экспорта STL.
use <knee_encoder_compact.scad>
use <../../vptc_roller_19_4_5_70.scad>
$fn=64;
part="hip";
if(part=="hip") proposed_hip();
if(part=="hip_original") original_hip_local();
if(part=="lower") original_lower_fork_local();
if(part=="cover") protective_cover();
if(part=="pcb") pcb();
if(part=="shin") proposed_shin();
if(part=="shin_original") shin(foot=false);
if(part=="rotor_base") rotor_blank();
if(part=="magnet_ring") knee_magnet_ring();
if(part=="magnet") magnets();
if(part=="cuff") foot_cuff_in_knee();
if(part=="wires") wires();
if(part=="screws") pcb_screws();
// Положительная огибающая новых неподвижных деталей; без вычитания старого STL.
if(part=="envelope") stationary_shell();
