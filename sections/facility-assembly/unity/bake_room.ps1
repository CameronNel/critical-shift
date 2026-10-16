# Bake one room for Unity URP on the owner's PC (Windows; Ryzen 7 5800X, 32 GB, Radeon RX 9070 XT 16 GB). Run from the repository root:
#
#   powershell -ExecutionPolicy Bypass -File sections/facility-assembly/unity/bake_room.ps1 -Room cooling-plant `
#       -Source sections/facility-assembly/sources/cooling-plant/module_aaa_A1.blend
#
# It runs bake_room.py stage by stage with --profile home (GPU through HIP, 4K atlases, 8 samples, shader AO/bevel at full quality), so a crash only loses the
# stage it was in: rerun with -From <stage> to continue. Output goes to sections/facility-assembly/unity/<room>/ and the source file is never saved.
# Needs Blender 5.2 and the source file pulled from LFS (git lfs pull --include <file>). AMD GPUs need the current Adrenalin driver for HIP.
param(
    [Parameter(Mandatory = $true)][string]$Room,
    [Parameter(Mandatory = $true)][string]$Source,
    [string]$Collection = "",
    [string]$Blender = "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe",
    [ValidateSet("prep", "base", "rough", "normal", "metal", "emit", "finish", "compare")][string]$From = "prep",
    [string]$Cameras = ""
)
$ErrorActionPreference = "Stop"
$U = "sections/facility-assembly/unity"; $Out = "$U/$Room"; $Py = "$U/bake_room.py"
if (-not (Test-Path $Blender)) { throw "Blender not found at $Blender (pass -Blender <path to blender.exe>)" }
if ((Get-Item $Source).Length -lt 1024) { throw "$Source looks like an LFS pointer: git lfs pull --include $Source" }
$common = @("--room", $Room, "--out", $Out, "--profile", "home")
if ($Collection) { $common += @("--collection", $Collection) }
$stages = @("prep", "base", "rough", "normal", "metal", "emit", "finish", "compare")
$start = [array]::IndexOf($stages, $From)
$t0 = Get-Date
foreach ($s in $stages[$start..($stages.Length - 1)]) {
    $t = Get-Date; Write-Host "== $Room : $s"
    switch ($s) {
        "prep"    { & $Blender -b $Source --python $Py -- --stage prep @common }
        "finish"  { & $Blender -b "$Out/_work.blend" --python $Py -- --stage finish @common }
        "compare" {
            if (-not $Cameras) { Write-Host "   (no -Cameras given: comparison renders skipped)"; continue }
            & $Blender -b $Source --python "$U/render_compare.py" -- "$Out/compare/source" $Cameras --samples 64
            & $Blender -b "$Out/$Room`_unity.blend" --python "$U/render_compare.py" -- "$Out/compare/baked" $Cameras --samples 64
        }
        default   { & $Blender -b "$Out/_work.blend" --python $Py -- --stage bake --pass $s @common }
    }
    if ($LASTEXITCODE -ne 0) { throw "stage $s failed (exit $LASTEXITCODE); fix it and rerun with -From $s" }
    Write-Host ("   {0:n1} min" -f ((Get-Date) - $t).TotalMinutes)
}
Write-Host ("== done in {0:n1} min: $Out" -f ((Get-Date) - $t0).TotalMinutes)
