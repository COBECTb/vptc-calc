"""Extract exact native board copper for standalone review figures."""
from pathlib import Path
import json,hashlib
import pcbnew as p
R=Path(__file__).resolve().parents[1];b=p.LoadBoard(str(R/'encoder_can_v2.kicad_pcb'))
def xy(q):return [p.ToMM(q.x),p.ToMM(q.y)]
def chain(q):return [xy(q.CPoint(i)) for i in range(q.PointCount())]
poly=p.SHAPE_POLY_SET();assert b.GetBoardPolygonOutlines(poly,False)
d=dict(source_pcb_sha256=hashlib.sha256((R/'encoder_can_v2.kicad_pcb').read_bytes()).hexdigest(),outline=chain(poly.Outline(0)),outline_holes=[chain(poly.Hole(0,i)) for i in range(poly.HoleCount(0))],pads=[],tracks=[],zones=[],components=[])
sizes={c['ref']:c['size_mm'] for c in json.loads((R/'design/component_envelopes.json').read_text())}
sizes.update({'U2':[1.7,3,1.45],'U3':[1.7,3,1.45]})
for f in b.GetFootprints():
 side='F' if f.GetLayer()==p.F_Cu else 'B';ref=f.GetReference();d['components'].append(dict(ref=ref,side=side,xy=xy(f.GetPosition()),angle=f.GetOrientationDegrees(),size=sizes.get(ref)))
 for pad in f.Pads():d['pads'].append(dict(ref=ref,num=pad.GetNumber(),xy=xy(pad.GetPosition()),side=side,size=xy(pad.GetSize()),angle=pad.GetOrientationDegrees(),round=pad.GetShape()==p.PAD_SHAPE_CIRCLE,corner_mm=p.ToMM(pad.GetRoundRectCornerRadius()) if pad.GetShape()==p.PAD_SHAPE_ROUNDRECT else 0,hole=pad.GetAttribute()==p.PAD_ATTRIB_NPTH,net=pad.GetNetname()))
for t in b.GetTracks():
 via=isinstance(t,p.PCB_VIA);d['tracks'].append(dict(a=xy(t.GetStart()),z=xy(t.GetEnd()),via=via,layer=b.GetLayerName(t.GetLayer()),width=p.ToMM(t.GetWidth(p.F_Cu) if via else t.GetWidth()),drill=p.ToMM(t.GetDrill()) if via else 0,net=t.GetNetname()))
for z in b.Zones():
 ps=z.GetFilledPolysList(z.GetLayer())
 for i in range(ps.OutlineCount()):d['zones'].append(dict(layer=b.GetLayerName(z.GetLayer()),net=z.GetNetname(),outer=chain(ps.Outline(i)),holes=[chain(ps.Hole(i,j)) for j in range(ps.HoleCount(i))]))
(R/'design/review_geometry.json').write_text(json.dumps(d))
