"""Builds the Castle Hill town: ground, hill, castle, landmarks and houses.

Run with:  blender -b -P art/scripts/town.py
Writes art/town.blend and public/models/town.glb.

At this stage the landmarks, castle and filler houses are grey blockout at their
final sizes. One finished house (house_showcase) shows the target style.
Empties named spot_<npc> mark where each NPC stands; the site reads them.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(__file__))
from lib import (box, cyl, disc_patch, empty, export_glb, gable_fill, gable_planks, mat, prism,
                 reset_scene, save_blend, sphere, _finish)  # noqa: E402

import bmesh  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
rng = random.Random(42)

# Layout radii (units from the town centre)
TOWN_R = 12.0
HILL_PROFILE = [(4.6, 0.0), (4.25, 0.8), (3.6, 1.65), (2.9, 2.25), (2.4, 2.48), (0.0, 2.5)]
HILL_TOP = 2.5
INNER_R = 6.4     # centre line of the inner ring of houses
OUTER_R = 9.0     # centre line of the outer ring (houses + landmarks)
NPC_R = 10.75     # where landmark NPCs stand, in front of their doors
STREETS = [45, 135, 225, 315]
# Landmarks on the outer ring. Angle 270 is the front of the town (toward the camera).
LANDMARKS = {"stall": 270, "smithy": 0, "wizard": 90, "guild": 180}
SHOWCASE_ANGLE = 270 + 27


def polar(r, deg):
    a = math.radians(deg)
    return r * math.cos(a), r * math.sin(a)


def facing_out(deg):
    """Z rotation that turns an object's -Y front to face away from the centre."""
    return deg + 90


def hill_height(r):
    for (r0, z0), (r1, z1) in zip(HILL_PROFILE, HILL_PROFILE[1:]):
        if r1 <= r <= r0:
            t = (r0 - r) / (r0 - r1)
            return z0 + (z1 - z0) * t
    return HILL_TOP if r < HILL_PROFILE[-2][0] else 0.0


def ang_dist(a, b):
    return abs((a - b + 180) % 360 - 180)


# --------------------------------------------------------------------------- ground

def lathe(name, profile, seg, m, parent=None):
    bm = bmesh.new()
    rings = []
    for r, z in profile:
        if r == 0:
            rings.append([bm.verts.new((0, 0, z))])
            continue
        rings.append([bm.verts.new((math.cos(i / seg * math.tau) * r, math.sin(i / seg * math.tau) * r, z)) for i in range(seg)])
    for a, b in zip(rings, rings[1:]):
        for i in range(seg):
            j = (i + 1) % seg
            if len(b) == 1:
                bm.faces.new((a[i], a[j], b[0]))
            else:
                bm.faces.new((a[i], a[j], b[j], b[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return _finish(name, bm, m, (0, 0, 0), (0, 0, 0), parent, smooth=True)


def build_ground(root):
    g = empty("ground", parent=root)
    cyl("ground_paving", TOWN_R, 0.3, (0, 0, -0.3), m="paving", parent=g, seg=48)
    # floating chunk of earth under the disc, ragged at the bottom
    bm = bmesh.new()
    seg = 28
    top = [bm.verts.new((math.cos(i / seg * math.tau) * (TOWN_R - 0.05), math.sin(i / seg * math.tau) * (TOWN_R - 0.05), -0.3)) for i in range(seg)]
    mid = []
    for i in range(seg):
        r = TOWN_R * rng.uniform(0.78, 0.86)
        mid.append(bm.verts.new((math.cos(i / seg * math.tau) * r, math.sin(i / seg * math.tau) * r, rng.uniform(-2.0, -1.6))))
    tip = bm.verts.new((0, 0, -4.2))
    for i in range(seg):
        j = (i + 1) % seg
        bm.faces.new((top[j], top[i], mid[i], mid[j]))
        bm.faces.new((mid[j], mid[i], tip))
    bm.faces.new(top)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    _finish("ground_earth", bm, "earth", (0, 0, 0), (0, 0, 0), g)

    # low stone parapet around the rim
    n = 56
    for i in range(n):
        deg = i / n * 360
        if any(ang_dist(deg, s) < 2.5 for s in STREETS):
            continue  # gaps where streets meet the edge
        x, y = polar(TOWN_R - 0.3, deg)
        box(f"wall_{i}", (1.18, 0.42, rng.uniform(0.32, 0.42)), (x, y, 0), rot=(0, 0, deg + 90 + rng.uniform(-3, 3)),
            m="cobble" if i % 3 else "stonedark", parent=g, bevel=0.04)

    # cobbles scattered in the streets for texture
    for i in range(140):
        r = rng.uniform(4.9, TOWN_R - 0.9)
        deg = rng.uniform(0, 360)
        x, y = polar(r, deg)
        box(f"cobble_{i}", (rng.uniform(0.25, 0.45), rng.uniform(0.2, 0.32), 0.03), (x, y, 0), rot=(0, 0, rng.uniform(0, 180)),
            m="cobble", parent=g)

    # hill and the winding path to the castle gate
    lathe("hill", HILL_PROFILE, 40, "grass", parent=g)
    steps = 46
    for i in range(steps):
        t = i / (steps - 1)
        deg = 270 + t * 330
        r = 4.75 - t * 2.35
        x, y = polar(r, deg)
        z = hill_height(r)
        box(f"path_{i}", (0.62, 0.42, 0.08), (x, y, z - 0.02), rot=(0, 0, deg + rng.uniform(-6, 6)), m="paving", parent=g, bevel=0.02)
    # bushes dotted on the hill
    for i in range(16):
        deg = rng.uniform(0, 360)
        r = rng.uniform(2.9, 4.2)
        if ang_dist(deg, (270 + (4.75 - r) / 2.35 * 330) % 360) < 25:
            continue
        x, y = polar(r, deg)
        s = rng.uniform(0.28, 0.45)
        sphere(f"bush_{i}", s, (x, y, hill_height(r) + s * 0.4), m="leafdark" if i % 2 else "leaf", parent=g, seg=10, rings=7)


# --------------------------------------------------------------------------- blockout

def blockout_house(name, parent, loc, rot_z, w, d, h):
    o = empty(name, loc=(*loc, 0), rot=(0, 0, rot_z), parent=parent)
    wall = h * 0.66
    box(f"{name}_walls", (w, d, wall), m="block", parent=o, bevel=0.03)
    gable_fill(f"{name}_gable", o, w, d, wall, h, m="blockroof")
    half = d / 2 + 0.18
    prism(f"{name}_roof", [(-half, wall - 0.08), (half, wall - 0.08), (0, h + 0.06)], w + 0.3, m="blockroof", parent=o, axis="x")
    return o


def build_castle(root):
    c = empty("castle", loc=(0, 0, HILL_TOP), parent=root)
    box("castle_base", (3.4, 3.4, 0.5), m="block", parent=c, bevel=0.05)
    box("castle_keep", (2.6, 2.6, 3.7), (0, 0, 0.0), m="block", parent=c, bevel=0.05)
    for i, (dx, dy) in enumerate([(-1.45, -1.45), (1.45, -1.45), (-1.45, 1.45), (1.45, 1.45)]):
        cyl(f"castle_tower_{i}", 0.5, 2.9, (dx, dy, 0), m="block", parent=c, seg=12)
        cyl(f"castle_tower_{i}_roof", 0.68, 1.0, (dx, dy, 2.9), m="blockroof", parent=c, seg=12, r2=0.0)
    cyl("castle_spire", 1.25, 1.3, (0, 0, 3.7), m="blockroof", parent=c, seg=4, r2=0.0)
    box("castle_gate", (1.0, 0.3, 1.25), (0, -1.38, 0.0), m="blockroof", parent=c)
    empty("spot_king", loc=(0, -2.05, 0.0), rot=(0, 0, 0), parent=c)


def build_landmarks(root):
    lm = empty("landmarks", parent=root)

    # market stall (front)
    deg = LANDMARKS["stall"]
    x, y = polar(OUTER_R + 0.6, deg)
    s = empty("stall", loc=(x, y, 0), rot=(0, 0, facing_out(deg)), parent=lm)
    box("stall_counter", (2.3, 1.0, 1.0), m="block", parent=s, bevel=0.03)
    for i, dx in enumerate((-1.05, 1.05)):
        box(f"stall_post_{i}", (0.12, 0.12, 2.2), (dx, -0.45, 0), m="blockroof", parent=s)
    prism("stall_awning", [(-0.75, 2.0), (0.55, 2.35), (0.55, 2.45), (-0.75, 2.1)], 2.6, m="blockroof", parent=s, axis="x")

    # smithy (right)
    deg = LANDMARKS["smithy"]
    x, y = polar(OUTER_R, deg)
    s = empty("smithy", loc=(x, y, 0), rot=(0, 0, facing_out(deg)), parent=lm)
    blockout_house("smithy_body", s, (0, 0), 0, 3.0, 2.4, 3.5)
    box("smithy_chimney", (0.55, 0.55, 3.9), (0.9, 0.5, 0), m="blockroof", parent=s)
    box("smithy_forge", (0.9, 0.8, 0.8), (-0.8, -1.55, 0), m="blockroof", parent=s, bevel=0.03)
    box("smithy_anvil", (0.45, 0.22, 0.45), (0.5, -1.7, 0), m="blockroof", parent=s)

    # wizard tower (back)
    deg = LANDMARKS["wizard"]
    x, y = polar(OUTER_R + 0.2, deg)
    s = empty("wizard", loc=(x, y, 0), rot=(0, 0, facing_out(deg)), parent=lm)
    cyl("wizard_base", 1.25, 0.6, m="block", parent=s, seg=14)
    cyl("wizard_tower", 1.0, 4.1, (0, 0, 0.6), m="block", parent=s, seg=14, r2=0.9)
    cyl("wizard_roof", 1.25, 1.5, (0, 0, 4.5), m="blockroof", parent=s, seg=14, r2=0.0)
    box("wizard_door", (0.6, 0.2, 1.0), (0, -1.15, 0.0), m="blockroof", parent=s)

    # guild hall (left)
    deg = LANDMARKS["guild"]
    x, y = polar(OUTER_R, deg)
    s = empty("guild", loc=(x, y, 0), rot=(0, 0, facing_out(deg)), parent=lm)
    blockout_house("guild_body", s, (0, 0), 0, 3.6, 2.6, 4.5)
    box("guild_board", (0.8, 0.1, 0.6), (1.2, -1.36, 0.8), m="blockroof", parent=s)

    for name, deg in LANDMARKS.items():
        x, y = polar(NPC_R, deg)
        npc = {"stall": "shopkeeper", "smithy": "blacksmith", "wizard": "wizard", "guild": "adventurer"}[name]
        empty(f"spot_{npc}", loc=(x, y, 0), rot=(0, 0, facing_out(deg)), parent=root)


def fill_ring(root, r, depth, hmin, hmax, skip, prefix):
    """Pack houses tangentially around a ring, leaving gaps for streets and reserved arcs."""
    ring = empty(prefix, parent=root)
    circ = math.tau * r
    deg = rng.uniform(0, 4)
    i = 0
    while deg < 360:
        w = rng.uniform(1.5, 2.3)
        span = w / circ * 360
        centre = deg + span / 2
        blocked = any(ang_dist(centre, s) < 4.2 + span / 2 for s in STREETS) or any(
            ang_dist(centre, a) < half + span / 2 for a, half in skip)
        if blocked:
            deg += 1.5
            continue
        x, y = polar(r + rng.uniform(-0.15, 0.15), centre)
        if rng.random() < 0.1:
            # a tree instead of a house now and then
            t = empty(f"{prefix}_tree_{i}", loc=(x, y, 0), parent=ring)
            cyl(f"{prefix}_tree_{i}_trunk", 0.12, 1.2, m="timber", parent=t, seg=6)
            sphere(f"{prefix}_tree_{i}_crown", 0.75, (0, 0, 1.75), m="leaf", parent=t, seg=12, rings=8)
        else:
            blockout_house(f"{prefix}_h{i}", ring, (x, y), facing_out(centre) + rng.uniform(-4, 4), w, depth * rng.uniform(0.85, 1.0),
                           rng.uniform(hmin, hmax))
        deg += span + 0.6
        i += 1


# --------------------------------------------------------------------------- finished house

def showcase_house(root, loc, rot_z):
    """The finished house that sets the style for every other building."""
    o = empty("house_showcase", loc=(*loc, 0), rot=(0, 0, rot_z), parent=root)
    r = random.Random(7)
    W, D = 2.3, 2.0
    PLINTH = 0.25
    WALL_TOP = 2.15
    RIDGE = 3.05

    box("hs_plinth", (W + 0.14, D + 0.14, PLINTH), m="stonedark", parent=o, bevel=0.04)
    box("hs_walls", (W, D, WALL_TOP - PLINTH), (0, 0, PLINTH), m="plaster", parent=o, bevel=0.03)
    gable_fill("hs_gable", o, W - 0.02, D, WALL_TOP, RIDGE - 0.12, m="plaster")

    # timber frame: corner posts and a mid-height band
    for i, (sx, sy) in enumerate([(-1, -1), (1, -1), (-1, 1), (1, 1)]):
        box(f"hs_post_{i}", (0.15, 0.15, WALL_TOP - PLINTH), (sx * W / 2, sy * D / 2, PLINTH), m="timber", parent=o, bevel=0.02)
    box("hs_band_front", (W + 0.08, 0.1, 0.12), (0, -D / 2 - 0.02, 1.3), m="timber", parent=o, bevel=0.015)
    box("hs_band_right", (0.1, D + 0.08, 0.12), (W / 2 + 0.02, 0, 1.3), m="timber", parent=o, bevel=0.015)
    box("hs_band_left", (0.1, D + 0.08, 0.12), (-W / 2 - 0.02, 0, 1.3), m="timber", parent=o, bevel=0.015)

    # stones showing through the plaster
    for i, (px, pz, pr) in enumerate([(-0.85, 0.55, 0.13), (-0.95, 1.75, 0.1), (0.25, 0.45, 0.11), (0.95, 1.0, 0.12), (0.15, 1.9, 0.09)]):
        disc_patch(f"hs_stone_f{i}", pr, (px, -D / 2 - 0.005, pz), (90, 0, r.uniform(-20, 20)), parent=o, rng=r)
    for i, (py, pz, pr) in enumerate([(-0.5, 0.6, 0.12), (0.55, 1.65, 0.11), (0.1, 1.0, 0.09)]):
        disc_patch(f"hs_stone_r{i}", pr, (W / 2 + 0.005, py, pz), (90, 0, 90 + r.uniform(-20, 20)), parent=o, rng=r)

    # door
    box("hs_door_frame", (0.78, 0.1, 1.28), (-0.45, -D / 2 - 0.02, PLINTH), m="timber", parent=o, bevel=0.02)
    for i in range(3):
        box(f"hs_door_plank_{i}", (0.2, 0.08, 1.12), (-0.65 + i * 0.2, -D / 2 - 0.05, PLINTH), m="wooddark", parent=o, bevel=0.01)
    sphere("hs_door_knob", 0.04, (-0.28, -D / 2 - 0.11, PLINTH + 0.6), m="iron", parent=o, seg=8, rings=6)
    box("hs_doormat", (0.62, 0.36, 0.03), (-0.45, -D / 2 - 0.28, 0), m="mat", parent=o)
    box("hs_step", (0.86, 0.3, PLINTH), (-0.45, -D / 2 - 0.12, 0), m="cobble", parent=o, bevel=0.02)

    # front window with shutters and a flower box
    wx, wz = 0.5, 1.45
    box("hs_win_frame", (0.62, 0.08, 0.62), (wx, -D / 2 - 0.02, wz), m="timber", parent=o, bevel=0.015)
    box("hs_win_glass", (0.48, 0.06, 0.48), (wx, -D / 2 - 0.04, wz + 0.07), m="glass", parent=o)
    box("hs_win_mullion_v", (0.05, 0.05, 0.48), (wx, -D / 2 - 0.07, wz + 0.07), m="timber", parent=o)
    box("hs_win_mullion_h", (0.48, 0.05, 0.05), (wx, -D / 2 - 0.07, wz + 0.285), m="timber", parent=o)
    box("hs_shutter_l", (0.22, 0.05, 0.6), (wx - 0.44, -D / 2 - 0.05, wz + 0.01), rot=(0, 0, -8), m="wooddark", parent=o, bevel=0.01)
    box("hs_shutter_r", (0.22, 0.05, 0.6), (wx + 0.44, -D / 2 - 0.05, wz + 0.01), rot=(0, 0, 8), m="wooddark", parent=o, bevel=0.01)
    box("hs_flowerbox", (0.72, 0.22, 0.16), (wx, -D / 2 - 0.13, wz - 0.12), m="timber", parent=o, bevel=0.015)
    for i, fx in enumerate((-0.22, 0.0, 0.22)):
        cyl(f"hs_stem_{i}", 0.015, 0.22, (wx + fx, -D / 2 - 0.13, wz + 0.02), m="leafdark", parent=o, seg=5)
        sphere(f"hs_leaf_{i}", 0.07, (wx + fx + 0.04, -D / 2 - 0.13, wz + 0.1), m="leaf", parent=o, seg=8, rings=5, scale=(1.3, 1, 0.7))
        sphere(f"hs_flower_{i}", 0.065, (wx + fx, -D / 2 - 0.13, wz + 0.25), m="flower" if i != 1 else "flower2", parent=o, seg=8, rings=6)

    # side window
    box("hs_side_frame", (0.08, 0.5, 0.55), (W / 2 + 0.02, -0.2, 1.45), m="timber", parent=o, bevel=0.015)
    box("hs_side_glass", (0.06, 0.38, 0.42), (W / 2 + 0.04, -0.2, 1.5), m="glass", parent=o)
    box("hs_side_mullion", (0.05, 0.04, 0.42), (W / 2 + 0.07, -0.2, 1.5), m="timber", parent=o)

    # roof, chimney, pipe and lantern
    gable_planks("hs_roof", o, W, D, WALL_TOP, RIDGE, overhang=0.26, plank=0.33, rng=r)
    box("hs_chimney", (0.38, 0.38, 1.35), (0.7, 0.42, WALL_TOP + 0.05), m="cobble", parent=o, bevel=0.03)
    box("hs_chimney_cap", (0.5, 0.5, 0.1), (0.7, 0.42, WALL_TOP + 1.4), m="slate", parent=o, bevel=0.02)
    cyl("hs_pipe", 0.055, WALL_TOP - 0.1, (W / 2 + 0.12, 0.62, 0.1), m="iron", parent=o, seg=8)
    cyl("hs_pipe_elbow", 0.055, 0.25, (W / 2 + 0.12, 0.62, WALL_TOP), rot=(0, -90, 0), m="iron", parent=o, seg=8)
    for i, z in enumerate((0.6, 1.5)):
        box(f"hs_pipe_bracket_{i}", (0.16, 0.16, 0.05), (W / 2 + 0.1, 0.62, z), m="slate", parent=o)
    box("hs_lantern_arm", (0.05, 0.38, 0.05), (-0.98, -D / 2 - 0.19, 1.72), m="slate", parent=o)
    box("hs_lantern_body", (0.16, 0.16, 0.22), (-0.98, -D / 2 - 0.34, 1.45), m="lamp", parent=o, bevel=0.01)
    cyl("hs_lantern_top", 0.12, 0.1, (-0.98, -D / 2 - 0.34, 1.67), m="slate", parent=o, seg=4, r2=0.02)

    # potted plant by the door and a crate
    cyl("hs_pot", 0.17, 0.3, (-1.05, -D / 2 - 0.3, 0), m="pot", parent=o, seg=10, r2=0.2)
    sphere("hs_plant", 0.24, (-1.05, -D / 2 - 0.3, 0.48), m="leaf", parent=o, seg=10, rings=7, scale=(1, 1, 1.25))
    box("hs_crate", (0.4, 0.4, 0.38), (W / 2 + 0.35, -0.55, 0), rot=(0, 0, 12), m="timber", parent=o, bevel=0.02)
    box("hs_crate_band", (0.42, 0.42, 0.06), (W / 2 + 0.35, -0.55, 0.16), rot=(0, 0, 12), m="wooddark", parent=o)
    return o


def main():
    reset_scene()
    root = empty("town")
    build_ground(root)
    build_castle(root)
    build_landmarks(root)

    show_xy = polar(OUTER_R, SHOWCASE_ANGLE)
    showcase_house(root, show_xy, facing_out(SHOWCASE_ANGLE))

    outer_skip = [(LANDMARKS["stall"], 11), (LANDMARKS["smithy"], 11), (LANDMARKS["wizard"], 9), (LANDMARKS["guild"], 13),
                  (SHOWCASE_ANGLE, 8.5)]
    fill_ring(root, INNER_R, 1.8, 2.3, 2.9, [], "inner")
    fill_ring(root, OUTER_R, 2.0, 2.2, 3.0, outer_skip, "outer")

    os.makedirs(os.path.join(ROOT, "public", "models"), exist_ok=True)
    save_blend(os.path.join(ROOT, "art", "town.blend"))
    export_glb(os.path.join(ROOT, "public", "models", "town.glb"))


main()
