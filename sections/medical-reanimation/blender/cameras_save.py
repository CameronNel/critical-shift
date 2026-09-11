"""Named player-height views and explicit host hook anchors; saves new owned artifact."""
current='Validation'
hooks=[('OCRU_LOAD',(-1.7,4.63,1.02),'OCRU_BERTH'),('OCRU_SUIT_PORT',(-1.38,6.23,1.36),'OCRU_SUIT_SERVICE'),('OCRU_CARTRIDGE',(-1.31,3,1.38),'OCRU_CARTRIDGE_RECEIVER'),('OCRU_RESTART',(-.41,8.1,1.03),'RESTART_CONSOLE'),('OCRU_POWER',(-2.15,8.40,.77),'RESERVE_POWER'),('OCRU_MAINTENANCE',(-1.50,6.40,1.30),'OCRU'),('DECON_WAND',(2.03,10.94,1.2),'DECON_WASH'),('RECOVERY_EXIT',(2.1,4.7,.7),'RECOVERY_BERTH'),('OCRU_COMPLIANCE_LOCK',(-.41,8.4,1.4),'RESTART_CONSOLE'),('AUDIO_MEDICAL',(0,4.5,1.6),None)]
for name,loc,target in hooks:
    o=assembly('HOOK_'+name,loc);o['host_hook']=name;o['target_id']=target or 'medical-reanimation';o['runtime_implemented']=False
o=assembly('IF_main_entry',(0,0,0));o['connection_id']='main_entry';o['outward_normal']=json.dumps([0,-1,0])
current='Cameras'
cams=[('CAM_ENTRY',(0,.48,1.68),(.1,5.4,1.4),22),('CAM_HERO',(1.35,4.55,1.68),(-2.05,4.7,1.3),24),('CAM_REVERSE',(.2,7.7,1.68),(.05,1.2,1.35),22),('CAM_ROUTE',(.1,1.55,1.68),(.2,6.5,1.2),24),('CAM_CONSOLE',(.15,6.85,1.68),(-.4,8.45,1.25),28),('CAM_DECON',(1.55,7.55,1.68),(2.33,10.2,1.15),28),('CAM_RECOVERY',(1.35,3.25,1.68),(3.2,4.7,.8),28),('CAM_PINCH',(-.15,3.85,1.68),(-2.15,4.75,1.1),28),('CAM_MATERIALS',(-.85,7.35,1.68),(-2.15,8.55,.85),35),('CAM_MAINT',(2.05,7.35,1.68),(3.05,8.7,1.35),28),('W01_ENTRY_OUTSIDE',(0,-1.2,1.68),(0,4.5,1.3),22),('W02_CART',(-1.15,1.40,1.68),(-3.1,1.33,.75),25),('W03_SUPPLIES',(1.6,1.3,1.68),(3.6,1.6,.9),26),('W04_REAR_SERVICE',(-.3,6.9,1.68),(1.65,8.6,1.15),23)]
for name,loc,target,lens in cams:
    d=bpy.data.cameras.new(name);d.lens=lens;d.clip_start=.04;d.clip_end=100;o=bpy.data.objects.new(name,d);COL[current].objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
SC.camera=bpy.data.objects['CAM_ENTRY'];SC.render.engine='CYCLES';SC.cycles.samples=32;SC.cycles.use_denoising=True;SC.cycles.seed=17
SC.render.resolution_x=1440;SC.render.resolution_y=900;SC.render.resolution_percentage=100
SC.world=bpy.data.worlds.new('Medical neutral ambient');SC.world.use_nodes=True;SC.world.node_tree.nodes['Background'].inputs[0].default_value=(.18,.17,.15,1);SC.world.node_tree.nodes['Background'].inputs[1].default_value=.20
SC.view_settings.view_transform='AgX';SC.view_settings.look='AgX - Medium High Contrast';SC.view_settings.exposure=0
SC['interface_json']=(ROOT/'interface.json').read_text();SC['camera_manifest']=json.dumps([{'name':o.name,'location':list(o.location),'rotation':list(o.rotation_euler),'lens':o.data.lens} for o in SC.objects if o.type=='CAMERA'])
authoring_names=['build_scene.py','medical_scene.py','ocru_assembly.py','stations.py','services_lighting.py','refinement.py','construction_corrections.py','service_completion.py','material_light_finish.py','cameras_save.py']
SC['authoring_sources']=json.dumps({n:hashlib.sha256((Path(__file__).parent/n).read_bytes()).hexdigest() for n in authoring_names},sort_keys=True)
bpy.context.view_layer.update()
out=Path(args.output) if args.output else ROOT/'blender/medical_integration.blend';out.parent.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out))
dest=ROOT/'production/checkpoints'/args.revision;dest.mkdir(parents=True,exist_ok=True)
(dest/'build_manifest.json').write_text(json.dumps({'revision':args.revision,'objects':len(SC.objects),'blend':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'sources':json.loads(SC['authoring_sources'])},indent=2))
print('BUILD_COMPLETE',args.revision,len(SC.objects),str(out),flush=True)
