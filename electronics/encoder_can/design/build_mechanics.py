#!/usr/bin/env python3
"""Generate mechanical transfer data; does not create the KiCad board or schematic."""
import json
import math
from pathlib import Path

OUT = Path(__file__).resolve().parent
ORIGIN = (100.0, 100.0)
RI, RO, START, END = 21.6, 33.4, -71.0, 89.0
BOLT_R, NOTCH_R = 31.5, 4.5
BOLT_ANGLES = [39, 99, 159, 219, 279, 339]
ACTIVE_ANGLES = [-21.0, 39.0]


def polar(r, a):
    a = math.radians(a)
    return [r * math.cos(a), r * math.sin(a)]


def kicad(p):
    return [ORIGIN[0] + p[0], ORIGIN[1] - p[1]]


def round_xy(p):
    return [round(v, 9) for v in p]


def arc(c, r, a0, a1):
    def p(a):
        q = polar(r, a)
        return [c[0] + q[0], c[1] + q[1]]
    return {"type": "arc", "center_scad_mm": round_xy(c), "radius_mm": r,
            "start_angle_scad_deg": a0, "sweep_scad_deg": a1 - a0,
            "start_scad_mm": round_xy(p(a0)), "mid_scad_mm": round_xy(p((a0+a1)/2)),
            "end_scad_mm": round_xy(p(a1)),
            "start_kicad_mm": round_xy(kicad(p(a0))),
            "mid_kicad_mm": round_xy(kicad(p((a0+a1)/2))),
            "end_kicad_mm": round_xy(kicad(p(a1)))}


def line(p, q):
    return {"type": "line", "start_scad_mm": round_xy(p), "end_scad_mm": round_xy(q),
            "start_kicad_mm": round_xy(kicad(p)), "end_kicad_mm": round_xy(kicad(q))}


def sample_edges(edges):
    points = []
    for e in edges:
        if e["type"] == "line":
            points.append(e["start_scad_mm"])
        else:
            n = max(2, math.ceil(abs(e["sweep_scad_deg"]) / 0.25))
            for i in range(n):
                a = e["start_angle_scad_deg"] + e["sweep_scad_deg"] * i / n
                v = polar(e["radius_mm"], a)
                points.append([e["center_scad_mm"][0]+v[0], e["center_scad_mm"][1]+v[1]])
    return points


delta = math.degrees(math.acos((RO*RO+BOLT_R*BOLT_R-NOTCH_R*NOTCH_R)/(2*RO*BOLT_R)))
beta = math.degrees(math.acos((RO*RO-BOLT_R*BOLT_R-NOTCH_R*NOTCH_R)/(2*BOLT_R*NOTCH_R)))
edges = []
last = START
for a in ACTIVE_ANGLES:
    edges.append(arc([0, 0], RO, last, a-delta))
    edges.append(arc(polar(BOLT_R, a), NOTCH_R, a-beta, a+beta-360))
    last = a+delta
edges.extend([arc([0, 0], RO, last, END), line(polar(RO, END), polar(RI, END))])
original_edges = edges + [arc([0, 0], RI, END, START), line(polar(RI, START), polar(RO, START))]
edges.append(arc([0, 0], RI, END, 21))
for i in range(8):
    edges.append(line(polar(21.6-.3*i/8,21-2*i/8), polar(21.6-.3*(i+1)/8,21-2*(i+1)/8)))
edges.append(arc([0, 0], 21.3, 19, -1))
for i in range(8):
    edges.append(line(polar(21.3+.3*i/8,-1-2*i/8), polar(21.3+.3*(i+1)/8,-1-2*(i+1)/8)))
edges.extend([arc([0, 0], RI, -3, START), line(polar(RI, START), polar(RO, START))])
polygon = sample_edges(edges)
area = abs(sum(p[0]*q[1]-q[0]*p[1] for p,q in zip(polygon,polygon[1:]+polygon[:1])))/2

holes = []
for i, a in enumerate([-59, 77], 1):
    p = polar(30.5, a)
    holes.append({"reference": f"H{i}", "type": "NPTH", "diameter_mm": 2.2,
                  "radius_from_axis_mm": 30.5, "angle_scad_deg": a,
                  "scad_mm": round_xy(p), "kicad_mm": round_xy(kicad(p)),
                  "recommended_copper_keepout_radius_mm": 2.25})

pad_template = [(1,-1.3,-.95),(2,-1.3,0),(3,-1.3,.95),
                (4,1.3,.95),(5,1.3,0),(6,1.3,-.95)]
pin_names = {1:"SCL", 2:"GND", 3:"GND_TEST", 4:"VCC", 5:"INT", 6:"SDA"}


def package_to_scad(center, local):
    # KiCad local X right and Y down; physical local Y is the positive tangent.
    a = math.radians(9)
    x, y = local
    return [center[0]+x*math.cos(a)+y*math.sin(a),
            center[1]+x*math.sin(a)-y*math.cos(a)]


sensors = []
for index, r in enumerate([23.5,29.5], 1):
    hall = polar(r, 9)
    center = package_to_scad(hall, [.12,-.4])
    pads = []
    min_clearance = 100
    for pin, x, y in pad_template:
        corners = [package_to_scad(center,[x+dx,y+dy]) for dx,dy in
                   [(-.55,-.3),(.55,-.3),(.55,.3),(-.55,.3)]]
        # Minimum radius of this rectangle occurs at a vertex or on an edge.
        for p, q in zip(corners,corners[1:]+corners[:1]):
            vx, vy = q[0]-p[0], q[1]-p[1]
            t = min(1,max(0,-(p[0]*vx+p[1]*vy)/(vx*vx+vy*vy)))
            min_clearance = min(min_clearance, math.hypot(p[0]+t*vx,p[1]+t*vy)-RI)
        pads.append({"pin":pin, "name":pin_names[pin], "local_kicad_mm":[x,y],
                     "size_mm":[1.1,.6],
                     "center_kicad_mm":round_xy(kicad(package_to_scad(center,[x,y]))),
                     "corners_scad_mm":[round_xy(p) for p in corners],
                     "corners_kicad_mm":[round_xy(kicad(p)) for p in corners]})
    sensors.append({"reference":f"U_SENSOR_{index}", "magnet_count":24 if index==1 else 26,
                    "track_radius_mm":r, "track_angle_scad_deg":9,
                    "side":"F.Cu", "kicad_rotation_deg":9,
                    "hall_scad_mm":round_xy(hall), "hall_kicad_mm":round_xy(kicad(hall)),
                    "body_center_scad_mm":round_xy(center),
                    "body_center_kicad_mm":round_xy(kicad(center)),
                    "hall_local_footprint_kicad_mm":[-.12,.4],
                    "body_center_from_hall_radial_tangent_mm":[.12,.4],
                    "land_pattern":"TI DBV0006A-C02 example board layout, 4231316/A 10/2024",
                    "pads":pads, "minimum_pad_inner_edge_clearance_original_mm":round(min_clearance,6),
                    "minimum_pad_inner_edge_clearance_relief_mm":round(min_clearance+.3,6) if index==1 else None})

info = {
    "units":"mm", "source":"output/encoder_can_pcb_layout.scad",
    "coordinates": {
        "scad":"Right handed: X right, Y up, +Z towards magnets in assembled cap; angles CCW from +X.",
        "kicad":"F.Cu faces magnets. X right, Y down; KiCad origin of reducer axis is (100,100).",
        "conversion":"kicad_x=100+scad_x; kicad_y=100-scad_y",
        "front_rotation":"KiCad +9 degree footprint rotation is CCW in front view; no XY mirror is used.",
        "board_z_in_assembly_mm":[11,11.8],
        "important":"SCAD housing mirror([0,0,1]) flips Z only, leaving XY unchanged."
    },
    "outline": {"inner_radius_mm":RI,"outer_radius_mm":RO,"start_angle_scad_deg":START,
                "end_angle_scad_deg":END,"center_angle_scad_deg":9,"span_deg":160,
                "thickness_mm":.8,"copper_edge_clearance_target_mm":.25,
                "local_inner_radius_mm":21.3,"local_inner_relief_active":True,
                "edges":edges,"original_edges_without_relief":original_edges,
                "polygon_scad_mm":[round_xy(p) for p in polygon],
                "polygon_kicad_mm":[round_xy(kicad(p)) for p in polygon],
                "approximation_max_sagitta_mm":round(RO*(1-math.cos(math.radians(.25/2))),9),
                "area_before_mount_holes_mm2":round(area,6),
                "area_after_mount_holes_mm2":round(area-2*math.pi*1.1**2,6)},
    "edge_segments":[dict(type=e['type'], start=e['start_kicad_mm'], end=e['end_kicad_mm'],
                          **({'mid':e['mid_kicad_mm']} if e['type']=='arc' else {})) for e in edges],
    "body_bolt_keepouts":[{"angle_scad_deg":a,"radius_from_axis_mm":BOLT_R,
                            "radius_mm":NOTCH_R,"scad_mm":round_xy(polar(BOLT_R,a)),
                            "kicad_mm":round_xy(kicad(polar(BOLT_R,a))),
                            "intersects_board":a in [39,339]} for a in BOLT_ANGLES],
    "mount_holes":holes,"sensors":sensors,
    "inner_sensor_relief_proposal":{
        "required_for":"TI recommended 1.10 x 0.60 mm lands; original inner pad edge clearance is only 0.17023 mm.",
        "inner_radius_mm":21.3,"flat_arc_start_scad_deg":-1,"flat_arc_end_scad_deg":19,
        "transition_start_scad_deg":-3,"transition_end_scad_deg":21,
        "transition":"Linear radius ramp from original21.6 to21.3 over2 degrees at each end.",
        "status":"Active: included in outline.edges, polygon, edge_segments and SCAD profile."
    },
    "narrow_zones":{
        "at_body_bolt_notch_minimum_radial_width_mm":5.4,
        "at_body_bolt_notch_minimum_copper_corridor_mm":4.9,
        "back_components_min_radius_mm":27,
        "back_components_max_radius_mm":33.7,
        "back_components_cavity_depth_mm":2.3,
        "notes":"Do not put back-side components under R27: bearing occupies that region. Front components other than sensors need lid pocket verification. Keep mounting heads and M3 fastener volumes free."
    },
    "tmag5273_source":{
        "datasheet":"https://www.ti.com/lit/ds/symlink/tmag5273.pdf",
        "revision":"SLYS045C, April2026", "hall_location_figure":"6-2, page13",
        "pin_map_figure":"4-1, page4", "package_drawing":"DBV0006A-C02, page54",
        "land_pattern":"4231316/A, page55",
        "hall_depth_from_package_top_mm":.73,
        "package_height_limits_mm":[.9,1.4],
        "hall_height_above_seating_plane_range_mm":[.17,.67],
        "body_molded_size_range_mm":{"radial_x":[1.45,1.75],"tangential_y":[2.75,3.05]},
        "pin1":"Top left at footprint0degrees. Pins1,2,3 run top-to-bottom onleft;6,5,4 top-to-bottom onright."
    }
}
(OUT/"mechanics.json").write_text(json.dumps(info,ensure_ascii=False,indent=2)+"\n")

# SVG: a front view in mechanical coordinates. All geometry is in millimetres.
svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="100mm" height="100mm" viewBox="-8 -43 52 86">',
       '<style>text{font:1.6px sans-serif;fill:#182932}.dim{stroke:#798891;stroke-width:.15;fill:none}.pad{fill:#ba8128;stroke:#573b0b;stroke-width:.08}</style>',
       '<rect x="-8" y="-43" width="52" height="86" fill="white"/>',
       '<text x="-5" y="-39">Encoder board: front / magnets side</text>',
       '<text x="-5" y="-36.5">Outline R21.6 ... R33.4, local R21.3, thickness0.8</text>']
path = 'M '+' L '.join(f'{p[0]:.6f},{-p[1]:.6f}' for p in polygon)+' Z'
svg.append(f'<path d="{path}" fill="#d5eade" stroke="#164c3a" stroke-width=".2"/>')
for h in holes:
    p=h['scad_mm']
    svg.extend([f'<circle cx="{p[0]}" cy="{-p[1]}" r="1.1" fill="white" stroke="#164c3a" stroke-width=".2"/>',
                f'<text x="{p[0]+1.3}" y="{-p[1]}">{h["reference"]}:2.2</text>'])
for s in sensors:
    for p in s['pads']:
        xy=' '.join(f'{v[0]},{-v[1]}' for v in p['corners_scad_mm'])
        svg.append(f'<polygon class="pad" points="{xy}"/>')
    c=s['body_center_scad_mm']; h=s['hall_scad_mm']
    svg.extend([f'<circle cx="{h[0]}" cy="{-h[1]}" r=".25" fill="#cf3341"/>',
                f'<text x="{c[0]-1.5}" y="{-c[1]-2.3}">R{s["track_radius_mm"]}</text>'])
svg.extend(['<path class="dim" d="M-1,0 H3 M0,-1 V3"/>',
            '<text x="-5" y="39">Hall points:red; M2 holes:white; gold:TI lands.</text>',
            '<text x="-5" y="41.5">Local inner relief R21.3 is included for0.25mm copper margin.</text>', '</svg>'])
(OUT/'mechanical_outline.svg').write_text('\n'.join(svg)+'\n')

# ASCII DXF R12, geometry in SCAD XY. Polygon error is at most0.00008mm.
dxf=['0','SECTION','2','HEADER','9','$INSUNITS','70','4','0','ENDSEC',
     '0','SECTION','2','ENTITIES','0','POLYLINE','8','Edge.Cuts','66','1','70','1']
for p in polygon:
    dxf += ['0','VERTEX','8','Edge.Cuts','10',f'{p[0]:.9f}','20',f'{p[1]:.9f}','30','0']
dxf += ['0','SEQEND']
for h in holes:
    p=h['scad_mm']
    dxf += ['0','CIRCLE','8','MountHoles','10',str(p[0]),'20',str(p[1]),'30','0','40','1.1']
dxf += ['0','ENDSEC','0','EOF']
(OUT/'mechanical_outline.dxf').write_text('\n'.join(dxf)+'\n')
print(json.dumps({"area_mm2":info['outline']['area_after_mount_holes_mm2'],
                  "outline_points":len(polygon),"sensor_centers":[s['body_center_kicad_mm'] for s in sensors],
                  "inner_pad_clearance_mm":sensors[0]['minimum_pad_inner_edge_clearance_original_mm']}))
