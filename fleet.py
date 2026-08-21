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
"""

# --------------------------------------------------------------- NJ TRANSIT --

VEHICLES = [
    dict(
        nml="alp46", sprite="njt_alp46", name="ALP-46",
        role="Bombardier electric, 2002 · 29 built",
        intro=(2002, 3, 1), length=7, track="ELRL",
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
        intro=(2011, 5, 7), length=7, track="ELRL",
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
        intro=(2012, 4, 1), length=8, track="RAIL",
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
        intro=(2006, 1, 1), length=8, track="RAIL",
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
        intro=(1978, 1, 1), length=8, track="ELRL",
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
        intro=(1978, 1, 1), length=8, track="ELRL",
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
        intro=(2003, 1, 1), length=8, track="RAIL",
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
        intro=(2003, 1, 1), length=8, track="RAIL",
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
        intro=(2006, 9, 1), length=8, track="RAIL",
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
        intro=(2006, 9, 1), length=8, track="RAIL",
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
        intro=(1965, 9, 1), length=5, track="ELRL",
        engine_class="ENGINE_CLASS_ELECTRIC", effect=None,
        run_base="RUNNING_COST_ELECTRIC", te=0.30, drag=0.05,
        flags=["TRAIN_FLAG_MU"], loading=25,
        real=dict(speed=50, power=0, weight=33, cap=100, cost=0, run=0,
                  model_life="VEHICLE_NEVER_EXPIRES", life=45, decay=22),
        bal=dict(speed=50, power=0, weight=20, cap=38, cost=0, run=0,
                 model_life="VEHICLE_NEVER_EXPIRES", life=45, decay=22),
    ),
    dict(
        nml="path_pa1_a", sprite="path_pa1_a", name="PATH PA1/PA2",
        role="St. Louis Car, 1965-67 · 202 built",
        intro=(1965, 9, 1), length=5, track="ELRL",
        engine_class="ENGINE_CLASS_ELECTRIC", effect="VISUAL_EFFECT_ELECTRIC",
        run_base="RUNNING_COST_ELECTRIC", te=0.30, drag=0.05,
        flags=["TRAIN_FLAG_MU"], artic="path_pa1_b", pair=True, loading=25,
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
        intro=(1987, 1, 1), length=5, track="ELRL",
        engine_class="ENGINE_CLASS_ELECTRIC", effect=None,
        run_base="RUNNING_COST_ELECTRIC", te=0.30, drag=0.05,
        flags=["TRAIN_FLAG_MU"], loading=25,
        real=dict(speed=55, power=0, weight=34, cap=102, cost=0, run=0,
                  model_life="VEHICLE_NEVER_EXPIRES", life=40, decay=18),
        bal=dict(speed=55, power=0, weight=20, cap=40, cost=0, run=0,
                 model_life="VEHICLE_NEVER_EXPIRES", life=40, decay=18),
    ),
    dict(
        nml="path_pa4_a", sprite="path_pa4_a", name="PATH PA4",
        role="Kawasaki, 1986-88 · 95 built",
        intro=(1987, 1, 1), length=5, track="ELRL",
        engine_class="ENGINE_CLASS_ELECTRIC", effect="VISUAL_EFFECT_ELECTRIC",
        run_base="RUNNING_COST_ELECTRIC", te=0.30, drag=0.05,
        flags=["TRAIN_FLAG_MU"], artic="path_pa4_b", pair=True, loading=25,
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
        intro=(2011, 6, 1), length=5, track="ELRL",
        engine_class="ENGINE_CLASS_ELECTRIC", effect=None,
        run_base="RUNNING_COST_ELECTRIC", te=0.30, drag=0.05,
        flags=["TRAIN_FLAG_MU"], loading=28,
        real=dict(speed=55, power=0, weight=35, cap=105, cost=0, run=0,
                  model_life="VEHICLE_NEVER_EXPIRES", life=40, decay=14),
        bal=dict(speed=60, power=0, weight=21, cap=44, cost=0, run=0,
                 model_life="VEHICLE_NEVER_EXPIRES", life=40, decay=14),
    ),
    dict(
        nml="path_pa5_a", sprite="path_pa5_a", name="PATH PA5",
        role="Kawasaki, 2009-11 · 340 built",
        intro=(2011, 6, 1), length=5, track="ELRL",
        engine_class="ENGINE_CLASS_ELECTRIC", effect="VISUAL_EFFECT_ELECTRIC",
        run_base="RUNNING_COST_ELECTRIC", te=0.30, drag=0.05,
        flags=["TRAIN_FLAG_MU"], artic="path_pa5_b", pair=True, loading=28,
        real=dict(speed=55, power=1200, weight=35, cap=105, cost=126, run=44,
                  model_life=45, life=40, decay=14),
        bal=dict(speed=60, power=860, weight=21, cap=44, cost=76, run=24,
                 model_life=45, life=40, decay=14),
        purchase="{BLACK}Kawasaki, 2009-2011. 340 built.{}The current PATH fleet: "
                 "stainless bodies, three doors a side, longitudinal seating for 35 "
                 "and standing room for a rush hour under the river.{}{GOLD}Third "
                 "rail - electrified track only.",
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
        intro=(1914, 5, 1), length=8, track="RAIL",
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
        intro=(1950, 3, 1), length=7, track="RAIL",
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
        intro=(1950, 5, 1), length=6, track="RAIL",
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
        intro=(1970, 9, 1), length=7, track="RAIL",
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
        intro=(1935, 1, 1), length=8, track="ELRL",
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
        intro=(1990, 6, 1), length=6, track="ELRL",
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
        intro=(1915, 1, 1), length=6, track="ELRL",
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
        intro=(1930, 9, 1), length=7, track="ELRL",
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
        intro=(1968, 10, 30), length=8, track="ELRL",
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
        intro=(1974, 10, 1), length=8, track="ELRL",
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
        intro=(1974, 10, 1), length=8, track="ELRL",
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
        intro=(1924, 1, 1), length=6, track="RAIL",
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
        intro=(1971, 1, 1), length=8, track="RAIL",
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
        intro=(1971, 1, 1), length=8, track="RAIL",
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
        intro=(1983, 1, 1), length=8, track="RAIL",
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
}

for _v in VEHICLES:
    _v["photo"] = PHOTOS.get(_v["nml"])


BY_ID = {v["nml"]: v for v in VEHICLES}
BUYABLE = [v for v in VEHICLES if not v.get("hidden")]

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
    out.append("{} t{}".format(s["weight"], " per car" if v.get("pair") else ""))
    out.append("{} mph".format(s["speed"]))
    if s["cap"]:
        total = s["cap"] * (2 if v.get("pair") else 1)
        out.append("{} seats".format(total) if "PATH" not in v["name"]
                   else "{} riders".format(total))
    out.append("catenary only" if v["track"] == "ELRL" else "any track")
    return out
