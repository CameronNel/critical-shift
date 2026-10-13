from pathlib import Path
helper=Path('/tmp/cs-mine-probe-uniform-preflight-final12.py').read_text()
prefix=helper.split('records=[];raws=[]')[0].replace("Path('/tmp/cs-mine-probe-uniform-preflight-final12')", "Path('/tmp/cs-mine-probe-visibility-control-final12')")
exec(compile(prefix,'known-world-preflight-construction','exec'))
flags=['visible_camera','visible_shadow','visible_diffuse','visible_glossy','visible_transmission','visible_volume_scatter']
cases=[('all-visible',{key:True for key in flags})]
cases += [(key+'-off',{f:f!=key for f in flags}) for key in flags]
cases += [('all-hidden',{key:False for key in flags})]
cases += [('only-'+key,{f:f==key for f in flags}) for key in ['visible_diffuse','visible_shadow','visible_camera']]
records=[]
for mode,visibility in cases:
 for key,value in visibility.items():setattr(sphere,key,value)
 image=bpy.data.images.new('Visibility_'+mode,64,32,alpha=True,float_buffer=True);image.colorspace_settings.name='Non-Color';node=nt.nodes.new('ShaderNodeTexImage');node.image=image;nt.nodes.active=node
 for n in nt.nodes:n.select=n==node
 bpy.ops.object.bake(type='DIFFUSE');raw=np.array(image.pixels[:],dtype=np.float32).reshape((32,64,4));assert np.isfinite(raw).all()
 scene.render.image_settings.file_format='OPEN_EXR';scene.render.image_settings.color_mode='RGBA';scene.render.image_settings.color_depth='32';scene.render.image_settings.exr_codec='ZIP';path=out/(mode+'.exr');image.save_render(str(path),scene=scene)
 mean=raw[coverage,:3].mean(0);record={'mode':mode,'visibility':visibility,'meanRGB':mean.tolist(),'expectedRGB':[.25,.5,.75],'validTexels':int(coverage.sum()),'meanErrorRGB':(mean-np.array([.25,.5,.75])).tolist(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()};records.append(record);print('CS_VISIBILITY_CONTROL',record,flush=True);nt.nodes.remove(node);bpy.data.images.remove(image)
(out/'review.json').write_text(json.dumps({'status':'VisibilityMechanismDiagnosticOnly','helperSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'constructionHelperSha256':hashlib.sha256(Path('/tmp/cs-mine-probe-uniform-preflight-final12.py').read_bytes()).hexdigest(),'coverageSha256':hashlib.sha256(coveragePath.read_bytes()).hexdigest(),'cases':records,'limits':['Known constantWorld only','No virtualprobe sourcefield acceptance','No source file saved']},indent=2)+'\n')
