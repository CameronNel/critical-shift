import bpy
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath="engine/reactor_room_R1.glb")
o=[x for x in bpy.data.objects if x.type=='MESH']
t=sum(len(x.data.polygons) for x in o)
import bmesh
tri=sum(sum(len(p.vertices)-2 for p in x.data.polygons) for x in o)
print("REIMPORT objects",len(bpy.data.objects),"meshes",len(o),"tris",tri,"mats",len(bpy.data.materials),"anims",len(bpy.data.actions))
