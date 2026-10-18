"""Read-only direct-contact signal graph audit, independent of KiCad DRC.

GetConnectedItems is deliberately not used: it returns the complete component.
Edges here require native copper-shape contact on a shared layer.
The suggested tree retains a path to every numbered electrical pad.
Never apply its suggestions without native DRC and topology verification.
"""
from pathlib import Path
import pcbnew as p
import json, math, heapq, hashlib
R=Path(__file__).resolve().parents[1]
b=p.LoadBoard(str(R/'encoder_can_v2.kicad_pcb'))
layers=[p.F_Cu,p.In1_Cu,p.In2_Cu,p.B_Cu]
objects={}
for t in b.GetTracks():
    if t.GetNetname() not in ['GND','+3V3','+5V']:
        objects.setdefault(t.GetNetname(),[]).append(t)
for f in b.GetFootprints():
    for q in f.Pads():
        if q.GetNumber() and q.GetNetname() in objects:
            objects[q.GetNetname()].append(q)
result=[]
for net,items in objects.items():
    pads=[i for i,q in enumerate(items) if isinstance(q,p.PAD)]
    if not pads:raise RuntimeError(('signal with no terminals',net))
    shapes=[{layer:q.GetEffectiveShape(layer) for layer in layers if q.IsOnLayer(layer)} for q in items]
    edges=[[] for q in items]
    for i in range(len(items)):
        for j in range(i):
            if any(shapes[i][l].Collide(shapes[j][l]) for l in shapes[i].keys() & shapes[j].keys()):
                edges[i].append(j);edges[j].append(i)
    def weight(i):
        q=items[i]
        if isinstance(q,p.PAD):return 0
        if isinstance(q,p.PCB_VIA):return 1.15
        return (q.GetStart()-q.GetEnd()).EuclideanNorm()/1e6+.10
    root=min(pads,key=lambda i:(items[i].GetParentFootprint().GetReference() not in ['U1','J1'],items[i].GetParentFootprint().GetReference(),items[i].GetNumber()))
    cost={root:0.};prev={};todo=[(0.,root)]
    while todo:
        g,i=heapq.heappop(todo)
        if g!=cost[i]:continue
        for j in edges[i]:
            value=g+weight(j)
            if value<cost.get(j,math.inf):
                cost[j]=value;prev[j]=i;heapq.heappush(todo,(value,j))
    assert all(i in cost for i in pads),('unreachable pad',net)
    keep=set(pads)
    for i in pads:
        while i!=root:keep.add(i);i=prev[i]
        keep.add(root)
    remove=[];internal=[]
    for i,q in enumerate(items):
        if i in keep:continue
        entry=dict(uuid=q.m_Uuid.AsString(),net=net,kind='via' if isinstance(q,p.PCB_VIA) else 'track',layer=q.GetLayerName(),length_mm=0 if isinstance(q,p.PCB_VIA) else (q.GetStart()-q.GetEnd()).EuclideanNorm()/1e6)
        # Keep an explicit route endpoint at the centre of a round test pad.
        # A capsule is contained in a circle iff both endpoint discs are.
        inside=not isinstance(q,p.PCB_VIA) and any(items[j].GetShape()==p.PAD_SHAPE_CIRCLE and items[j].IsOnLayer(q.GetLayer()) and max((q.GetStart()-items[j].GetPosition()).EuclideanNorm(),(q.GetEnd()-items[j].GetPosition()).EuclideanNorm())+q.GetWidth()/2 <= items[j].GetSize().x/2 for j in pads)
        (internal if inside else remove).append(entry)
    result.append(dict(net=net,pads=len(pads),items=len(items),suggested_remove=remove,retained_inside_round_pad=internal))
report=dict(source_sha256=hashlib.sha256((R/'encoder_can_v2.kicad_pcb').read_bytes()).hexdigest(),nets=result)
(R/'design/signal_route_audit.json').write_text(json.dumps(report,indent=2)+'\n')
print('External redundant signal candidates:',sum(len(n['suggested_remove']) for n in result))
for n in result:
    if n['suggested_remove']:print(n['net'],len(n['suggested_remove']),round(sum(q['length_mm'] for q in n['suggested_remove']),3),'mm')
