from pathlib import Path
import OpenEXR,numpy as np,sys
for p in map(Path,sys.argv[1:]):
 f=OpenEXR.File(str(p));c={k:v.pixels for part in f.parts for k,v in part.channels.items()}
 for name in ['BaseColor','Roughness','Metallic','ShadingNormal','DiagnosticOne']:
  a=c['ViewLayer.'+name];assert a.shape==(360,640,4) and np.isfinite(a).all(),(p,name)
 assert c['ViewLayer.DiagnosticOne'][:,:,:3].max()>.99,('Empty AOV: Blender5.2 needs aov_name',p)
 assert c['ViewLayer.BaseColor'][:,:,:3].max()>.01,('Empty colour AOV',p)
 print('CS_SOURCE_AOV_CHANNELS_VALID',p.name,flush=True)
