"""Move the complete C01-screening bollard to the ray-verified south bay."""
import json
from mathutils import Matrix,Vector

OLD=(8.3,-1.56)
NEW=(8.3,-2.38)
EXPECTED={'BLACK':36,'STEEL':200,'WHITE':36,'YELLOW':109}


def apply(scene,objects):
    key='rh_switchgear_bollard_access_fit'
    if key in scene:return json.loads(scene[key])
    dy=NEW[1]-OLD[1]
    changed=[]
    for material,count in EXPECTED.items():
        obj=objects['RH stations props '+material]
        assert obj.type=='MESH' and obj.data.users==1
        assert obj.matrix_world==Matrix.Identity(4),'Expected owned merged world-coordinate prop mesh'
        before=[tuple(v.co) for v in obj.data.vertices]
        indices={v.index for v in obj.data.vertices
                 if abs(v.co.x-OLD[0])<.125 and abs(v.co.y-OLD[1])<.125 and -.001<=v.co.z<=.954}
        assert len(indices)==count,(obj.name,len(indices),count)
        selected_faces=[]
        for face in obj.data.polygons:
            selected=sum(i in indices for i in face.vertices)
            assert selected in (0,len(face.vertices)),'Selection cuts a connected prop face'
            if selected:selected_faces.append(face.index)
        for index in indices:obj.data.vertices[index].co.y+=dy
        for vertex,prior in zip(obj.data.vertices,before):
            if vertex.index not in indices:assert tuple(vertex.co)==prior
            else:assert vertex.co.x==prior[0] and vertex.co.z==prior[2] and abs(vertex.co.y-prior[1]-dy)<1e-6
        obj.data.update()
        changed.append({'object':obj.name,'moved_vertices':len(indices),'moved_faces':len(selected_faces),
                        'unselected_vertices_unchanged':True,'topology_materials_matrix_unchanged':True})
    registry=json.loads(scene['rh_support_registry'])
    matches=[]
    for row in registry:
        anchors=row['anchors']
        if row['owner']=='stations props' and row['name']=='bollard' and len(anchors)==4:
            center=tuple(sum(p[i] for p in anchors)/4 for i in (0,1))
            if all(abs(a-b)<1e-6 for a,b in zip(center,OLD)):matches.append(row)
    assert len(matches)==1,'Expected exactly one registered four-anchor bollard seat'
    row=matches[0]
    assert row['subject']=='RH stations props' and row['target']=='R2 floor' and row['kind']=='floor'
    original=[list(p) for p in row['anchors']]
    for anchor in row['anchors']:anchor[1]+=dy
    scene['rh_support_registry']=json.dumps(registry)
    report={'old_center_xy':list(OLD),'new_center_xy':list(NEW),'delta_y_m':dy,
            'objects':changed,'moved_vertices_total':sum(r['moved_vertices'] for r in changed),
            'support_record_id':row['id'],'old_floor_anchors':original,'new_floor_anchors':row['anchors'],
            'scope':'Complete bollard body, cap, bands, footplate and four bolt heads. Only 381 selected vertices on four retained prop meshes and one existing support record change. Other prop vertices, all mesh topology/materials/matrices, lights, cameras and protected equipment stay unchanged.',
            'art_acceptance':False}
    assert report['moved_vertices_total']==381
    scene[key]=json.dumps(report,sort_keys=True)
    return report
