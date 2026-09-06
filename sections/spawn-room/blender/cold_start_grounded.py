"""Run against the saved blend in a new Blender process; no reconstruction."""
import bpy, sys, json, argparse
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import validate_contacts, validate_grounded

p=argparse.ArgumentParser();p.add_argument('--review-id',default='cold-start');p.add_argument('--no-render',action='store_true');p.add_argument('--states',action='store_true')
args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
out=HERE.parent/'production/renders/review'/args.review_id;out.mkdir(parents=True,exist_ok=True)
contact=validate_contacts.main();(out/'contact_validation.json').write_bytes((HERE.parent/'production/contact_validation.json').read_bytes())
objective=validate_grounded.main(out/'objective_validation.json')
names=sorted(o.name for o in bpy.data.objects if o.type=='CAMERA' and o.name.startswith('VALIDATE_'))
manifest={n:{'position':list(bpy.data.objects[n].location),'rotation':list(bpy.data.objects[n].rotation_euler),'lens':bpy.data.objects[n].data.lens} for n in names}
(out/'cameras.json').write_text(json.dumps(manifest,indent=2))
if not args.no_render:
    for name in names:
        bpy.context.scene.camera=bpy.data.objects[name];bpy.context.scene.render.filepath=str(out/(name+'.png'))
        bpy.ops.render.render(write_still=True)
    if args.states:
        for name in ['DETAIL_BriefingHuman','DETAIL_LockerWork']:
            bpy.context.scene.camera=bpy.data.objects[name];bpy.context.scene.render.filepath=str(out/(name+'.png'))
            bpy.ops.render.render(write_still=True)
        for fr in [31,61,91,121,151]:
            bpy.context.scene.frame_set(fr);bpy.context.scene.camera=bpy.data.objects['VALIDATE_Hero_A']
            bpy.context.scene.render.filepath=str(out/('STATE_%03d.png'%fr));bpy.ops.render.render(write_still=True)
        bpy.context.scene.frame_set(1)
if contact or objective:raise RuntimeError('Cold-start validation failed; inspect reports')
print('COLD_START_PASS',str(out))
