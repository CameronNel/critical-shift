"""Bring the complete generator plaque forward on fitted wall stand-offs."""
import json
from mathutils import Vector,Matrix
NAME='RH refine STANDBY GENERATOR'
ASSEMBLY=['RH refine sign STANDBY GENERATOR '+m for m in ('PANEL','ORANGE','STEEL')]
SPACERS='RH refine sign mounting spacers STEEL'
# Set only after measured whole-plaque and glyph sightline probes.
SHIFT=(.40,0,0)

def apply(scene,objects):
    key='rh_generator_sign_sightline_fit'
    if key in scene:return json.loads(scene[key])
    assert SHIFT is not None,'Measured placement has not been selected'
    shift=Vector(SHIFT);assert shift.y==0 and shift.z==0 and shift.x>0; font=objects[NAME];assert font.type=='FONT' and font.data.body=='STANDBY GENERATOR'
    rows=json.loads(scene['rh_support_registry']);owned=[r for r in rows if r['name'].startswith('sign STANDBY GENERATOR ')]
    assert len(owned)==8 and len([r for r in owned if r['name'].endswith('wall spacer')])==4
    mesh=objects[SPACERS];assert mesh.matrix_world==Matrix.Identity(4) and mesh.data.users==1
    adjacency={v.index:set()for v in mesh.data.vertices}
    for e in mesh.data.edges:
        a,b=e.vertices;adjacency[a].add(b);adjacency[b].add(a)
    used=set();components=[]
    for row in owned:
        if not row['name'].endswith('wall spacer'):continue
        assert len(row['anchors'])==1
        p=Vector(row['anchors'][0]);seed=min(mesh.data.vertices,key=lambda v:(v.co-p).length_squared).index
        pending=[seed];ids=set()
        while pending:
            i=pending.pop()
            if i in ids:continue
            ids.add(i);pending.extend(adjacency[i]-ids)
        assert not used&ids and 8<=len(ids)<=128
        assert all(abs(mesh.data.vertices[i].co.y-p.y)<.014 and abs(mesh.data.vertices[i].co.z-p.z)<.014 and -.001<mesh.data.vertices[i].co.x-p.x<.016 for i in ids)
        used|=ids;components.append(sorted(ids))
    before=[tuple(v.co)for v in mesh.data.vertices]
    for ids in components:
        x0=min(mesh.data.vertices[i].co.x for i in ids);x1=max(mesh.data.vertices[i].co.x for i in ids)
        assert .013<x1-x0<.015
        for i in ids:
            v=mesh.data.vertices[i];v.co.x=x0+(v.co.x-x0)*(x1-x0+shift.x)/(x1-x0)
    assert all(tuple(v.co)==before[v.index]for v in mesh.data.vertices if v.index not in used)
    mesh.data.update()
    before_location=list(font.location)
    for name in ASSEMBLY:
        o=objects[name];assert o.type=='MESH' and o.data.users==1 and o.matrix_world==Matrix.Identity(4)
        for v in o.data.vertices:v.co+=shift
        o.data.update()
    font.location+=shift
    for row in owned:
        if row['name'].endswith('wall plate'):row['anchors']=[list(Vector(p)+shift)for p in row['anchors']]
    scene['rh_support_registry']=json.dumps(rows)
    scene.view_layers[0].update()
    report={'changed_objects':[NAME,*ASSEMBLY,SPACERS],'shift_m':list(shift),'font_location_before':before_location,'font_location_after':list(font.location),'spacer_components':components,'spacer_vertices_moved':len(used),'support_records_moved':4,'wall_receiver_anchors_unchanged':True,'unselected_spacer_vertices_unchanged':True,'scope':'Whole generator plaque, orange edge, steel mounts and lettering moved forward together; four isolated wall-spacer components lengthened from unchanged wall seats to translated steel mounts, and four plate-seat anchors updated. Typography, plate dimensions, topology, materials, machinery, conduit, cameras and lighting unchanged. Intended main10 glyph and entire plate face visibility is required by audit; visual acceptance remains independent.','art_acceptance':False}
    scene[key]=json.dumps(report,sort_keys=True);return report
