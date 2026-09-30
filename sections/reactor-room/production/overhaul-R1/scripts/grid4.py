import bpy,numpy as np,sys
S=sys.argv[sys.argv.index("--")+1]
names=["north_toward_window","south_toward_back_wall","east_toward_door","west_toward_east_wall"]
im=[bpy.data.images.load(f"{S}/g4_{n}.png") for n in names]
w,h=im[0].size
a=[np.array(i.pixels[:]).reshape(h,w,4) for i in im]
# pixel arrays are bottom-up; row 0 = bottom. Top row of grid = first two images.
top=np.concatenate([a[0],a[1]],axis=1); bot=np.concatenate([a[2],a[3]],axis=1)
g=np.concatenate([bot,top],axis=0)
out=bpy.data.images.new("grid",w*2,h*2,alpha=False); out.pixels=g.flatten().tolist(); out.filepath_raw=f"{S}/control_room_4way.png"; out.file_format='PNG'; out.save()
print("saved grid",w*2,h*2)
