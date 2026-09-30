import bpy,numpy as np,sys
S=sys.argv[sys.argv.index("--")+1]
names=["back_wall_toward_window","window_toward_back_wall","back_east_corner_toward_door_side","back_west_corner_toward_east_side"]
im=[bpy.data.images.load(f"{S}/g5_{n}.png") for n in names]
w,h=im[0].size
a=[np.array(i.pixels[:]).reshape(h,w,4) for i in im]
# pixel arrays are bottom-up; row 0 = bottom. Top row of grid = first two images.
top=np.concatenate([a[0],a[1]],axis=1); bot=np.concatenate([a[2],a[3]],axis=1)
g=np.concatenate([bot,top],axis=0)
out=bpy.data.images.new("grid",w*2,h*2,alpha=False); out.pixels=g.flatten().tolist(); out.filepath_raw=f"{S}/control_room_4way_v2.png"; out.file_format='PNG'; out.save()
print("saved grid",w*2,h*2)
