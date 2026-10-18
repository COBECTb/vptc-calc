"""Check powered SWD clip geometry from fresh export_views.py output.

The 4 mm contact strip is an explicit jaw-envelope allowance, not a model of
an arbitrary commercial clip. Read the chosen clip's drawing before buying.
"""
from pathlib import Path
import hashlib
import json
import math
from shapely.geometry import Point, Polygon, box
from shapely.affinity import rotate, translate

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / 'design/review_geometry.json').read_text())
pads = sorted((p for p in data['pads'] if p['ref'] == 'J2'),
              key=lambda p: int(p['num']))
assert len(pads) == 5
assert [p['net'] for p in pads] == ['+5V', 'GND', 'SWDIO', 'SWCLK', 'NRST']
assert all(p['side'] == 'B' and p['size'] == [1, 1] for p in pads)
pitch = [math.dist(a['xy'], b['xy']) for a, b in zip(pads, pads[1:])]
assert all(abs(v - 2.54) < 0.000003 for v in pitch)
center = pads[2]['xy']
strip = translate(rotate(box(-5.75, -2, 5.75, 2), -46.8,
                         origin=(0, 0)), *center)
body_clearances = []
for part in data['components']:
    if not part['size']:
        continue
    w, h = part['size'][:2]
    body = translate(rotate(box(-w/2, -h/2, w/2, h/2), -part['angle'],
                            origin=(0, 0)), *part['xy'])
    assert not body.intersects(strip), ('clip jaw meets component', part['ref'])
    body_clearances.append((strip.distance(body), part['ref'], part['side']))
outline = Polygon(data['outline'])
edge_clearances = []
for pad in pads:
    if pad['round']:
        shape = Point(*pad['xy']).buffer(.5, quad_segs=96)
    else:
        radius = pad['corner_mm']
        shape = box(-.5+radius, -.5+radius, .5-radius, .5-radius).buffer(radius)
        shape = translate(rotate(shape, -pad['angle'], origin=(0, 0)), *pad['xy'])
    assert outline.covers(shape)
    edge_clearances.append(shape.distance(outline.boundary))
assert min(edge_clearances) >= .25
report = dict(
    source_pcb_sha256=hashlib.sha256((ROOT/'encoder_can_v2.kicad_pcb').read_bytes()).hexdigest(),
    pinout=[dict(pin=p['num'], net=p['net'], xy_mm=p['xy']) for p in pads],
    pitch_mm=pitch, pad_diameter_mm=1,
    blank_contact_strip_mm=[11.5, 4],
    nearest_component_clearance_mm=sorted(body_clearances)[:5],
    copper_to_edge_mm=edge_clearances,
    limits=['Program before mounting the PCB in its housing.',
            'Choose a 1x5 P2.54 clip for 0.8 mm PCB, with tips <=1 mm and no alignment pins requiring holes.',
            'Verify actual clip jaw dimensions; no particular commercial clip has been mechanically tested.',
            'Pin 1 is +5V power input, not VTREF; use one power source only.',
            'SWD logic is 3.3V. A probe needing VTREF requires a separate target 3.3V sense connection.'])
(ROOT/'design/swd_clip_audit.json').write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps(report, indent=2))
