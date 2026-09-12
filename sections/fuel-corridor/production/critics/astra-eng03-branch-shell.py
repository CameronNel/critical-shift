"""Frozen CPU read-only shell/seam bounds follow-up; no save/render/import."""
import bpy,json,hashlib,datetime
from pathlib import Path
from mathutils import Vector,Matrix
BASE=Path(__file__).resolve().parent
SNAP=BASE.parent/'checkpoints/eng03'
contract=json.loads((SNAP/'interface.json').read_text())
dg=bpy.context.evaluated_depsgraph_get()
def bds(vs):return [[min(v[i] for v in vs) for i in range(3)],[max(v[i] for v in vs) for i in range(3)]]
def rounded(rows):return [[round(x,7) for x in row] for row in rows]
report={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'blend_sha256':hashlib.sha256((SNAP/'Fuel_Corridor.blend').read_bytes()).hexdigest(),'scope':'All evaluated physical geometry near each external freight seam, including shoulder regions 1.50m outside nominal aperture edges. Separate interface mating transforms only. No neighbor geometry or collision test. Nominal footprint means clear-width strip for the owned sill/stub length; it is not a full neighbor building envelope.','seams':[],'saved':False}
for pid,key,length in [('F01_REFINERY','F01_connector_to_refinery',1.1),('F02_REACTOR','F02_connector_to_reactor',3.7)]:
    p=next(p for p in contract['ports'] if p['id']==pid);c=Vector(p['center']);n=Vector(p['outward']);t=Vector((-n.y,n.x,0));w=p['clear_width'];h=p['clear_height'];M=Matrix(contract['adjacent_measurements']['separate_mating_transforms'][key]['matrix4'])
    result={'id':pid,'nominal_clear_width_height':[w,h],'neighbor_owned_length':length,'architecture_near_seam':[],'masonry_beyond_seam_in_nominal_plan_footprint':[],'other_shell_beyond_seam_in_nominal_plan_footprint':[],'any_selected_shell_beyond_seam':[]}
    for ob in bpy.context.scene.objects:
        if ob.type not in {'MESH','CURVE','FONT','SURFACE'}:continue
        eo=ob.evaluated_get(dg);mesh=eo.to_mesh()
        try:
            vs=[eo.matrix_world@v.co for v in mesh.vertices]
            if not vs:continue
            local=[Vector(((v-c).dot(t),(v-c).dot(n),v.z)) for v in vs];lb=bds(local)
            if lb[1][0]<-w/2-1.5 or lb[0][0]>w/2+1.5 or lb[1][1]<-.6 or lb[0][1]>.6:continue
            u0,u1=max(lb[0][0],-w/2),min(lb[1][0],w/2);d0,d1=max(lb[0][1],0),min(lb[1][1],length)
            inside_plan=u1-u0>1e-5 and d1-d0>1e-5
            row={'object':ob.name,'type':ob.type,'materials':[m.name for m in mesh.materials],'bounds_corridor_xyz':rounded(bds(vs)),'bounds_u_outward_z':rounded(lb),'bounds_neighbor_xyz':rounded(bds([M@v for v in vs])),'beyond_seam_m':round(max(0,lb[1][1]),7),'positive_overlap_with_nominal_neighbor_plan':inside_plan,'positive_overlap_with_nominal_opening_height':inside_plan and min(lb[1][2],h)-max(lb[0][2],0)>1e-5}
            result['architecture_near_seam'].append(row)
            if lb[1][1]>.00001:result['any_selected_shell_beyond_seam'].append(row)
            if inside_plan:
                row['overlap_ud_z']=[[round(u0,7),round(d0,7),round(lb[0][2],7)],[round(u1,7),round(d1,7),round(lb[1][2],7)]]
                result['masonry_beyond_seam_in_nominal_plan_footprint' if ('masonry' in ob.name or '_concrete' in ob.name) else 'other_shell_beyond_seam_in_nominal_plan_footprint'].append(row)
        finally:eo.to_mesh_clear()
    report['seams'].append(result)
out=BASE/'astra-eng03-branch-shell-evidence.json';out.write_text(json.dumps(report,indent=2),encoding='utf-8')
print('SHELL_AUDIT_DONE',out)


