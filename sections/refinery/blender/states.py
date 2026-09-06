"""Ten reviewable static state presets; gameplay and networking belong in Unity."""
import bpy, math
import geometry as g
from materials import M

PRESETS={
 'idle':('CAM_ENTRY','No batch movement; equipment ready'),
 'normal_production':('CAM_MINE_TO_CRUSHER','Docked cart tipped into hopper; belt carries consolidated batch'),
 'crusher_jam':('CAM_PINCH','Wedge trapped at rollers; service access flagged'),
 'wet_ore_overload':('CAM_MINE_TO_CRUSHER','Wet intake batch and localized spill'),
 'sorter_gate_fault':('CAM_PROCESS','Diverter visibly stuck across accepted route'),
 'processor_warning':('CAM_PROCESS','Pressure warning; local leak/dump'),
 'dryer_filter_fault':('CAM_PROCESS','Removed blocked filter and amber fault'),
 'assembly_jam':('CAM_MATERIAL','Crosshead halted low with misaligned casing'),
 'inspection_uncertainty':('CAM_ASSEMBLY','Estimated reading and unresolved confidence'),
 'emergency_stopped':('CAM_ENTRY','Red local lamps; machine motion stopped'),
}

def prop(state,fn,*args,**kwargs):
    o=fn(*args,**kwargs);o['preview_state']=state;o.hide_render=True;return o

def build():
    with g.use('REFINERY_STATE_PREVIEWS'):
        prop('crusher_jam',g.box,'STATE_Crusher_jam_wedge',(-5.07,4.43,2.19),(.53,.24,.30),'ore',.035)
        prop('crusher_jam',g.box,'STATE_Crusher_mouth_jam',(-4.95,4.07,2.77),(.38,.43,.44),'ore',.055)
        prop('wet_ore_overload',g.box,'STATE_Wet_ore_pile',(-5.10,-1.58,.57),(.74,.52,.17),'ore',.08)
        prop('wet_ore_overload',g.mesh,'STATE_Wet_spill',[(-4.18,-1.8,.007),(-3.90,-2.05,.007),(-3.60,-1.6,.007),(-3.82,-1.22,.007),(-4.17,-1.35,.007)],[(0,1,2,3,4)],'dirtyfilter')
        prop('processor_warning',g.mesh,'STATE_Seal_leak',[(.20,3.45,.006),(.80,3.43,.006),(1.0,3.70,.006),(.22,3.72,.006)],[(0,1,2,3)],'dirtyfilter')
        prop('assembly_jam',g.rod,'STATE_Misaligned_fuel',(5.35,1.60,1.12),(5.48,1.5,1.53),.085,'fuel',16)
        for x,y,z in [(-4.42,3.77,2.14),(.55,3.88,2.3),(3.91,3.72,1.91),(5.37,1.5,2.46)]:
            prop('emergency_stopped',g.box,'STATE_Emergency_lamp',(x,y,z),(.13,.06,.10),'fault',.006)
    for name in ['CART_SIDE_TIP_PIVOT','Sorter_diverter_PIVOT','Assembly_ram_PIVOT']:
        o=bpy.data.objects.get(name)
        if o:o['rest_location']=list(o.location);o['rest_rotation']=list(o.rotation_euler)
    # Named timeline cues expose the presets without embedding scripts that auto-run.
    scene=bpy.context.scene
    for i,(name,(cam,desc)) in enumerate(PRESETS.items()):
        scene.timeline_markers.new(name,frame=1+i*20)
    scene['state_presets']='; '.join(PRESETS)
    apply('idle')

def apply(name):
    if name not in PRESETS:raise ValueError(name)
    for o in bpy.context.scene.objects:
        if o.get('preview_state'):o.hide_render=o['preview_state']!=name;o.hide_viewport=o.hide_render;o['intentional_hidden']=True
        if 'rest_location' in o:o.location=o['rest_location'];o.rotation_euler=o['rest_rotation']
    if name=='normal_production':bpy.data.objects['CART_SIDE_TIP_PIVOT'].rotation_euler.x=math.radians(-50)
    if name=='sorter_gate_fault':bpy.data.objects['Sorter_diverter_PIVOT'].rotation_euler.z=math.radians(-48)
    if name=='assembly_jam':bpy.data.objects['Assembly_ram_PIVOT'].location.z-=.23
    filt=bpy.data.objects.get('Dryer_filter_cartridge')
    if filt:
        if 'filter_rest' not in filt:filt['filter_rest']=list(filt.location)
        filt.location=filt['filter_rest']
        if name=='dryer_filter_fault':filt.location.y-=.30
    for lamp in ['Crusher_state_light','Processor_state_light','Dryer_fault_light']:
        o=bpy.data.objects.get(lamp)
        if o:
            mat='fault' if name=='emergency_stopped' else 'amber' if name in ['crusher_jam','processor_warning','dryer_filter_fault','wet_ore_overload'] else 'ready'
            o.data.materials.clear();o.data.materials.append(M[mat])
    bpy.context.scene['preview_state']=name;bpy.context.view_layer.update()

def recover_materials():
    for mat in bpy.data.materials:
        if mat.name.startswith('REF_'):M[mat.name[4:]]=mat
