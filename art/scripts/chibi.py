"""Shared chibi body for every NPC, so all five townsfolk keep the same proportions.

About 1.3 units tall with the head roughly 45% of the height. Origin at the feet,
facing -Y. The body, head and shoulders are empties, so idle loops can animate
them and props can be parented to a hand.
"""
import math

import bpy

from lib import box, cyl, empty, sphere

FPS = 24
LOOP = 48  # frames in one idle cycle (2 seconds)
HAND_Z = -0.3  # hand position relative to its shoulder


class Chibi:
    def __init__(self, root, body, head, arms):
        self.root, self.body, self.head, self.arms = root, body, head, arms


def build_chibi(name, *, shirt, sleeves=None, trousers="trousers", shoes="wooddark", brows="hair",
                bulk=1.0, robe=None, ears=True, belt=None):
    """Body, arms and face. Clothing that differs per NPC is added by the caller.

    robe: colour of a long robe that covers the legs (king, wizard), or None.
    bulk: widens the torso and shoulders (the blacksmith is broader).
    """
    root = empty(name)
    body = empty(f"{name}_body", parent=root)
    head = empty(f"{name}_head", loc=(0, 0, 0.6), parent=body)  # pivots at the neck

    if robe:
        cyl("robe", 0.29 * bulk, 0.6, (0, 0, 0.0), m=robe, parent=body, seg=18, r2=0.17 * bulk, smooth=True)
        for i, sx in enumerate((-1, 1)):
            sphere(f"foot_{i}", 0.08, (sx * 0.1, -0.16, 0.04), m=shoes, parent=root, seg=12, rings=8, scale=(1, 1.3, 0.6))
    else:
        for i, sx in enumerate((-1, 1)):
            sphere(f"foot_{i}", 0.085, (sx * 0.095, -0.03, 0.05), m=shoes, parent=root, seg=12, rings=8, scale=(1, 1.35, 0.65))
            cyl(f"leg_{i}", 0.065, 0.16, (sx * 0.09, 0, 0.06), m=trousers, parent=root, seg=10, smooth=True)
        cyl("torso", 0.25 * bulk, 0.42, (0, 0, 0.18), m=shirt, parent=body, seg=16, r2=0.17 * bulk, smooth=True)
    sphere("torso_top", 0.17 * bulk, (0, 0, 0.6), m=shirt if not robe else robe, parent=body, seg=16, rings=8,
           cut_below=0.0, scale=(1, 1, 0.45))
    if belt:
        cyl("belt", 0.235 * bulk, 0.06, (0, 0, 0.33), m=belt, parent=body, seg=16, r2=0.225 * bulk, smooth=True)

    arms = {}
    for i, sx in enumerate((-1, 1)):
        shoulder = empty(f"{name}_shoulder_{i}", loc=(sx * 0.19 * bulk, 0, 0.52), rot=(0, sx * -18, 0), parent=body)
        cyl(f"arm_{i}", 0.06 * bulk, 0.26, (0, 0, -0.26), m=sleeves or shirt, parent=shoulder, seg=10, smooth=True, r2=0.055 * bulk)
        sphere(f"hand_{i}", 0.075, (0, 0, HAND_Z), m="skin", parent=shoulder, seg=12, rings=8)
        arms[sx] = shoulder

    sphere("head_ball", 0.3, (0, 0, 0.29), m="skin", parent=head, seg=28, rings=18, scale=(1.05, 1, 0.95))
    for i, sx in enumerate((-1, 1)):
        sphere(f"eye_{i}", 0.038, (sx * 0.105, -0.288, 0.3), m="ink", parent=head, seg=10, rings=8, scale=(1, 0.5, 1.25))
        sphere(f"blush_{i}", 0.05, (sx * 0.18, -0.24, 0.22), m="blush", parent=head, seg=10, rings=6, scale=(1, 0.35, 0.6))
        box(f"brow_{i}", (0.08, 0.02, 0.022), (sx * 0.105, -0.28, 0.39), rot=(0, sx * -10, 0), m=brows, parent=head)
        if ears:
            sphere(f"ear_{i}", 0.06, (sx * 0.31, -0.01, 0.27), m="skin", parent=head, seg=10, rings=6, scale=(0.5, 0.8, 1))
    sphere("nose", 0.04, (0, -0.305, 0.25), m="skin", parent=head, seg=10, rings=6)
    return Chibi(root, body, head, arms)


def hold(arm, obj_parent_name, rot_y_cancel):
    """An empty at the hand, rotated so a prop parented to it stays upright at rest."""
    return empty(obj_parent_name, loc=(0, 0, HAND_Z), rot=(0, rot_y_cancel, 0), parent=arm)


# --------------------------------------------------------------------------- animation

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


def setup_timeline():
    scn = bpy.context.scene
    scn.render.fps = FPS
    scn.frame_start = 1
    scn.frame_end = LOOP + 1


def breathe(c, amount=0.03, lift=0.012, beats=2):
    """Small squash and stretch on the body, `beats` breaths per loop."""
    step = LOOP // (beats * 2)
    for k in range(beats * 2 + 1):
        s = 1.0 + (amount if k % 2 else 0.0)
        key(c.body, 1 + k * step, loc=(0, 0, lift if k % 2 else 0.0), scale=(1 / math.sqrt(s), 1 / math.sqrt(s), s))


def keys(obj, frames):
    """frames: list of (frame, rot_degrees) pairs."""
    for f, rot in frames:
        key(obj, f, rot=rot)


def smooth_all(*objs):
    for obj in objs:
        if not obj.animation_data or not obj.animation_data.action:
            continue
        for fc in obj.animation_data.action.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = "BEZIER"
                kp.easing = "AUTO"
