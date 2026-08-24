#!/usr/bin/env python3
"""
The fleet table: one source of truth for every vehicle in the set.

Each entry carries two stat sets:

  real  published prototype figures (horsepower at rail, tonnes, service speed,
        seated capacity for commuter rail / loaded capacity for rapid transit)

  bal   game-balanced figures, derived from `real` by four rules:
          capacity  ~x0.40, so a full-length car lands near OpenTTD's own
                    40-passenger carriage instead of tripling it
          power     ~x0.45, so the strongest electric is ~3,400 hp rather than
                    7,500 and does not outclass everything in the base set
          weight    trailers ~x0.60, locomotives ~x0.90 (heavy enough to keep
                    their tractive effort useful, light enough to accelerate)
          speed     shaped into an era progression, 50 -> 110 mph, instead of
                    a flat 100 mph across thirty years of equipment
        Purchase and running costs are then re-struck so cost per seat and per
        horsepower stay comparable across the set.

Tractive effort coefficients, air drag, lengths, dates and liveries are the
same in both modes: those are facts about the vehicle, not balance knobs.

Two different notions of "length" appear together on every entry:

  length     the NML length property: room reserved in a consist, in eighths
             of a tile (OpenTTD's VEHICLE_LENGTH). An integer 1-8, and a fact
             about how the vehicle occupies track, not a balance knob either.

  length_ft  published prototype length over couplers, in feet. gen_sprites.py
             draws each vehicle to this figure (scaled, and capped at what
             `length` allows) so a stubby 51 ft engine reads as visibly
             shorter than an 85 ft coach even when both carry the same NML
             `length` - which they often do, since two very differently sized
             prototypes can round to the same eighth-of-a-tile bucket.
"""

# --------------------------------------------------------------- NJ TRANSIT --

VEHICLES = [
    dict(
        nml="alp46", sprite="njt_alp46", name="ALP-46",
        role="Bombardier electric, 2002 · 29 built",
        intro=(2002, 3, 1), length_ft=65, length=7, track="ELRL",
        engine_class="ENGINE_CLASS_ELECTRIC", effect="VISUAL_EFFECT_ELECTRIC",
        run_base="RUNNING_COST_ELECTRIC", te=0.35, drag=0.06,
        flags=["TRAIN_FLAG_FLIP"],
        real=dict(speed=100, power=7100, weight=91, cap=0, cost=205, run=88,
                  model_life=40, life=30, decay=18),
        bal=dict(speed=95, power=3000, weight=84, cap=0, cost=135, run=62,
                 model_life=40, life=30, decay=18),
        purchase="{BLACK}Bombardier, 2001-2002. 29 built.{}TRAXX-family 25 kV / 12 kV "
                 "electric for Midtown Direct services. 7,100 hp at rail, 71,000 lbf "
                 "starting tractive effort.{}{GOLD}Electrified track only.",
    ),
    dict(
        nml="alp46a", sprite="njt_alp46a", name="ALP-46A",
        role="Bombardier electric, 2011 · 36 built",
        intro=(2011, 5, 7), length_ft=65, length=7, track="ELRL",
        engine_class="ENGINE_CLASS_ELECTRIC", effect="VISUAL_EFFECT_ELECTRIC",
        run_base="RUNNING_COST_ELECTRIC", te=0.35, drag=0.06,
        flags=["TRAIN_FLAG_FLIP"],
        real=dict(speed=100, power=7500, weight=92, cap=0, cost=228, run=92,
                  model_life=45, life=30, decay=15),
        bal=dict(speed=110, power=3400, weight=84, cap=0, cost=158, run=66,
                 model_life=45, life=30, decay=15),
        purchase="{BLACK}Bombardier, 2009-2011. 36 built.{}Uprated ALP-46 with 7,500 hp "
                 "at rail and a 125 mph capable body, held to 100 mph in NJ TRANSIT "
                 "service.{}{GOLD}Electrified track only.",
    ),
    dict(
        nml="alp45dp", sprite="njt_alp45dp", name="ALP-45DP",
        role="Bombardier dual-power, 2012",
        intro=(2012, 4, 1), length_ft=71.5, length=8, track="RAIL",
        engine_class="ENGINE_CLASS_DIESEL", effect="VISUAL_EFFECT_DIESEL",
        run_base="RUNNING_COST_DIESEL", te=0.23, drag=0.07,
        flags=["TRAIN_FLAG_FLIP"],
        dual=dict(real=(5360, 3600), bal=(2600, 1800)),
        real=dict(speed=100, power=5360, weight=130, cap=0, cost=250, run=120,
                  model_life=45, life=30, decay=20),
        bal=dict(speed=100, power=2600, weight=98, cap=0, cost=175, run=86,
                 model_life=45, life=30, decay=20),
        purchase="{BLACK}Bombardier, 2011-2012. Dual-power.{}5,360 hp under the wires, "
                 "3,600 hp on its two Caterpillar diesels, so it can run Hoboken "
                 "services straight through to New York.{}{GOLD}Full power on "
                 "electrified track, reduced power elsewhere.",
    ),
    dict(
        nml="pl42ac", sprite="njt_pl42ac", name="PL42AC",
        role="Alstom / EMD diesel, 2006 · 33 built",
        intro=(2006, 1, 1), length_ft=69.8, length=8, track="RAIL",
        engine_class="ENGINE_CLASS_DIESEL", effect="VISUAL_EFFECT_DIESEL",
        run_base="RUNNING_COST_DIESEL", te=0.24, drag=0.07,
        flags=["TRAIN_FLAG_FLIP"],
        real=dict(speed=100, power=4200, weight=130, cap=0, cost=188, run=112,
                  model_life=40, life=30, decay=22),
        bal=dict(speed=90, power=2000, weight=96, cap=0, cost=128, run=78,
                 model_life=40, life=30, decay=22),
        purchase="{BLACK}Alstom / EMD, 2003-2006. 33 built.{}EMD 16-710G3B-T1 rated "
                 "4,200 hp, AC traction, head-end power for the coaches behind it.",
    ),

    # Arrow III married pair: the A car pulls in a hidden B car as an
    # articulated part, so the cabs face outwards at both ends.
    dict(
        nml="arrow3_b", sprite="njt_arrow3_b", name="Arrow III EMU",
        hidden=True,
        intro=(1978, 1, 1), length_ft=85, length=8, track="ELRL",
        engine_class="ENGINE_CLASS_ELECTRIC", effect=None,
        run_base="RUNNING_COST_ELECTRIC", te=0.30, drag=0.05,
        flags=["TRAIN_FLAG_MU"],
        real=dict(speed=100, power=0, weight=57, cap=120, cost=0, run=0,
                  model_life="VEHICLE_NEVER_EXPIRES", life=45, decay=20),
        bal=dict(speed=80, power=0, weight=34, cap=46, cost=0, run=0,
                 model_life="VEHICLE_NEVER_EXPIRES", life=45, decay=20),
    ),
    dict(
        nml="arrow3_a", sprite="njt_arrow3_a", name="Arrow III EMU",
        role="General Electric married pair, 1978",
        intro=(1978, 1, 1), length_ft=85, length=8, track="ELRL",
        engine_class="ENGINE_CLASS_ELECTRIC", effect="VISUAL_EFFECT_ELECTRIC",
        run_base="RUNNING_COST_ELECTRIC", te=0.30, drag=0.05,
        flags=["TRAIN_FLAG_MU"], artic="arrow3_b", pair=True,
        real=dict(speed=100, power=1125, weight=57, cap=120, cost=118, run=52,
                  model_life=42, life=45, decay=20),
        bal=dict(speed=80, power=900, weight=34, cap=46, cost=72, run=30,
                 model_life=42, life=45, decay=20),
        purchase="{BLACK}General Electric, 1977-1978.{}Self-propelled electric married "
                 "pair, the backbone of NJ TRANSIT electric service for over forty "
                 "years. Buying one gives you both cars.{}{GOLD}Electrified track only.",
    ),

    dict(
        nml="comet5", sprite="njt_comet5", name="Comet V Coach",
        role="Alstom trailer, 2003",
        intro=(2003, 1, 1), length_ft=85, length=8, track="RAIL",
        engine_class=None, effect=None,
        run_base="RUNNING_COST_DIESEL", te=0.30, drag=0.05,
        flags=["TRAIN_FLAG_FLIP"],
        real=dict(speed=100, power=0, weight=46, cap=117, cost=62, run=26,
                  model_life=40, life=40, decay=20),
        bal=dict(speed=110, power=0, weight=28, cap=42, cost=34, run=13,
                 model_life=40, life=40, decay=20),
        purchase="{BLACK}Alstom, 2002-2004.{}Stainless steel single-level commuter "
                 "coach, 85 ft over couplers.",
    ),
    dict(
        nml="comet5_cab", sprite="njt_comet5_cab", name="Comet V Cab Car",
        role="Alstom push-pull cab, 2003",
        intro=(2003, 1, 1), length_ft=85, length=8, track="RAIL",
        engine_class=None, effect=None,
        run_base="RUNNING_COST_DIESEL", te=0.30, drag=0.05,
        flags=["TRAIN_FLAG_FLIP"],
        real=dict(speed=100, power=0, weight=47, cap=109, cost=70, run=28,
                  model_life=40, life=40, decay=20),
        bal=dict(speed=110, power=0, weight=29, cap=38, cost=38, run=14,
                 model_life=40, life=40, decay=20),
        purchase="{BLACK}Alstom, 2002-2004.{}Comet V with an operating cab for "
                 "push-pull service. Use CTRL+click in the depot to turn it around.",
    ),
    dict(
        nml="multilevel", sprite="njt_ml", name="MultiLevel Coach",
        role="Bombardier trailer, 2006",
        intro=(2006, 9, 1), length_ft=85, length=8, track="RAIL",
        engine_class=None, effect=None,
        run_base="RUNNING_COST_DIESEL", te=0.30, drag=0.05,
        flags=["TRAIN_FLAG_FLIP"], loading=18,
        real=dict(speed=100, power=0, weight=61, cap=132, cost=86, run=32,
                  model_life=45, life=40, decay=18),
        bal=dict(speed=110, power=0, weight=36, cap=55, cost=48, run=17,
                 model_life=45, life=40, decay=18),
        purchase="{BLACK}Bombardier, 2006-2009.{}MultiLevel trailer. Two seating decks "
                 "inside the same clearance envelope, the highest capacity car "
                 "NJ TRANSIT runs.",
    ),
    dict(
        nml="multilevel_cab", sprite="njt_ml_cab", name="MultiLevel Cab Car",
        role="Bombardier push-pull cab, 2006",
        intro=(2006, 9, 1), length_ft=85, length=8, track="RAIL",
        engine_class=None, effect=None,
        run_base="RUNNING_COST_DIESEL", te=0.30, drag=0.05,
        flags=["TRAIN_FLAG_FLIP"], loading=18,
        real=dict(speed=100, power=0, weight=63, cap=127, cost=94, run=34,
                  model_life=45, life=40, decay=18),
        bal=dict(speed=110, power=0, weight=37, cap=52, cost=52, run=18,
                 model_life=45, life=40, decay=18),
        purchase="{BLACK}Bombardier, 2006-2009.{}MultiLevel cab car for push-pull "
                 "service. Use CTRL+click in the depot to turn it around.",
    ),

    # ------------------------------------------------------------------ PATH --
    # Every PATH class is bought as a two-car set, the way they run under the
    # Hudson. Third rail, so they need electrified track.
    dict(
        nml="path_pa1_b", sprite="path_pa1_b", name="PATH PA1/PA2",
        hidden=True,
        intro=(1965, 9, 1), length_ft=51, length=5, track="ELRL",
        engine_class="ENGINE_CLASS_ELECTRIC", effect=None,
        run_base="RUNNING_COST_ELECTRIC", te=0.30, drag=0.05,
        flags=["TRAIN_FLAG_MU"], loading=25, riders=True,
        real=dict(speed=50, power=0, weight=33, cap=100, cost=0, run=0,
                  model_life="VEHICLE_NEVER_EXPIRES", life=45, decay=22),
        bal=dict(speed=50, power=0, weight=20, cap=38, cost=0, run=0,
                 model_life="VEHICLE_NEVER_EXPIRES", life=45, decay=22),
    ),
    dict(
        nml="path_pa1_a", sprite="path_pa1_a", name="PATH PA1/PA2",
        role="St. Louis Car, 1965-67 · 202 built",
        intro=(1965, 9, 1), length_ft=51, length=5, track="ELRL",
        engine_class="ENGINE_CLASS_ELECTRIC", effect="VISUAL_EFFECT_ELECTRIC",
        run_base="RUNNING_COST_ELECTRIC", te=0.30, drag=0.05,
        flags=["TRAIN_FLAG_MU"], artic="path_pa1_b", pair=True, loading=25, riders=True,
        real=dict(speed=50, power=800, weight=33, cap=100, cost=92, run=40,
                  model_life=46, life=45, decay=22),
        bal=dict(speed=50, power=560, weight=20, cap=38, cost=54, run=20,
                 model_life=46, life=45, decay=22),
        purchase="{BLACK}St. Louis Car Company, 1965-1967.{}The cars that replaced the "
                 "Hudson & Manhattan tubes' original stock: painted aluminium bodies, "
                 "two doors a side, 51 ft over couplers. Bought as an A car plus a "
                 "cabless C car.{}{GOLD}Third rail - electrified track only.",
    ),
    dict(
        nml="path_pa4_b", sprite="path_pa4_b", name="PATH PA4",
        hidden=True,
        intro=(1987, 1, 1), length_ft=51, length=5, track="ELRL",
        engine_class="ENGINE_CLASS_ELECTRIC", effect=None,
        run_base="RUNNING_COST_ELECTRIC", te=0.30, drag=0.05,
        flags=["TRAIN_FLAG_MU"], loading=25, riders=True,
        real=dict(speed=55, power=0, weight=34, cap=102, cost=0, run=0,
                  model_life="VEHICLE_NEVER_EXPIRES", life=40, decay=18),
        bal=dict(speed=55, power=0, weight=20, cap=40, cost=0, run=0,
                 model_life="VEHICLE_NEVER_EXPIRES", life=40, decay=18),
    ),
    dict(
        nml="path_pa4_a", sprite="path_pa4_a", name="PATH PA4",
        role="Kawasaki, 1986-88 · 95 built",
        intro=(1987, 1, 1), length_ft=51, length=5, track="ELRL",
        engine_class="ENGINE_CLASS_ELECTRIC", effect="VISUAL_EFFECT_ELECTRIC",
        run_base="RUNNING_COST_ELECTRIC", te=0.30, drag=0.05,
        flags=["TRAIN_FLAG_MU"], artic="path_pa4_b", pair=True, loading=25, riders=True,
        real=dict(speed=55, power=1000, weight=34, cap=102, cost=106, run=42,
                  model_life=40, life=40, decay=18),
        bal=dict(speed=55, power=700, weight=20, cap=40, cost=64, run=22,
                 model_life=40, life=40, decay=18),
        purchase="{BLACK}Kawasaki, 1986-1988. 95 built.{}PATH's first stainless steel "
                 "cars, with three doors a side for faster loading at Journal Square "
                 "and 33rd Street. All cab cars, so a set has a cab at each "
                 "end.{}{GOLD}Third rail - electrified track only.",
    ),
    dict(
        nml="path_pa5_b", sprite="path_pa5_b", name="PATH PA5",
        hidden=True,
        intro=(2011, 6, 1), length_ft=51, length=5, track="ELRL",
        engine_class="ENGINE_CLASS_ELECTRIC", effect=None,
        run_base="RUNNING_COST_ELECTRIC", te=0.30, drag=0.05,
        flags=["TRAIN_FLAG_MU"], loading=28, riders=True,
        real=dict(speed=55, power=0, weight=35, cap=105, cost=0, run=0,
                  model_life="VEHICLE_NEVER_EXPIRES", life=40, decay=14),
        bal=dict(speed=60, power=0, weight=21, cap=44, cost=0, run=0,
                 model_life="VEHICLE_NEVER_EXPIRES", life=40, decay=14),
    ),
    dict(
        nml="path_pa5_a", sprite="path_pa5_a", name="PATH PA5",
        role="Kawasaki, 2009-11 · 340 built",
        intro=(2011, 6, 1), length_ft=51, length=5, track="ELRL",
        engine_class="ENGINE_CLASS_ELECTRIC", effect="VISUAL_EFFECT_ELECTRIC",
        run_base="RUNNING_COST_ELECTRIC", te=0.30, drag=0.05,
        flags=["TRAIN_FLAG_MU"], artic="path_pa5_b", pair=True, loading=28, riders=True,
        real=dict(speed=55, power=1200, weight=35, cap=105, cost=126, run=44,
                  model_life=45, life=40, decay=14),
        bal=dict(speed=60, power=860, weight=21, cap=44, cost=76, run=24,
                 model_life=45, life=40, decay=14),
        purchase="{BLACK}Kawasaki, 2009-2011. 340 built.{}The current PATH fleet: "
                 "stainless bodies, three doors a side, longitudinal seating for 35 "
                 "and standing room for a rush hour under the river.{}{GOLD}Third "
                 "rail - electrified track only.",
    ),
    # ------------------------------------------------- HUDSON-BERGEN LIGHT RAIL --
    # A double-articulated low-floor tram, not a mainline car: three body
    # sections over three trucks, 750 V DC off the overhead. Runs as a single
    # unit - HBLR couples one to three of them into a train - so this one is
    # bought on its own rather than as a married pair like the PATH stock.
    dict(
        nml="hblr_lrv", sprite="njt_hblr", name="HBLR Light Rail",
        role="Kinki Sharyo low-floor LRV, 2000 \u00b7 52 built",
        intro=(2000, 4, 15), length_ft=90, length=8, track="ELRL",
        engine_class="ENGINE_CLASS_ELECTRIC", effect="VISUAL_EFFECT_ELECTRIC",
        run_base="RUNNING_COST_ELECTRIC", te=0.32, drag=0.05,
        flags=["TRAIN_FLAG_MU"], loading=32, riders=True,
        real=dict(speed=55, power=670, weight=45, cap=178, cost=112, run=38,
                  model_life=45, life=35, decay=16),
        bal=dict(speed=55, power=470, weight=27, cap=70, cost=68, run=18,
                 model_life=45, life=35, decay=16),
        purchase="{BLACK}Kinki Sharyo, 1998-2005. 52 built.{}Double-articulated "
                 "low-floor light rail car for the Hudson-Bergen line, which opened "
                 "in April 2000 between Bayonne and Jersey City. Three body sections, "
                 "wide doors and room for well over a hundred standing riders. Runs "
                 "singly or coupled into two- and three-car trains.{}{GOLD}750 V "
                 "overhead - electrified track only.",
    ),
]

# ------------------------------------------------ 1914-1990 historical stock --
# Predecessor railroads: Pennsylvania, Erie Lackawanna, Central Railroad of New
# Jersey, Delaware Lackawanna & Western, then Penn Central, Conrail, NJDOT and
# early NJ TRANSIT. Liveries are each railroad's own.

VEHICLES += [
    dict(
        nml="k4s", sprite="hist_k4s", name="PRR K4s Pacific",
        role="Pennsylvania Railroad 4-6-2, 1914-57",
        intro=(1914, 5, 1), length_ft=83.5, length=8, track="RAIL",
        engine_class="ENGINE_CLASS_STEAM", effect="VISUAL_EFFECT_STEAM",
        run_base="RUNNING_COST_STEAM", te=0.09, drag=0.09,
        flags=["TRAIN_FLAG_FLIP"],
        real=dict(speed=87, power=3286, weight=237, cap=0, cost=120, run=132,
                  model_life=44, life=40, decay=30),
        bal=dict(speed=75, power=1400, weight=130, cap=0, cost=78, run=90,
                 model_life=44, life=40, decay=30),
        purchase="{BLACK}Juniata Shops and Baldwin, 1914-1928. 425 built.{}The "
                 "Pennsylvania's standard passenger Pacific, and the last steam on "
                 "the New York & Long Branch - regular runs ended in 1956, the final "
                 "excursion behind No. 612 in October 1957.{}{GOLD}Dark Green "
                 "Locomotive Enamel. Heavy, thirsty, and magnificent at speed.",
    ),
    dict(
        nml="e8", sprite="hist_e8", name="EMD E8",
        role="Erie Lackawanna passenger diesel, 1950",
        intro=(1950, 3, 1), length_ft=70.3, length=7, track="RAIL",
        engine_class="ENGINE_CLASS_DIESEL", effect="VISUAL_EFFECT_DIESEL",
        run_base="RUNNING_COST_DIESEL", te=0.18, drag=0.06,
        flags=["TRAIN_FLAG_FLIP"],
        real=dict(speed=100, power=2250, weight=143, cap=0, cost=145, run=95,
                  model_life=32, life=32, decay=22),
        bal=dict(speed=90, power=1100, weight=105, cap=0, cost=92, run=62,
                 model_life=32, life=32, decay=22),
        purchase="{BLACK}EMD, 1949-1954. 450 A units built.{}Twin 1,125 hp 567B V12s "
                 "under a streamlined nose. The Pennsylvania was the largest buyer; "
                 "Erie Lackawanna ran 25 out of Hoboken, and NJDOT bought ex-Penn "
                 "Central examples in 1976 for commuter work.",
    ),
    dict(
        nml="rs3", sprite="hist_rs3", name="ALCO RS-3",
        role="Jersey Central road switcher, 1950",
        intro=(1950, 5, 1), length_ft=56.5, length=6, track="RAIL",
        engine_class="ENGINE_CLASS_DIESEL", effect="VISUAL_EFFECT_DIESEL",
        run_base="RUNNING_COST_DIESEL", te=0.25, drag=0.08,
        flags=["TRAIN_FLAG_FLIP"],
        real=dict(speed=70, power=1600, weight=112, cap=0, cost=96, run=80,
                  model_life=30, life=30, decay=26),
        bal=dict(speed=65, power=800, weight=84, cap=0, cost=62, run=52,
                 model_life=30, life=30, decay=26),
        purchase="{BLACK}ALCO, 1950-1956. 1,418 built.{}The go-anywhere road "
                 "switcher: 1,600 hp from a 244 V12, equally at home on a commuter "
                 "train or a local freight. The Jersey Central ran about 26 in dark "
                 "green and yellow; Erie Lackawanna had 62.",
    ),
    dict(
        nml="u34ch", sprite="hist_u34ch", name="GE U34CH",
        role="Erie Lackawanna / NJDOT, 1970",
        intro=(1970, 9, 1), length_ft=67.3, length=7, track="RAIL",
        engine_class="ENGINE_CLASS_DIESEL", effect="VISUAL_EFFECT_DIESEL",
        run_base="RUNNING_COST_DIESEL", te=0.25, drag=0.07,
        flags=["TRAIN_FLAG_FLIP"],
        real=dict(speed=70, power=3430, weight=165, cap=0, cost=165, run=118,
                  model_life=25, life=25, decay=28),
        bal=dict(speed=70, power=1700, weight=118, cap=0, cost=108, run=76,
                 model_life=25, life=25, decay=28),
        purchase="{BLACK}General Electric, 1970-73. 32 for NJDOT.{}Bought new to "
                 "haul the Comet coaches on the Bergen County lines, with head-end "
                 "power taken off the 3,600 hp FDL-16 - which is why they idled at a "
                 "constant roar. Retired from passenger work in 1994.{}{GOLD}The "
                 "blue-and-silver Bluebird scheme.",
    ),
    dict(
        nml="gg1", sprite="hist_gg1", name="PRR GG1",
        role="Pennsylvania Railroad electric, 1935",
        intro=(1935, 1, 1), length_ft=79.5, length=8, track="ELRL",
        engine_class="ENGINE_CLASS_ELECTRIC", effect="VISUAL_EFFECT_ELECTRIC",
        run_base="RUNNING_COST_ELECTRIC", te=0.14, drag=0.06,
        flags=["TRAIN_FLAG_FLIP"],
        real=dict(speed=100, power=4620, weight=215, cap=0, cost=190, run=96,
                  model_life=48, life=45, decay=16),
        bal=dict(speed=95, power=2800, weight=155, cap=0, cost=128, run=68,
                 model_life=48, life=45, decay=16),
        purchase="{BLACK}GE and Altoona Works, 1934-1943. 139 built.{}Raymond Loewy's "
                 "welded carbody over a 4,620 hp continuous rating and an 8,500 hp "
                 "short burst. NJ TRANSIT inherited thirteen and ran them to the very "
                 "end: the last revenue trip left New York Penn at 5:20 pm on 28 "
                 "October 1983, forty-nine years after the class was new.{}{GOLD}"
                 "Electrified track only.",
    ),
    dict(
        nml="alp44", sprite="hist_alp44", name="ALP-44",
        role="NJ TRANSIT electric, 1990",
        intro=(1990, 6, 1), length_ft=51, length=6, track="ELRL",
        engine_class="ENGINE_CLASS_ELECTRIC", effect="VISUAL_EFFECT_ELECTRIC",
        run_base="RUNNING_COST_ELECTRIC", te=0.25, drag=0.06,
        flags=["TRAIN_FLAG_FLIP"],
        real=dict(speed=100, power=7000, weight=94, cap=0, cost=190, run=84,
                  model_life=21, life=25, decay=20),
        bal=dict(speed=100, power=3100, weight=86, cap=0, cost=130, run=60,
                 model_life=21, life=25, decay=20),
        purchase="{BLACK}ASEA / ABB, 1989-1997. 32 for NJ TRANSIT.{}The AEM-7 "
                 "derivative that replaced the GG1s and E60s: 7,000 hp in a 51 ft "
                 "body weighing barely a hundred tons. Retired by 2011.{}{GOLD}"
                 "Electrified track only.",
    ),
    dict(
        nml="mp54", sprite="hist_mp54", name="PRR MP54 MU",
        role="Pennsylvania Railroad electric MU, 1915",
        intro=(1915, 1, 1), length_ft=64.5, length=6, track="ELRL",
        engine_class="ENGINE_CLASS_ELECTRIC", effect="VISUAL_EFFECT_ELECTRIC",
        run_base="RUNNING_COST_ELECTRIC", te=0.30, drag=0.05,
        flags=["TRAIN_FLAG_MU"], loading=22,
        real=dict(speed=65, power=450, weight=55, cap=72, cost=78, run=38,
                  model_life=62, life=50, decay=26),
        bal=dict(speed=60, power=380, weight=33, cap=30, cost=46, run=18,
                 model_life=62, life=50, decay=26),
        purchase="{BLACK}Pennsylvania Railroad, MU cars from 1915.{}Riveted steel "
                 "cars with arched clerestory roofs, 72 seats and a pantograph on the "
                 "roof, working the corridor to Trenton and the Princeton Dinky. The "
                 "Arrow IIs displaced them from New Jersey in 1977.{}{GOLD}"
                 "Electrified track only.",
    ),
    dict(
        nml="dlwmu", sprite="hist_dlwmu", name="DL&W MU",
        role="Lackawanna electric MU, 1930",
        intro=(1930, 9, 1), length_ft=70.1, length=7, track="ELRL",
        engine_class="ENGINE_CLASS_ELECTRIC", effect="VISUAL_EFFECT_ELECTRIC",
        run_base="RUNNING_COST_ELECTRIC", te=0.30, drag=0.05,
        flags=["TRAIN_FLAG_MU"], loading=22,
        real=dict(speed=63, power=1020, weight=67, cap=84, cost=92, run=44,
                  model_life=54, life=50, decay=22),
        bal=dict(speed=60, power=700, weight=40, cap=34, cost=54, run=21,
                 model_life=54, life=50, decay=22),
        purchase="{BLACK}Pullman and GE, 1929-1930. 141 motor cars.{}Built for the "
                 "Lackawanna's 3,000 volt DC Morris & Essex electrification and used, "
                 "in Pullman green, for fifty-four years - Lackawanna, Erie "
                 "Lackawanna, Conrail and finally NJ TRANSIT, last run August "
                 "1984.{}{GOLD}Electrified track only.",
    ),
    dict(
        nml="arrow1", sprite="hist_arrow1", name="Arrow I",
        role="St. Louis Car single unit, 1968",
        intro=(1968, 10, 30), length_ft=85, length=8, track="ELRL",
        engine_class="ENGINE_CLASS_ELECTRIC", effect="VISUAL_EFFECT_ELECTRIC",
        run_base="RUNNING_COST_ELECTRIC", te=0.30, drag=0.05,
        flags=["TRAIN_FLAG_MU"], loading=20,
        real=dict(speed=100, power=700, weight=55, cap=110, cost=105, run=50,
                  model_life=12, life=20, decay=45),
        bal=dict(speed=85, power=560, weight=33, cap=42, cost=62, run=26,
                 model_life=12, life=20, decay=45),
        purchase="{BLACK}St. Louis Car Company, 1968-69. 35 single cars.{}New "
                 "Jersey's first self-propelled stainless steel cars, run by Penn "
                 "Central for the state. Chronically unreliable: all 35 were out of "
                 "service by 1980, and 30 came back as unpowered Comet IB "
                 "trailers.{}{GOLD}Electrified track only.",
    ),
    dict(
        nml="arrow2_b", sprite="hist_arrow2_b", name="Arrow II",
        hidden=True,
        intro=(1974, 10, 1), length_ft=85, length=8, track="ELRL",
        engine_class="ENGINE_CLASS_ELECTRIC", effect=None,
        run_base="RUNNING_COST_ELECTRIC", te=0.30, drag=0.05,
        flags=["TRAIN_FLAG_MU"], loading=20,
        real=dict(speed=100, power=0, weight=57, cap=116, cost=0, run=0,
                  model_life="VEHICLE_NEVER_EXPIRES", life=25, decay=26),
        bal=dict(speed=85, power=0, weight=34, cap=46, cost=0, run=0,
                 model_life="VEHICLE_NEVER_EXPIRES", life=25, decay=26),
    ),
    dict(
        nml="arrow2_a", sprite="hist_arrow2_a", name="Arrow II",
        role="General Electric married pair, 1974",
        intro=(1974, 10, 1), length_ft=85, length=8, track="ELRL",
        engine_class="ENGINE_CLASS_ELECTRIC", effect="VISUAL_EFFECT_ELECTRIC",
        run_base="RUNNING_COST_ELECTRIC", te=0.30, drag=0.05,
        flags=["TRAIN_FLAG_MU"], artic="arrow2_b", pair=True, loading=20,
        real=dict(speed=100, power=1000, weight=57, cap=116, cost=115, run=52,
                  model_life=23, life=25, decay=26),
        bal=dict(speed=85, power=850, weight=34, cap=46, cost=70, run=29,
                 model_life=23, life=25, decay=26),
        purchase="{BLACK}General Electric, 1974. 70 cars, all married pairs.{}The "
                 "cars that finally retired the MP54s, reseated 3-and-2 to squeeze in "
                 "119 riders and repainted into NJ TRANSIT stripes at their 1983 "
                 "overhaul. Withdrawn in 1997 with tired car bodies.{}{GOLD}"
                 "Electrified track only.",
    ),
    dict(
        nml="stillwell", sprite="hist_stillwell", name="Stillwell Coach",
        role="Erie Railroad commuter coach, 1924",
        intro=(1924, 1, 1), length_ft=72, length=6, track="RAIL",
        engine_class=None, effect=None,
        run_base="RUNNING_COST_DIESEL", te=0.30, drag=0.05,
        flags=["TRAIN_FLAG_FLIP"], loading=16,
        real=dict(speed=70, power=0, weight=46, cap=86, cost=40, run=18,
                  model_life=48, life=45, decay=24),
        bal=dict(speed=80, power=0, weight=26, cap=34, cost=24, run=9,
                 model_life=48, life=45, decay=24),
        purchase="{BLACK}Pressed Steel Car, Pullman and ACF.{}Lewis Stillwell's "
                 "steel commuter coaches for the Erie: arched clerestory roof, "
                 "wooden-slat seats for 86, and a ride New Jersey commuters endured "
                 "into the early 1970s until the Comets arrived.",
    ),
    dict(
        nml="comet1", sprite="hist_comet1", name="Comet I Coach",
        role="Pullman-Standard trailer, 1971",
        intro=(1971, 1, 1), length_ft=85, length=8, track="RAIL",
        engine_class=None, effect=None,
        run_base="RUNNING_COST_DIESEL", te=0.30, drag=0.05,
        flags=["TRAIN_FLAG_FLIP"], loading=20,
        real=dict(speed=100, power=0, weight=48, cap=131, cost=60, run=25,
                  model_life=34, life=40, decay=22),
        bal=dict(speed=105, power=0, weight=28, cap=46, cost=33, run=12,
                 model_life=34, life=40, decay=22),
        purchase="{BLACK}Pullman-Standard, 1970-73. 155 built.{}Aluminium-bodied, "
                 "head-end powered and paid for by the state: the first modern "
                 "commuter coach in New Jersey, in Erie Lackawanna maroon and yellow "
                 "over bare metal. Nicknamed Sliders for their low doors.",
    ),
    dict(
        nml="comet1_cab", sprite="hist_comet1_cab", name="Comet I Cab Car",
        role="Pullman-Standard push-pull cab, 1971",
        intro=(1971, 1, 1), length_ft=85, length=8, track="RAIL",
        engine_class=None, effect=None,
        run_base="RUNNING_COST_DIESEL", te=0.30, drag=0.05,
        flags=["TRAIN_FLAG_FLIP"], loading=20,
        real=dict(speed=100, power=0, weight=49, cap=115, cost=66, run=27,
                  model_life=34, life=40, decay=22),
        bal=dict(speed=105, power=0, weight=29, cap=42, cost=36, run=13,
                 model_life=34, life=40, decay=22),
        purchase="{BLACK}Pullman-Standard, 1970-73. 35 cab cars.{}The other end of a "
                 "U34CH push-pull set. Use CTRL+click in the depot to turn it around.",
    ),
    dict(
        nml="comet2", sprite="hist_comet2", name="Comet II Coach",
        role="Bombardier trailer, 1983",
        intro=(1983, 1, 1), length_ft=85, length=8, track="RAIL",
        engine_class=None, effect=None,
        run_base="RUNNING_COST_DIESEL", te=0.30, drag=0.05,
        flags=["TRAIN_FLAG_FLIP"], loading=20,
        real=dict(speed=100, power=0, weight=44, cap=120, cost=62, run=26,
                  model_life=40, life=40, decay=20),
        bal=dict(speed=110, power=0, weight=28, cap=44, cost=34, run=13,
                 model_life=40, life=40, decay=20),
        purchase="{BLACK}Bombardier, 1982-1989. 161 built.{}NJ TRANSIT's first order "
                 "of its own, in the angular chevron stripes of the early eighties. "
                 "Long end doors with trapdoors let one car work both low platforms "
                 "and high ones - the operational advance over the Comet I.",
    ),
]


# ------------------------------------------------------------------- buses --
# NJ TRANSIT Bus Operations is the second-largest bus fleet in the United
# States, and it long predates the trains: the buses descend from Public
# Service Coordinated Transport, which was bustituting its own trolley lines
# before NJ TRANSIT existed. These are OpenTTD road vehicles rather than
# trains, so they carry the road-vehicle running cost base and a `feature`
# key that sends them to FEAT_ROADVEHS instead of FEAT_TRAINS.
#
# The balanced stat set moves the buses much less than it moves the trains,
# because a real transit bus is already about the size of an OpenTTD road
# vehicle - a 53-seat fishbowl against a vanilla bus's 31 is nothing like a
# MultiLevel's 132 against a vanilla carriage's 40. The road rules are:
#
#   capacity  x0.65   a 40 ft bus lands in the thirties, next to vanilla's 31
#   power     x0.60   gentler than the trains' x0.45; buses start low
#   weight    x0.75
#   speed     shaped into a 30 -> 65 mph ladder, city buses under coaches
#
# Capacity is seated capacity throughout. Every real one of these carries
# standees too, but NJ TRANSIT publishes seats, and the rail side of this set
# counts seats everywhere except PATH and the light rail car.

ROAD_VEHICLES = [
    dict(
        nml="asv", sprite="bus_asv", name="Yellow Coach ASV", feature="road",
        role="Public Service all-service vehicle, 1935 · 357 built",
        intro=(1935, 6, 1), length_ft=33, length=6,
        run_base="RUNNING_COST_ROADVEH", te=0.30, drag=0.10,
        effect="VISUAL_EFFECT_DIESEL", sound="SOUND_DEPARTURE_OLD_BUS",
        loading=8,
        real=dict(speed=35, power=150, weight=11, cap=40, cost=22, run=62,
                  model_life=25, life=15, decay=32),
        bal=dict(speed=30, power=90, weight=8, cap=26, cost=16, run=44,
                 model_life=25, life=15, decay=32),
        purchase="{BLACK}Yellow Coach for Public Service, 1935-1948. 357 built, all "
                 "but one of them for New Jersey.{}The All-Service Vehicle drew from "
                 "trolley wire where Public Service had strung it and ran as a "
                 "gas-electric where it had not - the same trick as the ALP-45DP, "
                 "fifty years earlier.{}{GOLD}Runs on any road.",
    ),
    dict(
        nml="newlook", sprite="bus_newlook", name="GMC New Look", feature="road",
        role="Transport of New Jersey fishbowl, 1960",
        intro=(1960, 1, 1), length_ft=40, length=8,
        run_base="RUNNING_COST_ROADVEH", te=0.30, drag=0.10,
        effect="VISUAL_EFFECT_DIESEL", sound="SOUND_DEPARTURE_OLD_BUS",
        loading=10,
        real=dict(speed=55, power=210, weight=11, cap=53, cost=26, run=70,
                  model_life=25, life=15, decay=28),
        bal=dict(speed=45, power=126, weight=8, cap=34, cost=18, run=50,
                 model_life=25, life=15, decay=28),
        purchase="{BLACK}GM Truck & Coach, 1960-1973.{}The fishbowl: six-piece curved "
                 "windshield, Detroit Diesel 6V-71 under the back seat. NJ TRANSIT "
                 "inherited its first buses from Transport of New Jersey in 1980 and "
                 "these were most of them.",
    ),
    dict(
        nml="flx870", sprite="bus_flx870", name="Grumman-Flxible 870", feature="road",
        role="NJ TRANSIT, 1981 · 271 built",
        intro=(1981, 3, 1), length_ft=40, length=8,
        run_base="RUNNING_COST_ROADVEH", te=0.30, drag=0.10,
        effect="VISUAL_EFFECT_DIESEL", sound="SOUND_DEPARTURE_OLD_BUS",
        loading=10,
        real=dict(speed=55, power=218, weight=12, cap=47, cost=28, run=78,
                  model_life=15, life=12, decay=44),
        bal=dict(speed=48, power=130, weight=9, cap=31, cost=20, run=56,
                 model_life=15, life=12, decay=44),
        purchase="{BLACK}Grumman Flxible, 1980-1981. 271 built.{}The Advanced Design "
                 "Bus that gave the type its reputation: square, ADA-ready, and "
                 "cracking its undercarriage A-frames across the whole industry.{}"
                 "{GOLD}Breaks down more than anything else in the set.",
    ),
    dict(
        nml="mc9", sprite="bus_mc9", name="MCI MC-9", feature="road",
        role="Suburban coach, 1982 · 700 built",
        intro=(1982, 6, 1), length_ft=45, length=8,
        run_base="RUNNING_COST_ROADVEH", te=0.28, drag=0.07,
        effect="VISUAL_EFFECT_DIESEL", sound="SOUND_DEPARTURE_MODERN_BUS",
        loading=5,
        real=dict(speed=65, power=318, weight=14, cap=47, cost=34, run=84,
                  model_life=20, life=18, decay=26),
        bal=dict(speed=58, power=190, weight=11, cap=31, cost=24, run=60,
                 model_life=20, life=18, decay=26),
        purchase="{BLACK}Motor Coach Industries, 1982-1984. 700 built.{}The Crusader II "
                 "highway coach, bought in quantity for the park-and-ride runs into "
                 "the Port Authority terminal. High floor over baggage lockers, one "
                 "door, and the fastest road vehicle of its decade here.",
    ),

    # Volvo B10M articulated pair: the front section pulls in a hidden rear
    # section as an articulated part, the same trick the EMU married pairs use.
    dict(
        nml="b10m_b", sprite="bus_b10m_b", name="Volvo B10M Artic", feature="road",
        hidden=True,
        intro=(1985, 1, 1), length_ft=22, length=4,
        run_base="RUNNING_COST_ROADVEH", te=0.28, drag=0.10,
        effect=None, loading=10,
        real=dict(speed=55, power=0, weight=6, cap=27, cost=0, run=0,
                  model_life=20, life=15, decay=30),
        bal=dict(speed=50, power=0, weight=5, cap=17, cost=0, run=0,
                 model_life=20, life=15, decay=30),
    ),
    dict(
        nml="b10m_a", sprite="bus_b10m_a", name="Volvo B10M Artic", feature="road",
        role="Articulated bus, 1985 · 210 built",
        intro=(1985, 1, 1), length_ft=38, length=7, artic="b10m_b",
        artic_with="b10m_b",
        run_base="RUNNING_COST_ROADVEH", te=0.28, drag=0.10,
        effect="VISUAL_EFFECT_DIESEL", sound="SOUND_DEPARTURE_MODERN_BUS",
        loading=10,
        real=dict(speed=55, power=250, weight=11, cap=38, cost=40, run=92,
                  model_life=20, life=15, decay=30),
        bal=dict(speed=50, power=150, weight=8, cap=25, cost=28, run=66,
                 model_life=20, life=15, decay=30),
        purchase="{BLACK}Volvo, 1985. 210 built.{}Sixty feet of bus on a mid-engined "
                 "Swedish chassis, hinged in the middle so it can still take a city "
                 "corner. Bought for the heaviest Hudson County loadings.{}{GOLD}Two "
                 "sections, bought and sold as one vehicle.",
    ),

    dict(
        nml="metrob", sprite="bus_metrob", name="Flxible Metro-B", feature="road",
        role="NJ TRANSIT, 1988 · 528 built",
        intro=(1988, 9, 1), length_ft=40, length=8,
        run_base="RUNNING_COST_ROADVEH", te=0.30, drag=0.10,
        effect="VISUAL_EFFECT_DIESEL", sound="SOUND_DEPARTURE_MODERN_BUS",
        loading=10,
        real=dict(speed=55, power=277, weight=12, cap=45, cost=29, run=76,
                  model_life=18, life=14, decay=30),
        bal=dict(speed=52, power=166, weight=9, cap=29, cost=21, run=54,
                 model_life=18, life=14, decay=30),
        purchase="{BLACK}Flxible, 1988-1989. 528 built.{}The 870 redrawn without the "
                 "structural sins, in the chevron stripes the Comet IIs and Arrow "
                 "IIIs were wearing at the same time. Detroit Diesel 6V-92TA.",
    ),
    dict(
        nml="rts06", sprite="bus_rts06", name="Nova Bus RTS-06", feature="road",
        role="NJ TRANSIT, 1999 · 580 built",
        intro=(1999, 5, 1), length_ft=40, length=8,
        run_base="RUNNING_COST_ROADVEH", te=0.30, drag=0.10,
        effect="VISUAL_EFFECT_DIESEL", sound="SOUND_DEPARTURE_MODERN_BUS",
        loading=10,
        real=dict(speed=55, power=275, weight=13, cap=43, cost=30, run=74,
                  model_life=15, life=15, decay=26),
        bal=dict(speed=55, power=165, weight=10, cap=28, cost=22, run=53,
                 model_life=15, life=15, decay=26),
        purchase="{BLACK}Nova Bus, 1999-2000. 580 built.{}The Rapid Transit Series that "
                 "GM drew in 1977 and three companies went on building: ribbed sides, "
                 "rounded corners, and the last of NJ TRANSIT's high-floor city "
                 "buses.",
    ),
    dict(
        nml="nabi416", sprite="bus_nabi416", name="NABI 416.15", feature="road",
        role="NJ TRANSIT 40-SFW, 2009 · 1,049 built",
        intro=(2009, 4, 1), length_ft=40, length=8,
        run_base="RUNNING_COST_ROADVEH", te=0.30, drag=0.10,
        effect="VISUAL_EFFECT_DIESEL", sound="SOUND_DEPARTURE_MODERN_BUS",
        loading=10,
        real=dict(speed=55, power=330, weight=13, cap=44, cost=32, run=72,
                  model_life=20, life=16, decay=24),
        bal=dict(speed=58, power=198, weight=10, cap=29, cost=23, run=52,
                 model_life=20, life=16, decay=24),
        purchase="{BLACK}North American Bus Industries, 2009-2013. 1,049 built.{}"
                 "The 40-SFW: forty feet, standard floor, wide body, Cummins ISL9. "
                 "The single largest order in the fleet and the bus most NJ TRANSIT "
                 "routes ran for a decade.",
    ),
    dict(
        nml="d4500ct", sprite="bus_d4500ct", name="MCI D4500CT", feature="road",
        role="Commuter coach, 2017",
        intro=(2017, 1, 1), length_ft=45, length=8,
        run_base="RUNNING_COST_ROADVEH", te=0.28, drag=0.07,
        effect="VISUAL_EFFECT_DIESEL", sound="SOUND_DEPARTURE_MODERN_BUS",
        loading=5,
        real=dict(speed=65, power=425, weight=17, cap=57, cost=44, run=90,
                  model_life=30, life=18, decay=20),
        bal=dict(speed=65, power=255, weight=13, cap=37, cost=31, run=64,
                 model_life=30, life=18, decay=20),
        purchase="{BLACK}Motor Coach Industries, 2017-2022.{}Forty-five feet of "
                 "commuter coach on the Lincoln Tunnel exclusive bus lane, which "
                 "moves more people at rush hour than any single rail line in the "
                 "set. Cummins X12, fifty-seven seats and no standees.",
    ),

    # New Flyer XD60 Xcelsior: the second articulated pair.
    dict(
        nml="xd60_b", sprite="bus_xd60_b", name="New Flyer XD60", feature="road",
        hidden=True,
        intro=(2020, 6, 1), length_ft=22, length=4,
        run_base="RUNNING_COST_ROADVEH", te=0.28, drag=0.10,
        effect=None, loading=12,
        real=dict(speed=55, power=0, weight=7, cap=23, cost=0, run=0,
                  model_life=30, life=16, decay=22),
        bal=dict(speed=58, power=0, weight=5, cap=15, cost=0, run=0,
                 model_life=30, life=16, decay=22),
    ),
    dict(
        nml="xd60_a", sprite="bus_xd60_a", name="New Flyer XD60", feature="road",
        role="Xcelsior articulated, 2020 · 110 built",
        intro=(2020, 6, 1), length_ft=38, length=7, artic="xd60_b",
        artic_with="xd60_b",
        run_base="RUNNING_COST_ROADVEH", te=0.28, drag=0.10,
        effect="VISUAL_EFFECT_DIESEL", sound="SOUND_DEPARTURE_MODERN_BUS",
        loading=12,
        real=dict(speed=55, power=280, weight=12, cap=32, cost=46, run=88,
                  model_life=30, life=16, decay=22),
        bal=dict(speed=58, power=168, weight=9, cap=21, cost=33, run=63,
                 model_life=30, life=16, decay=22),
        purchase="{BLACK}New Flyer, 2020. 110 built.{}Low-floor sixty-footers for the "
                 "Newark and Hudson County trunk routes - the first articulated buses "
                 "NJ TRANSIT had bought since the Volvos went in 2004. Cummins L9.{}"
                 "{GOLD}Two sections, bought and sold as one vehicle.",
    ),

    dict(
        nml="xe40", sprite="bus_xe40", name="New Flyer XE40 CHARGE", feature="road",
        role="Battery-electric, 2022 · 8 built",
        intro=(2022, 10, 24), length_ft=40, length=8,
        run_base="RUNNING_COST_ROADVEH", te=0.32, drag=0.10,
        effect="VISUAL_EFFECT_DISABLE", sound="SOUND_DEPARTURE_MODERN_BUS",
        loading=12,
        real=dict(speed=55, power=335, weight=15, cap=38, cost=50, run=46,
                  model_life="VEHICLE_NEVER_EXPIRES", life=16, decay=18),
        bal=dict(speed=60, power=201, weight=11, cap=25, cost=36, run=33,
                 model_life="VEHICLE_NEVER_EXPIRES", life=16, decay=18),
        purchase="{BLACK}New Flyer, 2022. 8 built.{}Xcelsior CHARGE NG: NJ TRANSIT's "
                 "first battery-electric bus, into service on Camden route 452 on "
                 "24 October 2022 and the start of a zero-emission fleet by 2040. "
                 "Batteries on the roof, no exhaust.{}{GOLD}Cheapest running cost "
                 "in the set.",
    ),
]


# Where to see the real thing. The artifact page links these; it does not
# reproduce anyone's photographs. Drop files into photos/<nml>.jpg to have
# make_pages.py embed your own instead (see README).
PHOTOS = {
    'k4s': 'https://en.wikipedia.org/wiki/Pennsylvania_Railroad_class_K4',
    'e8': 'https://en.wikipedia.org/wiki/EMD_E8',
    'rs3': 'https://en.wikipedia.org/wiki/ALCO_RS-3',
    'gg1': 'https://en.wikipedia.org/wiki/PRR_GG1',
    'mp54': 'https://en.wikipedia.org/wiki/PRR_MP54',
    'dlwmu': 'https://en.wikipedia.org/wiki/Erie_Lackawanna_MU_Cars',
    'stillwell': 'https://rgvrrm.org/about/railroad/erie2103/',
    'u34ch': 'https://en.wikipedia.org/wiki/GE_U34CH',
    'arrow1': 'https://en.wikipedia.org/wiki/Arrow_(railcar)',
    'arrow2_a': 'https://en.wikipedia.org/wiki/Arrow_(railcar)',
    'arrow3_a': 'https://en.wikipedia.org/wiki/Arrow_(railcar)',
    'comet1': 'https://whippanyrailwaymuseum.net/equipment/comet/',
    'comet1_cab': 'https://whippanyrailwaymuseum.net/equipment/comet/',
    'comet2': 'https://en.wikipedia.org/wiki/Comet_(railcar)',
    'comet5': 'https://en.wikipedia.org/wiki/Comet_V',
    'comet5_cab': 'https://en.wikipedia.org/wiki/Comet_V',
    'alp44': 'https://en.wikipedia.org/wiki/ABB_ALP-44',
    'alp46': 'https://en.wikipedia.org/wiki/Bombardier_ALP-46',
    'alp46a': 'https://en.wikipedia.org/wiki/Bombardier_ALP-46',
    'alp45dp': 'https://en.wikipedia.org/wiki/Bombardier_ALP-45DP',
    'pl42ac': 'https://en.wikipedia.org/wiki/Alstom_PL42AC',
    'multilevel': 'https://en.wikipedia.org/wiki/Bombardier_MultiLevel_Coach',
    'multilevel_cab': 'https://en.wikipedia.org/wiki/Bombardier_MultiLevel_Coach',
    'path_pa1_a': 'https://en.wikipedia.org/wiki/PATH_(rail_system)',
    'path_pa4_a': 'https://en.wikipedia.org/wiki/PATH_(rail_system)',
    'path_pa5_a': 'https://en.wikipedia.org/wiki/PATH_(rail_system)',
    'hblr_lrv': 'https://en.wikipedia.org/wiki/Hudson%E2%80%93Bergen_Light_Rail',
    'asv': 'https://en.wikipedia.org/wiki/Dual-mode_bus',
    'newlook': 'https://en.wikipedia.org/wiki/New_Look_bus',
    'flx870': 'https://en.wikipedia.org/wiki/Grumman_870',
    'mc9': 'https://en.wikipedia.org/wiki/MCI_MC-9',
    'b10m_a': 'https://en.wikipedia.org/wiki/Volvo_B10M',
    'metrob': 'https://en.wikipedia.org/wiki/Flxible_Metro',
    'rts06': 'https://en.wikipedia.org/wiki/Rapid_Transit_Series',
    'nabi416': 'https://en.wikipedia.org/wiki/North_American_Bus_Industries',
    'd4500ct': 'https://en.wikipedia.org/wiki/MCI_D4500',
    'xd60_a': 'https://en.wikipedia.org/wiki/New_Flyer_Xcelsior',
    'xe40': 'https://en.wikipedia.org/wiki/New_Flyer_Xcelsior',
}

# Trains are FEAT_TRAINS items, buses are FEAT_ROADVEHS items, and NML numbers
# item IDs per feature - so the two lists stay separate everywhere the NML is
# generated, and are only concatenated for the things that treat the set as one
# fleet: sprites, the roster image and the published pages.
ALL_VEHICLES = VEHICLES + ROAD_VEHICLES

for _v in ALL_VEHICLES:
    _v.setdefault("feature", "rail")
    _v["photo"] = PHOTOS.get(_v["nml"])


BY_ID = {v["nml"]: v for v in ALL_VEHICLES}
BUYABLE = [v for v in ALL_VEHICLES if not v.get("hidden")]

# Order shown in the roster image and on the artifact pages, grouped by era.
GROUPS = [
    ("Classic era — the predecessor railroads",
     ["k4s", "e8", "rs3", "gg1", "mp54", "dlwmu", "stillwell"]),
    ("Transition era — NJDOT and early NJ TRANSIT",
     ["u34ch", "arrow1", "arrow2_a", "comet1", "comet1_cab", "comet2",
      "alp44"]),
    ("Modern NJ TRANSIT",
     ["arrow3_a", "alp46", "alp46a", "alp45dp", "pl42ac",
      "comet5", "comet5_cab", "multilevel", "multilevel_cab"]),
    ("PATH — rapid transit",
     ["path_pa1_a", "path_pa4_a", "path_pa5_a"]),
    ("Hudson-Bergen Light Rail",
     ["hblr_lrv"]),
    ("Buses — Public Service and early NJ TRANSIT",
     ["asv", "newlook", "flx870", "mc9", "b10m_a"]),
    ("Buses — modern NJ TRANSIT",
     ["metrob", "rts06", "nabi416", "d4500ct", "xd60_a", "xe40"]),
]

ROSTER_ORDER = [k for _, keys in GROUPS for k in keys]


def figures(v, mode):
    """Human-readable spec line for a vehicle in 'real' or 'bal' mode."""
    s = v[mode]
    out = []
    if v.get("dual"):
        e, d = v["dual"][mode]
        out.append("{:,} hp electric".format(e))
        out.append("{:,} hp diesel".format(d))
    elif s["power"]:
        out.append("{:,} hp{}".format(s["power"], " per pair" if v.get("pair") else ""))
    # A married pair carries identical halves, so its figures are quoted per
    # car and doubled; an articulated bus has two unequal sections, so its
    # weight and seats are summed off the hidden rear half instead.
    rear = BY_ID.get(v.get("artic_with"))
    weight = s["weight"] + (rear[mode]["weight"] if rear else 0)
    cap = s["cap"] + (rear[mode]["cap"] if rear else 0)
    out.append("{} t{}".format(weight, " per car" if v.get("pair") else ""))
    out.append("{} mph".format(s["speed"]))
    if cap:
        total = cap * (2 if v.get("pair") else 1)
        out.append("{} riders".format(total) if v.get("riders")
                   else "{} seats".format(total))
    if v["feature"] == "road":
        out.append("any road")
    else:
        out.append("catenary only" if v["track"] == "ELRL" else "any track")
    return out
