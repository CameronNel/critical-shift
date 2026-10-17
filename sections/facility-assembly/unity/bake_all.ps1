# Bake every room the combined map uses, one after another, for Unity URP on the owner's PC. Run from the repository root:
#
#   powershell -ExecutionPolicy Bypass -File sections/facility-assembly/unity/bake_all.ps1 -Device GPU
#
# -Device GPU or -Device CPU is required: the owner chooses; nothing picks one or falls back (owner rule, 2026-10-16; ../blender_device.py).
# Each room runs bake_room.ps1 (prep, base, rough, normal, metal, emit, finish, compare) with --profile home. A log per room goes to
# sections/facility-assembly/unity/_logs/<room>.log. The run stops at the first failure and prints the command that resumes it.
#   -Only a,b     bake just these rooms        -Skip a,b     leave these out
#   -From <stage> resume the FIRST room at that stage (the rest start at prep)
# The condenser bay is left out on purpose: its finish is being reworked (sources/condenser-bay/REWORK_BRIEF.md).
# Rooms are baked from their room modules, not from the combined map, so map-side changes (door cuts, the mine cut, the turbine skin,
# the animated ore cart, the evacuation additions) are not in these bakes. Outputs stay local: do not commit them (LFS quota).
param(
    [Parameter(Mandatory = $true)][ValidateSet("GPU", "CPU")][string]$Device,
    [string[]]$Only = @(),
    [string[]]$Skip = @(),
    [ValidateSet("prep", "base", "rough", "normal", "metal", "emit", "finish", "compare")][string]$From = "prep",
    [string]$Blender = "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
)
$ErrorActionPreference = "Stop"
$U = "sections/facility-assembly/unity"; $S = "sections/facility-assembly/sources"
$Reactor = "02 ROOF STRUCTURE,03 POOL AND RAIL,04 BANK MECHANISMS,05 PERIMETER EQUIPMENT,RF APPROVED SKYLIGHT ROOF,MF WORKFLOW MACHINERY," +
           "WA A FUEL BAY,WB B WASTE VENT,WD D COOLING WALL,WF F RIM SERVICE HANDLING,20 CONTROL MEZZANINE,23 ASSET PORTS,24 REACTOR STATE," +
           "25 LIGHTING,22 R2 ARCHITECTURE,23 R2 FLOOR AND DRESSING,26 R2 CONTROL ROOM,24 R2 PIPING AND CABLES,27 R2 STATIONS,29 R2 DRESSING 2," +
           "30 R2 DOOR STUBS,31 CR CONTROL ROOM REDO,RH REFINEMENT,RH HOIST ANCHOR CORRECTION"
$Refinery = "REFINERY_ARCHITECTURE,REFINERY_MACHINES,REFINERY_CONVEYORS,REFINERY_UTILITIES,REFINERY_PROPS,REFINERY_LIGHTING,REFINERY_INTERACTION," +
            "REFINERY_VALIDATION,CS_SUPPORT_REQUIRED,CS_FLOOR_DRESSING,03_CART_UNLOAD,CS_SURFACE_DRESSING,CS_WALL_DRESSING,CS_CEILING_DRESSING," +
            "REFINERY_STATE_PREVIEWS,REFINERY_COBALT_ARCHITECTURE,REFINERY_OVERHAUL"
# Smallest first, so a problem shows up early. Same sources and collections as build_compact_map.py / build_combined_map.py.
$Rooms = @(
    @{ Room = "cooling-plant";       Source = "$S/cooling-plant/module_aaa_A1.blend";                   Collection = "MODULE_cooling-plant";        Cameras = "C02_HERO,C06_EXCHANGER,C05_PUMP_A" },
    @{ Room = "waste-storage";       Source = "$S/waste-storage/module_aaa_A1.blend";                   Collection = "MODULE_waste-storage";        Cameras = "AAA01_WIDE_ENTRY,AAA02_CASKS,C04_Route" },
    @{ Room = "turbine-room";        Source = "$S/turbine-room/rebuild/turbine_room_v2_geo.blend";      Collection = "TURBINE_ROOM_V2";             Cameras = "CAM_A_entry_north,CAM_G_generator,CAM_E_controls" },
    @{ Room = "fuel-corridor";       Source = "$S/fuel-corridor/module_short_S1.blend";                 Collection = "MODULE_fuel-corridor";        Cameras = "C01_ENTRY,C03_HERO,C05_EAST_TURN" },
    @{ Room = "electrical-room";     Source = "$S/electrical-room/overhaul/checkpoints/full-R11.blend"; Collection = "MODULE_electrical-room";      Cameras = "C01_Entry,C02_Hero,C06_Transformer" },
    @{ Room = "compliance-dock";     Source = "$S/compliance-dock/module_overhaul_R1.blend";            Collection = "MODULE_compliance-dock,09 Overhaul | full"; Cameras = "C01_ENTRY,C02_HERO_DOCK,C07_OFFICE_INTERIOR" },
    @{ Room = "medical-reanimation"; Source = "$S/medical-reanimation/module_overhaul_R2.blend";        Collection = "MODULE_medical-reanimation";  Cameras = "CAM_ENTRY,CAM_HERO,CAM_CONSOLE" },
    @{ Room = "refinery";            Source = "$S/refinery/module_overhaul_R1.blend";                   Collection = $Refinery;                     Cameras = "CAM_ENTRY,CAM_PROCESS,CAM_HERO_DETAIL" },
    @{ Room = "front-end-area";      Source = "$S/front-end-area/front_end_area_cafeteria_revamp.blend"; Collection = "MODULE_front-end-area";      Cameras = "CAF_02_DINING,HAL_01_FROM_CAFETERIA,YRD_01_FROM_PORCH" },
    @{ Room = "spawn-room";          Source = "$S/spawn-room/module.blend";                             Collection = "MODULE_spawn-room";           Cameras = "REFERENCE_BRIEFING,REFERENCE_HALL,REFERENCE_LOCKER" },
    @{ Room = "reactor-room";        Source = "sections/reactor-room/blender/reactorroom.blend";        Collection = $Reactor;                      Cameras = "01_HERO,02_WEST_ENTRY,07_EMERGENCY_COOLING" },
    @{ Room = "mine";                Source = "$S/mine-r39/module_r39_aaa.blend";                       Collection = "MODULE_mine-r39";             Cameras = "R39_01_PORTAL_APPROACH,R39_02_TUNNEL,R39_04_SHED_FRONT" }
)
$Only = @($Only | ForEach-Object { $_ -split "," } | Where-Object { $_ }); $Skip = @($Skip | ForEach-Object { $_ -split "," } | Where-Object { $_ })   # -File passes "a,b" as one string
if ($Only.Count) { $Rooms = $Rooms | Where-Object { $Only -contains $_.Room } }
if ($Skip.Count) { $Rooms = $Rooms | Where-Object { $Skip -notcontains $_.Room } }
if (-not $Rooms) { throw "no rooms selected" }

# Check everything before the first bake: Blender, the device, every source pulled from LFS.
if (-not (Test-Path $Blender)) { throw "Blender not found at $Blender (pass -Blender <path to blender.exe>)" }
& $Blender -b --factory-startup --python "$U/check_device.py" -- --device $Device
if ($LASTEXITCODE -ne 0) { throw "device check failed for -Device $Device (see above). Not switching devices: report to the owner." }
$need = @($Rooms | ForEach-Object { $_.Source })
if ($Rooms | Where-Object { $_.Room -eq "spawn-room" }) { $need += "$S/spawn-room/hero_suit.blend" }
foreach ($f in $need) {
    if (-not (Test-Path $f)) { throw "missing $f" }
    if ((Get-Item $f).Length -lt 1024) { throw "$f is an LFS pointer: git lfs pull --include `"$f`"" }
}
New-Item -ItemType Directory -Force "$U/_logs" | Out-Null

$t0 = Get-Date; $first = $true
foreach ($r in $Rooms) {
    $start = if ($first) { $From } else { "prep" }; $first = $false
    $log = "$U/_logs/$($r.Room).log"; $t = Get-Date
    Write-Host ("==== {0} (from {1}) started {2:HH:mm}" -f $r.Room, $start, $t)
    $ErrorActionPreference = "Continue"     # Windows PowerShell turns Blender's stderr lines into error records; with "Stop" the first warning would end the run
    & powershell -NoProfile -ExecutionPolicy Bypass -File "$U/bake_room.ps1" -Device $Device -Room $r.Room -Source $r.Source `
        -Collection $r.Collection -Cameras $r.Cameras -From $start -Blender $Blender *>&1 | ForEach-Object { "$_" } | Tee-Object -FilePath $log -Append
    $code = $LASTEXITCODE; $ErrorActionPreference = "Stop"
    if ($code -ne 0) {
        throw ("{0} failed; log: {1}. Resume after fixing with: -Only {0} -From <the stage that failed>, then run the rest with -Skip <the rooms already done>." -f $r.Room, $log)
    }
    Write-Host ("==== {0} done in {1:n1} min" -f $r.Room, ((Get-Date) - $t).TotalMinutes)
}
Write-Host ("==== all {0} rooms done in {1:n1} h" -f @($Rooms).Count, ((Get-Date) - $t0).TotalHours)
