#!/usr/bin/env python3
"""Export/import Specctra through the same KiCad version as the project."""
import pathlib
import sys
import pcbnew as pcb

ROOT = pathlib.Path(__file__).resolve().parents[1]
board = pcb.LoadBoard(str(ROOT/'encoder_can.kicad_pcb'))
nc = board.GetDesignSettings().m_NetSettings.GetDefaultNetclass()
nc.SetClearance(pcb.FromMM(.127))
nc.SetTrackWidth(pcb.FromMM(.15))
nc.SetViaDiameter(pcb.FromMM(.45))
nc.SetViaDrill(pcb.FromMM(.2))
mode = sys.argv[1]
if mode == 'export':
    ok = pcb.ExportSpecctraDSN(board, str(ROOT/'design/encoder_can.dsn'))
    print('DSN export', ok)
elif mode == 'import':
    ok = pcb.ImportSpecctraSES(board, str(ROOT/'design/encoder_can.ses'))
    print('SES import', ok)
    # No tracks are routed on In1.Cu: preserve an uninterrupted ground return.
    ground = next(n for n in board.GetNetsByNetcode().values() if n.GetNetname() == 'GND')
    zone = pcb.ZONE(board)
    zone.SetLayer(pcb.In1_Cu)
    zone.SetNetCode(ground.GetNetCode())
    zone.SetLocalClearance(pcb.FromMM(.127))
    zone.SetMinThickness(pcb.FromMM(.15))
    zone.SetPadConnection(pcb.ZONE_CONNECTION_FULL)
    outline = zone.Outline()
    outline.NewOutline()
    for x,y in [(99,65),(135,65),(135,134),(99,134)]:
        outline.Append(pcb.FromMM(x),pcb.FromMM(y))
    board.Add(zone)
    filler = pcb.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    pcb.SaveBoard(str(ROOT/'encoder_can.kicad_pcb'), board)
else:
    raise SystemExit('Use export or import')
