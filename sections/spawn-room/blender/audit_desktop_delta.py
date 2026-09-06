"""Read-only audit of the saved desktop checkpoint before a newer source is opened."""
import bpy,sys,json,hashlib,array
from pathlib import Path

def simple(value):
    if isinstance(value,(str,bool,int,float)):return value
    try:return list(value)
    except TypeError:return str(value)

def snapshot(path):
    bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False)
    objects={};materials={}
    for o in bpy.data.objects:
        row={'type':o.type,'matrix':[list(r) for r in o.matrix_basis],'parent':o.parent.name if o.parent else None,'hidden':[o.hide_viewport,o.hide_render],'materials':[s.material.name if s.material else None for s in o.material_slots]}
        if o.type=='MESH':
            h=hashlib.sha256()
            for coll,prop,width,kind in [(o.data.vertices,'co',3,'f'),(o.data.loops,'vertex_index',1,'i'),(o.data.polygons,'material_index',1,'i')]:
                v=array.array(kind,[0])*(len(coll)*width);coll.foreach_get(prop,v);h.update(v.tobytes())
            row['geometry']=h.hexdigest()
        elif o.type in {'CURVE','FONT'}:
            row['body']=getattr(o.data,'body',None)
            row['splines']=[[[list(p.co) for p in s.points],[list(p.co) for p in s.bezier_points]] for s in o.data.splines]
        elif o.type=='LIGHT':row['light']=[o.data.energy,list(o.data.color)]
        elif o.type=='CAMERA':row['camera']=[o.data.lens,o.data.sensor_width]
        objects[o.name]=row
    for m in bpy.data.materials:
        if not m.use_nodes:continue
        materials[m.name]={'nodes':{n.name:{'type':n.bl_idname,'inputs':{s.identifier:simple(s.default_value) for s in n.inputs if hasattr(s,'default_value')}} for n in m.node_tree.nodes},'links':sorted([(l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier) for l in m.node_tree.links])}
    return {'objects':objects,'materials':materials}

args=sys.argv[sys.argv.index('--')+1:];first=snapshot(Path(args[0]));second=snapshot(Path(args[1]))
out={}
for category in first:
    a,b=first[category],second[category]
    out[category]={'added':sorted(set(b)-set(a)),'removed':sorted(set(a)-set(b)),'changed':[k for k in a.keys()&b.keys() if a[k]!=b[k]]}
Path(args[2]).write_text(json.dumps(out,indent=2));print('DESKTOP_DELTA',json.dumps(out),flush=True)
