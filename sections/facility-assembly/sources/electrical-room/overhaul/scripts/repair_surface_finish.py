"""Apply declared material/practical changes while preserving existing geometry."""
import argparse,hashlib,json,os,sys
from pathlib import Path
import bpy
sys.path.insert(0,str(Path(__file__).resolve().parent))
import kit as k
from surface_finish import apply
p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--receipt',required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
source=Path(bpy.data.filepath).resolve();out=Path(a.output).resolve();assert source!=out
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
input_sha=sha(source)
def geometry(o):
    d={'matrix':sum((list(r) for r in o.matrix_world),[]),'type':o.type}
    if o.type=='MESH':d['verts']=[list(v.co) for v in o.data.vertices];d['faces']=[list(p.vertices) for p in o.data.polygons]
    return hashlib.sha256(json.dumps(d,sort_keys=True).encode()).hexdigest()
before={o.name:geometry(o) for o in bpy.context.scene.objects}
assert not bpy.context.scene.get('electrical_surface_finish_revision')
keys=['cream','slate','enamel','floor','route']
changes=apply(k,{n:bpy.data.materials[k.PREFIX+n] for n in keys})
bpy.context.view_layer.update()
assert all(geometry(bpy.data.objects[n])==sig for n,sig in before.items())
bpy.context.preferences.filepaths.save_version=0;out.parent.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
assert sha(source)==input_sha
receipt={'input_sha256':input_sha,'output_sha256':sha(out),'declared_changes':changes,
         'original_geometry_matrices_unchanged':True,'checked_objects':len(before),
         'source_bytes_unchanged':True,'scope':'Declared broad material response, existing practical powers and six supported service-floor contact additions; no shell/camera/interface edits'}
Path(a.receipt).resolve().write_text(json.dumps(receipt,indent=2)+'\n')
print('SURFACE_FINISH_SAVED',out,flush=True)
sys.stdout.flush();sys.stderr.flush();os._exit(0)
