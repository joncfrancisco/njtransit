#!/usr/bin/env python3
"""
Model builders for the 1950-1990 historical stock, in their own liveries.

Imported by gen_sprites.py. Everything here uses the same box/decal/quad
primitives, plus one new one: prism(), a faceted cylinder used for steam
locomotive boilers and the arched clerestory roofs of pre-war coaches.
"""

import math

from gen_sprites import (
    Quad, box, side_decal, end_decal, window_row, running_gear, pantograph,
    shade, EPS, GLASS, GLASS_DARK, HEADLIGHT, UNDER, BOGIE, WHEEL, PANTO,
    L_SOLID, L_TEXTURE, L_DOOR, L_STRIPE, L_WINDOW, L_LIGHT,
)

# ------------------------------------------------------------------ liveries --

PRR_GREEN     = (34, 46, 38)     # Dark Green Locomotive Enamel, near black
PRR_TUSCAN    = (118, 52, 46)
PRR_GOLD      = (206, 172, 84)
EL_GREY       = (152, 156, 158)
EL_MAROON     = (104, 42, 50)
EL_YELLOW     = (224, 186, 62)
CNJ_GREEN     = (36, 68, 56)
CNJ_YELLOW    = (226, 200, 84)
DLW_GREEN     = (48, 64, 50)     # Pullman green
ERIE_GREEN    = (44, 58, 46)
U34_BLUE      = (26, 48, 116)
U34_SILVER    = (196, 202, 208)
U34_RED       = (176, 42, 46)
ALUM          = (192, 196, 200)
STAINLESS     = (206, 211, 216)
CHEVRON_ORANGE = (232, 116, 28)
CHEVRON_RED   = (188, 46, 44)
CHEVRON_BLUE  = (28, 62, 152)
SMOKEBOX      = (74, 76, 78)
STEEL_DARK    = (54, 56, 60)
ROOF_MID      = (108, 114, 120)
ROOF_DARK     = (66, 70, 74)


def livery(body, roof, stripes=(), band=None, band_edge=None, window=GLASS):
    """stripes: list of (colour, height) drawn upward from the belt line.
    band: a wide window-height side band (EL grey/maroon, U34CH bluebird)."""
    return dict(body=body, roof=roof, stripes=list(stripes), band=band,
                band_edge=band_edge, window=window)


LIV = {
    "prr_green":  livery(PRR_GREEN, ROOF_DARK, stripes=[(PRR_GOLD, 0.5)]),
    "prr_tuscan": livery(PRR_TUSCAN, ROOF_DARK, stripes=[(PRR_GOLD, 0.55)]),
    "el_grey":    livery(EL_GREY, ROOF_DARK, band=EL_MAROON, band_edge=EL_YELLOW),
    "cnj":        livery(CNJ_GREEN, ROOF_DARK, stripes=[(CNJ_YELLOW, 0.55)]),
    "dlw":        livery(DLW_GREEN, ROOF_DARK, stripes=[(PRR_GOLD, 0.45)]),
    "erie":       livery(ERIE_GREEN, ROOF_DARK, stripes=[(PRR_GOLD, 0.4)]),
    "bluebird":   livery(U34_BLUE, ROOF_DARK, band=U34_SILVER, band_edge=U34_RED),
    "comet1":     livery(ALUM, ROOF_MID, band=EL_MAROON, band_edge=EL_YELLOW),
    "chevron":    livery(STAINLESS, ROOF_MID,
                         stripes=[(CHEVRON_BLUE, 0.8), (CHEVRON_RED, 0.55),
                                  (CHEVRON_ORANGE, 0.55)]),
    "stainless":  livery(STAINLESS, ROOF_MID, stripes=[]),
}


# ----------------------------------------------------------- new primitive --

def prism(x0, x1, cy, cz, ry, rz, rgb, facets=8, a0=-180.0, a1=180.0,
          top_rgb=None, caps=True, layer=L_SOLID):
    """A faceted cylinder along the x axis: boilers, tanks, arched roofs."""
    q = []
    n = max(3, facets)
    step = math.radians(a1 - a0) / n
    a = math.radians(a0)
    pts = []
    for i in range(n + 1):
        pts.append((cy + ry * math.sin(a + step * i),
                    cz + rz * math.cos(a + step * i)))
    for i in range(n):
        y0, z0 = pts[i]
        y1, z1 = pts[i + 1]
        my, mz = (y0 + y1) / 2 - cy, (z0 + z1) / 2 - cz
        norm = math.hypot(my, mz) or 1.0
        nz = mz / norm
        face_rgb = top_rgb if (top_rgb and nz > 0.72) else rgb
        q.append(Quad([(x0, y0, z0), (x1, y0, z0), (x1, y1, z1), (x0, y1, z1)],
                      face_rgb, (0, my / norm, nz), top=(nz > 0.85), layer=layer))
    if caps:
        for x, sgn in ((x1, 1), (x0, -1)):
            for i in range(n):
                y0, z0 = pts[i]
                y1, z1 = pts[i + 1]
                q.append(Quad([(x, cy, cz), (x, y0, z0), (x, y1, z1), (x, cy, cz)],
                              shade(rgb, 0.82), (sgn, 0, 0), layer=layer))
    return q


def band_and_stripes(x0, x1, half_w, liv, belt_z, band_z0=None, band_z1=None):
    """Apply a livery's side band and/or belt stripes to a carbody."""
    q = []
    if liv["band"] and band_z0 is not None:
        if liv["band_edge"]:
            q += side_decal(x0, x1, band_z0 - 0.34, band_z1 + 0.34, half_w,
                            liv["band_edge"], layer=L_TEXTURE)
        q += side_decal(x0, x1, band_z0, band_z1, half_w, liv["band"],
                        layer=L_STRIPE)
    z = belt_z
    for colour, height in liv["stripes"]:
        q += side_decal(x0, x1, z, z + height, half_w, colour, layer=L_STRIPE)
        z += height + 0.22
    return q


# ------------------------------------------------------------- steam power --

def steam_loco(length, half_w, liv):
    """A 4-6-2 Pacific with tender: prism boiler, cab, three driver pairs."""
    hl = length / 2.0
    q = []
    eng_x0, eng_x1 = -hl, hl - 6.4          # engine
    ten_x0, ten_x1 = hl - 6.0, hl           # tender, ahead in +x is the front

    # running gear: pilot truck, three drivers, trailing truck
    for wx, r in ((eng_x1 - 1.1, 0.55), (eng_x1 - 2.1, 0.55)):
        q += box(wx - 0.45, wx + 0.45, -half_w * 0.72, half_w * 0.72, 0.0, r * 2, WHEEL)
    for i in range(3):
        wx = eng_x0 + 3.4 + i * 2.1
        q += box(wx - 0.85, wx + 0.85, -half_w * 0.86, half_w * 0.86, 0.0, 3.1, WHEEL)
    q += box(eng_x0 + 0.5, eng_x0 + 1.6, -half_w * 0.7, half_w * 0.7, 0.0, 1.5, WHEEL)

    # frame and running boards
    q += box(eng_x0, eng_x1, -half_w * 0.94, half_w * 0.94, 3.0, 3.6, STEEL_DARK)

    # boiler, smokebox, stack, dome
    q += prism(eng_x0 + 1.2, eng_x1 - 2.2, 0.0, 6.0, half_w * 0.80, 2.35,
               liv["body"], facets=8, top_rgb=shade(liv["body"], 1.12), caps=False)
    q += prism(eng_x1 - 2.4, eng_x1 - 0.2, 0.0, 6.0, half_w * 0.84, 2.45,
               SMOKEBOX, facets=8, top_rgb=shade(SMOKEBOX, 1.1))
    q += box(eng_x1 - 1.9, eng_x1 - 1.0, -half_w * 0.30, half_w * 0.30,
             8.3, 9.5, SMOKEBOX)                                   # stack
    q += prism(eng_x0 + 4.3, eng_x0 + 5.5, 0.0, 7.9, half_w * 0.34, 0.85,
               shade(liv["body"], 1.05), facets=6, a0=-90, a1=90, caps=False)

    # cab
    q += box(eng_x0 + 0.2, eng_x0 + 3.2, -half_w * 0.92, half_w * 0.92,
             3.6, 9.4, liv["body"], top_rgb=liv["roof"])
    q += side_decal(eng_x0 + 0.6, eng_x0 + 2.8, 7.2, 8.7, half_w * 0.92,
                    GLASS_DARK, layer=L_WINDOW)

    # tender
    q += box(ten_x0, ten_x1, -half_w * 0.94, half_w * 0.94, 3.0, 7.6,
             liv["body"], top_rgb=STEEL_DARK)
    for wx in (ten_x0 + 1.2, ten_x1 - 1.6):
        q += box(wx - 0.5, wx + 0.5, -half_w * 0.8, half_w * 0.8, 0.0, 1.5, WHEEL)
    q += side_decal(ten_x0 + 0.6, ten_x1 - 0.6, 5.1, 5.6, half_w * 0.94,
                    liv["stripes"][0][0] if liv["stripes"] else PRR_GOLD,
                    layer=L_STRIPE)

    # headlight and pilot
    q += end_decal(eng_x1, 1, -half_w * 0.26, half_w * 0.26, 7.6, 8.3,
                   HEADLIGHT, flat=True, layer=L_LIGHT)
    q += box(eng_x1 - 0.4, eng_x1 + 0.0, -half_w * 0.8, half_w * 0.8,
             2.4, 3.8, STEEL_DARK)
    return q


# ------------------------------------------------------- diesel carbodies --

def hood_unit(length, half_w, liv, cab_frac=0.62, short_hood=True,
              hep_stack=False):
    """Road switcher: walkway frame, short hood, cab, long hood."""
    hl = length / 2.0
    q = []
    q += running_gear(length, half_w, truck_z=2.6, inset=2.5)
    q += box(-hl, hl, -half_w, half_w, 2.4, 3.3, STEEL_DARK)          # frame
    q += box(-hl + 1.4, hl - 1.4, -half_w * 0.8, half_w * 0.8,
             1.9, 2.5, UNDER)                                          # tank

    cab_x1 = -hl + length * cab_frac
    cab_x0 = cab_x1 - 2.9
    # long hood behind the cab
    q += box(-hl + 0.5, cab_x0, -half_w * 0.86, half_w * 0.86, 3.3, 8.4,
             liv["body"], top_rgb=liv["roof"])
    # cab
    q += box(cab_x0, cab_x1, -half_w * 0.94, half_w * 0.94, 3.3, 9.6,
             liv["body"], top_rgb=liv["roof"])
    q += side_decal(cab_x0 + 0.35, cab_x1 - 0.35, 7.3, 8.9, half_w * 0.94,
                    GLASS_DARK, layer=L_WINDOW)
    # short hood ahead of it
    if short_hood:
        q += box(cab_x1, hl - 0.5, -half_w * 0.86, half_w * 0.86, 3.3, 7.9,
                 liv["body"], top_rgb=liv["roof"])
        q += end_decal(hl - 0.5, 1, -half_w * 0.6, half_w * 0.6, 7.1, 7.7,
                       GLASS_DARK, layer=L_WINDOW)
    if hep_stack:
        q += box(-hl + 2.0, -hl + 3.4, -half_w * 0.5, half_w * 0.5,
                 8.4, 8.9, STEEL_DARK)
        q += box(cab_x0 - 3.2, cab_x0 - 1.0, -half_w * 0.55, half_w * 0.55,
                 8.4, 8.8, STEEL_DARK)

    q += band_and_stripes(-hl + 0.6, hl - 0.6, half_w * 0.86, liv, 4.2,
                          band_z0=5.4, band_z1=7.6)
    for sgn in (1, -1):
        q += end_decal(sgn * (hl - 0.5), sgn, -half_w * 0.62, -half_w * 0.26,
                       5.9, 6.5, HEADLIGHT, flat=True, layer=L_LIGHT)
        q += end_decal(sgn * (hl - 0.5), sgn, half_w * 0.26, half_w * 0.62,
                       5.9, 6.5, HEADLIGHT, flat=True, layer=L_LIGHT)
    return q


def cab_unit(length, half_w, liv):
    """Streamlined E-unit: full carbody with a sloped bulldog nose."""
    hl = length / 2.0
    q = []
    q += running_gear(length, half_w, truck_z=2.6, inset=2.6)
    q += box(-hl, hl - 2.6, -half_w, half_w, 2.6, 9.6, liv["body"],
             top_rgb=liv["roof"])
    # nose in three slices, each shorter and narrower than the last
    slices = [(hl - 2.6, hl - 1.7, 9.0, 0.98), (hl - 1.7, hl - 0.9, 8.1, 0.90),
              (hl - 0.9, hl - 0.2, 7.0, 0.78)]
    for x0, x1, top, w in slices:
        q += box(x0, x1, -half_w * w, half_w * w, 2.6, top, liv["body"],
                 top_rgb=shade(liv["body"], 0.88))
    q += box(-hl, hl - 2.4, -half_w * 0.9, half_w * 0.9, 9.6, 10.1,
             liv["roof"], top_rgb=liv["roof"])
    # windshield, portholes, headlight
    q += end_decal(hl - 0.9, 1, -half_w * 0.62, half_w * 0.62, 7.6, 8.7,
                   GLASS_DARK, layer=L_WINDOW)
    q += side_decal(hl - 3.4, hl - 2.0, 7.4, 8.8, half_w, GLASS_DARK,
                    layer=L_WINDOW)
    for i in range(4):
        cx = -hl + 2.4 + i * 2.4
        q += side_decal(cx - 0.42, cx + 0.42, 7.3, 8.2, half_w, GLASS,
                        layer=L_WINDOW)
    q += end_decal(hl - 0.2, 1, -half_w * 0.22, half_w * 0.22, 8.8, 9.4,
                   HEADLIGHT, flat=True, layer=L_LIGHT)
    q += band_and_stripes(-hl + 0.4, hl - 0.4, half_w, liv, 4.4,
                          band_z0=5.6, band_z1=8.9)
    return q


def gg1_body(length, half_w, liv):
    """Streamlined double-ended electric: centre cab, tapered hoods."""
    hl = length / 2.0
    q = []
    for sgn in (-1, 1):
        cx = sgn * (hl - 3.0)
        q += box(cx - 1.6, cx + 1.6, -half_w * 0.86, half_w * 0.86, 0.6, 2.9, BOGIE)
        for wx in (cx - 1.2, cx + 0.2):
            q += box(wx, wx + 1.0, -half_w, half_w, 0.0, 1.5, WHEEL)
    q += box(-hl + 1.6, hl - 1.6, -half_w * 0.92, half_w * 0.92, 2.4, 3.2, STEEL_DARK)

    # tapered ends, then the raised centre cab
    for sgn in (-1, 1):
        for i, (a, b, top, w) in enumerate([(hl - 0.2, hl - 1.4, 6.4, 0.66),
                                            (hl - 1.4, hl - 2.6, 7.4, 0.82),
                                            (hl - 2.6, hl - 4.0, 8.2, 0.92)]):
            x0, x1 = sorted((sgn * a, sgn * b))
            q += box(x0, x1, -half_w * w, half_w * w, 3.2, top, liv["body"],
                     top_rgb=liv["body"])
    q += box(-hl + 4.0, hl - 4.0, -half_w, half_w, 3.2, 8.4, liv["body"],
             top_rgb=liv["body"])
    q += box(-2.6, 2.6, -half_w * 0.96, half_w * 0.96, 8.4, 9.9, liv["body"],
             top_rgb=liv["roof"])
    q += side_decal(-2.2, 2.2, 8.7, 9.6, half_w * 0.96, GLASS_DARK, layer=L_WINDOW)
    for sgn in (-1, 1):
        q += side_decal(sgn * 3.0, sgn * (hl - 3.4), 6.9, 7.9, half_w,
                        GLASS, layer=L_WINDOW)
        q += end_decal(sgn * (hl - 0.2), sgn, -half_w * 0.3, half_w * 0.3,
                       5.4, 6.0, HEADLIGHT, flat=True, layer=L_LIGHT)
    q += band_and_stripes(-hl + 0.6, hl - 0.6, half_w, liv, 4.4)
    for cx in (-4.6, 4.6):
        q += pantograph(cx, half_w, 8.4, up=1.3)
    return q


# --------------------------------------------------------- pre-war coaches --

def clerestory_car(length, half_w, liv, cab=0, panto=False, doors=2,
                   windows=8):
    """Arch-roof coach or MU car with a raised clerestory."""
    hl = length / 2.0
    body_z0, body_z1 = 3.1, 8.5
    q = []
    q += running_gear(length, half_w, truck_z=2.5, inset=2.2)
    q += box(-hl + 1.0, hl - 1.0, -half_w * 0.9, half_w * 0.9,
             2.3, body_z0 + 0.2, UNDER)
    q += box(-hl, hl, -half_w, half_w, body_z0, body_z1, liv["body"],
             top_rgb=liv["body"])
    # arched roof, then the clerestory ridge on top of it
    q += prism(-hl + 0.2, hl - 0.2, 0.0, body_z1 - 0.5, half_w * 0.98, 1.15,
               liv["roof"], facets=6, a0=-92, a1=92, caps=False,
               top_rgb=shade(liv["roof"], 1.1))
    q += box(-hl + 1.4, hl - 1.4, -half_w * 0.46, half_w * 0.46,
             body_z1 + 0.55, body_z1 + 1.25, liv["roof"],
             top_rgb=shade(liv["roof"], 1.12))
    q += side_decal(-hl + 1.6, hl - 1.6, body_z1 + 0.75, body_z1 + 1.05,
                    half_w * 0.46, GLASS_DARK, layer=L_WINDOW)

    win_x0, win_x1 = -hl + 1.1, hl - 1.1
    if cab > 0:
        win_x1 = hl - 3.0
    elif cab < 0:
        win_x0 = -hl + 3.0
    q += window_row(win_x0, win_x1, body_z1 - 3.1, body_z1 - 1.2, half_w,
                    windows)
    for i in range(doors):
        dx = -hl + 1.5 + (length - 3.0) * (i / max(1, doors - 1)) if doors > 1 else 0.0
        q += side_decal(dx - 0.5, dx + 0.5, body_z0 + 0.2, body_z1 - 1.0,
                        half_w, shade(liv["body"], 0.76), layer=L_DOOR)

    if cab:
        sgn = 1 if cab > 0 else -1
        q += end_decal(sgn * hl, sgn, -half_w * 0.74, half_w * 0.74,
                       body_z1 - 3.1, body_z1 - 1.2, GLASS_DARK, layer=L_WINDOW)
        q += end_decal(sgn * hl, sgn, -half_w * 0.66, -half_w * 0.3,
                       body_z0 + 0.9, body_z0 + 1.5, HEADLIGHT, flat=True,
                       layer=L_LIGHT)
        q += end_decal(sgn * hl, sgn, half_w * 0.3, half_w * 0.66,
                       body_z0 + 0.9, body_z0 + 1.5, HEADLIGHT, flat=True,
                       layer=L_LIGHT)

    q += band_and_stripes(-hl + 0.3, hl - 0.3, half_w, liv, body_z0 + 1.0,
                          band_z0=body_z1 - 3.4, band_z1=body_z1 - 0.9)
    if panto:
        q += pantograph(0.0, half_w, body_z1 + 1.25, up=1.3)
    return q


# ------------------------------------------- flat-roof post-war carbodies --

def flat_roof_car(length, half_w, liv, cab=0, panto=False, corrugated=False,
                  windows=7, powered=False):
    """Comet / Arrow generation: flat roof, wide windows, optional pantograph."""
    hl = length / 2.0
    body_z0, body_z1, roof_z1 = 3.15, 8.7, 9.7
    q = []
    q += running_gear(length, half_w, truck_z=2.55, inset=2.3)
    q += box(-hl + 1.1, hl - 1.1, -half_w * 0.9, half_w * 0.9,
             2.3, body_z0 + 0.2, UNDER)
    q += box(-hl, hl, -half_w, half_w, body_z0, body_z1, liv["body"],
             top_rgb=liv["body"])
    q += box(-hl + 0.3, hl - 0.3, -half_w * 0.87, half_w * 0.87,
             body_z1, roof_z1, liv["roof"], top_rgb=liv["roof"])

    if corrugated:
        z = body_z0 + 0.5
        while z < body_z1 - 0.4:
            q += side_decal(-hl + 0.2, hl - 0.2, z, z + 0.16, half_w,
                            shade(liv["body"], 0.86), layer=L_TEXTURE)
            z += 0.85

    win_x0, win_x1 = -hl + 1.0, hl - 1.0
    if cab > 0:
        win_x1 = hl - 3.1
    elif cab < 0:
        win_x0 = -hl + 3.1
    q += window_row(win_x0, win_x1, body_z1 - 2.75, body_z1 - 0.75, half_w,
                    windows)

    if cab:
        sgn = 1 if cab > 0 else -1
        cz0, cz1 = body_z1 - 2.75, body_z1 - 0.75
        lo, hi = sorted((sgn * hl, sgn * (hl - 2.6)))
        q += side_decal(lo + 0.4, hi - 0.4, cz0, cz1, half_w, GLASS_DARK,
                        layer=L_WINDOW)
        q += end_decal(sgn * hl, sgn, -half_w * 0.76, half_w * 0.76,
                       cz0, cz1, GLASS_DARK, layer=L_WINDOW)
        q += end_decal(sgn * hl, sgn, -half_w * 0.7, -half_w * 0.34,
                       cz0 - 1.5, cz0 - 1.0, HEADLIGHT, flat=True, layer=L_LIGHT)
        q += end_decal(sgn * hl, sgn, half_w * 0.34, half_w * 0.7,
                       cz0 - 1.5, cz0 - 1.0, HEADLIGHT, flat=True, layer=L_LIGHT)

    for sgn in (-1, 1):
        dx = sgn * (hl - 2.0)
        q += side_decal(dx - 0.55, dx + 0.55, body_z0 + 0.2, body_z1 - 0.35,
                        half_w, shade(liv["body"], 0.8), layer=L_DOOR)

    q += band_and_stripes(-hl + 0.25, hl - 0.25, half_w, liv, body_z0 + 1.15,
                          band_z0=body_z1 - 2.95, band_z1=body_z1 - 0.55)
    if panto:
        q += pantograph(0.0, half_w, roof_z1, up=1.3)
    return q


def boxcab_loco(length, half_w, liv, pantos=()):
    """Square-carbody electric (ALP-44 generation) in an arbitrary livery."""
    hl = length / 2.0
    body_z0, body_z1, roof_z1 = 3.05, 9.5, 10.5
    q = []
    q += running_gear(length, half_w, truck_z=2.5, inset=2.4)
    q += box(-hl + 1.3, hl - 1.3, -half_w * 0.92, half_w * 0.92,
             2.2, body_z0 + 0.25, UNDER)
    q += box(-hl, hl, -half_w, half_w, body_z0, body_z1, liv["body"],
             top_rgb=liv["body"])
    q += box(-hl + 0.35, hl - 0.35, -half_w * 0.86, half_w * 0.86,
             body_z1, roof_z1, liv["roof"], top_rgb=liv["roof"])
    win_z0, win_z1 = body_z1 - 2.55, body_z1 - 0.55
    for sgn in (1, -1):
        lo, hi = sorted((sgn * hl, sgn * (hl - 2.3)))
        q += side_decal(lo + 0.35, hi - 0.35, win_z0, win_z1, half_w,
                        GLASS_DARK, layer=L_WINDOW)
        q += end_decal(sgn * hl, sgn, -half_w * 0.74, half_w * 0.74,
                       win_z0, win_z1, GLASS_DARK, layer=L_WINDOW)
        q += end_decal(sgn * hl, sgn, -half_w * 0.72, -half_w * 0.36,
                       win_z1 + 0.35, win_z1 + 0.85, HEADLIGHT, flat=True,
                       layer=L_LIGHT)
        q += end_decal(sgn * hl, sgn, half_w * 0.36, half_w * 0.72,
                       win_z1 + 0.35, win_z1 + 0.85, HEADLIGHT, flat=True,
                       layer=L_LIGHT)
    q += band_and_stripes(-hl + 0.3, hl - 0.3, half_w, liv, body_z0 + 1.4)
    for cx in pantos:
        q += pantograph(cx, half_w, roof_z1)
    return q


# ------------------------------------------------------------- the roster --

HW = 1.75          # same body half-width as the modern stock
CAR = 14.5


def models():
    return {
        "hist_k4s":       lambda: steam_loco(CAR, HW, LIV["prr_green"]),
        "hist_e8":        lambda: cab_unit(13.6, HW, LIV["el_grey"]),
        "hist_rs3":       lambda: hood_unit(11.0, HW, LIV["cnj"]),
        "hist_u34ch":     lambda: hood_unit(13.0, HW, LIV["bluebird"],
                                            hep_stack=True),
        "hist_gg1":       lambda: gg1_body(CAR, HW, LIV["prr_tuscan"]),
        "hist_alp44":     lambda: boxcab_loco(11.0, HW, LIV["chevron"],
                                              pantos=(-2.4, 2.4)),
        "hist_mp54":      lambda: clerestory_car(11.0, HW, LIV["prr_tuscan"],
                                                 panto=True, windows=8),
        "hist_dlwmu":     lambda: clerestory_car(12.2, HW, LIV["dlw"],
                                                 panto=True, windows=9),
        "hist_stillwell": lambda: clerestory_car(10.5, HW, LIV["erie"],
                                                 windows=9),
        "hist_arrow1":    lambda: flat_roof_car(CAR, HW, LIV["stainless"],
                                                cab=1, panto=True,
                                                corrugated=True),
        "hist_arrow2_a":  lambda: flat_roof_car(CAR, HW, LIV["chevron"],
                                                cab=1, panto=True,
                                                corrugated=True),
        "hist_arrow2_b":  lambda: flat_roof_car(CAR, HW, LIV["chevron"],
                                                cab=-1, panto=True,
                                                corrugated=True),
        "hist_comet1":    lambda: flat_roof_car(CAR, HW, LIV["comet1"]),
        "hist_comet1_cab": lambda: flat_roof_car(CAR, HW, LIV["comet1"], cab=1),
        "hist_comet2":    lambda: flat_roof_car(CAR, HW, LIV["chevron"]),
    }
