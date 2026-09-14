param([switch]$Preview)
$ErrorActionPreference='Stop'
$mapBlender=$env:BLENDER_EXECUTABLE
if (-not $mapBlender) {
    $mapCommand=Get-Command blender -ErrorAction SilentlyContinue
    if ($mapCommand) {$mapBlender=$mapCommand.Source}
    elseif (Test-Path 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe') {$mapBlender='C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'}
    else {throw 'Install Blender 5.2 LTS or set BLENDER_EXECUTABLE to its executable.'}
}
$mapArguments=@('--python',(Join-Path $PSScriptRoot 'open_map.py'))
if ($Preview) {$mapArguments+=@('--','--preview')}
& $mapBlender @mapArguments
