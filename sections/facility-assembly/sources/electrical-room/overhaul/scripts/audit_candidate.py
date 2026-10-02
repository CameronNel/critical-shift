"""Cold-load candidate links and compare inherited missing IDs to the base map."""
import bpy, json, hashlib, sys, os, argparse
from pathlib import Path

p=argparse.ArgumentParser()
p.add_argument('--candidate',required=True)
p.add_argument('--module',required=True)
p.add_argument('--out',required=True)
p.add_argument('--baseline-audit',help='Pre-promotion missing-ID receipt; defaults to the recorded R3 base audit')
a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
root=Path(__file__).resolve().parents[6]
base=root/json.loads((root/'MAP.json').read_text())['authoring_scene']
candidate=Path(a.candidate).resolve();module=Path(a.module).resolve()
sha=lambda path:hashlib.sha256(Path(path).read_bytes()).hexdigest()
base_sha=sha(base);module_sha=sha(module)

def missing_ids():
    result=[]
    for kind in ['objects','meshes','materials','curves','collections','lights',
                 'node_groups','images','textures','armatures','worlds','cameras','sounds','fonts']:
        for item in getattr(bpy.data,kind):
            if getattr(item,'is_missing',False):
                result.append([kind,item.name, str(Path(bpy.path.abspath(item.library.filepath)).resolve()) if item.library else None])
    return sorted(result,key=str)

def portable_missing_rows(rows):
    # Older receipts used absolute checkout paths. Compare asset identity rather
    # than the machine-specific checkout prefix; library containment is separate.
    result=[]
    for kind,name,path in rows:
        if path and '/sections/' in path:path='sections/'+path.split('/sections/',1)[1]
        result.append([kind,name,path])
    return sorted(result,key=str)

bpy.ops.wm.open_mainfile(filepath=str(base),load_ui=False)
inherited=missing_ids()
baseline_audit=Path(a.baseline_audit).resolve() if a.baseline_audit else Path(__file__).resolve().parents[1]/'candidate-audit-R3.json'
recorded_base=json.loads(baseline_audit.read_text()) if baseline_audit.exists() else None
recorded_base_pass=recorded_base is None or (recorded_base['base_sha256']==base_sha and portable_missing_rows(recorded_base['inherited_missing_ids'])==portable_missing_rows(inherited))
canonical_module=root/'sections/facility-assembly/sources/electrical-room/module.blend'
legacy_requests={}
for kind in ['objects','meshes','materials','curves','collections','lights','node_groups','images','armatures','worlds','cameras']:
    legacy_requests[kind]=[item.name for item in getattr(bpy.data,kind) if item.library
        and Path(bpy.path.abspath(item.library.filepath)).resolve()==canonical_module
        and not getattr(item,'is_missing',False)]
with bpy.data.libraries.load(str(module),link=False) as (src,dst):
    absent_legacy=[kind+':'+name for kind,names in legacy_requests.items() for name in names if name not in getattr(src,kind,[])]
bpy.ops.wm.open_mainfile(filepath=str(candidate),load_ui=False)
current=missing_ids();failures=[];libraries=[]
if not recorded_base_pass:failures.append('base differs from recorded pre-promotion missing-ID set or map bytes')
if absent_legacy:failures.append('canonical electrical library IDs absent: '+', '.join(absent_legacy))
for lib in bpy.data.libraries:
    resolved=Path(bpy.path.abspath(lib.filepath)).resolve()
    inside=resolved.is_relative_to(root);exists=resolved.is_file()
    libraries.append({'stored':lib.filepath,'relative_to_checkout':str(resolved.relative_to(root)) if inside else str(resolved),
                      'inside_checkout':inside,'exists':exists,'sha256':sha(resolved) if exists else None})
    if not inside or not exists:failures.append('library:'+lib.filepath)
if current!=inherited:failures.append('inherited missing-ID set changed')
missing_data=[o.name for o in bpy.context.scene.objects if o.type in {'MESH','CURVE','FONT'} and o.data is None]
if missing_data:failures.append('object data missing')
inst=bpy.data.objects.get('INSTANCE | electrical-room current source')
linked=inst.instance_collection if inst else None
resolved=Path(bpy.path.abspath(linked.library.filepath)).resolve() if linked and linked.library else None
if resolved!=module:failures.append('electrical instance does not resolve intended module')
if inst and inst.get('candidate_module_sha256')!=module_sha:failures.append('module hash differs from integrated receipt')
if bpy.data.objects.get('VC | Roof-finished MATERIAL_PREVIEW_electrical-room'):failures.append('old electrical interior cache still active')
for image in bpy.data.images:
    if image.source=='FILE' and image.users and not image.packed_file:
        path=Path(bpy.path.abspath(image.filepath,library=image.library)).resolve()
        if not path.is_file() or not path.is_relative_to(root):failures.append('image:'+image.name)
if sha(base)!=base_sha or sha(module)!=module_sha:failures.append('audit changed source bytes')
report={'scope':'Candidate link containment, canonical electrical library ID compatibility, intended electrical instance, retired cache and unchanged inherited missing-ID set. Not a clean whole-map/runtime certification.',
        'base_sha256':base_sha,'candidate_sha256':sha(candidate),'module_sha256':module_sha,
        'electrical_instance_module':str(resolved.relative_to(root)) if resolved and resolved.is_relative_to(root) else str(resolved),
        'libraries':libraries,'inherited_missing_id_count':len(inherited),'candidate_missing_id_count':len(current),
        'inherited_missing_ids_unchanged':current==inherited,'inherited_missing_ids':inherited,
        'pre_promotion_missing_id_receipt':str(baseline_audit.relative_to(root)) if baseline_audit.is_relative_to(root) else str(baseline_audit),
        'pre_promotion_base_missing_ids_unchanged':recorded_base_pass,
        'pre_promotion_receipt_available':recorded_base is not None,
        'canonical_map_electrical_id_requests':legacy_requests,'module_absent_legacy_ids':absent_legacy,
        'module_legacy_id_compatibility_pass':not absent_legacy,
        'missing_object_data':missing_data,'failures':failures,'pass':not failures}
Path(a.out).resolve().write_text(json.dumps(report,indent=2))
print('CANDIDATE_AUDIT',report['pass'],'INHERITED_MISSING_IDS',len(current),flush=True)
sys.stdout.flush();sys.stderr.flush();os._exit(0 if report['pass'] else 1)
