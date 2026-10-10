"""Reduce angular aggregate contrast without changing crack or traffic wear."""
import json

def apply(materials):
    tree=materials['RH floor wet concrete'].node_tree
    albedo=tree.nodes['Map Range.002']
    relief=tree.nodes['Math.072']
    assert albedo.type=='MAP_RANGE' and relief.type=='MATH' and relief.operation=='MULTIPLY'
    assert albedo.inputs[0].links[0].from_node.type=='SEPARATE_COLOR'
    assert relief.inputs[0].links[0].from_node.name=='Map Range.029'
    assert any(abs(albedo.inputs[3].default_value-v)<1e-5 for v in (.84,.97))
    assert any(abs(albedo.inputs[4].default_value-v)<1e-5 for v in (1.16,1.03))
    assert any(abs(relief.inputs[1].default_value-v)<1e-5 for v in (.45,.06))
    albedo.inputs[3].default_value=.97;albedo.inputs[4].default_value=1.03
    relief.inputs[1].default_value=.06
    return {'aggregate_albedo_range':[.97,1.03],'aggregate_relief_multiplier':.06,'scope':'Three socket values only; crack, joint, wet response and route wear unchanged.'}
