"""Builds the parchment scroll that holds the hint at the bottom of the screen.

Run with:  blender -b -P art/scripts/scroll.py
Writes art/scroll.blend and public/models/scroll.glb.

Parts, laid out by the site around the hint text (1 unit is drawn as 40 pixels):
  sheet   10 x 1 units, centred on the origin; the site stretches it to the text
  end_l   rolled end for the left side: paper roll, rod and brass knobs, 1.5 units tall
  end_r   the same, mirrored for the right
Parts whose names start with nolines_ get no ink outline.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(__file__))
from lib import _finish, cyl, empty, export_glb, reset_scene, save_blend, sphere  # noqa: E402

import bmesh  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
rng = random.Random(9)

SHEET_W, SHEET_H = 10.0, 1.0
END_H = 1.5


def wavy_sheet(name, parent, w, h, m, depth=0.05, waves=3.0, amp=0.06, segs=48):
    """A thin sheet with gentle ripples across it, so the toon shading picks out folds."""
    bm = bmesh.new()
    front, back = [], []
    for i in range(segs + 1):
        x = -w / 2 + w * i / segs
        y = math.sin(i / segs * math.pi * 2 * waves) * amp
        # edges sag a touch in the middle of each wave, like old paper
        sag = math.sin(i / segs * math.pi * 2 * waves + 1.1) * 0.025
        top, bot = h / 2 - sag, -h / 2 + sag
        front.append((bm.verts.new((x, y - depth / 2, top)), bm.verts.new((x, y - depth / 2, bot))))
        back.append((bm.verts.new((x, y + depth / 2, top)), bm.verts.new((x, y + depth / 2, bot))))
    for i in range(segs):
        ft, fb = front[i]
        ft2, fb2 = front[i + 1]
        bt, bb = back[i]
        bt2, bb2 = back[i + 1]
        bm.faces.new((ft, fb, fb2, ft2))      # front
        bm.faces.new((bt2, bb2, bb, bt))      # back
        bm.faces.new((ft, ft2, bt2, bt))      # top edge
        bm.faces.new((fb2, fb, bb, bb2))      # bottom edge
    bm.faces.new((front[0][0], back[0][0], back[0][1], front[0][1]))
    bm.faces.new((front[-1][1], back[-1][1], back[-1][0], front[-1][0]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return _finish(name, bm, m, (0, 0, 0), (0, 0, 0), parent, smooth=True)


def stain(name, parent, x, z, r):
    """A faint age mark on the parchment."""
    bm = bmesh.new()
    seg = 9
    pts = []
    for i in range(seg):
        a = i / seg * math.tau
        rr = r * rng.uniform(0.7, 1.15)
        pts.append(bm.verts.new((x + math.cos(a) * rr * 1.6, 0, z + math.sin(a) * rr)))
    bm.faces.new(pts)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for v in bm.verts:
        v.co.y = -0.12  # in front of the ripples
    for f in bm.faces:
        if f.normal.y > 0:
            f.normal_flip()
    return _finish(f"nolines_{name}", bm, "parchment2", (0, 0, 0), (0, 0, 0), parent)


def build_sheet():
    s = empty("sheet")
    wavy_sheet("sheet_body", s, SHEET_W, SHEET_H, "parchment")
    for i, (x, z, r) in enumerate([(-3.4, 0.12, 0.16), (-1.2, -0.2, 0.11), (1.6, 0.18, 0.13), (3.8, -0.15, 0.15), (0.3, 0.05, 0.08)]):
        stain(f"sheet_stain_{i}", s, x, z, r)
    return s


def build_end(side):
    """side -1 is the left end, +1 the right. The paper curls toward the middle of the scroll."""
    e = empty(f"end_{'l' if side < 0 else 'r'}")
    # paper rolled round the rod, with a darker band where it overlaps
    cyl("roll", 0.26, 1.18, (0, 0, -0.59), m="parchment2", parent=e, seg=16, smooth=True)
    cyl("nolines_roll_band", 0.265, 0.1, (0, 0, -0.05), m="parchmentdark", parent=e, seg=16, smooth=True)
    # the lip where the sheet leaves the roll, curling round the front
    bm = bmesh.new()
    segs = 8
    rows = []
    for i in range(segs + 1):
        a = math.radians(-90 + 110 * i / segs)  # sweep from the front of the roll round to the inner side
        x, y = math.cos(a) * 0.3 * -side, math.sin(a) * 0.3
        rows.append((bm.verts.new((x, y, 0.5)), bm.verts.new((x, y, -0.5))))
    for i in range(segs):
        (t1, b1), (t2, b2) = rows[i], rows[i + 1]
        bm.faces.new((t1, b1, b2, t2))
    bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=0.03)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    _finish("roll_lip", bm, "parchment", (0, 0, 0), (0, 0, 0), e, smooth=True)
    # wooden rod and brass knobs
    cyl("rod", 0.09, END_H - 0.1, (0, 0, -(END_H - 0.1) / 2), m="wooddark", parent=e, seg=10, smooth=True)
    for i, z in enumerate((END_H / 2 - 0.05, -END_H / 2 - 0.05)):
        cyl(f"knob_collar_{i}", 0.15, 0.1, (0, 0, z - 0.05 if i == 0 else z), m="gold", parent=e, seg=12)
        sphere(f"knob_{i}", 0.14, (0, 0, z + (0.12 if i == 0 else -0.04)), m="gold", parent=e, seg=12, rings=8)
    return e


def main():
    reset_scene()
    build_sheet()
    for side in (-1, 1):
        build_end(side)
    save_blend(os.path.join(ROOT, "art", "scroll.blend"))
    export_glb(os.path.join(ROOT, "public", "models", "scroll.glb"))


main()
