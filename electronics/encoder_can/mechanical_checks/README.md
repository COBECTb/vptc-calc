# Проверки сборочной геометрии

Сначала обновить механические габариты из текущего размещения платы:

```sh
python electronics/encoder_can/scripts/update_scad_components.py
openscad -o /tmp/bearing_collision.stl electronics/encoder_can/mechanical_checks/mcu_bearing_clearance.scad
openscad -o /tmp/mcu_floor.stl electronics/encoder_can/mechanical_checks/carrier_floor_probe.scad
openscad -o /tmp/assembly_collision.stl electronics/encoder_can/mechanical_checks/assembly_clearance.scad
```

Первый и третий результат должны быть пустыми. OpenSCAD 2021.01 сообщает
`Current top level object is empty` и возвращает код 1 для такого STL: это успешное
отсутствие пересечений, если в логе нет ошибок/предупреждений.

Второй результат — тонкий щуп оставшейся стенки от Z3 до Z10,25. Карман MCU имеет
дно Z10,25, корпус MCU заканчивается снизу на Z10,4; верх подшипника расположен на Z10.
При актуальном U1 R29,3/−5° и повороте 0° минимальный радиус кармана 26,4385 мм,
а наружный радиус подшипника 26 мм. Ни посадка, ни её верхний упор не меняются.

Полная проверка использует габаритные оболочки компонентов, а не STEP-модели.
Между телами сохраняются проектные зазоры; пайка и допуски печати требуют контроля
на опытной сборке. Проверка дорожек и паяльной маски выполняется отдельно в KiCad.
