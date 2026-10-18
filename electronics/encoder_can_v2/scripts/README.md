Утилиты готовой V2: audit_final.py, audit_engineering.py, audit_signal_routes.py, export_views.py, render_views.py, export_mechanics.py, package_project.py.

Остальные файлы в этой папке — рабочие эксперименты трассировки. Они не образуют воспроизводимый генератор финальной платы. В частности, build.py и place.py перезаписывают плату первоначальной заготовкой: не запускать их на готовой V2. Авторитетный источник электрической геометрии — encoder_can_v2.kicad_pcb.

audit_final.py/export_views.py требуют Python KiCad. render_views.py требует numpy, matplotlib, shapely. export_mechanics.py также требует Python KiCad: читает сохранённую PCB и обновляет только библиотеку её механического контура, креплений и компонентов; крышки и сборки не перезаписывает. package_project.py использует стандартные 3D-модели установленного KiCad; в копии для архива меняются только пути моделей.

audit_engineering.py требует Shapely 2.x и актуальный review_geometry.json; проверяет топологию защиты CAN, зазоры Hall и наличие реперов.

audit_signal_routes.py требует Python KiCad; читает плату и строит граф физических контактов дорожек, переходов и номерных площадок на общих слоях. Отмечает лишние по связности сигнальные объекты; питание и землю не обрабатывает. Плату не изменяет. render_screenshot_review.py создаёт сравнение с сохранённой геометрией из revisions/2026-10-16-before-screenshot-fixes и применяется только из полного репозитория.
