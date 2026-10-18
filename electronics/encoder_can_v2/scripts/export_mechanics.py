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
components, mounts = [], []
for footprint in board.GetFootprints():
    ref = footprint.GetReference()
    x, y = position(footprint.GetPosition())
    if ref in ('H1', 'H2'):
        mounts.append([x, y])
    if ref in ('U2', 'U3') or ref not in sizes:
        continue
    components.append(dict(ref=ref, r=math.hypot(x, y),
        a=math.degrees(math.atan2(y, x)), angle=footprint.GetOrientationDegrees(),
        front=footprint.GetLayer() == pcb.F_Cu, size_mm=sizes[ref]))
assert len(mounts) == 2

header = '''// Универсальная PCB V2: контур, крепления и корпуса из сохранённой KiCad PCB.
// Габаритные модели компонентов; номинальные положения без деформаций пайки.
use <../../encoder_can_pcb_layout.scad>
'''
header += '// Source PCB SHA256: ' + digest + '\n'
header += 'function compact_source_pcb_sha256() = "' + digest + '";\n'
header += 'function compact_mcu_height() = ' + str(sizes['U1'][2]) + ';\n'
header += 'compact_outline = ' + json.dumps(outline) + ';\n'
header += 'compact_mounts = ' + json.dumps(mounts) + ';\n'
header += 'compact_components = ' + json.dumps([[c['r'], c['a'], c['angle'],
    c['front'], c['size_mm']] for c in components]) + ';\n'
header += '''
function compact_component_list() = compact_components;
function compact_boundary_points() = compact_outline;
function compact_mount_points() = compact_mounts;
module compact_pcb_outline(clearance=0) {
    offset(delta=clearance) polygon(compact_outline);
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
    color("Goldenrod") rotate(20) for(y=[-1.8,-.6,.6,1.8])
        translate([32.4,y,-.025]) cube([1.2,.8,.05],center=true);
    color("OrangeRed") encoder_sensor_positions()
        translate([0,0,-encoder_hall_height()]) sphere(d=.35,$fn=16);
}
'''
OUT.mkdir(exist_ok=True)
(OUT / 'compact_encoder_pcb.scad').write_text(header)
(ROOT / 'design/component_envelopes_v2.json').write_text(json.dumps(components, indent=2)+'\n')
(ROOT / 'design/mechanics_v2.json').write_text(json.dumps(dict(
    source_pcb_sha256=digest, outline=outline, mounts=mounts,
    thickness_mm=.8, span_deg=80), indent=2)+'\n')
print('Mechanical PCB library:', OUT / 'compact_encoder_pcb.scad')
print('Source PCB SHA256:', digest)
