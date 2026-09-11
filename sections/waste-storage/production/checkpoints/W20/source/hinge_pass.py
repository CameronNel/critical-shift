"""W16: place hinge axes on opening faces so leaf sweeps clear wall returns."""
current='Architecture';bpy.data.objects['WS_PERSONNEL_LEAF'].location.x=6.36
for y in [1.735,3.065]:box('Personnel outer strike jamb',(6.335,y,1.15),(.08,.13,2.3),'darkpaint',bevel=.006)
bpy.data.objects['WS_MONITOR_BOOTH_LEAF'].location.x=-2.48
for z in [.25,1.15,2.03]:box('Booth fixed hinge backing',(-2.445,2.815,z),(.09,.045,.15),'metal',bevel=.003)
SC['interface_json']=(ROOT/'interface.json').read_text()
