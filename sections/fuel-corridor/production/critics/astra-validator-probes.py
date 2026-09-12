"""Independent disposable CPU probes. Never opens/saves a production scene."""
from pathlib import Path
import bpy, hashlib, json, runpy, sys

HERE = Path(__file__).resolve().parent
SECTION = HERE.parents[1]
VALIDATOR = SECTION / 'blender/validate.py'
EXPECTED_HASH = '947af229ea54958c9fed633fac3ccd7705d3ca938da1fe443e10476d32a37b78'
actual_hash = hashlib.sha256(VALIDATOR.read_bytes()).hexdigest()
assert actual_hash == EXPECTED_HASH, 'Validator changed after independent source review'
assert not bpy.data.filepath, 'Use a new factory-startup process'
v = runpy.run_path(str(VALIDATOR), run_name='astra_readonly_validator')
work = HERE / 'astra-validator-probe-evidence'
work.mkdir(exist_ok=True)
inputs = work / 'inputs'
inputs.mkdir(exist_ok=True)
interface_bytes = (SECTION / 'interface.json').read_bytes()
interface = json.loads(interface_bytes)
source_bytes = b'# disposable independent build identity fixture\n'
detail_bytes = b'# disposable independent detail identity fixture\n'
tests = []

def geometry():
    bpy.context.view_layer.update()
    deps = bpy.context.evaluated_depsgraph_get()
    return {o.name: v['Geometry'](o, deps) for o in bpy.context.scene.objects
            if o.type in v['GEOMETRY_TYPES']}

def cube(name, loc, size, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    if parent:
        obj.parent = parent
    mat = bpy.data.materials.get('Astra fixture material') or bpy.data.materials.new('Astra fixture material')
    obj.data.materials.append(mat)
    return obj

def record(name, expected, actual, **evidence):
    tests.append(dict(name=name, expected=expected, actual=actual,
                      pass_expected=(expected == actual), **evidence))

# Test the real routes_audit entry point, including visibility filtering.
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene['stage'] = 'full'
cube('Astra synthetic route floor', (5, 12, -.1), (44, 44, .2))
result = v['routes_audit'](scene, geometry(), interface)
record('full_route_clear_positive_control', 'PASS', result['status'])
block = cube('Astra render-hidden internal barrier', (0, 4, 1), (2.6, .01, 2))
block.hide_render = True
result = v['routes_audit'](scene, geometry(), interface)
record('render_hidden_internal_barrier_rejected', 'FAIL', result['status'],
       blocked_checks=[c['name'] for c in result['checks'] if c['status'] != 'PASS'])

def reset_main_fixture():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    (inputs / 'build.py').write_bytes(source_bytes)
    (inputs / 'valorant_details.py').write_bytes(detail_bytes)
    (inputs / 'interface.json').write_bytes(interface_bytes)
    s = bpy.context.scene
    s['revision'] = 'astra_disposable_probe'
    s['stage'] = 'slice'
    s['source_sha256'] = hashlib.sha256(source_bytes).hexdigest()
    s['detail_source_sha256'] = hashlib.sha256(detail_bytes).hexdigest()
    s['interface_sha256'] = hashlib.sha256(interface_bytes).hexdigest()
    root = bpy.data.objects.new('Long_cask_carrier', None)
    s.collection.objects.link(root)
    cube('Current_reactor_cartridge', (0, 0, .6), (1.18, .31, .31), root)
    cube('Current_cask_end_closure', (-.605, 0, .6), (.035, .34, .34), root)
    cube('Current_cask_end_closure.001', (.605, 0, .6), (.035, .34, .34), root)
    return root

def run_main(name):
    output = work / (name + '.json')
    old = sys.argv
    sys.argv = ['astra_probe', '--', '--source-dir', str(inputs), '--interface',
                str(inputs / 'interface.json'), '--output', str(output)]
    caught = None
    try:
        v['main']()
    except RuntimeError as exc:
        caught = str(exc)
    finally:
        sys.argv = old
    result = json.loads(output.read_text())
    assert caught is not None and result['status'] == 'FAIL'
    # Minimal fixtures intentionally fail unrelated camera/support/full/cold gates.
    # Each assertion below checks the requested gate, including positive controls.
    return result

reset_main_fixture()
r = run_main('positive_inventory_identity')
record('carrier_present_positive_control', 'PASS', r['carrier_actual_envelope']['status'])
record('core_three_parts_positive_control', 'PASS', r['current_cartridge_core']['status'])
record('matching_all_three_hashes_positive_control', True, r['source_matches_saved_scene'])

reset_main_fixture()
bpy.data.objects.remove(bpy.data.objects['Long_cask_carrier'], do_unlink=True)
r = run_main('missing_carrier')
record('missing_carrier_rejected', 'FAIL', r['carrier_actual_envelope']['status'],
       propagated_to_failed_gates='carrier_actual_envelope' in r['failed_gates'])

root = reset_main_fixture()
for o in list(root.children):
    bpy.data.objects.remove(o, do_unlink=True)
r = run_main('empty_carrier_all_core_missing')
record('empty_carrier_rejected', 'FAIL', r['carrier_actual_envelope']['status'])
record('all_core_missing_rejected', 'FAIL', r['current_cartridge_core']['status'],
       propagated_to_failed_gates='current_cartridge_core' in r['failed_gates'])

reset_main_fixture()
bpy.data.objects.remove(bpy.data.objects['Current_reactor_cartridge'], do_unlink=True)
r = run_main('missing_single_body')
record('missing_body_with_two_closures_rejected', 'FAIL', r['current_cartridge_core']['status'])

reset_main_fixture()
bpy.data.objects.remove(bpy.data.objects['Current_cask_end_closure.001'], do_unlink=True)
r = run_main('missing_single_closure')
record('missing_one_closure_rejected', 'FAIL', r['current_cartridge_core']['status'])

for name, filename in [('build', 'build.py'), ('detail', 'valorant_details.py'), ('interface', 'interface.json')]:
    reset_main_fixture()
    path = inputs / filename
    path.write_bytes(path.read_bytes() + b'\n')
    r = run_main(name + '_hash_mismatch')
    record(name + '_hash_mismatch_rejected', False, r['source_matches_saved_scene'],
           propagated_to_failed_gates='source_matches_saved_scene' in r['failed_gates'])

# Cardinality robustness: three matching prefixes do not guarantee one body/two ends.
reset_main_fixture()
bpy.data.objects['Current_reactor_cartridge'].name = 'Current_cask_end_closure.002'
r = run_main('missing_body_three_closure_named_parts')
record('one_body_two_closure_roles_enforced', 'FAIL', r['current_cartridge_core']['status'],
       issue='No body-role object exists; combined bounds unchanged with three closure-prefix objects')

summary = dict(validator_sha256=actual_hash,
               interface_sha256=hashlib.sha256(interface_bytes).hexdigest(),
               blender_version=bpy.app.version_string, tests=tests,
               all_expectations_met=all(t['pass_expected'] for t in tests),
               scope='Disposable factory scene only; no rendering, production scene load or save. main() tests assert specific gates; unrelated fixture gates intentionally fail.')
(HERE / 'astra-validator-probe-summary.json').write_text(json.dumps(summary, indent=2))
print('ASTRA_VALIDATOR_PROBES', json.dumps(summary, indent=2), flush=True)
