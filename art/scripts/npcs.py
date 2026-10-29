"""Builds the five chibi NPCs: shopkeeper, king, blacksmith, wizard and adventurer.

Run with:  blender -b -P art/scripts/npcs.py
Writes art/npc_<name>.blend and public/models/npc_<name>.glb for each.

Each NPC has a 2 second idle loop, exported as the glTF's only animation.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from chibi import LOOP, breathe, build_chibi, hold, key, keys, setup_timeline, smooth_all  # noqa: E402
from lib import box, cyl, empty, export_glb, reset_scene, save_blend, sphere  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
Q = LOOP // 4


def front_stripe(name, parent, m, z0=0.03, h=0.55, w=0.07):
    """A strip running up the front of a robe, leaning in with the robe's taper."""
    box(name, (w, 0.03, h), (0, -0.25, z0), rot=(-11, 0, 0), m=m, parent=parent, bevel=0.01)


# --------------------------------------------------------------------------- shopkeeper

def shopkeeper():
    c = build_chibi("npc_shopkeeper", shirt="shirt", belt="timber")
    b, h = c.body, c.head
    box("apron", (0.3, 0.035, 0.34), (0, -0.215, 0.2), rot=(-9, 0, 0), m="apron", parent=b, bevel=0.012)
    box("apron_pocket", (0.14, 0.02, 0.08), (0, -0.24, 0.27), rot=(-9, 0, 0), m="timber", parent=b)
    box("apron_strap_l", (0.04, 0.02, 0.24), (-0.09, -0.17, 0.48), rot=(-22, 0, 0), m="apron", parent=b)
    box("apron_strap_r", (0.04, 0.02, 0.24), (0.09, -0.17, 0.48), rot=(-22, 0, 0), m="apron", parent=b)
    for i, sx in enumerate((-1, 1)):
        sphere(f"moustache_{i}", 0.06, (sx * 0.055, -0.29, 0.2), rot=(0, sx * 20, 0), m="hair", parent=h, seg=10, rings=6, scale=(1.3, 0.6, 0.7))
    sphere("scarf", 0.315, (0, 0.005, 0.31), m="scarf", parent=h, seg=28, rings=18, cut_below=0.1, scale=(1.06, 1.02, 1.0))
    sphere("scarf_knot", 0.07, (0, 0.31, 0.38), m="scarf", parent=h, seg=10, rings=6)
    sphere("scarf_tail_0", 0.06, (-0.05, 0.33, 0.28), rot=(20, 0, 0), m="scarf", parent=h, seg=10, rings=6, scale=(0.8, 0.5, 1.5))
    sphere("scarf_tail_1", 0.06, (0.06, 0.33, 0.29), rot=(20, 0, 0), m="scarf", parent=h, seg=10, rings=6, scale=(0.8, 0.5, 1.5))

    breathe(c)
    keys(h, [(1, (0, 0, 0)), (1 + Q, (0, 6, 0)), (1 + 2 * Q, (0, 0, 0)), (1 + 3 * Q, (0, -6, 0)), (1 + LOOP, (0, 0, 0))])
    r, l = c.arms[1], c.arms[-1]
    keys(r, [(1, (0, -18, 0)), (1 + Q // 2, (-10, -60, 0)), (1 + Q, (-10, -80, 0)), (1 + Q + Q // 2, (-10, -60, 0)),
             (1 + 2 * Q, (0, -18, 0)), (1 + LOOP, (0, -18, 0))])
    keys(l, [(1, (0, 18, 0)), (1 + 2 * Q, (6, 18, 0)), (1 + LOOP, (0, 18, 0))])
    smooth_all(c.body, h, r, l)
    return c


# --------------------------------------------------------------------------- king

def king():
    c = build_chibi("npc_king", shirt="royal", robe="royal", brows="beard", shoes="wooddark")
    b, h = c.body, c.head
    cyl("robe_hem", 0.3, 0.07, (0, 0, 0.0), m="fur", parent=b, seg=18, smooth=True)
    front_stripe("robe_stripe", b, "fur")
    cyl("robe_belt", 0.235, 0.05, (0, 0, 0.33), m="gold", parent=b, seg=16, r2=0.225, smooth=True)
    sphere("collar", 0.21, (0, 0, 0.58), m="fur", parent=b, seg=18, rings=8, scale=(1, 1, 0.38))
    box("cape", (0.5, 0.04, 0.62), (0, 0.22, 0.0), rot=(11, 0, 0), m="cape", parent=b, bevel=0.015)
    for i, z in enumerate((0.18, 0.28, 0.42)):
        sphere(f"button_{i}", 0.022, (0, -0.27 + z * 0.19, z), m="gold", parent=b, seg=8, rings=6)

    # white hair, beard and crown
    sphere("hair", 0.312, (0, 0.01, 0.3), m="beard", parent=h, seg=28, rings=18, cut_below=0.06, scale=(1.06, 1.03, 1.0))
    sphere("beard", 0.17, (0, -0.19, 0.11), m="beard", parent=h, seg=16, rings=10, scale=(1.25, 0.7, 1.05))
    for i, sx in enumerate((-1, 1)):
        sphere(f"moustache_{i}", 0.055, (sx * 0.06, -0.295, 0.2), rot=(0, sx * 25, 0), m="beard", parent=h, seg=10, rings=6, scale=(1.4, 0.6, 0.7))
    cyl("crown_band", 0.19, 0.11, (0, 0.0, 0.53), m="gold", parent=h, seg=16, r2=0.2)
    for i in range(6):
        a = i / 6 * math.tau + math.pi / 2
        cyl(f"crown_point_{i}", 0.045, 0.1, (math.cos(a) * 0.17, math.sin(a) * 0.17, 0.64), m="gold", parent=h, seg=6, r2=0.0)
    sphere("crown_gem", 0.035, (0, -0.2, 0.585), m="cape", parent=h, seg=10, rings=6, scale=(1, 0.6, 1))

    # sceptre in the right hand
    grip = hold(c.arms[1], "sceptre_grip", 18)
    cyl("sceptre_rod", 0.024, 0.58, (0, 0, -0.18), m="gold", parent=grip, seg=8)
    sphere("sceptre_orb", 0.075, (0, 0, 0.44), m="cape", parent=grip, seg=14, rings=10)
    cyl("sceptre_collar", 0.05, 0.05, (0, 0, 0.36), m="gold", parent=grip, seg=10)

    breathe(c, amount=0.025, beats=1)
    keys(h, [(1, (0, 0, 0)), (1 + Q, (6, 4, 0)), (1 + 2 * Q, (0, 0, 0)), (1 + 3 * Q, (6, -4, 0)), (1 + LOOP, (0, 0, 0))])
    r, l = c.arms[1], c.arms[-1]
    keys(r, [(1, (-15, -18, 0)), (1 + 2 * Q, (-32, -22, 0)), (1 + LOOP, (-15, -18, 0))])
    keys(l, [(1, (-25, 30, 0)), (1 + 2 * Q, (-30, 34, 0)), (1 + LOOP, (-25, 30, 0))])
    smooth_all(c.body, h, r, l)
    return c


# --------------------------------------------------------------------------- blacksmith

def blacksmith():
    c = build_chibi("npc_blacksmith", shirt="slate", sleeves="skin", trousers="wooddark", shoes="hairdark",
                    brows="hairdark", bulk=1.2, belt="hairdark")
    b, h = c.body, c.head
    box("apron", (0.38, 0.035, 0.42), (0, -0.25, 0.14), rot=(-10, 0, 0), m="leather", parent=b, bevel=0.012)
    box("apron_strap_l", (0.05, 0.02, 0.24), (-0.1, -0.2, 0.47), rot=(-24, 0, 0), m="leather", parent=b)
    box("apron_strap_r", (0.05, 0.02, 0.24), (0.1, -0.2, 0.47), rot=(-24, 0, 0), m="leather", parent=b)
    box("apron_pocket", (0.16, 0.02, 0.09), (0, -0.28, 0.22), rot=(-10, 0, 0), m="hairdark", parent=b)

    # bald top, short dark hair at the sides, a big beard and goggles on the forehead
    for i, sx in enumerate((-1, 1)):
        sphere(f"hair_side_{i}", 0.13, (sx * 0.24, 0.07, 0.33), m="hairdark", parent=h, seg=12, rings=8, scale=(0.6, 1.1, 0.9))
        cyl(f"goggle_{i}", 0.075, 0.07, (sx * 0.095, -0.24, 0.46), rot=(-62, 0, 0), m="steel", parent=h, seg=12)
        cyl(f"goggle_lens_{i}", 0.055, 0.075, (sx * 0.095, -0.245, 0.462), rot=(-62, 0, 0), m="crystal", parent=h, seg=12)
    sphere("hair_back", 0.2, (0, 0.2, 0.28), m="hairdark", parent=h, seg=14, rings=10, scale=(1.3, 0.6, 0.9))
    cyl("goggle_strap", 0.292, 0.05, (0, 0.0, 0.45), rot=(-14, 0, 0), m="leather", parent=h, seg=24)
    sphere("beard", 0.2, (0, -0.19, 0.11), m="hairdark", parent=h, seg=16, rings=10, scale=(1.3, 0.72, 1.0))
    for i, sx in enumerate((-1, 1)):
        sphere(f"moustache_{i}", 0.06, (sx * 0.06, -0.3, 0.2), rot=(0, sx * 20, 0), m="hairdark", parent=h, seg=10, rings=6, scale=(1.4, 0.6, 0.7))

    # hammer in the right hand, pointing forward so the swing lands on the anvil
    grip = hold(c.arms[1], "hammer_hold", 18)
    g = empty("hammer_grip", rot=(120, 0, 0), parent=grip)
    cyl("hammer_handle", 0.024, 0.26, (0, 0, -0.06), m="timber", parent=g, seg=8)
    box("hammer_head", (0.1, 0.2, 0.1), (0, 0, 0.22), m="slate", parent=g, base=False, bevel=0.012)

    # anvil on a stump in front of him
    ax, ay = 0.36, -0.36
    cyl("stump", 0.13, 0.12, (ax, ay, 0), m="timber", parent=c.root, seg=10)
    box("anvil_waist", (0.1, 0.09, 0.07), (ax, ay, 0.12), m="slate", parent=c.root)
    box("anvil_top", (0.26, 0.13, 0.06), (ax, ay, 0.19), rot=(0, 0, -30), m="iron", parent=c.root, bevel=0.01)
    cyl("anvil_horn", 0.045, 0.1, (ax - 0.11, ay - 0.065, 0.22), rot=(0, -90, -30), m="iron", parent=c.root, seg=8, r2=0.0)

    breathe(c, amount=0.02, beats=1)
    r, l = c.arms[1], c.arms[-1]
    strike, raised = (-30, -18, 0), (-115, -18, 0)
    keys(r, [(1, strike), (7, raised), (13, strike), (19, raised), (25, strike), (37, (-20, -18, 0)), (1 + LOOP, strike)])
    keys(l, [(1, (-10, 18, 0)), (25, (-14, 20, 0)), (1 + LOOP, (-10, 18, 0))])
    keys(h, [(1, (8, 0, 0)), (13, (10, 0, 0)), (25, (8, 0, 0)), (37, (2, 0, 6)), (1 + LOOP, (8, 0, 0))])
    smooth_all(c.body, h, r, l)
    return c


# --------------------------------------------------------------------------- wizard

def wizard():
    c = build_chibi("npc_wizard", shirt="robe", robe="robe", brows="beard", shoes="robe2")
    b, h = c.body, c.head
    front_stripe("robe_stripe", b, "gold", w=0.05)
    cyl("robe_sash", 0.235, 0.05, (0, 0, 0.33), m="robe2", parent=b, seg=16, r2=0.225, smooth=True)

    # long white beard, side hair and the hat
    cyl("beard", 0.02, 0.5, (0, -0.2, -0.32), m="beard", parent=h, seg=12, r2=0.2, smooth=True)
    for i, sx in enumerate((-1, 1)):
        sphere(f"hair_side_{i}", 0.12, (sx * 0.25, 0.04, 0.24), m="beard", parent=h, seg=12, rings=8, scale=(0.6, 1.0, 1.2))
        sphere(f"moustache_{i}", 0.06, (sx * 0.06, -0.3, 0.2), rot=(0, sx * 25, 0), m="beard", parent=h, seg=10, rings=6, scale=(1.5, 0.6, 0.7))
    cyl("hat_brim", 0.44, 0.04, (0, 0, 0.46), m="robe2", parent=h, seg=24)
    cyl("hat_lower", 0.27, 0.26, (0, 0, 0.49), m="robe", parent=h, seg=18, r2=0.18)
    cyl("hat_band", 0.272, 0.06, (0, 0, 0.49), m="gold", parent=h, seg=18, r2=0.25)
    cyl("hat_mid", 0.18, 0.22, (0, 0.03, 0.74), rot=(14, 0, 0), m="robe", parent=h, seg=16, r2=0.09)
    cyl("hat_tip", 0.09, 0.2, (0, 0.1, 0.93), rot=(40, 0, 0), m="robe", parent=h, seg=12, r2=0.0)
    for i, (x, y, z) in enumerate([(-0.15, -0.17, 0.6), (0.12, -0.13, 0.7), (0.0, -0.06, 0.86)]):
        sphere(f"hat_star_{i}", 0.03, (x, y, z), m="gold", parent=h, seg=8, rings=6)

    # staff in the left hand, a floating crystal over the right
    grip = hold(c.arms[-1], "staff_grip", -18)
    cyl("staff", 0.028, 1.2, (0, 0, -0.42), m="timber", parent=grip, seg=8)
    cyl("staff_ring", 0.045, 0.05, (0, 0, 0.66), m="gold", parent=grip, seg=10)
    sphere("staff_crystal", 0.08, (0, 0, 0.82), m="crystal", parent=grip, seg=6, rings=4, scale=(1, 1, 1.6), smooth=False)
    orb = empty("orb", loc=(0.2, -0.32, 0.6), parent=c.root)
    sphere("orb_crystal", 0.07, (0, 0, 0), m="crystal", parent=orb, seg=6, rings=4, scale=(1, 1, 1.4), smooth=False)

    breathe(c, amount=0.025, beats=1)
    keys(h, [(1, (0, 0, 0)), (1 + Q, (4, 5, 0)), (1 + 2 * Q, (0, 0, 0)), (1 + 3 * Q, (4, -5, 0)), (1 + LOOP, (0, 0, 0))])
    r, l = c.arms[1], c.arms[-1]
    keys(r, [(1, (-55, -15, 0)), (1 + 2 * Q, (-62, -12, 0)), (1 + LOOP, (-55, -15, 0))])
    keys(l, [(1, (-12, 18, 0)), (1 + 2 * Q, (-14, 18, 0)), (1 + LOOP, (-12, 18, 0))])
    for f, z, spin in [(1, 0.58, 0), (1 + 2 * Q, 0.66, 180), (1 + LOOP, 0.58, 360)]:
        key(orb, f, loc=(0.2, -0.33, z), rot=(0, 0, spin))
    smooth_all(c.body, h, r, l, orb)
    # the orb spins at a steady rate so the loop has no hitch
    for fc in orb.animation_data.action.fcurves:
        if fc.data_path == "rotation_euler":
            for kp in fc.keyframe_points:
                kp.interpolation = "LINEAR"
    return c


# --------------------------------------------------------------------------- adventurer

def adventurer():
    c = build_chibi("npc_adventurer", shirt="tunic", trousers="leather", shoes="hairdark", brows="hairred", belt="leather")
    b, h = c.body, c.head
    box("belt_pouch", (0.1, 0.06, 0.09), (0.15, -0.2, 0.28), rot=(0, 0, 25), m="leather", parent=b, bevel=0.01)
    sphere("belt_buckle", 0.03, (0, -0.24, 0.36), m="gold", parent=b, seg=8, rings=6, scale=(1, 0.5, 1))
    box("cape", (0.42, 0.035, 0.42), (0, 0.2, 0.15), rot=(12, 0, 0), m="cape", parent=b, bevel=0.012)
    sphere("cape_clasp_l", 0.035, (-0.12, -0.12, 0.56), m="gold", parent=b, seg=8, rings=6)
    sphere("cape_clasp_r", 0.035, (0.12, -0.12, 0.56), m="gold", parent=b, seg=8, rings=6)

    # sword across the back
    s = empty("sword", loc=(0, 0.25, 0.38), rot=(10, 35, 0), parent=b)
    box("sword_blade", (0.06, 0.018, 0.52), (0, 0, -0.2), m="steel", parent=s, bevel=0.005)
    box("sword_guard", (0.2, 0.04, 0.035), (0, 0, 0.32), m="gold", parent=s)
    cyl("sword_grip", 0.022, 0.12, (0, 0, 0.34), m="leather", parent=s, seg=8)
    sphere("sword_pommel", 0.035, (0, 0, 0.47), m="gold", parent=s, seg=8, rings=6)

    # spiky hair and a headband
    sphere("hair", 0.315, (0, 0.01, 0.31), m="hairred", parent=h, seg=28, rings=18, cut_below=0.06, scale=(1.06, 1.03, 1.0))
    for i in range(7):
        a = i / 7 * math.tau
        x, y = math.cos(a) * 0.17, math.sin(a) * 0.17 + 0.03
        tilt_x, tilt_y = -math.sin(a) * 40, math.cos(a) * 40
        cyl(f"spike_{i}", 0.08, 0.2, (x, y, 0.5), rot=(tilt_x, tilt_y, 0), m="hairred", parent=h, seg=6, r2=0.0)
    cyl("spike_top", 0.09, 0.22, (0, 0.04, 0.55), rot=(15, 0, 0), m="hairred", parent=h, seg=6, r2=0.0)
    for i, sx in enumerate((-1, 0, 1)):
        cyl(f"fringe_{i}", 0.06, 0.14, (sx * 0.1, -0.24, 0.48), rot=(160, sx * 15, 0), m="hairred", parent=h, seg=6, r2=0.0)
    cyl("headband", 0.302, 0.05, (0, 0, 0.4), rot=(-6, 0, 0), m="cape", parent=h, seg=24)
    sphere("headband_tail_0", 0.05, (-0.05, 0.33, 0.37), rot=(25, 0, 10), m="cape", parent=h, seg=10, rings=6, scale=(0.7, 0.5, 1.8))
    sphere("headband_tail_1", 0.05, (0.06, 0.34, 0.35), rot=(30, 0, -10), m="cape", parent=h, seg=10, rings=6, scale=(0.7, 0.5, 1.8))

    breathe(c)
    r, l = c.arms[1], c.arms[-1]
    # a big welcoming wave, then back to hands at the sides
    keys(r, [(1, (0, -18, 0)), (7, (0, -150, 0)), (11, (12, -140, 0)), (15, (-12, -150, 0)), (19, (12, -140, 0)),
             (23, (-12, -150, 0)), (31, (0, -18, 0)), (1 + LOOP, (0, -18, 0))])
    keys(l, [(1, (0, 35, 0)), (1 + 2 * Q, (4, 38, 0)), (1 + LOOP, (0, 35, 0))])
    keys(h, [(1, (0, 0, 0)), (11, (0, 8, 4)), (23, (0, 8, -4)), (31, (0, 0, 0)), (1 + LOOP, (0, 0, 0))])
    smooth_all(c.body, h, r, l)
    return c


NPCS = {"shopkeeper": shopkeeper, "king": king, "blacksmith": blacksmith, "wizard": wizard, "adventurer": adventurer}


def main():
    only = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else list(NPCS)
    os.makedirs(os.path.join(ROOT, "public", "models"), exist_ok=True)
    for name in only:
        reset_scene()
        setup_timeline()
        NPCS[name]()
        save_blend(os.path.join(ROOT, "art", f"npc_{name}.blend"))
        export_glb(os.path.join(ROOT, "public", "models", f"npc_{name}.glb"), animations=True)


main()
