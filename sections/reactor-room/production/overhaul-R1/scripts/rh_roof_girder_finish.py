"""Give the roof girders a readable neutral-gray painted steel finish."""
import bpy
NAME='RH roof girder Audi grey coating'
OBJECT='RH walls girders STEEL'
def apply(objects):
    obj=objects[OBJECT]
    assert len(obj.data.materials)==1
    current=obj.data.materials[0]
    material=bpy.data.materials.get(NAME)
    if material is None:
        material=current.copy();material.name=NAME
    tree=material.node_tree
    base=[n for n in tree.nodes if n.type=='VECT_MATH' and n.operation=='SCALE' and not n.inputs[0].is_linked]
    assert len(base)==1,('Unexpected girder color graph',len(base))
    shader=next(n for n in tree.nodes if n.type=='BSDF_PRINCIPLED')
    rough=shader.inputs['Roughness'].links[0].from_node
    assert rough.type=='MAP_RANGE'
    base[0].inputs[0].default_value=(.22,.22,.22)
    shader.inputs['Metallic'].default_value=.12
    rough.inputs['To Min'].default_value=.56*.82
    rough.inputs['To Max'].default_value=.56*1.18
    obj.data.materials[0]=material
    return {'object':OBJECT,'material':NAME,'base_rgb':[.22,.22,.22],'metallic':.12,'roughness_nominal':.56,'scope':'Owned girder material slot/clone only; adjacent wall/roof steel, geometry, lighting, exposure and animation unchanged.'}
