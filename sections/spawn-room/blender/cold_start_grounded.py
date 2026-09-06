"""Run against the saved blend in a new Blender process; no reconstruction."""
import bpy, sys, json, argparse, hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import validate_contacts, validate_grounded

p=argparse.ArgumentParser();p.add_argument('--review-id',default='cold-start');p.add_argument('--no-render',action='store_true');p.add_argument('--states',action='store_true');p.add_argument('--cameras',default='')
args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
out=HERE.parent/'production/renders/review'/args.review_id;out.mkdir(parents=True,exist_ok=True)
contact=validate_contacts.main();(out/'contact_validation.json').write_bytes((HERE.parent/'production/contact_validation.json').read_bytes())
objective=validate_grounded.main(out/'objective_validation.json')
texture_manifest=json.loads((HERE.parent/'assets/textures/manifest.json').read_text(encoding='utf-8-sig'))
records=texture_manifest if isinstance(texture_manifest,list) else texture_manifest['files']
texture_checks=[]
for record in records:
    name=Path(record['file']).name;image=bpy.data.images.get(name)
    digest=hashlib.sha256(bytes(image.packed_file.data)).hexdigest() if image and image.packed_file else None
    texture_checks.append({'image':name,'packed_sha256':digest,'pass':digest==record['sha256'].lower()})
viewports=[space.shading.type for screen in bpy.data.screens for area in screen.areas for space in area.spaces if space.type=='VIEW_3D']
dependencies={'source_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'textures':texture_checks,'startup_viewports':viewports,'pass':all(t['pass'] for t in texture_checks) and len(texture_checks)==6 and all(v=='SOLID' for v in viewports)}
(out/'dependency_validation.json').write_text(json.dumps(dependencies,indent=2))
names=sorted(o.name for o in bpy.data.objects if o.type=='CAMERA' and o.name.startswith('VALIDATE_'))
manifest={n:{'position':list(bpy.data.objects[n].location),'rotation':list(bpy.data.objects[n].rotation_euler),'lens':bpy.data.objects[n].data.lens} for n in names}
(out/'cameras.json').write_text(json.dumps(manifest,indent=2))
if not args.no_render:
    for name in (args.cameras.split(',') if args.cameras else names):
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
if contact or objective or not dependencies['pass']:raise RuntimeError('Cold-start validation failed; inspect reports')
print('COLD_START_PASS',str(out))
