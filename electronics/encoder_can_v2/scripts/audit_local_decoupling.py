"""Verify capacitor supply and return paths on their component face.

Uses saved, filled copper; does not infer high-frequency impedance or model EMC.
"""
from pathlib import Path
import hashlib
import json
import math
from shapely.geometry import Point, LineString, Polygon, box
from shapely.affinity import rotate, translate
from shapely.ops import unary_union

R = Path(__file__).resolve().parents[1]
d = json.loads((R/'design/review_geometry.json').read_text())
digest = hashlib.sha256((R/'encoder_can_v2.kicad_pcb').read_bytes()).hexdigest()
assert d['source_pcb_sha256'] == digest
pads = {(p['ref'], p['num']): p for p in d['pads']}


def shape(p):
    w, h = p['size']
    r = p.get('corner_mm', 0)
    g = (Point(0, 0).buffer(w/2, quad_segs=64) if p['round'] else
         box(-w/2+r, -h/2+r, w/2-r, h/2-r).buffer(r, quad_segs=32)
         if r else box(-w/2, -h/2, w/2, h/2))
    return translate(rotate(g, -p['angle'], origin=(0, 0)), *p['xy'])


def same_face_path(pp, qq):
    assert pp['side'] == qq['side'] and pp['net'] == qq['net']
    layer, net = pp['side']+'.Cu', pp['net']
    shapes = [shape(p) for p in d['pads'] if p['side']+'.Cu' == layer and p['net'] == net]
    shapes += [(Point(t['a']).buffer(t['width']/2) if t['via'] else
                LineString([t['a'], t['z']]).buffer(t['width']/2))
               for t in d['tracks'] if t['net'] == net and (t['via'] or t['layer'] == layer)]
    shapes += [Polygon(z['outer'], z['holes']) for z in d['zones']
               if z['net'] == net and z['layer'] == layer]
    copper = unary_union(shapes)
    return any(g.buffer(.00001).covers(Point(pp['xy'])) and
               g.buffer(.00001).covers(Point(qq['xy']))
               for g in getattr(copper, 'geoms', [copper]))


checks = []
for ref, vpin, gpin, cap in [('U1','1','32','C1'), ('U1','17','16','C2'),
                            ('U2','4','3','C6'), ('U3','4','3','C7'),
                            ('U4','3','2','C8'), ('U5','1','2','C10'),
                            ('U5','5','2','C11')]:
    vv, gg, cv, cg = [pads[k] for k in [(ref,vpin), (ref,gpin), (cap,'1'), (cap,'2')]]
    row = dict(ic=ref, capacitor=cap, face=vv['side'],
               supply_connected_on_same_face=same_face_path(vv, cv),
               return_connected_on_same_face=same_face_path(gg, cg),
               supply_pad_center_distance_mm=math.dist(vv['xy'], cv['xy']))
    checks.append(row)
report = dict(source_pcb_sha256=digest, checks=checks,
              passed=all(q['supply_connected_on_same_face'] and
                         q['return_connected_on_same_face'] for q in checks),
              limits=['Same-face geometric connectivity includes filled ground pours.',
                      'This does not measure loop inductance, supply impedance or EMC.'])
(R/'design/local_decoupling_audit.json').write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps(report, indent=2))
assert report['passed'], 'A bypass capacitor relies on an indirect layer transition'
