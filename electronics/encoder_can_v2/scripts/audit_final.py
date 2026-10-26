"""Read-only native V2 audit; complements KiCad ERC, DRC and schematic parity."""
from pathlib import Path
import sys,json,math,hashlib,collections,datetime
import pcbnew as p
R=Path(__file__).resolve().parents[1]
def xy(v):
    return p.ToMM(v.x), p.ToMM(v.y)


def local(q, origin, angle):
    x,y=q[0]-origin[0],q[1]-origin[1]; a=math.radians(angle)
    return x*math.cos(a)-y*math.sin(a),x*math.sin(a)+y*math.cos(a)


def distance_to_pad(q, pad):
    u,v=local(q,xy(pad.GetPosition()),pad.GetOrientationDegrees());w,h=xy(pad.GetSize())
    if pad.GetShape()==p.PAD_SHAPE_CIRCLE:
        return max(0,math.hypot(u,v)-w/2)
    # The enclosing rectangle is conservative for rounded rectangles/ovals.
    return math.hypot(max(abs(u)-w/2,0),max(abs(v)-h/2,0))


def crosses_rectangle(a,b,origin,angle,size,margin=0):
    a=local(a,origin,angle);b=local(b,origin,angle);lo,hi=0.,1.
    for i in (0,1):
        delta=b[i]-a[i];half=size[i]/2+margin
        if abs(delta)<1e-10:
            if abs(a[i])>half:return False
            continue
        v,w=(-half-a[i])/delta,(half-a[i])/delta
        lo=max(lo,min(v,w));hi=min(hi,max(v,w))
        if lo>hi:return False
    return True


b=p.LoadBoard(str(R/'encoder_can_v2.kicad_pcb'));fps={f.GetReference():f for f in b.GetFootprints()};pads=[q for f in fps.values() for q in f.Pads() if q.GetAttribute()==p.PAD_ATTRIB_SMD];vias=[t for t in b.GetTracks() if isinstance(t,p.PCB_VIA)];tracks=[t for t in b.GetTracks() if not isinstance(t,p.PCB_VIA)]
vip=[];mindrill=(100,None);near=[]
for v in vias:
 for pad in pads:
  d=distance_to_pad(xy(v.GetPosition()),pad)-p.ToMM(v.GetDrill())/2
  if d<mindrill[0]:mindrill=(d,(pad.GetParentFootprint().GetReference(),pad.GetNumber(),xy(v.GetPosition())))
  if d<-.00001:vip.append(dict(net=v.GetNetname(),ref=pad.GetParentFootprint().GetReference(),pad=pad.GetNumber(),via=xy(v.GetPosition())))
y=fps['Y1'];under=[]
for t in tracks:
 if t.GetLayer()==p.B_Cu and t.GetNetname() not in ['HSE_IN','HSE_OUT','GND'] and crosses_rectangle(xy(t.GetStart()),xy(t.GetEnd()),xy(y.GetPosition()),y.GetOrientationDegrees(),[2.5,2],p.ToMM(t.GetWidth())/2):under.append(dict(net=t.GetNetname(),a=xy(t.GetStart()),z=xy(t.GetEnd())))
placement=json.loads((R/'design/placement.json').read_text());placement_errors=[]
for ref,c in placement.items():
 if ref not in fps:continue
 f=fps[ref]
 if math.dist(xy(f.GetPosition()),c['position'])>2e-6 or abs((f.GetOrientationDegrees()-c['angle']+180)%360-180)>1e-5:placement_errors.append(ref)
op=json.loads((R/'design/hall_reference_v1.json').read_text());hall=[]
for ref in ['U2','U3']:
 f=fps[ref];o=op[ref];hall.append(dict(ref=ref,position_mm=xy(f.GetPosition()),angle=f.GetOrientationDegrees(),unchanged_from_v1=math.dist(xy(f.GetPosition()),o['position_mm'])<1e-6 and abs(f.GetOrientationDegrees()-o['angle_deg'])<1e-6))
drc=json.loads((R/'design/drc-final.json').read_text());erc=json.loads((R/'design/erc.json').read_text())
report=dict(date_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),source_sha256=hashlib.sha256((R/'encoder_can_v2.kicad_pcb').read_bytes()).hexdigest(),copper_layers=b.GetCopperLayerCount(),thickness_mm=p.ToMM(b.GetDesignSettings().GetBoardThickness()),segments=len(tracks),vias=len(vias),layer_segments=dict(collections.Counter(t.GetLayerName() for t in tracks)),widths_mm=sorted({round(p.ToMM(t.GetWidth()),6) for t in tracks}),via_dimensions_mm=sorted({(round(p.ToMM(v.GetWidth(p.F_Cu)),6),round(p.ToMM(v.GetDrill()),6)) for v in vias}),ground_plane_signal_tracks=sum(t.GetLayer()==p.In1_Cu for t in tracks),zones=[dict(layer=b.GetLayerName(z.GetLayer()),net=z.GetNetname(),filled=z.IsFilled(),filled_polygons=z.GetFilledPolysList(z.GetLayer()).OutlineCount(),area_mm2=z.GetFilledPolysList(z.GetLayer()).Area()/1e12) for z in b.Zones()],all_vias_tented_both_sides=all(v.IsTented(p.F_Cu) and v.IsTented(p.B_Cu) for v in vias),ignored_drc_checks=drc.get('ignored_checks',[]),via_drills_in_smd_pads=vip,minimum_drill_edge_to_pad_enclosing_rectangle_mm=mindrill[0],minimum_drill_location=mindrill[1],unrelated_back_routes_under_crystal=under,clock_vias=sum(v.GetNetname() in ['HSE_IN','HSE_OUT'] for v in vias),hall_positions=hall,placement_errors=placement_errors,drc_violations=len(drc['violations']),unconnected=len(drc['unconnected_items']),schematic_parity_issues=len(drc.get('schematic_parity',[])))
project=json.loads((R/'encoder_can_v2.kicad_pro').read_text())['board']['design_settings']
report['minimum_connection_width_mm']=project['rules']['min_connection']
report['connection_width_severity']=project['rule_severities']['connection_width']
report['erc_violations']=sum(len(sheet.get('violations',[])) for sheet in erc.get('sheets',[]))
(R/'design/layout_audit.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))

assert not vip and not under and not placement_errors,'Geometry audit failed; inspect layout_audit.json'
assert all(q['unchanged_from_v1'] for q in hall),'Hall placement changed'
assert report['minimum_connection_width_mm']>=.125 and report['connection_width_severity']=='error','Connection neck check must be enforced'
assert not any(report[k] for k in ['drc_violations','unconnected','schematic_parity_issues','erc_violations']),'CAD checks are not clean'
