# NJ TRANSIT + PATH Trainset for OpenTTD

A NewGRF covering a century of New Jersey railroading: 27 buyable vehicles from a
1914 Pennsylvania Railroad K4s Pacific through the fallen-flag diesels, the GG1's
last run in 1983, NJ TRANSIT's modern fleet, three generations of PATH rapid
transit and the Hudson-Bergen light rail car — each in its own railroad's livery,
with two selectable stat sets.

Built with [NML](https://github.com/OpenTTD/nml) 0.9. Verified to load cleanly in
OpenTTD 13.4 at both parameter settings — 32 engine slots registered, no GRF errors.
All sprites are generated from 3D models rather than hand-pixelled.

---

## Install

Drop `njtransit.grf` into your OpenTTD `newgrf` folder, then enable it from
*Game Options → NewGRF Settings* before starting a new game:

| Platform | Folder |
| --- | --- |
| Windows | `%USERPROFILE%\Documents\OpenTTD\newgrf\` |
| macOS | `~/Documents/OpenTTD/newgrf/` |
| Linux | `~/.local/share/openttd/newgrf/` |

The set only adds vehicles, so it can be added to an existing save; engines appear
from their introduction dates onwards. Start a game in 1930 and you get Lackawanna
MU cars and Stillwell coaches; start in 2012 and you get ALP-45DPs and PA5s.

---

## Realistic or game-balanced

The GRF carries **both** stat sets. In *NewGRF Settings → Parameters*, **Statistics**
switches between them:

- **Realistic** (default) — published prototype figures. Faithful, and frankly
  overpowered: a MultiLevel carries three vanilla carriages' worth of passengers, an
  ALP-46A out-muscles anything in the base set, and a K4s Pacific turns up in 1914
  with 3,286 horsepower.
- **Game-balanced** — the same 26 vehicles with capacity, power, weight, speed and
  cost re-struck so the fleet sits alongside OpenTTD's own vehicles.

OpenTTD resolves the parameter while the GRF loads (the balanced values sit behind an
`if (stats == 1)` block, which compiles to an Action 7 skip), so **set it before
starting a game** — changing it mid-game needs a restart.

### How the balanced numbers were derived

Four rules, applied across the whole roster rather than tuned vehicle by vehicle, so
the fleet keeps its internal shape — an Arrow III stays the poor relation of a
MultiLevel, and a 1950 RS-3 still can't touch a GG1:

| | Rule | Why |
| --- | --- | --- |
| Capacity | ×0.40 | A full-length car lands near OpenTTD's own 40-passenger carriage instead of tripling it. The MultiLevel still tops the roster, at 55 rather than 132. |
| Power | ×0.45 | The strongest electric makes 3,400 hp instead of 7,500 — enough to lead a heavy train, not enough to make the base set pointless. |
| Weight | trailers ×0.60, locos ×0.90 | Lighter trailers so the reduced power still accelerates them; locomotives keep most of their weight, because tractive effort is struck off it. |
| Speed | 50 → 110 mph progression | Instead of a flat 100 mph across a century of equipment, there's a generational ladder worth climbing. |

Purchase and running costs are then re-struck against the new capacity and power.
Dates, lengths, tractive effort coefficients, air drag, reliability and every sprite
are identical in both modes: those are facts about the vehicle, not balance knobs.

---

## Roster

Values shown as `realistic → balanced`; a single value means both modes agree.
Capacity and weight are per car for the married pairs.

**Classic era — the predecessor railroads**

| Vehicle | Intro | Speed mph | Power hp | Weight t | Capacity | Buy | Running |
| --- | --- | --- | --- | --- | --- | --- | --- |
| PRR K4s Pacific | 1914 | 87 → 75 | 3286 → 1400 | 237 → 130 | — | 120 → 78 | 132 → 90 |
| EMD E8 | 1950 | 100 → 90 | 2250 → 1100 | 143 → 105 | — | 145 → 92 | 95 → 62 |
| ALCO RS-3 | 1950 | 70 → 65 | 1600 → 800 | 112 → 84 | — | 96 → 62 | 80 → 52 |
| PRR GG1 | 1935 | 100 → 95 | 4620 → 2800 | 215 → 155 | — | 190 → 128 | 96 → 68 |
| PRR MP54 MU | 1915 | 65 → 60 | 450 → 380 | 55 → 33 | 72 → 30 | 78 → 46 | 38 → 18 |
| DL&W MU | 1930 | 63 → 60 | 1020 → 700 | 67 → 40 | 84 → 34 | 92 → 54 | 44 → 21 |
| Stillwell Coach | 1924 | 70 → 80 | — | 46 → 26 | 86 → 34 | 40 → 24 | 18 → 9 |

**Transition era — NJDOT and early NJ TRANSIT**

| Vehicle | Intro | Speed mph | Power hp | Weight t | Capacity | Buy | Running |
| --- | --- | --- | --- | --- | --- | --- | --- |
| GE U34CH | 1970 | 70 | 3430 → 1700 | 165 → 118 | — | 165 → 108 | 118 → 76 |
| Arrow I | 1968 | 100 → 85 | 700 → 560 | 55 → 33 | 110 → 42 | 105 → 62 | 50 → 26 |
| Arrow II (pair) | 1974 | 100 → 85 | 1000 → 850 | 57 → 34 | 116 → 46 | 115 → 70 | 52 → 29 |
| Comet I Coach | 1971 | 100 → 105 | — | 48 → 28 | 131 → 46 | 60 → 33 | 25 → 12 |
| Comet I Cab Car | 1971 | 100 → 105 | — | 49 → 29 | 115 → 42 | 66 → 36 | 27 → 13 |
| Comet II Coach | 1983 | 100 → 110 | — | 44 → 28 | 120 → 44 | 62 → 34 | 26 → 13 |
| ALP-44 | 1990 | 100 | 7000 → 3100 | 94 → 86 | — | 190 → 130 | 84 → 60 |

**Modern NJ TRANSIT**

| Vehicle | Intro | Speed mph | Power hp | Weight t | Capacity | Buy | Running |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Arrow III EMU (pair) | 1978 | 100 → 80 | 1125 → 900 | 57 → 34 | 120 → 46 | 118 → 72 | 52 → 30 |
| ALP-46 | 2002 | 100 → 95 | 7100 → 3000 | 91 → 84 | — | 205 → 135 | 88 → 62 |
| ALP-46A | 2011 | 100 → 110 | 7500 → 3400 | 92 → 84 | — | 228 → 158 | 92 → 66 |
| ALP-45DP | 2012 | 100 | 5360 / 3600 → 2600 / 1800 | 130 → 98 | — | 250 → 175 | 120 → 86 |
| PL42AC | 2006 | 100 → 90 | 4200 → 2000 | 130 → 96 | — | 188 → 128 | 112 → 78 |
| Comet V Coach | 2003 | 100 → 110 | — | 46 → 28 | 117 → 42 | 62 → 34 | 26 → 13 |
| Comet V Cab Car | 2003 | 100 → 110 | — | 47 → 29 | 109 → 38 | 70 → 38 | 28 → 14 |
| MultiLevel Coach | 2006 | 100 → 110 | — | 61 → 36 | 132 → 55 | 86 → 48 | 32 → 17 |
| MultiLevel Cab Car | 2006 | 100 → 110 | — | 63 → 37 | 127 → 52 | 94 → 52 | 34 → 18 |

**PATH — rapid transit**

| Vehicle | Intro | Speed mph | Power hp | Weight t | Capacity | Buy | Running |
| --- | --- | --- | --- | --- | --- | --- | --- |
| PATH PA1/PA2 (pair) | 1965 | 50 | 800 → 560 | 33 → 20 | 100 → 38 | 92 → 54 | 40 → 20 |
| PATH PA4 (pair) | 1987 | 55 | 1000 → 700 | 34 → 20 | 102 → 40 | 106 → 64 | 42 → 22 |
| PATH PA5 (pair) | 2011 | 55 → 60 | 1200 → 860 | 35 → 21 | 105 → 44 | 126 → 76 | 44 → 24 |

**Hudson-Bergen Light Rail**

| Vehicle | Intro | Speed mph | Power hp | Weight t | Capacity | Buy | Running |
| --- | --- | --- | --- | --- | --- | --- | --- |
| HBLR Light Rail | 2000 | 55 | 670 → 470 | 45 → 27 | 178 → 70 | 112 → 68 | 38 → 18 |

Power for the married pairs is carried on the lead car and applies to the set. Buy
and running are OpenTTD cost factors, not currency.

### Things worth knowing

- **Every railroad in its own paint.** Pennsylvania Brunswick green and Tuscan red,
  Erie Lackawanna grey-maroon-yellow, Jersey Central green, Lackawanna Pullman green,
  the U34CH's blue-and-silver Bluebird, NJ TRANSIT's 1980s chevron stripes, then
  today's silver, and PATH stainless with its black window band. At 32 pixels these
  are impressions, not reproductions.
- **Steam starts badly on purpose.** The K4s' tractive effort coefficient is struck
  against engine *and* tender weight, and a tender contributes nothing to adhesion —
  so it is fast once rolling and hopeless at getting a heavy train moving, which is
  much of why the E8s replaced it.
- **The ALP-45DP really is dual-power.** A power callback reads the railtype under
  the locomotive — full output on electrified track, diesel output everywhere else —
  and the exhaust switches from sparks to diesel smoke to match. Both stat sets get
  their own version of the callback.
- **EMUs come as married pairs.** The Arrow II, Arrow III and all three PATH classes
  are bought as articulated two-car sets. The MP54, DL&W MU and Arrow I ran as single
  cars and are modelled that way.
- **The light rail car is a tram, not a train.** The Hudson-Bergen car is
  double-articulated — three body sections over three trucks, with a bellows at each
  joint and the floor dropped between them. It is the one vehicle here that is a
  complete train on its own: buy one, or couple two or three the way the real line
  does.
- **Cab cars can be turned around.** CTRL+click a cab car in the depot to flip it so
  the cab faces the right way for push-pull running.
- **Catenary, third rail and trolley wire are the same thing here.** OpenTTD has one
  electrified railtype, so the GG1, MP54, DL&W MU, Arrows, ALP-44/46/46A, every PATH
  class and the HBLR car — 25 kV overhead, 600 volt third rail and a 750 volt trolley
  wire in reality — all need electrified track. Steam, diesels and all trailer cars
  run on plain track.
- **Vehicles expire.** Model lives follow the prototypes: the K4s is gone by 1958,
  the GG1 in 1983, the Arrow I in 1980, the DL&W MUs in 1984, the U34CH in 1995.

---

## Rebuilding from source

```sh
pip install nml pillow numpy
python3 gen_sprites.py     # sprites/*.png + sprite_preview.png
python3 gen_nml.py         # njtransit.pnml + lang/english.lng, from fleet.py
nmlc --grf njtransit.grf njtransit.pnml
python3 make_roster.py     # roster.png + roster_balanced.png
```

or just `make`.

**`fleet.py` is the single source of truth.** Every vehicle's two stat sets, dates,
flags, purchase text and sprite live there; the NML, the language file, the roster
images and the artifact pages are all generated from it. Change a number there and
rebuild — don't edit `njtransit.pnml`, it is overwritten.

### Adding real-world photographs

The published page links each vehicle to a photograph rather than reproducing one.
To embed your own instead, drop a file into `photos/` named after the vehicle's
`nml` id — `photos/gg1.jpg`, `photos/path_pa5_a.jpg`, and so on (`.jpg`, `.jpeg`,
`.png` and `.webp` all work) — and rebuild the page:

```sh
python3 make_pages.py
```

Each one is resized to 118 px wide, re-encoded as JPEG and embedded as a data URI,
so the page stays self-contained; the row switches from a text link to a thumbnail
beside the sprite. Put an attribution line in the `CREDITS` dict in `make_pages.py`
for anything you did not shoot yourself — it renders as a caption under the
thumbnail. Only publish photographs you own or that are licensed for it.

### How the sprites work

`gen_sprites.py` builds each vehicle as a little 3D model — boxes for carbodies,
roofs, bogies, hoods and pantographs, faceted prisms for boilers and arched
clerestory roofs, plus flat decals for windows, doors, corrugation and livery
stripes — and projects it into OpenTTD's isometric view for all eight vehicle
directions:

```
screen_x = (wy - wx) * 2
screen_y = (wy + wx) - wz
```

which is the same mapping OpenTTD uses internally (one tile = 16 world units =
64 × 32 px). Faces are back-face culled against the view direction (1, 1, 2), sorted
painter-style by paint layer then depth, shaded by the direction the face points,
rendered at 4× and downsampled with a mask-weighted filter so edges don't bleed the
background, then quantised to the OpenTTD DOS palette.

Because every direction is projected from the same model, consists line up exactly on
straight track and stay consistent through curves. Palette indices are restricted to
1–197, which keeps the liveries clear of the company-colour and animated-colour
ranges — a GG1 stays Tuscan red whatever colour your company is.

#### Vehicle length

Two different things are both called "length" here, and getting either one wrong
shows up as a sprite that overlaps its neighbour or as a train where every vehicle
looks the same size.

The first is a unit mistake: a tile is 16 world units, but a train vehicle is
*not*. OpenTTD's `VEHICLE_LENGTH` is 8 (`src/vehicle_type.h`) against a tile's
`TILE_SIZE` of 16, so a full-length 8/8 vehicle is **half a tile**, and the game
spaces consecutive vehicles by exactly the NML `length` property in world units —
not twice that. A sprite drawn to a full tile overlaps its neighbour by about 45%.

The second is coarseness: `length` is an integer from 1 to 8, so two prototypes of
quite different size often round to the same bucket — a 65 ft ALP-46 and an 85 ft
MultiLevel coach are both an 8/8 vehicle. Scaling every model to fill its bucket
draws the locomotive as long as the coach, which is what a set that only fixes the
first problem ends up looking like.

`fleet.py` carries a second figure per vehicle, `length_ft` — the published
prototype length over couplers — alongside the NML `length` bucket. The models are
built at roughly twice final scale, where a bogie is more than one unit long and
the detail work is easier to reason about, and `scale_to_length()` in
`gen_sprites.py` scales each one down to `length_ft` (converted to world units by a
fixed ft-per-unit ratio, calibrated so an 85 ft coach very nearly fills an 8/8
slot), capped at whatever the `length` bucket actually allows so a generous
`length_ft` estimate can never make a sprite overrun into the next vehicle. A short
engine in a bucket sized for something longer just shows more coupling gap around
it — which is the correct read: it *is* a short engine sharing a slot built for
something bigger.

Each sheet is 8 cells of 52 × 40 px at a common reference point (offsets −26, −26),
one cell per direction in the order N, NE, E, SE, S, SW, W, NW.

---

## Files

```
njtransit.grf         the compiled NewGRF — this is the file you install
fleet.py              the fleet table: both stat sets, dates, flags, purchase text
gen_sprites.py        sprite generator and the modern-stock models
historic.py           liveries and models for the 1914-1990 stock
gen_nml.py            generates njtransit.pnml and lang/english.lng
make_roster.py        renders roster.png and roster_balanced.png
make_pages.py         builds the two published HTML pages
photos/               optional: drop photos here to embed them in the roster
njtransit.pnml        generated NML source
lang/english.lng      generated names, purchase text and parameter strings
sprites/*.png         generated 8bpp sprite sheets, 32 of them
sprite_preview.png    every vehicle in every direction, 4x
roster.png            labelled roster, realistic figures
roster_balanced.png   labelled roster, balanced figures
Makefile              regenerate everything
```

---

## Sources and accuracy notes

Modern NJ TRANSIT and PATH:
[ALP-46 / ALP-46A](https://en.wikipedia.org/wiki/Bombardier_ALP-46),
[ALP-45DP](https://en.wikipedia.org/wiki/Bombardier_ALP-45DP),
[PL42AC](https://en.wikipedia.org/wiki/Alstom_PL42AC),
[Arrow](https://en.wikipedia.org/wiki/Arrow_(railcar)),
[Comet V](https://en.wikipedia.org/wiki/Comet_V),
[MultiLevel](https://en.wikipedia.org/wiki/Bombardier_MultiLevel_Coach),
[PATH](https://en.wikipedia.org/wiki/PATH_(rail_system)),
[PA5 order](https://www.railway-technology.com/projects/ny-path/),
[Hudson-Bergen Light Rail](https://en.wikipedia.org/wiki/Hudson%E2%80%93Bergen_Light_Rail).

Historical stock:
[PRR K4s](https://en.wikipedia.org/wiki/Pennsylvania_Railroad_class_K4) and
[Locobase test data](http://www.steamlocomotive.com/locobase.php?country=USA&wheel=4-6-2&railroad=prr),
[EMD E8](https://en.wikipedia.org/wiki/EMD_E8),
[ALCO RS-3](https://en.wikipedia.org/wiki/ALCO_RS-3),
[GE U34CH](https://en.wikipedia.org/wiki/GE_U34CH),
[PRR GG1](https://en.wikipedia.org/wiki/PRR_GG1),
[ABB ALP-44](https://en.wikipedia.org/wiki/ABB_ALP-44),
[PRR MP54](https://en.wikipedia.org/wiki/PRR_MP54),
[Erie Lackawanna MU cars](https://en.wikipedia.org/wiki/Erie_Lackawanna_MU_Cars),
[Comet](https://en.wikipedia.org/wiki/Comet_(railcar)),
[Erie 2103 Stillwell coach](https://rgvrrm.org/about/railroad/erie2103/),
[EL diesel roster](https://www.american-rails.com/eldiesel.html),
[Whippany Railway Museum on the Comet I](https://whippanyrailwaymuseum.net/equipment/comet/),
[the U34CH in service](https://www.trains.com/ctr/railroads/locomotives/nj-transit-ge-u34ch-diesel-locomotives/).

### Where the numbers are soft

Everything below is a judgement call, not a sourced figure. They are listed so you
can change them in `fleet.py` if you disagree:

- **K4s power** uses the published 3,286 hp, which is indicated cylinder horsepower,
  not power at the drawbar — the at-rail figure would be materially lower. Its
  weight is engine plus a Baldwin-batch tender; tender weights varied across the
  class.
- **U34CH weight and speed** are disputed in the sources: 364,800 lb vs 395,500 lb,
  and 70 mph vs 103 mph. The set uses 165 t and 70 mph.
- **MP54 and Arrow I weights, and Arrow I/II seating and Arrow II power** could not
  be verified; they are plausible values for cars of that size and era.
- **PATH per-car power and weight** are likewise estimates — published traction
  figures for the PA1/PA2, PA4 and PA5 are not readily available. PATH capacity
  counts standing riders, because that is how rapid transit capacity is measured;
  everything else is counted in seats.
- **HBLR power, weight and capacity** are the same kind of estimate: 670 hp for the
  four traction motors, 45 t and a 178-rider crush load are plausible figures for a
  90 ft double-articulated LRV rather than published NJ TRANSIT ones. Its capacity
  counts standing riders too. The 55 mph and the April 2000 opening are sourced.
- **Comet I and Comet II weights, and Comet II seating**, rest on the Comet family
  range rather than per-series figures.
- **The Stillwell coach's livery is a guess.** No source reached describes the Erie
  commuter coach scheme; the set uses the dark green with gold lettering that Erie
  passenger equipment generally wore.
- **Arrow III seating** is rounded to 120 per car, and its realistic speed is the
  as-built 100 mph rather than the 80 mph it was later restricted to.
- Modern realistic speeds are capped at NJ TRANSIT's 100 mph operating limit even
  where the equipment is certified higher.

This is a fan-made set for a game, not affiliated with or endorsed by NJ TRANSIT,
the Port Authority of New York and New Jersey, or any of the railroads represented.
