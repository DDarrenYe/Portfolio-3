"""Builds the hanging wooden sign that holds Darren's name and the section buttons.

Run with:  blender -b -P art/scripts/sign.py
Writes art/sign.blend and public/models/sign.glb.

The site assembles the sign from separate parts so it can fit any amount of text:
  post    the upright on the left edge of the screen, with the beam's iron bracket
  brace   the diagonal strut
  beam    10 units long from x=0; the site stretches it along X
  clamp   iron clamp on the beam, placed above each chain
  chain   1 unit long hanging down from z=0, ending in a ring
  board   10 x 3.6 units with its origin at the top centre; the site scales it to the text
1 unit is drawn as 40 pixels. Parts whose names start with nolines_ get no ink outline.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(__file__))
from lib import beam, box, empty, export_glb, mat, prism, reset_scene, save_blend, sphere  # noqa: E402

import bpy  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
rng = random.Random(3)

BOARD_W, BOARD_H = 10.0, 3.6
FRAME = 0.3  # width of the red-brown frame
CHAMFER = 0.45


def octagon(x0, x1, z0, z1, c):
    """Rectangle with its corners cut at 45 degrees, as (x, z) points."""
    return [(x0 + c, z1), (x1 - c, z1), (x1, z1 - c), (x1, z0 + c), (x1 - c, z0), (x0 + c, z0), (x0, z0 + c), (x0, z1 - c)]


def grain(name, parent, x0, x1, z, y, m, count):
    """Short wood-grain strokes along a plank."""
    for i in range(count):
        ln = rng.uniform(0.5, 1.5)
        x = rng.uniform(x0 + ln / 2, x1 - ln / 2)
        box(f"nolines_{name}_{i}", (ln, 0.02, 0.035), (x, y, z + rng.uniform(-0.18, 0.18)), m=m, parent=parent, base=False)


def build_board():
    b = empty("board")
    hw = BOARD_W / 2
    # red-brown frame: a chamfered plate behind the planks
    prism("board_frame", octagon(-hw, hw, -BOARD_H, 0, CHAMFER), 0.32, (0, 0, 0), m="signframe", parent=b, axis="y")
    # planks across the board, clipped to the frame's chamfered corners
    ix0, ix1, iz0, iz1 = -hw + FRAME, hw - FRAME, -BOARD_H + FRAME, -FRAME
    c = CHAMFER - FRAME * 0.4
    n = 4
    ph = (iz1 - iz0) / n
    for i in range(n):
        top = iz1 - i * ph
        bot = top - ph + 0.035
        pts = [(ix0, top), (ix1, top), (ix1, bot), (ix0, bot)]
        if i == 0:
            pts = [(ix0 + c, top), (ix1 - c, top), (ix1, top - c), (ix1, bot), (ix0, bot), (ix0, top - c)]
        if i == n - 1:
            pts = [(ix0, top), (ix1, top), (ix1, bot + c), (ix1 - c, bot), (ix0 + c, bot), (ix0, bot + c)]
        lift = rng.uniform(-0.015, 0.015)
        prism(f"nolines_board_plank_{i}", pts, 0.14, (0, -0.2 + lift, 0), m="signwood" if i % 2 == 0 else "signwood2", parent=b, axis="y")
        grain(f"board_grain_{i}", b, ix0 + 0.3, ix1 - 0.3, (top + bot) / 2, -0.28, "signgrain", 4)
        for j, x in enumerate((ix0 + 0.22, ix1 - 0.22)):
            sphere(f"nolines_board_nail_{i}_{j}", 0.055, (x, -0.27, (top + bot) / 2), m="iron", parent=b, seg=8, rings=6)
    return b


def build_chain():
    ch = empty("chain")
    links = 5
    step = 1.0 / links
    for i in range(links):
        z = -step * (i + 0.5)
        bpy.ops.mesh.primitive_torus_add(major_segments=12, minor_segments=6, major_radius=0.085, minor_radius=0.03,
                                         location=(0, 0, z), rotation=(math.radians(90), 0, math.radians(90 if i % 2 else 0)))
        o = bpy.context.active_object
        o.name = f"chain_link_{i}"
        o.scale = (1, 1.35, 1)
        o.data.materials.append(mat("iron"))
        o.parent = ch
    return ch


def build_beam():
    bm_ = empty("beam")
    box("beam_body", (10.0, 0.5, 0.6), (5.0, 0, -0.3), m="weathered", parent=bm_, base=False)
    box("beam_top", (10.0, 0.52, 0.12), (5.0, 0, -0.06), m="weathered2", parent=bm_, base=False)
    for i in range(6):
        ln = rng.uniform(0.8, 2.2)
        box(f"nolines_beam_grain_{i}", (ln, 0.02, 0.035), (rng.uniform(0.6, 9.4), -0.26, rng.uniform(-0.48, -0.2)),
            m="weatheredgrain", parent=bm_, base=False)
    return bm_


def build_clamp():
    cl = empty("clamp")
    box("clamp_body", (0.5, 0.62, 0.78), (0, 0, -0.3), m="slate", parent=cl, base=False)
    sphere("clamp_rivet", 0.07, (0, -0.32, -0.3), m="steel", parent=cl, seg=8, rings=6)
    return cl


def build_post():
    p = empty("post")
    box("post_body", (0.6, 0.5, 6.5), (0.3, 0.05, -5.0), m="weathered", parent=p)
    for i in range(4):
        box(f"nolines_post_grain_{i}", (0.035, 0.02, rng.uniform(0.8, 1.6)), (rng.uniform(0.12, 0.48), -0.21, rng.uniform(-4.6, -1.2)),
            m="weatheredgrain", parent=p)
    # iron bracket where the beam meets the post
    box("post_bracket", (0.95, 0.6, 0.82), (0.42, -0.02, -0.71), m="slate", parent=p)
    for i, x in enumerate((0.2, 0.68)):
        sphere(f"post_rivet_{i}", 0.06, (x, -0.33, -0.3), m="steel", parent=p, seg=8, rings=6)
    return p


def build_brace():
    br = empty("brace")
    # short and steep, so it stays above the top of the board hanging beside the post
    beam("brace_body", (0.5, -0.02, -1.5), (1.7, -0.02, -0.5), 0.26, m="weathered", parent=br)
    return br


def main():
    reset_scene()
    build_post()
    build_brace()
    build_beam()
    build_clamp()
    build_chain()
    build_board()
    save_blend(os.path.join(ROOT, "art", "sign.blend"))
    export_glb(os.path.join(ROOT, "public", "models", "sign.glb"))


main()
