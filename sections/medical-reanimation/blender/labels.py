"""Industrial labels, screens and floor graphics. Original copy only."""
from __future__ import annotations

import os
from pathlib import Path

import bpy
from mathutils import Vector

import config
import mesh as g
from materials import M, image_mat

FONT_PATHS = [
    r"C:\Windows\Fonts\consola.ttf",
    r"C:\Windows\Fonts\consolab.ttf",
    r"C:\Windows\Fonts\courbd.ttf",
    r"C:\Windows\Fonts\arialbd.ttf",
    r"C:\Windows\Fonts\arial.ttf",
]

_FONT = None

# 5x7 caps for screen raster
_F = {
    "A": "011101001111111000110001",
    "B": "11110100111110100111110",
    "C": "0111010000100001000001110",
    "D": "1110010010100101001011100",
    "E": "1111110000111001000011111",
    "F": "1111110000111001000010000",
    "G": "0111010000101111000101110",
    "H": "1000110001111111000110001",
    "I": "11111001000010000100011111",
    "J": "0011100010000101001011100",
    "K": "1001010100110001010010001",
    "L": "1000010000100001000011111",
    "M": "1000111011101011000110001",
    "N": "1000111001101011001110001",
    "O": "0111010001100011000101110",
    "P": "1111010001111101000010000",
    "Q": "0111010001100011001001101",
    "R": "1111010001111101010010001",
    "S": "0111110000011100000111110",
    "T": "1111100100001000010000100",
    "U": "1000110001100011000101110",
    "V": "1000110001010100101000100",
    "W": "1000110001101011101110001",
    "X": "1000101010001000101010001",
    "Y": "1000101010001000010000100",
    "Z": "1111100010001000100011111",
    "0": "0111010001101011000101110",
    "1": "0010001100001000010001110",
    "2": "0111010001000100010001111",
    "3": "0111010001001100000101110",
    "4": "1001010010111110000100001",
    "5": "1111110000111100000111110",
    "6": "0111010000111101000101110",
    "7": "1111100001000100010001000",
    "8": "0111010001011101000101110",
    "9": "0111010001011110000101110",
    " ": "0000000000000000000000000",
    "-": "0000000000011100000000000",
    ".": "0000000000000000000000100",
    ":": "0000000100000000010000000",
    "/": "0000100010001000100010000",
    "+": "0000000100011100010000000",
    "*": "0010001110001000000000000",
}


def font():
    global _FONT
    if _FONT:
        return _FONT
    for p in FONT_PATHS:
        if os.path.isfile(p):
            _FONT = bpy.data.fonts.load(p, check_existing=True)
            return _FONT
    _FONT = bpy.data.fonts.get("Bfont") or bpy.data.fonts[0]
    return _FONT


def text3d(name, body, pos, size=0.06, extrude=0.003, mat="ink", align="CENTER", rot=None, width=1.0, normal=(0.0, -1.0, 0.0), flip_x=False, flip_y=False):
    from mathutils import Vector
    cu = bpy.data.curves.new(name, "FONT")
    cu.body = body
    cu.font = font()
    cu.size = size
    cu.extrude = extrude
    cu.offset = 0.0
    cu.bevel_depth = max(0.0004, extrude * 0.12)
    cu.align_x = align
    cu.align_y = "CENTER"
    ob = bpy.data.objects.new(name, cu)
    ob.location = pos
    if rot is not None:
        ob.rotation_euler = rot
    elif normal is not None:
        ob.rotation_euler = Vector(normal).to_track_quat("Z", "Y").to_euler()
    g.finish(ob, name, mat, edge=0.0)
    sx = (-1.0 if flip_x else 1.0) * width
    ob.scale.x = sx
    if flip_y:
        ob.scale.y = -1.0
    return ob


def plate(name, pos, size, mat="shell", edge=0.003):
    return g.box(name, pos, size, mat, edge)


def decal_text(name, body, pos, size, mat="ink", rot=(1.5708, 0.0, 0.0)):
    return text3d(name, body, pos, size=size, extrude=0.0016, mat=mat, rot=rot)


def _glyph(ch):
    bits = _F.get(ch.upper(), _F[" "])
    bits = (bits + "0" * 25)[:25]
    return bits


def raster_text(pixels, w, h, text, ox, oy, color, scale=2, gap=1):
    r, g_, b, a = color
    x = ox
    for ch in text:
        bits = _glyph(ch)
        for row in range(5):
            for col in range(5):
                if bits[row * 5 + col] == "1":
                    for dy in range(scale):
                        for dx in range(scale):
                            px = x + col * scale + dx
                            py = oy + (4 - row) * scale + dy
                            if 0 <= px < w and 0 <= py < h:
                                i = (py * w + px) * 4
                                pixels[i:i + 4] = (r, g_, b, a)
        x += (5 * scale) + gap
    return x


def make_image(name, w, h, fill, draw_fn):
    img = bpy.data.images.new(name, w, h, alpha=True)
    pix = [fill[0], fill[1], fill[2], fill[3]] * (w * h)
    draw_fn(pix, w, h)
    img.pixels = pix
    img.pack()
    dest = config.LABELS / f"{name}.png"
    dest.parent.mkdir(parents=True, exist_ok=True)
    img.filepath_raw = str(dest)
    img.file_format = "PNG"
    img.save()
    return img


def _rect(pixels, w, h, x0, y0, x1, y1, color):
    r, g_, b, a = color
    for y in range(max(0, y0), min(h, y1)):
        for x in range(max(0, x0), min(w, x1)):
            i = (y * w + x) * 4
            pixels[i:i + 4] = (r, g_, b, a)


def screen_status():
    bg = (0.02, 0.07, 0.09, 1)

    def draw(p, w, h):
        _rect(p, w, h, 0, 0, w, h, bg)
        _rect(p, w, h, 16, h - 70, w - 16, h - 18, (0.04, 0.14, 0.18, 1))
        raster_text(p, w, h, "STANDBY", 28, h - 58, (0.35, 0.95, 1.0, 1), scale=4, gap=2)
        raster_text(p, w, h, "READY FOR RECOMMISSION", 28, h - 100, (0.55, 0.9, 0.95, 1), scale=2, gap=1)
        lines = [
            "VITALS NOMINAL",
            "FLUIDS CHECKED",
            "OXYGEN ONLINE",
            "THERMAL REGULATION",
            "SYSTEMS GREEN",
        ]
        y = h - 150
        for line in lines:
            _rect(p, w, h, 28, y, 44, y + 16, (0.15, 0.85, 0.45, 1))
            raster_text(p, w, h, line, 56, y, (0.7, 0.95, 0.9, 1), scale=2, gap=1)
            y -= 36
        raster_text(p, w, h, "AWAITING SUBJECT", 28, 36, (0.9, 0.55, 0.2, 1), scale=2, gap=1)

    img = make_image("screen_status", 512, 384, bg, draw)
    return image_mat("screen_status", img, rough=0.18, emit=4.5)


def screen_body():
    bg = (0.02, 0.06, 0.08, 1)

    def draw(p, w, h):
        _rect(p, w, h, 0, 0, w, h, bg)
        raster_text(p, w, h, "UNIT MAP", 24, h - 40, (0.4, 0.9, 1.0, 1), scale=3, gap=2)
        # schematic body
        cx, cy = w // 2, h // 2 - 10
        _rect(p, w, h, cx - 18, cy + 70, cx + 18, cy + 110, (0.2, 0.7, 0.8, 1))
        _rect(p, w, h, cx - 40, cy - 20, cx + 40, cy + 70, (0.15, 0.55, 0.7, 1))
        _rect(p, w, h, cx - 70, cy + 20, cx - 40, cy + 60, (0.15, 0.55, 0.7, 1))
        _rect(p, w, h, cx + 40, cy + 20, cx + 70, cy + 60, (0.15, 0.55, 0.7, 1))
        _rect(p, w, h, cx - 28, cy - 90, cx - 8, cy - 20, (0.15, 0.55, 0.7, 1))
        _rect(p, w, h, cx + 8, cy - 90, cx + 28, cy - 20, (0.15, 0.55, 0.7, 1))
        raster_text(p, w, h, "NO SUBJECT", 24, 28, (0.95, 0.7, 0.25, 1), scale=2, gap=1)

    img = make_image("screen_body", 384, 384, bg, draw)
    return image_mat("screen_body", img, rough=0.18, emit=3.8)


def screen_small():
    bg = (0.03, 0.05, 0.06, 1)

    def draw(p, w, h):
        _rect(p, w, h, 0, 0, w, h, bg)
        raster_text(p, w, h, "OCRU T-01", 12, h - 28, (0.4, 0.9, 1.0, 1), scale=2, gap=1)
        raster_text(p, w, h, "CYCLE IDLE", 12, 16, (0.2, 0.85, 0.4, 1), scale=2, gap=1)

    img = make_image("screen_small", 256, 128, bg, draw)
    return image_mat("screen_small", img, rough=0.2, emit=3.0)


def floor_stencil():
    bg = (0.16, 0.17, 0.175, 1)
    fg = (0.82, 0.82, 0.78, 1)

    def draw(p, w, h):
        _rect(p, w, h, 0, 0, w, h, bg)
        raster_text(p, w, h, "CLEAN SAFE ACCESS ONLY", 24, h // 2 - 10, fg, scale=3, gap=2)

    img = make_image("floor_stencil", 768, 128, bg, draw)
    return image_mat("floor_stencil", img, rough=0.7, emit=0.0)


def build():
    config.LABELS.mkdir(parents=True, exist_ok=True)
    screen_status()
    screen_body()
    screen_small()
    floor_stencil()
    font()
