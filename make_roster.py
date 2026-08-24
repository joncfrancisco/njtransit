#!/usr/bin/env python3
"""Render labelled roster images for both stat sets."""

import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from nml import palette as nmlpal

from fleet import BY_ID, GROUPS, figures

CW, CH = 52, 40
SCALE = 4
PAL = np.array(nmlpal.raw_palette_data[0]).reshape(256, 3)

# DejaVu Sans ships under different paths per platform/package manager. Check
# them in order and use whichever exists; `brew install --cask font-dejavu`
# on macOS and the dejavu-fonts-ttf / fonts-dejavu-core package on Linux both
# land in one of these.
_FONT_DIRS = [
    os.path.expanduser("~/Library/Fonts"),               # macOS, Homebrew cask
    "/Library/Fonts",                                     # macOS, system-wide
    "/usr/share/fonts/truetype/dejavu",                   # Debian/Ubuntu
    "/usr/share/fonts/dejavu-sans-fonts",                 # Fedora/RHEL
    "/usr/share/fonts/dejavu",                             # Arch
]
FONT_DIR = next((d for d in _FONT_DIRS
                  if os.path.exists(os.path.join(d, "DejaVuSans.ttf"))), None)
if FONT_DIR is None:
    raise SystemExit(
        "make_roster.py needs DejaVu Sans and couldn't find it in any of:\n  "
        + "\n  ".join(_FONT_DIRS)
        + "\n\nInstall it and re-run:\n"
          "  macOS:  brew install --cask font-dejavu\n"
          "  Debian/Ubuntu: sudo apt install fonts-dejavu-core\n"
          "  Fedora: sudo dnf install dejavu-sans-fonts")
FONT_DIR = FONT_DIR + os.sep

f_name = ImageFont.truetype(FONT_DIR + "DejaVuSans-Bold.ttf", 19)
f_spec = ImageFont.truetype(FONT_DIR + "DejaVuSans.ttf", 14)
f_head = ImageFont.truetype(FONT_DIR + "DejaVuSans-Bold.ttf", 26)
f_tag = ImageFont.truetype(FONT_DIR + "DejaVuSans-Bold.ttf", 13)

BG = (26, 30, 36)
ROW_A = (32, 37, 44)
LABEL = (236, 240, 244)
SPEC = (150, 160, 172)
ORANGE = (240, 124, 26)
RED = (214, 60, 62)
BLUE = (72, 138, 236)
GREEN = (86, 186, 118)

ROW_H = 122
SPR_X = 26
TXT_X = SPR_X + CW * SCALE + 24
W = 860
HEAD = 78


GRP_H = 46


def render(mode, path, subtitle):
    n_rows = sum(len(keys) for _, keys in GROUPS)
    H = HEAD + ROW_H * n_rows + GRP_H * len(GROUPS) + 18
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    title = "NJ TRANSIT + PATH Vehicle Set"
    d.text((26, 20), title, font=f_head, fill=LABEL)
    tw = d.textlength(title, font=f_head)
    d.text((26 + tw + 14, 30), subtitle, font=f_spec, fill=ORANGE)
    d.line([(0, HEAD - 8), (W, HEAD - 8)], fill=(58, 64, 74), width=2)

    y_cursor = HEAD
    i = 0
    for title, keys in GROUPS:
        d.text((26, y_cursor + 14), title.upper(), font=f_tag, fill=(120, 132, 146))
        d.line([(26, y_cursor + 36), (W - 26, y_cursor + 36)], fill=(58, 64, 74))
        y_cursor += GRP_H
        for k in keys:
            v = BY_ID[k]
            render_row(img, d, v, mode, y_cursor, i)
            y_cursor += ROW_H
            i += 1
    img.save(path)
    print(path, img.size)


def render_row(img, d, v, mode, y, i):
        if i % 2 == 0:
            d.rectangle([0, y, W, y + ROW_H - 2], fill=ROW_A)
        sheet = np.array(Image.open("sprites/%s.png" % v["sprite"]))
        cell = sheet[:, 5 * CW:6 * CW]        # direction 5, three-quarter view
        ys, xs = np.nonzero(cell)
        cell = cell[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        ch, cw = cell.shape
        spr = Image.fromarray(PAL[cell].astype(np.uint8)).resize(
            (cw * SCALE, ch * SCALE), Image.NEAREST)
        mask = Image.fromarray(((cell != 0) * 255).astype(np.uint8)).resize(
            (cw * SCALE, ch * SCALE), Image.NEAREST)
        img.paste(spr, (SPR_X, y + (ROW_H - ch * SCALE) // 2), mask)

        d.text((TXT_X, y + ROW_H // 2 - 32), v["name"], font=f_name, fill=LABEL)
        nw = d.textlength(v["name"], font=f_name)
        if v["nml"].startswith("path_"):
            d.text((TXT_X + nw + 12, y + ROW_H // 2 - 29), "PATH", font=f_tag, fill=RED)
        elif v["nml"].startswith("hblr_"):
            d.text((TXT_X + nw + 12, y + ROW_H // 2 - 29), "LIGHT RAIL", font=f_tag,
                   fill=BLUE)
        elif v["feature"] == "road":
            d.text((TXT_X + nw + 12, y + ROW_H // 2 - 29), "BUS", font=f_tag,
                   fill=GREEN)
        d.text((TXT_X, y + ROW_H // 2 - 6), v["role"], font=f_spec, fill=SPEC)
        d.text((TXT_X, y + ROW_H // 2 + 16), "  ·  ".join(figures(v, mode)),
               font=f_spec, fill=(190, 198, 208))


if __name__ == "__main__":
    render("real", "roster.png", "realistic statistics")
    render("bal", "roster_balanced.png", "game-balanced statistics")
