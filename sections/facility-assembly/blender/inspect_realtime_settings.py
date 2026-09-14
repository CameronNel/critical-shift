import bpy,json
s=bpy.context.scene
p=bpy.data.lightprobes.new('inspect','VOLUME')
for label,obj in [('eevee',s.eevee),('probe',p),('light',bpy.data.lights.new('inspect','AREA'))]:
 print(label,[(x.identifier,x.type,getattr(obj,x.identifier,None)) for x in obj.bl_rna.properties if any(k in x.identifier for k in ['bake','resolution','sample','shadow','surfel','grid','capture','bias','jitter'])],flush=True)
print('BAKE_OP',bpy.ops.object.lightprobe_cache_bake.get_rna_type().properties.keys())
