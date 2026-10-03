"""R15: camera-visible worker tools on measured empty, supported worktop areas."""

# Ray-tested sightlines from the unchanged gameplay cameras identify these clear
# worktop shoulders. Move the complete authored groups, including their contact
# declarations; don't enlarge props or shift cameras to manufacture readability.
placements=[(('Assembly_work_glove','ART_Assembly_work_glove'),(-.125,-1.13,0)),
            (('RF1 | Inspection folded cotton wipe','RF1 | Inspection caliper',
              'RF1 | Caliper engraved scale'),(-.67,-.99,0))]
for prefixes,offset in placements:
 group=[o for o in s.objects if o.name.startswith(prefixes)]
 names={o.name for o in group};shift=Matrix.Translation(Vector(offset))
 rigid_group(group,shift)
 for record in supports:
  if record['group'] in names:record['anchor']=list(shift@Vector(record['anchor']))

# Seat the original sensor-frame fastener group at the new frame's actual front
# plane. The old source had a 1 mm visual gap at the screw backs.
fasteners=bpy.data.objects.get('ART_Sorter_sensor_head_fasteners')
if fasteners:
 bpy.context.view_layer.update();world=fasteners.matrix_world.copy()
 world.translation.y+=.001;fasteners.matrix_world=world

bpy.context.view_layer.update()
