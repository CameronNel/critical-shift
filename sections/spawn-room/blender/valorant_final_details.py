"""Seventh comparison: tactile soft goods, dark bench frames and readable floor plan."""
import bpy
import grounded_kit as k
import worn_surfaces as wear
import revise_spawn as rev

def run():
    assert not bpy.context.scene.get('valorant_final_detail_pass')
    k.M={m.name:m for m in bpy.data.materials};k.STAGE=3
    for root in bpy.data.objects:
        if root.type=='EMPTY' and 'bench' in root.name:
            for ob in root.children_recursive:
                if ob.type in {'CURVE','MESH'} and '_laminate_slat' not in ob.name:
                    for slot in ob.material_slots:
                        if slot.material and slot.material.name in ['steel','pale','paint','pressure_metal','V_utility_pale','V_utility_paint']:slot.material=k.M['V_graphite']
    for name in ['rug_field','rug_cream','rug_border','bench_worn_timber']:
        m=k.M[name];n=m.node_tree.nodes;l=m.node_tree.links;p=n['Principled BSDF'];coord=n.new('ShaderNodeTexCoord')
        q=wear.noise(n,l,coord.outputs['Object'],19 if name.startswith('rug') else 8,3)
        fade=wear.ramp(n,l,q,[(.58,.60,.61),(1.15,1.08,1.0)],(.25,.73))
        mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=.56
        l.new(p.inputs['Base Color'].links[0].from_socket,mix.inputs[1]);l.new(fade,mix.inputs[2]);l.new(mix.outputs[0],p.inputs['Base Color'])
    # Printed floor plan is real vector linework based on the three-room arrangement.
    rev.remove_prefix('V_BRIEF_plan_line')
    root=bpy.data.objects['V_BRIEF_map'];old=bpy.data.objects['V_BRIEF_map_type'];old.data.body='FACILITY / 08';old.data.size=.025;old.location.z=.125
    b=k.start()
    for pts in [[(-.035,.075),(.035,.075),(.035,-.12),(-.035,-.12),(-.035,.075)],[(-.18,.025),(-.060,.025),(-.060,-.080),(-.18,-.080),(-.18,.025)],[(.060,.056),(.18,.056),(.18,-.103),(.060,-.103),(.060,.056)]]:
        k.tube('V_BRIEF_plan_outline',[(x,-.004,z) for x,z in pts],.0018,'dry_marker')
    for x in [-.052,.052]:k.tube('V_BRIEF_plan_door',[(x-.017,-.004,-.034),(x+.017,-.004,-.034)],.0016,'dry_marker')
    k.tube('V_BRIEF_plan_route',[(0,-.004,-.105),(0,-.004,.057)],.0015,'canvas_rust')
    for x,z,label in [(-.120,-.029,'01'),(.120,-.034,'02'),(0,.081,'03')]:k.label('V_BRIEF_plan_room',label,(x,-.004,z),.021,'dry_marker',align='CENTER')
    k.label('V_BRIEF_plan_legend','01 BRIEF  /  02 LOCKERS',(0,-.004,-.148),.014,'dry_marker',align='CENTER')
    for ob in set(bpy.data.objects)-b:ob.parent=root
    bpy.context.scene['valorant_final_detail_pass']=7
