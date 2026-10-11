"""Remove texel-scale noise from baked tangent-space normal maps.

System Python with numpy and Pillow:  python3 bake_filter_normals.py IN_DIR OUT_DIR [--prefix spawn_a] [--sigma 2.0]
Fine procedural bump (features near or below one texel) bakes as random per-texel normals, which
reads as grit under engine specular lighting. This low-pass filters each normal map (Gaussian,
island-normalised so island edges do not fade), keeping broad relief. Albedo and packed maps are
copied unchanged. Coverage is taken from the albedo map. Prints RMS tilt and the share of
normal-map energy at texel scale before and after. Fine surface grain belongs in an engine detail normal.
"""
import argparse
import shutil
from pathlib import Path

import numpy as np
from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument('src', type=Path)
ap.add_argument('dst', type=Path)
ap.add_argument('--prefix', default='spawn_a')
ap.add_argument('--sigma', type=float, default=2.0)
ap.add_argument('--atlases', type=int, default=8)
args = ap.parse_args()
args.dst.mkdir(parents=True, exist_ok=True)
R = int(3 * args.sigma)
ker = np.exp(-0.5 * (np.arange(-R, R + 1) / args.sigma) ** 2).astype(np.float32)
ker /= ker.sum()


def blur(a):
    for axis in (0, 1):
        p = np.pad(a, [(R, R) if i == axis else (0, 0) for i in range(a.ndim)], mode='edge')
        out = np.zeros_like(a)
        for i, w in enumerate(ker):
            sl = [slice(None)] * a.ndim
            sl[axis] = slice(i, i + a.shape[axis])
            out += w * p[tuple(sl)]
        a = out
    return a


for k in range(args.atlases):
    for ch in ('albedo', 'rm'):
        shutil.copy(args.src / f'{args.prefix}{k}_{ch}.png', args.dst / f'{args.prefix}{k}_{ch}.png')
    n = np.asarray(Image.open(args.src / f'{args.prefix}{k}_normal.png').convert('RGB')).astype(np.float32)
    alb = np.asarray(Image.open(args.src / f'{args.prefix}{k}_albedo.png').convert('RGB')).astype(np.float32)
    cov = (alb.sum(axis=2) > 6).astype(np.float32)
    xy = (n[..., :2] - 127.5) / 127.5
    hf0 = xy - blur(xy)
    num, den = blur(xy * cov[..., None]), blur(cov)[..., None]
    f = np.where(den > 1e-3, num / np.maximum(den, 1e-3), 0) * cov[..., None]
    z = np.sqrt(np.clip(1 - (f ** 2).sum(axis=-1), 0, 1))
    out = np.zeros(n.shape, np.float32)
    out[..., :2] = f * 127.5 + 127.5
    out[..., 2] = z * 127.5 + 127.5
    out[cov == 0] = (127.5, 127.5, 255)
    m = cov > 0
    b, a = np.sqrt((xy[m] ** 2).mean()), np.sqrt((f[m] ** 2).mean())
    share = (hf0[m] ** 2).mean() / max((xy[m] ** 2).mean(), 1e-12)
    print(f'atlas {k}: RMS tilt {np.degrees(np.arcsin(min(b, 1))):.2f} -> {np.degrees(np.arcsin(min(a, 1))):.2f} deg; texel-scale share of energy before {100 * share:.0f}%')
    Image.fromarray(np.clip(out, 0, 255).astype('uint8'), 'RGB').save(args.dst / f'{args.prefix}{k}_normal.png')
