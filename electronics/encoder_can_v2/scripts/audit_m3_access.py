"""Check D70 reducer assembly screw access through the encoder PCB.

These are the original six M3 centres, independent of the relocated M2 PCB
mounts. At least two access openings intersect this sector board.
"""
from pathlib import Path
import hashlib
import json
import math
from shapely.geometry import Point, Polygon

R = Path(__file__).resolve().parents[1]
d = json.loads((R/'design/review_geometry.json').read_text())
digest = hashlib.sha256((R/'encoder_can_v2.kicad_pcb').read_bytes()).hexdigest()
assert digest == d['source_pcb_sha256'], 'Refresh the native geometry export'
outline = Polygon(d['outline'], d.get('outline_holes', []))
rows = []
for angle in range(39, 399, 60):
    a = math.radians(angle)
    xy = [100+31.5*math.cos(a), 100-31.5*math.sin(a)]
    # Allow 0.01 mm only for polygon/chord conversion at the nominal boundary.
    probe = Point(xy).buffer(3.4-.01, quad_segs=128)
    intersection = outline.intersection(probe).area
    rows.append(dict(angle_deg=angle, center_mm=xy,
                     pcb_in_access_area_mm2=intersection,
                     clear=intersection < .000001))
report = dict(source_pcb_sha256=digest, required_M3_access_radius_mm=3.4,
              original_M3_pitch_radius_mm=31.5,
              polygon_boundary_allowance_mm=.01, checks=rows,
              passed=all(q['clear'] for q in rows),
              limits=['Nominal D70 geometry; tool envelope and real screw tolerances require assembly validation.',
                      'Does not replace the independent copper-to-edge DRC or M2 mounting audit.'])
(R/'design/m3_access_audit.json').write_text(json.dumps(report, indent=2)+'\n')
print('M3 assembly access:', 'passed' if report['passed'] else 'FAILED')
assert report['passed'], 'PCB material blocks original reducer assembly screws'
