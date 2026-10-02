#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../../../../.."
overhaul_dir="sections/facility-assembly/sources/electrical-room/overhaul"
blender_exec="${BLENDER_EXECUTABLE:-/workspace/toolchains/blender-5.2.1-linux-x64/blender}"
if [[ ! -x "$blender_exec" ]]; then blender_exec="$(command -v blender)"; fi
if ! "$blender_exec" --version | head -1 | rg -q 'Blender 5\.2\.'; then
  echo 'Set BLENDER_EXECUTABLE to an installed Blender 5.2 LTS executable.' >&2
  exit 1
fi
export XDG_CACHE_HOME="${XDG_CACHE_HOME:-/tmp/electrical-cache}"
case "${1:-}" in
  build)
    "$blender_exec" -noaudio --background --disable-autoexec "$overhaul_dir/checkpoints/baseline.blend" --python-exit-code 1 --python "$overhaul_dir/scripts/build.py" -- --stage "${2:-full}" --output "${3:-$overhaul_dir/checkpoints/rebuilt.blend}"
    ;;
  validate)
    "$blender_exec" -noaudio --background --disable-autoexec "$2" --python-exit-code 1 --python "$overhaul_dir/scripts/validate.py" -- --baseline "$overhaul_dir/checkpoints/baseline.blend" --out "$3"
    ;;
  capture)
    "$blender_exec" -noaudio --background --disable-autoexec "$2" --python-exit-code 1 --python "$overhaul_dir/scripts/capture.py" -- --out "$3" --samples "${4:-24}" --width 1280
    ;;
  *) echo 'Usage: bash overhaul/run.sh build [slice|full] [output.blend] | validate source.blend report.json | capture source.blend output-dir [samples]' >&2;exit 2;;
esac
