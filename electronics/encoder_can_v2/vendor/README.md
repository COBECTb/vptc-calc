# Библиотеки KiCad в проекте

Официальные посадочные места принадлежат **KiCad library contributors**.
Они распространяются по **CC-BY-SA 4.0 с исключением KiCad для электронных
проектов**; исходный текст лицензии сохранён в [LICENSE-KiCad.md](LICENSE-KiCad.md).
Исключение распространяется на схемы, платы и производственные результаты,
но не отменяет условия распространения самих библиотечных коллекций.

Основной upstream: [KiCad Footprints на GitLab](https://gitlab.com/kicad/libraries/kicad-footprints).
Использованные здесь десять неизменённых файлов совпадают с историческим
[официальным зеркалом KiCad на GitHub](https://github.com/KiCad/kicad-footprints)
на ветке `master`: совпадение содержимого проверено 11.10.2026.
Это снимки библиотечных файлов в старом формате `module`; KiCad 10.0.6
читает их штатно. Версия проверяющей программы не означает, что этот снимок
библиотеки взят из релиза 10.0.6.

| Каталог | Использованные файлы | Источник |
|---|---|---|
| Capacitor_SMD.pretty | C_0402_1005Metric, C_0603_1608Metric | [upstream](https://github.com/KiCad/kicad-footprints/tree/master/Capacitor_SMD.pretty) |
| Resistor_SMD.pretty | R_0402_1005Metric, R_0603_1608Metric | [upstream](https://github.com/KiCad/kicad-footprints/tree/master/Resistor_SMD.pretty) |
| Package_TO_SOT_SMD.pretty | SOT-23, SOT-23-5, SOT-23-8 | [upstream](https://github.com/KiCad/kicad-footprints/tree/master/Package_TO_SOT_SMD.pretty) |
| Crystal.pretty | Crystal_SMD_2520-4Pin_2.5x2.0mm | [upstream](https://github.com/KiCad/kicad-footprints/tree/master/Crystal.pretty) |
| MountingHole.pretty | MountingHole_2.2mm_M2 | [upstream](https://github.com/KiCad/kicad-footprints/tree/master/MountingHole.pretty) |
| TestPoint.pretty | TestPoint_Pad_D1.0mm | [upstream](https://github.com/KiCad/kicad-footprints/tree/master/TestPoint.pretty) |
| Fiducial.pretty | Fiducial_1mm_Mask2mm | [upstream](https://gitlab.com/kicad/libraries/kicad-footprints/-/tree/master/Fiducial.pretty); снимок официальной библиотеки контейнера KiCad 10.0.6 |

`footprint_sources.json` содержит точные URL и SHA-256 этих файлов.
Fiducial-метки добавлены отдельно 12.10.2026 из библиотеки KiCad 10.0.6;
на них распространяется та же лицензия CC-BY-SA 4.0 с исключением KiCad.
Пустой каталог Package_DFN_QFN.pretty не содержит используемого посадочного места.
MCU и датчики используют локальную библиотеку `../Encoder_CAN.pretty`:
STM32 — адаптация внешних IPC-площадок KiCad 10.0.6 с центральной площадкой ST,
TMAG5273 — рекомендуемый land pattern TI. Контакты проводов и SWD также локальные.

Символы схемы закреплены отдельно: [symbols/README.md](symbols/README.md).
Их исходная версия — официальная библиотека 9.0.6; лицензия сохранена рядом.

В V2 15.10.2026 добавлены локальные производные `Encoder_CAN:SOT-23_TVS_CompactCourtyard` и `MountingHole_2.2mm_M2_LowHead`: площадки сохранены, изменён только монтажный контур под фактическую сборку. В закреплённых символах MCU, TCAN и разъёмов расширены фильтры посадочных мест; электрические выводы сохранены. Модель Hall — стандартная SOT-23-6 из установленной KiCad, не модель кристалла датчика.
