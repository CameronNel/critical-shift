"""Export only the measured normalized Source spotlight family; reject other closures."""
import math


def context_spot_lights(members, matrix):
    records = []
    for o in members:
        if o.type!='LIGHT' or o.data.type!='SPOT' or o.hide_render: continue
        d=o.data
        # The measured power convention assumes the actual neutral emission closure.
        # Refuse unsupported authored modifiers instead of silently approximating them.
        if not d.normalize or not d.use_soft_falloff or d.exposure!=0 or d.use_temperature or any(
            getattr(d,k)!=1 for k in ('diffuse_factor','specular_factor','volume_factor')):
            raise ValueError('Unsupported context spotlight modifiers: '+o.name)
        if d.use_nodes:
            outputs=[n for n in d.node_tree.nodes if n.type=='OUTPUT_LIGHT' and n.is_active_output]
            links=list(outputs[0].inputs['Surface'].links) if len(outputs)==1 else []
            if len(links)!=1 or links[0].from_node.type!='EMISSION':
                raise ValueError('Unsupported context spotlight closure: '+o.name)
            e=links[0].from_node
            if e.inputs['Color'].is_linked or e.inputs['Strength'].is_linked or tuple(e.inputs['Color'].default_value)!=(1,1,1,1) or e.inputs['Strength'].default_value!=1:
                raise ValueError('Unsupported context spotlight emission: '+o.name)
        records.append(dict(name=o.name,type='SPOT',
            position=list(matrix(o).translation),rotation=list(matrix(o).to_quaternion()),
            color=list(d.color),power=float(d.energy),radius=float(d.shadow_soft_size),
            spotSize=float(d.spot_size),spotBlend=float(d.spot_blend),normalized=bool(d.normalize),softFalloff=bool(d.use_soft_falloff)))
    for r in records:
        scalars = [*r["position"], *r["rotation"], *r["color"], r["power"], r["radius"], r["spotSize"], r["spotBlend"]]
        if not all(math.isfinite(v) for v in scalars) or r["power"]<0 or r["radius"]<=0 or not 0<r["spotSize"]<math.pi or not 0<r["spotBlend"]<=1:
            raise ValueError("Unsupported context spotlight parameters: "+r["name"])
    if len({r["name"] for r in records}) != len(records):
        raise ValueError("Duplicate authored context spotlight names")
    return records
