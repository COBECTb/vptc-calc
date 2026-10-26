"""Portable printable CAD package built by calc-vpts.py, without output/ inputs."""
from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib
import json
import re
from encoder_scad import native_pcb_layout, native_pcb_components, encoder_metrics

ROOT = Path(__file__).resolve().parent
CAD = ROOT / 'cad'


@dataclass(frozen=True)
class PrintPart:
    name: str
    label: str
    family: str
    quantity: int
    call: str
    material: str = 'rigid'
    orientation: str = 'model; slicer supports may be needed'


BASE_PARTS = [
    PrintPart('rigid_gear', 'Жёсткое колесо', 'reducer', 1, 'rigid_gear();'),
    PrintPart('rigid_gear_with_bracing', 'Жёсткое колесо с креплением', 'alternative', 1, 'rigid_gear_with_bracing();'),
    PrintPart('separator', 'Сепаратор', 'reducer', 1, 'separator();'),
    PrintPart('eccentric', 'Эксцентрик', 'reducer', 1, 'eccentric();'),
    PrintPart('eccentric_shaft', 'Вал эксцентрика', 'reducer', 1, 'eccentric_shaft();'),
    PrintPart('rollers', 'Комплект роликов', 'reducer', 1, 'rollers();'),
    PrintPart('motor_cover', 'Кожух двигателя', 'reducer', 1, 'motor_cover();'),
    PrintPart('shoulder_horn', 'Качалка привода', 'leg', 1, 'shoulder_horn();'),
    PrintPart('shoulder_top', 'Корпус плечевого узла', 'leg', 1, 'shoulder_top();'),
    PrintPart('body', 'Комплект корпуса робота с соединителем', 'collection', 1, 'body(parts=false);'),
    PrintPart('body_front', 'Передняя секция корпуса', 'body', 1, 'body_wall_for_legs();'),
    PrintPart('body_rear', 'Задняя секция корпуса', 'body', 1, 'body_wall_for_legs(h_move=-10,w_move=10);'),
    PrintPart('body_battery', 'Средняя секция корпуса', 'body', 1, 'body_centr_for_bat(h=105,w=100,d=210,l=25);'),
    PrintPart('control_rod', 'Тяга', 'leg', 1, 'connect_points_rod([0,0,0],[184,0,0]);'),
    PrintPart('encoder_adapter', 'Адаптер моторного датчика', 'reducer', 1, 'encoder_adapter();'),
    PrintPart('magnet_spacer', 'Держатель моторного магнита', 'reducer', 1, 'rsgl_magnet_spacer();'),
    PrintPart('foot_rigid', 'Стопа с зажимом', 'leg', 1, 'rigid_print();', orientation='flat back on Z=0'),
    PrintPart('foot_sole', 'Накладка стопы', 'leg', 1, 'sole_print();', material='TPU', orientation='open mounting face on Z=0'),
    PrintPart('foot_cuff', 'Зажим стопы отдельно', 'spare', 1, 'foot_cuff();'),
    PrintPart('cap', 'Исходная крышка без энкодера', 'alternative', 1, 'cap();'),
    PrintPart('cap_with_bracing', 'Исходная крышка с креплением', 'alternative', 1, 'cap_with_bracing();'),
    PrintPart('shin', 'Исходный рычаг без магнитов', 'alternative', 1, 'shin(foot=false);'),
    PrintPart('hip', 'Исходная щека без платы', 'alternative', 1, 'hip();'),
    PrintPart('hip_top', 'Съёмная щека', 'leg', 1, 'hip_top();'),
    PrintPart('reducer_connector', 'Исходный соединитель', 'alternative', 1, 'reducer_connector();'),
    PrintPart('connector_clamp', 'Исходная половинка зажима', 'alternative', 2, 'connector_clamp();'),
]
ENCODER_PRINT_PARTS = [
    PrintPart('encoder_cap', 'Крышка под плату энкодера', 'encoder_reducer', 1, 'cap'),
    PrintPart('encoder_lid', 'Защитная накладка платы', 'encoder_reducer', 1, 'lid', orientation='outer face on Z=0'),
    PrintPart('encoder_light_guides', 'Три прозрачных световода — опытный вариант', 'encoder_reducer', 1, 'light_guides', material='clear_resin_prototype', orientation='flat Z=0; optical finish required'),
    PrintPart('encoder_clamp_half', 'Половинка корпуса магнитного зажима', 'encoder_reducer', 2, 'body', orientation='ends on Z=0'),
    PrintPart('encoder_magnet_ring_half', 'Половинка кольца магнитов 0.8 мм', 'encoder_reducer', 2, 'ring', orientation='flat on Z=0'),
    PrintPart('encoder_connector', 'Соединитель редуктора под энкодер', 'encoder_reducer', 1, 'output_connector'),
    PrintPart('encoder_load_connector', 'Соединитель нагрузки под энкодер', 'encoder_reducer', 1, 'load_connector'),
]
KNEE_PRINT_PARTS = [
    PrintPart('knee_hip', 'Щека колена с карманом платы', 'encoder_knee', 1, 'hip_print', orientation='outer face on Z=0'),
    PrintPart('knee_lower', 'Съёмная щека колена', 'encoder_knee', 1, 'lower_print', orientation='flat on Z=0'),
    PrintPart('knee_shin', 'Рычаг с двумя опорами полукольца', 'encoder_knee', 1, 'shin_print', orientation='Z=0; supports required'),
    PrintPart('knee_cover', 'Крышка кармана платы колена', 'encoder_knee', 1, 'cover_print', orientation='outer face on Z=0'),
    PrintPart('knee_magnet_ring', 'Магнитное полукольцо колена', 'encoder_knee', 1, 'ring_print', orientation='flat on Z=0'),
]
ASSEMBLY_PARTS = ['legacy', 'encoder_lights', 'encoder_assembly', 'encoder_section', 'encoder_exploded',
    'encoder_print', 'encoder_clamp', 'encoder_magnet_ring', 'encoder_clamp_print', 'encoder_pcb',
    'reducer_complete', 'leg_assembly', 'knee_assembly', 'knee_section', 'knee_exploded',
    'knee_mount', 'knee_stage']
PART_NAMES = list(dict.fromkeys(ASSEMBLY_PARTS + [p.name for p in BASE_PARTS+ENCODER_PRINT_PARTS+KNEE_PRINT_PARTS]))


def _template(name):
    return (CAD/name).read_text()


def _pcb_library(d):
    metrics=encoder_metrics(d)
    layout=native_pcb_layout(d, metrics)
    if not layout:
        return '// Native V2 PCB not compatible with this diameter.\n'
    components,_=native_pcb_components(d, metrics)
    # Older mechanical exports predate the explicit J1 pad list.
    import math
    j1=layout.get('j1_pads') or [dict(xy=[32.4*math.cos(math.radians(20))-y*math.sin(math.radians(20)),
        32.4*math.sin(math.radians(20))+y*math.cos(math.radians(20))]) for y in [-1.8,-.6,.6,1.8]]
    values={'compact_outline':layout['outline'], 'compact_holes':layout.get('outline_holes',[]), 'compact_mounts':layout['mounts'],
            'compact_j1_pads':[pad['xy'] for pad in j1],
            'compact_swd_pads':[pad['xy'] for pad in layout['swd_pads']],
            'compact_components':[[c['r'],c['a'],c['angle'],c['front'],c['size_mm']] for c in components],
            'compact_leds':[[c['r'],c['a'],c['size_mm'][2]] for ref in ['D2','D3','D4'] for c in components if c['ref']==ref]}
    header='\n'.join(k+' = '+json.dumps(v)+';' for k,v in values.items())+'\n'
    header+='function compact_source_pcb_sha256() = '+json.dumps(layout['source_pcb_sha256'])+';\n'
    return header+_template('pcb_v2.scad')


def _reducer_library(d, base_dimensions):
    source=_template('reducer_v2.scad')
    metrics=encoder_metrics(d)
    replacements={
        'original_cap_h = 11;':f'original_cap_h = {d.cap_height};',
        'source_gear_h = 15.5;':f"source_gear_h = {base_dimensions['h_reducer']};",
        'source_side_short = 12.246;':f"source_side_short = {base_dimensions['side_short']:.3f};",
        'source_side_long = 29.564;':f"source_side_long = {base_dimensions['side_long']:.3f};",
        'r = 27.08, h = 3+eps':f'r = {base_dimensions["Rsep_out"]+1:.3f}, h = 3+eps',
        'separator_base_z = -9 + separator_axial_lift;':f'separator_base_z = {metrics["separator_base_z"]-d.separator_lift} + separator_axial_lift;',
        'separator_top_z = separator_base_z + 18.5;':f'separator_top_z = separator_base_z + {d.separator_height+d.flange_extra};',
    }
    for old,new in replacements.items():
        if old not in source:raise ValueError('CAD template changed: '+old)
        source=source.replace(old,new)
    return source


def _native_reducer_helper(encoder_available=True):
    return '''
// Whole reducer from geometry, without pre-exported STL dependencies.
module generated_reducer_base_assembly(){
    rigid_gear_with_bracing();
    translate([0,0,h_reducer]) __CAP__
    translate([0,0,.5]) eccentric_shaft();
    translate([0,0,3]) bearing_simple(17,26,5);
    translate([0,0,10]) bearing_simple(17,26,5);
    translate([0,0,14]) rotate([180,0,0]) eccentric();
    translate([0,0,16.5]) bearing_simple(8,16,5);
    translate([0,0,13.5]) rollers();
    translate([0,0,-mc_total_height]) motor_cover();
}
'''.replace('__CAP__', 'encoder_assembly();' if encoder_available else 'cap_with_bracing();')


def prepare_package(base_code, dimensions, encoder_data, base_dimensions, output_file):
    """Return all relative asset contents, master SCAD and a per-unit print list."""
    output_file=Path(output_file)
    asset_dir=output_file.stem+'_assets'
    print_dir=output_file.stem+'_print'
    native=encoder_data.get('native_pcb_compatible',False)
    available=encoder_data.get('available',False)
    # The base library has definitions only, never top-level assembly geometry.
    base_code=re.sub(r'^use <[^>]+>\s*\n','use <foots.scad>\n',base_code,count=1,flags=re.M)
    base_code=base_code[:base_code.index('// === Сборка ===')]
    # Replace historical imported previews with the corresponding procedural modules.
    base_code=re.sub(r'import\("[^"]*_leg_left_front\.stl"\);','leg();',base_code)
    base_code=re.sub(r'import\("[^"]*_reducer(?:_with_bracing_and_connector)?\.stl"[^;]*\);',
                     'generated_reducer_base_assembly();',base_code)
    base_code+='\nzazor=1; // Original exploded leg display spacing.\n'
    base_code+=_native_reducer_helper(available)
    files={
        f'{asset_dir}/base.scad':base_code,
        f'{asset_dir}/foots.scad':_template('foots.scad'),
        f'{asset_dir}/foots_h.scad':_template('foots_h.scad'),
        f'{asset_dir}/sensors.scad':_template('sensors_v2.scad'),
        f'{asset_dir}/pcb.scad':_pcb_library(dimensions) if available else '// Encoder unavailable.\n',
        f'{asset_dir}/clamp.scad':_template('clamp_v2.scad'),
        f'{asset_dir}/reducer.scad':_reducer_library(dimensions,base_dimensions) if native else '// Native V2 installation unavailable.\n',
        f'{asset_dir}/knee.scad':_template('knee_v2.scad'),
    }
    encoder_parts=[p for p in ENCODER_PRINT_PARTS if native or p.name!='encoder_light_guides']
    parts=BASE_PARTS+(encoder_parts if available else [])+(KNEE_PRINT_PARTS if native else [])
    dispatch=[]
    for part in BASE_PARTS:
        dispatch.append(f'if(part=={json.dumps(part.name)}) {{ {part.call} }}')
    dispatch.append('else if(part=="encoder_magnet_ring_half") encoder_magnet_ring_half_for_print();')
    if native:
        # Native parts are routed to the verified V2 geometry, rather than a budget envelope.
        for part in ENCODER_PRINT_PARTS:
            if part.name=='encoder_clamp_half':call='connector_clamp_body_for_print();'
            elif part.name=='encoder_magnet_ring_half':call='magnet_ring_half_for_print();'
            else:call=f'reducer_encoder_scene(view={json.dumps(part.call)},time=time);'
            dispatch.append(f'else if(part=={json.dumps(part.name)}) {{ {call} }}')
        dispatch.extend([
            'else if(part=="encoder_assembly") reducer_encoder_scene(time=time,rotation_angle=rotation_angle,animate_rotation=animate_rotation);',
            'else if(part=="encoder_section") reducer_encoder_scene(view="section",time=time);',
            'else if(part=="encoder_lights") reducer_encoder_scene(view="lights",time=time);',
            'else if(part=="encoder_exploded") reducer_encoder_scene(view="exploded",time=time);',
            'else if(part=="encoder_print") reducer_encoder_scene(view="print");',
            'else if(part=="encoder_magnet_ring") magnet_ring_for_print();',
            'else if(part=="encoder_clamp_print") { translate([-39,0,0]) connector_clamp_body_for_print(); translate([39,0,0]) connector_clamp_body_for_print(); translate([0,31,0]) magnet_ring_for_print(); }',
            'else if(part=="encoder_clamp") { for(h=[0,1]) rotate(180*h) { connector_clamp_base(); magnet_rims(); %magnet_preview(second_half=h==1); } }',
            'else if(part=="encoder_pcb") compact_pcb();',
        ])
    views={p.name:p.call for p in KNEE_PRINT_PARTS}
    views.update(knee_assembly='assembly',knee_section='section',knee_exploded='exploded',knee_mount='mount',knee_stage='stage')
    for name,view in views.items():
        if native:
            dispatch.append(f'else if(part=={json.dumps(name)}) knee_encoder_scene(view={json.dumps(view)},knee_angle=knee_angle,animate=animate,time=time,assembly_step=assembly_step,show_magnets=show_magnets,show_rod=show_rod);')
        else:
            dispatch.append(f'else if(part=={json.dumps(name)}) assert(false,"Колено под V2 рассчитано для штатного D70; нужна новая компоновка");')
    dispatch.append('else if(part=="legacy") body(a1=0,a2=360*time,parts=true);')
    dispatch.append('else if(part=="reducer_complete") package_reducer_complete(time,rotation_angle,animate_rotation);')
    dispatch.append('else if(part=="leg_assembly") package_leg_assembly(time);')
    dispatch.append('else encoder_selected_part(part);')
    # The first branch is an if; the following base branches must be else-if.
    for i in range(1,len(BASE_PARTS)):dispatch[i]='else '+dispatch[i]
    # For the native half ring, prefer the authoritative clamp library branch.
    if native:dispatch.pop(len(BASE_PARTS))
    master='''// Generated by calc-vpts.py. Edit source parameters and cad/, then regenerate.
/* [Деталь] */
generated_part = __PART__; // [__CHOICES__]
/* [Колено] */
knee_angle = 0; // [-44.6458:0.1:54.204]
animate = true;
assembly_step = 4; // [1:4]
show_magnets = true;
show_rod = true;
/* [Редуктор] */
rotation_angle = 0; // [0:360]
animate_rotation = false;
/* [Hidden] */
include <__ASSETS__/base.scad>
use <__ASSETS__/foots.scad>
use <__ASSETS__/pcb.scad>
use <__ASSETS__/clamp.scad>
use <__ASSETS__/knee.scad>
use <__ASSETS__/reducer.scad>

module generated_selected_part(part,time=0,knee_angle=0,animate=false,assembly_step=4,
    show_magnets=true,show_rod=true,rotation_angle=0,animate_rotation=false){
__DISPATCH__
}
module package_reducer_complete(time=0,rotation_angle=0,animate_rotation=false){
    // The accepted cap assembly also supplies its separator, bearing and connectors.
    rigid_gear_with_bracing();
    translate([0,0,__REDUCER_H__]) __REDUCER_SCENE__
    translate([0,0,.5]) eccentric_shaft();
    translate([0,0,3]) bearing_simple(17,26,5);
    translate([0,0,10]) bearing_simple(17,26,5);
    translate([0,0,14]) rotate([180,0,0]) eccentric();
    translate([0,0,16.5]) bearing_simple(8,16,5);
    translate([0,0,13.5]) rollers();
    translate([0,0,-27.5]) motor_cover();
}
module package_leg_assembly(time=0){
    assert(__NATIVE__,"Колено под готовую V2 поддерживается для штатного D70");
    angle=package_knee_angle(time);
    servo=package_servo_angle(angle);
    package_reducer_complete(time,rotation_angle=servo);
    translate([0,0,__REDUCER_H__+11]) shoulder_top();
    rotate(servo) translate([0,0,__REDUCER_H__+19]) rotate([180,0,0]) shoulder_horn();
    translate([-13,184,__REDUCER_H__+20.5]) {
        knee_encoder_scene(knee_angle=angle,animate=false,time=time);
        rotate(angle) translate([-47,0,0]) rotate([180,180,0]) robot_foot();
    }
}
// The same bounded knee cycle as the local installation. Solve its drive angle
// geometrically, rather than driving the original linkage beyond its stops.
function package_knee_angle(t,start_angle=0)=let(
    lo=-44.6458,hi=54.2040,middle=(lo+hi)/2,amplitude=(hi-lo)/2,
    bounded=max(lo,min(hi,start_angle)),phase=asin((bounded-middle)/amplitude))
    (t==0||t==1)?bounded:middle+amplitude*sin(360*t+phase);
function package_servo_angle(angle)=let(
    p=[37*cos(angle),37*sin(angle)],c=[13,-184],v=p-c,d=norm(v),
    beta=atan2(v[1],v[0]),alpha=acos((31*31+d*d-184*184)/(2*31*d)))
    beta-alpha;
generated_selected_part(generated_part,time=$t,knee_angle=knee_angle,animate=animate,
    assembly_step=assembly_step,show_magnets=show_magnets,show_rod=show_rod,
    rotation_angle=rotation_angle,animate_rotation=animate_rotation);
'''
    for key,value in {'__ASSETS__':asset_dir,'__CHOICES__':','.join(PART_NAMES),
                      '__DISPATCH__':'\n'.join(dispatch),'__REDUCER_H__':str(base_dimensions['h_reducer']),
                      '__REDUCER_SCENE__':('reducer_encoder_scene(time=time,rotation_angle=rotation_angle,animate_rotation=animate_rotation);' if native else
                          'encoder_assembly();' if available else 'cap_with_bracing();'),
                      '__NATIVE__':'true' if native else 'false'}.items():master=master.replace(key,value)
    for part in parts:
        files[f'{print_dir}/{part.name}.scad']=(
            f'// {part.label}; {part.quantity} per {part.family}.\n'
            f'// Material: {part.material}; {part.orientation}.\n'
            f'use <../{output_file.name}>\n'
            f'generated_selected_part({json.dumps(part.name)},time=0,animate=false);\n')
    files[f'{print_dir}/README.md']=_print_readme(parts,native,encoder_data)
    catalog={'schema_version':1,'quantities':'per indicated assembly; alternatives and spares are not additive',
             'native_v2_compatible':native,'parts':[
                 {**asdict(p),'file':f'{print_dir}/{p.name}.scad'} for p in parts],
             'assemblies':{
                 'reducer_with_encoder': (['rigid_gear_with_bracing','separator','eccentric',
                     'eccentric_shaft','rollers','motor_cover','encoder_adapter','magnet_spacer']+
                     [p.name for p in encoder_parts]) if available else [],
                 'knee_with_encoder': ([p.name for p in KNEE_PRINT_PARTS]+
                     ['control_rod','foot_rigid','foot_sole']) if native else [],
                 'body':['body_front','body_rear','body_battery','encoder_load_connector' if available else 'reducer_connector']},
             'known_limitations':['Original rod/short-arm axial overlap of 0.5 mm is not fixed by this package.',
                 'Other diameters need a new PCB and knee layout; no automatic electrical redesign.',
                 'Printed deformation, strength and full actuator assembly require prototype qualification.']}
    return master,files,catalog


def _print_readme(parts,native,encoder_data):
    metrics = encoder_data.get('derived', {})
    inner = metrics.get('inner_magnet_count')
    outer = metrics.get('outer_magnet_count')
    text='# Детали для печати\n\nВсе файлы созданы основным calc-vpts.py.\n'
    text+='Для печати повторить генерацию с --export-stl: двоичные STL проверяются на замкнутость сетки. Логи — в .build/. Для просмотра открыть нужный SCAD в OpenSCAD.\n\n'
    text+='Количество указано на один соответствующий узел, а не на всю собаку.\n'
    text+='Группы alternative и spare — замены и запасные детали; collection — сборный комплект уже перечисленных деталей. Их не нужно печатать вместе с основным вариантом.\n'
    if inner is not None:
        text+='Кольца магнитов приклеиваются; по 2 одинаковые половины на редуктор.\n'
        text+='Сначала затянуть половины зажима, затем вклеить закрывающие крепёж магниты.\n'
        for name,count in [('внутреннего',inner),('внешнего',outer)]:
            polarity='противоположна' if (count//2)%2 else 'та же'
            text+=f'У второй половины полярность первого магнита {name} ряда — {polarity}.\n'
    text+='\n'
    text+='| Файл | Деталь | На узел | Группа | Материал |\n|---|---|---:|---|---|\n'
    for p in parts:text+=f'| [{p.name}.scad]({p.name}.scad) | {p.label} | {p.quantity} | {p.family} | {p.material} |\n'
    text+='\nКрышки плат и магнитные кольца уже обращены печатной плоскостью к Z=0.\n'
    text+='Другим деталям могут потребоваться поддержка и своя ориентация в слайсере.\n'
    text+='Печатная стопа foot_rigid включает зажим; foot_cuff — отдельная запасная деталь.\n'
    text+='\n## Сборка узлов\n\n'
    text+='Редуктор: выбрать исходный корпус/крышку либо вариант с креплением.\n\n'
    if inner is not None:
        text+=f'Для энкодера использовать encoder_cap и encoder_lid вместо исходной крышки; encoder_connector и encoder_load_connector соединяются двумя encoder_clamp_half. Приклеить две encoder_magnet_ring_half и установить {inner} внутренних и {outer} наружных магнитов Ø5×1 мм.\n\n'
    if native:
        text+='Колено: сначала прошить PCB V2 через J2; установить плату на два штифта и уложить четыре провода в открытую knee_hip. На knee_shin уже напечатаны две опоры: приклеить knee_magnet_ring по установочному штифту и вклеить 12 внутренних и 13 наружных магнитов с чередованием полюсов. Вставить подшипники 688ZZ, шарнир и тягу, затем закрепить съёмную knee_lower. Закрыть карман knee_cover тремя винтами M2×6 с низкой головкой Ø3.8×1.3 мм. Этапы видны в knee_stage (assembly_step=1…4).\n\n'
    text+='Покупные детали не печатаются. На редуктор: 2×6803ZZ (17×26×5), 1×688ZZ (8×16×5), 1×6808-2RS (40×52×7) для штатного Ø70, крепёж корпуса и двигателя M3. Для другого диаметра сверить выбранный подшипник в JSON/выводе расчёта. Крепёж платы и крышки — M2; длину винтов платы выбирать по фактической высоте кармана. Количество дано по узлам; полный крепёжный BOM собаки пока не рассчитан.\n\n'
    text+='Номинальная посадка тяги всё ещё имеет осевое пересечение 0.5 мм: перед сборкой его необходимо исправить.\n'
    if not native:text+='\nГотовая PCB V2 и колено не соответствуют выбранным размерам.\n'
    return text


def write_package(output_file, master, files, manifest_file, manifest, overwrite=False):
    """Preflight the entire package before changing any existing file."""
    output_file=Path(output_file);manifest_file=Path(manifest_file)
    targets={output_file:master, **{output_file.parent/name:text for name,text in files.items()}}
    if manifest_file.resolve() in {p.resolve() for p in targets}:
        raise ValueError('JSON-манифест совпадает с одним из файлов CAD-комплекта')
    manifest['print_package']['generated_files_sha256']={
        str(path.relative_to(output_file.parent)):hashlib.sha256(text.encode()).hexdigest()
        for path,text in targets.items()}
    targets[manifest_file]=json.dumps(manifest,ensure_ascii=False,indent=2)+'\n'
    for path in targets:
        if path.exists() and (not overwrite or not path.is_file()):
            raise ValueError(f'Файл комплекта {path} уже существует; нужен --overwrite или новый --output')
    for path,text in targets.items():
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(text,encoding='utf-8')


def check_stl_mesh(path):
    """Reject open meshes; weld export-rounding slivers at most 0.00001 mm.

    CGAL's solid can be valid while its float32 STL has near-duplicate vertices
    and collapsed triangles. Only this numerical defect is repaired here.
    """
    import struct
    import numpy as np

    data = path.read_bytes()
    count = struct.unpack_from('<I', data, 80)[0]
    if not count or len(data) != 84 + 50 * count:
        raise RuntimeError(f'Некорректный двоичный STL: {path.name}')
    dtype = np.dtype([('normal', '<f4', (3,)), ('vertices', '<f4', (3, 3)),
                      ('attribute', '<u2')])
    records = np.frombuffer(data, dtype=dtype, offset=84)
    points = records['vertices'].reshape(-1, 3)
    if not np.isfinite(points).all():
        raise RuntimeError(f'Некорректные координаты STL: {path.name}')

    def indexed(points):
        vertices, inverse = np.unique(points, axis=0, return_inverse=True)
        faces = inverse.reshape(-1, 3)
        keep = ((faces[:, 0] != faces[:, 1]) & (faces[:, 1] != faces[:, 2]) &
                (faces[:, 0] != faces[:, 2]))
        return vertices, faces[keep]

    def closed(faces):
        edges = np.concatenate([faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]])
        unique, inverse, counts = np.unique(np.sort(edges, axis=1), axis=0,
                                            return_inverse=True, return_counts=True)
        orientation = np.bincount(inverse, weights=np.where(edges[:, 0] < edges[:, 1], 1, -1),
                                  minlength=len(unique))
        return len(counts) > 0 and bool(np.all(counts == 2) and np.all(orientation == 0))

    vertices, faces = indexed(points)
    repaired = not closed(faces)
    if repaired:
        rounded = np.round(points.astype(np.float64), 5).astype(np.float32)
        vertices, faces = indexed(rounded)
    if not closed(faces):
        raise RuntimeError(f'STL {path.name} имеет незамкнутую сетку; исправьте исходную CAD-геометрию')
    if repaired or len(faces) != count:
        result = np.zeros(len(faces), dtype=dtype)
        triangles = vertices[faces]
        normals = np.cross(triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0])
        lengths = np.linalg.norm(normals, axis=1)
        if np.any(lengths == 0):
            raise RuntimeError(f'Вырожденные грани STL: {path.name}')
        result['normal'] = normals / lengths[:, None]
        result['vertices'] = triangles
        path.write_bytes(data[:80] + struct.pack('<I', len(faces)) + result.tobytes())
    return dict(closed=True, consistent_winding=True, triangles=len(faces),
                removed_degenerate_triangles=count-len(faces),
                rounding_repair_mm=.00001 if repaired else 0)


def export_stl(output_file, catalog, openscad=None, selected=None, overwrite=False):
    """Render actual printable parts; a failed render cannot be reported as success."""
    from concurrent.futures import ThreadPoolExecutor, as_completed
    import shutil
    import subprocess
    output_file=Path(output_file).resolve()
    exe=openscad or shutil.which('openscad')
    if not exe:
        candidate=Path('/Applications/OpenSCAD-2021.01.app/Contents/MacOS/OpenSCAD')
        if candidate.exists():exe=str(candidate)
    if not exe:raise ValueError('Для STL нужен OpenSCAD: установите его или укажите --openscad')
    parts=[p for p in catalog['parts'] if not selected or p['name'] in selected]
    for part in parts:
        path=(output_file.parent/part['file']).with_suffix('.stl')
        if path.exists() and not overwrite:raise ValueError(f'Файл {path} уже существует; нужен --overwrite')
    def render(part):
        source=output_file.parent/part['file'];target=source.with_suffix('.stl')
        logs=source.parent/'.build';logs.mkdir(exist_ok=True)
        temporary=logs/(part['name']+'.stl')
        temporary.unlink(missing_ok=True)
        try:
            # ASCII STL in OpenSCAD 2021 rounds to six significant digits:
            # nearby vertices on long curved parts can collapse into one edge.
            result=subprocess.run([exe,'--export-format','binstl','-o',str(temporary),str(source)],
                                  capture_output=True,text=True,timeout=1200)
        except subprocess.TimeoutExpired as error:
            temporary.unlink(missing_ok=True)
            raise RuntimeError(f'Экспорт {part["name"]} превысил 20 минут') from error
        log=result.stdout+result.stderr
        (logs/(part['name']+'.log')).write_text(log)
        if result.returncode or 'ERROR:' in log or 'WARNING:' in log or not temporary.exists() or not temporary.stat().st_size:
            temporary.unlink(missing_ok=True)
            raise RuntimeError(f'Не удалось экспортировать {part["name"]}: {log[-1800:]}')
        try:
            mesh_report = check_stl_mesh(temporary)
        except RuntimeError:
            temporary.unlink(missing_ok=True)
            raise
        (logs/(part['name']+'.mesh.json')).write_text(json.dumps(mesh_report,indent=2)+'\n')
        temporary.replace(target)
        return part['name']
    with ThreadPoolExecutor(max_workers=3) as pool:
        for done in as_completed([pool.submit(render,p) for p in parts]):
            print('STL:',done.result(),flush=True)
