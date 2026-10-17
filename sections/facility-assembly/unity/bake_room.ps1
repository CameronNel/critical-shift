# Bake one room for Unity URP on the owner's PC (Windows; Ryzen 7 5800X, 32 GB, Radeon RX 9070 XT 16 GB). Run from the repository root:
#
#   powershell -ExecutionPolicy Bypass -File sections/facility-assembly/unity/bake_room.ps1 -Device GPU -Room cooling-plant `
#       -Source sections/facility-assembly/sources/cooling-plant/module_aaa_A1.blend
#
# -Device GPU or -Device CPU is required: the owner chooses, the script never picks one or falls back (owner rule, 2026-10-16; sections/facility-assembly/blender_device.py).
# It runs bake_room.py stage by stage with --profile home (4K atlases, 8 samples, shader AO/bevel at full quality), so a crash only loses the
# stage it was in: rerun with -From <stage> to continue. Output goes to sections/facility-assembly/unity/<room>/ and the source file is never saved.
# Needs Blender 5.2 and the source file pulled from LFS (git lfs pull --include <file>). AMD GPUs need the current Adrenalin driver for HIP.
param(
    [Parameter(Mandatory = $true)][ValidateSet("GPU", "CPU")][string]$Device,
    [Parameter(Mandatory = $true)][string]$Room,
    [Parameter(Mandatory = $true)][string]$Source,
    [string]$Collection = "",
    [string]$Blender = "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe",
    [ValidateSet("prep", "base", "rough", "normal", "metal", "emit", "finish", "compare")][string]$From = "prep",
    [string]$Cameras = "",
    [string]$OutRoot = "sections/facility-assembly/unity",   # bake_all.ps1 -Map writes to .../unity/map
    [string]$CompareSource = "",                              # the file the source comparison renders come from (default: -Source)
    [switch]$Isolate                                          # map mode: bake the room collection alone (bake_room.py --isolate)
)
$ErrorActionPreference = "Stop"
$U = "sections/facility-assembly/unity"; $Out = "$OutRoot/$Room"; $Py = "$U/bake_room.py"
if (-not $CompareSource) { $CompareSource = $Source }
if (-not (Test-Path $Blender)) { throw "Blender not found at $Blender (pass -Blender <path to blender.exe>)" }
if ((Get-Item $Source).Length -lt 1024) { throw "$Source looks like an LFS pointer: git lfs pull --include $Source" }
$common = @("--room", $Room, "--out", $Out, "--profile", "home", "--device", $Device)
if ($Collection) { $common += @("--collection", $Collection) }
if ($Isolate) { $common += "--isolate" }
$stages = @("prep", "base", "rough", "normal", "metal", "emit", "finish", "compare")
$start = [array]::IndexOf($stages, $From)
$t0 = Get-Date
foreach ($s in $stages[$start..($stages.Length - 1)]) {
    $t = Get-Date; Write-Host "== $Room : $s"
    switch ($s) {
        "prep"    { & $Blender --factory-startup -b $Source --python $Py -- --stage prep @common }
        "finish"  { & $Blender --factory-startup -b "$Out/_work.blend" --python $Py -- --stage finish @common }
        "compare" {
            if (-not $Cameras) { Write-Host "   (no -Cameras given: comparison renders skipped)"; continue }
            & $Blender --factory-startup -b $CompareSource --python "$U/render_compare.py" -- "$Out/compare/source" $Cameras --samples 64 --device $Device
            & $Blender --factory-startup -b "$Out/$Room`_unity.blend" --python "$U/render_compare.py" -- "$Out/compare/baked" $Cameras --samples 64 --device $Device
        }
        default   { & $Blender --factory-startup -b "$Out/_work.blend" --python $Py -- --stage bake --pass $s @common }
    }
    if ($LASTEXITCODE -ne 0) { throw "stage $s failed (exit $LASTEXITCODE); fix it and rerun with -From $s" }
    Write-Host ("   {0:n1} min" -f ((Get-Date) - $t).TotalMinutes)
}
Write-Host ("== done in {0:n1} min: $Out" -f ((Get-Date) - $t0).TotalMinutes)
