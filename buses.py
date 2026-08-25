#!/usr/bin/env python3
"""
Model builders for NJ TRANSIT Bus Operations, in their own liveries.

Imported by gen_sprites.py and built from the same box/decal/quad primitives
as the trains. What differs is underneath: a bus rides on two or three axles
rather than a pair of bogies, its floor sits a foot above the road instead of
four feet above the rail, and it is 8 ft 6 in wide against a rail car's
10 ft 6. Those three numbers are most of what makes a bus read as a bus at
52 px, before any livery goes on.

One primitive is new here: strut(), a thin sloping slab in the x-z plane,
used for the trolley poles laid back along the All-Service Vehicle's roof.
box() is axis-aligned and cannot lean.
"""

from gen_sprites import (
    Quad, box, side_decal, end_decal, top_decal, window_row, shade,
    GLASS, GLASS_DARK, HEADLIGHT, UNDER, WHEEL, AC_UNIT, PANTO,
    NJT_BLUE, NJT_ORANGE,
    L_SOLID, L_TEXTURE, L_DOOR, L_STRIPE, L_WINDOW, L_LIGHT,
)
from historic import CHEVRON_ORANGE, CHEVRON_RED, CHEVRON_BLUE

# ------------------------------------------------------------------ liveries --

PS_GREY    = (134, 140, 147)     # Public Service grey, as the PCC cars wore it
PS_BLUE    = (34, 60, 118)
PS_CREAM   = (206, 202, 186)
TNJ_WHITE  = (224, 227, 230)
NJT_WHITE  = (232, 235, 238)
NJT_SILVER = (204, 210, 216)
BUS_ROOF   = (180, 185, 191)     # bus roofs are painted, not weathered steel
DARK_ROOF  = (120, 126, 132)
TAIL_RED   = (176, 38, 34)
SIGN       = (26, 28, 32)        # destination sign box
MASK       = (42, 46, 52)        # dark glazing band on the modern low-floors
TYRE       = WHEEL


def livery(body, roof, stripes=(), skirt=None, window=GLASS, mask=None):
    """stripes: [(colour, height)] stacked downward from the belt line.
    skirt:  colour of the panel below the stripes, None to leave it body colour.
    mask:   a dark band wrapping the body at window height, as the modern
            low-floor buses carry."""
    return dict(body=body, roof=roof, stripes=list(stripes), skirt=skirt,
                window=window, mask=mask)


# The orange / red / blue trio is the same one the Comet IIs and Arrow IIIs
# wear on the rail side. It reached NJ TRANSIT the other way round from what
# the dates suggest: the colours appeared on Transport of New Jersey buses in
# the seventies, and NJ TRANSIT, which took over TNJ first, kept them.
LIV = {
    "public_service": livery(PS_GREY, PS_CREAM, stripes=[(PS_BLUE, 0.95)],
                             skirt=PS_BLUE),
    "tnj":            livery(TNJ_WHITE, BUS_ROOF,
                             stripes=[(CHEVRON_ORANGE, 0.34),
                                      (CHEVRON_RED, 0.24),
                                      (CHEVRON_BLUE, 0.24)]),
    "chevron":        livery(NJT_WHITE, BUS_ROOF,
                             stripes=[(CHEVRON_ORANGE, 0.36),
                                      (CHEVRON_RED, 0.26),
                                      (CHEVRON_BLUE, 0.26)]),
    "modern":         livery(NJT_WHITE, BUS_ROOF,
                             stripes=[(NJT_ORANGE, 0.32)],
                             skirt=NJT_BLUE, mask=MASK),
    "modern_silver":  livery(NJT_SILVER, BUS_ROOF,
                             stripes=[(NJT_ORANGE, 0.32)],
                             skirt=NJT_BLUE, mask=MASK),
}


# ----------------------------------------------------------- new primitive --

def strut(x0, z0, x1, z1, y, thick, rgb, layer=L_WINDOW):
    """A thin sloping slab in the x-z plane at a fixed y, faced both ways so
    it stays visible whichever side of the vehicle the camera is on."""
    pts = [(x0, y, z0), (x1, y, z1), (x1, y, z1 + thick), (x0, y, z0 + thick)]
    return [Quad(pts, rgb, (0, 1, 0), layer=layer),
            Quad(pts, rgb, (0, -1, 0), layer=layer)]


def axle_set(xs, half_w, top=1.45, width=1.0):
    """Wheels at the given x positions - a bus has axles, not bogies. The
    tyres are drawn slightly proud of the body so they read against the
    skirt above them."""
    q = []
    y_in, y_out = half_w * 0.52, half_w + 0.07
    for x in xs:
        for lo, hi in ((y_in, y_out), (-y_out, -y_in)):
            q += box(x - width / 2.0, x + width / 2.0, lo, hi, 0.0, top, TYRE)
    return q


# ----------------------------------------------------------------- the bus --

def bus_body(length, half_w, liv, doors=(0.76, -0.04), windows=6, axles=None,
             coach=False, artic=None, ribs=False, roof_pods=(), poles=False,
             wrap_screen=0.0, sign=True, band=None):
    """One transit bus or highway coach.

    doors        x positions of the doorways as fractions of the half length,
                 positive towards the front (+x). A city bus has two, a
                 highway coach one.
    windows      number of passenger window bays to fit between the doors.
    coach        high floor over baggage lockers, tall tinted glass, one door.
    artic        None, "front" or "rear": which half of an articulated bus
                 this is. The joint end gets bellows instead of a face.
    ribs         horizontal corrugation, as on the RTS.
    roof_pods    [(x0, x1, height, colour)] as fractions of the half length -
                 air conditioning, battery packs, roof hatches.
    poles        trolley poles laid back along the roof (the ASV).
    wrap_screen  how far the windscreen glass wraps around the front corners,
                 as a fraction of the half length. The fishbowl's six-piece
                 curved screen is most of what identifies it.
    band         (z0, z1) to override the window band, for the pre-war stock
                 whose windows are shorter and set higher than a modern bus's.
    """
    hl = length / 2.0
    if coach:
        wheel_z = 1.60
        skirt_z0, body_z0, body_z1, roof_z1 = 1.25, 3.05, 7.90, 8.22
        band_z0, band_z1 = 5.20, 7.40
        axle_w = 1.05
    else:
        wheel_z = 1.45
        skirt_z0, body_z0, body_z1, roof_z1 = 1.10, 2.05, 6.95, 7.28
        band_z0, band_z1 = 4.30, 6.45
        axle_w = 1.00
    if band:
        band_z0, band_z1 = band

    if axles is None:
        axles = (0.72, -0.62)
    q = axle_set([f * hl for f in axles], half_w, top=wheel_z, width=axle_w)

    # skirt / underframe: on a coach this is the baggage locker line, and it
    # runs the full width because that is what you see of it from the side
    q += box(-hl + 0.15, hl - 0.15, -half_w * 0.94, half_w * 0.94,
             skirt_z0, body_z0 + 0.2, UNDER)
    q += box(-hl, hl, -half_w, half_w, body_z0, body_z1, liv["body"],
             top_rgb=liv["body"])
    q += box(-hl + 0.12, hl - 0.12, -half_w * 0.90, half_w * 0.90,
             body_z1, roof_z1, liv["roof"], top_rgb=liv["roof"])

    for x0, x1, h, rgb in roof_pods:
        q += box(x0 * hl, x1 * hl, -half_w * 0.52, half_w * 0.52,
                 roof_z1, roof_z1 + h, rgb)

    # which ends are real faces and which are a bellows into the other half
    front = artic != "rear"
    rear = artic != "front"

    if ribs:
        z = body_z0 + 0.45
        while z < band_z0 - 0.5:
            q += side_decal(-hl + 0.2, hl - 0.2, z, z + 0.14, half_w,
                            shade(liv["body"], 0.87), layer=L_TEXTURE)
            z += 0.62

    # the glazing mask, where the livery has one, wraps the body at window
    # height and the windows are then cut out of it
    if liv["mask"]:
        q += side_decal(-hl + 0.16, hl - 0.16, band_z0, band_z1, half_w,
                        liv["mask"], layer=L_TEXTURE)
        if front:
            q += end_decal(hl, 1, -half_w * 0.94, half_w * 0.94,
                           band_z0, band_z1, liv["mask"], layer=L_TEXTURE)
        if rear:
            q += end_decal(-hl, -1, -half_w * 0.94, half_w * 0.94,
                           band_z0, band_z1, liv["mask"], layer=L_TEXTURE)

    # ------------------------------------------------------------- livery --
    belt = band_z0 - 0.22
    if liv["skirt"]:
        q += side_decal(-hl + 0.18, hl - 0.18, body_z0 + 0.12, belt, half_w,
                        liv["skirt"], layer=L_TEXTURE)
    z = belt
    for rgb, h in liv["stripes"]:
        q += side_decal(-hl + 0.18, hl - 0.18, z - h, z, half_w, rgb,
                        layer=L_STRIPE)
        for sgn, on in ((1, front), (-1, rear)):
            if on:
                q += end_decal(sgn * hl, sgn, -half_w * 0.92, half_w * 0.92,
                               z - h, z, rgb, layer=L_STRIPE)
        z -= h + 0.07

    # ------------------------------------------------------------ glazing --
    door_x = [f * hl for f in doors]
    door_hw = 0.30 * (length / 6.8)          # a 3 ft doorway at this scale
    for dx in door_x:
        q += side_decal(dx - door_hw, dx + door_hw, body_z0 + 0.12,
                        band_z1 - 0.10, half_w, shade(liv["body"], 0.74),
                        layer=L_DOOR)
        q += side_decal(dx - door_hw + 0.06, dx + door_hw - 0.06,
                        band_z0 + 0.12, band_z1 - 0.22, half_w,
                        liv["window"], layer=L_WINDOW)

    # passenger windows fill whatever the doors and the cab leave
    win_x0 = -hl + (0.85 if rear else 0.25)
    win_x1 = hl - (2.05 if front else 0.25)
    blocked = sorted((dx - door_hw - 0.16, dx + door_hw + 0.16)
                     for dx in door_x)
    edges = [win_x0]
    for a, b in blocked:
        if win_x0 < b and a < win_x1:
            edges += [max(a, win_x0), min(b, win_x1)]
    edges.append(win_x1)
    bays = [(a, b) for a, b in zip(edges[0::2], edges[1::2]) if b - a > 0.5]
    span = sum(b - a for a, b in bays) or 1.0
    for a, b in bays:
        n = max(1, int(round(windows * (b - a) / span)))
        q += window_row(a, b, band_z0 + 0.16, band_z1 - 0.22, half_w, n,
                        rgb=liv["window"], pillar=0.24)

    if front:
        # windscreen: the front face, plus however far it wraps around the
        # corners onto the sides
        screen_z1 = band_z1 - (0.50 if sign else 0.10)
        q += end_decal(hl, 1, -half_w * 0.86, half_w * 0.86,
                       band_z0 + 0.05, screen_z1, GLASS_DARK, layer=L_WINDOW)
        if wrap_screen:
            q += side_decal(hl - wrap_screen * hl, hl - 0.12,
                            band_z0 + 0.10, screen_z1, half_w,
                            GLASS_DARK, layer=L_WINDOW)
        # driver's window and the cab door pillar behind the screen
        q += side_decal(hl - 1.95, hl - 0.95, band_z0 + 0.14, band_z1 - 0.20,
                        half_w, GLASS_DARK, layer=L_WINDOW)
        if sign:
            # the roller sign reads across the fascia above the screen
            q += end_decal(hl, 1, -half_w * 0.78, half_w * 0.78,
                           screen_z1 + 0.08, band_z1 + 0.02, SIGN,
                           layer=L_WINDOW)
            q += side_decal(hl - 2.15, hl - 1.05, screen_z1 + 0.08,
                            band_z1 + 0.02, half_w, SIGN, layer=L_WINDOW)
        q += end_decal(hl, 1, -half_w * 0.74, -half_w * 0.36,
                       body_z0 + 0.45, body_z0 + 0.95, HEADLIGHT, flat=True,
                       layer=L_LIGHT)
        q += end_decal(hl, 1, half_w * 0.36, half_w * 0.74,
                       body_z0 + 0.45, body_z0 + 0.95, HEADLIGHT, flat=True,
                       layer=L_LIGHT)
    if rear:
        q += end_decal(-hl, -1, -half_w * 0.72, half_w * 0.72,
                       band_z0 + 0.25, band_z1 - 0.05, GLASS_DARK,
                       layer=L_WINDOW)
        q += end_decal(-hl, -1, -half_w * 0.76, -half_w * 0.40,
                       body_z0 + 0.45, body_z0 + 0.95, TAIL_RED, flat=True,
                       layer=L_LIGHT)
        q += end_decal(-hl, -1, half_w * 0.40, half_w * 0.76,
                       body_z0 + 0.45, body_z0 + 0.95, TAIL_RED, flat=True,
                       layer=L_LIGHT)

    # bellows on whichever end runs into the other half of an artic
    if artic:
        sgn = -1 if artic == "front" else 1
        q += end_decal(sgn * hl, sgn, -half_w * 0.96, half_w * 0.96,
                       body_z0, body_z1, shade(MASK, 1.0), layer=L_TEXTURE)
        q += side_decal(sgn * hl - 0.22, sgn * hl + 0.22, body_z0, body_z1,
                        half_w, MASK, layer=L_WINDOW)
        q += top_decal(sgn * hl - 0.22, sgn * hl + 0.22,
                       -half_w * 0.90, half_w * 0.90, roof_z1, MASK)

    if poles:
        base = -0.30 * hl
        q += box(base - 0.35, base + 0.35, -half_w * 0.34, half_w * 0.34,
                 roof_z1, roof_z1 + 0.22, PANTO)
        for y in (-half_w * 0.22, half_w * 0.22):
            q += strut(base, roof_z1 + 0.20, base - 0.62 * hl,
                       roof_z1 + 1.15, y, 0.20, PANTO)
    return q


# ------------------------------------------------------------- the roster --

HW = 1.42          # 8 ft 6 in over the body
FT = 0.17          # model units per foot: the same ~2x working scale as the
                   # trains, brought down by gen_sprites.scale_to_length()

AC = (0.10, 0.62, 0.30, AC_UNIT)
HATCH = (-0.30, 0.05, 0.16, DARK_ROOF)


def models():
    return {
        # Public Service and Transport of New Jersey
        "bus_asv":      lambda: bus_body(33 * FT, HW, LIV["public_service"],
                                         doors=(0.68,), windows=7,
                                         axles=(0.70, -0.66), poles=True,
                                         sign=False, band=(4.75, 6.35)),
        "bus_newlook":  lambda: bus_body(40 * FT, HW, LIV["tnj"],
                                         doors=(0.74, -0.06), windows=6,
                                         wrap_screen=0.14,
                                         roof_pods=[HATCH]),
        # early NJ TRANSIT
        "bus_flx870":   lambda: bus_body(40 * FT, HW, LIV["chevron"],
                                         doors=(0.74, -0.02), windows=6,
                                         roof_pods=[HATCH]),
        "bus_mc9":      lambda: bus_body(45 * FT, HW, LIV["chevron"],
                                         doors=(0.66,), windows=9, coach=True,
                                         axles=(0.74, -0.44, -0.70),
                                         roof_pods=[AC]),
        "bus_b10m_a":   lambda: bus_body(38 * FT, HW, LIV["chevron"],
                                         doors=(0.74, -0.10), windows=5,
                                         axles=(0.72, -0.50), artic="front"),
        "bus_b10m_b":   lambda: bus_body(22 * FT, HW, LIV["chevron"],
                                         doors=(0.10,), windows=3,
                                         axles=(-0.45,), artic="rear"),
        "bus_metrob":   lambda: bus_body(40 * FT, HW, LIV["chevron"],
                                         doors=(0.74, -0.02), windows=6,
                                         roof_pods=[AC]),
        # modern NJ TRANSIT
        "bus_rts06":    lambda: bus_body(40 * FT, HW, LIV["modern_silver"],
                                         doors=(0.74, -0.02), windows=6,
                                         ribs=True, roof_pods=[AC]),
        "bus_nabi416":  lambda: bus_body(40 * FT, HW, LIV["modern"],
                                         doors=(0.74, -0.02), windows=6,
                                         roof_pods=[AC]),
        "bus_d4500ct":  lambda: bus_body(45 * FT, HW, LIV["modern"],
                                         doors=(0.66,), windows=9, coach=True,
                                         axles=(0.74, -0.44, -0.70),
                                         roof_pods=[AC]),
        "bus_xd60_a":   lambda: bus_body(38 * FT, HW, LIV["modern"],
                                         doors=(0.74, -0.10), windows=5,
                                         axles=(0.72, -0.50), artic="front",
                                         roof_pods=[AC]),
        "bus_xd60_b":   lambda: bus_body(22 * FT, HW, LIV["modern"],
                                         doors=(0.10,), windows=3,
                                         axles=(-0.45,), artic="rear"),
        # batteries where the engine used to be, and a roof full of them
        "bus_xe40":     lambda: bus_body(40 * FT, HW, LIV["modern"],
                                         doors=(0.74, -0.02), windows=6,
                                         roof_pods=[(-0.62, -0.05, 0.34,
                                                     DARK_ROOF),
                                                    (0.10, 0.60, 0.34,
                                                     DARK_ROOF)]),
    }
