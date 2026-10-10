"""Localized grime at the six actual doorway return surfaces, not hall walls."""
import bpy
import json
from mathutils import Vector
from r2lib import WALLS

DOORS = [(6,'MAIN ACCESS'),(4,'FUEL HANDLING'),(1,'COOLING PLANT')]


def apply(scene, objects, materials):
    base = materials['RH refine wall concrete']
    report = []
    for wall_index, label in DOORS:
        wall = WALLS[wall_index]
        material_name = 'RH localized '+label+' return grime'
        owned = materials.get(material_name)
        returns = [objects[label+'.link wall'], objects[label+'.link wall.001']]
        assert all(o.type == 'MESH' for o in returns)
        if owned is not None:
            assert all(len(o.data.materials)==1 and o.data.materials[0]==owned for o in returns)
            report.append({'door':label,'objects':[o.name for o in returns],'material':owned.name})
            continue
        assert all(len(o.data.materials)==1 and o.data.materials[0]==base for o in returns)
        owned = base.copy()
        owned.name = material_name
        tree = owned.node_tree
        serial = 0
        def node(kind):
            nonlocal serial
            result = tree.nodes.new(kind)
            result.name = 'RH return grime '+str(serial)
            serial += 1
            return result
        def wire(socket, value):
            if isinstance(value,bpy.types.NodeSocket): tree.links.new(value,socket)
            else: socket.default_value = value
        def math(operation,a,b):
            result=node('ShaderNodeMath');result.operation=operation
            wire(result.inputs[0],a);wire(result.inputs[1],b)
            return result.outputs[0]
        def ramp(value,start,end,low,high):
            result=node('ShaderNodeMapRange');result.clamp=True;result.interpolation_type='SMOOTHSTEP'
            wire(result.inputs[0],value)
            for index,item in enumerate((start,end,low,high),1):result.inputs[index].default_value=item
            return result.outputs[0]
        geometry=node('ShaderNodeNewGeometry')
        coordinates=node('ShaderNodeSeparateXYZ');tree.links.new(geometry.outputs['Position'],coordinates.inputs[0])
        depth=node('ShaderNodeVectorMath');depth.operation='DOT_PRODUCT'
        tree.links.new(geometry.outputs['Position'],depth.inputs[0])
        depth.inputs[1].default_value=(wall.n.x,wall.n.y,0)
        datum=Vector((wall.P.x,wall.P.y,0)).dot(Vector((wall.n.x,wall.n.y,0)))
        local_depth=math('SUBTRACT',depth.outputs['Value'],datum)
        mouth=ramp(local_depth,-1.20,-.25,0,1)
        z=coordinates.outputs['Z']
        ground=ramp(z,.12,1.10,.50,0)
        roof_height=max((o.matrix_world@Vector(c)).z for o in returns for c in o.bound_box)
        head=ramp(z,roof_height-1.10,roof_height-.04,0,.42)
        edge=math('MULTIPLY',ramp(local_depth,-.40,-.08,0,.20),ramp(local_depth,-.08,.02,1,0))
        areas=math('MAXIMUM',math('MAXIMUM',ground,head),edge)
        noise=node('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=4.5;noise.inputs['Detail'].default_value=3
        tree.links.new(geometry.outputs['Position'],noise.inputs['Vector'])
        irregular=ramp(noise.outputs['Fac'],.25,.75,.25,1)
        weight=math('MULTIPLY',math('MULTIPLY',areas,mouth),irregular)
        shader=next(n for n in tree.nodes if n.type=='BSDF_PRINCIPLED')
        original=shader.inputs['Base Color'].links[0].from_socket
        mix=node('ShaderNodeMixRGB');mix.blend_type='MIX';mix.inputs[2].default_value=(.095,.092,.08,1)
        tree.links.new(weight,mix.inputs[0]);tree.links.new(original,mix.inputs[1]);tree.links.new(mix.outputs[0],shader.inputs['Base Color'])
        for obj in returns:obj.data.materials[0]=owned
        report.append({'door':label,'objects':[o.name for o in returns],'material':owned.name})
    result={'returns':report,'scope':'Only three owned material clones on six kept side-return meshes; masks begin at floor/head joints and the mouth edge, within the first1.2m of each return. Hall-wide materials, geometry, lighting, signs and water unchanged.','art_acceptance':False}
    scene['rh_door_return_stain_fit']=json.dumps(result,sort_keys=True)
    return result
