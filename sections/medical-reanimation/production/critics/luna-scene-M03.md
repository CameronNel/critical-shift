# Independent Luna pixel review — Medical/Reanimation M03

Reviewer: Luna (independent)

Reviewed all fourteen actual M03 Blender renders in `production/renders/review/M03`: ten fixed cameras (`CAM_*`) and four workflow cameras (`W01_ENTRY_OUTSIDE`, `W02_CART`, `W03_SUPPLIES`, `W04_REAR_SERVICE`). Compared against approved M03 whole-room guidance, M04 OCRU assembly guidance, M05 rear-service guidance, and the preserved R09 layout.

This is a pixel review. Geometry/state/contact scripts are considered supporting evidence where available, but final state and cold-start evidence are still pending. Host gameplay implementation is not required for this room-art review; any runtime, physics, navmesh, or host-hook claim that is not visible in the images remains unverified.

## Decision

**M03 scene: FAIL.** This is a real improvement over M01: the chamber is darker and more constructed, the palette remains strictly no-teal, the body cart is represented in the workflow set, and the decon now has a used-PPE bin. The scene still falls short of the strict greater-than-90 gate. Repeated softened box construction, under-resolved material families, broad even lighting, label obstruction, weak rear-service specificity, and incomplete state/contact evidence remain visible.

## Independent eight-category scores

| Category | Score /100 | Gate |
|---|---:|---|
| Scale / circulation | 86 | **FAIL** |
| Shape / art direction | 82 | **FAIL** |
| Hierarchy / gameplay readability | 84 | **FAIL** |
| Materials | 83 | **FAIL** |
| Lighting | 85 | **FAIL** |
| Color discipline / no-teal | 96 | Pass |
| Environmental storytelling | 86 | **FAIL** |
| Technical correctness / evidence | 78 | **FAIL / incomplete** |

Strict gate result: **FAIL**. Every relevant category must be strictly greater than 90; the no-teal pass cannot compensate for the other categories.

## Pixel evidence by category

### Scale / circulation — 86

CAM_ENTRY, CAM_ROUTE, CAM_REVERSE, and W01 show a believable adult-scale room with a broad central apron, a large OCRU opening, rear process wall, east recovery position, and clear decon threshold. W02 shows a full stretcher/cart with casters, scissor support, handles, and a continuous deck. The M04 transfer relationship is now more plausible in the chamber than in M01.

The pack still does not show a loaded ragdoll or a cart actively aligned to the transfer bridge. W02 isolates the cart against a wall, and the wide views do not show the southwest parking state clearly enough to establish the complete retrieve → decon → load route. Recovery transfer and simultaneous rear-service clearance remain image-unproven. These are room-art evidence limits; no relocation is recommended.

### Shape / art direction — 82

The M03 OCRU is darker and more legible than M01. CAM_HERO/CAM_PINCH show a continuous berth, orange restraint straps, supported rails, dark stacked supports, interior task lights, side service housings, and an opening with depth. The console and cartridge rack have clearer silhouette grouping, and the decon bin/fixture have more purpose.

The scene still reads as a family of softened slabs and rectangular housings. M04’s distinctive folding transfer bridge, rolled shutter/gasket track, capped receiver, guarded emergency release, adjustable cradle, and removable service panel are only partially translated. The console controls remain three beveled blocks on a white top. The recovery cot, supply bench, reserve cabinet, and cabinet cases use the same broad box language. The M03 concept target is more specific and layered than these final pixels.

### Hierarchy / gameplay readability — 84

The room sequence reads quickly: OCRU left, restart center, cartridge rack and decon rear, supplies and recovery right. CAM_ROUTE is the clearest process overview, and CAM_HERO makes the OCRU interaction area findable. The dark chamber and orange floor/process marks improve focal separation over M01.

The rear wall remains too equal in value. The large `RESTART STATION` banner competes with the actual controls, while wide cameras reduce the lower console labels and cartridge detail to marks. The label mounting stems visibly cross or obscure `INSERT`, `SUIT`, and `RELEASE` in CAM_ENTRY/CAM_HERO/CAM_ROUTE. The recovery and decon masses remain quiet enough to disappear instead of reading as purposeful secondary stations.

### Materials — 83

M03 separates graphite console/chamber surfaces, light painted shell, dark rubber-like hoses and pads, orange functional trim, glass cabinet panes, and metal rails better than M01. CAM_MATERIALS shows a more controlled reserve cabinet; CAM_PINCH shows dark berth pads and rails; W02 shows caster and scissor hardware.

The dominant response is still smooth painted plastic/satin across walls, equipment, floor, and recovery furniture. Concrete/plaster, painted metal, rubber, glass, and fabric do not separate strongly enough at gameplay distance. The recovery cot remains almost entirely bone/cream and reads like a hospital slab. CAM_W03 supplies are uniform pale boxes, and the rear cabinet/rack surfaces lack the tactile material breakup shown by M04/M05. Localized wear is sparse. This is a material-family failure rather than a color failure.

### Lighting — 85

M03 improves local contrast over M01. Dark ceiling beams and the OCRU interior provide depth; practical wall strips and chamber task lights are visible; contacts under the console, stool, cot, cabinet, and cart read. W01 and CAM_ENTRY hold a readable room exposure, and the chamber uses neutral white light without teal/cyan contamination.

The hall is still broadly and evenly exposed by the overhead grid. CAM_ROUTE and CAM_REVERSE have weak separation between wall, floor, and secondary stations; CAM_DECON is flat around the hose and bin; CAM_RECOVERY is low in material/light contrast. The OCRU interior is sometimes so dark that its construction details collapse into a few bright rails. The M05 rear-service pool and controlled falloff are not yet reproduced at room level.

### Color discipline / no-teal — 96

No teal or cyan appears in the M03 room, chamber, monitors, or practical lights. Graphite, bone/steel, neutral grey, orange controls/trim, and restrained hazard marks follow the explicit user override and the approved M03/M04/M05 guidance. Orange is concentrated on interaction hardware, cart handles/straps, floor route markings, and small functional edges.

The deduction reflects the over-heavy pale base and underdeveloped secondary value blocks, not a teal violation. Keep the no-teal/no-cyan rule intact.

### Environmental storytelling — 86

M03 now includes a used-PPE bin in decon, cartridge rows with shelf labels, a reserve cabinet/gauge, a shift-log workbench, stocked glazed storage, a cart, and a transfer floor marking. CAM_CONSOLE’s `POWER / READY`, `SUIT / PARKED`, `CARTRIDGE / WAIT`, `CHAMBER / OPEN`, and `AWAITING TRANSFER` cues connect the room to the chapter 5 procedure. The room reads as active employee infrastructure.

The procedure remains mostly a lineup of stations. The cart is not shown in the arrival-to-OCRU sequence, the decon hose/fixture connection is visually ambiguous, and no subject is present in the transfer system. The console’s lower labels are too small to carry interaction meaning, while `RESTART STATION` supplies more signage than physical construction. Recovery has little worker-use evidence and remains close to a generic medical cot.

### Technical correctness / evidence — 78

The pack contains all fourteen expected renders at consistent dimensions. Camera placement is player-height, the entry and workflow views are present, major equipment appears supported by floors or frames, and the new state/contact scripts provide useful supporting checks. The monitor/state wording and physical control grouping are visible enough to guide host-facing state poses.

Final state and cold-start evidence are not yet complete. Pixels do not prove collision/navmesh, loaded-body/cart obstruction, host authority, interaction transitions, or recoverable failure states. The label-stem occlusion and tiny console labels are visible technical/readability defects. In CAM_DECON, the hose and wall fixture do not yet read as a confidently connected service assembly. This score deliberately separates available evidence from unverified runtime claims.

## View-by-view pixel scores

These are overall view-read scores for each image, not substitutes for the eight-category gate.

| View | Score /100 | Pixel read and limiting defect |
|---|---:|---|
| CAM_ENTRY | 84 | Complete room read with OCRU, process wall, decon, cabinet, recovery, and route. Pale values flatten the hierarchy; `INSERT`/`SUIT`/`RELEASE` mounting stems obscure labels; no staged cart/body. |
| CAM_REVERSE | 82 | Entry portal, OCRU depth, east work area, and broad floor read. Rear wall remains under-detailed and quiet; no transfer or body evidence. |
| CAM_ROUTE | 85 | Strongest process overview with console, cartridges, decon bin/hose, cabinet, and OCRU edge. Lower console labels are tiny; station construction still reads as repeated boxes. |
| CAM_HERO | 85 | Darker OCRU chamber, supported berth, rails, straps, side panels, and service hose read. `INSERT`/`SUIT`/`RELEASE` labels are partially obscured; M04 transfer/receiver details remain incomplete. |
| CAM_CONSOLE | 82 | Monitors and three guarded controls are findable. Lower labels are too small/soft, controls remain simple blocks, and the oversized banner dominates the panel. |
| CAM_DECON | 79 | Used-PPE bin, grate, shower, and wall hose are visible. Hose/fixture endpoints read ambiguously; stall remains flat and under-constructed. |
| CAM_MAINT | 78 | Decon bin/hose and supply cabinet materials are visible. No strong maintenance access read; the camera is dominated by blank panel and cabinet faces. |
| CAM_MATERIALS | 82 | Reserve gauge, handle, fasteners, graphite panel, and light shell show some separation. Surfaces remain smooth satin with limited concrete/rubber/fabric distinction. |
| CAM_PINCH | 84 | Continuous berth, dark pads, orange straps, rails, and stacked supports are clearer than M01. The chamber back is broad and featureless; service/receiver details are not fully legible. |
| CAM_RECOVERY | 78 | Cot, rails, pad, and floor contact read. All-bone materials and sparse use evidence create a hospital/morgue-like read; hierarchy is weak. |
| W01_ENTRY_OUTSIDE | 86 | Entry frame and whole-room composition are clear; orange transfer marking and route improve the read. Cart/body transfer is still absent and rear stations are small. |
| W02_CART | 83 | Complete cart with casters, scissor frame, handles, deck pads, and contact shadow. It is isolated from the OCRU; no body, bridge engagement, or route proof. |
| W03_SUPPLIES | 81 | Sink, supply bench, sealed cartons, cloth/paper cues, and lower shelf are visible. Uniform pale boxes and broad blank wall reduce specificity. |
| W04_REAR_SERVICE | 86 | Console edge, labelled cartridge rack, glazed cabinet, decon opening, and used-PPE bin form a coherent rear-service view. Console controls are cropped; rear power/maintenance distinction remains weak. |

No individual view clears 90 as a complete visual-read proof, and no view proves runtime/physics behavior.

## Prioritized corrections

1. **Translate the M04 OCRU component study into the actual scene.** Make the shutter/gasket track, supported transfer bridge and cart interface, adjustable cradle, suit-service coupling, capped cartridge receiver, guarded release, and removable service panel visibly distinct in the fixed cameras. Preserve the inherited footprint and berth orientation.

2. **Fix known interaction-label occlusion and scale.** Remove the mounting-stem interference over `INSERT`, `SUIT`, and `RELEASE`, and make the console’s lower labels readable at the player camera. Keep labels subordinate to the constructed controls and canonical OCRU naming.

3. **Separate material families.** Reduce the universal satin/cream response and give painted metal, graphite, concrete/plaster, rubber, glass, and fabric visibly different roughness and edge behavior. Add localized, authored wear at handles, cart routes, kick plates, and service contacts; avoid photographic grunge.

4. **Correct the decon assembly read.** Make the hose, fixture, wall plate, nozzle/holder, grate, and used-PPE bin read as one connected gross-decontamination system. The current hose/fixture relationship is visually ambiguous in CAM_DECON/CAM_MAINT.

5. **Strengthen lighting hierarchy.** Keep neutral OCRU task light and no-teal color; add practical pools and falloff so OCRU is the landmark, rear service is a readable work zone, and recovery/decon remain distinct secondary stations without flat overhead exposure.

6. **Make the room’s procedure visible as a connected sequence.** Show the cart/transfer relationship, decon-to-load relationship, service/power/cartridge controls, monitored state, and recovery handoff through the existing fixed-camera set. A loaded body and obstruction tests remain separate validation evidence.

7. **Complete evidence after the visual pass.** Finish final state, support/contact, obstruction, host-hook, and fresh-process cold-start records. Treat the existing scripts as partial supporting evidence, not a final technical pass.

## Final review status

M03 is rejected at the strict >90 scene gate. M03/M04/M05 remain approved concept guidance; the actual scene has not yet reached their construction, material, lighting, or rear-service specificity. No layout change is requested. The next review should re-render all fourteen views after the listed corrections and keep technical evidence clearly separated from pixel scores.

