"""Read-only player-eye position and near-field checks for supplementary views."""
import ast,bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[1];source=root/'blender/render_final_walkthrough.py'
tree=ast.parse(source.read_text())
views=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='views' for t in n.targets))
s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();rows=[]
for name,loc,target in views:
    origin=Vector(loc);forward=(Vector(target)-origin).normalized()
    rotation=forward.to_track_quat('-Z','Y').to_matrix()
    hit,p,n,idx,obj,_=s.ray_cast(dg,origin,Vector((0,0,-1)),distance=2)
    floor={'object':obj.name if hit else None,'z':p.z if hit else None,'eye_above_hit':origin.z-p.z if hit else None}
    near=[]
    for ix in range(9):
        for iy in range(7):
            direction=rotation@Vector((-.018+.036*ix/8,-.012+.024*iy/6,-.022)).normalized()
            hit,p,n,idx,obj,_=s.ray_cast(dg,origin,direction,distance=.12)
            if hit:near.append({'object':obj.name,'distance':(p-origin).length})
    good=floor['eye_above_hit'] is not None and abs(floor['eye_above_hit']-1.7)<=.005 and not near
    rows.append({'view':name,'position':loc,'target':target,'floor':floor,'near_hits':near,'pass':good})
report={'blend_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'walkthrough_source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'rows':rows,'pass':all(r['pass'] for r in rows),'scope':'Twelve grounded1.70m eye positions and63 near-field rays each. Not a continuous body/controller simulation or full optical occlusion proof.'}
(root/'production/evidence/final-pass/walkthrough-positions.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report));assert report['pass']
