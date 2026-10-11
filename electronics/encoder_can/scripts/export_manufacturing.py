#!/usr/bin/env python3
"""Prepare assembly notes; export fabrication data only after clean KiCad checks.

No arguments: update the draft BOM and assembly instructions only.
--export: run ERC/DRC, then export the board with KiCad CLI.
--docker: use the pinned, already-installed kicad/kicad:10.0.6 image.
"""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'manufacturing'
IMAGE = 'kicad/kicad:10.0.6'
PAD_ONLY = {'J1', 'J2', 'TP1'}
GERBER_LAYERS = 'F.Cu,In1.Cu,In2.Cu,B.Cu,F.Mask,B.Mask,F.SilkS,B.SilkS,Edge.Cuts,F.Paste,B.Paste'


def natural(ref):
    return re.sub(r'\d+', lambda m: m.group().zfill(6), ref)


def requirements(component):
    ref = component['ref']
    if ref in PAD_ONLY:
        return 'PCB pads only; no fitted connector or purchasable component'
    if ref.startswith('R'):
        return '1%; >=0.1 W' if ref == 'R9' else '1%; 0402'
    if ref.startswith('C'):
        text = f"{component.get('dielectric', '')}; >={component.get('voltage_v', '')} V"
        if component['value'] in ('4.7uF', '1uF'):
            text += '; X5R allowed after DC-bias/effective-capacitance check'
        if component['value'] == '4.7uF':
            text += '; C11 effective capacitance must exceed 0.47 uF'
        if component['value'] == '18pF':
            text += '; initial value; tune HSE load on prototype'
        return text
    if ref == 'Y1':
        return '16 MHz; CL=12 pF; ESR<=80 ohm; confirm orderable configuration; ESR150 is not an automatic substitute'
    if ref in ('U2', 'U3'):
        return 'A2 variant; check pin-1 orientation; Hall point must align with its magnetic track'
    return '; '.join(component.get('notes', []))


def population(component):
    return component['ref'] not in PAD_ONLY and not component.get('dnp', False)


def procurement(component):
    if component['ref'] in PAD_ONLY:
        return 'PCB only; do not order'
    if component.get('dnp'):
        return 'DNP; do not fit by default'
    if not component.get('mpn'):
        return 'Exact MPN and supplier stock code required'
    if component['ref'] == 'Y1':
        return 'Order-code configuration; manufacturer/supplier confirmation required'
    if component.get('supplier_stock_code'):
        return 'Supplier code recorded; stock/substitution approval still required'
    return 'Manufacturer MPN selected; supplier stock not verified'


def write_csv(path, fields, rows):
    with path.open('w', newline='', encoding='utf-8-sig') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def prepare_assembly(spec, placements):
    OUT.mkdir(exist_ok=True)
    groups = {}
    details = []
    for component in spec['components']:
        ref = component['ref']
        fit = population(component)
        row = {
            'Reference': ref,
            'Value': component['value'],
            'Footprint': component['footprint'],
            'Manufacturer': component.get('manufacturer', ''),
            'MPN': component.get('mpn', ''),
            'Populate': 'Yes' if fit else 'No',
            'Supplier_stock_code': component.get('supplier_stock_code', ''),
            'Procurement_status': procurement(component),
            'Requirements': requirements(component),
        }
        side = placements.get(ref, {}).get('side', component.get('side', ''))
        details.append({**row, 'Design_side': 'Front' if side == 'F' else 'Back'})
        key = tuple(row[k] for k in row if k != 'Reference')
        groups.setdefault(key, {'row': row, 'refs': []})['refs'].append(ref)
    rows = []
    for group in groups.values():
        refs = sorted(group['refs'], key=natural)
        row = dict(group['row'])
        row['References'] = ', '.join(refs)
        row['Quantity_per_board'] = len(refs)
        row['Fitted_quantity_per_board'] = len(refs) if row['Populate'] == 'Yes' else 0
        row.pop('Reference')
        rows.append(row)
    fields = ['References', 'Quantity_per_board', 'Fitted_quantity_per_board', 'Value',
              'Footprint', 'Manufacturer', 'MPN', 'Populate', 'Supplier_stock_code',
              'Procurement_status', 'Requirements']
    write_csv(OUT / 'BOM.csv', fields, rows)
    write_csv(OUT / 'assembly_components.csv', ['Reference', *fields[3:], 'Design_side'], details)
    fitted = sum(population(c) for c in spec['components'])
    instructions = f'''Плата абсолютного энкодера CAN, опытная ревизия A

ИЗГОТОВЛЕНИЕ ПЛАТЫ
4 слоя, FR-4, общая толщина 0,8 мм. Рекомендуемое покрытие ENIG.
Порядок меди сверху вниз: F.Cu / In1.Cu / In2.Cu / B.Cu.
Внутренний In1.Cu используется как земля; In2.Cu — питание и сигналы.
Точный stackup, толщина меди и допуски согласуются с изготовителем.
Требования проекта: минимальный зазор 0,127 мм; основные дорожки 0,15 мм;
переходные отверстия диаметром 0,45 мм со сверлением 0,20 мм.
Не увеличивать готовую толщину до стандартных 1,6 мм: плата входит в крышку.
Gerber F.Paste/B.Paste — трафареты, не дополнительные слои меди.
Excellon — миллиметры, абсолютное начало координат, без зеркалирования.
Фрезеровка контура и внутренних вырезов определяется замкнутым Edge.Cuts.

СБОРКА
На плату по умолчанию устанавливается {fitted} компонентов.
BOM.csv сгруппирован; assembly_components.csv перечисляет обозначения по одному.
BOM является черновиком закупки: пустые MPN/stock code надо согласовать со сборщиком.
Заполненный MPN сам по себе не означает подтверждённое наличие.
Y1: ABM10-16.000MHZ-12-R80-3-D30-T, 16 МГц, CL12 пФ, ESR<=80 Ом.
Подтвердить наличие этой конфигурации; стандартный ESR150 автоматически не подходит.
R9 120 Ом — DNP. Установить только на двух физических концах CAN-шины всей собаки.
J1, J2 и TP1 — медные площадки платы, отдельные разъёмы/компоненты не устанавливать.
Не добавлять корпусные разъёмы: высота и положение ограничены редуктором.
U2 — внутреннее магнитное кольцо R23,5 мм; U3 — внешнее R29,5 мм.
Оба датчика на F.Cu. Проверять чувствительную точку, а не только центр корпуса.
Контроллер, CAN и LDO на B.Cu; пассивы и кварц могут находиться на F.Cu.
В итоговом CPL позиции и сторона берутся из PCB, а не из предварительных заметок.
Front/top соответствует F.Cu; Back/bottom соответствует B.Cu.
encoder_can_positions.csv сохраняет штатные углы KiCad и координаты в мм.
Экспорт не меняет знак X для нижней стороны и не зеркалирует позиции.
Сборщик должен сопоставить эти углы со своей библиотекой посадок и проверить pin 1
на предварительном просмотре обеих сторон; не зеркалировать нижнюю сторону дважды.
Центр вращения конструкции имеет координаты PCB X=100 мм, Y=100 мм.
Чувствительная точка TMAG смещена относительно начала footprint; CPL этого не меняет.
Центральную площадку U1 (33, GND) обязательно пропаять; девять окон пасты уже заданы.
Обязательно проверить ориентацию U1–U5, D1 и Y1 по pin 1 и сборочным слоям.
Номиналы C13/C14 18 пФ предварительные: уточнить запуск, частоту и drive level HSE.

ПОДКЛЮЧЕНИЕ
J1: 1=+5V, 2=GND, 3=CAN_H, 4=CAN_L.
J2: 1=+3V3 VTREF sense, 2=GND, 3=SWDIO, 4=SWCLK, 5=NRST.
TP1=BOOT0; по умолчанию подтянут к GND.
Питание только регулируемые 5 В, расчётный диапазон 4,5–5,5 В.
Не подключать аккумулятор напрямую; не подавать 5 В на J2 VTREF.
CAN всех узлов имеет общую землю; на общей шине ровно два терминатора 120 Ом.

ПРОВЕРКА ПЕРВОГО ПРОТОТИПА
Осмотр пайки, сопротивления питания, включение с ограничением тока.
Проверить 3,3 В, нагрев LDO, подключение SWD и устойчивый старт HSE.
Проверить оба независимых I2C, INT и обмен CAN на общей шине.
Прошивка и калибровка магнитных дорожек в производственный пакет не входят.
Для работы при включении нужны прошивка, номер сустава и сохранённая калибровка.
Проверить полный оборот, уникальность угла, влияние соседнего кольца и зазора.
Сначала квалифицировать малую опытную партию; затем тиражировать на 12+ суставов.

СОСТОЯНИЕ ЭКСПОРТА
Производственные Gerber/Excellon/CPL появляются только после отдельного --export.
Актуальность пакета подтверждает export_manifest.json с хешами исходников.
При изменении PCB или схемы старый производственный пакет нужно пересоздать.
'''
    (OUT / 'assembly_instructions.txt').write_text(instructions, encoding='utf-8')
    print(f'Prepared draft BOM and assembly notes: {fitted} fitted components/board.')


def cli_command(args):
    if not args.docker:
        return [args.kicad_cli]
    docker = args.docker_cli or shutil.which('docker')
    if not docker and Path('/Applications/Docker.app/Contents/Resources/bin/docker').exists():
        docker = '/Applications/Docker.app/Contents/Resources/bin/docker'
    if not docker:
        raise RuntimeError('Docker CLI not found; specify --docker-cli or use local kicad-cli.')
    return [str(docker), 'run', '--rm', '--platform', 'linux/amd64', '--network', 'none',
            '-v', f'{ROOT}:/work', '-w', '/work', '--entrypoint', 'kicad-cli', IMAGE]


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_hashes():
    return {str(p.relative_to(ROOT)): sha256(p) for p in
            [ROOT / 'encoder_can.kicad_pcb', ROOT / 'encoder_can.kicad_sch',
             ROOT / 'encoder_can.kicad_pro', ROOT / 'design/electrical_spec.json',
             ROOT / 'design/placements.json']}


def commands(stage):
    p = stage.relative_to(ROOT).as_posix()
    board, sch = 'encoder_can.kicad_pcb', 'encoder_can.kicad_sch'
    return [
        ['sch', 'erc', '--format', 'json', '--output', p + '/checks/erc.json',
         '--severity-all', '--exit-code-violations', sch],
        ['pcb', 'drc', '--format', 'json', '--output', p + '/checks/drc.json',
         '--severity-all', '--schematic-parity', '--refill-zones', '--exit-code-violations', board],
        ['pcb', 'export', 'gerbers', '--output', p + '/gerbers/', '--layers', GERBER_LAYERS,
         '--subtract-soldermask', '--check-zones', board],
        ['pcb', 'export', 'drill', '--output', p + '/drills/', '--format', 'excellon',
         '--drill-origin', 'absolute', '--excellon-units', 'mm', '--excellon-zeros-format',
         'decimal', '--excellon-separate-th', '--generate-map', '--map-format', 'pdf',
         '--generate-report', board],
        ['pcb', 'export', 'pos', '--output', p + '/encoder_can_positions.csv',
         '--format', 'csv', '--units', 'mm', '--side', 'both', '--smd-only', '--exclude-dnp', board],
    ]


def check_positions(path, spec):
    with path.open(newline='', encoding='utf-8-sig') as stream:
        rows = list(csv.DictReader(stream))
    if not rows or 'Ref' not in rows[0] or 'Side' not in rows[0]:
        raise RuntimeError('Unexpected KiCad CPL columns; inspect encoder_can_positions.csv.')
    actual = {r['Ref'] for r in rows}
    expected = {c['ref'] for c in spec['components'] if population(c)}
    if actual != expected or len(rows) != len(expected):
        raise RuntimeError(f'CPL assembly set differs from BOM: missing={sorted(expected-actual)}, extra={sorted(actual-expected)}')
    if any(r['Side'] not in ('top', 'bottom', 'front', 'back') for r in rows):
        raise RuntimeError('Unexpected CPL side convention; do not reinterpret automatically.')
    for ref in ('U2', 'U3'):
        row = next(r for r in rows if r['Ref'] == ref)
        if row['Side'] not in ('top', 'front'):
            raise RuntimeError(f'{ref} must be on the sensor/front side.')


def export(args, spec):
    base = cli_command(args)
    if args.dry_run:
        import shlex
        for cmd in commands(OUT / 'PREVIEW'):
            print(shlex.join(base + cmd))
        return
    before = source_hashes()
    version = subprocess.check_output(base + ['--version'], cwd=ROOT, text=True).strip()
    if not version.startswith('10.0.'):
        raise RuntimeError(f'Expected validated KiCad 10.0.x CLI; found {version!r}.')
    with tempfile.TemporaryDirectory(prefix='.export-', dir=OUT) as temp:
        stage = Path(temp)
        for name in ('checks', 'gerbers', 'drills'):
            (stage / name).mkdir()
        for index, cmd in enumerate(commands(stage)):
            print('KiCad: ' + ' '.join(cmd[:3]))
            result = subprocess.run(base + cmd, cwd=ROOT, text=True, capture_output=True)
            (stage / 'checks' / f'{index+1:02d}_cli.log').write_text(result.stdout + result.stderr, encoding='utf-8')
            if result.returncode:
                shutil.copytree(stage / 'checks', OUT / 'checks', dirs_exist_ok=True)
                raise RuntimeError(f'KiCad command failed ({result.returncode}); see manufacturing/checks/. No new fabrication package was published.')
            if index == 1 and source_hashes() != before:
                raise RuntimeError('CAD sources changed during checks; rerun after editing finishes.')
        check_positions(stage / 'encoder_can_positions.csv', spec)
        if source_hashes() != before:
            raise RuntimeError('CAD sources changed during export; generated files were not published.')
        with zipfile.ZipFile(stage / 'encoder_can_fabrication.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
            for folder in ('gerbers', 'drills'):
                for file in sorted((stage / folder).iterdir()):
                    if file.suffix.lower() in ('.pdf', '.rpt'):
                        continue
                    archive.write(file, file.name)
        for name in ('BOM.csv', 'assembly_components.csv', 'assembly_instructions.txt'):
            shutil.copy2(OUT / name, stage / name)
        manifest = {
            'revision': 'A prototype', 'kicad_version': version, 'source_sha256': before,
            'pcb': {'copper_layers': 4, 'thickness_mm': 0.8, 'suggested_finish': 'ENIG'},
            'checks': {'erc': 'zero violations', 'drc': 'zero violations with schematic parity'},
            'assembly': {'fitted_components': sum(population(c) for c in spec['components']),
                         'dnp': ['R9'], 'pads_only': sorted(PAD_ONLY),
                         'stock_codes_complete': all(c.get('mpn') and c.get('supplier_stock_code')
                                                     for c in spec['components'] if population(c))},
            'files_sha256': {str(f.relative_to(stage)): sha256(f)
                             for f in sorted(stage.rglob('*')) if f.is_file()},
        }
        (stage / 'export_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
        for file in stage.iterdir():
            target = OUT / file.name
            if file.is_dir():
                if target.exists():
                    shutil.rmtree(target)
                shutil.copytree(file, target)
            else:
                os.replace(file, target)
    print('Published checked Gerber, Excellon, and CPL in manufacturing/.')
    print('BOM still requires supplier MPN/stock confirmation before assembly ordering.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--export', action='store_true', help='Run clean ERC/DRC gates, then export manufacturing files.')
    parser.add_argument('--dry-run', action='store_true', help='Print export commands; no CAD checks or fabrication export.')
    parser.add_argument('--docker', action='store_true', help=f'Use the installed {IMAGE} container.')
    parser.add_argument('--docker-cli', help='Path to the Docker executable.')
    parser.add_argument('--kicad-cli', default=os.environ.get('KICAD_CLI', 'kicad-cli'), help='Local KiCad CLI path.')
    args = parser.parse_args()
    spec = json.loads((ROOT / 'design/electrical_spec.json').read_text())
    placements = json.loads((ROOT / 'design/placements.json').read_text())
    prepare_assembly(spec, placements)
    if args.export:
        export(args, spec)
    elif args.dry_run:
        parser.error('--dry-run requires --export')
    else:
        print('No Gerber/Excellon/CPL export requested. Use --export after completing PCB review.')


if __name__ == '__main__':
    try:
        main()
    except (OSError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f'Export stopped: {error}', file=sys.stderr)
        raise SystemExit(1)
