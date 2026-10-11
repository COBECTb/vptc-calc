#!/usr/bin/env python3
"""Independent geometric check of placed land patterns, before KiCad DRC."""
import json
import math
import pathlib
import re
from PIL import Image, ImageDraw

ROOT = pathlib.Path(__file__).resolve().parents[1]


def parse(text):
    tokens = re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+', text)
    stack, root = [], []
    current = root
    for t in tokens:
        if t == '(':
            child = []
            current.append(child)
            stack.append(current)
            current = child
        elif t == ')':
            current = stack.pop()
        else:
            current.append(t[1:-1] if t.startswith('"') else t)
    return root[0]


def field(node, name, default=None):
    return next((x[1:] for x in node if isinstance(x, list) and x and x[0] == name), default)


def transform(p, placement):
    a = math.radians(placement.get('angle', placement['a']))
    x, y = p
    if placement.get('side') == 'B':
        y = -y
    pa = math.radians(placement['a'])
    cx, cy = 100 + placement['r']*math.cos(pa), 100 - placement['r']*math.sin(pa)
    return cx+x*math.cos(a)+y*math.sin(a), cy-x*math.sin(a)+y*math.cos(a)


def inside(p, poly):
    x, y = p
    result = False
    for (a, b), (c, d) in zip(poly, poly[1:]+poly[:1]):
        if (b > y) != (d > y) and x < (c-a)*(y-b)/(d-b)+a:
            result = not result
    return result


def distance(p, poly):
    result = 1e9
    for a, b in zip(poly, poly[1:]+poly[:1]):
        dx, dy = b[0]-a[0], b[1]-a[1]
        t = max(0, min(1, ((p[0]-a[0])*dx+(p[1]-a[1])*dy)/(dx*dx+dy*dy)))
        result = min(result, math.hypot(p[0]-a[0]-t*dx, p[1]-a[1]-t*dy))
    return result if inside(p, poly) else -result


def main():
    spec = json.loads((ROOT/'design/electrical_spec.json').read_text())
    placements = json.loads((ROOT/'design/placements.json').read_text())
    mech = json.loads((ROOT/'design/mechanics.json').read_text())
    poly = mech['outline']['polygon_kicad_mm']
    image = Image.new('RGB', (900, 1500), '#f4f3f0')
    draw = ImageDraw.Draw(image)
    def pixel(p):
        return (int((p[0]-97)*22), int((p[1]-66)*22))
    draw.polygon([pixel(p) for p in poly], fill='#d4e9dc', outline='#113b2a')
    for h in mech['mount_holes']:
        x,y = pixel(h['kicad_mm']); r=h['diameter_mm']/2*22
        draw.ellipse((x-r,y-r,x+r,y+r), fill='#f4f3f0', outline='#333333')
    results = []
    for c in spec['components']:
        ref, p = c['ref'], placements[c['ref']]
        lib, name = c['footprint'].split(':')
        path = (ROOT if lib == 'Encoder_CAN' else ROOT/'vendor')/(lib+'.pretty')/(name+'.kicad_mod')
        if not path.exists():
            results.append({'ref':ref,'missing_footprint':str(path)})
            continue
        fp = parse(path.read_text())
        clearances = []
        for pad in [x for x in fp if isinstance(x,list) and x and x[0]=='pad']:
            xy = field(pad,'at',['0','0']); size = list(map(float,field(pad,'size')))
            x,y = map(float,xy[:2]); angle=float(xy[2]) if len(xy)>2 else 0
            points=[]
            for dx,dy in [(-.5,-.5),(-.5,.5),(.5,.5),(.5,-.5)]:
                aa=math.radians(angle)
                xx,yy=dx*size[0],dy*size[1]
                points.append(transform((x+xx*math.cos(aa)-yy*math.sin(aa),y+xx*math.sin(aa)+yy*math.cos(aa)),p))
            clearances += [distance(pt,poly) for pt in points]
            color = '#ce4e3d' if p['side']=='F' else '#447ac2'
            draw.polygon([pixel(pt) for pt in points], fill=color, outline='#363636')
        results.append({'ref':ref,'minimum_rectangular_pad_corner_edge_mm':round(min(clearances),4) if clearances else None})
        loc = transform((0,0),p)
        px,py=pixel(loc)
        draw.text((px+4,py+4),ref,fill='#111111')
    (ROOT/'design/placement_edge_check.json').write_text(json.dumps(results,indent=2)+'\n')
    image.save(ROOT/'design/placement_preview.png')
    for r in results:
        if r.get('missing_footprint') or (r.get('minimum_rectangular_pad_corner_edge_mm') or 0)<.25:
            print(r)


if __name__=='__main__':
    main()
