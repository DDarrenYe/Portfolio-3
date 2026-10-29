"""Finished buildings in the approved style: a configurable house and the five landmarks.

Every builder takes a parent empty and works in local space: origin at the ground
centre, front facing -Y. Details sit on the walls through `anchor()`, which puts an
empty on a wall face with its -Y pointing outward, so doors and windows are written
once and work on any face.
"""
import math
import random

from lib import beam, box, cyl, disc_patch, empty, gable_fill, gable_planks, prism, sphere

ROOFS = {"terra": ("roof", "roof2"), "slate": ("slate", "slate2")}
PLINTH = 0.25


def anchor(o, name, W, D, face, along=0.0, z=0.0):
    """Empty on a wall face, -Y pointing out of the wall. `along` runs left to right as seen from outside."""
    if face == "front":
        return empty(name, loc=(along, -D / 2, z), parent=o)
    if face == "back":
        return empty(name, loc=(-along, D / 2, z), rot=(0, 0, 180), parent=o)
    if face == "right":
        return empty(name, loc=(W / 2, along, z), rot=(0, 0, 90), parent=o)
    return empty(name, loc=(-W / 2, -along, z), rot=(0, 0, -90), parent=o)


# --------------------------------------------------------------------------- wall details

def door(a, name, w=0.6, h=1.05, frame="timber", leaf="wooddark", knob_side=1, mat=True):
    box(f"{name}_frame", (w + 0.18, 0.1, h + 0.23), (0, -0.02, 0), m=frame, parent=a, bevel=0.02)
    n = 3 if w < 0.8 else 4
    pw = w / n
    for i in range(n):
        box(f"{name}_plank_{i}", (pw, 0.08, h + 0.07), (-w / 2 + pw * (i + 0.5), -0.05, 0), m=leaf, parent=a, bevel=0.01)
    sphere(f"{name}_knob", 0.04, (knob_side * (w / 2 - 0.12), -0.11, h * 0.55), m="iron", parent=a, seg=8, rings=6)
    if mat:
        box(f"{name}_mat", (w + 0.02, 0.36, 0.03), (0, -0.28, -PLINTH), m="mat", parent=a)
        box(f"{name}_step", (w + 0.26, 0.3, PLINTH), (0, -0.12, -PLINTH), m="cobble", parent=a, bevel=0.02)


def window(a, name, w=0.62, h=0.62, shutters=None, flowers=None, lit=False, rng=None, arched=False):
    rng = rng or random
    box(f"{name}_frame", (w, 0.08, h), (0, -0.02, 0), m="timber", parent=a, bevel=0.015)
    box(f"{name}_glass", (w - 0.14, 0.06, h - 0.14), (0, -0.04, 0.07), m="lamp" if lit else "glass", parent=a)
    box(f"{name}_mullion_v", (0.05, 0.05, h - 0.14), (0, -0.07, 0.07), m="timber", parent=a)
    box(f"{name}_mullion_h", (w - 0.14, 0.05, 0.05), (0, -0.07, h / 2 - 0.025), m="timber", parent=a)
    if arched:
        cyl(f"{name}_arch", w / 2, 0.08, (0, 0.02, h), rot=(90, 0, 0), m="timber", parent=a, seg=12)
        cyl(f"{name}_arch_glass", w / 2 - 0.07, 0.1, (0, 0.0, h), rot=(90, 0, 0), m="lamp" if lit else "glass", parent=a, seg=12)
    if shutters:
        box(f"{name}_shutter_l", (w * 0.36, 0.05, h - 0.02), (-w * 0.71, -0.05, 0.01), rot=(0, 0, -8), m=shutters, parent=a, bevel=0.01)
        box(f"{name}_shutter_r", (w * 0.36, 0.05, h - 0.02), (w * 0.71, -0.05, 0.01), rot=(0, 0, 8), m=shutters, parent=a, bevel=0.01)
    if flowers:
        box(f"{name}_box", (w + 0.1, 0.22, 0.16), (0, -0.13, -0.12), m="timber", parent=a, bevel=0.015)
        for i, fx in enumerate((-0.22, 0.0, 0.22)):
            fx *= w / 0.62
            cyl(f"{name}_stem_{i}", 0.015, 0.22, (fx, -0.13, 0.02), m="leafdark", parent=a, seg=5)
            sphere(f"{name}_leaf_{i}", 0.07, (fx + 0.04, -0.13, 0.1), m="leaf", parent=a, seg=8, rings=5, scale=(1.3, 1, 0.7))
            sphere(f"{name}_flower_{i}", 0.065, (fx, -0.13, 0.25), m=flowers[i % len(flowers)], parent=a, seg=8, rings=6)


def stones(a, name, spots, rng):
    for i, (x, z, r) in enumerate(spots):
        disc_patch(f"{name}_{i}", r, (x, 0.005, z), (90, 0, rng.uniform(-20, 20)), parent=a, rng=rng)


def lantern(a, name, x, z):
    box(f"{name}_arm", (0.05, 0.38, 0.05), (x, -0.19, z + 0.27), m="slate", parent=a)
    box(f"{name}_body", (0.16, 0.16, 0.22), (x, -0.34, z), m="lamp", parent=a, bevel=0.01)
    cyl(f"{name}_top", 0.12, 0.1, (x, -0.34, z + 0.22), m="slate", parent=a, seg=4, r2=0.02)


def hanging_sign(a, name, x, z, icon):
    """A board hung from a bracket, with a simple painted-on icon for the shop's trade."""
    box(f"{name}_arm", (0.05, 0.7, 0.05), (x, -0.35, z + 0.5), m="slate", parent=a)
    for i, dy in enumerate((-0.2, -0.55)):
        box(f"{name}_chain_{i}", (0.02, 0.02, 0.1), (x, dy, z + 0.4), m="iron", parent=a)
    s = empty(f"{name}_board", loc=(x, -0.38, z - 0.05), rot=(0, 0, 90), parent=a)
    box(f"{name}_wood", (0.55, 0.06, 0.42), m="timber", parent=s, bevel=0.015)
    icon(s, name)


def potted_plant(o, name, x, y, rng):
    cyl(f"{name}_pot", 0.17, 0.3, (x, y, 0), m="pot", parent=o, seg=10, r2=0.2)
    sphere(f"{name}_leaves", 0.24, (x, y, 0.48), m="leaf" if rng.random() < 0.6 else "leafdark", parent=o, seg=10, rings=7, scale=(1, 1, 1.25))


def crate(o, name, x, y, rot, size=0.4, z=0.0):
    box(f"{name}", (size, size, size * 0.95), (x, y, z), rot=(0, 0, rot), m="timber", parent=o, bevel=0.02)
    box(f"{name}_band", (size + 0.02, size + 0.02, 0.06), (x, y, z + size * 0.4), rot=(0, 0, rot), m="wooddark", parent=o)


def barrel(o, name, x, y, h=0.55, r=0.22):
    cyl(f"{name}", r, h, (x, y, 0), m="timber", parent=o, seg=12, smooth=True)
    for i, z in enumerate((0.1, h - 0.16)):
        cyl(f"{name}_hoop_{i}", r + 0.012, 0.05, (x, y, z), m="slate", parent=o, seg=12)


# --------------------------------------------------------------------------- house

def house(name, parent, loc, rot_z, W=2.3, D=2.0, wall_top=2.15, ridge=3.05, seed=0, roof=None,
          chimney=None, door_along=None, flowers=True, props=True, showcase=False, shutters=None, blooms=None):
    """A finished house. Leave the options as None and the seed picks a variation."""
    r = random.Random(seed)
    o = empty(name, loc=(*loc, 0), rot=(0, 0, rot_z), parent=parent)
    roof = roof or ("terra" if r.random() < 0.6 else "slate")
    chimney = (r.random() < 0.7) if chimney is None else chimney
    if door_along is None:
        door_along = -W * 0.2 if r.random() < 0.5 else W * 0.2
    shutters = shutters or r.choice(["wooddark", "wooddark", "slate", "banner", "pot"])
    if flowers and not blooms:
        blooms = [r.choice(["flower", "flower2", "lamp"]) for _ in range(3)]
    if not flowers:
        blooms = None
    win_z = min(1.45, wall_top - 0.78)  # keep windows under the eaves on short houses
    two_storey = wall_top > 2.7

    box(f"{name}_plinth", (W + 0.14, D + 0.14, PLINTH), m="stonedark", parent=o, bevel=0.04)
    box(f"{name}_walls", (W, D, wall_top - PLINTH), (0, 0, PLINTH), m="plaster", parent=o, bevel=0.03)
    gable_fill(f"{name}_gable", o, W - 0.02, D, wall_top, ridge - 0.12, m="plaster")
    for i, (sx, sy) in enumerate([(-1, -1), (1, -1), (-1, 1), (1, 1)]):
        box(f"{name}_post_{i}", (0.15, 0.15, wall_top - PLINTH), (sx * W / 2, sy * D / 2, PLINTH), m="timber", parent=o, bevel=0.02)
    band_z = 1.3 if not two_storey else wall_top * 0.52
    box(f"{name}_band_f", (W + 0.08, 0.1, 0.12), (0, -D / 2 - 0.02, band_z), m="timber", parent=o, bevel=0.015)
    box(f"{name}_band_b", (W + 0.08, 0.1, 0.12), (0, D / 2 + 0.02, band_z), m="timber", parent=o, bevel=0.015)
    box(f"{name}_band_r", (0.1, D + 0.08, 0.12), (W / 2 + 0.02, 0, band_z), m="timber", parent=o, bevel=0.015)
    box(f"{name}_band_l", (0.1, D + 0.08, 0.12), (-W / 2 - 0.02, 0, band_z), m="timber", parent=o, bevel=0.015)

    # front: door and a window on the other side
    f = anchor(o, f"{name}_front", W, D, "front")
    stones(f, f"{name}_sf", [(-W * 0.37, 0.55, 0.13), (-W * 0.41, wall_top - 0.4, 0.1), (W * 0.1, 0.45, 0.11),
                             (W * 0.41, 1.0, 0.12), (W * 0.06, wall_top - 0.3, 0.09)], r)
    d = empty(f"{name}_door", loc=(door_along, 0, PLINTH), parent=f)
    door(d, f"{name}_door", knob_side=1 if door_along < 0 else -1)
    win_x = -door_along * 1.1
    window(empty(f"{name}_wf", loc=(win_x, 0, win_z if not two_storey else 1.0), parent=f), f"{name}_wf",
           shutters=shutters, flowers=blooms, rng=r)
    if two_storey:
        for i, x in enumerate((-W * 0.25, W * 0.25)):
            window(empty(f"{name}_wu{i}", loc=(x, 0, wall_top - 0.95), parent=f), f"{name}_wu{i}", w=0.5, h=0.55,
                   shutters=shutters if i else None, lit=r.random() < 0.3, rng=r)
    if props:
        lantern(f, f"{name}_lantern", door_along - (0.53 if door_along < 0 else -0.53), min(1.45, wall_top - 0.7))

    # sides and back so the house holds up from every angle as the town turns
    for face in ("right", "left"):
        a = anchor(o, f"{name}_{face}", W, D, face)
        stones(a, f"{name}_s{face}", [(-D * 0.25, 0.6, 0.12), (D * 0.27, 1.65, 0.11), (0.05, 1.0, 0.09)], r)
        if r.random() < 0.7:
            window(empty(f"{name}_w{face}", loc=(r.uniform(-0.2, 0.2) * D, 0, win_z), parent=a), f"{name}_w{face}",
                   w=0.5, h=0.55, lit=r.random() < 0.25, rng=r)
    b = anchor(o, f"{name}_back", W, D, "back")
    stones(b, f"{name}_sb", [(-W * 0.3, 0.7, 0.12), (W * 0.33, 1.5, 0.1)], r)
    window(empty(f"{name}_wb", loc=(r.uniform(-0.25, 0.25) * W, 0, win_z), parent=b), f"{name}_wb",
           shutters=shutters if r.random() < 0.5 else None, flowers=blooms if r.random() < 0.4 else None,
           lit=r.random() < 0.3, rng=r)

    gable_planks(f"{name}_roof", o, W, D, wall_top, ridge, overhang=0.26, plank=0.33, colors=ROOFS[roof], rng=r)
    if roof == "slate":
        # rivets along the bottom of a slate roof, like the reference's riveted panels
        half = D / 2 + 0.26
        for side in (-1, 1):
            for i in range(int((W + 0.4) / 0.33)):
                x = -W / 2 - 0.1 + i * 0.33 + 0.16
                box(f"{name}_rivet_{side}_{i}", (0.06, 0.06, 0.04), (x, side * (half - 0.12), wall_top + 0.12),
                    rot=(-side * 33, 0, 0), m="iron", parent=o)
    if chimney:
        cx = r.choice([-1, 1]) * W * 0.28
        cy = D * 0.2
        box(f"{name}_chimney", (0.38, 0.38, ridge - wall_top + 0.45), (cx, cy, wall_top + 0.05), m="cobble", parent=o, bevel=0.03)
        box(f"{name}_chimney_cap", (0.5, 0.5, 0.1), (cx, cy, ridge + 0.5), m="slate", parent=o, bevel=0.02)
        empty(f"smoke_{name}", loc=(cx, cy, ridge + 0.65), parent=o)

    if props:
        side = 1 if door_along < 0 else -1
        if showcase or r.random() < 0.6:
            cyl(f"{name}_pipe", 0.055, wall_top - 0.1, (side * (W / 2 + 0.12), D * 0.3, 0.1), m="iron", parent=o, seg=8)
            cyl(f"{name}_pipe_elbow", 0.055, 0.25, (side * (W / 2 + 0.12), D * 0.3, wall_top), rot=(0, -90 * side, 0), m="iron", parent=o, seg=8)
            for i, z in enumerate((0.6, 1.5)):
                box(f"{name}_pipe_bracket_{i}", (0.16, 0.16, 0.05), (side * (W / 2 + 0.1), D * 0.3, z), m="slate", parent=o)
        potted_plant(o, f"{name}_plant", door_along - side * 0.6, -D / 2 - 0.3, r)
        pick = r.random()
        if showcase or pick < 0.4:
            crate(o, f"{name}_crate", side * (W / 2 + 0.35), -D * 0.27, r.uniform(-15, 15))
        elif pick < 0.7:
            barrel(o, f"{name}_barrel", side * (W / 2 + 0.3), -D * 0.25)
    return o


# --------------------------------------------------------------------------- landmarks

def castle(parent, z):
    c = empty("castle", loc=(0, 0, z), parent=parent)
    r = random.Random(11)
    K, KH = 2.6, 3.0  # keep width and wall height
    box("castle_base", (3.5, 3.5, 0.45), m="stonedark", parent=c, bevel=0.06)
    for i in range(3):
        box(f"castle_step_{i}", (1.3, 0.3, 0.15 * (3 - i)), (0, -1.75 - 0.3 * i - 0.15, 0), m="cobble", parent=c, bevel=0.02)
    box("castle_keep", (K, K, KH), (0, 0, 0.45), m="plaster", parent=c, bevel=0.04)
    # stone quoins up the corners
    for i, (sx, sy) in enumerate([(-1, -1), (1, -1), (-1, 1), (1, 1)]):
        for j in range(5):
            w = 0.36 if j % 2 else 0.24
            box(f"castle_quoin_{i}_{j}", (w, w, 0.28), (sx * (K / 2 - w / 2 + 0.03), sy * (K / 2 - w / 2 + 0.03), 0.6 + j * 0.52),
                m="cobble", parent=c, bevel=0.02)
    # battlements around the top of the keep
    top = 0.45 + KH
    for side in range(4):
        rot = side * 90
        for j in range(5):
            along = -K / 2 + 0.2 + j * (K - 0.4) / 4
            x, y = (along, -K / 2) if side == 0 else (K / 2, along) if side == 1 else (-along, K / 2) if side == 2 else (-K / 2, -along)
            box(f"castle_merlon_{side}_{j}", (0.3, 0.22, 0.3), (x, y, top), rot=(0, 0, rot), m="plaster", parent=c, bevel=0.02)
    box("castle_parapet", (K + 0.1, K + 0.1, 0.12), (0, 0, top - 0.06), m="cobble", parent=c, bevel=0.02)

    # central upper tower rising out of the keep, then the spire
    U, UH = 1.5, 1.35
    box("castle_upper", (U, U, UH), (0, 0, top - 0.1), m="plaster", parent=c, bevel=0.03)
    box("castle_upper_band", (U + 0.1, U + 0.1, 0.12), (0, 0, top + UH - 0.22), m="cobble", parent=c, bevel=0.02)
    for face in ("front", "right", "left", "back"):
        a = anchor(c, f"castle_upper_{face}", U, U, face, 0, top + 0.25)
        window(empty(f"castle_upper_win_{face}", loc=(0, 0, 0), parent=a), f"castle_upper_win_{face}", w=0.42, h=0.42,
               lit=face in ("front", "back"), arched=True, rng=r)
    st = top - 0.1 + UH
    cyl("castle_spire", 1.22, 1.55, (0, 0, st), rot=(0, 0, 45), m="slate", parent=c, seg=4, r2=0.0)
    for i in range(4):
        a = math.radians(45 + i * 90)
        beam(f"castle_spire_rib_{i}", (math.cos(a) * 1.24, math.sin(a) * 1.24, st - 0.02), (0, 0, st + 1.55), 0.08, m="gold", parent=c)
    sphere("castle_finial", 0.12, (0, 0, st + 1.57), m="gold", parent=c, seg=10, rings=8)
    cyl("castle_flagpole", 0.03, 0.8, (0, 0, st + 1.65), m="timber", parent=c, seg=6)
    prism("castle_flag", [(0, 0), (0.55, 0.13), (0, 0.3)], 0.03, (0, 0, st + 2.1), m="banner", parent=c, axis="y")

    # corner towers
    for i, (sx, sy) in enumerate([(-1, -1), (1, -1), (-1, 1), (1, 1)]):
        tx, ty = sx * 1.45, sy * 1.45
        cyl(f"castle_tower_{i}", 0.52, 3.0, (tx, ty, 0.45), m="plaster", parent=c, seg=14)
        cyl(f"castle_tower_{i}_band", 0.55, 0.14, (tx, ty, 1.9), m="cobble", parent=c, seg=14)
        cyl(f"castle_tower_{i}_lip", 0.6, 0.14, (tx, ty, 3.4), m="cobble", parent=c, seg=14)
        cyl(f"castle_tower_{i}_roof", 0.68, 1.05, (tx, ty, 3.52), m="roof", parent=c, seg=14, r2=0.0)
        sphere(f"castle_tower_{i}_finial", 0.06, (tx, ty, 4.6), m="gold", parent=c, seg=8, rings=6)
        ang = math.degrees(math.atan2(ty, tx)) + 90
        a = empty(f"castle_tower_{i}_win", loc=(tx + sx * 0.36, ty + sy * 0.36, 2.35), rot=(0, 0, ang), parent=c)
        box(f"castle_tower_{i}_slit", (0.16, 0.12, 0.42), m="glass", parent=a)

    # gate, banners and windows on the front of the keep
    g = anchor(c, "castle_gate", K, K, "front", 0, 0.45)
    box("castle_gate_frame", (1.2, 0.14, 1.45), (0, -0.03, 0), m="cobble", parent=g, bevel=0.03)
    cyl("castle_gate_arch", 0.6, 0.14, (0, 0.04, 1.45), rot=(90, 0, 0), m="cobble", parent=g, seg=14)
    box("castle_gate_door", (0.9, 0.1, 1.4), (0, -0.07, 0), m="wooddark", parent=g, bevel=0.01)
    cyl("castle_gate_door_top", 0.45, 0.1, (0, 0.03, 1.4), rot=(90, 0, 0), m="wooddark", parent=g, seg=14)
    for j, zz in enumerate((0.35, 0.95)):
        box(f"castle_gate_band_{j}", (0.92, 0.04, 0.07), (0, -0.13, zz), m="iron", parent=g)
    for j, sx in enumerate((-1, 1)):
        box(f"castle_banner_{j}", (0.42, 0.04, 1.0), (sx * 0.95, -0.03, 1.45), m="banner", parent=g)
        prism(f"castle_banner_tip_{j}", [(-0.21, 0), (0.21, 0), (0, -0.22)], 0.04, (sx * 0.95, -0.03, 1.45), m="banner", parent=g, axis="y")
        box(f"castle_banner_rod_{j}", (0.52, 0.06, 0.06), (sx * 0.95, -0.06, 2.45), m="gold", parent=g)
        sphere(f"castle_banner_emblem_{j}", 0.09, (sx * 0.95, -0.06, 1.95), m="gold", parent=g, seg=10, rings=6, scale=(1, 0.4, 1))
        lantern(g, f"castle_lantern_{j}", sx * 0.62, 1.15)
    window(empty("castle_win_f", loc=(0, 0, 2.15), parent=g), "castle_win_f", w=0.5, h=0.45, lit=True, arched=True, rng=r)
    for face in ("right", "left", "back"):
        a = anchor(c, f"castle_{face}", K, K, face, 0, 0.45)
        for j, x in enumerate((-0.55, 0.55)):
            window(empty(f"castle_win_{face}_{j}", loc=(x, 0, 1.7), parent=a), f"castle_win_{face}_{j}", w=0.46, h=0.5,
                   lit=r.random() < 0.5, arched=True, rng=r)
        stones(a, f"castle_stone_{face}", [(-0.9, 0.8, 0.14), (0.2, 1.2, 0.12), (0.8, 2.6, 0.12), (-0.4, 2.75, 0.1)], r)
    stones(g, "castle_stone_front", [(-0.85, 2.7, 0.13), (0.7, 2.8, 0.11)], r)
    empty("spot_king", loc=(0, -2.15, 0.0), parent=c)

    return c


def market_stall(name, parent, loc, rot_z):
    o = empty(name, loc=(*loc, 0), rot=(0, 0, rot_z), parent=parent)
    r = random.Random(5)
    W, D = 2.4, 1.0
    # counter with a plank front
    box(f"{name}_counter", (W, D, 0.88), (0, 0, 0), m="timber", parent=o, bevel=0.02)
    for i in range(8):
        box(f"{name}_board_{i}", (W / 8 - 0.02, 0.05, 0.8), (-W / 2 + W / 8 * (i + 0.5), -D / 2 - 0.02, 0.04),
            m="wooddark" if i % 2 else "timber", parent=o, bevel=0.008)
    box(f"{name}_top", (W + 0.16, D + 0.12, 0.08), (0, 0, 0.88), m="leather", parent=o, bevel=0.015)
    # posts and a striped, scalloped awning
    for i, (sx, sy) in enumerate([(-1, -1), (1, -1), (-1, 1), (1, 1)]):
        box(f"{name}_post_{i}", (0.12, 0.12, 2.15 if sy < 0 else 2.45), (sx * (W / 2 + 0.02), sy * (D / 2 - 0.05), 0), m="timber", parent=o, bevel=0.015)
    n = 8
    pw = (W + 0.5) / n
    for i in range(n):
        x = -(W + 0.5) / 2 + pw * (i + 0.5)
        col = "awning" if i % 2 == 0 else "awning2"
        box(f"{name}_awning_{i}", (pw, 1.55, 0.05), (x, -0.05, 2.32), rot=(-11, 0, r.uniform(-1, 1)), m=col, parent=o, base=False)
        prism(f"{name}_scallop_{i}", [(-pw / 2, 0), (pw / 2, 0), (0, -0.18)], 0.04, (x, -0.82, 2.17), m=col, parent=o, axis="y")
    # patches stitched onto the awning, like the reference
    box(f"{name}_patch_0", (0.38, 0.32, 0.02), (-0.6, -0.1, 2.36), rot=(-11, 0, 8), m="robe2", parent=o, base=False)
    box(f"{name}_patch_1", (0.3, 0.26, 0.02), (0.75, 0.25, 2.43), rot=(-11, 0, -6), m="pot", parent=o, base=False)

    # wares on the counter: apples, bread, jars and potions
    t = 0.96
    for i in range(7):
        sphere(f"{name}_apple_{i}", 0.075, (-0.85 + (i % 4) * 0.13, -0.12 + (i // 4) * 0.14, t + 0.06), m="cape", parent=o, seg=10, rings=7)
    box(f"{name}_basket", (0.62, 0.36, 0.08), (-0.66, -0.06, t - 0.02), m="leather", parent=o, bevel=0.02)
    for i in range(3):
        sphere(f"{name}_bread_{i}", 0.1, (-0.05 + i * 0.2, 0.05, t + 0.06), rot=(0, 0, 20 * i), m="bread", parent=o, seg=10, rings=6, scale=(1.6, 0.9, 0.7))
    for i, col in enumerate(("crystal", "flower", "lamp", "tunic")):
        x = 0.55 + i * 0.16
        cyl(f"{name}_potion_{i}", 0.06, 0.14, (x, -0.1, t), m=col, parent=o, seg=8, smooth=True)
        cyl(f"{name}_potion_neck_{i}", 0.025, 0.08, (x, -0.1, t + 0.14), m=col, parent=o, seg=6)
        cyl(f"{name}_potion_cork_{i}", 0.03, 0.04, (x, -0.1, t + 0.22), m="timber", parent=o, seg=6)
    for i in range(2):
        cyl(f"{name}_jar_{i}", 0.09, 0.22, (0.75 + i * 0.22, 0.25, t), m="pot", parent=o, seg=10, smooth=True)
        cyl(f"{name}_jar_lid_{i}", 0.095, 0.04, (0.75 + i * 0.22, 0.25, t + 0.22), m="wooddark", parent=o, seg=10)
    # sign on the awning with a gold coin
    box(f"{name}_sign", (0.9, 0.08, 0.42), (0, 0.55, 2.55), m="timber", parent=o, bevel=0.02)
    cyl(f"{name}_sign_coin", 0.15, 0.04, (0, 0.5, 2.76), rot=(90, 0, 0), m="gold", parent=o, seg=14)
    # crates, sacks and a barrel around it
    crate(o, f"{name}_crate_0", -W / 2 - 0.45, -0.1, 12)
    crate(o, f"{name}_crate_1", -W / 2 - 0.42, -0.08, -6, size=0.3, z=0.38)
    barrel(o, f"{name}_barrel", W / 2 + 0.4, 0.1)
    sphere(f"{name}_sack", 0.24, (W / 2 + 0.38, -0.45, 0.2), m="bread", parent=o, seg=10, rings=7, scale=(1, 0.9, 0.85))
    cyl(f"{name}_sack_tie", 0.07, 0.12, (W / 2 + 0.38, -0.45, 0.38), m="leather", parent=o, seg=6)
    return o


def smithy(name, parent, loc, rot_z):
    o = empty(name, loc=(*loc, 0), rot=(0, 0, rot_z), parent=parent)
    r = random.Random(17)
    W, D = 2.8, 2.4
    house(f"{name}_house", o, (0.25, 0.1), 0, W=W, D=D, wall_top=2.45, ridge=3.5, roof="terra", chimney=False,
          door_along=0.55, flowers=False, props=False, seed=17)
    # tall stone forge chimney with a glowing top
    cx, cy = -0.75, 0.6
    box(f"{name}_chimney", (0.62, 0.62, 3.75), (cx, cy, 0), m="cobble", parent=o, bevel=0.04)
    box(f"{name}_chimney_band", (0.7, 0.7, 0.12), (cx, cy, 2.6), m="stonedark", parent=o, bevel=0.02)
    box(f"{name}_chimney_cap", (0.76, 0.76, 0.14), (cx, cy, 3.75), m="slate", parent=o, bevel=0.02)
    box(f"{name}_chimney_glow", (0.48, 0.48, 0.08), (cx, cy, 3.86), m="ember", parent=o)
    box(f"{name}_chimney_mouth", (0.4, 0.06, 0.32), (cx, cy - 0.32, 0.5), m="ember", parent=o)
    empty(f"smoke_{name}", loc=(cx, cy, 4.0), parent=o)
    # open lean-to on the left with the forge, bellows and water barrel
    lx = -W / 2 - 0.55
    for i, (px, py) in enumerate([(lx - 0.5, -0.95), (lx - 0.5, 0.85)]):
        box(f"{name}_leanto_post_{i}", (0.14, 0.14, 1.95), (px, py, 0), m="timber", parent=o, bevel=0.015)
    for i in range(6):
        box(f"{name}_leanto_plank_{i}", (1.45, 0.34, 0.06), (lx + 0.1, -0.95 + i * 0.36, 2.1), rot=(0, 18, 0), m="slate" if i % 2 else "slate2",
            parent=o, base=False, bevel=0.01)
    box(f"{name}_forge", (0.9, 0.85, 0.75), (lx + 0.05, 0.1, 0), m="cobble", parent=o, bevel=0.04)
    box(f"{name}_forge_coals", (0.62, 0.58, 0.05), (lx + 0.05, 0.1, 0.75), m="ember", parent=o)
    box(f"{name}_forge_hood", (0.8, 0.75, 0.45), (lx + 0.05, 0.12, 1.45), m="stonedark", parent=o, bevel=0.03)
    box(f"{name}_bellows", (0.32, 0.5, 0.18), (lx - 0.45, 0.1, 0.5), rot=(0, 0, 0), m="leather", parent=o, bevel=0.03)
    barrel(o, f"{name}_water", lx - 0.2, -0.75, h=0.5, r=0.2)
    cyl(f"{name}_water_top", 0.18, 0.02, (lx - 0.2, -0.75, 0.49), m="crystal", parent=o, seg=12)
    # weapon rack against the front wall
    rack = empty(f"{name}_rack", loc=(-0.45, -D / 2 + 0.1 - 0.25, 0), parent=o)
    box(f"{name}_rack_rail", (0.9, 0.08, 0.08), (0, 0, 0.9), m="timber", parent=rack)
    for i, sx in enumerate((-0.42, 0.42)):
        box(f"{name}_rack_leg_{i}", (0.08, 0.08, 1.0), (sx, 0, 0), m="timber", parent=rack)
    for i, x in enumerate((-0.25, 0.0, 0.25)):
        box(f"{name}_blade_{i}", (0.06, 0.02, 0.7), (x, -0.05, 0.15), rot=(0, r.uniform(-4, 4), 0), m="steel", parent=rack)
        box(f"{name}_guard_{i}", (0.16, 0.04, 0.03), (x, -0.05, 0.85), m="gold", parent=rack)
        cyl(f"{name}_grip_{i}", 0.02, 0.12, (x, -0.05, 0.87), m="leather", parent=rack, seg=6)
    # sign with a hammer icon
    front = anchor(o, f"{name}_front", W, D, "front", 0.25, 0)
    front.location.y += 0.1

    def hammer_icon(s, n):
        box(f"{n}_icon_handle", (0.05, 0.08, 0.26), (0.02, 0, 0.06), rot=(0, -30, 0), m="wooddark", parent=s)
        box(f"{n}_icon_head", (0.22, 0.08, 0.09), (0.08, 0, 0.26), rot=(0, -30, 0), m="slate", parent=s)
    hanging_sign(front, f"{name}_sign", W / 2 - 0.1, 2.0, hammer_icon)
    crate(o, f"{name}_crate", W / 2 + 0.55, -0.6, 10)
    for i in range(3):
        box(f"{name}_ingot_{i}", (0.22, 0.1, 0.07), (W / 2 + 0.55 + (i - 1) * 0.08, -0.6, 0.38 + i * 0.07), rot=(0, 0, 90 * (i % 2)),
            m="gold" if i == 2 else "iron", parent=o)
    return o


def wizard_tower(name, parent, loc, rot_z):
    o = empty(name, loc=(*loc, 0), rot=(0, 0, rot_z), parent=parent)
    r = random.Random(23)
    T = 3.0  # top of the tower body; balcony and roof sit on it
    taper = lambda z: 1.02 - 0.12 * (z - 0.6) / (T - 0.6)  # noqa: E731
    cyl(f"{name}_base", 1.3, 0.6, m="stonedark", parent=o, seg=16, bevel=0.03)
    cyl(f"{name}_body", 1.02, T - 0.6, (0, 0, 0.6), m="plaster", parent=o, seg=16, r2=0.9)
    for i, z in enumerate((1.5, T - 0.35)):
        cyl(f"{name}_band_{i}", taper(z) + 0.04, 0.14, (0, 0, z), m="cobble", parent=o, seg=16)
    # stones and lit windows spiralling up the tower
    for i in range(9):
        a = r.uniform(0, math.tau)
        z = r.uniform(0.9, T - 0.3)
        rad = taper(z)
        disc_patch(f"{name}_stone_{i}", r.uniform(0.1, 0.15), (math.cos(a) * rad, math.sin(a) * rad, z),
                   (90, 0, math.degrees(a) + 90), parent=o, rng=r)
    for i in range(4):
        a = math.radians(-90 + 54 + i * 90)
        z = 1.1 + i * 0.4
        rad = taper(z)
        w = empty(f"{name}_win_{i}", loc=(math.cos(a) * rad, math.sin(a) * rad, z), rot=(0, 0, math.degrees(a) + 90), parent=o)
        window(w, f"{name}_win_{i}", w=0.4, h=0.45, lit=i % 2 == 0, arched=True, rng=r)
    # door
    d = empty(f"{name}_door", loc=(0, -1.06, 0.6), parent=o)
    door(d, f"{name}_door", w=0.58, h=1.0, leaf="robe2", mat=False)
    cyl(f"{name}_door_arch", 0.38, 0.1, (0, -0.02, 1.23), rot=(90, 0, 0), m="timber", parent=d, seg=12)
    for i in range(2):
        box(f"{name}_step_{i}", (1.0, 0.32, 0.4 - 0.2 * i), (0, -1.45 - 0.3 * i, 0), m="cobble", parent=o, bevel=0.02)
    # balcony ring with railing, then the roof
    cyl(f"{name}_balcony", 1.25, 0.12, (0, 0, T), m="timber", parent=o, seg=16)
    for i in range(16):
        a = i / 16 * math.tau
        box(f"{name}_rail_post_{i}", (0.06, 0.06, 0.38), (math.cos(a) * 1.18, math.sin(a) * 1.18, T + 0.12), m="timber", parent=o)
    cyl(f"{name}_rail", 1.2, 0.05, (0, 0, T + 0.46), m="timber", parent=o, seg=16)
    cyl(f"{name}_roof", 1.3, 0.85, (0, 0, T + 0.55), m="robe2", parent=o, seg=16, r2=0.62)
    cyl(f"{name}_roof_tip", 0.62, 0.65, (0, 0.06, T + 1.39), rot=(6, 0, 0), m="robe2", parent=o, seg=16, r2=0.0)
    cyl(f"{name}_roof_trim", 1.32, 0.08, (0, 0, T + 0.55), m="gold", parent=o, seg=16)
    for i in range(4):
        a = math.radians(-100 + i * 70)
        sphere(f"{name}_roof_star_{i}", 0.06, (math.cos(a) * 0.98, math.sin(a) * 0.98, T + 0.97), m="gold", parent=o, seg=8, rings=6)
    sphere(f"{name}_finial", 0.1, (0, 0.14, T + 2.07), m="crystal", parent=o, seg=6, rings=4, scale=(1, 1, 1.6), smooth=False)
    # telescope poking out over the balcony, pointed at the sky
    tel = empty(f"{name}_telescope", loc=(0.62, -0.68, T + 0.2), rot=(-50, 0, 35), parent=o)
    cyl(f"{name}_telescope_tube", 0.08, 0.7, m="gold", parent=tel, seg=10, r2=0.06)
    cyl(f"{name}_telescope_lens", 0.09, 0.06, (0, 0, 0.7), m="steel", parent=tel, seg=10)
    # copper pipes with a steam vent and a little annex hut
    cyl(f"{name}_pipe", 0.07, T - 0.8, (1.0, 0.25, 0.4), m="iron", parent=o, seg=8)
    cyl(f"{name}_pipe_vent", 0.11, 0.2, (1.0, 0.25, T - 0.4), m="slate", parent=o, seg=8)
    empty(f"smoke_{name}", loc=(1.0, 0.25, T - 0.1), parent=o)
    house(f"{name}_annex", o, (-1.85, 0.4), 90, W=1.2, D=1.1, wall_top=1.35, ridge=1.95, roof="slate", chimney=False,
          door_along=0.0, flowers=False, props=False, seed=29)
    potted_plant(o, f"{name}_plant_0", -0.75, -1.25, r)
    for i in range(3):
        cyl(f"{name}_book_{i}", 0.12, 0.08, (0.75, -0.95, 0.6 + i * 0.08), rot=(0, 0, 20 * i), m=("robe", "cape", "tunic")[i], parent=o, seg=4)
    return o


def guild_hall(name, parent, loc, rot_z):
    o = empty(name, loc=(*loc, 0), rot=(0, 0, rot_z), parent=parent)
    r = random.Random(31)
    W, D, GROUND, TOP, RIDGE = 3.6, 2.6, 2.0, 3.25, 4.5
    box(f"{name}_plinth", (W + 0.2, D + 0.2, PLINTH), m="stonedark", parent=o, bevel=0.04)
    # stone ground floor, plaster upper floor jettied out over it
    box(f"{name}_ground", (W, D, GROUND - PLINTH), (0, 0, PLINTH), m="cobble", parent=o, bevel=0.04)
    for i in range(14):
        x = r.uniform(0.75, W / 2 - 0.3) * r.choice((-1, 1))  # keep clear of the doors
        box(f"{name}_block_{i}", (r.uniform(0.3, 0.5), 0.04, r.uniform(0.18, 0.26)),
            (x, -D / 2 - 0.02, r.uniform(0.35, GROUND - 0.2)), m="stonedark", parent=o, bevel=0.01)
    box(f"{name}_joists", (W + 0.3, D + 0.3, 0.14), (0, 0, GROUND), m="timber", parent=o, bevel=0.02)
    box(f"{name}_upper", (W + 0.2, D + 0.2, TOP - GROUND - 0.14), (0, 0, GROUND + 0.14), m="plaster", parent=o, bevel=0.03)
    gable_fill(f"{name}_gable", o, W + 0.18, D + 0.2, TOP, RIDGE - 0.12, m="plaster")
    # cross-braced timber frame on the upper floor
    up = anchor(o, f"{name}_upper_front", W + 0.2, D + 0.2, "front", 0, GROUND + 0.14)
    h = TOP - GROUND - 0.14
    for i, x in enumerate((-1.8, -0.9, 0.0, 0.9, 1.8)):
        box(f"{name}_stud_{i}", (0.13, 0.08, h), (x, -0.02, 0), m="timber", parent=up)
    for i, x in enumerate((-1.35, 1.35)):
        for j, s in enumerate((1, -1)):
            box(f"{name}_brace_{i}_{j}", (0.1, 0.07, 1.25), (x, -0.03, h / 2), rot=(0, s * 48, 0), m="timber", parent=up, base=False)
    box(f"{name}_top_beam", (W + 0.3, 0.1, 0.12), (0, -0.03, h - 0.06), m="timber", parent=up)
    for i, x in enumerate((-0.45, 0.45)):
        window(empty(f"{name}_wu_{i}", loc=(x, 0, 0.2), parent=up), f"{name}_wu_{i}", w=0.6, h=0.65, shutters="banner",
               lit=i == 1, rng=r)
    # big double doors with banners and a quest board
    f = anchor(o, f"{name}_front", W, D, "front", 0, PLINTH)
    door(empty(f"{name}_door", loc=(0, 0, 0), parent=f), f"{name}_door", w=1.0, h=1.35, knob_side=1)
    cyl(f"{name}_door_arch", 0.59, 0.1, (0, -0.0, 1.58), rot=(90, 0, 0), m="timber", parent=f, seg=14)
    for j, sx in enumerate((-1, 1)):
        bx = sx * 1.25
        box(f"{name}_banner_{j}", (0.48, 0.04, 1.2), (bx, -0.18, GROUND - 1.25), m="banner" if j else "cape", parent=f)
        prism(f"{name}_banner_tip_{j}", [(-0.24, 0), (0.24, 0), (0, -0.24)], 0.04, (bx, -0.18, GROUND - 1.25), m="banner" if j else "cape", parent=f, axis="y")
        box(f"{name}_banner_rod_{j}", (0.6, 0.06, 0.06), (bx, -0.2, GROUND - 0.08), m="gold", parent=f)
        # crossed swords emblem
        for k, s in enumerate((1, -1)):
            box(f"{name}_emblem_{j}_{k}", (0.05, 0.03, 0.5), (bx, -0.21, GROUND - 0.65), rot=(0, s * 35, 0), m="steel", parent=f, base=False)
        lantern(f, f"{name}_lantern_{j}", sx * 0.78, 1.25)
    board = empty(f"{name}_board", loc=(W / 2 + 0.55, -D / 2 - 0.35, 0), rot=(0, 0, -15), parent=o)
    for i, sx in enumerate((-0.42, 0.42)):
        box(f"{name}_board_leg_{i}", (0.08, 0.08, 1.45), (sx, 0, 0), m="timber", parent=board)
    box(f"{name}_board_panel", (0.95, 0.06, 0.7), (0, -0.02, 0.65), m="leather", parent=board, bevel=0.015)
    box(f"{name}_board_roof", (1.1, 0.3, 0.06), (0, -0.04, 1.42), rot=(-20, 0, 0), m="roof", parent=board, bevel=0.01)
    for i in range(5):
        box(f"{name}_note_{i}", (r.uniform(0.18, 0.26), 0.02, r.uniform(0.2, 0.28)),
            (-0.3 + (i % 3) * 0.3, -0.06, 0.75 + (i // 3) * 0.3), rot=(0, r.uniform(-12, 12), 0), m="apron", parent=board)
    gable_planks(f"{name}_roof", o, W + 0.2, D + 0.2, TOP, RIDGE, overhang=0.3, plank=0.36, rng=r)
    box(f"{name}_chimney", (0.45, 0.45, 1.6), (-1.1, 0.5, TOP), m="cobble", parent=o, bevel=0.03)
    box(f"{name}_chimney_cap", (0.58, 0.58, 0.1), (-1.1, 0.5, TOP + 1.6), m="slate", parent=o, bevel=0.02)
    empty(f"smoke_{name}", loc=(-1.1, 0.5, TOP + 1.75), parent=o)
    for face in ("right", "left", "back"):
        a = anchor(o, f"{name}_{face}", W, D, face, 0, PLINTH)
        window(empty(f"{name}_w_{face}", loc=(0, 0, 0.9), parent=a), f"{name}_w_{face}", w=0.55, h=0.6, lit=r.random() < 0.4, rng=r)
    barrel(o, f"{name}_barrel_0", -W / 2 - 0.35, -D / 2 + 0.1)
    barrel(o, f"{name}_barrel_1", -W / 2 - 0.3, -D / 2 + 0.55, h=0.45, r=0.19)
    return o
