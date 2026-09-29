param([string]$Scene='facility_environment.blend',[string]$Script='inspect_spawn_integration.py',[string]$Mode='')
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
$taskOut=Join-Path $taskRoot 'runtime/out/spawn-integration'
New-Item -ItemType Directory -Force -Path $taskOut | Out-Null
$scenePath=if([IO.Path]::IsPathRooted($Scene)){$Scene}else{Join-Path $PSScriptRoot $Scene}
$argsLine='--background --factory-startup --disable-autoexec --python-exit-code 1 --threads 1 "'+$scenePath+'" --python "'+(Join-Path $PSScriptRoot $Script)+'"'
if($Mode){$argsLine+=' -- '+$Mode}
$worker=Start-Process -FilePath 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' -ArgumentList $argsLine -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $taskOut 'worker.log') -RedirectStandardError (Join-Path $taskOut 'worker-errors.log')
$worker.PriorityClass='BelowNormal'
$worker.WaitForExit()
Get-Content (Join-Path $taskOut 'worker.log') -Tail 10
if($worker.ExitCode -ne 0){Get-Content (Join-Path $taskOut 'worker-errors.log');throw "Blender worker exit $($worker.ExitCode)"}
