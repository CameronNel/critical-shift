$assemblyRoot = Split-Path -Parent $PSScriptRoot
$env:BLENDER_USER_CONFIG = Join-Path $assemblyRoot 'production/blender-profile'
$walkScript = Join-Path $PSScriptRoot 'open_walkthrough.py'
Start-Process -FilePath 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' -ArgumentList @('--python',('"' + $walkScript + '"')) -WindowStyle Normal
