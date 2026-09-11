"""W09: measured access corrections; preserve external opening centers/sizes."""
p=bpy.data.objects['WS_PERSONNEL_LEAF'];p.location.y=3.065;p.scale.x=1.25/1.15
p=bpy.data.objects['WS_MONITOR_BOOTH_LEAF'];p.location.y=2.815;p.scale.x=1.14/1.04
bpy.data.objects['Inventory chair'].location.y=1.30
bpy.data.objects['HJ01_HANDLING_JIB'].location.y=9.95
bpy.data.objects['HJ01_HANDLING_JIB'].rotation_euler.z=math.pi/4
bpy.data.objects['HJ01_HANDLING_JIB']['parked_boom']='45deg Z; hook in non-circulating inter-cell gap'
bpy.data.objects['DR02'].location.y=7.85
