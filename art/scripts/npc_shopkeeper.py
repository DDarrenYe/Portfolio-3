"""Builds the shopkeeper, the first finished chibi NPC.

Run with:  blender -b -P art/scripts/npc_shopkeeper.py
Writes art/npc_shopkeeper.blend and public/models/npc_shopkeeper.glb.

Proportions follow the plan: about 1.3 units tall, head roughly 45% of the height.
Origin at the feet, facing -Y. The idle loop is a 2 second cycle of breathing,
a head tilt and a little wave, exported as the glTF's only animation.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from lib import box, cyl, empty, export_glb, reset_scene, save_blend, sphere  # noqa: E402

import bpy  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
FPS = 24
LOOP = 48  # frames


def build():
    root = empty("npc_shopkeeper")
    body = empty("body", parent=root)            # bobs and breathes
    head = empty("head", loc=(0, 0, 0.6), parent=body)  # pivots at the neck

    # feet and legs
    for i, sx in enumerate((-1, 1)):
        sphere(f"foot_{i}", 0.085, (sx * 0.095, -0.03, 0.05), m="wooddark", parent=root, seg=12, rings=8, scale=(1, 1.35, 0.65))
        cyl(f"leg_{i}", 0.065, 0.16, (sx * 0.09, 0, 0.06), m="trousers", parent=root, seg=10, smooth=True)

    # torso: a rounded frustum with an apron and belt
    cyl("torso", 0.25, 0.42, (0, 0, 0.18), m="shirt", parent=body, seg=16, r2=0.17, smooth=True)
    sphere("torso_top", 0.17, (0, 0, 0.6), m="shirt", parent=body, seg=16, rings=8, cut_below=0.0, scale=(1, 1, 0.45))
    cyl("belt", 0.235, 0.06, (0, 0, 0.33), m="timber", parent=body, seg=16, r2=0.225, smooth=True)
    box("apron", (0.3, 0.035, 0.34), (0, -0.215, 0.2), rot=(-9, 0, 0), m="apron", parent=body, bevel=0.012)
    box("apron_pocket", (0.14, 0.02, 0.08), (0, -0.24, 0.27), rot=(-9, 0, 0), m="timber", parent=body)
    box("apron_strap_l", (0.04, 0.02, 0.24), (-0.09, -0.17, 0.48), rot=(-22, 0, 0), m="apron", parent=body)
    box("apron_strap_r", (0.04, 0.02, 0.24), (0.09, -0.17, 0.48), rot=(-22, 0, 0), m="apron", parent=body)

    # arms hang from shoulder pivots so the wave can rotate them
    arms = {}
    for i, sx in enumerate((-1, 1)):
        shoulder = empty(f"shoulder_{i}", loc=(sx * 0.19, 0, 0.52), rot=(0, sx * -18, 0), parent=body)
        cyl(f"arm_{i}", 0.06, 0.26, (0, 0, -0.26), m="shirt", parent=shoulder, seg=10, smooth=True, r2=0.055)
        sphere(f"hand_{i}", 0.075, (0, 0, -0.3), m="skin", parent=shoulder, seg=12, rings=8)
        arms[sx] = shoulder

    # head
    sphere("head_ball", 0.3, (0, 0, 0.29), m="skin", parent=head, seg=28, rings=18, scale=(1.05, 1, 0.95))
    for i, sx in enumerate((-1, 1)):
        sphere(f"eye_{i}", 0.038, (sx * 0.105, -0.288, 0.3), m="ink", parent=head, seg=10, rings=8, scale=(1, 0.5, 1.25))
        sphere(f"blush_{i}", 0.05, (sx * 0.18, -0.24, 0.22), m="blush", parent=head, seg=10, rings=6, scale=(1, 0.35, 0.6))
        box(f"brow_{i}", (0.08, 0.02, 0.022), (sx * 0.105, -0.28, 0.39), rot=(0, sx * -10, 0), m="hair", parent=head)
        sphere(f"ear_{i}", 0.06, (sx * 0.31, -0.01, 0.27), m="skin", parent=head, seg=10, rings=6, scale=(0.5, 0.8, 1))
        # bushy moustache, the shopkeeper's signature
        sphere(f"moustache_{i}", 0.06, (sx * 0.055, -0.29, 0.2), rot=(0, sx * 20, 0), m="hair", parent=head, seg=10, rings=6, scale=(1.3, 0.6, 0.7))
    sphere("nose", 0.04, (0, -0.305, 0.25), m="skin", parent=head, seg=10, rings=6)

    # headscarf with a knot at the back
    sphere("scarf", 0.315, (0, 0.005, 0.31), m="scarf", parent=head, seg=28, rings=18, cut_below=0.1, scale=(1.06, 1.02, 1.0))
    sphere("scarf_knot", 0.07, (0, 0.31, 0.38), m="scarf", parent=head, seg=10, rings=6)
    sphere("scarf_tail_0", 0.06, (-0.05, 0.33, 0.28), rot=(20, 0, 0), m="scarf", parent=head, seg=10, rings=6, scale=(0.8, 0.5, 1.5))
    sphere("scarf_tail_1", 0.06, (0.06, 0.33, 0.29), rot=(20, 0, 0), m="scarf", parent=head, seg=10, rings=6, scale=(0.8, 0.5, 1.5))

    return root, body, head, arms


def key(obj, frame, loc=None, rot=None, scale=None):
    if loc is not None:
        obj.location = loc
        obj.keyframe_insert("location", frame=frame)
    if rot is not None:
        obj.rotation_euler = [math.radians(a) for a in rot]
        obj.keyframe_insert("rotation_euler", frame=frame)
    if scale is not None:
        obj.scale = scale
        obj.keyframe_insert("scale", frame=frame)


def animate(body, head, arms):
    scn = bpy.context.scene
    scn.render.fps = FPS
    scn.frame_start = 1
    scn.frame_end = LOOP + 1
    q = LOOP // 4
    # breathing: a small squash and stretch on the body
    for f, s, z in [(1, 1.0, 0.0), (1 + q, 1.03, 0.012), (1 + 2 * q, 1.0, 0.0), (1 + 3 * q, 1.03, 0.012), (1 + LOOP, 1.0, 0.0)]:
        key(body, f, loc=(0, 0, z), scale=(1 / math.sqrt(s), 1 / math.sqrt(s), s))
    # head tilts side to side once per loop
    for f, tilt in [(1, 0), (1 + q, 6), (1 + 2 * q, 0), (1 + 3 * q, -6), (1 + LOOP, 0)]:
        key(head, f, rot=(0, tilt, 0))
    # right arm gives a small wave in the first half, left arm sways
    r, l = arms[1], arms[-1]
    for f, rx, ry in [(1, 0, -18), (1 + q // 2, -10, -60), (1 + q, -10, -80), (1 + q + q // 2, -10, -60), (1 + 2 * q, 0, -18), (1 + LOOP, 0, -18)]:
        key(r, f, rot=(rx, ry, 0))
    for f, rx in [(1, 0), (1 + 2 * q, 6), (1 + LOOP, 0)]:
        key(l, f, rot=(rx, 18, 0))
    for obj in (body, head, r, l):
        for fc in obj.animation_data.action.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = "BEZIER"
                kp.easing = "AUTO"


def main():
    reset_scene()
    root, body, head, arms = build()
    animate(body, head, arms)
    save_blend(os.path.join(ROOT, "art", "npc_shopkeeper.blend"))
    export_glb(os.path.join(ROOT, "public", "models", "npc_shopkeeper.glb"), animations=True)


main()
