"""Compare native Edge.Cuts against the user's original, pre-enlargement outline."""
from pathlib import Path
import hashlib,json,math
from schematic_sexpr import parse,get,nodes
R=Path(__file__).resolve().parents[1];src=R/'encoder_can_v2.kicad_pcb'
ref=json.loads((R/'design/narrow_outline_reference.json').read_text());board=parse(src.read_text())
actual=sorted(sorted([get(q,'start')[1:3],get(q,'end')[1:3]]) for q in nodes(board,'gr_line') if get(q,'layer')[1]=='Edge.Cuts')
assert actual==ref['edge_lines_mm'],'Outline differs from original narrow board'
assert not any(get(q,'layer')[1]=='Edge.Cuts' for q in nodes(board,'gr_arc'))
g=json.loads((R/'design/review_geometry.json').read_text());digest=hashlib.sha256(src.read_bytes()).hexdigest();assert g['source_pcb_sha256']==digest
assert not g.get('outline_holes',[]),'Original narrow M3 accesses must remain open notches'
a=math.radians(9);local=[((x-100)*math.cos(a)+(100-y)*math.sin(a),-(x-100)*math.sin(a)+(100-y)*math.cos(a)) for x,y in g['outline']]
span=[max(p[j] for p in local)-min(p[j] for p in local) for j in (0,1)]
report=dict(source_pcb_sha256=digest,reference_backup_sha256=ref['source_sha256'],exact_original_edge_lines=True,profile_segments=len(actual),closed_internal_cutouts=0,local_envelope_mm=span,passed=True)
(R/'design/narrow_outline_audit.json').write_text(json.dumps(report,indent=2)+'\n');print('Exact original narrow profile:',len(actual),'segments, envelope',span)
