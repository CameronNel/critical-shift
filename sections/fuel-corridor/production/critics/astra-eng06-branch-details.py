"""CPU read-only bounds of eng06 signs and reactor pressed leaf components."""
import bpy,json,hashlib
from pathlib import Path
base=Path(__file__).resolve().parent
snap=base.parent/'checkpoints/eng06'
dg=bpy.context.evaluated_depsgraph_get()
report={'blend_sha256':hashlib.sha256((snap/'Fuel_Corridor.blend').read_bytes()).hexdigest(),'signs':{},'reactor_pressed_components':[],'saved':False,'scope':'Evaluated bounds and parent/export identities only. Axis gaps are reported separately as numeric contact diagnostics, not complete triangle support or collision certification.'}
for group,prefix in [('plant','Plant_blade_'),('clean','Clean_blade_'),('reactor_pressed','REACTOR_BOUNDARY_leaf_pressed_')]:
    components=[];all_points=[]
    for ob in bpy.context.scene.objects:
        if not ob.name.startswith(prefix) or ob.type not in {'MESH','CURVE','FONT','SURFACE'}:continue
        eo=ob.evaluated_get(dg);mesh=eo.to_mesh()
        try:
            vs=[eo.matrix_world@v.co for v in mesh.vertices]
            if not vs:continue
            all_points.extend(vs)
            row={'object':ob.name,'type':ob.type,'parent':ob.parent.name if ob.parent else None,'bounds_xyz':[[round(f(v[i] for v in vs),9) for i in range(3)] for f in [min,max]],'collision_policy':ob.get('collision_handoff'),'external_presentation_cap':bool(ob.get('external_presentation_cap',False))}
            components.append(row)
        finally:eo.to_mesh_clear()
    if group=='reactor_pressed':report['reactor_pressed_components']=components;continue
    b=[[round(f(v[i] for v in all_points),9) for i in range(3)] for f in [min,max]]
    panel=next(o for o in components if o['object']==prefix+'panel')
    drops=[o for o in components if o['object'].startswith(prefix+'drop')]
    report['signs'][group]={'components':components,'assembly_bounds_xyz':b,'bottom_above_operating_height_2p2_m':round(b[0][2]-2.2,9),'drop_to_panel_axis_gaps_m':[round(o['bounds_xyz'][0][2]-panel['bounds_xyz'][1][2],9) for o in drops]}
out=base/'astra-eng06-branch-detail-evidence.json';out.write_text(json.dumps(report,indent=2),encoding='utf-8')
print('DETAIL_AUDIT_DONE',out)
