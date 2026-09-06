"""Download an explicit CC0 selection from Poly Haven's public API.
Source attribution and SHA-256 are retained. No downloaded code is executed.
"""
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import urlparse
import json,hashlib,time,sys
OUT=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parent/'assets'
HEAD={'User-Agent':'CriticalShift-Gullet-Artmatch/1.0 (CameronNel/critical-shift)','Referer':'https://github.com/CameronNel/critical-shift'}
MODELS=['metal_toolbox','metal_tool_chest','barrel_03','wooden_crate_02','rusted_spade_01','sledgehammer_01','rusted_hacksaw','wooden_ladder','can_rusted','sand_rocks_small_01','rock_09','rock_07','rock_face_01','coast_rocks_03']
TEXTURES=['damaged_concrete_floor','concrete_debris','rocky_gravel','rust_coarse_01','muddy_tracks']
OUT.mkdir(parents=True,exist_ok=True)
def get(url):
    last=None
    for attempt in range(3):
        try:
            with urlopen(Request(url,headers=HEAD),timeout=100) as r: return r.read()
        except Exception as e:
            last=e;time.sleep(1+attempt)
    raise last

def save(url,path):
    path.parent.mkdir(parents=True,exist_ok=True)
    data=get(url)
    if len(data)>150_000_000:raise RuntimeError('Unexpected oversized asset: '+url)
    path.write_bytes(data)
    return {'path':str(path.relative_to(OUT)),'url':url,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}

records=[];errors=[]
for name in MODELS+TEXTURES:
    try:
        info=json.loads(get('https://api.polyhaven.com/files/'+name));folder=OUT/name;folder.mkdir(exist_ok=True)
        (folder/'api_files.json').write_text(json.dumps(info,indent=2))
        record={'id':name,'license':'CC0-1.0','source':'https://polyhaven.com/a/'+name,'files':[],'kind':'model' if name in MODELS else 'texture'}
        if name in MODELS:
            kind='gltf' if 'gltf' in info else 'blend'
            sizes=info[kind];res='1k' if '1k' in sizes else '2k' if '2k' in sizes else next(iter(sizes))
            node=sizes[res];node=node.get(kind,next(iter(node.values())))
            if not isinstance(node,dict) or 'url' not in node:raise ValueError('Unexpected model schema '+repr(node)[:500])
            dest=folder/Path(urlparse(node['url']).path).name
            record['files'].append(save(node['url'],dest));record['entrypoint']=str(dest.relative_to(OUT));record['format']=kind
            for rel,value in node.get('include',{}).items():
                path=Path(rel)
                if path.is_absolute() or '..' in path.parts:raise ValueError('Unsafe relative path')
                if isinstance(value,dict) and 'url' in value:record['files'].append(save(value['url'],folder/path))
                elif isinstance(value,str):record['files'].append(save(value,folder/path))
        else:
            record['maps']={}
            for role,keys in [('color',['diff','Diffuse','albedo']),('roughness',['rough','Rough']),('height',['disp','Displacement'])]:
                key=next((k for k in keys if k in info),None)
                if key is None:key=next((k for k in info if k.lower() in [x.lower() for x in keys]),None)
                if key is None:raise ValueError('Missing '+role+' in '+str(list(info)))
                sizes=info[key];node=sizes.get('2k',sizes.get('1k'));fmt='jpg' if 'jpg' in node else 'png' if 'png' in node else next(iter(node));node=node[fmt]
                item=save(node['url'],folder/(role+'.'+fmt));record['files'].append(item);record['maps'][role]=item['path']
        records.append(record);print('ASSET_OK',name,len(record['files']),flush=True)
    except Exception as e:
        errors.append({'asset':name,'error':repr(e)});print('ASSET_ERROR',name,repr(e),flush=True)
    (OUT/'selected_manifest.json').write_text(json.dumps({'provider':'Poly Haven','license_url':'https://polyhaven.com/license','assets':records,'errors':errors},indent=2))
    time.sleep(.25)
print('FINISHED',len(records),'assets;',len(errors),'errors')
if errors:raise SystemExit(1)
