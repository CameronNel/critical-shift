"""Clear the measured vestibule-roof clash without editing reactor geometry."""
import bpy,ast,math,hashlib,json,ctypes
from pathlib import Path
from mathutils import Vector
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x4000)
root=Path(__file__).resolve().parents[3];src=Path(bpy.data.filepath);out=root/'runtime/out/spawn-integration';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
before=sha(src);assert before=='bb93d7c8c5b86c10af95409cf1eecfa05d1ac0a5989b42caab185bc52dee06f3'
coll=bpy.data.collections['ART | Spawn and medical courtyard']
tree=ast.parse(Path(__file__).with_name('build_refinery_exterior.py').read_text().replace("'RFX | '","'SY | '"))
for name in ('mesh','pipe'):
    fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name);exec(compile(ast.Module(body=[fn],type_ignores=[]),'<preserved pipe helper>','exec'))
old=bpy.data.objects['SY | Tall service riser'];wall=3.4644222259521484
new=pipe('Temporary corrected riser',[(wall-.06,41.8,12.1),(wall-.22,41.8,11.8),(wall-.22,41.8,1.1),(wall-.06,41.8,.8)],.115,old.data.materials[0])
old.data=new.data;bpy.data.objects.remove(new,do_unlink=True)
for o in coll.objects:
    if o.name.startswith(('SY | Tall pipe flange','SY | Tall pipe sealed joint')):o.location.x+=.20
    elif o.name.startswith('SY | Tall riser wall bracket'):
        pts=[o.matrix_world@v.co for v in o.data.vertices];lo=min(p.x for p in pts);hi=max(p.x for p in pts);inv=o.matrix_world.inverted();o.data=o.data.copy()
        for v,p in zip(o.data.vertices,pts):p.x=lo+.20+(p.x-lo)/(hi-lo)*(hi-lo-.20);v.co=inv@p
        o.data.update()
assert sha(src)==before;bpy.context.view_layer.update();bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(src),check_existing=False)
(out/'riser-correction.json').write_text(json.dumps(dict(before=before,after=sha(src),move_m=.20,reason='18 triangle pairs intersected Vestibule roof; keep end connections and clear roof/stair interfaces'),indent=2))
print('RISER_CLEARED',sha(src),flush=True)
