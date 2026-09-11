"""W14: remove duplicate receiving floor under the measured Electrical seam."""
current='Architecture'
floor=bpy.data.objects['Floor'];cut=box('Receiving seam ownership cutter',(0,-.16,-.15),(3,.3202,.62),'wall',bevel=0)
mod=floor.modifiers.new('Electrical owned receiving seam relief','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut
bpy.context.view_layer.objects.active=floor;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
SC['interface_json']=(ROOT/'interface.json').read_text()
SC['receiving_floor_ownership']='Electrical measured seam owns local X[-1.5,1.5],Y[-.32,0], topZ0. Waste clear room floor beginsY0.'
