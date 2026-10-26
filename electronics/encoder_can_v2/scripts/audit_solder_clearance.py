"""Independent, same-net-inclusive checks of via-to-land and body clearance.

Run export_views.py first. Uses maximum mechanical body envelopes, including
components on the opposite face. Mask tenting is not a substitute for this test.
Requires Shapely. Does not certify solder process quality or physical assembly.
"""
from pathlib import Path
import argparse
import hashlib
import json
from shapely.geometry import Point, Polygon, box
from shapely.affinity import rotate, translate

R = Path(__file__).resolve().parents[1]
ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument('--gap', type=float, default=0.5)
ap.add_argument('--output', type=Path, default=R/'design/solder_clearance_audit.json')
args = ap.parse_args()
digest = hashlib.sha256((R/'encoder_can_v2.kicad_pcb').read_bytes()).hexdigest()
d = json.loads((R/'design/review_geometry.json').read_text())
assert d.get('source_pcb_sha256') == digest, 'Export native geometry again before checking'


def rectangle(center, size, angle, radius=0):
    w, h = size
    sh = (box(-w/2+radius, -h/2+radius, w/2-radius, h/2-radius).buffer(radius, quad_segs=48)
          if radius else box(-w/2, -h/2, w/2, h/2))
    return translate(rotate(sh, -angle, origin=(0, 0)), *center)


lands = []
for q in d['pads']:
    if q['hole'] or not q['num'] or q['ref'].startswith('FID'):
        continue
    shape = (Point(q['xy']).buffer(q['size'][0]/2, quad_segs=64) if q['round']
             else rectangle(q['xy'], q['size'], q['angle'], q.get('corner_mm', 0)))
    lands.append((q, shape))
bodies = [(c, rectangle(c['xy'], c['size'][:2], c['angle']))
          for c in d['components'] if c['size']]
vias = [q for q in d['tracks'] if q['via']]
violations = []
minimum = (float('inf'), None)
body_minimum = (float('inf'), None)
for v in vias:
    pt = Point(v['a'])
    radius = v['width']/2
    for q, shape in lands:
        gap = pt.distance(shape) - radius
        item = dict(via_xy=v['a'], via_net=v['net'], ref=q['ref'], pad=q['num'],
                    pad_net=q['net'], gap_mm=gap)
        if gap < minimum[0]:
            minimum = (gap, item)
        if gap < args.gap - 0.00001:
            violations.append(dict(kind='via_to_land', **item))
    for c, shape in bodies:
        gap = pt.distance(shape) - radius
        item = dict(via_xy=v['a'], via_net=v['net'], ref=c['ref'], gap_mm=gap)
        if gap < body_minimum[0]:
            body_minimum = (gap, item)
        if gap < 0.1 - 0.00001:
            violations.append(dict(kind='via_under_body_or_margin', **item))
pair_minimum = (float('inf'), None)
for i, v in enumerate(vias):
    for other in vias[:i]:
        gap = Point(v['a']).distance(Point(other['a'])) - (v['width']+other['width'])/2
        if gap < pair_minimum[0]:
            pair_minimum = (gap, dict(a=v['a'], b=other['a'], gap_mm=gap))
report = dict(source_pcb_sha256=digest, required_via_to_land_mm=args.gap,
              required_via_to_body_mm=0.1, same_net_included=True,
              contact_pads_J1_J2_included=True, via_count=len(vias),
              minimum_via_to_land_mm=minimum[0], minimum_via_to_land=minimum[1],
              minimum_via_to_body_mm=body_minimum[0], minimum_via_to_body=body_minimum[1],
              minimum_via_to_via_mm=pair_minimum[0], nearest_via_pair=pair_minimum[1],
              violations=violations, passed=not violations,
              limits=['Maximum nominal body envelopes; fabrication and assembly tolerances still apply.',
                      'Includes pads on both faces. Via-to-via separation is reported independently.',
                      'Does not predict solder bridging probability or prove electrical qualification.'])
args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
print('Via-to-land minimum:', round(minimum[0], 4), 'mm;', len(violations), 'clearance/body issues')
if violations:
    raise SystemExit(1)
