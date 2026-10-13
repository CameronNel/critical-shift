"""Bake hanging hood self-occlusion from source geometry, independently of room lighting.

Run with the pinned spawn module open. No source datablock is edited or saved.
Two cosine-weighted hemispheres preserve the open hood's front and inside faces.
"""
import hashlib
import json
import math
import sys
from pathlib import Path
import bpy
sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector
from mathutils.bvhtree import BVHTree


def main():
    output=Path(sys.argv[sys.argv.index("--")+1]).resolve()
    path=output/"map-bindings.json"; manifest=json.loads(path.read_text())
    package=next(p for p in manifest["materials"] if p["room"]=="spawn-room")
    room=next(r for r in manifest["rooms"] if r["key"]=="spawn-room")
    bpy.context.scene.frame_set(1); graph=bpy.context.evaluated_depsgraph_get()
    instances=[(i.object.original, i.matrix_world.copy(), i.parent.name) for i in graph.object_instances
               if i.is_instance and i.parent and i.parent.name.startswith("PPE_") and i.object.original.name.startswith("SUIT_")]
    records=[]; samples=96
    for parent in sorted({parent for _,_,parent in instances}):
        vertices=[]; faces=[]; hood=None
        for original,matrix,owner in instances:
            if owner!=parent or original.name=="SUIT_VISOR": continue
            mesh=original.evaluated_get(graph).to_mesh()
            offset=len(vertices); vertices.extend(matrix@v.co for v in mesh.vertices)
            faces.extend(tuple(offset+i for i in p.vertices) for p in mesh.polygons)
            if original.name=="SUIT_HOOD":
                normal_matrix=matrix.to_3x3().inverted().transposed()
                hood=[(matrix@v.co,(normal_matrix@v.normal).normalized()) for v in mesh.vertices]
            original.evaluated_get(graph).to_mesh_clear()
        if not hood: raise ValueError("Missing source hood: "+parent)
        tree=BVHTree.FromPolygons(vertices,faces,all_triangles=False)
        def visibility(position,normal):
            tangent=normal.cross(Vector((0,0,1)) if abs(normal.z)<0.9 else Vector((1,0,0))).normalized()
            bitangent=normal.cross(tangent); clear=0
            for i in range(samples):
                radius=math.sqrt((i+0.5)/samples); angle=i*math.pi*(3-math.sqrt(5))
                direction=tangent*(radius*math.cos(angle))+bitangent*(radius*math.sin(angle))+normal*math.sqrt(1-radius*radius)
                hit=tree.ray_cast(position+normal*0.0005,direction,2.0)[0]
                clear+=hit is None
            return clear/samples
        node="CS_spawn-room_"+parent+"__SUIT_HOOD"
        if not any(o["node"]==node and o["dynamic"] for o in room["objects"]): raise ValueError("Hood binding changed: "+node)
        rows=[{"position":list(p),"front":visibility(p,n),"back":visibility(p,-n)} for p,n in hood]
        records.append({"node":node,"vertices":rows})
        print("CS_SUIT_OCCLUSION",node,len(rows),flush=True)
    file=output/"Surfaces/hanging-suit-occlusion.json"
    file.write_text(json.dumps({"samples":samples,"distanceMetres":2,"lightingIncluded":False,"meshes":records},indent=2)+"\n")
    package["suitOcclusion"]={"file":file.relative_to(output).as_posix(),"sha256":hashlib.sha256(file.read_bytes()).hexdigest()}
    path.write_text(json.dumps(manifest,indent=2)+"\n")
    from prepare_spawn import derivative_meta
    if not Path(str(file)+".meta").exists():derivative_meta(file,output)
    print("CS_SUIT_OCCLUSION_OK; source and room geometry unchanged",flush=True)


if __name__=="__main__": main()
