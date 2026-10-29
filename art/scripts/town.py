"""Builds the Castle Hill town: ground, hill, castle, landmarks and houses.

Run with:  blender -b -P art/scripts/town.py, then node art/optimize.mjs (npm run models does both).
Writes art/town.blend and art/build/town.raw.glb.

Empties named spot_<npc> mark where each NPC stands and smoke_<name> marks each
chimney; the site reads both.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(__file__))
from buildings import castle, guild_hall, house, market_stall, smithy, wizard_tower  # noqa: E402
from lib import box, cyl, empty, export_glb, reset_scene, save_blend, sphere, _finish  # noqa: E402

import bmesh  # noqa: E402
import bpy  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
rng = random.Random(42)

# Layout radii (units from the town centre)
TOWN_R = 12.0
HILL_PROFILE = [(4.6, 0.0), (4.25, 0.8), (3.6, 1.65), (2.9, 2.25), (2.4, 2.48), (0.0, 2.5)]
HILL_TOP = 2.5
INNER_R = 6.4     # centre line of the inner ring of houses
OUTER_R = 9.0     # centre line of the outer ring (houses + landmarks)
NPC_R = 10.7     # where landmark NPCs stand, in front of their doors
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
        box(f"wall_{i}", (1.18, 0.42, rng.uniform(0.26, 0.34)), (x, y, 0), rot=(0, 0, deg + 90 + rng.uniform(-3, 3)),
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


# --------------------------------------------------------------------------- buildings

def build_landmarks(root):
    lm = empty("landmarks", parent=root)
    castle(root, HILL_TOP)

    deg = LANDMARKS["stall"]
    market_stall("stall", lm, polar(OUTER_R + 0.55, deg), facing_out(deg))
    deg = LANDMARKS["smithy"]
    smithy("smithy", lm, polar(OUTER_R, deg), facing_out(deg))
    deg = LANDMARKS["wizard"]
    wizard_tower("wizard", lm, polar(OUTER_R + 0.15, deg), facing_out(deg))
    deg = LANDMARKS["guild"]
    guild_hall("guild", lm, polar(OUTER_R - 0.05, deg), facing_out(deg))

    for name, deg in LANDMARKS.items():
        npc = {"stall": "shopkeeper", "smithy": "blacksmith", "wizard": "wizard", "guild": "adventurer"}[name]
        empty(f"spot_{npc}", loc=(*polar(NPC_R, deg), 0), rot=(0, 0, facing_out(deg)), parent=root)


def fill_ring(root, r, depth, hmin, hmax, skip, prefix):
    """Pack houses tangentially around a ring, leaving gaps for streets and reserved arcs."""
    ring = empty(prefix, parent=root)
    circ = math.tau * r
    deg = rng.uniform(0, 4)
    i = 0
    while deg < 360:
        w = rng.uniform(1.6, 2.3)
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
            for k, (dx, dy, dz, s) in enumerate([(0, 0, 1.75, 0.75), (0.35, 0.1, 1.45, 0.5), (-0.3, -0.15, 1.5, 0.48)]):
                sphere(f"{prefix}_tree_{i}_crown_{k}", s, (dx, dy, dz), m="leaf" if k == 0 else "leafdark", parent=t, seg=12, rings=8)
        else:
            ridge = rng.uniform(hmin, hmax)
            house(f"{prefix}_h{i}", ring, (x, y), facing_out(centre) + rng.uniform(-4, 4), W=w - 0.1,
                  D=depth * rng.uniform(0.88, 1.0), wall_top=ridge - rng.uniform(0.75, 0.95), ridge=ridge,
                  seed=rng.randrange(1 << 30))
        deg += span + 0.6
        i += 1


def count_triangles():
    import bpy
    deps = bpy.context.evaluated_depsgraph_get()
    tris = 0
    for o in bpy.context.scene.objects:
        if o.type == "MESH":
            me = o.evaluated_get(deps).to_mesh()
            tris += sum(len(p.vertices) - 2 for p in me.polygons)
            o.evaluated_get(deps).to_mesh_clear()
    return tris


def main():
    reset_scene()
    root = empty("town")
    build_ground(root)
    build_landmarks(root)

    house("house_showcase", root, polar(OUTER_R, SHOWCASE_ANGLE), facing_out(SHOWCASE_ANGLE), roof="terra", chimney=True,
          door_along=-0.45, shutters="wooddark", blooms=["flower", "flower2", "flower"], showcase=True, seed=7)

    outer_skip = [(LANDMARKS["stall"], 11), (LANDMARKS["smithy"], 13), (LANDMARKS["wizard"], 11), (LANDMARKS["guild"], 14),
                  (SHOWCASE_ANGLE, 8.5)]
    fill_ring(root, INNER_R, 1.8, 2.6, 3.0, [], "inner")
    fill_ring(root, OUTER_R, 2.0, 2.65, 3.3, outer_skip, "outer")

    print(f"TRIANGLES {count_triangles()}  OBJECTS {len(bpy.data.objects)}")
    # the raw export is optimised into public/models/town.glb by art/optimize.mjs
    os.makedirs(os.path.join(ROOT, "art", "build"), exist_ok=True)
    save_blend(os.path.join(ROOT, "art", "town.blend"))
    export_glb(os.path.join(ROOT, "art", "build", "town.raw.glb"))


main()
