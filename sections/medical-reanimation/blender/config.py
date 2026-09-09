"""OCRU section metric contract. Z up, +Y inward, entry threshold at origin."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BLENDER = ROOT / "blender"
PRODUCTION = ROOT / "production"
BLEND = BLENDER / "ocru.blend"
ART = ROOT / "art"
ASSETS = ROOT / "assets"
LABELS = ASSETS / "textures" / "labels"

# Interior lining of the main hall. Wall thickness is additional outside these faces.
X0, X1 = -4.00, 4.00
Y0, Y1 = 0.00, 9.00
Z0, Z1 = 0.00, 3.60
HALL = (X1 - X0, Y1 - Y0, Z1 - Z0)  # 8.00 x 9.00 x 3.60
WALL_T = 0.18
LINING = 0.0425  # inner lining offset used by flush equipment
EYE = 1.65
ADULT_H = 1.75
CART = (2.10, 0.74, 0.92)  # L x W x H, wheels included
BERTH = (0.88, 2.20, 1.02)  # W x L x surface height
DOOR_W, DOOR_H = 2.20, 2.50
DECON_CLEAR_W, DECON_CLEAR_H = 1.20, 2.15

# Decon alcove extends +Y beyond the main hall rear lining.
DECON = {
    "x0": 1.48,
    "x1": 3.18,
    "y0": 9.00,
    "y1": 11.12,
    "z1": 2.55,
}

# Equipment axis-aligned footprints (minx, miny, maxx, maxy), interior lining space.
EQUIP = {
    "OCRU": (-3.9575, 2.48, -1.46, 6.78),
    "Console": (-1.34, 8.10, 0.52, 9.00),
    "Cartridges": (0.64, 8.30, 1.36, 9.00),
    "ReservePower": (-2.58, 8.44, -1.72, 9.00),
    "Decon": (1.48, 9.00, 3.18, 11.12),
    "PowerPanel": (3.18, 8.86, 3.72, 9.00),
    "SuppliesCabinet": (3.22, 6.52, 3.9575, 8.42),
    "Recovery": (2.58, 3.52, 3.88, 5.88),
    "SupplyBench": (3.08, 0.42, 3.9575, 2.52),
    "Wash": (3.42, 2.62, 3.9575, 3.28),
    "CartParking": (-3.82, 0.18, -2.42, 2.48),
}

# Reserved circulation (plan). Widths are implementation decisions for ragdoll/cart survival.
ROUTES = {
    "arrival": {"x0": -1.10, "x1": 1.10, "y0": 0.00, "y1": 3.20, "width": 2.20},
    "apron": {"x0": -1.40, "x1": 2.40, "y0": 3.20, "y1": 8.00, "width": 3.80},
    "east_bypass": {"x0": 1.55, "x1": 2.55, "y0": 2.60, "y1": 8.20, "width": 1.00},
    "west_face": {"x0": -1.46, "x1": -0.40, "y0": 2.50, "y1": 7.20, "width": 1.06},
    "rear_service": {"x0": -1.60, "x1": 3.10, "y0": 7.85, "y1": 8.95, "width": 1.10},
}

CAMERAS = {
    "CAM_ENTRY": {"loc": (0.00, 0.48, EYE), "look": (0.10, 5.40, 1.40), "lens": 22, "role": "entry"},
    "CAM_HERO": {"loc": (1.35, 4.55, 1.52), "look": (-2.05, 4.70, 1.25), "lens": 24, "role": "hero"},
    "CAM_REVERSE": {"loc": (0.20, 7.70, EYE), "look": (0.05, 1.20, 1.35), "lens": 22, "role": "reverse"},
    "CAM_ROUTE": {"loc": (0.10, 1.55, EYE), "look": (0.20, 6.50, 1.20), "lens": 24, "role": "route"},
    "CAM_CONSOLE": {"loc": (0.15, 6.85, 1.38), "look": (-0.40, 8.45, 1.25), "lens": 28, "role": "machinery"},
    "CAM_DECON": {"loc": (1.55, 7.55, 1.52), "look": (2.33, 10.20, 1.15), "lens": 28, "role": "secondary"},
    "CAM_RECOVERY": {"loc": (1.35, 3.25, 1.22), "look": (3.20, 4.70, 0.80), "lens": 28, "role": "cramped"},
    "CAM_PINCH": {"loc": (-0.15, 3.85, 1.35), "look": (-2.15, 4.75, 1.10), "lens": 28, "role": "cramped"},
    "CAM_MATERIALS": {"loc": (-0.85, 7.35, 1.15), "look": (-2.15, 8.55, 0.85), "lens": 35, "role": "materials"},
    "CAM_MAINT": {"loc": (2.05, 7.35, 1.48), "look": (3.05, 8.70, 1.35), "lens": 28, "role": "machinery"},
}

COLLECTIONS = [
    "ARCHITECTURE",
    "OCRU",
    "STATIONS",
    "UTILITIES",
    "PROPS",
    "LIGHTING",
    "GRAPHICS",
    "CAMERAS",
    "VALIDATION",
]

SEED = 20260909
REVISION = "R09"
