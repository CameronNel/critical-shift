"""Build a perforated submerged diffuser while preserving the verified inlet route."""
import bpy
import json
import math
from mathutils import Vector
CENTRE=(-1.4,-3.0)
BODY='RH services R2 PIPING diffuser STEEL'
CORE='RH services R2 PIPING diffuser slot BLACK'
FLANGE='RH services R2 PIPING flange IRON'

def replace(obj, vertices, faces):
    inverse=obj.matrix_world.inverted()
    old=obj.data
    mesh=bpy.data.meshes.new(old.name+' perforated')
    mesh.from_pydata([inverse@Vector(v) for v in vertices],[],faces)
    mesh.update()
    for material in old.materials:mesh.materials.append(material)
    obj.data=mesh
    if old.users==0:bpy.data.meshes.remove(old)

def apply(scene,objects):
    x,y=CENTRE;n=48
    levels=[-3.28]+[z for k in range(5) for z in (-3.23+k*.05,-3.215+k*.05)]+[-2.98]
    vertices=[];faces=[];keys={}
    def v(r,k,j):
        key=(r,k,j%n)
        if key not in keys:
            a=2*math.pi*(j%n)/n;keys[key]=len(vertices)
            vertices.append((x+r*math.cos(a),y+r*math.sin(a),levels[k]))
        return keys[key]
    def solid(k,j):return 0<=k<len(levels)-1 and (k%2==0 or j%n%6==0)
    for k in range(len(levels)-1):
        for j in range(n):
            if not solid(k,j):continue
            a,b,c,d=v(.070,k,j),v(.070,k,j+1),v(.070,k+1,j+1),v(.070,k+1,j)
            ai,bi,ci,di=v(.064,k,j),v(.064,k,j+1),v(.064,k+1,j+1),v(.064,k+1,j)
            faces.extend([(a,b,c,d),(di,ci,bi,ai)])
            if not solid(k-1,j):faces.append((b,a,ai,bi))
            if not solid(k+1,j):faces.append((d,c,ci,di))
            if not solid(k,j-1):faces.append((a,d,di,ai))
            if not solid(k,j+1):faces.append((b,bi,ci,c))
    replace(objects[BODY],vertices,faces)
    material=bpy.data.materials.get('RH pool perforated diffuser steel') or bpy.data.materials.new('RH pool perforated diffuser steel')
    material.use_nodes=True
    shader=material.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value=(.34,.36,.35,1)
    shader.inputs['Metallic'].default_value=.8
    shader.inputs['Roughness'].default_value=.36
    objects[BODY].data.materials.clear();objects[BODY].data.materials.append(material)
    # Recessed dark channel, mechanically supported by three integral upper arms.
    vertices=[];faces=[];keys={}
    def point(r,z,j):
        a=2*math.pi*(j%n)/n
        p=(round(x+r*math.cos(a),9),round(y+r*math.sin(a),9),round(z,9))
        if p not in keys:keys[p]=len(vertices);vertices.append(p)
        return keys[p]
    def face(indices):
        clean=list(dict.fromkeys(indices))
        if len(clean)>=3:faces.append(tuple(clean))
    low=[point(.028,-3.26,j) for j in range(n)]
    ring=[point(.028,-3.007,j) for j in range(n)]
    radius=lambda j:.064 if j%n in (0,1,16,17,32,33) else .028
    star=[point(radius(j),-3.007,j) for j in range(n)]
    top=[point(radius(j),-3.001,j) for j in range(n)]
    for j in range(n):
        t=(j+1)%n
        face((low[j],low[t],ring[t],ring[j]))
        face((ring[t],star[t],star[j],ring[j]))
        face((star[j],star[t],top[t],top[j]))
    face(list(reversed(low)));face(top)
    replace(objects[CORE],vertices,faces)
    obj=objects[FLANGE];inverse=obj.matrix_world.inverted();count=0
    for vertex in obj.data.vertices:
        p=obj.matrix_world@vertex.co;r=math.hypot(p.x-x,p.y-y)
        if -3.000002<=p.z<=-2.959998 and (abs(r-.12)<2e-6 or abs(r-.075)<2e-6):
            if abs(r-.12)<2e-6:
                vertex.co=inverse@Vector((x+(p.x-x)*.075/r,y+(p.y-y)*.075/r,p.z))
            count+=1
    assert count==36,('Unexpected flange ring coverage',count)
    obj.data.update()
    report={'side_window_count':40,'outer_radius_m':.070,'shell_thickness_m':.006,'recessed_channel_radius_m':.028,'upper_support_arms':3,'flange_radius_m':.075,'scope':'Two owned diffuser meshes and its owned steel finish; known flange ring fit. Route, liner, other merged flanges and object transforms preserved.'}
    scene['rh_pool_diffuser_fit']=json.dumps(report,sort_keys=True)
    return report
