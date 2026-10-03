"""Bounded actual-paper/flat-ink surface diagnostic; no scene changes."""
import hashlib,json,sys
from pathlib import Path
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
HERE=Path(__file__).resolve().parent
EXPECTED='2820ac1c7a79a28d739d0b953d73b4490f264c119775eeeef37c46bf6792a7c6'
native=Path(bpy.data.filepath);sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
assert sha(native)==EXPECTED
S=bpy.data.scenes['COMPLIANCE_EDIT_LOCAL'];deps=bpy.context.evaluated_depsgraph_get()
def geometry(obj):
    ev=obj.evaluated_get(deps);me=ev.to_mesh()
    vs=[obj.matrix_world@v.co for v in me.vertices];fs=[list(f.vertices) for f in me.polygons]
    normals=[obj.matrix_world.to_3x3().inverted().transposed()@f.normal for f in me.polygons]
    ev.to_mesh_clear();return vs,fs,normals
def bounds(vs):return [[min(v[k] for v in vs) for k in range(3)],[max(v[k] for v in vs) for k in range(3)]]
def mats(obj):
    rows=[]
    for m in obj.data.materials:
        bs=m.node_tree.nodes.get('Principled BSDF') if m.use_nodes else None
        row={'name':m.name,'diffuse_rgba':list(m.diffuse_color)}
        if bs:
            row['principled_defaults']={name:list(bs.inputs[name].default_value) if name in ['Base Color','Emission Color'] else bs.inputs[name].default_value for name in ['Base Color','Roughness','Metallic','Emission Color','Emission Strength']}
            row['base_color_link_sources']=[l.from_node.name for l in bs.inputs['Base Color'].links]
            row['color_ramps']=[{'node':n.name,'colors':[list(e.color) for e in n.color_ramp.elements]} for n in m.node_tree.nodes if n.type=='VALTORGB']
        rows.append(row)
    return rows
paper=S.objects['Counter manifest paper'];pv,pf,pn=geometry(paper);tree=BVHTree.FromPolygons(pv,pf,all_triangles=False)
report={'native_sha256':EXPECTED,'paper':{'object':paper.name,'bounds':bounds(pv),'matrix_world':[list(r) for r in paper.matrix_world],'materials':mats(paper)},'ink':[]}
for name in ['Manifest header','Manifest line 1','Manifest line 2','Manifest line 3']:
    obj=S.objects[name];vs,fs,normals=geometry(obj);gaps=[];misses=0;witness=[]
    for v in vs:
        hit=tree.ray_cast(v+Vector((0,0,.10)),Vector((0,0,-1)),.20)
        if hit[0] is None:misses+=1;continue
        gap=v.z-hit[0].z;gaps.append(gap)
        if len(witness)<5:witness.append({'ink_vertex':list(v),'paper_surface':list(hit[0]),'signed_gap_m':gap,'paper_normal':list(hit[1])})
    report['ink'].append({'object':name,'type':obj.type,'body':obj.data.body,'extrude_m':obj.data.extrude,'size':obj.data.size,'matrix_world':[list(r) for r in obj.matrix_world],
        'bounds':bounds(vs),'normal_z_min':min(n.z for n in normals),'normal_z_max':max(n.z for n in normals),'samples':len(gaps),'paper_ray_misses':misses,
        'signed_gap_min_m':min(gaps) if gaps else None,'signed_gap_max_m':max(gaps) if gaps else None,
        'buried_samples':sum(g<-.00001 for g in gaps),'gap_witnesses':witness,'materials':mats(obj)})
assert sha(native)==EXPECTED
(HERE/'manifest-paper-ink.json').write_text(json.dumps(report,indent=2)+'\n')
print('MANIFEST_MEASUREMENTS',json.dumps({'paper_bounds':report['paper']['bounds'],'ink':[dict(object=r['object'],bounds=r['bounds'],signed_gap_min_m=r['signed_gap_min_m'],signed_gap_max_m=r['signed_gap_max_m'],buried_samples=r['buried_samples'],samples=r['samples'],normal_z_min=r['normal_z_min']) for r in report['ink']]}))
