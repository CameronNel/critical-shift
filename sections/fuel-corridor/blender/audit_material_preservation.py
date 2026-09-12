"""Fresh-process material-node, texture and UV comparison; no scene writes."""
import bpy,json,hashlib,sys
from pathlib import Path
args=sys.argv[sys.argv.index('--')+1:]
def plain(value):
    if isinstance(value,(str,bool,int)) or value is None:return value
    if isinstance(value,float):return round(value,7)
    try:return [plain(v) for v in value]
    except TypeError:return str(value)
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest()
def snapshot(path):
    bpy.ops.wm.open_mainfile(filepath=path,load_ui=False,use_scripts=False)
    materials={}
    for m in bpy.data.materials:
        nodes=[];links=[]
        if m.node_tree:
            for n in m.node_tree.nodes:
                row={'name':n.name,'type':n.bl_idname,'inputs':{s.identifier:plain(s.default_value) for s in n.inputs if hasattr(s,'default_value')}}
                for key in ['operation','blend_type','data_type','interpolation','extension','projection','vector_type']:
                    if hasattr(n,key):row[key]=plain(getattr(n,key))
                if hasattr(n,'image'):row['image']=n.image.name if n.image else None
                if hasattr(n,'color_ramp'):row['ramp']=[(e.position,list(e.color)) for e in n.color_ramp.elements]
                nodes.append(row)
            links=sorted((l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier) for l in m.node_tree.links)
        materials[m.name]=digest({'color':list(m.diffuse_color),'nodes':nodes,'links':links})
    uv={o.name:digest({l.name:[list(x.uv) for x in l.data] for l in o.data.uv_layers}) for o in bpy.context.scene.objects if o.type=='MESH' and o.data.uv_layers}
    textures={i.name:hashlib.sha256(i.packed_file.data).hexdigest() if i.packed_file else None for i in bpy.data.images}
    return {'materials':materials,'uv':uv,'textures':textures}
a=snapshot(args[0]);b=snapshot(args[1]);differences={}
for kind in a:
    differences[kind]={'changed':sorted(n for n in a[kind].keys()&b[kind].keys() if a[kind][n]!=b[kind][n]),'missing':sorted(a[kind].keys()-b[kind].keys()),'added':sorted(b[kind].keys()-a[kind].keys())}
out={'baseline':args[0],'candidate':args[1],'differences':differences,'snapshots':{'baseline':a,'candidate':b},'limits':'Node input values, selected node operations, ramps, links, packed image bytes and UV layers. Not every possible Blender RNA property.'}
Path(args[2]).write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps(differences))
