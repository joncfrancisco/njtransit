#!/usr/bin/env python3
"""
Sprite generator for the NJ Transit trainset NewGRF.

Renders each vehicle as a simple 3D model (boxes + surface decals) and projects
it into OpenTTD's isometric view for all 8 vehicle directions, then quantises
the result to the OpenTTD (DOS) palette and writes an 8bpp indexed PNG sheet.

Projection (matches OpenTTD's RemapCoords, tile = 16 world units = 64x32 px):
    screen_x = (wy - wx) * 2
    screen_y = (wy + wx) - wz
Sprite order is N, NE, E, SE, S, SW, W, NW, i.e. world heading angle
phi = 225deg - 45deg * index.

Note that a tile is 16 world units but a train vehicle is not: OpenTTD's
VEHICLE_LENGTH is 8, so a full-length 8/8 vehicle is half a tile. See
LENGTH_SCALE and squash_to_length() below.
"""

import math
import os

import numpy as np
from PIL import Image, ImageDraw

from nml import palette as nmlpal

# ---------------------------------------------------------------- constants --

SS = 4                       # supersampling factor
CELL_W, CELL_H = 52, 40      # sprite cell size in final pixels
ORIGIN_X, ORIGIN_Y = 26, 26  # vehicle reference point inside a cell
NUM_DIRS = 8

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sprites")

# NJ Transit-ish colour set (modern silver/blue/orange scheme)
SILVER      = (206, 212, 218)
SILVER_LOCO = (198, 204, 210)
STAINLESS   = (212, 217, 222)
ROOF        = (112, 118, 124)
ROOF_DARK   = (72, 76, 80)
UNDER       = (46, 48, 52)
BOGIE       = (38, 40, 44)
WHEEL       = (24, 25, 27)
GLASS       = (48, 60, 74)
GLASS_DARK  = (34, 42, 54)
NJT_BLUE    = (0, 76, 190)
NJT_ORANGE  = (252, 124, 8)
HEADLIGHT   = (250, 246, 210)
PANTO       = (58, 60, 64)
GRILLE      = (60, 63, 67)

# PATH: painted aluminium (PA1/PA2) or stainless (PA4/PA5), black window band,
# red trim below it.
PATH_PAINT  = (178, 183, 189)
PATH_STEEL  = (208, 213, 218)
PATH_BAND   = (28, 30, 34)
PATH_RED    = (198, 32, 38)
PATH_ROOF   = (120, 126, 132)
AC_UNIT     = (78, 84, 90)

EPS = 0.06  # decal offset above a face, in world units

# paint layers: solid geometry first, then decals in this order
L_SOLID, L_TEXTURE, L_DOOR, L_STRIPE, L_WINDOW, L_LIGHT = 0, 1, 2, 3, 4, 5
L_DECAL = L_STRIPE


# ------------------------------------------------------------------ palette --

def build_palette():
    raw = list(nmlpal.raw_palette_data[0])          # DEFAULT == DOS palette
    pal = np.array(raw, dtype=np.int16).reshape(256, 3)
    # Usable indices: skip 0 (transparent), the company-colour range (0xC6-0xCD),
    # the special/animated entries at the top of the palette and pure white.
    allowed = [i for i in range(1, 198)]
    return pal, np.array(allowed, dtype=np.int32)


PAL_RGB, ALLOWED = build_palette()
ALLOWED_RGB = PAL_RGB[ALLOWED].astype(np.float32)


def quantise(rgb):
    """rgb: float array (h, w, 3) -> palette index array (h, w) uint8."""
    h, w, _ = rgb.shape
    flat = rgb.reshape(-1, 1, 3).astype(np.float32)
    # weighted euclidean distance, slightly favouring green like the eye does
    weights = np.array([0.9, 1.1, 0.8], dtype=np.float32)
    d = (((flat - ALLOWED_RGB[None, :, :]) * weights) ** 2).sum(axis=2)
    idx = ALLOWED[np.argmin(d, axis=1)]
    return idx.reshape(h, w).astype(np.uint8)


# --------------------------------------------------------------- geometry ---

class Quad:
    __slots__ = ("pts", "rgb", "normal", "top", "flat", "layer")

    def __init__(self, pts, rgb, normal, top=False, flat=False, layer=0):
        self.pts = pts          # 4 x (x, y, z) in vehicle-local coordinates
        self.rgb = rgb
        self.normal = normal    # outward normal, vehicle-local
        self.top = top          # use full brightness (roof/horizontal surfaces)
        self.flat = flat        # do not shade at all (lights etc.)
        self.layer = layer      # paint order: solids first, then decals on top


def rotate(p, c, s):
    x, y, z = p
    return (x * c - y * s, x * s + y * c, z)


def project(p):
    x, y, z = p
    return ((y - x) * 2.0, (y + x) - z)


def shade(rgb, factor):
    return tuple(max(0, min(255, int(round(v * factor)))) for v in rgb)


# ---------------------------------------------------------- model builders ---

def box(x0, x1, y0, y1, z0, z1, rgb, top_rgb=None, skip=()):
    """Axis-aligned box -> list of quads (only the 5 potentially visible faces)."""
    q = []
    if "top" not in skip:
        q.append(Quad([(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)],
                      top_rgb or rgb, (0, 0, 1), top=True))
    if "y+" not in skip:
        q.append(Quad([(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)],
                      rgb, (0, 1, 0)))
    if "y-" not in skip:
        q.append(Quad([(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)],
                      rgb, (0, -1, 0)))
    if "x+" not in skip:
        q.append(Quad([(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)],
                      rgb, (1, 0, 0)))
    if "x-" not in skip:
        q.append(Quad([(x0, y0, z0), (x0, y1, z0), (x0, y1, z1), (x0, y0, z1)],
                      rgb, (-1, 0, 0)))
    return q


def side_decal(x0, x1, z0, z1, half_w, rgb, flat=False, layer=L_DECAL):
    """Decal on both long sides of the body."""
    y = half_w + EPS
    return [
        Quad([(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)],
             rgb, (0, 1, 0), flat=flat, layer=layer),
        Quad([(x0, -y, z0), (x1, -y, z0), (x1, -y, z1), (x0, -y, z1)],
             rgb, (0, -1, 0), flat=flat, layer=layer),
    ]


def end_decal(x, sign, y0, y1, z0, z1, rgb, flat=False, layer=L_DECAL):
    """Decal on one end face (sign = +1 front, -1 rear)."""
    xx = x + sign * EPS
    return [Quad([(xx, y0, z0), (xx, y1, z0), (xx, y1, z1), (xx, y0, z1)],
                 rgb, (sign, 0, 0), flat=flat, layer=layer)]


def top_decal(x0, x1, y0, y1, z, rgb):
    return [Quad([(x0, y0, z + EPS), (x1, y0, z + EPS),
                  (x1, y1, z + EPS), (x0, y1, z + EPS)], rgb, (0, 0, 1), top=True)]


def window_row(x0, x1, z0, z1, half_w, count, rgb=GLASS, pillar=0.42):
    """A row of individual windows along both sides."""
    q = []
    span = (x1 - x0)
    unit = span / count
    for i in range(count):
        a = x0 + i * unit + pillar * 0.5
        b = x0 + (i + 1) * unit - pillar * 0.5
        q += side_decal(a, b, z0, z1, half_w, rgb, layer=L_WINDOW)
    return q


def running_gear(length, half_w, truck_z=2.45, inset=2.2):
    """Bogies and wheels under the body."""
    q = []
    bw = half_w * 0.80
    for sgn in (-1, 1):
        cx = sgn * (length / 2.0 - inset)
        q += box(cx - 1.55, cx + 1.55, -bw, bw, 0.85, truck_z, BOGIE)
        for wx in (cx - 1.15, cx + 0.15):
            q += box(wx, wx + 1.0, -bw - 0.18, bw + 0.18, 0.0, 1.35, WHEEL)
    return q


def pantograph(cx, half_w, z_roof, up=1.35):
    """A folded pantograph sitting on the roof."""
    q = []
    q += box(cx - 1.5, cx + 1.5, -half_w * 0.62, half_w * 0.62,
             z_roof, z_roof + 0.30, PANTO)
    # bow + arms, drawn as a thin slab so it reads at this size
    q += box(cx - 0.35, cx + 0.35, -half_w * 0.30, half_w * 0.30,
             z_roof + 0.30, z_roof + up - 0.28, PANTO)
    q += box(cx - 1.7, cx + 1.7, -half_w * 0.55, half_w * 0.55,
             z_roof + up - 0.28, z_roof + up, PANTO)
    return q


def livery_stripes(x0, x1, half_w, z_blue, blue_h=1.7, orange_h=0.72, gap=0.22):
    q = []
    q += side_decal(x0, x1, z_blue, z_blue + blue_h, half_w, NJT_BLUE,
                    layer=L_STRIPE)
    q += side_decal(x0, x1, z_blue - gap - orange_h, z_blue - gap, half_w,
                    NJT_ORANGE, layer=L_STRIPE)
    return q


# ------------------------------------------------------------ the vehicles ---

def loco_body(length, half_w, body_z0, body_z1, roof_z1, body_rgb,
              cabs=2, pantos=(), grilles=False):
    """Shared shape for the four locomotives."""
    hl = length / 2.0
    q = []
    q += running_gear(length, half_w, truck_z=2.5, inset=2.4)
    # underframe / fuel tank
    q += box(-hl + 1.3, hl - 1.3, -half_w * 0.92, half_w * 0.92,
             2.2, body_z0 + 0.25, UNDER)
    # carbody
    q += box(-hl, hl, -half_w, half_w, body_z0, body_z1, body_rgb,
             top_rgb=body_rgb)
    # roof
    q += box(-hl + 0.35, hl - 0.35, -half_w * 0.86, half_w * 0.86,
             body_z1, roof_z1, ROOF, top_rgb=ROOF)

    win_z0, win_z1 = body_z1 - 2.55, body_z1 - 0.55
    # cab windows at the ends, plus a body-side band
    for sgn in (1, -1):
        if cabs == 1 and sgn == -1:
            continue
        x_out = sgn * hl
        x_in = sgn * (hl - 2.3)
        lo, hi = min(x_out, x_in), max(x_out, x_in)
        q += side_decal(lo + 0.35, hi - 0.35, win_z0, win_z1, half_w, GLASS_DARK,
                        layer=L_WINDOW)
        q += end_decal(sgn * hl, sgn, -half_w * 0.74, half_w * 0.74,
                       win_z0, win_z1, GLASS_DARK, layer=L_WINDOW)
        # headlights
        q += end_decal(sgn * hl, sgn, -half_w * 0.72, -half_w * 0.36,
                       win_z1 + 0.35, win_z1 + 0.85, HEADLIGHT, flat=True,
                       layer=L_LIGHT)
        q += end_decal(sgn * hl, sgn, half_w * 0.36, half_w * 0.72,
                       win_z1 + 0.35, win_z1 + 0.85, HEADLIGHT, flat=True,
                       layer=L_LIGHT)

    if grilles:
        for sgn in (-1, 1):
            q += side_decal(sgn * 1.0, sgn * (hl - 3.2), win_z0 - 0.2, win_z1,
                            half_w, GRILLE, layer=L_TEXTURE)

    # NJT stripes along the flanks
    q += livery_stripes(-hl + 0.3, hl - 0.3, half_w, body_z0 + 1.55)
    q += end_decal(hl, 1, -half_w * 0.9, half_w * 0.9,
                   body_z0 + 1.55, body_z0 + 3.25, NJT_BLUE, layer=L_STRIPE)
    q += end_decal(-hl, -1, -half_w * 0.9, half_w * 0.9,
                   body_z0 + 1.55, body_z0 + 3.25, NJT_BLUE, layer=L_STRIPE)

    for cx in pantos:
        q += pantograph(cx, half_w, roof_z1)
    return q


def coach_body(length, half_w, levels=1, cab=0, corrugated=False,
               body_rgb=STAINLESS, panto=False):
    """Single-level or multilevel passenger car. cab: 0 none, +1/-1 cab at one end."""
    hl = length / 2.0
    body_z0 = 3.15
    if levels == 1:
        body_z1, roof_z1 = 8.7, 9.7
    else:
        body_z1, roof_z1 = 11.3, 12.4

    q = []
    q += running_gear(length, half_w, truck_z=2.55, inset=2.3)
    q += box(-hl + 1.1, hl - 1.1, -half_w * 0.9, half_w * 0.9,
             2.3, body_z0 + 0.2, UNDER)
    q += box(-hl, hl, -half_w, half_w, body_z0, body_z1, body_rgb,
             top_rgb=body_rgb)
    q += box(-hl + 0.3, hl - 0.3, -half_w * 0.87, half_w * 0.87,
             body_z1, roof_z1, ROOF, top_rgb=ROOF)

    if corrugated:
        z = body_z0 + 0.5
        while z < body_z1 - 0.4:
            q += side_decal(-hl + 0.2, hl - 0.2, z, z + 0.16, half_w,
                            shade(body_rgb, 0.86), layer=L_TEXTURE)
            z += 0.85

    if levels == 1:
        rows = [(body_z1 - 2.75, body_z1 - 0.75, 7)]
    else:
        rows = [(body_z0 + 0.95, body_z0 + 2.5, 7),
                (body_z1 - 2.6, body_z1 - 0.85, 7)]

    win_x0, win_x1 = -hl + 1.0, hl - 1.0
    if cab:
        # keep the cab end clear of passenger windows
        if cab > 0:
            win_x1 = hl - 3.1
        else:
            win_x0 = -hl + 3.1

    for z0, z1, n in rows:
        q += window_row(win_x0, win_x1, z0, z1, half_w, n)

    if cab:
        sgn = 1 if cab > 0 else -1
        cz0, cz1 = body_z1 - 2.75, body_z1 - 0.75
        x_out, x_in = sgn * hl, sgn * (hl - 2.6)
        lo, hi = min(x_out, x_in), max(x_out, x_in)
        q += side_decal(lo + 0.4, hi - 0.4, cz0, cz1, half_w, GLASS_DARK,
                        layer=L_WINDOW)
        q += end_decal(sgn * hl, sgn, -half_w * 0.76, half_w * 0.76,
                       cz0, cz1, GLASS_DARK, layer=L_WINDOW)
        q += end_decal(sgn * hl, sgn, -half_w * 0.7, -half_w * 0.34,
                       cz0 - 1.5, cz0 - 1.0, HEADLIGHT, flat=True, layer=L_LIGHT)
        q += end_decal(sgn * hl, sgn, half_w * 0.34, half_w * 0.7,
                       cz0 - 1.5, cz0 - 1.0, HEADLIGHT, flat=True, layer=L_LIGHT)

    stripe_z = body_z0 + (1.15 if levels == 1 else 3.05)
    q += livery_stripes(-hl + 0.25, hl - 0.25, half_w, stripe_z)
    q += end_decal(hl, 1, -half_w * 0.9, half_w * 0.9,
                   stripe_z, stripe_z + 1.7, NJT_BLUE, layer=L_STRIPE)
    q += end_decal(-hl, -1, -half_w * 0.9, half_w * 0.9,
                   stripe_z, stripe_z + 1.7, NJT_BLUE, layer=L_STRIPE)

    # doors
    for sgn in (-1, 1):
        dx = sgn * (hl - 2.0)
        q += side_decal(dx - 0.55, dx + 0.55, body_z0 + 0.2, body_z1 - 0.35,
                        half_w, shade(body_rgb, 0.80), layer=L_DOOR)

    if panto:
        q += pantograph(0.0, half_w, roof_z1, up=1.3)
    return q


def metro_body(length, half_w, doors=3, cab=0, body_rgb=PATH_STEEL,
               roof_ac=False):
    """PATH rapid-transit car: short, narrow, low, black window band.

    cab: +1 cab at the front, -1 cab at the rear, 0 for a cabless C car.
    """
    hl = length / 2.0
    body_z0, body_z1, roof_z1 = 3.0, 8.0, 8.8
    band_z0, band_z1 = body_z1 - 2.75, body_z1 - 0.5

    q = []
    q += running_gear(length, half_w, truck_z=2.4, inset=1.9)
    q += box(-hl + 0.8, hl - 0.8, -half_w * 0.9, half_w * 0.9,
             2.2, body_z0 + 0.2, UNDER)
    q += box(-hl, hl, -half_w, half_w, body_z0, body_z1, body_rgb,
             top_rgb=body_rgb)
    q += box(-hl + 0.25, hl - 0.25, -half_w * 0.88, half_w * 0.88,
             body_z1, roof_z1, PATH_ROOF, top_rgb=PATH_ROOF)
    if roof_ac:
        for cx in (-1.9, 1.9):
            q += box(cx - 0.85, cx + 0.85, -half_w * 0.42, half_w * 0.42,
                     roof_z1, roof_z1 + 0.35, AC_UNIT)

    # the black band wraps the whole car at window height
    q += side_decal(-hl + 0.2, hl - 0.2, band_z0, band_z1, half_w, PATH_BAND,
                    layer=L_TEXTURE)
    for sgn in (1, -1):
        q += end_decal(sgn * hl, sgn, -half_w * 0.94, half_w * 0.94,
                       band_z0, band_z1, PATH_BAND, layer=L_TEXTURE)
    # red trim under the band
    q += side_decal(-hl + 0.2, hl - 0.2, band_z0 - 0.75, band_z0 - 0.2,
                    half_w, PATH_RED, layer=L_STRIPE)
    q += end_decal(hl, 1, -half_w * 0.94, half_w * 0.94,
                   band_z0 - 0.75, band_z0 - 0.2, PATH_RED, layer=L_STRIPE)
    q += end_decal(-hl, -1, -half_w * 0.94, half_w * 0.94,
                   band_z0 - 0.75, band_z0 - 0.2, PATH_RED, layer=L_STRIPE)

    # doorways break the band from roof line to floor
    step = (length - 2.2) / doors
    door_x = [-hl + 1.1 + step * (i + 0.5) for i in range(doors)]
    for dx in door_x:
        # door leaves sit below the band; the band runs unbroken over them
        q += side_decal(dx - 0.52, dx + 0.52, body_z0 + 0.25, band_z0 - 0.9,
                        half_w, shade(body_rgb, 0.74), layer=L_DOOR)
        q += side_decal(dx - 0.38, dx + 0.38, band_z0 + 0.18, band_z1 - 0.18,
                        half_w, GLASS, layer=L_WINDOW)

    # passenger windows in the gaps between doors
    edges = [-hl + 0.9] + [x for dx in door_x for x in (dx - 0.62, dx + 0.62)] + [hl - 0.9]
    if cab > 0:
        edges[-1] = hl - 2.4
    elif cab < 0:
        edges[0] = -hl + 2.4
    for i in range(0, len(edges), 2):
        a, b = edges[i], edges[i + 1]
        if b - a > 0.9:
            q += window_row(a, b, band_z0 + 0.22, band_z1 - 0.22, half_w,
                            max(1, int((b - a) / 1.9)))

    if cab:
        sgn = 1 if cab > 0 else -1
        q += side_decal(sgn * (hl - 2.2), sgn * (hl - 0.45),
                        band_z0 + 0.22, band_z1 - 0.22, half_w, GLASS_DARK,
                        layer=L_WINDOW)
        q += end_decal(sgn * hl, sgn, -half_w * 0.78, half_w * 0.78,
                       band_z0 + 0.15, band_z1 - 0.15, GLASS_DARK,
                       layer=L_WINDOW)
        q += end_decal(sgn * hl, sgn, -half_w * 0.72, -half_w * 0.36,
                       body_z0 + 0.7, body_z0 + 1.25, HEADLIGHT, flat=True,
                       layer=L_LIGHT)
        q += end_decal(sgn * hl, sgn, half_w * 0.36, half_w * 0.72,
                       body_z0 + 0.7, body_z0 + 1.25, HEADLIGHT, flat=True,
                       layer=L_LIGHT)
    return q


HALF_W = 1.75          # half body width in world units
PATH_HALF_W = 1.52     # PATH cars are narrower: 9 ft 2 in against 10 ft 6 in
PATH_L = 9.0           # 51 ft 8 in against 85 ft, so 5/8 vehicle length
LOCO_L = 13.0          # 7/8 length vehicles
CAR_L = 14.5           # 8/8 length vehicles


# ------------------------------------------------------------ vehicle length --
#
# OpenTTD measures a train vehicle in eighths of VEHICLE_LENGTH, and
# VEHICLE_LENGTH is 8 against a tile's 16 (src/vehicle_type.h, src/map_type.h).
# A full-length 8/8 vehicle is therefore half a tile, and the game spaces
# consecutive vehicles by exactly `length` world units - not the 2 x `length`
# a full tile would suggest.
#
# The models above are laid out in carbody units, twice that scale, because the
# detail work - bogie insets, door pitch, cab fractions - is easier to reason
# about at a size where a bogie is not one world unit long. squash_to_length()
# halves every model down its long axis just before rendering, so the sprite
# that ships is exactly as long as the room the game leaves for the vehicle.
# Draw at full scale and every car in a consist overlaps the next by ~45%.
LENGTH_SCALE = 0.5


def squash_to_length(quads):
    """Scale a model into OpenTTD's vehicle-length units, centred on the
    vehicle reference point.

    Every normal in this set points either along x or square across it, so a
    pure x scale leaves all of them facing the right way and none of them need
    renormalising.
    """
    xs = [p[0] for q in quads for p in q.pts]
    mid = (min(xs) + max(xs)) / 2.0
    for q in quads:
        q.pts = [((p[0] - mid) * LENGTH_SCALE, p[1], p[2]) for p in q.pts]
    return quads


def model_alp46(a=False):
    return loco_body(LOCO_L, HALF_W, 3.05, 9.5, 10.5, SILVER_LOCO,
                     cabs=2, pantos=(-2.6, 2.6))


def model_alp45dp():
    return loco_body(14.2, HALF_W, 3.05, 9.6, 10.6, SILVER_LOCO,
                     cabs=2, pantos=(-3.3, 3.3), grilles=True)


def model_pl42ac():
    return loco_body(14.0, HALF_W, 3.05, 9.4, 10.4, SILVER_LOCO,
                     cabs=1, pantos=(), grilles=True)


MODELS = {
    "njt_alp46":      lambda: model_alp46(),
    "njt_alp46a":     lambda: model_alp46(True),
    "njt_alp45dp":    lambda: model_alp45dp(),
    "njt_pl42ac":     lambda: model_pl42ac(),
    "njt_arrow3_a":   lambda: coach_body(CAR_L, HALF_W, 1, cab=1,
                                         corrugated=True, panto=True),
    "njt_arrow3_b":   lambda: coach_body(CAR_L, HALF_W, 1, cab=-1,
                                         corrugated=True, panto=True),
    "njt_comet5":     lambda: coach_body(CAR_L, HALF_W, 1, cab=0,
                                         corrugated=True),
    "njt_comet5_cab": lambda: coach_body(CAR_L, HALF_W, 1, cab=1,
                                         corrugated=True),
    "njt_ml":         lambda: coach_body(CAR_L, HALF_W, 2, cab=0),
    "njt_ml_cab":     lambda: coach_body(CAR_L, HALF_W, 2, cab=1),
    "path_pa1_a":     lambda: metro_body(PATH_L, PATH_HALF_W, doors=2, cab=1,
                                         body_rgb=PATH_PAINT),
    "path_pa1_b":     lambda: metro_body(PATH_L, PATH_HALF_W, doors=2, cab=0,
                                         body_rgb=PATH_PAINT),
    "path_pa4_a":     lambda: metro_body(PATH_L, PATH_HALF_W, doors=3, cab=1,
                                         body_rgb=PATH_STEEL),
    "path_pa4_b":     lambda: metro_body(PATH_L, PATH_HALF_W, doors=3, cab=-1,
                                         body_rgb=PATH_STEEL),
    "path_pa5_a":     lambda: metro_body(PATH_L, PATH_HALF_W, doors=3, cab=1,
                                         body_rgb=PATH_STEEL, roof_ac=True),
    "path_pa5_b":     lambda: metro_body(PATH_L, PATH_HALF_W, doors=3, cab=0,
                                         body_rgb=PATH_STEEL, roof_ac=True),
}


# ---------------------------------------------------------------- rendering --

def render_direction(quads, direction):
    """Render one direction into (rgb float array, alpha float array)."""
    phi = math.radians(225.0 - 45.0 * direction)
    c, s = math.cos(phi), math.sin(phi)

    w = CELL_W * SS
    h = CELL_H * SS
    img = Image.new("RGB", (w, h), (0, 0, 0))
    mask = Image.new("L", (w, h), 0)
    d_img = ImageDraw.Draw(img)
    d_mask = ImageDraw.Draw(mask)

    prepared = []
    for q in quads:
        nx, ny, nz = rotate(q.normal, c, s)
        if nx + ny + 2.0 * nz <= 0.02:       # back-face cull (view dir 1,1,2)
            continue
        wpts = [rotate(p, c, s) for p in q.pts]
        depth = sum(p[0] + p[1] + p[2] for p in wpts) / 4.0
        if q.flat:
            factor = 1.0
        elif q.top:
            factor = 1.0
        else:
            n = math.hypot(nx, ny) or 1.0
            t = (nx - ny) / (n * math.sqrt(2.0))
            factor = 0.82 + 0.13 * t
        rgb = q.rgb if q.flat else shade(q.rgb, factor)
        poly = []
        for p in wpts:
            sx, sy = project(p)
            poly.append(((sx + ORIGIN_X) * SS, (sy + ORIGIN_Y) * SS))
        prepared.append((q.layer, depth, poly, rgb))

    prepared.sort(key=lambda item: (item[0], item[1]))
    for _, _, poly, rgb in prepared:
        d_img.polygon(poly, fill=rgb)
        d_mask.polygon(poly, fill=255)

    rgb_a = np.asarray(img, dtype=np.float32)
    m_a = np.asarray(mask, dtype=np.float32) / 255.0

    # mask-weighted downsample so edges do not bleed the background colour
    rgb_a = rgb_a.reshape(CELL_H, SS, CELL_W, SS, 3)
    m_a = m_a.reshape(CELL_H, SS, CELL_W, SS)
    wsum = m_a.sum(axis=(1, 3))
    csum = (rgb_a * m_a[..., None]).sum(axis=(1, 3))
    alpha = wsum / (SS * SS)
    colour = np.where(wsum[..., None] > 0, csum / np.maximum(wsum, 1e-6)[..., None], 0.0)
    return colour, alpha


def render_vehicle(name, quads):
    sheet = np.zeros((CELL_H, CELL_W * NUM_DIRS), dtype=np.uint8)
    for d in range(NUM_DIRS):
        colour, alpha = render_direction(quads, d)
        idx = quantise(colour)
        idx[alpha < 0.42] = 0
        sheet[:, d * CELL_W:(d + 1) * CELL_W] = idx

    img = Image.fromarray(sheet, mode="P")
    img.putpalette(list(nmlpal.raw_palette_data[0]))
    path = os.path.join(OUT_DIR, name + ".png")
    img.save(path, optimize=False)
    return path


def make_preview(names, scale=4):
    """A human-readable preview: all vehicles, all directions, on a grid."""
    pal = PAL_RGB
    rows = []
    for name in names:
        arr = np.array(Image.open(os.path.join(OUT_DIR, name + ".png")))
        rgb = pal[arr].astype(np.uint8)
        bg = np.zeros_like(rgb)
        bg[:, :] = (58, 92, 56)
        for d in range(NUM_DIRS):
            sl = slice(d * CELL_W, (d + 1) * CELL_W)
            if d % 2 == 0:
                bg[:, sl] = (52, 84, 50)
        out = np.where((arr == 0)[..., None], bg, rgb)
        rows.append(out)
    grid = np.concatenate(rows, axis=0)
    img = Image.fromarray(grid.astype(np.uint8))
    img = img.resize((img.width * scale, img.height * scale), Image.NEAREST)
    path = os.path.join(os.path.dirname(OUT_DIR), "sprite_preview.png")
    img.save(path)
    return path


def check_length(name, quads, length):
    """A sprite must not be longer than the room OpenTTD leaves the vehicle.

    `length` is the vehicle's NML length property, in eighths, which is also
    its span in world units. Anything longer here reaches into the next
    vehicle in the consist.
    """
    xs = [p[0] for q in quads for p in q.pts]
    drawn = max(xs) - min(xs)
    if drawn > length + 1e-6:
        raise SystemExit(
            "{}: sprite is {:.2f} world units long but the vehicle is only "
            "{} - consists would overlap".format(name, drawn, length))
    return drawn


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    from fleet import VEHICLES
    from historic import models as historic_models   # late: it imports us back
    MODELS.update(historic_models())
    lengths = {v["sprite"]: v["length"] for v in VEHICLES}
    names = []
    for name, builder in MODELS.items():
        quads = squash_to_length(builder())
        drawn = check_length(name, quads, lengths[name])
        render_vehicle(name, quads)
        names.append(name)
        print("wrote {:<18} {:.2f} of {} world units ({:.0f}%)".format(
            name + ".png", drawn, lengths[name], 100 * drawn / lengths[name]))
    print("preview:", make_preview(names))


if __name__ == "__main__":
    main()
