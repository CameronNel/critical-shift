"""Offline Blender art-state controls; Unity gameplay remains a separate layer."""
import bpy,json,math
NAMES={0:'Sealed',1:'Shallow',2:'Extended',3:'Deep',4:'Collapsed'}
def read(scene):return json.loads(scene['csm_states_json'])
def refresh(scene):
    states=read(scene)
    for o in scene.objects:
        if 'csm_meta' not in o:continue
        m=json.loads(o['csm_meta']);show=True;sec=m.get('sector')
        if m.get('collision_only'):show=False
        elif sec:
            st=states[sec]
            if 'gate_index' in m:show=st['state']==int(m['gate_index'])
            elif m.get('collapse_only'):show=st['state']==4 and (m.get('damage_only') or int(m.get('rubble_index',-1)) not in st['cleared_rubble'])
            elif m.get('ore_chunk') and st['state']==4:show=False
            elif 'min_stage' in m:show=st['unlocked_stage']>=int(m['min_stage'])
        o.hide_render=not show;o.hide_set(not show)
    for sec,st in states.items():
        root=scene.objects.get('CSM_CTRL_SECTOR_'+sec)
        if root:
            for k in ['state','unlocked_stage','remaining_rubble']:root['csm_'+k]=st[k]
    bpy.context.view_layer.update()
def reset(scene,showcase=False):
    stages={'A':1,'B':2,'C':4} if showcase else dict.fromkeys('ABC',0)
    scene['csm_states_json']=json.dumps({k:{'state':v,'unlocked_stage':3 if v==4 else v,'remaining_rubble':22 if v==4 else 0,'cleared_rubble':[]} for k,v in stages.items()});refresh(scene)
def excavate(scene,sector,index):
    if sector not in 'ABC' or len(sector)!=1 or not math.isfinite(index) or index<0:raise ValueError('Use sector A/B/C and a nonnegative fictional game index.')
    states=read(scene);st=states[sector]
    if st['remaining_rubble']:raise ValueError('Clear this collapse before another excavation event.')
    target=0 if index==0 else 1 if index<=2 else 2 if index<=4 else 3 if index<=6 else 4
    if target==4:st.update(state=4,unlocked_stage=3,remaining_rubble=22,cleared_rubble=[])
    elif target:
        stage=max(target,st['unlocked_stage']);st.update(state=stage,unlocked_stage=stage,remaining_rubble=0,cleared_rubble=[])
    scene['csm_states_json']=json.dumps(states);refresh(scene);return st

def clear(scene,sector):
    states=read(scene);st=states[sector]
    if st['remaining_rubble']:
        removed=set(st['cleared_rubble']);removed.add(next(i for i in range(22) if i not in removed));st['cleared_rubble']=sorted(removed);st['remaining_rubble']=22-len(removed)
        if not st['remaining_rubble']:st['state']=st['unlocked_stage']
        scene['csm_states_json']=json.dumps(states);refresh(scene)
    return st

def gate(scene,value):
    fraction=max(0,min(float(value),1))
    for key in ['CSM_Blast_leaf_L','CSM_Blast_leaf_R']:
        o=scene.objects[key];o.location.x=o['csm_closed_x']+o['csm_travel']*fraction
    scene.objects['CSM_CTRL_BLAST_GATE']['csm_open_fraction']=fraction;bpy.context.view_layer.update()

def register():
    for name in ['Q50_OT_cut','Q50_OT_clear','Q50_OT_reset','Q50_OT_showcase','Q50_OT_gate','Q50_PT_controls']:
        old=getattr(bpy.types,name,None)
        if old:bpy.utils.unregister_class(old)
    class Q50_OT_cut(bpy.types.Operator):
        bl_idname='q50.cut';bl_label='Apply game excavation index';bl_options={'REGISTER','UNDO'}
        def execute(self,context):
            try:excavate(context.scene,context.scene.q50_sector,context.scene.q50_index)
            except ValueError as e:self.report({'WARNING'},str(e));return {'CANCELLED'}
            return {'FINISHED'}
    class Q50_OT_clear(bpy.types.Operator):
        bl_idname='q50.clear';bl_label='Remove next rubble fragment';bl_options={'REGISTER','UNDO'}
        def execute(self,context):clear(context.scene,context.scene.q50_sector);return {'FINISHED'}
    class Q50_OT_reset(bpy.types.Operator):
        bl_idname='q50.reset';bl_label='Reset to sealed';bl_options={'REGISTER','UNDO'}
        def execute(self,context):reset(context.scene);return {'FINISHED'}
    class Q50_OT_showcase(bpy.types.Operator):
        bl_idname='q50.showcase';bl_label='Showcase stages';bl_options={'REGISTER','UNDO'}
        def execute(self,context):reset(context.scene,True);return {'FINISHED'}
    class Q50_OT_gate(bpy.types.Operator):
        bl_idname='q50.gate';bl_label='Open / close blast gate';bl_options={'REGISTER','UNDO'}
        def execute(self,context):gate(context.scene,1-context.scene.objects['CSM_CTRL_BLAST_GATE'].get('csm_open_fraction',1));return {'FINISHED'}
    class Q50_PT_controls(bpy.types.Panel):
        bl_idname='Q50_PT_controls';bl_label='Gullet / quality build';bl_space_type='VIEW_3D';bl_region_type='UI';bl_category='Gullet'
        @classmethod
        def poll(cls,context):return bool(context.scene.get('q50_revision'))
        def draw(self,context):
            layout=self.layout;sc=context.scene;layout.prop(sc,'q50_sector');layout.prop(sc,'q50_index');layout.operator('q50.cut');layout.operator('q50.clear')
            st=read(sc)[sc.q50_sector];layout.label(text=NAMES[st['state']]+f" / rubble left: {st['remaining_rubble']}");layout.operator('q50.gate');layout.operator('q50.reset');layout.operator('q50.showcase');layout.label(text='Art-state controls, not Unity gameplay.')
    for cls in [Q50_OT_cut,Q50_OT_clear,Q50_OT_reset,Q50_OT_showcase,Q50_OT_gate,Q50_PT_controls]:bpy.utils.register_class(cls)
    bpy.types.Scene.q50_sector=bpy.props.EnumProperty(name='Sector',items=[(a,a,'') for a in 'ABC'],default='A')
    bpy.types.Scene.q50_index=bpy.props.IntProperty(name='Fictional game index',default=3,min=1,max=12)
    bpy.app.driver_namespace['CSM_API']={'excavate':lambda s,i:excavate(bpy.context.scene,s,i),'clear_rubble':lambda s:clear(bpy.context.scene,s),'reset':lambda:reset(bpy.context.scene),'showcase':lambda:reset(bpy.context.scene,True),'gate':lambda f:gate(bpy.context.scene,f)}
if __name__=='__main__':register()
