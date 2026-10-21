"""Render actual exported CAD facets; no illustrative replacement geometry."""
from pathlib import Path
import argparse
import numpy as np
import trimesh
import manifold3d as md
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import colors
from matplotlib.path import Path as PlotPath
from matplotlib.patches import PathPatch
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

HERE = Path(__file__).resolve().parent
BUILD = HERE/'build'


def load(name):
    return trimesh.load(BUILD/f'{name}.stl', force='mesh', process=True)


def draw(ax, mesh, color, lift=0, alpha=1):
    triangles = np.asarray(mesh.triangles).copy()
    triangles[:, :, 2] += lift
    base = np.tile(colors.to_rgba(color), (len(triangles), 1))
    if color == '#398875':
        z = mesh.triangles_center[:, 2]
        base[(z < 15.74) | (z > 16.58)] = colors.to_rgba('#38434c')
        base[(z > 16.551) & (z < 16.579)] = colors.to_rgba('#d4b46b')
    if color == '#d75b63':
        centers, poles = [], []
        for radius, count in [(23.5, 24), (29.5, 26)]:
            for j in range(count):
                angle = (j+.5)*360/count
                signed = (angle+180)%360-180
                if -180 <= signed <= 0:
                    centers.append([radius*np.cos(np.deg2rad(angle)), radius*np.sin(np.deg2rad(angle))])
                    poles.append(j%2)
        nearest = np.argmin(np.linalg.norm(mesh.triangles_center[:, None, :2]-np.array(centers)[None], axis=2), axis=1)
        base[np.array(poles)[nearest] == 1] = colors.to_rgba('#4389bd')
    light = np.array([.3, -.35, .88])
    light /= np.linalg.norm(light)
    shade = .65+.35*np.maximum(0, mesh.face_normals@light)
    base[:, :3] *= shade[:, None]
    base[:, 3] = alpha
    ax._cad_triangles.append(triangles)
    ax._cad_colors.append(base)


def model(ax, opened=False):
    ax._cad_triangles, ax._cad_colors = [], []
    draw(ax, load('lower'), '#aeb8bd')
    draw(ax, load('shin'), '#748898')
    draw(ax, load('magnet_ring'), '#bba87d')
    draw(ax, load('magnet'), '#d75b63')
    draw(ax, load('hip'), '#d3dadd')
    draw(ax, load('pcb'), '#398875')
    draw(ax, load('wires'), '#354952')
    draw(ax, load('cover'), '#7fa8be', lift=12 if opened else 0)
    draw(ax, load('screws'), '#bcc7cd', lift=12 if opened else 0)
    # All facets share one depth-sorted collection, so recessed parts are not
    # hidden by the bounding depth of an unrelated large housing mesh.
    ax.add_collection3d(Poly3DCollection(np.concatenate(ax._cad_triangles),
        facecolors=np.concatenate(ax._cad_colors), edgecolors='none', zsort='average'))
    ax.set(xlim=(-21, 43), ylim=(-56, 13), zlim=(-14, 38))
    ax.set_box_aspect((64, 69, 52))
    ax.set_proj_type('ortho')
    ax.view_init(elev=53 if opened else 36, azim=-64)
    ax.set_axis_off()
    ax.set_title('Крышка снята: доступ к плате и проводам' if opened else
                 'Собрано: крышка и винты утоплены', fontsize=13, color='#223d4b', pad=2)


def raster_model(opened=False, mount=False):
    # CPU depth buffer: unlike a painter's algorithm, handles deep pockets and
    # overlapping projected bounds of the housing and its lid correctly.
    class Buffer:
        _cad_triangles = []
        _cad_colors = []
    buffer = Buffer()
    parts = [('shin_original', '#c9d2d8'), ('rotor_base', '#cb8858')] if mount else [
        ('lower', '#aeb8bd'), ('shin', '#748898'),
        ('magnet_ring', '#bba87d'), ('magnet', '#d75b63'),
        ('hip', '#d3dadd'), ('pcb', '#398875'), ('wires', '#354952')]
    for name, color in parts:
        draw(buffer, load(name), color)
    if not opened and not mount:
        for name, color in [('cover', '#7fa8be'), ('screws', '#bcc7cd')]:
            draw(buffer, load(name), color)
    triangles = np.concatenate(buffer._cad_triangles)
    rgba = np.concatenate(buffer._cad_colors)
    width, height = 1050, 850
    image = np.tile(np.array([246, 248, 249], dtype=np.uint8), (height, width, 1))
    depth = np.full((height, width), np.inf)
    azimuth, elevation = np.deg2rad([-70, 20] if mount else [-64, 63 if opened else 36])
    view = np.array([np.cos(elevation)*np.cos(azimuth),
                     np.cos(elevation)*np.sin(azimuth), np.sin(elevation)])
    right = np.cross([0, 0, 1], view)
    right /= np.linalg.norm(right)
    up = np.cross(view, right)
    target = np.array([0, -6, 5] if mount else [5, -20, 10])
    projected = triangles-target
    pixel = np.stack((projected@right*10.7+width/2,
                      height/2-projected@up*10.7), axis=-1)
    z = -projected@view
    for p, zz, color in zip(pixel, z, rgba):
        lo = np.maximum(np.floor(p.min(axis=0)).astype(int), [0, 0])
        hi = np.minimum(np.ceil(p.max(axis=0)).astype(int), [width-1, height-1])
        if np.any(hi < lo):
            continue
        a, b, c = p
        denominator = (b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
        if abs(denominator) < 1e-8:
            continue
        xx, yy = np.meshgrid(np.arange(lo[0], hi[0]+1)+.5,
                             np.arange(lo[1], hi[1]+1)+.5)
        u = ((b[1]-c[1])*(xx-c[0])+(c[0]-b[0])*(yy-c[1]))/denominator
        v = ((c[1]-a[1])*(xx-c[0])+(a[0]-c[0])*(yy-c[1]))/denominator
        w = 1-u-v
        values = u*zz[0]+v*zz[1]+w*zz[2]
        region = depth[lo[1]:hi[1]+1, lo[0]:hi[0]+1]
        valid = (u >= -1e-8) & (v >= -1e-8) & (w >= -1e-8) & (values < region)
        region[valid] = values[valid]
        image[lo[1]:hi[1]+1, lo[0]:hi[0]+1][valid] = np.clip(color[:3]*255, 0, 255).astype(np.uint8)
    return image


def solid(mesh):
    return md.Manifold(md.Mesh64(np.asarray(mesh.vertices, np.float64),
                                np.asarray(mesh.faces, np.uint64)))


def section_path(cross):
    vertices, codes = [], []
    for contour in cross.to_polygons():
        contour = np.asarray(contour)
        vertices.extend(contour)
        vertices.append(contour[0])
        codes.extend([PlotPath.MOVETO]+[PlotPath.LINETO]*(len(contour)-1)+[PlotPath.CLOSEPOLY])
    return PlotPath(vertices, codes)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', type=Path,
                        help='Optional folder containing the previous hip.stl and cover.stl')
    args = parser.parse_args()
    fig = plt.figure(figsize=(13, 6.5), facecolor='#f6f8f9')
    for i, opened in enumerate([False, True], 1):
        ax = fig.add_subplot(1, 2, i, facecolor='#f6f8f9')
        ax.imshow(raster_model(opened))
        ax.axis('off')
        ax.set_title('Крышка снята: доступ к плате и проводам' if opened else
                     'Собрано: крышка и винты утоплены', fontsize=13, color='#223d4b')
    fig.suptitle('Компактный энкодер V2 в колене', fontsize=20, color='#223d4b', y=.96)
    fig.text(.055, .055, 'Та же PCB · крышка заподлицо · боковой выход жгута · съёмный сектор магнитов 0,8 мм',
             fontsize=11, color='#49616f')
    fig.subplots_adjust(left=0, right=1, bottom=.08, top=.88, wspace=0)
    fig.savefig(HERE/'installation_preview.png', dpi=180, facecolor=fig.get_facecolor())
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(10, 7), facecolor='#f6f8f9')
    ax.imshow(raster_model(mount=True))
    ax.axis('off')
    ax.set_title('Основание полукольца: две опоры на шарнире', fontsize=17, color='#223d4b')
    fig.text(.08, .07, 'Серый — исходный рычаг · оранжевый — основание и обе опоры\n'
             'Корни Ø10 мм, расстояние между опорами 50 мм · основание усилено снизу',
             fontsize=11, color='#49616f')
    fig.subplots_adjust(left=0, right=1, bottom=.13, top=.90)
    fig.savefig(HERE/'carrier_mount.png', dpi=170, facecolor=fig.get_facecolor())
    plt.close(fig)
    original = solid(load('hip_original'))
    current = solid(load('hip'))+solid(load('cover'))
    fig, ax = plt.subplots(figsize=(7.5, 7), facecolor='#f6f8f9')
    ax.set_facecolor('#f6f8f9')
    ax.add_patch(PathPatch(section_path(original.project()), fc='#d8dee2', ec='#a9b4bd', lw=.8))
    if args.baseline:
        previous = solid(trimesh.load(args.baseline/'hip.stl', force='mesh'))
        previous += solid(trimesh.load(args.baseline/'cover.stl', force='mesh'))
        extra = previous.project()-original.project()
        ax.add_patch(PathPatch(section_path(extra), fc='#e79892', ec='#bd625d', lw=1, alpha=.8,
                               label='Прежний выступ'))
    extra = current.project()-original.project()
    ax.add_patch(PathPatch(section_path(extra), fc='#5b9abb', ec='#366d8b', lw=1, alpha=.9,
                           label='Новый выступ'))
    board = load('pcb')
    ax.add_patch(PathPatch(section_path(solid(board).project()), fc='#40846c', ec='none', alpha=.8,
                           label='PCB V2'))
    ax.set(xlim=(-22, 45), ylim=(-56, 15), aspect='equal', xlabel='X, мм', ylabel='Y, мм')
    ax.grid(alpha=.18)
    ax.legend(loc='lower left', frameon=True)
    ax.set_title('Контур относительно исходной щеки\nСерое — исходная геометрия', fontsize=14, color='#223d4b')
    fig.tight_layout()
    fig.savefig(HERE/'profile_comparison.png', dpi=170, facecolor=fig.get_facecolor())
    print(HERE/'installation_preview.png')
