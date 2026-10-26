"""Export actual solder-mask apertures separately from the copper-only figures."""
from pathlib import Path
import pcbnew as p,json,hashlib
R=Path(__file__).resolve().parents[1];b=p.LoadBoard(str(R/'encoder_can_v2.kicad_pcb'));fs=list(b.GetFootprints());pads=[q for f in fs for q in f.Pads()];data=[];other=[]
for f in fs:
 for q in f.Pads():
  if q.GetAttribute()==p.PAD_ATTRIB_NPTH:continue
  for layer,side in [(p.F_Mask,'F'),(p.B_Mask,'B')]:
   if q.IsOnLayer(layer):data.append(dict(ref=f.GetReference(),num=q.GetNumber(),side=side,net=q.GetNetname(),mask_expansion_mm=p.ToMM(q.GetSolderMaskExpansion(p.F_Cu if side=='F' else p.B_Cu))))
 for q in list(f.GraphicalItems()):
  if q.GetLayer() in [p.F_Mask,p.B_Mask]:other.append(dict(ref=f.GetReference(),type=type(q).__name__))
for q in b.GetDrawings():
 if q.GetLayer() in [p.F_Mask,p.B_Mask]:other.append(dict(ref='board',type=type(q).__name__))
report=dict(source_pcb_sha256=hashlib.sha256((R/'encoder_can_v2.kicad_pcb').read_bytes()).hexdigest(),apertures=data,additional_mask_drawings=other)
(R/'design/mask_geometry.json').write_text(json.dumps(report,indent=2)+'\n');print('Mask apertures:',len(data),'; additional drawings:',len(other))
