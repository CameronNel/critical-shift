"""Separate worn route chips and secondary equipment within the gloomy palette.

No geometry, camera or source pose changes. Existing wear coverage, grime and
outages remain. Higher residual paint reflectance and modest casing differences
recover essential contours without adding illumination or restoring clean paint.
"""
for name,colour in [
 ('RF1_green',(.068,.103,.085)),
 ('RF1_thermal_jacket_finish',(.072,.108,.091)),
 ('RF1_cast_hydraulic_powdercoat',(.138,.094,.066)),
 ('RF1_muted_service_trunk',(.094,.110,.100)),
 ('RF1_dark',(.049,.059,.054)),
]:
 aged_colour(name,colour)

# Preserve every missing/chipped paint fragment; only surviving pigment gains
# contrast. Equipment legends keep their existing materials and coverage.
for material in paint_materials.values():
 dims=[n for n in material.node_tree.nodes if n.type=='MIX_RGB'
       and n.blend_type=='MULTIPLY'
       and all(abs(n.inputs[2].default_value[i]-v)<1e-6
               for i,v in enumerate((.62,.65,.58)))]
 assert len(dims)==1,(material.name,len(dims))
 dims[0].inputs[2].default_value=(.87,.89,.79,1)

# Distinguish abandoned PPE from the similarly dark timber. Isolate this finish
# from cart cloth, bristles and other original leather users.
glove_material=M['leather'].copy();glove_material.name='RF24_abandoned_glove_leather'
aged_colour(glove_material.name,(.210,.197,.144))
gloves=[o for o in s.objects if o.name.startswith(('RF1 | Work glove palm',
        'RF1 | Glove gauntlet cuff','RF1 | Glove finger','RF1 | Glove thumb'))]
assert len(gloves)==14,len(gloves)
for o in gloves:
 o.data=o.data.copy()
 for i in range(len(o.data.materials)):o.data.materials[i]=glove_material

# Small local power increases in already working fixtures. The dark ceiling,
# six failed pairs, weak lens emission and fixture/source poses stay fixed.
for key,energy in [('Ceiling pendant 4',50),('Wall service lamp 3',20),
                   ('Inspection sample practical',26),('Work nook lamp',20)]:
 light=bpy.data.objects['RF1 LIGHT | '+key]
 assert light.data.energy>0 and light['electrical_state']=='weak'
 light.data.energy=energy
assert len([o for o in s.objects if o.type=='LIGHT' and o.data.energy==0])==6
bpy.context.view_layer.update()
