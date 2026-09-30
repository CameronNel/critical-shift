import bpy,numpy as np,sys
S=sys.argv[sys.argv.index("--")+1]
files=["h3_a_window_to_back_telemetry","h3_b_window_to_back_broadcast","h2_c_back_to_window","h3_e_rack_and_east_wall"]
im=[bpy.data.images.load(f"{S}/{n}.png") for n in files]
w,h=im[0].size
a=[np.array(i.pixels[:]).reshape(h,w,4) for i in im]
top=np.concatenate([a[0],a[1]],axis=1); bot=np.concatenate([a[2],a[3]],axis=1)
g=np.concatenate([bot,top],axis=0)
out=bpy.data.images.new("grid",w*2,h*2,alpha=False); out.pixels=g.flatten().tolist(); out.filepath_raw=f"{S}/control_room_1990_4way.png"; out.file_format='PNG'; out.save(); print("saved",w*2,h*2)
