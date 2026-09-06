"""Fetch only the selected CC0 timber and rust packs from ambientCG.
All files stay inside this mine section. Cached files are hash-verified.
"""
from pathlib import Path
import hashlib, io, json, time, urllib.request, zipfile
HERE=Path(__file__).resolve().parent
DEST=HERE.parents[2]/'assets'/'pbr'/'quality50'
ASSETS={'Wood060':'https://ambientcg.com/view?id=Wood060','Metal026':'https://ambientcg.com/view?id=Metal026'}
def main():
    DEST.mkdir(parents=True,exist_ok=True)
    manifest_path=DEST/'manifest.json'
    if manifest_path.exists():
        cached=json.loads(manifest_path.read_text())
        if all((DEST/f['path']).is_file() and hashlib.sha256((DEST/f['path']).read_bytes()).hexdigest()==f['sha256'] for a in cached['assets'] for f in a['maps'].values()):
            print('WEATHERING_TEXTURE_CACHE_VERIFIED',flush=True);return
    records=[]
    for asset,source in ASSETS.items():
        url='https://ambientcg.com/get?file='+asset+'_2K-JPG.zip'
        req=urllib.request.Request(url,headers={'User-Agent':'CriticalShiftMaterialAuthoring/1.0'})
        data=None
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req,timeout=120) as response:data=response.read(90*1024*1024)
                break
            except Exception:
                if attempt==2:raise
                time.sleep(2*(attempt+1))
        out=DEST/asset;out.mkdir(exist_ok=True)
        maps={}
        with zipfile.ZipFile(io.BytesIO(data)) as pack:
            for role,suffix in [('color','_Color.jpg'),('roughness','_Roughness.jpg'),('height','_Displacement.jpg'),('normal','_NormalGL.jpg')]:
                matches=[n for n in pack.namelist() if n.endswith(suffix)]
                if not matches:raise RuntimeError(f'Missing {role} in {asset}')
                payload=pack.read(matches[0]);p=out/(role+'.jpg');p.write_bytes(payload)
                maps[role]={'path':str(p.relative_to(DEST)),'sha256':hashlib.sha256(payload).hexdigest(),'bytes':len(payload)}
        records.append({'asset':asset,'source':source,'download_url':url,'license':'CC0-1.0','license_url':'https://docs.ambientcg.com/license/','archive_sha256':hashlib.sha256(data).hexdigest(),'maps':maps})
        print('DOWNLOADED_CC0',asset,flush=True)
    manifest_path.write_text(json.dumps({'assets':records,'usage':'Rough cart timber; selective corrosion, flaking paint and water-driven rust.'},indent=2))
if __name__=='__main__':main()
