"""Update only the generated-parts section of the root README from catalog.json."""
from pathlib import Path
import json
D=Path(__file__).resolve().parent;ROOT=D.parents[1]
items=json.loads((D/'catalog.json').read_text())
intro='''## Генерируемые детали

Каталог ниже показывает **29 деталей**: редуктор, варианты его деталей под энкодер, ногу и корпус робота.
На каждой картинке — геометрия соответствующего модуля OpenSCAD, а не эскиз.
Слева объёмный вид, справа вид вдоль локальной оси Z. Масштаб видов подбирается
отдельно; габарит XYZ указан под изображением. Размеры — в миллиметрах, углы — в градусах.

### Как получить и открыть отдельную деталь

Для каждой детали есть готовый файл в [docs/parts](docs/parts), который вызывает
ровно один модуль и скрывает остальную сборку. Ссылка «Открыть деталь» дана
в каждой карточке. Открыть этот `.scad` в OpenSCAD, нажать **F5** для просмотра,
**F6** для точного рендера, затем **Файл → Экспорт → STL**. Положение для
печати отдельно задано только там, где вызван модуль с суффиксом `_print`.

Картинки и файлы карточек используют сохранённый
[эталонный результат генератора](docs/parts/reference_model.scad):

```sh
python3 calc-vpts.py --resolution 600 --ratio 19 --roller-d 4 --roller-h 5 \\
  --rout 28 --diameter 70 --hole-angle 39 --part encoder_assembly \\
  --output output/my_reducer.scad
```

Для собственной версии создать рядом с результатом небольшой файл, например
`output/my_cap.scad`:

```scad
use <my_reducer.scad>
$fn=60;
cap();
```

Вместо `cap();` подставить вызов из нужной карточки. Для голени и TPU-опоры
использовать `use <foots.scad>` — это отдельная библиотека текущей формы стопы.

### Где изменять параметры

| Уровень | Что менять | Когда пересчитывается |
| --- | --- | --- |
| CLI генератора | `--resolution`, `--ratio`, `--roller-d`, `--roller-h`, `--rout`, `--diameter`, `--hole-angle` | Повторным запуском `calc-vpts.py` с новым `--output` |
| Аргументы модулей | Например, `reducer_connector(h1=8,skirt=true)` или `shin(foot=false)` | Сразу при F5/F6 в файле отдельной детали |
| Переменные SCAD | Толщины, высоты, зазоры и размеры посадок в сгенерированном файле | После изменения самого файла, из которого импортируется модуль |
| Библиотека стопы | Переменные `h_*` в `output/foots_h.scad` | Для всех деталей, использующих эту библиотеку |

**Профиль впадин, число роликов, координаты отверстий и часть размеров записываются
Python как готовые числа.** Одной замены `D_out` или `d_roller` в SCAD недостаточно:
для другой передачи или диаметра нужно повторно запустить генератор.
Переменные из файла, подключённого через `use`, не становятся переменными внешнего
файла: менять их нужно в исходном SCAD, а через вызов передавать только его аргументы.
Значения в таблицах ниже относятся к указанному эталону Ø70; это не универсальные
размеры для всех диаметров. Исходный генератор и его формулы — [calc-vpts.py](calc-vpts.py),
параметры доработок редуктора под энкодер — [encoder_scad.py](encoder_scad.py).

'''
sections=[intro];group=None
for i,item in enumerate(items,1):
 if item['group']!=group:
  group=item['group'];sections.append(f'### {group}\n\n')
  if group=='Редуктор с установленным энкодером':
   sections.append('Здесь показаны варианты крышки редуктора, полузажима и соединителей, доработанные для установки энкодера. Носитель магнитов и плата указаны отдельно как компоненты самого энкодера.\n\n')
 sections.append(f'#### {i}. {item["title"]}\n\n')
 sections.append(f'![{item["title"]}](images/parts/{item["id"]}.png)\n\n')
 sections.append(f'[Открыть деталь](docs/parts/{item["id"]}.scad) · ')
 sections.append(f'Источник: [{item["source"].split("/")[-1]}]({"docs/parts/"+item["source"] if item["source"]=="reference_model.scad" else "output/foots.scad"}).\n\n')
 sections.append('Вызов для отдельного файла:\n\n```scad\n'+item['call']+'\n```\n\n')
 sections.append('Как построить: '+item['construction']+'\n\n')
 sections.append('| Параметр | Значение в эталоне | Что задаёт |\n| --- | --- | --- |\n')
 for par in item['parameters']:
  sections.append(f'| `{par["name"]}` | {par["value"]} | {par["meaning"]} |\n')
 sections.append('\n')
sections.append('''### Сборочные режимы редуктора с энкодером

После генерации можно менять `generated_part` в самой модели либо передавать
`-D 'generated_part="encoder_section"'` через CLI OpenSCAD. В файле с `use` удобнее
вызвать `encoder_selected_part("encoder_section");`.

| Режим `--part` / `generated_part` | Что показать | Какие параметры использовать |
| --- | --- | --- |
| `legacy` | Исходная сборка и модули робота | Комментировать вызовы в секции «Сборка», либо открыть одну из карточек |
| `encoder_assembly` | Сборка доработанных деталей редуктора с энкодером | `encoder_assembly(with_bracing=true,show_electronics=true,show_magnets=true)` |
| `encoder_section` | Разрез сборки | `encoder_assembly(section=true)` |
| `encoder_exploded` | Разнесённая сборка | `encoder_assembly(exploded=true)` |
| `encoder_cap` | Крышка редуктора под установку энкодера | `cap_encoder(with_bracing=true)` |
| `encoder_lid` | Защитная накладка крышки редуктора с переносом к Z=0 | `encoder_selected_part("encoder_lid")` |
| `encoder_print` | Крышка редуктора и её защитная накладка рядом | `encoder_selected_part("encoder_print")` |
| `encoder_clamp` | Доработанный зажим соединителей с носителями магнитов | `connector_clamp_encoder(show_magnets=true)`; магниты — фоновые объекты просмотра |
| `encoder_clamp_half` | Корпус полузажима соединителей под энкодер | `connector_clamp_encoder_body_half()`; для печатной ориентации — `encoder_clamp_body_for_print()` |
| `encoder_magnet_ring` | Две половинки носителя магнитов плашмя | `encoder_magnet_ring_for_print()`; одна — `encoder_magnet_ring_half_for_print()` |
| `encoder_clamp_print` | Корпуса полузажимов и носители в печатном положении | `encoder_selected_part("encoder_clamp_print")` |
| `encoder_connector` | Выходной соединитель редуктора под энкодер | `reducer_connector_encoder()` |
| `encoder_load_connector` | Соединитель нагрузки редуктора под энкодер | `load_connector_encoder()` |
| `encoder_pcb` | Механический контур платы | `encoder_pcb_bare()`; это не электрическая разводка |

Изображения обновляются скриптом [render_catalog.py](docs/parts/render_catalog.py).
Подробности воспроизведения — [docs/parts/README.md](docs/parts/README.md).

''')
readme=ROOT/'README.md';s=readme.read_text()
start=s.index('## Робот-собака: стопа, ходьба и бег');end=s.find('\n## ',start+5)
if end<0:end=len(s)
gifs=s[start:end].strip();s=s[:start]+s[end:]
start=s.index('## Генерируемые детали');end=s.index('## Управление сборкой',start)
s=s[:start]+''.join(sections)+s[end:]
s=s.replace('**Внешний радиус впадин жесткого колеса (мм)** (по умолчанию: 29.0)','**Внешний радиус впадин жесткого колеса (мм)** (по умолчанию: 28.0)')
s=s.replace('| `legacy` | Исходная модель ноги |','| `legacy` | Исходная сборка и модули робота |')
s=s.rstrip()+'\n\n'+gifs+'\n';readme.write_text(s)
print('README: 29 illustrated cards, GIF gallery at end')
