"""Build the night sky's textures (runtime/unity/Assets/CriticalShift/Content/Sky/Textures/) from NASA's public sources.

    blender -b --factory-startup --python runtime/tools/build_sky_textures.py -- <download folder>

Blender is used only to read OpenEXR and TIFF; nothing is rendered. Download these into <download folder> first (NASA Scientific
Visualization Studio; credits in Content/Sky/README.md):
  https://svs.gsfc.nasa.gov/vis/a000000/a004800/a004851/hiptyc_2020_8k.exr        bright stars (Hipparcos, Tycho), celestial, 8192x4096
  https://svs.gsfc.nasa.gov/vis/a000000/a004800/a004851/milkyway_2020_4k.exr      Milky Way without those stars, celestial, 4096x2048
  https://svs.gsfc.nasa.gov/vis/a000000/a004700/a004720/lroc_color_poles_2k.tif   Moon colour (LROC WAC), 2048x1024
  https://svs.gsfc.nasa.gov/vis/a000000/a004700/a004720/ldem_4.tif                Moon heights (LOLA), km, 1440x720

Writes (8-bit PNG, written here with zlib so no colour management touches the values):
  NightSky_Stars.png      sRGB-encoded linear star radiance (the map's own 0..1 scale), 8192x4096, equirectangular, pole at the top
  NightSky_MilkyWay.png   sRGB-encoded, 4096x2048, same projection
  NightSky_MoonColor.png  the LROC colour unchanged, 2048x1024, longitude 0 at the centre, east to the right
  NightSky_MoonNormal.png tangent-space normals (x east, y north, z up; linear, 0.5 = flat) from the heights, 1440x720
"""
import bpy, numpy as np, sys, os, zlib, struct

SRC = os.path.abspath(sys.argv[sys.argv.index('--') + 1])
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'unity', 'Assets', 'CriticalShift', 'Content', 'Sky', 'Textures')
MOON_RADIUS_KM = 1737.4
RELIEF = 3.0          # height exaggeration for the normals: the true slopes barely show on a disc a few dozen pixels wide

def load(name, colorspace):
    im = bpy.data.images.load(os.path.join(SRC, name)); im.colorspace_settings.name = colorspace
    w, h = im.size; a = np.empty(w * h * 4, np.float32); im.pixels.foreach_get(a); bpy.data.images.remove(im)
    return a.reshape(h, w, 4)[::-1]               # Blender's rows run bottom to top; PNG rows run top to bottom

def srgb(x):
    x = np.clip(x, 0.0, 1.0)
    return np.where(x <= 0.0031308, 12.92 * x, 1.055 * np.power(x, 1 / 2.4) - 0.055)

def write_png(name, rgb):
    """rgb: float array (h, w, 3) in 0..1, already encoded. Writes an 8-bit RGB PNG."""
    data = np.round(np.clip(rgb, 0, 1) * 255).astype(np.uint8)
    h, w, _ = data.shape
    raw = np.concatenate([np.zeros((h, 1), np.uint8), data.reshape(h, w * 3)], axis=1).tobytes()   # filter byte 0 per row
    def chunk(tag, body): return struct.pack('>I', len(body)) + tag + body + struct.pack('>I', zlib.crc32(tag + body) & 0xffffffff)
    png = b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(raw, 9)) + chunk(b'IEND', b'')
    path = os.path.join(OUT, name); open(path, 'wb').write(png)
    print('wrote %s %dx%d %.1f MB' % (name, w, h, len(png) / 1e6), flush=True)

os.makedirs(OUT, exist_ok=True)
write_png('NightSky_Stars.png', srgb(load('hiptyc_2020_8k.exr', 'Linear Rec.709')[..., :3]))
write_png('NightSky_MilkyWay.png', srgb(load('milkyway_2020_4k.exr', 'Linear Rec.709')[..., :3]))
write_png('NightSky_MoonColor.png', load('lroc_color_poles_2k.tif', 'Non-Color')[..., :3])      # 8-bit sRGB in, bytes out unchanged

h = load('ldem_4.tif', 'Non-Color')[..., 0].astype(np.float64)                                    # km above the reference sphere
rows, cols = h.shape
lat = (0.5 - (np.arange(rows) + 0.5) / rows) * np.pi                                               # +90 deg at the top row
step = np.pi / rows                                                                                # radians per pixel, both axes
dx = (np.roll(h, -1, 1) - np.roll(h, 1, 1)) / (2 * step * MOON_RADIUS_KM * np.maximum(np.cos(lat), 0.05)[:, None])   # east slope
dn = np.empty_like(h); dn[1:-1] = (h[:-2] - h[2:]) / (2 * step * MOON_RADIUS_KM); dn[0] = dn[1]; dn[-1] = dn[-2]     # north slope
n = np.stack([-dx * RELIEF, -dn * RELIEF, np.ones_like(h)], -1); n /= np.linalg.norm(n, axis=-1, keepdims=True)
write_png('NightSky_MoonNormal.png', n * 0.5 + 0.5)
print('slopes: 99th percentile %.3f, max %.3f (rise over run, before the x%.0f relief)' % (np.percentile(np.hypot(dx, dn), 99), np.hypot(dx, dn).max(), RELIEF))
