"""Fresh-process saved-artifact fingerprint; read only, no save or render."""
import bpy,json,hashlib,sys
from pathlib import Path

def clean(v):
    if isinstance(v,(str,int,bool,float)) or v is None:return v
    try:return [clean(x) for x in v]
    except TypeError:return str(v)

scene=bpy.context.scene;objects=[];materials=[];dg=bpy.context.evaluated_depsgraph_get()
for o in sorted(scene.objects,key=lambda x:x.name):
    row={'name':o.name,'type':o.type,'matrix':clean(o.matrix_world),'materials':[m.name if m else None for m in o.data.materials] if hasattr(o.data,'materials') else []}
    if o.type in {'MESH','CURVE','FONT'}:
        ev=o.evaluated_get(dg);me=ev.to_mesh()
        geometry={'vertices':[[round(v,7) for v in p.co] for p in me.vertices],'polygons':[list(p.vertices) for p in me.polygons]}
        row['evaluated_sha256']=hashlib.sha256(json.dumps(geometry).encode()).hexdigest();row['vertices']=len(me.vertices);ev.to_mesh_clear()
    if o.type=='FONT':row['text']=o.data.body
    if o.type=='CAMERA':row['camera']={'lens':o.data.lens,'clip_start':o.data.clip_start,'clip_end':o.data.clip_end}
    if o.type=='LIGHT':row['light']={'energy':o.data.energy,'color':clean(o.data.color),'type':o.data.type}
    if o.type=='EMPTY':row['metadata']={k:clean(o[k]) for k in o.keys()}
    objects.append(row)
for m in sorted(bpy.data.materials,key=lambda x:x.name):
    row={'name':m.name,'diffuse':clean(m.diffuse_color),'nodes':[],'links':[]}
    if m.node_tree:
        for n in sorted(m.node_tree.nodes,key=lambda x:x.name):
            r={'name':n.name,'type':n.bl_idname,'inputs':{i.name:clean(i.default_value) for i in n.inputs if hasattr(i,'default_value')}}
            if hasattr(n,'color_ramp'):r['ramp']=[{'position':e.position,'color':clean(e.color)} for e in n.color_ramp.elements]
            if hasattr(n,'operation'):r['operation']=n.operation
            row['nodes'].append(r)
        row['links']=sorted((l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier) for l in m.node_tree.links)
    materials.append(row)
data={'objects':objects,'materials':materials,'images':[{'name':i.name,'path':i.filepath,'packed':bool(i.packed_file),'source':i.source} for i in bpy.data.images if i.type!='RENDER_RESULT'],'cameras':scene.get('camera_contract'),'supplement':scene.get('supplementary_cameras'),'source_revision':scene.get('revision'),'authoring_source_sha256':scene.get('authoring_sources')}
payload=json.dumps(data,sort_keys=True)
report={'blender':bpy.app.version_string,'file':bpy.data.filepath,'blend_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'artifact_fingerprint':hashlib.sha256(payload.encode()).hexdigest(),'objects':len(objects),'materials':len(materials),'cameras':sum(o.type=='CAMERA' for o in scene.objects),'data':data,'method':'factory startup, open saved file, evaluate geometry and serialize materials/cameras/text/markers; no write to blend'}
out=Path(sys.argv[sys.argv.index('--')+1]);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2),encoding='utf-8');print('COLD SNAPSHOT',out,report['artifact_fingerprint'])

