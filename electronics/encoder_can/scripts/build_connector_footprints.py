#!/usr/bin/env python3
"""Local flat connection pads. No pin header height is available in the cap."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / 'Encoder_CAN.pretty'
LIB.mkdir(exist_ok=True)


def make(name, positions, size, labels):
    parts = [f'(footprint "{name}" (version 20241229) (generator "pcbnew")',
             '  (layer "F.Cu")', '  (attr smd exclude_from_pos_files exclude_from_bom)',
             f'  (property "Reference" "J" (at 0 -4) (layer "F.SilkS") (hide yes) (effects (font (size .6 .6) (thickness .1))))',
             f'  (property "Value" "{name}" (at 0 4) (layer "F.Fab") (hide yes) (effects (font (size .6 .6) (thickness .1))))']
    for i, ((x, y), label) in enumerate(zip(positions, labels), 1):
        parts += [f'  (pad "{i}" smd roundrect (at {x} {y}) (size {size[0]} {size[1]}) (layers "F.Cu" "F.Mask") (roundrect_rratio .2))',
                  f'  (fp_text user "{i}:{label}" (at {x} {y}) (layer "F.Fab") (effects (font (size .35 .35) (thickness .06))))']
    parts.append(')')
    (LIB / (name + '.kicad_mod')).write_text('\n'.join(parts) + '\n')


make('WirePads_1x04', [(-2.25, 0), (-.75, 0), (.75, 0), (2.25, 0)], (1.0, 2.0), ['5V', 'GND', 'CANH', 'CANL'])
make('SWD_Pogo_1x05', [(0, y * 1.27) for y in (-2, -1, 0, 1, 2)], (1, 1), ['3V3', 'GND', 'DIO', 'CLK', 'RST'])
