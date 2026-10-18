// Slow inspection: four complete running cycles per one camera orbit.
// View > Animate: FPS 10, Steps 480 (~48 seconds/orbit if rendering keeps up).
use <step_motion.scad>
run_cycles=4; // [1:1:8]
camera_elevation=68;
camera_distance=2700;
/* [Hidden] */
// GUI animation supplies $t before evaluation. For CLI probes override the
// regular orbit_time variable (-D orbit_time=.25); -D $t is applied too late
// for top-level camera assignments in OpenSCAD 2021.01.
orbit_time=$t;
$vpt=[step_configuration()[0]*step_configuration()[4]*run_cycles*orbit_time,0,170];
$vpr=[camera_elevation,0,25+360*orbit_time];
$vpd=camera_distance;
echo(orbit_time=orbit_time,running_cycle_time=run_cycles*orbit_time,camera_target=$vpt,camera_rotation=$vpr);
walking_robot(run_cycles*orbit_time,view="quadruped",gait="run");
