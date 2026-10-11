#!/usr/bin/env python3
"""Transfer placed component envelopes into the existing mechanical mockup."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = json.loads((ROOT/'design/electrical_spec.json').read_text())
places = json.loads((ROOT/'design/placements.json').read_text())
out = [
    '// Generated from design/placements.json by scripts/update_scad_components.py.',
    '// Mechanical envelopes, not manufacturing models.',
    'module placed_component(r,a,rotation,front,size,pcb_h,c) {',
    '  rotate([0,0,a]) translate([r,0,0]) rotate([0,0,rotation-a])',
    '    color(c) translate([0,0,front ? -size[2]/2 : pcb_h+size[2]/2]) cube(size,center=true);',
    '}',
    'module placed_pad(r,a,rotation,local_xy,size,pcb_h) {',
    '  rotate([0,0,a]) translate([r,0,pcb_h+size[2]/2]) rotate([0,0,rotation-a])',
    '    color("Goldenrod") translate([local_xy[0],-local_xy[1],0]) cube(size,center=true);',
    '}',
    'module encoder_can_placed_components(pcb_h=.8) {'
]
envelopes = []
for c in spec['components']:
    ref=c['ref']; p=places[ref]
    r,a,ang=p['r'],p['a'],p.get('angle',p['a'])
    if ref in ['U2','U3']:
        continue
    front=p.get('side','F')=='F'
    color='DimGray'
    if ref=='J1':
        for x in [-2.25,-.75,.75,2.25]:
            out.append(f'  placed_pad({r},{a},{ang},[{x},0],[1,2,.08],pcb_h); // {ref}')
        continue
    if ref=='J2':
        for y in [-2.54,-1.27,0,1.27,2.54]:
            out.append(f'  placed_pad({r},{a},{ang},[0,{y}],[1,1,.08],pcb_h); // {ref}')
        continue
    if ref=='TP1':
        out.append(f'  placed_pad({r},{a},{ang},[0,0],[1,1,.08],pcb_h); // {ref}')
        continue
    if ref=='U1': size=[5.1,5.1,.6]
    elif ref in ['U4','U5']: size=[3,3,c.get('max_height_mm',1.45)]
    elif ref=='D1': size=[3,3,1.1]
    elif ref=='Y1': size=[2.5,2,.5]; color='Silver'
    elif '0603' in c['footprint']: size=[1.6,.8,.95]; color='BurlyWood' if ref.startswith('C') else 'DimGray'
    elif '0402' in c['footprint']: size=[1,.5,.8]; color='BurlyWood' if ref.startswith('C') else 'DimGray'
    else: raise ValueError('Unknown envelope '+ref)
    out.append(f'  placed_component({r},{a},{ang},{str(front).lower()},{json.dumps(size)},pcb_h,"{color}"); // {ref}')
    envelopes.append({'ref':ref,'r':r,'a':a,'angle':ang,'front':front,'size_mm':size})
out += ['}', '']
# Keep the shallow carrier relief tied to the real MCU placement as well.
# It ends above the bearing's unchanged Z10 seating stop in the D70 assembly.
mcu=places['U1']
mcu_r,mcu_a,mcu_ang=mcu['r'],mcu['a'],mcu.get('angle',mcu['a'])
out += [
    'function encoder_can_mcu_height() = .6;',
    'module encoder_can_mcu_clearance(pcb_bottom_z=11,xy_gap=.2,z_gap=.15,eps=.01) {',
    f'  rotate([0,0,{mcu_a}]) translate([{mcu_r},0,pcb_bottom_z-encoder_can_mcu_height()-z_gap])',
    f'    rotate([0,0,{mcu_ang-mcu_a}]) translate([-5.1/2-xy_gap,-5.1/2-xy_gap,0])',
    '      cube([5.1+2*xy_gap,5.1+2*xy_gap,encoder_can_mcu_height()+z_gap+eps]);',
    '}', ''
]
(ROOT/'design/placed_components.scad').write_text('\n'.join(out))
(ROOT/'design/component_envelopes.json').write_text(json.dumps(envelopes,indent=2)+'\n')
print(f'Updated {len(envelopes)} component bodies and flat connector pads.')
