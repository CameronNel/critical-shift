"""Read-only coverage and physical-scale statistics for actual consumed UVs."""
import argparse,hashlib,json,math,sys
from pathlib import Path
import bpy

HERE=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--expected-sha',required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
native=Path(bpy.data.filepath);assert sha(native)==a.expected_sha
S=bpy.data.scenes['COMPLIANCE_EDIT_LOCAL'];deps=bpy.context.evaluated_depsgraph_get()
rows=[];errors=[]
for obj in S.objects:
    if obj.type!='MESH':continue
    required=sorted({n.uv_map for m in obj.data.materials if m and m.use_nodes for n in m.node_tree.nodes if n.type=='UVMAP'})
    if not required:continue
    evaluated=obj.evaluated_get(deps);me=evaluated.to_mesh();me.calc_loop_triangles()
    world=[obj.matrix_world@v.co for v in me.vertices]
    for name in required:
        layer=me.uv_layers.get(name)
        if layer is None:errors.append({'object':obj.name,'missing_consumed_layer':name});continue
        areas=[];ratios=[];bad=0;collapsed=0;world_area=0;uv_area=0;minimum=math.inf;maximum=0
        for t in me.loop_triangles:
            vertices=[world[i] for i in t.vertices];uvs=[layer.data[i].uv.copy() for i in t.loops]
            area=(vertices[1]-vertices[0]).cross(vertices[2]-vertices[0]).length/2
            chart=abs((uvs[1].x-uvs[0].x)*(uvs[2].y-uvs[0].y)-(uvs[1].y-uvs[0].y)*(uvs[2].x-uvs[0].x))/2
            if not all(math.isfinite(v) for uv in uvs for v in uv):bad+=1;continue
            if area>1e-12 and chart<1e-14:collapsed+=1
            world_area+=area;uv_area+=chart
            if area>1e-12:areas.append((chart/area,area))
            for i in range(3):
                distance=(vertices[(i+1)%3]-vertices[i]).length
                if distance>.0001:
                    ratio=(uvs[(i+1)%3]-uvs[i]).length/distance
                    minimum=min(minimum,ratio);maximum=max(maximum,ratio)
        rows.append({'object':obj.name,'layer':name,'consumed_materials':[m.name for m in me.materials if m and m.use_nodes and any(n.type=='UVMAP' and n.uv_map==name for n in m.node_tree.nodes)],
            'triangle_count':len(me.loop_triangles),'nonfinite_triangles':bad,'collapsed_uv_triangles':collapsed,
            'world_area_m2':world_area,'uv_area':uv_area,'aggregate_area_ratio':uv_area/world_area if world_area else None,
            'edge_scale_min':minimum if minimum<math.inf else None,'edge_scale_max':maximum,
            'overlap_policy':obj.get('uv_contract'),'fabric_contract':obj.get('fabric_uv_contract'),
            'fabric_normalization':obj.get('fabric_uv_normalization')})
        if bad or collapsed:errors.append({'object':obj.name,'layer':name,'nonfinite':bad,'collapsed':collapsed})
    evaluated.to_mesh_clear()
assert sha(native)==a.expected_sha
report={'native_sha256':a.expected_sha,'probe_sha256':sha(__file__),'coverage_errors':errors,'rows':rows,
    'interpretation':'Intentional tiled face charts are not a bake/lightmap atlas. Fabric area normalization does not independently prove local edge distortion or seam continuity.'}
(HERE/'independent-uv.json').write_text(json.dumps(report,indent=2)+'\n')
print('INDEPENDENT_UV',len(rows),'ROWS',len(errors),'COVERAGE_ERRORS')
