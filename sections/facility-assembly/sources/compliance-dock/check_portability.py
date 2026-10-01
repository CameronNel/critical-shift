"""Read-only cold native open and dependency inventory in an actual checkout."""
import argparse, hashlib, json, sys
from pathlib import Path
import bpy

p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--expected',required=True);p.add_argument('--out',required=True)
p.add_argument('--expected-libraries',type=int,default=25)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);source=Path(a.source).resolve()
sha=lambda x:hashlib.sha256(Path(x).read_bytes()).hexdigest()
if sha(source)!=a.expected:raise RuntimeError('Source differs from published expected hash')
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
scene=bpy.data.scenes['COMPLIANCE_EDIT_LOCAL'];bpy.context.window.scene=scene
libraries=[]
for lib in bpy.data.libraries:
    resolved=Path(bpy.path.abspath(lib.filepath,library=lib.parent))
    # Blender can normalize inherited links relative to the top-level file.
    if not resolved.is_file():resolved=Path(bpy.path.abspath(lib.filepath))
    header=resolved.read_bytes()[:8] if resolved.is_file() else b''
    native_payload=header.startswith((b'BLENDER',b'\x28\xb5\x2f\xfd',b'\x1f\x8b'))
    libraries.append(dict(path=lib.filepath,relative=lib.filepath.startswith('//'),exists=resolved.is_file(),native_payload=native_payload,sha256=sha(resolved) if resolved.is_file() else None))
images=[]
for img in bpy.data.images:
    if img.source!='FILE':continue
    packed=bool(img.packed_file or img.packed_files)
    resolved=Path(bpy.path.abspath(img.filepath,library=img.library))
    images.append(dict(name=img.name,path=img.filepath,packed=packed,exists=resolved.is_file(),local=img.library is None))
report=dict(source_sha256=a.expected,cold_open=True,source_unchanged=sha(source)==a.expected,scene=scene.name,objects=len(scene.objects),local_scene=scene.library is None,local_objects=all(o.library is None for o in scene.objects),libraries=libraries,file_images=images,recipe_sha256=json.loads(scene.get('recipe_sha256','{}')),runtime_verified=False)
report['expected_library_count']=a.expected_libraries
report['pass']=report['source_unchanged'] and report['local_scene'] and report['local_objects'] and len(libraries)==a.expected_libraries and all(x['exists'] and x['native_payload'] for x in libraries) and all(x['packed'] or x['exists'] for x in images)
Path(a.out).write_text(json.dumps(report,indent=2)+'\n')
print('PORTABILITY',report['pass'],'objects',report['objects'],'libraries',len(libraries),'images',len(images),flush=True)
if not report['pass']:raise RuntimeError('Cold dependency/editability check failed')
