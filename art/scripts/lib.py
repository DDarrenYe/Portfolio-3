"""Shared helpers for the Castle Hill model scripts.

Conventions (Blender side, Z up; the glTF exporter converts to Y up):
  * 1 Blender unit = 1 town unit. The town disc is 24 units across.
  * Front of the town faces -Y (it becomes +Z in three.js, toward the camera).
  * Every object's origin sits at its base, so code can place things on the ground.
  * Materials are flat colours named pal_<name>. The site swaps them for toon
    materials of the same colour, so lighting and outlines live in code, not here.
"""
import math
import random

import bmesh
import bpy
from mathutils import Euler, Matrix, Vector

PALETTE = {
    "plaster": "#f7f1e3",
    "cobble": "#b8c4d4",
    "stonedark": "#9aa7ba",
    "paving": "#d3c8ad",
    "roof": "#d4825a",
    "roof2": "#e39b6f",
    "slate": "#5e5874",
    "slate2": "#726b8a",
    "timber": "#7a5236",
    "wooddark": "#553826",
    "leaf": "#6fa94c",
    "leafdark": "#4f8a3a",
    "grass": "#8cbf5f",
    "earth": "#8a6446",
    "lamp": "#f2d98a",
    "glass": "#3d4a63",
    "iron": "#8a93a6",
    "pot": "#6f9b86",
    "flower": "#e88aa8",
    "flower2": "#8f9de8",
    "mat": "#5b7fd0",
    "skin": "#f3cfa8",
    "blush": "#ee9d8f",
    "ink": "#2a2d3a",
    "shirt": "#5f86b8",
    "apron": "#f4ecda",
    "trousers": "#4d4a63",
    "hair": "#6b4630",
    "scarf": "#d0624b",
    # blockout greys
    "block": "#c9ced8",
    "blockroof": "#a9afbd",
}


def srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def mat(name):
    """Get or create the flat palette material pal_<name>."""
    full = f"pal_{name}"
    m = bpy.data.materials.get(full)
    if m:
        return m
    h = PALETTE[name].lstrip("#")
    rgb = [srgb_to_linear(int(h[i:i + 2], 16) / 255) for i in (0, 2, 4)]
    m = bpy.data.materials.new(full)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*rgb, 1)
    bsdf.inputs["Roughness"].default_value = 1.0
    bsdf.inputs["Metallic"].default_value = 0.0
    m.diffuse_color = (*rgb, 1)
    return m


def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.unit_settings.system = "METRIC"


def empty(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None):
    o = bpy.data.objects.new(name, None)
    o.empty_display_size = 0.3
    o.location = loc
    o.rotation_euler = Euler([math.radians(a) for a in rot])
    bpy.context.scene.collection.objects.link(o)
    if parent:
        o.parent = parent
    return o


def _finish(name, bm, m, loc, rot, parent, smooth=False, bevel=0.0, bevel_segments=1):
    me = bpy.data.meshes.new(name)
    if smooth:
        for f in bm.faces:
            f.smooth = True
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    o.data.materials.append(mat(m))
    o.location = loc
    o.rotation_euler = Euler([math.radians(a) for a in rot])
    bpy.context.scene.collection.objects.link(o)
    if parent:
        o.parent = parent
    if bevel > 0:
        mod = o.modifiers.new("bevel", "BEVEL")
        mod.width = bevel
        mod.segments = bevel_segments
        mod.limit_method = "ANGLE"
        mod.harden_normals = False
    return o


def box(name, size, loc=(0, 0, 0), rot=(0, 0, 0), m="block", parent=None, base=True, bevel=0.0):
    """Box of size (x, y, z). With base=True the origin is at the bottom centre."""
    sx, sy, sz = size
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    off = 0.5 if base else 0.0
    for v in bm.verts:
        v.co = Vector((v.co.x * sx, v.co.y * sy, (v.co.z + off) * sz))
    return _finish(name, bm, m, loc, rot, parent, bevel=bevel)


def cyl(name, r, h, loc=(0, 0, 0), rot=(0, 0, 0), m="block", parent=None, seg=12, r2=None, smooth=False, bevel=0.0):
    """Cylinder (or cone/frustum with r2) standing on its base."""
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg,
                          radius1=r, radius2=r if r2 is None else r2, depth=h)
    bmesh.ops.translate(bm, verts=bm.verts, vec=(0, 0, h / 2))
    return _finish(name, bm, m, loc, rot, parent, smooth=smooth, bevel=bevel)


def sphere(name, r, loc=(0, 0, 0), rot=(0, 0, 0), m="block", parent=None, scale=(1, 1, 1), seg=16, rings=10, smooth=True, cut_below=None):
    """UV sphere centred on loc. cut_below (local z) deletes the lower part, for caps and hair."""
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=rings, radius=r)
    if cut_below is not None:
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < cut_below - 1e-4], context="VERTS")
        # close the open rim so the inverted-hull outline has a solid shape
        edges = [e for e in bm.edges if e.is_boundary]
        if edges:
            bmesh.ops.holes_fill(bm, edges=edges, sides=0)
    for v in bm.verts:
        v.co = Vector((v.co.x * scale[0], v.co.y * scale[1], v.co.z * scale[2]))
    return _finish(name, bm, m, loc, rot, parent, smooth=smooth)


def prism(name, verts2d, depth, loc=(0, 0, 0), rot=(0, 0, 0), m="block", parent=None, axis="x"):
    """Extrude a 2D polygon (in the YZ plane for axis='x', XZ for axis='y') by depth, centred."""
    bm = bmesh.new()
    d = depth / 2
    if axis == "x":
        front = [bm.verts.new((-d, a, b)) for a, b in verts2d]
        back = [bm.verts.new((d, a, b)) for a, b in verts2d]
    else:
        front = [bm.verts.new((a, -d, b)) for a, b in verts2d]
        back = [bm.verts.new((a, d, b)) for a, b in verts2d]
    bm.faces.new(front[::-1] if axis == "x" else front)
    bm.faces.new(back if axis == "x" else back[::-1])
    n = len(verts2d)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((front[i], front[j], back[j], back[i]) if axis == "x" else (front[i], back[i], back[j], front[j]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return _finish(name, bm, m, loc, rot, parent)


def disc_patch(name, r, loc, normal_rot, m="cobble", parent=None, seg=7, depth=0.035, rng=None):
    """A flat, slightly irregular stone set into a wall. normal_rot orients its face."""
    rng = rng or random
    bm = bmesh.new()
    top, bot = [], []
    for i in range(seg):
        a = i / seg * math.tau
        rr = r * (0.8 + rng.random() * 0.35)
        x, y = math.cos(a) * rr * 1.25, math.sin(a) * rr
        top.append(bm.verts.new((x, y, depth)))
        bot.append(bm.verts.new((x, y, 0)))
    bm.faces.new(top)
    bm.faces.new(bot[::-1])
    for i in range(seg):
        j = (i + 1) % seg
        bm.faces.new((bot[i], bot[j], top[j], top[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return _finish(name, bm, m, loc, normal_rot, parent)


def gable_planks(name, parent, width, depth, wall_top, ridge, overhang=0.25, plank=0.34, thick=0.07,
                 colors=("roof", "roof2"), rng=None, ridge_mat="timber"):
    """Plank roof over a box footprint, ridge along X. Planks run down the slope with
    slightly ragged ends and a few degrees of wobble, like the reference's hand-drawn roofs."""
    rng = rng or random
    half = depth / 2 + overhang
    rise = ridge - wall_top
    slope_len = math.hypot(half, rise) + 0.05
    ang = math.degrees(math.atan2(rise, half))
    span = width + overhang * 2
    n = max(2, round(span / plank))
    pw = span / n
    roof = empty(name, parent=parent)
    for side in (-1, 1):
        for i in range(n):
            x = -span / 2 + pw * (i + 0.5)
            ln = slope_len + rng.uniform(-0.1, 0.06)
            # plank hangs from the ridge down toward this side
            mid = ln / 2
            cy = side * math.cos(math.radians(ang)) * mid
            cz = ridge - math.sin(math.radians(ang)) * mid + thick * 0.5
            box(f"{name}_p{side}_{i}", (pw - 0.025, ln, thick), (x, cy, cz),
                    rot=(-side * ang + rng.uniform(-1.5, 1.5), 0, rng.uniform(-3, 3)),
                    m=colors[(i + (side > 0)) % len(colors)], parent=roof, base=False, bevel=0.012)
    box(f"{name}_ridge", (span + 0.1, 0.18, 0.14), (0, 0, ridge + 0.04), m=ridge_mat, parent=roof, base=False, bevel=0.015)
    return roof


def gable_fill(name, parent, width, depth, wall_top, ridge, m="plaster"):
    """Triangular wall pieces closing the two gable ends."""
    half = depth / 2
    pts = [(-half, wall_top), (half, wall_top), (0, ridge)]
    return prism(name, pts, width, m=m, parent=parent, axis="x")


def export_glb(path, objects=None, animations=False):
    bpy.ops.object.select_all(action="DESELECT")
    if objects:
        for o in objects:
            o.select_set(True)
            for c in o.children_recursive:
                c.select_set(True)
    bpy.ops.export_scene.gltf(
        filepath=path,
        export_format="GLB",
        use_selection=bool(objects),
        export_apply=True,
        export_yup=True,
        export_animations=animations,
        export_animation_mode="SCENE",
        export_cameras=False,
        export_lights=False,
        export_materials="EXPORT",
        export_extras=False,
    )


def save_blend(path):
    bpy.ops.wm.save_as_mainfile(filepath=path, compress=True)
