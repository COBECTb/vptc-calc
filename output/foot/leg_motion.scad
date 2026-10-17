// Full native leg, using the existing time law. Open View > Animate, time 0..1.
use <../vptc_roller.scad>
$fn=64;
leg(servo=$t*135-60.5);
// This is a knee sweep with a fixed hip, not a ground-contact walking controller.
// The original lower end of the sweep exceeds the historical rod-clearance limit.
