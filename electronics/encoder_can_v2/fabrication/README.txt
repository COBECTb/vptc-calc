Encoder CAN V2.4 — single prototype PCB, 2026-10-26

4 copper layers, finished thickness 0.8 mm, FR4 TG150 requested.
Order: F.Cu / In1.Cu (continuous GND, no signal tracks) / In2.Cu (3.3 V + routing) / B.Cu.
Envelope in the board's radial/tangential frame: 16.853 x 42.938 mm.
Through NPTH mounting holes: 2 x diameter 2.2 mm.
Two open M3 access notches; zero closed internal profile cutouts. Preserve ALL 826 Edge.Cuts lines.
Minimum routed track/clearance 0.127/0.127 mm; foreign-zone clearance >=0.15 mm.
Through vias 0.4/0.2 and 0.45/0.2 mm. Minimum annulus 0.1 mm.
Copper-to-edge >=0.25 mm. All vias tented BOTH sides, no drilled SMD pads or vias beneath component bodies.
Exterior copper keepout diameter 4.4 mm at the M2 mounts, including pours.
Via copper edge to solderable land >=0.5 mm nominal (measured minimum 0.505 mm), including same-net and both faces.

For Rezonit: BASE foil 18 um; not base 35 um. Confirm advanced via class,
finished 0.8 mm tolerance, actual dielectric stack and finished plated copper.
No factory stack, controlled impedance or four-up assembly panel is agreed.
No automatic Gerber job with default stack is included.
Gerber X2: 4 copper, 2 mask, 2 paste, 2 silk and Edge.Cuts = 11 files.
PTH/NPTH Excellon use absolute origin, mm. Drill report included.
Prefer ENIG, subject to assembler confirmation.

Three global fiducials per face: copper 1 mm, mask 2 mm, no paste.
J1/J2/TP1 are PCB lands, not fitted connectors. J2 1x5 P2.54 has no paste.
Preserve its blank 11.5x4 mm clip landing on both sides.
J2 pin1 +5V INPUT, then GND/SWDIO/SWCLK/NRST. It is not VTREF.

35 fitted components, R9 120 ohm DNP. BOM/CPL/fiducials in ../assembly/.
Two-sided 0402 and UFQFPN32 with EP: request stencil/process and EP X-ray review.
LED Kingbright APG1005 cathode pad1; 80% paste, initial stencil80–100um,
maximum two reflow cycles per manufacturer. Exact height <=0.3mm.
Assembly carrier for 4 boards, rails/tabs and support of this 0.8mm shaped board
must be designed by the assembler; no production panel is included.
Confirm exact MPN supply and solder profile before payment.
These files support prototype fabrication, not qualified angle/thermal/EMC performance.

Printed silk strokes >=0.15mm, visible text >=1mm; no decorative 0402 bars.

V2.4 route cleanup: 71 plated through vias. No unintended bare ground under bodies; required GND solder lands including U1 EP33 remain exposed.
