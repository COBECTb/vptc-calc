"""Native OpenSCAD meshes: assembly, service access, wiring and knee motion.

Use --export to regenerate all meshes. Dependencies: numpy, trimesh, manifold3d.
No PCB file or original robot part is modified. build/ contains derived outputs.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import argparse
import hashlib
import json
import math
import re
import shutil
import subprocess
import numpy as np
import trimesh
import manifold3d as md

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BUILD = HERE / 'build'
PARTS = ['hip', 'hip_original', 'lower', 'cover', 'pcb', 'shin',
         'shin_original', 'rotor_base', 'magnet_ring', 'magnet', 'cuff', 'wires', 'screws', 'envelope']
TOL = 1e-5  # mm^3 numerical comparison threshold, not manufacturing clearance.


def source_files():
    seen = set()

    def visit(path):
        path = path.resolve()
        if path in seen:
            return
        seen.add(path)
        for ref in re.findall(r'^\s*(?:use|include)\s*<([^>]+)>', path.read_text(), re.M):
            visit(path.parent / ref)

    visit(HERE / 'validation_parts.scad')
    seen.add(ROOT/'electronics/encoder_can_v2/encoder_can_v2.kicad_pcb')
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(seen)}


def export(openscad):
    def one(part):
        target = BUILD / f'{part}.stl'
        result = subprocess.run([openscad, '-o', str(target), '-D', f'part="{part}"',
                                 str(HERE/'validation_parts.scad')],
                                capture_output=True, text=True, check=False)
        log = result.stdout + result.stderr
        (BUILD/f'{part}.log').write_text(log)
        assert result.returncode == 0 and 'WARNING:' not in log and 'ERROR:' not in log, (part, log)
        print('Exported', part, flush=True)

    with ThreadPoolExecutor(max_workers=3) as pool:
        list(pool.map(one, PARTS))


def volume(solid):
    assert solid.status() == md.Error.NoError, solid.status()
    return max(0., float(solid.volume()))


def vertical_surfaces(mesh, xy):
    # Explicit triangle/vertical-line intersections; no optional spatial-index dependency.
    triangles = mesh.triangles
    a, b, c = triangles[:, 0], triangles[:, 1], triangles[:, 2]
    u, v = b[:, :2]-a[:, :2], c[:, :2]-a[:, :2]
    determinant = u[:, 0]*v[:, 1]-u[:, 1]*v[:, 0]
    good = np.abs(determinant) > 1e-10
    a, u, v, c, b, determinant = a[good], u[good], v[good], c[good], b[good], determinant[good]
    q = np.asarray(xy)-a[:, :2]
    s = (q[:, 0]*v[:, 1]-q[:, 1]*v[:, 0])/determinant
    t = (u[:, 0]*q[:, 1]-u[:, 1]*q[:, 0])/determinant
    good = (s >= -1e-8) & (t >= -1e-8) & (s+t <= 1+1e-8)
    values = np.sort(a[good, 2]+s[good]*(b[good, 2]-a[good, 2])+t[good]*(c[good, 2]-a[good, 2]))
    return [float(z) for i, z in enumerate(values) if i == 0 or z-values[i-1] > .0001]


def rod(angle):
    radians = math.radians(angle)
    p = np.array([37*math.cos(radians), 37*math.sin(radians), 5.])
    center = np.array([13., -184., 5.])
    distance = np.linalg.norm(p-center)
    beta = math.atan2(p[1]-center[1], p[0]-center[0])
    alpha = math.acos((31**2+distance**2-184**2)/(2*31*distance))
    q = center + 31*np.array([math.cos(beta-alpha), math.sin(beta-alpha), 0.])
    eye = md.Manifold.cylinder(11, 6, circular_segments=60, center=True)
    eye -= md.Manifold.cylinder(22, 2, circular_segments=60, center=True)
    shaft = md.Manifold.cylinder(176, 3, circular_segments=60, center=True)
    heading = math.degrees(math.atan2(q[1]-p[1], q[0]-p[0]))
    result = eye.translate(p) + eye.translate(q)
    result += shaft.rotate([0, 90, heading]).translate((p+q)/2)
    # Same recessed low-head envelope as in knee_encoder_compact.scad.
    result -= md.Manifold.cylinder(2.41, 4, circular_segments=64).translate([p[0], p[1], 8.1])
    head = md.Manifold.cylinder(2.2, 3.8, circular_segments=64).translate([p[0], p[1], 8.3])
    return result + head


def verify():
    meshes, solids, geometry = {}, {}, {}
    for name in PARTS:
        mesh = trimesh.load(BUILD/f'{name}.stl', force='mesh', process=True)
        assert mesh.is_watertight and mesh.is_winding_consistent, name
        solid = md.Manifold(md.Mesh64(np.asarray(mesh.vertices, np.float64),
                                     np.asarray(mesh.faces, np.uint64)))
        assert solid.status() == md.Error.NoError, (name, solid.status())
        meshes[name], solids[name] = mesh, solid
        geometry[name] = dict(volume_mm3=volume(solid), bounds_mm=mesh.bounds.tolist(),
                              closed_components=len(solid.decompose()))
    assert all(geometry[n]['closed_components'] == 1 for n in ['hip', 'cover', 'shin', 'rotor_base', 'magnet_ring'])
    assert geometry['wires']['closed_components'] == 4
    assert geometry['magnet']['closed_components'] == 25
    assert abs(np.ptp(meshes['magnet_ring'].vertices[:, 2])-.8) < .0001
    # Both ends lie on the hinge's longitudinal X axis; all ring material is
    # on the negative-Y side. Check the exported shape, not just parameters.
    ring_bounds = meshes['magnet_ring'].bounds
    assert np.allclose(ring_bounds[:, 0], [-33, 33], atol=.001), ring_bounds
    assert abs(ring_bounds[1, 1]) < .0001, ring_bounds
    relative_sensor_angles = [-72-54.204, -72-(-44.6458)]
    edge_margin = min(relative_sensor_angles[0]-(-180), 0-relative_sensor_angles[1])
    assert edge_margin > 27, relative_sensor_angles
    d = solids
    anchors = (d['rotor_base'] ^ d['shin_original']).decompose()
    assert len(anchors) == 2, ('Two separate physical attachment areas required', len(anchors))
    anchor_contacts = []
    for anchor in anchors:
        vertices = np.asarray(anchor.to_mesh64().vert_properties)
        anchor_contacts.append(dict(overlap_mm3=volume(anchor),
                                    bounds_mm=[vertices.min(axis=0).tolist(), vertices.max(axis=0).tolist()]))
    anchor_contacts.sort(key=lambda row: row['bounds_mm'][0][0])
    assert all(row['overlap_mm3'] > 100 for row in anchor_contacts), anchor_contacts
    assert anchor_contacts[0]['bounds_mm'][1][0] < 0 < anchor_contacts[1]['bounds_mm'][0][0]
    pairs = [('hip', 'pcb'), ('cover', 'pcb'), ('cover', 'hip'), ('wires', 'hip'),
             ('wires', 'cover'), ('wires', 'pcb'), ('screws', 'pcb'),
             ('screws', 'wires'), ('magnet_ring', 'shin')]
    overlaps = {a+' / '+b: volume(d[a] ^ d[b]) for a, b in pairs}
    assert max(overlaps.values()) < TOL, overlaps
    lifts = [0, .1, .5, 1, 2, 4, 6, 10, 20]
    insertion = [dict(lift_mm=z, pcb_hip_mm3=volume(d['pcb'].translate([0, 0, z]) ^ d['hip']),
                      lid_hip_mm3=volume(d['cover'].translate([0, 0, z]) ^ d['hip']),
                      lid_pcb_mm3=volume(d['cover'].translate([0, 0, z]) ^ d['pcb'])) for z in lifts]
    assert max(row[k] for row in insertion for k in ['pcb_hip_mm3', 'lid_hip_mm3', 'lid_pcb_mm3']) < TOL
    windows = []
    for radius in [23.5, 29.5]:
        xy = [radius*math.cos(math.radians(-72)), radius*math.sin(math.radians(-72))]
        surfaces = vertical_surfaces(meshes['hip'], xy)
        assert any(abs(z-13.7) < .0001 for z in surfaces), surfaces
        assert any(abs(z-14.1) < .0001 for z in surfaces), surfaces
        windows.append(dict(radius_mm=radius, xy_mm=xy, z_surfaces_mm=surfaces,
                            membrane_mm=.4, magnet_air_gap_mm=.4))
    fixed = d['hip'] + d['cover'] + d['lower']
    original = d['hip_original'] + d['lower']
    added = fixed - original
    moving = d['shin'] + d['cuff'] + d['magnet_ring'] + d['magnet']
    added_bottom = float(meshes['envelope'].vertices[:, 2].min())
    moving_top = float(np.asarray(moving.to_mesh64().vert_properties)[:, 2].max())
    axial_gap = added_bottom-moving_top
    # Rotation about Z cannot change either Z interval. This complements the
    # sampled whole-fork test with a continuous clearance bound for additions.
    assert axial_gap >= .3999, axial_gap
    rows, carrier_gaps = [], []
    for angle in np.linspace(-44.6458, 54.204, 201):
        rotating = moving.rotate([0, 0, float(angle)])
        linkage = rod(float(angle))
        carrier_gaps.append(dict(angle_deg=float(angle),
            gap_mm=d['rotor_base'].rotate([0, 0, float(angle)]).min_gap(d['hip'], 2)))
        rows.append(dict(angle_deg=float(angle), moving_fixed_mm3=volume(rotating ^ fixed),
                         moving_added_mm3=volume(rotating ^ added),
                         rod_added_mm3=volume(linkage ^ added),
                         rod_carrier_mm3=volume(linkage ^ (d['magnet_ring'] +
                             (d['shin']-d['shin_original'])).rotate([0, 0, float(angle)]))))
    maxima = {k: max(r[k] for r in rows) for k in rows[0] if k != 'angle_deg'}
    assert max(maxima.values()) < TOL, maxima
    minimum_carrier_gap = min(carrier_gaps, key=lambda row: row['gap_mm'])
    assert minimum_carrier_gap['gap_mm'] >= .4, minimum_carrier_gap
    # Selected animation frame, with the actual phase for initial knee_angle=0.
    middle=(-44.6458+54.204)/2
    amplitude=(54.204+44.6458)/2
    angle_t027=middle+amplitude*math.sin(2*math.pi*.27+math.asin(-middle/amplitude))
    carrier_t027=d['rotor_base'].rotate([0, 0, angle_t027])
    frame_t027=dict(animation_time=.27, initial_angle_deg=0, angle_deg=angle_t027,
                    base_hip_overlap_mm3=volume(carrier_t027 ^ d['hip']),
                    base_hip_gap_mm=carrier_t027.min_gap(d['hip'], 2))
    assert frame_t027['base_hip_overlap_mm3'] < TOL
    print('Motion: 201 positions passed', flush=True)
    # Preserve original M3 fastener bores near the knee.
    m3 = md.Manifold()
    for x in [-7, 13]:
        m3 += md.Manifold.cylinder(3, 3, circular_segments=60).translate([x, -39, 20.5])
    m3_overlap = volume((d['hip']+d['cover']) ^ m3)
    baseline_m3_overlap = volume(d['hip_original'] ^ m3)
    # These original nominal head/bore faces coincide. STL decimal rounding
    # may create a tiny baseline sliver; check that the new housing adds none.
    additional_m3_overlap = volume(d['envelope'] ^ m3)
    assert additional_m3_overlap < TOL, (m3_overlap, baseline_m3_overlap, additional_m3_overlap)
    report = dict(date='2026-10-21', source_sha256=source_files(),
        geometry=geometry, overlap_mm3=overlaps, service_insertion=insertion,
        carrier_attachment=dict(contacts=anchor_contacts, support_root_diameter_mm=10,
                                inner_base_thickness_mm=3.2, outer_lip_thickness_mm=1.6),
        motion=dict(range_deg=[-44.6458, 54.204], positions=len(rows),
                    maximum_overlap_mm3=maxima,
                    minimum_carrier_to_hip_gap=minimum_carrier_gap,
                    critical_animation_frame=frame_t027,
                    encoder_positive_envelope_min_z_mm=added_bottom,
                    modeled_moving_parts_max_z_mm=moving_top,
                    continuous_axial_clearance_mm=axial_gap), windows=windows,
        original_m3_head_bores_overlap_mm3=m3_overlap,
        original_m3_baseline_contact_mm3=baseline_m3_overlap,
        added_material_in_original_m3_head_bores_mm3=additional_m3_overlap,
        layout=dict(board_rotation_deg=-81, hall_azimuth_deg=-72, cover_face_z_mm=23.5,
                    screw_head_top_z_mm=23.4, external_height_reduction_mm=2.1,
                    screw_count=3, screws='M2x6, low head <=3.8mm diameter x1.3mm height',
                    cable_diameter_mm=1, ring_thickness_mm=.8, magnet_count=[12, 13],
                    magnet_sector_deg=[-180, 0],
                    sensor_relative_angle_range_deg=relative_sensor_angles,
                    minimum_sensor_to_sector_edge_deg=edge_margin),
        limits=['Nominal CAD geometry, no deformation, printed/PCB/solder tolerance qualification.',
                'Motion checks the encoder installation and local fixed fork; the whole shoulder linkage is not qualified.',
                'Original rod/shin seating and procurement of its fasteners remain properties of the base mechanism.',
                'Air-field comparison does not establish actual encoder accuracy; calibration and prototype tests required.',
                'Use a service loop beyond the side exit; the harness outside this CAD envelope is not modeled.'])
    (HERE/'installation_checks.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    for part in ['hip', 'cover']:
        mesh = meshes[part].copy()
        mesh.apply_transform(trimesh.transformations.rotation_matrix(math.pi, [1, 0, 0]))
        mesh.apply_translation([0, 0, 23.5])
        mesh.export(BUILD/f'{part}_print.stl')
    ring = meshes['magnet_ring'].copy()
    ring.apply_translation([0, 0, -12.3])
    ring.export(BUILD/'magnet_ring_print.stl')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--export', action='store_true')
    parser.add_argument('--openscad', default=shutil.which('openscad') or
                        '/Applications/OpenSCAD-2021.01.app/Contents/MacOS/OpenSCAD')
    args = parser.parse_args()
    BUILD.mkdir(exist_ok=True)
    if args.export:
        export(args.openscad)
    result = verify()
    print('Installation checks passed:', HERE/'installation_checks.json')
