param(
    [string]$Revision = 'art-01',
    [string]$Render = 'all',
    [int]$Samples = 48,
    [int]$Width = 1280,
    [switch]$ColdStart
)
$ErrorActionPreference = 'Stop'
$sceneBlender = 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
$sceneSection = Split-Path $PSScriptRoot -Parent
$sceneProfile = Join-Path $sceneSection 'production/private-blender-profile'
New-Item -ItemType Directory -Force -Path $sceneProfile | Out-Null
$env:BLENDER_USER_RESOURCES = $sceneProfile
$sceneArgs = @('--background','--disable-autoexec','--threads','8','--python-exit-code','1')
if ($ColdStart) { $sceneArgs += (Join-Path $PSScriptRoot 'reactor_scene.blend') }
else { $sceneArgs += '--factory-startup' }
$sceneArgs += @('--python',(Join-Path $PSScriptRoot 'build_scene.py'),'--','--revision',$Revision,'--render',$Render,'--samples',"$Samples",'--width',"$Width")
if ($ColdStart) { $sceneArgs += '--cold-start' }
& $sceneBlender @sceneArgs
exit $LASTEXITCODE
