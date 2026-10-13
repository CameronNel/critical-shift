from pathlib import Path
import bpy,sys,json,hashlib
root=Path('/workspace/critical-shift-spawn-runtime');sys.path.insert(0,str(root/'runtime/tools'));from mine_context_lights import context_spot_lights
from mathutils import Matrix
matrix=lambda o: matrix(o.parent)@o.matrix_parent_inverse@o.matrix_basis if o.parent else o.matrix_basis.copy()
front=bpy.data.objects['ROOM_front-end-area'];records=context_spot_lights(front.instance_collection.all_objects,matrix);assert len(records)==6
out=Path('/tmp/cs-mine-production-spot-source-final14.json');assert not out.exists();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();out.write_text(json.dumps({'status':'ActualProductionSourceSpotContractExtracted','lights':records,'sourceSnapshotSha256':sha(root/'runtime/out/spawn-export-source/combined-runtime-source.blend'),'exporterSha256':sha(root/'runtime/tools/mine_context_lights.py'),'helperSha256':sha(Path(__file__)),'limits':['Readonly source exporter reproduction; Source/main/Generated files untouched']},indent=2)+'\n');print('CS_PRODUCTION_SOURCE_SPOT_CONTRACT_OK',len(records))
