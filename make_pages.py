#!/usr/bin/env python3
"""Builds the two artifact pages from the fleet table and the sprite sheets."""

import base64
import io
import math
import os

import numpy as np
from PIL import Image
from nml import palette as nmlpal

from fleet import BY_ID, GROUPS, ROSTER_ORDER, figures

CW, CH, OX, OY = 52, 40, 26, 26
PAL = np.array(nmlpal.raw_palette_data[0]).reshape(256, 3)
SPRITE_SCALE = 3
_sheets = {}


# ------------------------------------------------------------------ sprites --

def cell(name, d):
    if name not in _sheets:
        _sheets[name] = np.array(Image.open("sprites/%s.png" % name))
    return _sheets[name][:, d * CW:(d + 1) * CW]


def rgba(idx):
    return np.dstack([PAL[idx].astype(np.uint8), ((idx != 0) * 255).astype(np.uint8)])


def crop(a):
    ys, xs = np.nonzero(a[..., 3])
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def uri(a):
    im = Image.fromarray(a, "RGBA")
    b = io.BytesIO()
    im.save(b, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(b.getvalue()).decode()


def sprite_img(sprite, direction=5, alt=""):
    a = crop(rgba(cell(sprite, direction)))
    h, w = a.shape[:2]
    return '<img src="{}" width="{}" height="{}" alt="{}">'.format(
        uri(a), w * SPRITE_SCALE, h * SPRITE_SCALE, alt)


def consist(items, direction=3, pad=4):
    """Lay a train out the way OpenTTD does: each vehicle sits `length` world
    units behind the one in front - length is in eighths of VEHICLE_LENGTH, and
    VEHICLE_LENGTH is half a tile, so the step is `length`, not 2 x `length`."""
    phi = math.radians(225 - 45 * direction)
    c, s = math.cos(phi), math.sin(phi)
    pts, pos, depth = [], np.array([0.0, 0.0]), 0.0
    for sprite, length in items:
        pts.append((sprite, pos.copy(), depth))
        wx, wy = -c * length, -s * length
        pos = pos + np.array([(wy - wx) * 2.0, (wy + wx)])
        depth += wx + wy
    xs = [p[1][0] for p in pts]
    ys = [p[1][1] for p in pts]
    W = int(max(xs) - min(xs)) + CW + pad * 2
    H = int(max(ys) - min(ys)) + CH + pad * 2
    cv = np.zeros((H, W, 4), dtype=np.uint8)
    ox, oy = -int(min(xs)) + pad, -int(min(ys)) + pad
    # far to near along the (1, 1, 2) view direction, so the vehicle nearest the
    # camera wins the overlap - which of the two ends that is depends on which
    # way the train is pointing, so sort rather than assume.
    for sprite, pt, d in sorted(pts, key=lambda p: p[2]):
        a = rgba(cell(sprite, direction))
        x0, y0 = int(round(pt[0])) + ox, int(round(pt[1])) + oy
        yy, xx = np.nonzero(a[..., 3])
        for Y, X in zip(yy, xx):
            cv[y0 + Y, x0 + X] = a[Y, X]
    return crop(cv)


def hero_img(items, alt, scale=3, direction=3):
    a = consist(items, direction)
    h, w = a.shape[:2]
    return '<img src="{}" width="{}" height="{}" alt="{}">'.format(
        uri(a), w * scale, h * scale, alt)


# --------------------------------------------------------------------- CSS --

def css(accent_light, accent_dark, accent_wash_l, accent_wash_d,
        extra=""):
    return """
  :root {
    --ground:   #ebeef2;
    --surface:  #ffffff;
    --ink:      #161a21;
    --muted:    #5b6472;
    --faint:    #858e9c;
    --line:     #d4d9e1;
    --accent:   %s;
    --accent-w: %s;
    --orange:   #d9690f;
    --shadow:   0 1px 2px rgba(20, 26, 40, .06), 0 8px 24px rgba(20, 26, 40, .05);
  }
  @media (prefers-color-scheme: dark) {
    :root:not([data-theme="light"]) {
      --ground:   #0f1319;
      --surface:  #161b23;
      --ink:      #e8edf4;
      --muted:    #98a3b2;
      --faint:    #6f7a89;
      --line:     #252d39;
      --accent:   %s;
      --accent-w: %s;
      --orange:   #f0902f;
      --shadow:   0 1px 2px rgba(0, 0, 0, .4), 0 10px 28px rgba(0, 0, 0, .28);
    }
  }
  :root[data-theme="dark"] {
    --ground:   #0f1319;
    --surface:  #161b23;
    --ink:      #e8edf4;
    --muted:    #98a3b2;
    --faint:    #6f7a89;
    --line:     #252d39;
    --accent:   %s;
    --accent-w: %s;
    --orange:   #f0902f;
    --shadow:   0 1px 2px rgba(0, 0, 0, .4), 0 10px 28px rgba(0, 0, 0, .28);
  }

  * { box-sizing: border-box; }

  body {
    margin: 0;
    background: var(--ground);
    color: var(--ink);
    font-family: "IBM Plex Sans", ui-sans-serif, system-ui, sans-serif;
    font-size: 16px;
    line-height: 1.62;
    -webkit-font-smoothing: antialiased;
  }

  .wrap { max-width: 880px; margin: 0 auto; padding: 56px 24px 88px; }

  h1, h2, h3 { font-family: "Barlow Semi Condensed", "IBM Plex Sans", sans-serif; text-wrap: balance; margin: 0; }
  h1 { font-size: clamp(38px, 7vw, 58px); font-weight: 700; letter-spacing: -.01em; line-height: 1.02; }
  h2 { font-size: 27px; font-weight: 600; letter-spacing: .01em; }
  h3 { font-size: 19px; font-weight: 600; }

  .eyebrow {
    font-family: "Barlow Semi Condensed", sans-serif;
    font-size: 14px; font-weight: 600;
    letter-spacing: .2em; text-transform: uppercase;
    color: var(--orange); margin: 0 0 10px;
  }
  .lede { font-size: 18px; color: var(--muted); margin: 14px 0 0; max-width: 62ch; }

  .stripe {
    height: 7px; border: 0; margin: 30px 0 0;
    background:
      linear-gradient(#1b44c8, #1b44c8) top / 100%% 4px no-repeat,
      linear-gradient(#d9690f, #d9690f) bottom / 100%% 2px no-repeat;
  }

  .hero {
    margin: 26px 0 0; padding: 22px 18px 16px;
    background: var(--surface); border: 1px solid var(--line);
    border-radius: 3px; box-shadow: var(--shadow); overflow-x: auto;
  }
  .hero img { display: block; margin: 0 auto; image-rendering: pixelated; }
  .hero figcaption {
    margin-top: 14px; text-align: center;
    font-family: "IBM Plex Mono", monospace; font-size: 12px; color: var(--faint);
  }

  .meta {
    display: flex; flex-wrap: wrap; gap: 8px;
    list-style: none; padding: 0; margin: 22px 0 0;
    font-family: "IBM Plex Mono", monospace; font-size: 12.5px;
  }
  .meta li {
    border: 1px solid var(--line); border-radius: 2px;
    padding: 4px 9px; color: var(--muted); background: var(--surface);
  }

  section { margin-top: 54px; }
  section > h2 { display: flex; align-items: baseline; gap: 12px; }
  section > h2::after { content: ""; flex: 1; height: 1px; background: var(--line); }
  section > p { max-width: 65ch; }

  ol.steps { margin: 18px 0 0; padding-left: 20px; }
  ol.steps li { margin-bottom: 8px; }
  code {
    font-family: "IBM Plex Mono", monospace; font-size: 13.5px;
    background: var(--accent-w); color: var(--ink);
    padding: 1px 5px; border-radius: 2px;
  }

  .paths { margin-top: 20px; overflow-x: auto; }
  table { border-collapse: collapse; width: 100%%; font-size: 14.5px; }
  .paths th, .paths td { text-align: left; padding: 9px 14px 9px 0; border-bottom: 1px solid var(--line); white-space: nowrap; }
  .paths th { font-family: "Barlow Semi Condensed", sans-serif; font-size: 13px; letter-spacing: .12em; text-transform: uppercase; color: var(--faint); font-weight: 600; }
  .paths td:last-child { font-family: "IBM Plex Mono", monospace; font-size: 13px; color: var(--muted); }

  .group {
    font-family: "Barlow Semi Condensed", sans-serif; font-size: 14px;
    letter-spacing: .16em; text-transform: uppercase; color: var(--faint);
    font-weight: 600; margin: 26px 0 8px;
  }
  .roster { display: flex; flex-direction: column; gap: 2px; }
  .unit {
    display: grid; grid-template-columns: 132px 1fr; gap: 4px 20px;
    align-items: center; padding: 16px 18px;
    background: var(--surface); border: 1px solid var(--line); border-radius: 3px;
  }
  .unit img { image-rendering: pixelated; display: block; }
  .unit .name { font-family: "Barlow Semi Condensed", sans-serif; font-size: 22px; font-weight: 600; line-height: 1.15; margin: 0; }
  .unit .role { font-size: 14px; color: var(--muted); margin: 2px 0 0; }
  .unit .figures {
    margin: 8px 0 0; padding: 0; list-style: none;
    display: flex; flex-wrap: wrap; gap: 4px 16px;
    font-family: "IBM Plex Mono", monospace; font-size: 12.5px;
    font-variant-numeric: tabular-nums; color: var(--muted);
  }
  .unit.has-photo { grid-template-columns: 132px 118px 1fr; }
  .unit .photo { margin: 0; }
  .unit .photo img {
    display: block; width: 118px; height: auto; border-radius: 2px;
    border: 1px solid var(--line);
  }
  .unit .photo figcaption {
    font-family: "IBM Plex Mono", monospace; font-size: 10px; line-height: 1.35;
    color: var(--faint); margin-top: 4px; max-width: 118px;
  }
  .unit .ref {
    font-family: "IBM Plex Mono", monospace; font-size: 11.5px;
    letter-spacing: .04em; white-space: nowrap; margin-left: 8px;
    text-decoration: none; border-bottom: 1px solid var(--accent-w);
  }
  .unit .ref:hover { border-bottom-color: var(--accent); }
  .unit .figures .cat { color: var(--accent); }
  .unit .figures .seats { color: var(--orange); }

  .notes { display: grid; gap: 20px; margin-top: 22px; }
  .note { border-left: 3px solid var(--accent); padding-left: 16px; }
  .note h3 { margin-bottom: 2px; }
  .note p { margin: 0; color: var(--muted); max-width: 62ch; }

  pre {
    margin: 20px 0 0; padding: 16px 18px; overflow-x: auto;
    background: var(--surface); border: 1px solid var(--line); border-radius: 3px;
    font-family: "IBM Plex Mono", monospace; font-size: 13px; line-height: 1.7;
    color: var(--ink);
  }
  pre .c { color: var(--faint); }

  footer { margin-top: 64px; padding-top: 22px; border-top: 1px solid var(--line); color: var(--faint); font-size: 13.5px; }
  footer p { margin: 0 0 8px; max-width: 66ch; }
  a { color: var(--accent); text-decoration-thickness: 1px; text-underline-offset: 2px; }
  a:focus-visible { outline: 2px solid var(--accent); outline-offset: 3px; }

  @media (max-width: 560px) {
    .unit { grid-template-columns: 1fr; }
    .unit img { margin-bottom: 6px; }
  }
%s""" % (accent_light, accent_wash_l, accent_dark, accent_wash_d,
         accent_dark, accent_wash_d, extra)


FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
         'family=Barlow+Semi+Condensed:wght@500;600;700&'
         'family=IBM+Plex+Mono:wght@400;500&'
         'family=IBM+Plex+Sans:wght@400;500;600&display=swap">\n')


PHOTO_W = 118          # thumbnail width on the page, in CSS pixels


def photo_block(v):
    """A supplied photograph if one exists in photos/, else a link to one."""
    for ext in ("jpg", "jpeg", "png", "webp"):
        path = os.path.join("photos", "%s.%s" % (v["nml"], ext))
        if os.path.exists(path):
            im = Image.open(path).convert("RGB")
            im.thumbnail((PHOTO_W * 2, PHOTO_W * 2), Image.LANCZOS)
            b = io.BytesIO()
            im.save(b, "JPEG", quality=78, optimize=True)
            data = "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()
            credit = CREDITS.get(v["nml"], "")
            fig = ('<figure class="photo"><img src="%s" alt="%s, the real vehicle">'
                   % (data, v["name"]))
            if credit:
                fig += '<figcaption>%s</figcaption>' % credit
            return fig + "</figure>", True
    if v.get("photo"):
        return ('<a class="ref" href="%s" target="_blank" rel="noopener">photo &#8599;'
                '</a>' % v["photo"]), False
    return "", False


# Attribution lines for any photographs dropped into photos/. Fill these in
# before publishing anyone else's work.
CREDITS = {}


def unit_row(v, mode):
    figs = figures(v, mode)
    lis = ""
    for f in figs:
        cls = ""
        if "track" in f or "catenary" in f or "road" in f:
            cls = ' class="cat"'
        elif "seat" in f or "rider" in f:
            cls = ' class="seats"'
        lis += "<li%s>%s</li>" % (cls, f)
    photo, embedded = photo_block(v)
    ref = "" if embedded else photo
    return """      <article class="unit%s">
        %s
        %s
        <div>
          <p class="name">%s</p>
          <p class="role">%s%s</p>
          <ul class="figures">%s</ul>
        </div>
      </article>""" % (" has-photo" if embedded else "",
                       sprite_img(v["sprite"], alt=v["name"] + " sprite"),
                       photo if embedded else "",
                       v["name"], v["role"],
                       (" " + ref) if ref else "", lis)


# ------------------------------------------------------------- page one --

def build_main(balanced_url):
    hero = hero_img([("hist_k4s", 8), ("hist_stillwell", 6), ("hist_stillwell", 6),
                     ("hist_stillwell", 6)],
                    "A PRR K4s Pacific with three Stillwell commuter coaches")
    hero2 = hero_img([("hist_u34ch", 7), ("hist_comet1", 8), ("hist_comet1", 8),
                      ("hist_comet1_cab", 8)],
                     "A U34CH with Comet I coaches", direction=1)
    hero3 = hero_img([("njt_alp46", 7), ("njt_ml", 8), ("njt_ml", 8),
                      ("njt_ml_cab", 8)],
                     "An ALP-46 hauling three MultiLevel cars", direction=5)
    hero4 = hero_img([("bus_nabi416", 8), ("bus_xd60_a", 7), ("bus_xd60_b", 4)],
                     "A NABI 416.15 and a New Flyer XD60 articulated bus",
                     direction=5)

    roster_html = ""
    for title, keys in GROUPS:
        roster_html += '    <p class="group">%s</p>\n    <div class="roster">\n' % title
        roster_html += "\n".join(unit_row(BY_ID[k], "real") for k in keys)
        roster_html += "\n    </div>\n"
        if title.startswith("Transition"):
            roster_html += ('    <figure class="hero">%s<figcaption>A U34CH and '
                            'Comet I set, the 1970s Bergen County look'
                            '</figcaption></figure>\n' % hero2)
        if title.startswith("Modern"):
            roster_html += ('    <figure class="hero">%s<figcaption>ALP-46 with '
                            'MultiLevels</figcaption></figure>\n' % hero3)
        if title.startswith("Buses — modern"):
            roster_html += ('    <figure class="hero">%s<figcaption>A NABI 416.15 '
                            'beside an XD60, whose rear section is a hidden '
                            'articulated part</figcaption></figure>\n' % hero4)

    body = """<title>NJ TRANSIT Vehicle Set</title>
%s
<style>%s</style>

<div class="wrap">

  <header>
    <p class="eyebrow">OpenTTD · NewGRF</p>
    <h1>NJ TRANSIT Vehicle Set</h1>
    <p class="lede">Thirty-eight vehicles covering a century of New Jersey transit:
      a PRR K4s Pacific and Erie Lackawanna diesels, the GG1 through to its last run in
      1983, NJ TRANSIT's modern fleet, three generations of PATH rapid transit, the
      Hudson-Bergen light rail car — and eleven buses, from a 1935 Public Service
      All-Service Vehicle to a battery-electric Xcelsior. Each in its own operator's
      livery, with real figures and a switch for people who would rather have balanced
      ones.</p>
    <hr class="stripe">
    <figure class="hero">
      %s
      <figcaption>PRR K4s Pacific and Stillwell coaches, 1950</figcaption>
    </figure>
    <ul class="meta">
      <li>27 vehicles</li>
      <li>1914 – 2012</li>
      <li>Realistic or balanced stats</li>
      <li>Built with NML 0.9</li>
      <li>Verified in OpenTTD 13.4</li>
    </ul>
  </header>

  <section>
    <h2>Install</h2>
    <ol class="steps">
      <li>Put <code>njtransit.grf</code> in your OpenTTD <code>newgrf</code> folder.</li>
      <li>Open <strong>Game Options → NewGRF Settings</strong>, add it to the active list, and apply.</li>
      <li>Start a new game. The set only adds vehicles, so it can also be added to a
          save in progress — engines appear from their introduction dates onwards.</li>
    </ol>
    <div class="paths">
      <table>
        <thead><tr><th>Platform</th><th>Folder</th></tr></thead>
        <tbody>
          <tr><td>Windows</td><td>%%USERPROFILE%%\\Documents\\OpenTTD\\newgrf\\</td></tr>
          <tr><td>macOS</td><td>~/Documents/OpenTTD/newgrf/</td></tr>
          <tr><td>Linux</td><td>~/.local/share/openttd/newgrf/</td></tr>
        </tbody>
      </table>
    </div>
  </section>

  <section>
    <h2>The roster</h2>
    <p>Figures below are the prototype's own. Tractive effort comes from published
      starting effort over locomotive weight, so the electrics get heavy trains moving
      noticeably better than the diesels do — and the K4s, with all that weight in a
      tender it cannot use for adhesion, starts worst of all. Each entry links out to
      a photograph of the real vehicle; this page reproduces nobody's photography.</p>
%s
  </section>

  <section>
    <h2>Realistic or balanced</h2>
    <p>The GRF ships both stat sets. In <strong>NewGRF Settings → Parameters</strong>,
      <em>Statistics</em> switches between the published prototype figures above and a
      game-balanced set that scales capacity, power, speed and cost so the fleet sits
      alongside OpenTTD's own vehicles instead of outclassing them. OpenTTD resolves
      the choice when the GRF loads, so set it before starting a game.</p>
    <p><a href="%s">See what changes, vehicle by vehicle →</a></p>
  </section>

  <section>
    <h2>Details worth knowing</h2>
    <div class="notes">
      <div class="note">
        <h3>The ALP-45DP really is dual-power</h3>
        <p>A power callback reads the railtype under the locomotive: full output on
          electrified track, diesel output everywhere else, with the exhaust switching
          from sparks to diesel smoke to match.</p>
      </div>
      <div class="note">
        <h3>EMUs come as married pairs</h3>
        <p>The Arrow III and all three PATH classes are bought as articulated two-car
          sets, the way they actually run. The PA1/PA2 and PA5 pair a cab car with a
          cabless C car; the PA4, being all cab cars, has a cab at each end.</p>
      </div>
      <div class="note">
        <h3>Every railroad in its own paint</h3>
        <p>Pennsylvania Brunswick green and Tuscan red, Erie Lackawanna grey-maroon-
          yellow, Jersey Central green, Lackawanna Pullman green, the U34CH's blue-and-
          silver Bluebird, NJ TRANSIT's 1980s chevron stripes and then today's silver.
          At 32 pixels these are impressions rather than reproductions.</p>
      </div>
      <div class="note">
        <h3>The light rail car is a tram, not a train</h3>
        <p>The Hudson-Bergen car is double-articulated: three body sections over three
          trucks, with a bellows at each joint and the floor dropped between them. It is
          the one vehicle in the set that is a complete train on its own — buy one, or
          couple two or three the way the real line does.</p>
      </div>
      <div class="note">
        <h3>The buses are road vehicles, not trams</h3>
        <p>All eleven run on ordinary road, so towns build their own network for them
          and nothing needs electrifying. The Volvo B10M and the New Flyer XD60 are
          sixty-footers built the same way the EMU married pairs are: a visible front
          section that pulls a hidden rear section in behind it, bought and sold as one
          vehicle. The 1935 All-Service Vehicle really did draw from trolley wire where
          Public Service had strung it and run as a gas-electric where it had not —
          the ALP-45DP's trick, fifty years earlier — but OpenTTD has nowhere to put
          that, so it is simply a bus that goes anywhere.</p>
      </div>
      <div class="note">
        <h3>Buses are drawn on their own scale</h3>
        <p>A tile is a tile whichever vehicle is on it, but a 40 ft bus at the rail
          scale would be about seven pixels long — too few for a windscreen, a door and
          three window bays. OpenTTD's own artwork makes the same concession. So the
          buses are calibrated against each other, with a 45 ft highway coach filling
          the slot an 85 ft rail coach fills. Within the road fleet the lengths are
          honest; against the trains they are generous.</p>
      </div>
      <div class="note">
        <h3>Cab cars turn around</h3>
        <p>CTRL+click a cab car in the depot to flip it, so the cab faces the right way
          for push-pull running.</p>
      </div>
      <div class="note">
        <h3>Catenary and third rail are the same thing here</h3>
        <p>OpenTTD has one electrified railtype, so 25 kV catenary, PATH's third rail
          and the light rail car's 750 volt trolley wire are all the same thing here:
          the ALP-46, ALP-46A, Arrow III, every PATH class and the HBLR car all need
          electrified track. The PL42AC, ALP-45DP and the trailer cars run on plain
          track too.</p>
      </div>
    </div>
  </section>

  <section>
    <h2>How the sprites were drawn</h2>
    <p>Nothing was pixelled by hand. Each vehicle is a small 3D model — boxes for
      carbody, roof, bogies and pantographs, flat decals for windows, doors,
      corrugation and stripes — projected into OpenTTD's own isometric mapping for all
      eight directions:</p>
    <pre><span class="c"># one tile = 16 world units = 64 x 32 px</span>
screen_x = (wy - wx) * 2
screen_y = (wy + wx) - wz</pre>
    <p style="margin-top:18px">A tile is 16 world units, but a train vehicle is not.
      OpenTTD's <code>VEHICLE_LENGTH</code> is 8 against a tile's 16, so a full-length
      8/8 vehicle is half a tile and the game spaces vehicles by the
      <code>length</code> property in world units — not twice it.</p>
    <p style="margin-top:18px">That property is also coarse: an integer from 1 to 8,
      so a 65 ft locomotive and an 85 ft coach can round to the same bucket. Each
      vehicle is drawn to its own published length instead of stretched to fill
      whatever bucket it landed in, capped at what the bucket actually allows so a
      generous estimate can never make a sprite overrun into the next vehicle — a
      short engine just shows a little more coupling gap, which is the correct
      read for a short engine.</p>
    <p style="margin-top:18px">Faces are back-face culled against the view direction,
      painted in layer then depth order, shaded by the direction each face points,
      rendered at 4× and downsampled with a mask-weighted filter so edges don't bleed,
      then quantised to the OpenTTD DOS palette. Because every direction comes from the
      same model, consists line up exactly on straight track. Palette indices stay
      inside 1–197, which keeps the liveries clear of the company-colour range — the
      trains stay NJ TRANSIT silver and PATH stainless whatever colour your company
      is.</p>
  </section>

  <footer>
    <p>Fan-made set for a game. Not affiliated with or endorsed by NJ TRANSIT or the
      Port Authority of New York and New Jersey.</p>
    <p>Figures from published specifications:
      <a href="https://en.wikipedia.org/wiki/Bombardier_ALP-46">ALP-46 / ALP-46A</a>,
      <a href="https://en.wikipedia.org/wiki/Bombardier_ALP-45DP">ALP-45DP</a>,
      <a href="https://en.wikipedia.org/wiki/Alstom_PL42AC">PL42AC</a>,
      <a href="https://en.wikipedia.org/wiki/Arrow_(railcar)">Arrow III</a>,
      <a href="https://en.wikipedia.org/wiki/Comet_V">Comet V</a>,
      <a href="https://en.wikipedia.org/wiki/Bombardier_MultiLevel_Coach">MultiLevel</a>,
      <a href="https://en.wikipedia.org/wiki/PATH_(rail_system)">PATH</a>,
      <a href="https://en.wikipedia.org/wiki/Hudson%%E2%%80%%93Bergen_Light_Rail">Hudson-Bergen
      Light Rail</a>.
      Arrow III seating is rounded to 120 per car; PATH and HBLR per-car power and
      weight are estimates, since published figures for those are not readily available,
      and their capacity counts standing riders because that is how rapid transit is
      measured.</p>
  </footer>

</div>
""" % (FONTS, css("#1b44c8", "#7ba2ff", "#e4e9fa", "#1a2540"),
       hero, roster_html, balanced_url)
    open("njtransit_page.html", "w").write(body)
    print("njtransit_page.html", len(body) // 1024, "KB")


# ------------------------------------------------------------- page two --

RULES = [
    ("&times;0.40", "Capacity",
     "A full-length car lands near OpenTTD's own 40-passenger carriage instead of "
     "tripling it. A MultiLevel still tops the roster, at 55 rather than 132."),
    ("&times;0.45", "Power",
     "The strongest electric makes 3,400 hp instead of 7,500, so an ALP-46A leads a "
     "heavy train well without making every base-set engine pointless."),
    ("&times;0.6 / 0.9", "Weight",
     "Trailers lose about 40% so the lighter power can still accelerate them; "
     "locomotives keep most of theirs, because tractive effort is struck off weight."),
    ("50 → 110", "Speed",
     "Instead of a flat 100 mph across thirty years of equipment, speed becomes a "
     "progression: 1965 PATH cars at 50, the Arrow III at 80, the ALP-46A at 110."),
]


def metric_cells(v):
    r, b = v["real"], v["bal"]
    def pair(rv, bv, suffix=""):
        same = rv == bv
        cls = "same" if same else "chg"
        return ('<td class="%s"><span class="was">%s</span>'
                '<span class="arrow">→</span><span class="now">%s%s</span></td>'
                % (cls, rv, bv, suffix))
    cells = pair(r["speed"], b["speed"])
    if v.get("dual"):
        cells += pair("%s / %s" % v["dual"]["real"], "%s / %s" % v["dual"]["bal"])
    else:
        cells += pair(r["power"], b["power"]) if r["power"] or b["power"] else '<td class="none">—</td>'
    cells += pair(r["weight"], b["weight"])
    cells += pair(r["cap"], b["cap"]) if r["cap"] else '<td class="none">—</td>'
    cells += pair(r["cost"], b["cost"])
    cells += pair(r["run"], b["run"])
    return cells


def build_balanced(main_url):
    table = ""
    for title, keys in GROUPS:
        table += ('        <tr class="grp"><th colspan="7" scope="colgroup">%s</th>'
                  '</tr>\n' % title)
        for k in keys:
            v = BY_ID[k]
            tag = ""
            if v["nml"].startswith("path_"):
                tag = ' <span class="tag">PATH</span>'
            elif v["nml"].startswith("hblr_"):
                tag = ' <span class="tag">LIGHT RAIL</span>'
            elif v["feature"] == "road":
                tag = ' <span class="tag">BUS</span>'
            table += ('        <tr><th scope="row">%s%s</th>%s</tr>\n'
                      % (v["name"], tag, metric_cells(v)))

    rule_cards = "\n".join(
        '      <div class="rule"><p class="mult">%s</p><h3>%s</h3><p>%s</p></div>'
        % r for r in RULES)

    extra_css = """
  .rules { display: grid; grid-template-columns: repeat(auto-fit, minmax(186px, 1fr)); gap: 2px; margin-top: 24px; }
  .rule { background: var(--surface); border: 1px solid var(--line); border-radius: 3px; padding: 16px 16px 18px; }
  .rule .mult {
    font-family: "IBM Plex Mono", monospace; font-size: 20px; font-weight: 500;
    color: var(--accent); margin: 0 0 6px; font-variant-numeric: tabular-nums;
  }
  .rule h3 { font-size: 17px; margin-bottom: 4px; }
  .rule p { margin: 0; color: var(--muted); font-size: 14px; line-height: 1.55; }

  .cmp { margin-top: 24px; overflow-x: auto; border: 1px solid var(--line); border-radius: 3px; background: var(--surface); }
  .cmp table { font-size: 13.5px; font-variant-numeric: tabular-nums; }
  .cmp th, .cmp td { padding: 10px 9px; border-bottom: 1px solid var(--line); text-align: right; white-space: nowrap; }
  .cmp thead th {
    font-family: "Barlow Semi Condensed", sans-serif; font-size: 12.5px;
    letter-spacing: .12em; text-transform: uppercase; color: var(--faint);
    font-weight: 600; text-align: right; position: sticky; top: 0; background: var(--surface);
  }
  .cmp tbody th, .cmp thead th:first-child { text-align: left; padding-left: 14px; font-family: "Barlow Semi Condensed", sans-serif; font-size: 17px; font-weight: 600; color: var(--ink); }
  .cmp tbody tr:last-child th, .cmp tbody tr:last-child td { border-bottom: 0; }
  .cmp .was { color: var(--faint); }
  .cmp .arrow { color: var(--line); padding: 0 4px; }
  .cmp .now { color: var(--accent); font-weight: 500; }
  .cmp .same .now { color: var(--muted); font-weight: 400; }
  .cmp .none { color: var(--line); }
  .cmp .tag { font-family: "IBM Plex Mono", monospace; font-size: 10.5px; letter-spacing: .1em; color: #d63c3e; vertical-align: 2px; margin-left: 6px; }
  .units { font-family: "IBM Plex Mono", monospace; font-size: 12px; color: var(--faint); margin-top: 10px; }
  .cmp tr.grp th {
    font-family: "Barlow Semi Condensed", sans-serif; font-size: 12.5px;
    letter-spacing: .14em; text-transform: uppercase; color: var(--faint);
    font-weight: 600; text-align: left; padding-top: 20px; background: var(--surface);
  }
"""

    body = """<title>Rebalanced Fleet</title>
%s
<style>%s</style>

<div class="wrap">

  <header>
    <p class="eyebrow">NJ TRANSIT + PATH Trainset · Parameter</p>
    <h1>Rebalanced Fleet</h1>
    <p class="lede">The realistic figures make an honest model and an overpowered
      NewGRF: a single MultiLevel carries three vanilla carriages' worth of passengers,
      an ALP-46A out-muscles anything in the base set, and a K4s Pacific arrives in 1914
      with 3,286 horsepower. This is the same twenty-seven vehicles with the numbers
      re-struck for play — and what each one becomes.</p>
    <hr class="stripe">
    <ul class="meta">
      <li>NewGRF parameter</li>
      <li>Statistics: Game-balanced</li>
      <li>Same sprites, dates and liveries</li>
      <li>27 vehicles, 1914 – 2012</li>
    </ul>
  </header>

  <section>
    <h2>Turning it on</h2>
    <ol class="steps">
      <li>In <strong>NewGRF Settings</strong>, select the trainset and open
          <strong>Parameters</strong>.</li>
      <li>Set <strong>Statistics</strong> to <em>Game-balanced</em>.</li>
      <li>Do it before starting the game. OpenTTD resolves the parameter while the GRF
          loads, so changing it mid-game needs a restart.</li>
    </ol>
    <p style="margin-top:18px">Under the hood the GRF carries both stat sets. The
      balanced values sit behind an <code>if (stats == 1)</code> block, which compiles
      to an Action 7 skip: with the parameter at 0 OpenTTD steps straight over them and
      the realistic properties stand.</p>
  </section>

  <section>
    <h2>The four rules</h2>
    <p>Every balanced number on the rail side comes from one of these, applied across
      the whole roster rather than tuned vehicle by vehicle — so the fleet keeps its
      internal shape: an Arrow III is still the poor relation of a MultiLevel, and a
      1950 RS-3 still can't touch a GG1.</p>
    <div class="rules">
%s
    </div>
    <p style="margin-top:20px">Purchase and running costs are then re-struck against
      the new capacity and power, so cost per seat stays roughly level across the set
      and against the base game. Dates, lengths, tractive effort coefficients, air drag,
      reliability and every sprite are untouched: those are facts about the vehicle, not
      balance knobs.</p>
    <p style="margin-top:20px">The buses barely move between the two settings, and the
      reason is worth saying plainly: a real transit bus is already about the size of an
      OpenTTD road vehicle. A 53-seat fishbowl against a vanilla bus's 31 is nothing
      like a MultiLevel's 132 against a vanilla carriage's 40, so the road fleet gets
      its own gentler rules — capacity &times;0.65, power &times;0.60, weight
      &times;0.75, and a 30 → 65 mph ladder that puts city buses under highway
      coaches. Cutting them by the rail figures would have left a forty-foot bus
      carrying fewer people than the base set's.</p>
  </section>

  <section>
    <h2>Vehicle by vehicle</h2>
    <div class="cmp">
      <table>
        <thead>
          <tr>
            <th scope="col">Vehicle</th>
            <th scope="col">Speed</th>
            <th scope="col">Power</th>
            <th scope="col">Weight</th>
            <th scope="col">Capacity</th>
            <th scope="col">Buy</th>
            <th scope="col">Run</th>
          </tr>
        </thead>
        <tbody>
%s        </tbody>
      </table>
    </div>
    <p class="units">realistic → balanced · speed mph · power hp (electric/diesel for
      the ALP-45DP) · weight tonnes per car · capacity per car · buy and running are
      OpenTTD cost factors</p>
  </section>

  <section>
    <h2>What it feels like</h2>
    <div class="notes">
      <div class="note">
        <h3>A rush-hour MultiLevel train</h3>
        <p>Six MultiLevels behind an ALP-46A carry 330 passengers instead of 800 — still
          the biggest thing on your network, but a busy station now needs more than one
          train an hour.</p>
      </div>
      <div class="note">
        <h3>PATH stays a metro</h3>
        <p>A PA5 pair costs less than two MultiLevel coaches and carries 88 riders at
          60 mph in half the train length. Short, cheap and frequent is what these are
          for, and the balanced costs reward running them that way.</p>
      </div>
      <div class="note">
        <h3>Speed becomes a reason to upgrade</h3>
        <p>With everything at a flat 100 mph the newer equipment only differed on paper.
          At 50 / 65 / 80 / 95 / 110 the fleet has an actual generational ladder, and
          holding on to 1950s stock costs you something.</p>
      </div>
      <div class="note">
        <h3>Steam stays awkward, on purpose</h3>
        <p>The K4s keeps its low tractive effort coefficient in both modes — all that
          weight sits in a tender that contributes nothing to adhesion. It is fast once
          rolling and hopeless at starting a heavy train, which is exactly why the E8s
          replaced it.</p>
      </div>
    </div>
  </section>

  <footer>
    <p><a href="%s">← Back to the trainset, install steps and full roster</a></p>
    <p>Fan-made set for a game. Not affiliated with or endorsed by NJ TRANSIT or the
      Port Authority of New York and New Jersey.</p>
  </footer>

</div>
""" % (FONTS, css("#0f7a6b", "#4fc7b0", "#dff0ec", "#12302c", extra_css),
       rule_cards, table, main_url)
    open("njtransit_balanced_page.html", "w").write(body)
    print("njtransit_balanced_page.html", len(body) // 1024, "KB")


if __name__ == "__main__":
    import sys
    main_url = sys.argv[1] if len(sys.argv) > 1 else "#"
    bal_url = sys.argv[2] if len(sys.argv) > 2 else "#"
    build_main(bal_url)
    build_balanced(main_url)
