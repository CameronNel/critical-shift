"""Reuse our proven primitive helpers; no scene geometry imported."""
from pathlib import Path
R=Path(__file__).resolve().parents[1]
src=(R.parent/'waste-storage/blender/build_scene.py').read_text()
src=src[:src.index("exec(compile((Path(__file__).parent/'full_hall.py')")]
src=src.replace('Original Waste Storage.','Original Medical / Reanimation.').replace("SC['section']='waste-storage'","SC['section']='medical-reanimation'")
src=src.replace("['Architecture','Casks','Containers','Cart','Monitoring','Ventilation','Workshop','Lighting','Cameras','Validation']","['Architecture','OCRU','Stations','Utilities','Props','Lighting','Cameras','Validation']")
src += "\nexec(compile((Path(__file__).parent/'medical_scene.py').read_text(),str(Path(__file__).parent/'medical_scene.py'),'exec'))\n"
(R/'blender/build_scene.py').write_text(src)
