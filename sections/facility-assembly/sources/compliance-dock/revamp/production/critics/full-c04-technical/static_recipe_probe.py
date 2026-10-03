"""Read-only numerical witness from recipe constants; does not import bpy."""
import hashlib, json, math
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
recipe = ROOT / 'full_repairs.py'
# Reproduce the authored outer hanger outline only, then clip the outline to
# the lower-flange vertical strip. The bore lies entirely above this strip.
outline = []
for j in range(16):
    xx = .019 * math.sin(2 * math.pi * j / 16)
    zz = 3.56 + .019 * math.cos(2 * math.pi * j / 16)
    if j in [7, 8, 9]:
        xx = {7: .027, 8: 0, 9: -.027}[j]
        zz = 3.48
    outline.append([xx, zz])

def clip(poly, z, above):
    result = []
    for a, b in zip(poly, poly[1:] + poly[:1]):
        ina = a[1] >= z if above else a[1] <= z
        inb = b[1] >= z if above else b[1] <= z
        if ina:
            result.append(a)
        if ina != inb:
            t = (z - a[1]) / (b[1] - a[1])
            result.append([a[0] + t * (b[0] - a[0]), z])
    return result

section = clip(clip(outline, 3.50, True), 3.52, False)
area = abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(section,section[1:]+section[:1]))) / 2
report = {
    'scope': 'Current authored recipe only. Native not opened. No final score.',
    'recipe_sha256': hashlib.sha256(recipe.read_bytes()).hexdigest(),
    'P2_hanger_lower_flange_intersection': {
        'rail_lower_flange_y_m': [15.8,16.08],
        'rail_lower_flange_z_m': [3.5,3.52],
        'hanger_y_m': [15.8,15.826],
        'hanger_foot_z_m': 3.48,
        'clipped_hanger_cross_section_relative_x_world_z': section,
        'cross_section_area_m2': area,
        'intersection_volume_per_hanger_m3': area*.026,
        'hanger_count': 4,
        'bore_bottom_z_m': 3.56-.0085,
        'interpretation': 'A continuous solid hanger neck crosses the anchored C-rail lower flange. Real roller contact does not remove this intersection.'
    },
    'key_cabinet_recipe': {
        'shell_y_m': [9.37,9.52],
        'interior_back_web_y_m': [9.514,9.52],
        'stated_glass_rear_y_m': 9.475,
        'bow_y_m': [9.4775,9.4805],
        'hook_y_m': [9.476,9.514],
        'interpretation': 'Recipe predicts pane/bow separation and back-web hook engagement. Retained native pane still needs measurement.'
    },
    'validator_limit': 'Registered anchors can be substantiated by any assembly component; an internal physical load path is not proven by ancestry or this validator alone.'
}
(HERE/'static-recipe-findings.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
