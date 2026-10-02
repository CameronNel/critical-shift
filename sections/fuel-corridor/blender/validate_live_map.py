"""Cold-check the normal map launcher and repeat installation without saving it.

blender -b --factory-startup --disable-autoexec --python-exit-code 1 \
 --python sections/fuel-corridor/blender/validate_live_map.py

Uses the existing map launcher and live-module installer. Writes task QA JSON
only; no native scene, registry, frozen preview or other section is saved.
"""
from pathlib import Path
import datetime
import hashlib
import json
import runpy
import sys
import bpy

ROOT = Path(__file__).resolve().parents[3]
TASK = ROOT / 'sections/fuel-corridor/production'
registry = json.loads((ROOT / 'MAP.json').read_text())
canonical = ROOT / registry['authoring_scene']
source = ROOT / 'sections/facility-assembly/sources/fuel-corridor/module.blend'
preview = ROOT / 'sections/facility-assembly/blender/facility_spawn_material_preview_R17.blend'
spawn = ROOT / 'sections/facility-assembly/sources/spawn-room/module.blend'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
frozen = {
    canonical: '7d263a04e42b357f30c38df1ff012a4b7e80fc9bab3f4869e4782318e9fa88c8',
    preview: '4d5d160d5c9d25b0a447fda933974790260cdde7aced2db1da1c908afdcdc937',
    spawn: '1964d3d16716730631af0d5c77bcc604a64455092142cc57c0283172a563a977',
}
assert all(sha(p) == expected for p, expected in frozen.items()), 'Frozen dependency differs'
build = json.loads((TASK / 'BUILD_MANIFEST.json').read_text())
cold = json.loads((TASK / 'COLD_VALIDATION.json').read_text())
assert sha(source) == build['sha256'] == cold['sha256'], 'Native/build/cold pair differs'
assert cold['status'] == 'PASS' and not cold['failures']
assert all(sha(ROOT / p) == expected for p, expected in build['recipe_inputs'].items())

runpy.run_path(str(ROOT / 'open_map.py'), run_name='__main__')
sys.path.insert(0, str(ROOT))
import open_fuel_overhaul
instance = bpy.data.objects['FUEL_OVERHAUL_LIVE']
module = instance.instance_collection
assert module.library and Path(bpy.path.abspath(module.library.filepath)).resolve() == source
assert module['fc_recipe_sha256'] == build['recipe_sha256']
compatibility = build.get('main_cache_material_compatibility', {})
linked_materials = {m.name: m for m in bpy.data.materials if m.library and
    Path(bpy.path.abspath(m.library.filepath)).resolve() == source}
assert all(name in linked_materials and not linked_materials[name].is_missing
    for name in compatibility), 'Frozen main fuel material reference did not resolve'
assert not any(m.is_missing for m in linked_materials.values()), 'Missing fuel material ID'
cache = bpy.data.objects['VC | Roof-finished MATERIAL_PREVIEW_fuel-corridor']
assert cache.hide_render and cache.hide_get()
counts = (len(bpy.data.objects), len(bpy.data.collections))
matrix = [list(row) for row in instance.matrix_world]
again, new_instance, new_cache, hidden = open_fuel_overhaul.install_live_fuel()
assert (again, new_instance, new_cache) == (module, instance, cache)
assert counts == (len(bpy.data.objects), len(bpy.data.collections))
assert matrix == [list(row) for row in instance.matrix_world]
lighting_policy=json.loads(instance['fc_lighting_policy'])
expected_receivers=[instance]+[o for o in module.all_objects if o.type in {'MESH','FONT','CURVE','SURFACE'}]
for light in bpy.context.scene.objects:
    if light.type!='LIGHT' or light.data.type!='SUN' or light.hide_render:continue
    receiver=light.light_linking.receiver_collection
    assert receiver and all(receiver.objects.find(o.name)>=0 and receiver.collection_objects[receiver.objects.find(o.name)].light_linking.link_state=='EXCLUDE' for o in expected_receivers),'Map helper can illuminate fuel surfaces'
assert len(lighting_policy['excluded_map_helpers'])==5,'Map daylight helper inventory changed'
assert all(bpy.data.objects[name].hide_render for name in hidden)
assert len(hidden) == len([o for o in build['baseline_asset_inventory'] if o['type'] == 'LIGHT'])
assert all(sha(p) == expected for p, expected in frozen.items()), 'Frozen dependency changed'
assert sha(source) == build['sha256'], 'Source changed'
animation=[]
atmo=build.get('atmosphere',{})
if atmo:
    # The actual linked collection must retain light and isolated optic keys.
    # Preserve the main scene's timeline; only evaluate in this disposable run.
    scene=bpy.context.scene;saved_frame=scene.frame_current
    for frame in [1,18,29,33,46,110,151,240,241]:
        scene.frame_set(frame);graph=bpy.context.evaluated_depsgraph_get();values=[]
        for record in atmo['flicker']+atmo.get('alarms',[]):
            obj=next(o for o in module.all_objects if o.name==record['light'])
            energy=float(obj.evaluated_get(graph).data.energy);factor=energy/record['energy_base_w']
            assert obj.data.animation_data and obj.data.animation_data.action,'Linked light keys absent'
            for optic in record['optics']:
                m=next(m for m in linked_materials.values() if m.name==optic['material'])
                assert m.node_tree.animation_data and m.node_tree.animation_data.action,'Linked optic keys absent'
                emission=m.node_tree.nodes.get('Principled BSDF').inputs['Emission Strength'].default_value
                assert abs(emission/optic['emission_base']-factor)<1e-5,'Linked optic/light mismatch'
            values.append({'light':obj.name,'energy_w':energy,'factor':factor})
        animation.append({'frame':frame,'values':values})
    scene.frame_set(saved_frame)
report = {
    'schema': 'fuel-normal-map-launcher-validation/1',
    'created_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'status': 'PASS', 'launcher': 'open_map.py',
    'canonical_map_sha256': frozen[canonical], 'frozen_R17_sha256': frozen[preview],
    'spawn_reference_sha256': frozen[spawn],
    'native_sha256': build['sha256'], 'recipe_sha256': build['recipe_sha256'],
    'linked_module': module.name, 'module_objects': len(module.all_objects),
    'hidden_old_fuel_lights': len(hidden), 'old_cache_hidden': True,
    'main_cache_material_ids_resolved': len(compatibility),
    'repeat_install_idempotent': True, 'instance_matrix': matrix,
    'saved_main': False, 'source_bytes_unchanged': True,
    'linked_animation_samples': animation,
    'map_fps': bpy.context.scene.render.fps,
    'map_fps_base': bpy.context.scene.render.fps_base,
    'fixture_lighting_policy': lighting_policy,
    'lighting_installer_sha256': sha(ROOT/'open_fuel_overhaul.py'),
    'limits': ['No Unity build, performance, controller or continuous collision test.'],
}
(TASK / 'MAP_LAUNCHER_VALIDATION.json').write_text(json.dumps(report, indent=2) + '\n')
print('NORMAL_MAP_LAUNCHER_VALIDATION', json.dumps(report), flush=True)
