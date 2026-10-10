"""Give each switchgear breaker a fitted, high-contrast circuit nameplate."""
import json
from mathutils import Matrix,Vector

PLATE='RH stations east WHITE'
INK='RH refine label ink'
ROWS=((.26,.282,.30),(.71,.732,.75),(1.16,1.182,1.20))

def apply(scene,objects,materials):
    key='rh_switchgear_circuit_label_fit'
    if key in scene:return json.loads(scene[key])
    o=objects[PLATE];assert o.type=='MESH' and o.data.users==1 and o.matrix_world==Matrix.Identity(4)
    original=[tuple(v.co)for v in o.data.vertices];used=set();records=[]
    for i,py in enumerate((-1.88,-1.20,-.52)):
        for j,(z0,z1,zc)in enumerate(ROWS):
            ids={v.index for v in o.data.vertices if 9.4659<=v.co.x<=9.4691 and py-.2601<=v.co.y<=py-.0599 and z0-.0001<=v.co.z<=z1+.0001}
            assert len(ids)==24,(i,j,len(ids));assert not ids&used;used|=ids
            faces=[f for f in o.data.polygons if any(v in ids for v in f.vertices)]
            assert all(all(v in ids for v in f.vertices)for f in faces),'Plate selection cuts another component'
            for k in ids:
                v=o.data.vertices[k];v.co.z=zc+(v.co.z-(z0+z1)/2)*(.09/(z1-z0))
            name='RH refine switchgear circuit '+str((i,j));t=objects[name];assert t.type=='FONT' and t.data.body=='C%02d'%(i*3+j+1)
            t.data.size=.062;t.data.materials.clear();t.data.materials.append(materials[INK])
            scene.view_layers[0].update()
            corners=[t.matrix_world@Vector(v)for v in t.bound_box]
            t.location.y+=(py-.16)-(min(v.y for v in corners)+max(v.y for v in corners))/2
            t.location.z+=zc-(min(v.z for v in corners)+max(v.z for v in corners))/2
            scene.view_layers[0].update();corners=[t.matrix_world@Vector(v)for v in t.bound_box]
            bounds=[[min(v[a]for v in corners),max(v[a]for v in corners)]for a in range(3)]
            assert bounds[1][0]>py-.26+.015 and bounds[1][1]<py-.06-.015
            assert bounds[2][0]>zc-.045+.012 and bounds[2][1]<zc+.045-.012
            assert bounds[0][1]<9.466,'Glyphs must remain wholly in front of plate face'
            records.append({'circuit':t.data.body,'glyph':name,'plate_vertices':sorted(ids),'plate_center':[9.4675,py-.16,zc],'plate_height_m':.09,'glyph_size_m':.062,'glyph_material':INK,'glyph_world_bounds':bounds,'glyph_inside_plate_margins_pass':True})
    for v,before in zip(o.data.vertices,original):
        if v.index not in used:assert tuple(v.co)==before
        else:assert v.co.x==before[0] and v.co.y==before[1]
    o.data.update();report={'changed_mesh':PLATE,'changed_mesh_vertices':len(used),'unselected_vertices_unchanged':True,'topology_and_material_graphs_unchanged':True,'records':records,'scope':'Nine existing white circuit strips enlarged vertically to90mm. Nine existing C01–C09 curves resized to62mm, centered wholly on their own plate and assigned existing matte label ink. Cabinet, headers, lamps, handles, other white components, lighting and cameras unchanged.','art_acceptance':False}
    scene[key]=json.dumps(report,sort_keys=True);return report
