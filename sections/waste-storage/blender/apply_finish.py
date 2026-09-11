"""Apply the W06 owned correction to the saved W05 artifact, without rebuilding."""
import bpy,ast,math,json,random,hashlib,argparse,sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];SC=bpy.context.scene
parser=argparse.ArgumentParser();parser.add_argument('--pass-file',default='finish_pass.py');parser.add_argument('--from-revision',default='W05');parser.add_argument('--to-revision',default='W06');args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
assert SC.get('section')=='waste-storage' and SC.get('revision')==args.from_revision
tree=ast.parse((ROOT/'blender/build_scene.py').read_text())
for n in tree.body:
    if isinstance(n,ast.FunctionDef):exec(compile(ast.Module(body=[n],type_ignores=[]),'owned_helpers','exec'))
COL={c.name:c for c in SC.collection.children};current='Architecture';SUP=[];M={}
for n in tree.body:
    if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='M' for t in n.targets) and isinstance(n.value,ast.Dict):
        for key,value in zip(n.value.keys,n.value.values):
            M[key.value]=bpy.data.materials.get(value.args[0].value)
            if M[key.value] is None:M[key.value]=eval(compile(ast.Expression(value),'owned_material','eval'))
for key,name in [('wall','Warm architectural concrete'),('pale','Ivory industrial enamel'),('paint','Oxide painted steel')]:M[key]=bpy.data.materials.get(name)
M['floor']=bpy.data.objects['Floor'].data.materials[0]
for key,name in [('lamp','Warm prismatic diffuser'),('green','Energized pilot lens'),('amber','Transfer pilot lens'),('glass','Instrument glass')]:M[key]=bpy.data.materials.get(name)
existing_lights=set(bpy.data.lights.keys())
exec(compile((ROOT/'blender'/args.pass_file).read_text(),args.pass_file,'exec'))
for light_data in bpy.data.lights:
    if light_data.name not in existing_lights:light_data.energy*=.25
SC['revision']=args.to_revision
SC['interface_json']=(ROOT/'interface.json').read_text()
SC['authoring_sources']=json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'blender').glob('*.py')},sort_keys=True)
SC['camera_manifest']=json.dumps([{'name':o.name,'location':list(o.location),'rotation_euler':list(o.rotation_euler),'lens':o.data.lens} for o in SC.objects if o.type=='CAMERA'])
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print('REVISION_SAVED',args.to_revision,len(SC.objects),flush=True)

