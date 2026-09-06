param(
    [ValidateSet('review','final','none','cold-start')] [string]$Mode = 'final',
    [int]$Samples = 24,
    [switch]$States
)
$ErrorActionPreference = 'Stop'
$refineryBlender = 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe'
$refinerySection = Split-Path $PSScriptRoot -Parent
$refineryProfile = Join-Path $refinerySection 'production\private-blender-profile'
New-Item -ItemType Directory -Force $refineryProfile | Out-Null
$env:BLENDER_USER_RESOURCES = $refineryProfile
$refineryArgs = @('--background','--disable-autoexec','--threads','6','--python-exit-code','1')
if ($Mode -eq 'cold-start') {
    $refineryArgs += (Join-Path $PSScriptRoot 'Refinery.blend')
} else {
    $refineryArgs += '--factory-startup'
}
$refineryArgs += @('--python',(Join-Path $PSScriptRoot 'build_refinery.py'),'--','--samples',"$Samples")
if ($Mode -eq 'cold-start') { $refineryArgs += '--cold-start' }
if ($Mode -eq 'none') { $refineryArgs += @('--render','none') } else { $refineryArgs += @('--render','all','--pass-name',$Mode) }
if ($States) { $refineryArgs += '--states' }
& $refineryBlender @refineryArgs
exit $LASTEXITCODE
