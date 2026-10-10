"""Narrow the two rolled drum beads on an existing integrated correction scene.

Only the eight known lathe rings per drum move. Shell, chimes, bungs,
labels, materials, faces, supports and unrelated merged geometry stay intact.
"""
import json, math
from mathutils import Vector

DRUMS=((5.2,9.5,0),(5.9,9.9,0),(5.5,8.9,0),(-6.6,-8.3,0),(-7.35,-8.65,0),
       (-3.84,4.93,.135),(-3.14,4.93,.135),(-3.84,5.67,.135),(-3.14,5.67,.135),
       (6.52,-3.70,.135),(7.18,-3.70,.135),(6.52,-2.98,.135),(7.18,-2.98,.135))

def apply(scene, objects):
    mappings=[]
    for centre,levels in ((.36,(.30,.34,.38,.42)),(.66,(.60,.64,.68,.72))):
        for index,level in enumerate(levels):
            mappings.append((.88*level,.29*(1.05 if index in (1,2) else .985),
                             .88*centre+(-.009,-.003,.003,.009)[index],
                             .29*.985+(.006 if index in (1,2) else 0)))
    hits=[0]*13; already=[0]*13; changed={};sharp_edges=0;sharp_changes=0
    for obj in objects:
        if obj.type!='MESH' or not obj.name.startswith(('RH stations props ','RH refine legacy drums ')):
            continue
        inverse=obj.matrix_world.inverted();count=0;ring_vertices=set()
        for vertex in obj.data.vertices:
            p=obj.matrix_world@vertex.co
            for number,(x,y,z) in enumerate(DRUMS):
                dx,dy=p.x-x,p.y-y;radius=math.hypot(dx,dy)
                if not .28<radius<.31:continue
                for old_z,old_r,new_z,new_r in mappings:
                    if abs(p.z-(z+old_z))<3e-6 and abs(radius-old_r)<3e-6:
                        vertex.co=inverse@Vector((x+dx*new_r/radius,y+dy*new_r/radius,z+new_z))
                        hits[number]+=1;count+=1;ring_vertices.add(vertex.index);break
                    if abs(p.z-(z+new_z))<3e-6 and abs(radius-new_r)<3e-6:
                        already[number]+=1;ring_vertices.add(vertex.index);break
                else:continue
                break
        # The narrowed 45-degree shoulders cross the builder's 38-degree
        # sharp-edge threshold. Preserve radial smoothing, but prevent these
        # bends from smearing their normals over the long cylinder faces.
        for edge in obj.data.edges:
            a,b=edge.vertices
            if a in ring_vertices and b in ring_vertices:
                pa=obj.matrix_world@obj.data.vertices[a].co
                pb=obj.matrix_world@obj.data.vertices[b].co
                if abs(pa.z-pb.z)<1e-6:
                    sharp_edges+=1
                    if not edge.use_edge_sharp:sharp_changes+=1;edge.use_edge_sharp=True
        if count or ring_vertices:obj.data.update()
        if count:changed[obj.name]=count
    assert [a+b for a,b in zip(hits,already)]==[384]*13, ('Unexpected drum ring coverage',hits,already)
    assert sharp_edges==4992, ('Unexpected bead-edge coverage',sharp_edges)
    report={'drums':13,'vertices_changed':sum(hits),'per_drum_ring_vertices':hits,
            'already_correct_ring_vertices':already,
            'bead_edges_sharp':sharp_edges,'edge_sharp_flags_changed':sharp_changes,
            'objects':changed,'bead_width_m':.018,'bead_projection_m':.006,
            'scope':'Eight known 48-vertex rings and their circumferential sharp flags per drum only; no topology, materials, transforms, supports or other vertices changed.'}
    scene['rh_drum_hoop_correction']=json.dumps(report,sort_keys=True)
    return report
