"""Align concrete wear with the three real doorway lanes and circulation ring.

Own only appended nodes and selected linked-input edits in the concrete material.
Paint, water films, aggregate relief and geometry remain under their existing
owners. Retain original socket identities so applying twice rebuilds exactly.
"""
import bpy
import json
from r2lib import WALLS

PREFIX = 'RH travel wear '
BASELINE = 'rh_travel_wear_baseline'


def apply(materials):
    material = materials['RH floor wet concrete']
    tree = material.node_tree
    rough = [n for n in tree.nodes if n.type == 'MIX' and n.data_type == 'FLOAT'
             and not n.inputs[3].is_linked and abs(n.inputs[3].default_value-.62) < 1e-6]
    colour = [n for n in tree.nodes if n.type == 'MIX' and n.data_type == 'RGBA'
              and tuple(round(x, 3) for x in n.inputs[7].default_value[:3]) == (.035, .033, .03)]
    assert len(rough) == len(colour) == 1, 'Unexpected owned concrete graph'
    polish = rough[0].inputs[0].links[0].from_node
    scuff = colour[0].inputs[0].links[0].from_node.inputs[0].links[0].from_node
    assert polish.operation == scuff.operation == 'MULTIPLY'
    assert any(abs(polish.inputs[1].default_value-v) < 1e-6 for v in (.22, .65))
    assert any(abs(scuff.inputs[1].default_value-v) < 1e-6 for v in (.18, .50))

    def socket_id(socket):
        return [socket.node.name, list(socket.node.outputs).index(socket)]
    if BASELINE not in material:
        original = polish.inputs[0].links[0].from_socket
        material[BASELINE] = json.dumps({
            'traffic': socket_id(original),
            'traffic_targets': [[link.to_node.name, list(link.to_node.inputs).index(link.to_socket)]
                                for link in original.links],
            'scuff': socket_id(scuff.inputs[0].links[0].from_socket)}, sort_keys=True)
    baseline = json.loads(material[BASELINE])
    for node in list(tree.nodes):
        if node.name.startswith(PREFIX):
            tree.nodes.remove(node)
    original_scuff = tree.nodes[baseline['scuff'][0]].outputs[baseline['scuff'][1]]
    assert baseline['traffic'][0] in tree.nodes
    serial = 0
    def node(kind, label):
        nonlocal serial
        result = tree.nodes.new(kind)
        result.name = PREFIX + str(serial) + ' ' + label
        result.label = label
        serial += 1
        return result
    def value(socket, item):
        if isinstance(item, bpy.types.NodeSocket):
            tree.links.new(item, socket)
        else:
            socket.default_value = item
    def math(op, a, b=0):
        result = node('ShaderNodeMath', op)
        result.operation = op
        value(result.inputs[0], a); value(result.inputs[1], b)
        return result.outputs[0]
    def vector(op, a, b):
        result = node('ShaderNodeVectorMath', op)
        result.operation = op
        value(result.inputs[0], a); value(result.inputs[1], b)
        return result.outputs[1] if op in {'DOT_PRODUCT', 'LENGTH'} else result.outputs[0]
    def range_(item, a, b, c=0, d=1):
        result = node('ShaderNodeMapRange', 'soft travel limit')
        result.interpolation_type = 'SMOOTHSTEP'
        for socket, item_ in zip(result.inputs, (item, a, b, c, d)):
            value(socket, item_)
        return result.outputs[0]

    position = node('ShaderNodeNewGeometry', 'world position in metres').outputs['Position']
    traffic = directional = None
    lanes = []
    for wall_index, along in ((6, 6.0), (4, 6.0), (1, 3.395)):
        wall = WALLS[wall_index]
        origin = wall.pt(along, 0)
        local = vector('SUBTRACT', position, (origin.x, origin.y, 0))
        forward = vector('DOT_PRODUCT', local, (wall.n.x, wall.n.y, 0))
        cross = vector('DOT_PRODUCT', local, (-wall.n.y, wall.n.x, 0))
        end = origin.length - 5.25
        mask = math('MULTIPLY', range_(math('ABSOLUTE', cross), .95, .50),
                    math('MULTIPLY', range_(forward, 1.1, 1.6), range_(forward, end+.1, end-.4)))
        traffic = mask if traffic is None else math('MAXIMUM', traffic, mask)
        coordinates = node('ShaderNodeCombineXYZ', 'broken wear along travel')
        tree.links.new(math('MULTIPLY', forward, .65), coordinates.inputs[0])
        tree.links.new(math('MULTIPLY', cross, 4.2), coordinates.inputs[1])
        noise = node('ShaderNodeTexNoise', 'irregular longitudinal scuffs')
        noise.inputs['Scale'].default_value = 1.7
        noise.inputs['Detail'].default_value = 3
        noise.inputs['Roughness'].default_value = .65
        tree.links.new(coordinates.outputs[0], noise.inputs['Vector'])
        wear = math('MULTIPLY', mask, range_(noise.outputs['Fac'], .49, .61, 0, .90))
        directional = wear if directional is None else math('MAXIMUM', directional, wear)
        lanes.append({'wall': wall_index, 'origin': list(origin), 'normal': list(wall.n), 'end_m': end})
    radius = vector('LENGTH', vector('MULTIPLY', position, (1, 1, 0)), (0, 0, 0))
    ring = range_(math('ABSOLUTE', math('SUBTRACT', radius, 5.7)), 1.0, .45)
    traffic = math('MAXIMUM', traffic, ring)
    for name, index in baseline['traffic_targets']:
        tree.links.new(traffic, tree.nodes[name].inputs[index])
    tree.links.new(math('MAXIMUM', math('MULTIPLY', original_scuff, .4), directional), scuff.inputs[0])
    polish.inputs[1].default_value = .65
    scuff.inputs[1].default_value = .50
    return {'material': material.name, 'owned_nodes': serial, 'lanes': lanes,
            'circulation_radius_m': 5.7,
            'scope': 'Concrete traffic mask, scuff field and polish factor only; original paint, puddle suppression, aggregate relief and geometry preserved'}
