"""Read native V2 PCB; update its mechanical library and preserve housings.

Run with KiCad Python. No PCB, knee or reducer housing is rewritten.
"""
from pathlib import Path
import hashlib
import json
import math
import pcbnew as pcb

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
OUT = REPO / 'output/knee_encoder/v2'
SOURCE = ROOT / 'encoder_can_v2.kicad_pcb'
board = pcb.LoadBoard(str(SOURCE))
digest = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
sizes = {c['ref']: c['size_mm'] for c in
         json.loads((ROOT / 'design/component_envelopes.json').read_text())}


def position(point):
    return [pcb.ToMM(point.x) - 100, 100 - pcb.ToMM(point.y)]


polygon = pcb.SHAPE_POLY_SET()
assert board.GetBoardPolygonOutlines(polygon, False)
assert polygon.OutlineCount() == 1
chain = polygon.Outline(0)
outline = [position(chain.CPoint(i)) for i in range(chain.PointCount())]
outline_holes = [[position(polygon.Hole(0,j).CPoint(i))
                  for i in range(polygon.Hole(0,j).PointCount())]
                 for j in range(polygon.HoleCount(0))]
components, mounts = [], []
swd_pads = []
j1_pads = []
for footprint in board.GetFootprints():
    ref = footprint.GetReference()
    x, y = position(footprint.GetPosition())
    if ref in ('H1', 'H2'):
        mounts.append([x, y])
    if ref == 'J2':
        swd_pads = [dict(number=pad.GetNumber(), xy=position(pad.GetPosition()),
                        net=pad.GetNetname()) for pad in footprint.Pads()]
    if ref == 'J1':
        j1_pads = [dict(number=pad.GetNumber(), xy=position(pad.GetPosition()),
                       net=pad.GetNetname()) for pad in footprint.Pads()]
    if ref in ('U2', 'U3') or ref not in sizes:
        continue
    components.append(dict(ref=ref, r=math.hypot(x, y),
        a=math.degrees(math.atan2(y, x)), angle=footprint.GetOrientationDegrees(),
        front=footprint.GetLayer() == pcb.F_Cu, size_mm=sizes[ref]))
assert len(mounts) == 2
assert len(j1_pads) == 4
j1_pads.sort(key=lambda pad:int(pad['number']))

header = '''// Универсальная PCB V2: контур, крепления и корпуса из сохранённой KiCad PCB.
// Габаритные модели компонентов; номинальные положения без деформаций пайки.
use <../../encoder_can_pcb_layout.scad>
'''
header += '// Source PCB SHA256: ' + digest + '\n'
header += 'function compact_source_pcb_sha256() = "' + digest + '";\n'
header += 'function compact_mcu_height() = ' + str(sizes['U1'][2]) + ';\n'
header += 'compact_outline = ' + json.dumps(outline) + ';\n'
header += 'compact_holes = ' + json.dumps(outline_holes) + ';\n'
header += 'compact_mounts = ' + json.dumps(mounts) + ';\n'
header += 'compact_swd_pads = ' + json.dumps([p['xy'] for p in swd_pads]) + ';\n'
header += 'compact_j1_pads = ' + json.dumps([p['xy'] for p in j1_pads]) + ';\n'
header += 'compact_components = ' + json.dumps([[c['r'], c['a'], c['angle'],
    c['front'], c['size_mm']] for c in components]) + ';\n'
header += 'compact_leds = '+json.dumps([[c['r'],c['a'],c['size_mm'][2]] for ref in ['D2','D3','D4'] for c in components if c['ref']==ref])+';\n'
header += '''
function compact_led_points() = compact_leds;
function compact_component_list() = compact_components;
function compact_boundary_points() = compact_outline;
function compact_mount_points() = compact_mounts;
function compact_j1_center() = [
    (compact_j1_pads[0].x+compact_j1_pads[1].x+compact_j1_pads[2].x+compact_j1_pads[3].x)/4,
    (compact_j1_pads[0].y+compact_j1_pads[1].y+compact_j1_pads[2].y+compact_j1_pads[3].y)/4];
function compact_j1_radius() = norm(compact_j1_center());
function compact_j1_angle() = atan2(compact_j1_center().y,compact_j1_center().x);
function compact_pcb_max_radius() = max([for(p=compact_outline)norm(p)]);
function compact_wire_exit_radius() = max(35,compact_pcb_max_radius()+1.5);
module compact_pcb_outline(clearance=0) {
    offset(delta=clearance) difference() {
        polygon(compact_outline);
        for(h=compact_holes) polygon(h);
    }
}
module compact_pcb_mounts() {
    for(p=compact_mounts) translate([p[0],p[1],0]) children();
}
module compact_pcb() {
    color("SeaGreen") difference() {
        linear_extrude(.8) compact_pcb_outline();
        compact_pcb_mounts() translate([0,0,-.01]) cylinder(d=2.2,h=.82,$fn=48);
    }
    color("DimGray") encoder_sensor_positions() tmag5273_envelope();
    for(c=compact_components) rotate(c[1]) translate([c[0],0,0]) rotate(c[2]-c[1])
        color("DimGray") translate([0,0,c[3] ? -c[4][2]/2 : .8+c[4][2]/2])
            cube(c[4],center=true);
    color("Goldenrod") for(p=compact_j1_pads)
        translate([p.x,p.y,-.025]) rotate(compact_j1_angle()) cube([1.2,.8,.05],center=true);
    // J2 on B.Cu: +5V input, GND, SWDIO, SWCLK, NRST; pitch 2.54 mm.
    color("Goldenrod") for(i=[0:4])
        translate([compact_swd_pads[i][0],compact_swd_pads[i][1],.8])
            if(i==0) rotate(46.8) linear_extrude(.025)
                offset(r=.25) square([.5,.5],center=true);
            else cylinder(d=1,h=.025,$fn=32);
    color("OrangeRed") encoder_sensor_positions()
        translate([0,0,-encoder_hall_height()]) sphere(d=.35,$fn=16);
}
'''
OUT.mkdir(parents=True, exist_ok=True)
(OUT / 'compact_encoder_pcb.scad').write_text(header)
(ROOT / 'design/component_envelopes_v2.json').write_text(json.dumps(components, indent=2)+'\n')
(ROOT / 'design/mechanics_v2.json').write_text(json.dumps(dict(
    source_pcb_sha256=digest, outline=outline, outline_holes=outline_holes, mounts=mounts,
    thickness_mm=.8, span_deg=80, swd_pads=swd_pads,
    j1_pads=j1_pads, outer_radius_mm=max(math.hypot(*p) for p in outline),
    swd_pitch_mm=2.54), indent=2)+'\n')
print('Mechanical PCB library:', OUT / 'compact_encoder_pcb.scad')
print('Source PCB SHA256:', digest)
