"""Run only inside the shared GPU gate. Each batch cold-opens the saved file in a new Blender process."""
import subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];blender='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe';blend=R/'blender/medical_integration.blend'
for folder in ['final','cold']:
 cmd=[blender,'--background',str(blend),'--python',str(R/'blender/render_room.py'),'--','--out',str(R/'production/renders'/folder),'--samples','64']
 subprocess.run(cmd,check=True)
 if not (R/'production/renders'/folder/'render_manifest.json').exists():raise RuntimeError('Missing render manifest')
subprocess.run([blender,'--background',str(blend),'--python',str(R/'blender/interaction_evidence.py'),'--','--render'],check=True)
print('FINAL_COLD_STATE_BATCH_COMPLETE',flush=True)
