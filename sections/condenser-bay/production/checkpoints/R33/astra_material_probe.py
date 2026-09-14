"""Read-only saved shader and surface diagnostics; run under resource_guard."""
import bpy,json
rows=[]
for o in bpy.context.scene.objects:
    if not o.name.startswith(('CD chest wall','CD chest flange','CD shell','LG -1 0 glass')):continue
    row={'object':o.name,'materials':[],'modifiers':[m.type for m in o.modifiers]}
    for slot in o.material_slots:
        m=slot.material
        if not m:continue
        row['materials'].append({'name':m.name,'bump_distances':[n.inputs['Distance'].default_value for n in m.node_tree.nodes if n.type=='BUMP']})
    rows.append(row)
print('ASTRA_MATERIAL_PROBE',json.dumps(rows),flush=True)
