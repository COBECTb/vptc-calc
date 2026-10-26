"""Check straight, staggered MCU exits against exported native copper.

This checks actual tracks and vias, rather than trusting the routing plan.
Run export_views.py first. It does not replace native connectivity/width DRC.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
from shapely.geometry import LineString, Point
from shapely.ops import unary_union

ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
args = ap.parse_args()
root = args.root
pcb = root / 'encoder_can_v2.kicad_pcb'
sha = hashlib.sha256(pcb.read_bytes()).hexdigest()
d = json.loads((root / 'design/review_geometry.json').read_text())
assert d['source_pcb_sha256'] == sha, 'Export geometry from the saved PCB again'
mcu = next(c for c in d['components'] if c['ref'] == 'U1')
angle = math.radians(mcu['angle'] - 90)
ux = (math.cos(angle), -math.sin(angle))
uy = (-math.sin(angle), -math.cos(angle))
pads = {(p['ref'], p['num']): p for p in d['pads']}
vias = [t for t in d['tracks'] if t['via']]
tracks = [t for t in d['tracks'] if not t['via'] and t['layer'] == 'B.Cu' and t['width'] >= .125]
groups = [('bottom', ['4', '5', '6'], (0, -1)),
          ('top', ['18', '19', '21', '22', '23', '24'], (0, 1)),
          ('left', ['9', '10'], (-1, 0)),
          ('right', ['25', '30', '31'], (1, 0))]
# These three routes continue on B.Cu at the staggered bend. They need no
# drilled transition. Verify the real bend and outgoing copper, not a dummy via.
same_face_exits = {'5': 1.65, '19': 1.95, '9': 1.95}
rows, violations = [], []
for group, pins, local_normal in groups:
    normal = tuple(local_normal[0]*ux[i] + local_normal[1]*uy[i] for i in (0, 1))
    along = []
    for pin in pins:
        pad = pads['U1', pin]
        origin = pad['xy']

        def projection(q):
            delta = [q[i] - origin[i] for i in (0, 1)]
            return (sum(delta[i]*normal[i] for i in (0, 1)),
                    delta[0]*normal[1] - delta[1]*normal[0])

        candidates = []
        for via in vias:
            dist, off = projection(via['a'])
            if via['net'] == pad['net'] and .9 <= dist <= 2.1 and abs(off) <= .002:
                candidates.append((dist, via))
        via = None
        if pin in same_face_exits:
            if candidates:
                violations.append(dict(group=group, pin=pin, reason='Unnecessary via at a same-face bend'))
            bends = []
            for track in tracks:
                if track['net'] != pad['net']:
                    continue
                pa, pz = [projection(track[k]) for k in ('a', 'z')]
                if max(abs(pa[1]), abs(pz[1])) <= .002:
                    continue
                for key, pr in [('a', pa), ('z', pz)]:
                    if abs(pr[1]) <= .002 and abs(pr[0] - same_face_exits[pin]) <= .05:
                        bends.append((pr[0], track[key]))
            if not bends:
                violations.append(dict(group=group, pin=pin, reason='No outgoing B.Cu branch at the expected straight exit'))
                along.append(None)
                continue
            dist, target = max(bends)
        elif len(candidates) != 1:
            violations.append(dict(group=group, pin=pin, reason='Expected one outward, collinear escape via', count=len(candidates)))
            along.append(None)
            continue
        else:
            dist, via = candidates[0]
            target = via['a']
            copper_layers = {t['layer'] for t in d['tracks']
                             if not t['via'] and t['net'] == pad['net']
                             and LineString([t['a'], t['z']]).distance(Point(target))
                             <= max(.001, (via['width'] - t['width'])/2)}
            if len(copper_layers) < 2:
                violations.append(dict(group=group, pin=pin, reason='Via does not connect two copper layers'))
        collinear = []
        for track in tracks:
            if track['net'] != pad['net']:
                continue
            if max(abs(projection(track[k])[1]) for k in ('a', 'z')) <= .002:
                collinear.append(LineString([track['a'], track['z']]).buffer(.003))
        direct = unary_union(collinear).covers(LineString([origin, target]))
        if not direct:
            violations.append(dict(group=group, pin=pin, reason='Straight B.Cu track is interrupted or bends before via'))
        rows.append(dict(group=group, pin=pin, net=pad['net'], pad_xy=origin,
                         kind='through_via' if via else 'same_face_bend',
                         via_xy=via['a'] if via else None, exit_xy=target,
                         normal_distance_mm=dist, direct_track=direct))
        along.append(dist)
    for i in range(1, len(along)):
        if along[i] is None or along[i-1] is None:
            continue
        if abs(along[i] - along[i-1]) < .45:
            violations.append(dict(group=group, pins=pins[i-1:i+1], reason='Neighboring escape depths do not alternate by at least 0.45 mm'))
        if i >= 2 and along[i-2] is not None and abs(along[i] - along[i-2]) > .025:
            violations.append(dict(group=group, pins=pins[i-2:i+1], reason='Short/long stagger pattern is inconsistent'))
report = dict(source_pcb_sha256=sha, expected_escape_count=14, checked_escapes=rows,
              expected_through_vias=11, expected_same_face_bends=3,
              straight_track_min_width_mm=.125, collinearity_tolerance_mm=.002,
              minimum_stagger_mm=.45, violations=violations, passed=not violations,
              limits=['Nominal geometry only; native DRC, body/land clearance and electrical/mechanical audits are required separately.'])
(root / 'design/fanout_audit.json').write_text(json.dumps(report, indent=2) + '\n')
print('Straight staggered escapes:', len(rows), '/14;', len(violations), 'issues')
if violations:
    raise SystemExit(1)
