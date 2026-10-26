"""Bind route-cleanup changes to the reviewed baseline and immutable mechanics."""
from pathlib import Path
import json,math,hashlib
from shapely.geometry import Polygon,Point
from shapely import make_valid
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[1];before=json.loads((R/'design/cleanup_before_geometry.json').read_text());after=json.loads((R/'design/review_geometry.json').read_text());sha=hashlib.sha256((R/'encoder_can_v2.kicad_pcb').read_bytes()).hexdigest();assert after['source_pcb_sha256']==sha
assert before['outline']==after['outline'] and before['outline_holes']==after['outline_holes']
assert sorted(before['components'],key=lambda q:q['ref'])==sorted(after['components'],key=lambda q:q['ref'])
assert sorted(before['pads'],key=lambda q:(q['ref'],q['num'],q['side']))==sorted(after['pads'],key=lambda q:(q['ref'],q['num'],q['side']))
via_signature=lambda data:sorted((tuple(t['a']),t['width'],t['drill'],t['net']) for t in data['tracks'] if t['via'])
old_vias=set(via_signature(before));new_vias=set(via_signature(after));assert new_vias<=old_vias,'A retained via was moved or its drill/net changed'
removed_vias=old_vias-new_vias
old_mask=json.loads((R/'design/cleanup_before_mask_geometry.json').read_text());new_mask=json.loads((R/'design/mask_geometry.json').read_text());mask_signature=lambda d:sorted((q['ref'],q['num'],q['side'],q['net'],q['mask_expansion_mm']) for q in d['apertures'])
assert mask_signature(old_mask)==mask_signature(new_mask) and not new_mask['additional_mask_drawings']
def plane(data):
 def polys(s):return [s] if s.geom_type=='Polygon' else [q for c in getattr(s,'geoms',[]) for q in polys(c)]
 return unary_union([poly for z in data['zones'] if z['layer']=='In1.Cu' for poly in polys(make_valid(Polygon(z['outer'],z['holes'])))])
plane_difference=plane(before).symmetric_difference(plane(after));difference=plane_difference.area
allowed=unary_union([Point(xy).buffer(width/2+.4) for xy,width,drill,net in removed_vias]);assert plane(before).difference(plane(after)).area<.00001,'Removing unused vias must not reduce the ground plane'
assert plane_difference.difference(allowed).area<.00001,'Ground-plane changes extend beyond removed via antipads'
stats=[]
for label,data in [('before',before),('after',after)]:
 tracks=[t for t in data['tracks'] if not t['via']];length=[math.dist(t['a'],t['z']) for t in tracks]
 stats.append(dict(version=label,track_segments=len(tracks),via_count=sum(t['via'] for t in data['tracks']),sum_track_lengths_mm=sum(length),segments_shorter_than_point1mm=sum(x<.1 for x in length)))
assert stats[1]['track_segments']<stats[0]['track_segments'] and stats[1]['sum_track_lengths_mm']<stats[0]['sum_track_lengths_mm']
report=dict(source_pcb_sha256=sha,baseline_pcb_sha256=before['source_pcb_sha256'],outline_and_all_component_pad_positions_unchanged=True,retained_via_positions_and_drills_unchanged=True,removed_unused_vias=[dict(xy=xy,diameter_mm=width,drill_mm=drill,net=net) for xy,width,drill,net in sorted(removed_vias)],solder_mask_apertures_unchanged=True,in1_ground_symmetric_difference_mm2=difference,in1_ground_area_before_mm2=plane(before).area,in1_ground_area_after_mm2=plane(after).area,in1_changes_limited_to_removed_via_antipads=True,statistics=stats,passed=True,limits=['No unwanted mask apertures were present: mask openings remain the required solder lands and fiducials. U1 EP33 stays exposed for soldering.','Removed duplicate detours, tiny jogs and unnecessary parallel connections. Necessary capacitor return branches remain.','Statistics count native segments and summed lengths, including overlapping segments; they are not a physical copper-area measurement.'])
(R/'design/cleanup_audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report['statistics'],indent=2))
