#!/usr/bin/env python3
"""Generate the editable KiCad schematic from the checked electrical specification.

Run inside the pinned KiCad image: python3 scripts/build_schematic.py.
Library symbols are embedded unchanged (apart from alias expansion and root name).
Connectivity comes solely from design/electrical_spec.json, never from the 3D model.
"""
import copy
import json
import math
import os
import pathlib
import re
import uuid

ROOT = pathlib.Path(__file__).resolve().parents[1]
LIBDIR = pathlib.Path(os.environ.get('ENCODER_SYMBOL_DIR', str(ROOT / 'vendor/symbols')))
NAMESPACE = uuid.uuid5(uuid.NAMESPACE_URL, 'https://vptc-calc.local/encoder_can/rev-a')


def uid(name):
    return str(uuid.uuid5(NAMESPACE, name))


class Atom(str):
    pass


def parse(text):
    tokens = re.findall(r'"(?:\\.|[^"\\])*"|\(|\)|[^\s()]+', text)
    stack, root = [], None
    for tok in tokens:
        if tok == '(':
            x = []
            if stack:
                stack[-1].append(x)
            else:
                root = x
            stack.append(x)
        elif tok == ')':
            stack.pop()
        else:
            stack[-1].append(json.loads(tok) if tok.startswith('"') else Atom(tok))
    assert not stack
    return root


def dump(x, level=0):
    if isinstance(x, list):
        if not any(isinstance(v, list) for v in x):
            return '(' + ' '.join(dump(v) for v in x) + ')'
        return '(' + ' '.join(dump(v) for v in x if not isinstance(v, list)) + ''.join('\n' + '  ' * (level + 1) + dump(v, level + 1) for v in x if isinstance(v, list)) + ')'
    if isinstance(x, Atom):
        return str(x)
    if isinstance(x, str):
        return json.dumps(x, ensure_ascii=False)
    return str(x)


def node(tag, *args):
    return [Atom(tag), *args]


def num(v):
    return Atom(f'{v:.6f}'.rstrip('0').rstrip('.') if v else '0')


def get(x, tag, default=None):
    return next((v for v in x if isinstance(v, list) and v and v[0] == tag), default)


def nodes(x, tag):
    return [v for v in x if isinstance(v, list) and v and v[0] == tag]


library_cache = {}


def library(lib):
    if lib not in library_cache:
        p = LIBDIR / (lib + '.kicad_sym')
        if not p.exists():
            library_cache[lib] = {}
        else:
            library_cache[lib] = {str(x[1]): x for x in nodes(parse(p.read_text()), 'symbol')}
    return library_cache[lib]


def expand(lib, name):
    original = copy.deepcopy(library(lib)[name])
    ext = get(original, 'extends')
    if not ext:
        return original
    inherited = expand(lib, str(ext[1]))
    parent_name = str(inherited[1])
    inherited[1] = name
    # Internal sub-symbol names must follow their final owner after alias expansion.
    for subsymbol in nodes(inherited, 'symbol'):
        subsymbol[1] = name + str(subsymbol[1])[len(parent_name):]
    for prop in nodes(original, 'property'):
        inherited[:] = [p for p in inherited if not (isinstance(p, list) and p[:2] == prop[:2])]
        inherited.append(prop)
    for k in ('description', 'keywords', 'fp_filters'):
        value = get(original, k)
        if value is not None:
            inherited[:] = [p for p in inherited if not (isinstance(p, list) and p and p[0] == k)]
            inherited.append(value)
    return inherited


def choose(c):
    r = c['ref']
    if r in ('U2', 'U3', 'U5', 'D1'):
        return 'Encoder_CAN:' + c['value'].replace(',215', ''), local_symbol(c)
    if r == 'U1':
        choices = ['MCU_ST_STM32G4:STM32G431KBUx']
    elif r in ('U2', 'U3'):
        choices = ['Sensor_Magnetic:TMAG5273A2', 'Sensor_Magnetic:TMAG5273A2DBV', 'Sensor_Magnetic:TMAG5273A1', 'Sensor_Magnetic:TMAG5273']
    elif r == 'U4':
        choices = ['Interface_CAN_LIN:TCAN332GDCN', 'Interface_CAN_LIN:TCAN332G', 'Interface_CAN_LIN:TCAN332']
    elif r == 'U5':
        choices = ['Regulator_Linear:TPS7A2033PDBV', 'Regulator_Linear:TPS7A2033PDBVR', 'Regulator_Linear:TPS7A20']
    elif r == 'D1':
        choices = ['Power_Protection:PESD5V0S2BT', 'Protection:PESD5V0S2BT', 'Device:D_TVS_Dual_ACA']
    elif r == 'Y1':
        choices = ['Device:Crystal_GND24']
    elif r.startswith('R'):
        choices = ['Device:R']
    elif r.startswith('C'):
        choices = ['Device:C']
    elif r == 'J1':
        choices = ['Connector_Generic:Conn_01x04']
    elif r == 'J2':
        choices = ['Connector_Generic:Conn_01x05']
    elif r.startswith('TP'):
        choices = ['Connector:TestPoint']
    else:
        raise ValueError(r)
    for choice in choices:
        lib, name = choice.split(':')
        if name in library(lib):
            return choice, expand(lib, name)
    raise RuntimeError(f'No official library symbol for {r}: {choices}')


def local_symbol(c):
    """Checked parts missing from the pinned official library; meaningful ERC types."""
    name = c['value'].replace(',215', '')
    symbol = node('symbol', name, node('pin_names', node('offset', Atom('0.5'))), node('in_bom', Atom('yes')), node('on_board', Atom('yes')))
    symbol.extend([property_('Reference', c['ref'][0], 0, 12.7), property_('Value', name, 0, 10.16)])
    graphics = node('symbol', name + '_0_1', node('rectangle', node('start', Atom('-7.62'), Atom('7.62')), node('end', Atom('7.62'), Atom('-7.62')), node('stroke', node('width', Atom('0.254')), node('type', Atom('default'))), node('fill', node('type', Atom('background')))))
    symbol.append(graphics)
    ps = node('symbol', name + '_1_1')
    if c['ref'] in ('U2', 'U3'):
        definition = [('1', 'SCL', 'input', -10.16, 2.54, 0), ('6', 'SDA', 'bidirectional', -10.16, -2.54, 0), ('5', 'INT', 'bidirectional', 10.16, 0, 180), ('4', 'VCC', 'power_in', 0, 10.16, 270), ('2', 'GND', 'power_in', -2.54, -10.16, 90), ('3', 'TEST/GND', 'power_in', 2.54, -10.16, 90)]
    elif c['ref'] == 'U5':
        definition = [('1', 'IN', 'power_in', -10.16, 2.54, 0), ('3', 'EN', 'input', -10.16, -2.54, 0), ('5', 'OUT', 'power_out', 10.16, 2.54, 180), ('4', 'NC', 'no_connect', 10.16, -2.54, 180), ('2', 'GND', 'power_in', 0, -10.16, 90)]
    elif c['ref'] == 'D1':
        definition = [('1', 'K1', 'passive', -10.16, 2.54, 0), ('2', 'K2', 'passive', -10.16, -2.54, 0), ('3', 'COMMON/GND', 'passive', 10.16, 0, 180)]
    else:
        raise ValueError(c['ref'])
    for number, label, typ, x, y, angle in definition:
        ps.append(node('pin', Atom(typ), Atom('line'), node('at', num(x), num(y), Atom(str(angle))), node('length', Atom('2.54')), node('name', label, effects(1.05)), node('number', number, effects(1.05))))
    symbol.append(ps)
    return symbol


def all_pins(symbol):
    pins = []
    for subsymbol in nodes(symbol, 'symbol'):
        pins.extend(nodes(subsymbol, 'pin'))
    return pins


def effects(size=1.05, justify=None, hide=False):
    v = node('effects', node('font', node('size', num(size), num(size))))
    if justify:
        v.append(node('justify', Atom(justify)))
    if hide:
        v.append(node('hide', Atom('yes')))
    return v


def property_(name, value, x, y, hidden=False):
    return node('property', name, value, node('at', num(x), num(y), Atom('0')), effects(1.05, hide=hidden))


def main():
    spec = json.loads((ROOT / 'design/electrical_spec.json').read_text())
    root_id = uid('schematic-root')
    doc = node('kicad_sch', node('version', Atom('20250114')), node('generator', 'vptc_encoder_schematic'), node('generator_version', '1.0'), node('uuid', root_id), node('paper', 'A3'))
    doc.append(node('title_block', node('title', 'Dual-track absolute encoder / CAN'), node('date', '2026-10-11'), node('rev', 'A prototype'), node('company', 'vptc-calc'), node('comment', Atom('1'), '5 V input; 3.3 V logic; 2 x TMAG5273A2; 4 layers / 0.8 mm')))
    embedded = node('lib_symbols')
    doc.append(embedded)
    used = set()
    paths = {}
    positions = {'U1': (72.39, 81.28), 'U2': (180.34, 45.72), 'U3': (180.34, 91.44), 'U4': (274.32, 45.72), 'U5': (274.32, 96.52), 'D1': (353.06, 45.72), 'Y1': (353.06, 96.52), 'J1': (43.18, 269.24), 'J2': (119.38, 269.24), 'TP1': (187.96, 269.24)}
    passives = [c for c in spec['components'] if c['ref'][0] in ('R', 'C')]
    for i, c in enumerate(passives):
        positions[c['ref']] = (35.56 + (i % 7) * 53.34, 152.4 + (i // 7) * 27.94)
    for c in spec['components']:
        ref = c['ref']
        lib_id, symbol = choose(c)
        pins = all_pins(symbol)
        numbers = {str(get(p, 'number')[1]) for p in pins}
        if numbers != set(c['pins']):
            raise RuntimeError(f'{ref}: official symbol {lib_id} pins {sorted(numbers)} differ from checked spec {sorted(c["pins"])}')
        if lib_id not in used:
            symbol[1] = lib_id
            embedded.append(symbol)
            used.add(lib_id)
        x, y = positions[ref]
        sid = uid('symbol/' + ref)
        paths[ref] = {'uuid': sid, 'path': '/' + root_id + '/' + sid, 'lib_id': lib_id}
        fitted_part = ref not in ('J1', 'J2', 'TP1')
        inst = node('symbol', node('lib_id', lib_id), node('at', num(x), num(y), Atom('0')), node('unit', Atom('1')), node('in_bom', Atom('yes' if fitted_part else 'no')), node('on_board', Atom('yes')), node('dnp', Atom('yes' if c.get('dnp') else 'no')), node('uuid', sid))
        ys = [float(get(p, 'at')[2]) for p in pins]
        top = y - max(ys)
        if ref[0] in ('R', 'C'):
            ref_pos, value_pos = (x + 6.35, y - 1.27), (x + 6.35, y + 1.27)
        else:
            ref_pos, value_pos = (x, top - 15.24), (x, top - 12.7)
        inst.extend([property_('Reference', ref, *ref_pos), property_('Value', c['value'], *value_pos), property_('Footprint', c['footprint'], x, y, True), property_('Datasheet', '', x, y, True)])
        for key, value in [('Manufacturer', c.get('manufacturer', '')), ('MPN', c.get('mpn', ''))]:
            if value:
                inst.append(property_(key, value, x, y, True))
        for p in pins:
            number = str(get(p, 'number')[1])
            inst.append(node('pin', number, node('uuid', uid(ref + '/pin/' + number))))
            at = get(p, 'at')
            px, py, angle = x + float(at[1]), y - float(at[2]), float(at[3])
            net = c['pins'][number]
            if net is None:
                doc.append(node('no_connect', node('at', num(px), num(py)), node('uuid', uid(ref + '/nc/' + number))))
                continue
            rad = math.radians(angle)
            length = 5.08
            ex, ey = px - length * math.cos(rad), py + length * math.sin(rad)
            doc.append(node('wire', node('pts', node('xy', num(px), num(py)), node('xy', num(ex), num(ey))), node('stroke', node('width', Atom('0')), node('type', Atom('default'))), node('uuid', uid(ref + '/wire/' + number))))
            label_angle = 90 if angle in (90, 270) else 0
            justify = 'right' if angle == 0 else 'left'
            if angle == 90:
                justify = 'left'
            doc.append(node('global_label', net, node('shape', Atom('bidirectional')), node('at', num(ex), num(ey), Atom(str(label_angle))), effects(.95, justify), node('uuid', uid(ref + '/label/' + number))))
        inst.append(node('instances', node('project', 'encoder_can', node('path', '/' + root_id, node('reference', ref), node('unit', Atom('1'))))))
        doc.append(inst)
    # Input cable is the source of +5V and common GND. Explicit flags make ERC meaningful.
    lib_id = 'power:PWR_FLAG'
    flag = expand('power', 'PWR_FLAG')
    flag[1] = lib_id
    embedded.append(flag)
    for i, net in enumerate(('+5V', 'GND')):
        ref = '#FLG0' + str(i + 1)
        x, y = 259.08 + 40.64 * i, 238.76
        fid = uid(ref)
        inst = node('symbol', node('lib_id', lib_id), node('at', num(x), num(y), Atom('0')), node('unit', Atom('1')), node('in_bom', Atom('no')), node('on_board', Atom('no')), node('dnp', Atom('no')), node('uuid', fid), property_('Reference', ref, x, y - 5.08, True), property_('Value', 'PWR_FLAG', x, y - 2.54), node('pin', '1', node('uuid', uid(ref + '/pin/1'))), node('instances', node('project', 'encoder_can', node('path', '/' + root_id, node('reference', ref), node('unit', Atom('1'))))))
        doc.append(inst)
        doc.append(node('global_label', net, node('shape', Atom('bidirectional')), node('at', num(x), num(y), Atom('0')), effects(1.05, 'left'), node('uuid', uid(ref + '/net'))))
    doc.append(node('text', 'R9 DNP: fit 120 ohm only at physical CAN bus ends.\nJ2 VTREF is 3.3 V sense; power the board through J1.\nY1 ESR80/CL12, C13/C14 must be qualified on prototype.\nAbsolute angle requires two-track calibration and firmware.', node('at', num(230), num(124), Atom('0')), effects(1.15, 'left'), node('uuid', uid('design-notes'))))
    path = ROOT / 'encoder_can.kicad_sch'
    path.write_text(dump(doc) + '\n')
    (ROOT / 'design/schematic_paths.json').write_text(json.dumps({'root_uuid': root_id, 'components': paths}, indent=2) + '\n')
    print(f'Saved {path}: {len(spec["components"])} symbols, {len(spec["nets"])} nets')


if __name__ == '__main__':
    main()
