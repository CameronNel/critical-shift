#!/bin/sh
# Hall pass chain: rh_pipeline.sh <hall_base.blend> <out_dir>
# BLENDER_EXECUTABLE selects the portable Blender CLI; PY retains bpy-Python use.
set -e
P=${PY:-/tmp/bv/bin/python}; B=$1; O=$2
mkdir -p "$O"
D=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$D"
run() {
    if [ -n "${BLENDER_EXECUTABLE:-}" ]; then
        "$BLENDER_EXECUTABLE" --background --disable-autoexec -noaudio --python-exit-code 1 --python "$D/rh_stage_runner.py" -- "$D/$1" "$2" "$3"
    else
        "$P" "$D/$1" -- "$2" "$3"
    fi
}
run rh_floor.py "$B" "$O/s1_floor.blend" > "$O/s1.log" 2>&1
run rh_walls.py "$O/s1_floor.blend" "$O/s2_walls.blend" > "$O/s2.log" 2>&1
run rh_stations.py "$O/s2_walls.blend" "$O/s3_stations.blend" > "$O/s3.log" 2>&1
run rh_services.py "$O/s3_stations.blend" "$O/s4_services.blend" > "$O/s4.log" 2>&1
run rh_pool_surround.py "$O/s4_services.blend" "$O/s5_pool.blend" > "$O/s5.log" 2>&1
run rh_light.py "$O/s5_pool.blend" "$O/s5b_light.blend" > "$O/s5b.log" 2>&1
run rh_refine.py "$O/s5b_light.blend" "$O/s5c_refined.blend" > "$O/s5c.log" 2>&1
run rh_final.py "$O/s5c_refined.blend" "$O/hall_final.blend" > "$O/s6.log" 2>&1
run rh_door_hardware_audit.py "$O/hall_final.blend" "$O/door-hardware-audit.json" > "$O/door_hardware-check.log" 2>&1
echo chain-ok > "$O/chain.ok"
