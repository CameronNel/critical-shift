param(
  [ValidateSet('build','render','cold','validate')][string]$Action = 'build',
  [string]$Revision = 'R01',
  [int]$Samples = 48,
  [int]$Width = 1600,
  [int]$Height = 900,
  [string]$Cameras = 'all',
  [string]$Device = 'CPU',
  [int]$MaxWait = 3600
)
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$BlenderDir = Join-Path $Root 'blender'
$Profile = Join-Path $Root 'production/runtime/blender-user'
$Blender = 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
$Py = 'C:/Users/Camer/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
$Gate = 'C:/Users/Camer/Games/critical-shift/ops/facility-run/gpu_gate.py'
$Script = Join-Path $BlenderDir 'build_ocru.py'
$Blend = Join-Path $BlenderDir 'ocru.blend'
New-Item -ItemType Directory -Force -Path $Profile, (Join-Path $Root "production/renders/$Revision") | Out-Null
$env:BLENDER_USER_RESOURCES = $Profile
$env:BLENDER_USER_CONFIG = Join-Path $Profile 'config'
$env:BLENDER_USER_SCRIPTS = Join-Path $Profile 'scripts'
$env:BLENDER_USER_DATAFILES = Join-Path $Profile 'datafiles'
$env:BLENDER_USER_EXTENSIONS = Join-Path $Profile 'extensions'
$BlenderArgs = @('--background','--factory-startup','--disable-autoexec','--python-exit-code','1','--python',$Script,'--')
switch ($Action) {
  'build' {
    $BlenderArgs += @('--save','--validate','--render','none')
    & $Blender @BlenderArgs
    exit $LASTEXITCODE
  }
  'validate' {
    $BlenderArgs += @('--open',$Blend,'--cold-start','--validate','--render','none')
    & $Blender @BlenderArgs
    exit $LASTEXITCODE
  }
  'render' {
    $renderList = $Cameras
    $extra = @('--save','--validate','--render',$renderList,'--pass-name',$Revision,'--samples',"$Samples",'--width',"$Width",'--height',"$Height",'--device',$Device)
    if ($Device -eq 'GPU') {
      $cmd = @($Blender) + $BlenderArgs + $extra
      & $Py $Gate --owner medical-reanimation --max-wait $MaxWait -- @cmd
      exit $LASTEXITCODE
    } else {
      & $Blender @BlenderArgs @extra
      exit $LASTEXITCODE
    }
  }
  'cold' {
    $extra = @('--open',$Blend,'--cold-start','--render',$Cameras,'--pass-name','cold-start','--samples',"$Samples",'--width',"$Width",'--height',"$Height",'--device',$Device)
    if ($Device -eq 'GPU') {
      $cmd = @($Blender) + $BlenderArgs + $extra
      & $Py $Gate --owner medical-reanimation --max-wait $MaxWait -- @cmd
      exit $LASTEXITCODE
    } else {
      & $Blender @BlenderArgs @extra
      exit $LASTEXITCODE
    }
  }
}
