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
#   -Map          bake the rooms AS THEY ARE IN THE COMBINED MAP (combined/combined_map.blend): door cuts, the slim mine, the turbine skin
#                 and other map-side changes included, plus one extra piece, map-connections (connectors, stairs, signs, evacuation road).
#                 Output goes to unity/map/<room>; Critical Shift > Rooms > Import Baked Map places them with map/map_placement.json.
#                 Without -Map, rooms are baked from their own room files and the map-side changes are missing.
# Outputs stay local: do not commit them (LFS quota).
param(
    [Parameter(Mandatory = $true)][ValidateSet("GPU", "CPU")][string]$Device,
    [string[]]$Only = @(),
    [string[]]$Skip = @(),
    [ValidateSet("prep", "base", "rough", "normal", "metal", "emit", "mask", "finish", "check", "compare")][string]$From = "prep",
    [string]$Blender = "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe",
    [switch]$Map,
    [ValidateSet("home", "rehearsal")][string]$Quality = "home",   # rehearsal: every stage at 256 px and 1 sample, to prove the run before the real one
    [string]$OutRoot = "",                                          # default unity/ (unity/map with -Map)
    [string]$LogDir = ""                                            # default unity/_logs
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
    @{ Room = "mine";                Source = "$S/mine-r39/module_r39_aaa.blend";                       Collection = "MODULE_mine-r39";             Cameras = "R39_01_PORTAL_APPROACH,R39_02_TUNNEL,R39_04_SHED_FRONT"; Exclude = "R40 | " }   # the mountain over the mine: being reworked (owner, 2026-10-18)
)
$MapFile = "sections/facility-assembly/combined/combined_map.blend"
$out_ = $OutRoot; $OutRoot = "$U"
if ($Map) {
    # Each room's map version is its ROOM_<room>_members collection, in the room's own frame; comparison renders still come from the room file.
    $Rooms = @($Rooms | ForEach-Object { @{ Room = $_.Room; Source = $MapFile; Collection = "ROOM_$($_.Room)_members"; Cameras = $_.Cameras; CompareSource = $_.Source; Exclude = $_.Exclude } })
    $Rooms += @{ Room = "map-connections"; Source = $MapFile; Cameras = ""; CompareSource = ""
                 Collection = "CONNECTOR_reactor_south_concourse,CONNECTOR_condenser_stair,CONNECTOR_condenser_escape,CONNECTOR_signs,EXTERIOR_evacuation" }
    $OutRoot = "$U/map"
}
if ($out_) { $OutRoot = $out_ }
if (-not $LogDir) { $LogDir = "$U/_logs" }
$Only = @($Only | ForEach-Object { $_ -split "," } | ForEach-Object { $_.Trim() } | Where-Object { $_ }); $Skip = @($Skip | ForEach-Object { $_ -split "," } | ForEach-Object { $_.Trim() } | Where-Object { $_ })   # -File passes "a,b" as one string
$names = @($Rooms | ForEach-Object { $_.Room }); $unknown = @(@($Only) + @($Skip) | Where-Object { $names -notcontains $_ })
if ($unknown.Count) { throw ("unknown room name(s): {0}. Rooms: {1}" -f ($unknown -join ", "), ($names -join ", ")) }
if ($Only.Count) { $Rooms = $Rooms | Where-Object { $Only -contains $_.Room } }
if ($Skip.Count) { $Rooms = $Rooms | Where-Object { $Skip -notcontains $_.Room } }
if (-not $Rooms) { throw "no rooms selected" }

# Check everything before the first bake: Blender, the device, every source pulled from LFS.
if (-not (Test-Path $Blender)) { throw "Blender not found at $Blender (pass -Blender <path to blender.exe>)" }
& $Blender -b --factory-startup --python-exit-code 1 --python "$U/check_device.py" -- --device $Device
if ($LASTEXITCODE -ne 0) { throw "device check failed for -Device $Device (see above). Not switching devices: report to the owner." }
$need = @($Rooms | ForEach-Object { $_.Source } | Select-Object -Unique)
if ($Map) {
    # the room files the map links (and the compare renders use); the map cannot bake a room whose library is still an LFS pointer
    $need += @($Rooms | Where-Object { $_.CompareSource } | ForEach-Object { $_.CompareSource })
    $need += @("$S/spawn-room/hero_suit.blend", "$S/condenser-bay/module_aaa_A1.blend",
               "sections/facility-assembly/exteriors/refinery/exterior-R01.blend", "sections/facility-assembly/exteriors/medical-reanimation/exterior-R04.blend",
               "sections/facility-assembly/exteriors/spawn-room/exterior-R05.blend")
    $need = @($need | Select-Object -Unique)
}
if ($Rooms | Where-Object { $_.Room -eq "spawn-room" }) { $need += "$S/spawn-room/hero_suit.blend" }
if ($Map -or ($Rooms | Where-Object { $_.Room -eq "turbine-room" })) {
    # the turbine rebuild's textures are external PNGs (LFS), not packed in its .blend: without them its maps bake magenta
    $png = @(Get-ChildItem "$S/turbine-room/rebuild/*.png" | ForEach-Object { "$S/turbine-room/rebuild/$($_.Name)" })
    if ($png.Count -lt 23) { throw "expected 23 turbine textures in $S/turbine-room/rebuild, found $($png.Count): git lfs pull --include `"$S/turbine-room/rebuild/*.png`"" }
    $need += $png
}
foreach ($f in $need) {
    if (-not (Test-Path $f)) { throw "missing $f" }
    if ((Get-Item $f).Length -lt 1024) { throw "$f is an LFS pointer: git lfs pull --include `"$f`"" }
}
New-Item -ItemType Directory -Force $LogDir | Out-Null
$PSExe = (Get-Process -Id $PID).Path     # the PowerShell running this script (powershell.exe on Windows), for each room

$t0 = Get-Date; $first = $true
foreach ($r in $Rooms) {
    $start = if ($first) { $From } else { "prep" }; $first = $false
    $log = if ($Map) { "$LogDir/map-$($r.Room).log" } else { "$LogDir/$($r.Room).log" }; $t = Get-Date
    $extra = @("-OutRoot", $OutRoot, "-Quality", $Quality)
    if ($r.Cameras) { $extra += @("-Cameras", $r.Cameras) }
    if ($r.Exclude) { $extra += @("-Exclude", $r.Exclude) }   # never an empty argument: Windows PowerShell 5.1 drops it and the child fails
    if ($Map) { $extra += "-Isolate"; if ($r.CompareSource) { $extra += @("-CompareSource", $r.CompareSource) } }
    Write-Host ("==== {0} (from {1}) started {2:HH:mm}" -f $r.Room, $start, $t)
    $ErrorActionPreference = "Continue"     # Windows PowerShell turns Blender's stderr lines into error records; with "Stop" the first warning would end the run
    & $PSExe -NoProfile -ExecutionPolicy Bypass -File "$U/bake_room.ps1" -Device $Device -Room $r.Room -Source $r.Source `
        -Collection $r.Collection -From $start -Blender $Blender @extra *>&1 | ForEach-Object { "$_" } | Tee-Object -FilePath $log -Append
    $code = $LASTEXITCODE; $ErrorActionPreference = "Stop"
    if ($code -ne 0) {
        $again = "-Device $Device" + $(if ($Map) { " -Map" } else { "" }) + $(if ($Quality -ne "home") { " -Quality $Quality" } else { "" })
        throw ("{0} failed; log: {1}. Resume after fixing with: bake_all.ps1 {2} -Only {0} -From <the stage that failed>, then the rest with: bake_all.ps1 {2} -Skip <the rooms already done>." -f $r.Room, $log, $again)
    }
    Write-Host ("==== {0} done in {1:n1} min" -f $r.Room, ((Get-Date) - $t).TotalMinutes)
}
Write-Host ("==== all {0} rooms done in {1:n1} h" -f @($Rooms).Count, ((Get-Date) - $t0).TotalHours)
