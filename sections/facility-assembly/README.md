# Critical Shift — assembled facility A04

> **Current full-map entrypoint: [MAP.md](../../MAP.md) and [MAP.json](../../MAP.json).** Use `blender/facility_spawn_concept02_R17.blend` for editing the entire map, or its R17 material preview for inspection. The A04 description below is retained as history; connectors, exteriors and subsequent whole-map work now exist.


Open **[blender/facility_master.blend](blender/facility_master.blend)**. This is the actual master scene containing twelve linked room modules at their original metre scale. Keep this entire section folder together: the master uses relative links into `sources/`.

**Connecting structures are deliberately unbuilt.** Dashed guides reserve routes; outlined volumes reserve stairs/lift, utilities and external aprons. They are planning annotations, not walkable floors or finished architecture. Toggle the named planning collections independently of `01_LINKED_ROOMS`.

![Facility plan](production/FACILITY_PLAN.png)

## Flow decisions

- **Production:** existing descending mine/adit → refinery's existing nine-stage room → existing fuel-corridor module → reactor. Refinery intake and dispatch use opposite existing ports; no duplicated processing rooms or invented mine lift.
- **Power:** reactor → turbine → electrical → waste forms the eastern wing. The condenser is one level below the turbine at the exact section-contract offset; its U04 centre is aligned in the master.
- **Clean and rescue:** spawn, medical and compliance connect through a distinct clean header. Medical is a short branch off that header, not behind waste or freight inspection. Compliance has a bent, reservable controlled approach and an outward-facing arrival apron.
- **Recovery:** a western maintenance route reaches cooling; eastern and southern crossovers form alternate loops. Players can reach power/recovery areas without traversing the entire fuel-handling path. No new room-wall opening is assumed.
- **Reserved construction:** 21 labelled routes, usually 4–6m wide, plus a 5.5×10m condenser access footprint, separate overhead utility allowance, dock arrival apron and waste dispatch apron. Existing narrow portals remain bottlenecks; future connectors must taper and preserve door pockets and cart turning clearances.

## Spec and measurements

The layout follows canonical `GAME_SPEC.md` sections 23.1–23.4 (production geography, travel targets, alternate routes, modularity), 4.2/4.5 (movement and body carrying), and the recovery/compliance requirements. Canonical art direction and the headless-first build protocol were read before placement. The accepted descending mine supersedes the legacy list's mine-lift wording.

The current planned route graph is connected. Its conservative planned longest path is **248.5m**, about **55.2 seconds at an assumed 4.5m/s**. At 4m/s it is **62.1 seconds**. The engine controller is not measured here; meeting the under-60-second target requires about 4.142m/s on these planning paths. Loaded carts use the fuel corridor's inherited 1.5m/s planning assumption and take longer. Room-internal paths are planning centre-lines, not a fresh navmesh or collision-certified walkthrough. Door operation, carrying, interaction time and the actual connecting structures must be tested in-engine before claiming perfect flow.

Source geometry was surveyed before placing rooms. `production/LAYOUT.json` records every transform, endpoint, width and reservation. `production/PLAN_AUDIT.json` records the conservative 0.25m player-height screen. A01/A02 routing failures are preserved under `production/checkpoints/`; A04 has no remaining reservation-clearance candidates outside the disclosed endpoint transition zones.

The broad bounding-box screen flags the **intentional turbine/condenser stacked interface**. This is not reported as zero mesh overlap: curved pipe bounding boxes overestimate occupied volume, and the upper U04 receive intentionally enters the turbine interface. The exact U04 centre match is verified separately on cold load. Final slab, collar, utility and cap mating remains connection-detail work; no source geometry was cut to hide a conflict.

## Sources and preservation

`production/SOURCES.json` identifies all twelve originals, selected delivery commits/hashes and the mutable-file hashes observed at assembly time. Accepted Git bytes are used for cooling, turbine, electrical, waste, medical and fuel corridor. Newer mutable edits are preserved in their original worktrees. The current authoritative mine, refinery, reactor, spawn, compliance and condenser files were frozen by hash. Spawn retains its recorded unfinished art-review status; layout inclusion is not a new art pass.

Each `sources/<room>/accepted.blend` is byte-exact. `module.blend` is a portable wrapper prepared from that input: geometry transforms remain unchanged, dependencies are packed, and one named export collection is added. The reactor's 100×100m **`RF outdoor sky proxy`** is disabled only in its assembly copy because it is a room-presentation background, not facility architecture. No original room file was edited.

## What remains deliberately open

1. Build the reserved corridors, junctions, stair/lift access and external approaches. Dimension transitions against the actual door widths and moving leaves; reserve turning/landing pockets at bends.
2. Resolve source boundary closures as part of connector integration: reactor fuel/cooling doors, the mine's far continuation door, the condenser receiving closure and applicable controlled doors. They remain visible and intact here.
3. Finish U04 slab/hood mating; coordinate turbine-owned U02 cap action. Bind CW, steam, condensate, power, drainage and ventilation to actual remote sockets. Local ports are not functioning facility networks.
4. Implement Unity import adaptation, collision, navmesh, interactions, door states, lighting, visibility/LOD and performance work; time actual player/cart/body routes.

This delivery is **spatial assembly with construction allowances**, not a finished connected or playable map.

## Replay

Run from a copied section folder using the supplied scripts:

1. `blender/collect_sources.py` — freeze source inputs (requires the documented original worktrees/Git objects; refuses hash drift).
2. Blender background `--factory-startup --disable-autoexec --python blender/prepare_modules.py` — prepare portable module collections.
3. Python `blender/plan_layout.py` — write the versioned layout.
4. Blender background `--factory-startup --disable-autoexec --python blender/build_master.py` — rebuild the linked master.
5. Python with NumPy/Pillow `blender/audit_plan.py` — produce the conservative screen and plan sheet.
6. Blender background `--factory-startup --disable-autoexec --python blender/review_master.py` — cold-check linked sources/transforms/dependencies and render three layout views.

GPU review jobs use the shared `gpu_gate.py`, owner `astra-facility-assembly`; no lock was deleted. Workbench evidence is for layout/readability, not replacement scoring of the rooms' original lighting/materials. The source assets retain their authored materials and lights.

Workspace: `C:/Users/Camer/Games/critical-shift/worktrees/facility-assembly-astra`. Branch: `codex/facility-assembly-20260912`. Only `sections/facility-assembly/` is authored by this assembly pass. No main merge.
