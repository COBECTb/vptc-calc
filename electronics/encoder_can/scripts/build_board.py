#!/usr/bin/env python3
"""Build the encoder PCB with KiCad's pcbnew API; dimensions are millimetres.

Run in the pinned KiCad container, from electronics/encoder_can.
Electrical connectivity is supplied by design/electrical_spec.json.
"""
import json
import math
import pathlib
import uuid
import xml.etree.ElementTree as ET
import pcbnew as pcb

ROOT = pathlib.Path(__file__).resolve().parents[1]
ORIGIN = (100.0, 100.0)


def v(x, y):
    return pcb.VECTOR2I(pcb.FromMM(x), pcb.FromMM(y))


def polar(r, a):
    a = math.radians(a)
    return ORIGIN[0] + r * math.cos(a), ORIGIN[1] - r * math.sin(a)


def segment(board, p1, p2, layer, width=.15, net=None):
    t = pcb.PCB_TRACK(board)
    t.SetStart(v(*p1))
    t.SetEnd(v(*p2))
    t.SetLayer(layer)
    t.SetWidth(pcb.FromMM(width))
    if net:
        t.SetNet(net)
    board.Add(t)
    return t


def draw_line(board, p1, p2, layer=pcb.Edge_Cuts, width=.05):
    s = pcb.PCB_SHAPE()
    s.SetShape(pcb.SHAPE_T_SEGMENT)
    s.SetStart(v(*p1))
    s.SetEnd(v(*p2))
    s.SetLayer(layer)
    s.SetWidth(pcb.FromMM(width))
    board.Add(s)


def footprint(board, ref, value, lib_id, r, a, side='F', angle=None):
    lib, name = lib_id.split(':', 1)
    libpath = ROOT / (lib + '.pretty') if lib == 'Encoder_CAN' else ROOT / 'vendor' / (lib + '.pretty')
    fp = pcb.FootprintLoad(str(libpath), name)
    if fp is None:
        raise RuntimeError(f'Footprint unavailable: {lib_id}')
    fp.SetReference(ref)
    fp.SetValue(value)
    fp.SetFPID(pcb.LIB_ID(lib, name))
    # KiCad10 Flip requires the board layer stack; attach before flipping.
    board.Add(fp)
    pos = v(*polar(r, a))
    fp.SetPosition(pos)
    if side == 'B':
        fp.Flip(pos, False)
    fp.SetOrientationDegrees(a if angle is None else angle)
    for item in (fp.Reference(), fp.Value()):
        item.SetVisible(False)
    return fp


def main():
    spec = json.loads((ROOT / 'design/electrical_spec.json').read_text())
    mechanics = json.loads((ROOT / 'design/mechanics.json').read_text())
    placements = json.loads((ROOT / 'design/placements.json').read_text())
    paths = json.loads((ROOT / 'design/schematic_paths.json').read_text())
    board = pcb.BOARD()
    board.SetCopperLayerCount(4)
    ds = board.GetDesignSettings()
    ds.SetBoardThickness(pcb.FromMM(.8))
    ds.m_TrackMinWidth = pcb.FromMM(.127)
    ds.m_MinClearance = pcb.FromMM(.127)
    ds.m_CopperEdgeClearance = pcb.FromMM(.25)
    ds.m_MinThroughDrill = pcb.FromMM(.2)
    ds.m_ViasMinSize = pcb.FromMM(.45)
    nc = ds.m_NetSettings.GetDefaultNetclass()
    nc.SetClearance(pcb.FromMM(.127))
    nc.SetTrackWidth(pcb.FromMM(.15))
    nc.SetViaDiameter(pcb.FromMM(.45))
    nc.SetViaDrill(pcb.FromMM(.2))
    # The exported schematic also names each explicitly unconnected pad.
    netlist = ET.parse(ROOT/'design/netlist.xml').getroot()
    connectivity = {}
    for n in netlist.findall('./nets/net'):
        for pad in n.findall('node'):
            connectivity[(pad.get('ref'),pad.get('pin'))] = n.get('name')
    netnames = sorted(set(connectivity.values()))
    nets = {}
    for name in netnames:
        net = pcb.NETINFO_ITEM(board, name)
        board.Add(net)
        nets[name] = net
    components = {}
    for c in spec['components']:
        p = placements[c['ref']]
        fp = footprint(board, c['ref'], c['value'], c['footprint'], p['r'], p['a'], p.get('side', 'F'), p.get('angle'))
        path = pcb.KIID_PATH()
        for item in paths['components'][c['ref']]['path'].strip('/').split('/'):
            path.push_back(pcb.KIID(item))
        fp.SetPath(path)
        for pad in fp.Pads():
            name = connectivity.get((c['ref'],pad.GetNumber()))
            if name:
                pad.SetNet(nets[name])
        if c.get('dnp'):
            fp.SetDNP(True)
        for key, source in [('Manufacturer','manufacturer'),('MPN','mpn')]:
            if c.get(source):
                fp.SetField(key,c[source])
                fp.GetField(key).SetVisible(False)
        components[c['ref']] = fp
    # The mechanical outline is supplied as an exact closed boundary.
    for arc in mechanics['outline']['edges']:
        if arc['type'] == 'line':
            draw_line(board, arc['start_kicad_mm'], arc['end_kicad_mm'])
        else:
            s = pcb.PCB_SHAPE()
            s.SetShape(pcb.SHAPE_T_ARC)
            s.SetArcGeometry(v(*arc['start_kicad_mm']), v(*arc['mid_kicad_mm']), v(*arc['end_kicad_mm']))
            s.SetLayer(pcb.Edge_Cuts)
            s.SetWidth(pcb.FromMM(.05))
            board.Add(s)
    for hole in mechanics['mount_holes']:
        fp = footprint(board, hole['reference'], 'M2 NPTH', 'MountingHole:MountingHole_2.2mm_M2', hole['radius_from_axis_mm'], hole['angle_scad_deg'])
        fp.SetExcludedFromBOM(True)
        fp.SetExcludedFromPosFiles(True)
        fp.SetAttributes(fp.GetAttributes() | pcb.FP_BOARD_ONLY)
    # Escape the two outer MCU pads before autorouting. The small fanout
    # avoids a crowded escape between the adjacent 0.5 mm pitch pads.
    for number in ('21', '22', '23'):
        pad = next(p for p in components['U1'].Pads() if p.GetNumber() == number)
        pos = pad.GetPosition()
        end = (132.64 if number == '22' else 132.20, pcb.ToMM(pos.y))
        segment(board, (pcb.ToMM(pos.x), pcb.ToMM(pos.y)), end, pcb.B_Cu, net=pad.GetNet())
        via = pcb.PCB_VIA(board)
        via.SetPosition(v(*end))
        via.SetWidth(pcb.FromMM(.45))
        via.SetDrill(pcb.FromMM(.2))
        via.SetViaType(pcb.VIATYPE_THROUGH)
        via.SetLayerPair(pcb.F_Cu, pcb.B_Cu)
        via.SetNet(pad.GetNet())
        board.Add(via)
    board.SetFileName(str(ROOT / 'encoder_can.kicad_pcb'))
    pcb.SaveBoard(board.GetFileName(), board)
    print(f'Saved {len(components)} components / {len(nets)} nets: {board.GetFileName()}')


if __name__ == '__main__':
    main()
