"""Fresh-process native Blender rebuild and explicit numeric authoring gates.

Usage: python rebuild.py --blender /path/to/blender [--render-review]
Requires Blender 5.2+ and Pillow in the calling Python environment.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path
from review_images import FIXED, HERO

HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/'front_end_area.blend'
OUTPUT=HERE.parent/'front_end_area_cafeteria_revamp.blend'

def run(command, log):
    print('Running', log.name, flush=True)
    with log.open('w') as f:
        subprocess.run([str(v) for v in command],stdout=f,stderr=subprocess.STDOUT,check=True,cwd=HERE)

def check_report(path):
    report=json.loads(path.read_text());detail=report['cafeteria_revamp']
    gates={
        'module_triangles':report['triangles']['within_budget'],
        'furniture_lanes':report['lane_pass'],
        'support_anchors':detail['support_anchor_pass'],
        'complete_support_registration':not detail['support_coverage']['missing'],
        'reimport_bounds':detail['reimport_bounds_pass'],
        'five_reimported_instances':len(detail['reimport_instances'])==5,
        'seven_interfaces_unchanged':detail['interfaces_unchanged'] and len(report['interfaces'])==7,
        'packed_images':detail['all_file_images_packed'] and not detail['missing_image_dependencies'],
        'packed_fonts':detail['external_fonts_packed'] and not detail['missing_font_dependencies'],
        'no_linked_dependencies':not detail['linked_libraries'],
        'unrelated_geometry':all(x['unchanged'] for x in detail['unrelated_geometry'].values()),
        'interior_floor_contacts':not report['support_contact']['interior']['gap_fail'] and not report['support_contact']['interior']['pen_fail'],
        'yard_floor_contacts':not report['support_contact']['yard']['gap_fail'] and not report['support_contact']['yard']['pen_fail'],
    }
    print(json.dumps(gates,indent=2),flush=True)
    if not all(gates.values()):raise RuntimeError('Authoring validation failed: '+', '.join(k for k,v in gates.items() if not v))
    return gates

if __name__ == '__main__':
    p=argparse.ArgumentParser();p.add_argument('--blender',required=True,type=Path);p.add_argument('--render-review',action='store_true');p.add_argument('--skip-asset-renders',action='store_true');a=p.parse_args()
    with SOURCE.open('rb') as f:header=f.read(128)
    if header.startswith(b'version https://git-lfs.github.com/spec/v1'):
        raise RuntimeError('Hydrate front_end_area.blend with Git LFS first')
    logs=HERE/'logs';logs.mkdir(exist_ok=True)
    cli=[a.blender,'--background','--disable-autoexec','--python-exit-code','1']
    run([sys.executable,HERE/'paint_graphics.py'],logs/'rebuild_graphics.log')
    for kind in ('foosball','dartboard','basketball'):
        tail=[kind]+(['--no-render'] if a.skip_asset_renders else [])
        run(cli+['--factory-startup','--python',HERE/'build_assets.py','--']+tail,logs/('rebuild_'+kind+'.log'))
    run(cli+[SOURCE,'--python',HERE/'revamp_room.py','--',OUTPUT],logs/'rebuild_room.log')
    report=HERE/'validation_final.json'
    run(cli+[OUTPUT,'--python',HERE.parent/'validate_front_end.py','--',report,'--original',SOURCE],logs/'rebuild_validation.log')
    check_report(report)
    if a.render_review:
        folder=HERE/'renders'/'rebuild_review'
        run(cli+[OUTPUT,'--python',HERE.parent/'render_views.py','--',folder,','.join(FIXED+HERO),8,960,540,-.5],logs/'rebuild_review.log')
        run([sys.executable,HERE/'review_images.py',folder],logs/'rebuild_contact_sheet.log')
    print('Editable candidate:',OUTPUT,flush=True)
