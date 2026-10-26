"""Verify exported archives against saved sources, then run portable native checks.

Run after export_prototype.py and package_project.py. No source PCB is modified.
This checks release consistency, not physical qualification of an assembled board.
"""
import datetime
from pathlib import Path
import csv
import hashlib
import json
import re
import subprocess
import tempfile
import zipfile

from schematic_sexpr import parse, get, nodes

R = Path(__file__).resolve().parents[1]
CLI = '/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def table(path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


source = (R / 'encoder_can_v2.kicad_pcb').read_bytes()
source_sha = sha(source)
manifest = json.loads((R / 'fabrication/export_manifest.json').read_text())
assert manifest['source_pcb_sha256'] == source_sha
for name, digest in manifest['files_sha256'].items():
    assert sha((R / name).read_bytes()) == digest, name

for name in ['engineering_audit', 'layout_audit', 'swd_clip_audit',
             'signal_route_audit', 'fanout_audit', 'ground_return_audit', 'factory_rules_audit', 'mask_audit', 'cleanup_audit', 'u1_ground_change', 'green_marks_change', 'narrow_outline_audit', 'status_led_review', 'electrical_release_audit',
             'mechanical_release_2026-10-25', 'solder_clearance_audit',
             'mounting_clearance_audit', 'local_decoupling_audit', 'm3_access_audit', 'fabrication_geometry_audit', 'generator_release_audit']:
    report = json.loads((R / 'design' / (name + '.json')).read_text())
    assert report.get('source_pcb_sha256', report.get('source_sha256')) == source_sha, name
fabcheck=json.loads((R/'design/fabrication_geometry_audit.json').read_text())
geometry=json.loads((R/'design/review_geometry.json').read_text())
assert fabcheck['passed'] and fabcheck['closed_internal_cutouts']==len(geometry.get('outline_holes',[]))
fanout=json.loads((R/'design/fanout_audit.json').read_text())
assert fanout['passed'] and len(fanout['checked_escapes'])==14
for name in ['solder_clearance_audit','mounting_clearance_audit','local_decoupling_audit','m3_access_audit','ground_return_audit', 'factory_rules_audit', 'mask_audit', 'cleanup_audit','narrow_outline_audit']:
    assert json.loads((R/'design'/(name+'.json')).read_text())['passed'],name
solder=json.loads((R/'design/solder_clearance_audit.json').read_text())
assert solder['required_via_to_land_mm']>=.5 and solder['minimum_via_to_land_mm']>=.5
generator=json.loads((R/'design/generator_release_audit.json').read_text())
assert generator['passed']
for name,digest in generator['source_files_sha256'].items():
    assert sha((R.parents[1]/name).read_bytes())==digest,name
mechanics = json.loads((R / 'design/mechanical_release_2026-10-25.json').read_text())
assert len(mechanics['probes']) == 7 and all(q['empty'] for q in mechanics['probes'])
assert {'reducer_m3_access','reducer_m3_heads'} <= {q['name'] for q in mechanics['probes']}
for name, digest in mechanics['cad_sha256'].items():
    assert sha((R.parents[1] / name).read_bytes()) == digest, name

board = parse(source.decode())
footprints = {next(q[2] for q in nodes(f, 'property') if q[1] == 'Reference'): f
              for f in nodes(board, 'footprint')}
bom_refs = set()
for row in table(R / 'assembly/BOM.csv'):
    if row['Populate'] == 'Yes':
        refs = [q.strip() for q in row['References'].split(',')]
        assert len(refs) == int(row['Fitted_quantity_per_board'])
        assert not bom_refs.intersection(refs)
        bom_refs.update(refs)
positions = table(R / 'assembly/positions_kicad.csv')
assert len(positions) == len(bom_refs) == 35
assert {q['Ref'] for q in positions} == bom_refs
for row in positions:
    f = footprints[row['Ref']]
    at = get(f, 'at')
    x, y = map(float, at[1:3])
    angle = float(at[3]) if len(at) > 3 else 0
    assert abs(x - float(row['PosX'])) < 0.000002, row['Ref']
    assert abs(y + float(row['PosY'])) < 0.000002, row['Ref']
    delta = (angle - float(row['Rot']) + 180) % 360 - 180
    assert abs(delta) < 0.000002, row['Ref']
    assert row['Side'] == ('top' if get(f, 'layer')[1] == 'F.Cu' else 'bottom')

fiducials = table(R / 'assembly/fiducials.csv')
assert len(fiducials) == 6
assert {q['Ref'] for q in fiducials} == {r for r in footprints if r.startswith('FID')}
for row in fiducials:
    f = footprints[row['Ref']]
    at = get(f, 'at')
    assert abs(float(at[1])-float(row['PosX_mm'])) < .000002
    assert abs(float(at[2])+float(row['PosY_mm_KiCad_CPL'])) < .000002
    assert row['Side'] == ('top' if get(f, 'layer')[1] == 'F.Cu' else 'bottom')

gerbers = list((R / 'fabrication/gerbers').iterdir())
assert len(gerbers) == 11 and not any(q.suffix == '.gbrjob' for q in gerbers)
assert len(list((R / 'fabrication/drills').glob('*.drl'))) == 2

archive = R / 'encoder_can_v2_kicad.zip'
with tempfile.TemporaryDirectory(prefix='encoder-v2-portable-') as tmp:
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        for name in z.namelist():
            assert not Path(name).is_absolute() and '..' not in Path(name).parts
        z.extractall(tmp)
    root = Path(tmp) / 'encoder_can_v2'
    package = json.loads((root / 'archive_manifest.json').read_text())
    assert package['source_pcb_sha256'] == source_sha
    for name, digest in package['files_sha256'].items():
        assert sha((root / name).read_bytes()) == digest, name
    # No saved copper, placement, properties or settings may change in packaging.
    model = r'\(model "[^"]+"'
    normalize = lambda text: re.sub(model, '(model "NORMALIZED"', text)
    assert normalize(source.decode()) == normalize((root / 'encoder_can_v2.kicad_pcb').read_text())
    for name in ['encoder_can_v2.kicad_sch', 'encoder_can_v2.kicad_pro']:
        assert (root / name).read_bytes() == (R / name).read_bytes()
    for name, digest in manifest['files_sha256'].items():
        assert sha((root / name).read_bytes()) == digest, name
    for kind, ext in [('drc', 'pcb'), ('erc', 'sch')]:
        out = Path(tmp) / (kind + '.json')
        args = ['pcb', 'drc', '--schematic-parity', '--refill-zones'] if kind == 'drc' else ['sch', 'erc']
        p = subprocess.run([CLI, *args, '--severity-all', '--exit-code-violations',
                            '--format', 'json', '-o', str(out),
                            str(root / ('encoder_can_v2.kicad_' + ext))],
                           capture_output=True, text=True)
        assert p.returncode == 0, p.stdout + p.stderr
        result = json.loads(out.read_text())
        assert not result.get('violations') and not result.get('unconnected_items') and not result.get('schematic_parity')
        assert not any(s.get('violations') for s in result.get('sheets', []))
        (R / 'design' / ('portable_' + kind + '.json')).write_bytes(out.read_bytes())

# The embedded validation must be from this same saved PCB, not an older package.
with zipfile.ZipFile(archive) as z:
    embedded=json.loads(z.read('encoder_can_v2/design/portable_validation.json'))
    assert embedded['native_pcb_sha256']==source_sha,'Repackage with the newly verified portable validation'
    assert embedded['portable_drc_violations']==embedded['portable_erc_violations']==embedded['portable_schematic_parity_issues']==embedded['portable_unconnected_items']==0

with zipfile.ZipFile(R / 'encoder_can_v2_fabrication.zip') as z:
    expected = {q.relative_to(R / 'fabrication').as_posix(): q
                for q in (R / 'fabrication').rglob('*') if q.is_file()}
    assert set(z.namelist()) == set(expected)
    assert all(z.read(n) == p.read_bytes() for n, p in expected.items())

report = dict(date=datetime.date.today().isoformat(), native_pcb_sha256=source_sha,
              archive_sha256=sha(archive.read_bytes()),
              archive_copper_and_properties_identical=True,
              archive_model_references_only_changed=True,
              archive_manifest_hashes_verified=True,
              manufacturing_hashes_verified=True,
              portable_drc_violations=0, portable_unconnected_items=0,
              portable_schematic_parity_issues=0, portable_erc_violations=0,
              bom_cpl_fitted_reference_match=True, fitted_components=35,
              cpl_coordinates_angles_and_sides_match_saved_pcb=True,
              gerber_layers=11, drill_files=2, current_mechanical_probes_passed=7,
              limits='Factory stack/panel, exact sourcing and hardware qualification remain pending.')
(R / 'design/package_verification.json').write_text(json.dumps(report, indent=2) + '\n')
portable={k:v for k,v in report.items() if k!='archive_sha256'}
portable['note']='Electrical and manufacturing consistency checks. Exact ZIP digest is in the source-project package_verification.json, outside the ZIP to avoid a circular checksum.'
(R/'design/portable_validation.json').write_text(json.dumps(portable,indent=2)+'\n')
print('Portable archive and manufacturing release verified:', source_sha)
