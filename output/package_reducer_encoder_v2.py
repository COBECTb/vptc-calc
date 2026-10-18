"""Bundle the checked mechanical prototype and all OpenSCAD use/include dependencies."""
from pathlib import Path
import csv
import hashlib
import io
import json
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output'
PRINT_PARTS = [
    ('Основание', 1, 'reducer_encoder_v2_cap.stl', 'Как в файле', ''),
    ('Защитная крышка', 1, 'reducer_encoder_v2_lid.stl', 'Наружной ровной стороной вниз', 'Карманы открыты вверх'),
    ('Соединитель редуктора', 1, 'reducer_encoder_v2_output_connector.stl', 'Фланцем вниз', 'Шейка 6.75 мм'),
    ('Второй соединитель', 1, 'reducer_encoder_v2_load_connector.stl', 'Фланцем вниз', 'Поддержки под началом юбки'),
    ('Полузажим', 2, 'connector_clamp_body_for_print.stl', 'Дугой концами на столе', 'Два одинаковых экземпляра'),
    ('Магнитное полукольцо', 2, 'connector_clamp_magnet_ring_half_0p8.stl', 'Плашмя', '0.8 мм, два одинаковых экземпляра'),
]


def build():
    files = {}

    def include(path):
        path = path.resolve()
        name = path.relative_to(ROOT).as_posix()
        if name in files:
            return
        files[name] = path.read_bytes()
        if path.suffix == '.scad':
            for dependency in re.findall(r'^\s*(?:use|include)\s*<([^>]+)>', path.read_text(), re.M):
                include(path.parent / dependency)

    for name in ['reducer_cap_encoder_can.scad', 'reducer_encoder_v2_checks.scad',
                 'reducer_encoder_v2_output_connector.scad', 'reducer_encoder_v2_load_connector.scad',
                 'connector_clamp_body_for_print.scad', 'connector_clamp_magnet_ring_half_0p8.scad']:
        include(OUT / name)
    for _, _, filename, _, _ in PRINT_PARTS:
        include(OUT / filename)
    for name in ['reducer_encoder_v2_README.md', 'reducer_encoder_v2_fit.json',
                 'reducer_encoder_v2_preview.png']:
        include(OUT / name)
    include(ROOT / 'electronics/encoder_can_v2/PROGRAMMING.md')
    for log in sorted((OUT / 'reducer_encoder_v2_check_logs').glob('*.log')):
        include(log)
    listing = io.StringIO(newline='')
    writer = csv.writer(listing)
    writer.writerow(['Деталь', 'Количество', 'STL в папке output', 'Ориентация', 'Примечание'])
    writer.writerows(PRINT_PARTS)
    files['print_list.csv'] = listing.getvalue().encode('utf-8-sig')
    files['START_HERE.md'] = '''# Редуктор Ø70: компактный энкодер V2

Комплект для пробной печати механического узла. Распаковать архив целиком.
Открыть `output/reducer_cap_encoder_can.scad` в OpenSCAD.
Все библиотеки use/include, необходимые этому файлу, находятся в архиве.

Количество и ориентация деталей: `print_list.csv` — всего 8 печатных деталей.
Размеры STL в миллиметрах, масштаб 100%. Крышка уже перевёрнута наружной
стороной к столу; полукольца печатать плашмя. Нельзя зеркалить детали в слайсере.
Второй соединитель сохраняет исходную юбку: нужны поддержки под её началом.

В OpenSCAD: `view="stage"`, `assembly_step=1…5` показывает порядок сборки.
`rotation_angle` поворачивает соединители, сепаратор и магниты; для анимации
включить `animate_rotation` и штатную анимацию OpenSCAD.
Размеры крепежа, пайка и порядок установки — `output/reducer_encoder_v2_README.md`.
Отчёт CAD-проверок — `output/reducer_encoder_v2_fit.json`.

Проверены номинальные габариты, полный оборот и прямой выход проводов.
Реальную пайку, жгут, слой клея, печатные допуски и работу редуктора под нагрузкой
проверять на первом комплекте. Это механический комплект; заказ самой PCB
и монтаж электроники используют отдельный комплект KiCad V2.
'''.encode('utf-8')
    manifest = dict(
        scope='Mechanical prototype: compact encoder V2 in D70 reducer',
        source_pcb_sha256=json.loads((OUT / 'reducer_encoder_v2_fit.json').read_text())['source_pcb_sha256'],
        printed_piece_count=sum(row[1] for row in PRINT_PARTS),
        sha256={name: hashlib.sha256(data).hexdigest() for name, data in sorted(files.items())})
    files['manifest.json'] = (json.dumps(manifest, ensure_ascii=False, indent=2)+'\n').encode('utf-8')
    destination = OUT / 'reducer_encoder_v2_print_kit.zip'
    with zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in sorted(files.items()):
            archive.writestr(name, data)
    print(destination)
    print(f'{len(files)} files; {manifest["printed_piece_count"]} printed pieces')
    return destination


if __name__ == '__main__':
    build()
