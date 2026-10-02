# Luna independent full-corridor review — F4

## Decision

**F4 is a meaningful visual improvement over F3, but it is not accepted.** Every category and every area remains below the strict >98 target. The central beige tile lane with blue margins now gives the route a visible hierarchy; the conditioning/extraction unit reads as connected to the overhead service path; and the new PPE/clean-stock rack makes the north corridor feel used. Those improvements help the long views. Spawn also uses smooth painted walls and some quiet fields; the gap is that its fields are organized by stronger threshold silhouettes, warmer/cooler color blocks, lockers, notices and human-use fixtures. F4 repeats the same cream upper wall, blue lower band, ceiling grid and restrained door palette through most areas without an equally clear functional hierarchy in the east turn and long service routes.

I opened all 19 F4 native-state images and the matching `RENDER_MANIFEST.json`, plus `closed-F4/E03_FREIGHT_LEAF.png` and its manifest. The full manifest binds the 1280×853, 32-sample images to `checkpoints/fuel_full_F4.blend`, SHA256 `dabe7628ee596e93df007326373cf9ef05776a657e59ca77755b1dabee0d7278`; all 19 image hashes match. The closed diagnostic uses the same native checkpoint and its image hash matches its manifest. The F3 score baseline and spawn reference remain unchanged. Technical/build checks receive no visual points.

The expanded tile pattern is a strong improvement in spatial hierarchy and material separation. It is also now a repeated graphic across several branches, so keep its use deliberate: the spawn reference varies its floor language by room and threshold rather than relying on a single grid everywhere. This is a refinement question, not a reason to undo the new route lane.

## Seven-category scores

| Category | F4 | F3 | Visible basis and remaining gap |
|---|---:|---:|---|
| Spatial composition and readability | 92 | 90 | The warm center lane and blue border clarify travel direction in `C01`–`C08`; the C02 overhead header visually joins the duct and wall unit. C01/C03/C05/C08 still share long, quiet wall planes, and the station labels often need the close views to read. |
| Modeling and fabrication detail | 92 | 91 | The connected service unit, mounted stock rack, carrier, bench, utility panel, freight drive, and door panels show credible assembled detail. The broad corridor architecture remains mostly shallow panel fields; F4's added detail is concentrated in a few fixtures rather than expressed in the bay silhouettes. |
| Materials and surfacing | 89 | 86 | The new tiled center lane, blue margin tiles, dark wall panels, orange safety parts and equipment improve separation. Most architecture still uses clean painted panels with little tactile variation, and the tile/grout rhythm repeats across multiple routes. Spawn offers more distinct wood, fabric, rubber, paper, PPE and strongly separated color zones. |
| Lighting | 86 | 86 | `C08` stock and `D06` service panel have readable local fixtures; `D05` drive remains clearly lit. Overall route lighting is still cool/neutral and flat beside spawn's warmer pools and stronger focal contrast. `D05` has a very bright task-light patch against a deep shadowed rail/guard assembly. |
| Environmental storytelling and asset diversity | 92 | 89 | The `C08` stock rack with folded cloth/clean supplies adds a useful human-use cue; `D02` remains a credible bench and `E01` a clear waste station. Story remains clustered: C07's clean-transfer sign and C08's supplies help, while the east turn and plant/reactor approaches have little visible evidence of ongoing use. |
| Professional finish and support contacts | 91 | 90 | The carrier/cradle, wheeled rack, bench, mounted utility fixtures, freight rail and leaf hardware read as supported. The new floor finish follows the visible thresholds and carrier berth cleanly; no clear support/contact defect stands out in these views. Render evidence still cannot prove hidden contacts or engine behavior. |
| Visual parity with spawn | 89 | 86 | F4's floor hierarchy and clean-stock rack bring stronger color and human scale. Spawn remains more composed at thresholds and richer in large-surface/material variation, props, signage, PPE and warm/cool lighting across the whole view. |

No category reaches the required >98.

## Nine area scores

| Area | F4 | F3 | Visible evidence and remaining gap |
|---|---:|---:|---|
| Entry / refinery | 91 | 89 | `C01_ENTRY`, `C02_PRIMARY_ROUTE`, `C03_HERO`, `C04_REVERSE`: new floor lane and C02's joined header make the approach clearer. C01 still clips the handover board at left and cuts off the new right-edge equipment; the wall spans above the blue band remain broad and repetitive. |
| Staging / bench / cask / utilities | 93 | 92 | `C03`, `C09`, `D01`, `D02`, `D03`: the carrier berth, cradle and restraints, staged workbench, pegboard tools, and brass/blue utility panel form the strongest cluster. New tile finish adds a defined work/travel zone. The materials and warm contrast still trail spawn; C03 also crops the left bench, though D02 supplies a dedicated bench view. |
| Freight gate | 92 | 91 | `C03`, `D05`, `E03`, and closed-pose `E03`: motor/bellows, attached task light, running channel and layered leaf panels are visible. The closed view confirms the actual door faces and inspection windows, while the normal open views appropriately hide the parked leaves. D05's dark, heavy lower rail still dominates part of the frame; its local light is bright and hard. The closed diagnostic does not validate a controller or continuous sweep. |
| East turn | 89 | 87 | `C05_EAST_TURN`: the tiled approach and blue edge treatment make the route turn clearer, and the orange gate remains a useful focal marker. The large near-left wall and long cream field on the right remain plain; the small wall box and distant portal do not yet give the corner a strong destination hierarchy. |
| Delivery / waste | 91 | 89 | `E01_WASTE_APPROACH`: orange paired leaves, `WASTE / S03` header, and the wheeled bin give this branch a clear job. The new floor finish integrates the threshold, but the approach still centers on a single gate and bin with little visible transfer workflow; the header is small at route distance. |
| Reactor adapter | 91 | 90 | `C06_REACTOR_THRESHOLD`, `D04_REACTOR_WIDE`: robust paired leaves, metal rails, raised panels and real glazed inspection apertures remain legible; F4 adds the floor boundary. The broad leaf faces and bare adjacent wall still dominate the wide view, with limited process context. |
| Bypass / recess | 91 | 89 | `C07_BYPASS`, `D06_SERVICE_RECESS`: floor zoning improves the approach and the recessed valve/panel/hose reads as an installed service fixture. The `CLEAN TRANSFER` plate uses dark ink on warm enamel, but its lettering is small in the wide C07 view. D06 is locally readable but dark around the edges and isolated from wider maintenance context. |
| Plant header | 91 | 89 | `C10_PLANT_HEADER`: the portal frame, paired blue leaves, viewports, overhead cable path and floor border create a coherent destination. Its label is small in the full route, and the quiet side walls leave the plant threshold too similar to the other framed gates. |
| North / clean corridor | 90 | 85 | `C08_SERVICE_JUNCTION`, `E02_CLEAN_APPROACH`: the stock rack, folded cloth and bottles make C08 more human and function-specific, and the blue/beige tile lane clearly leads to the end wall. E02's `CLEAN / S02` text is white on a dark plate but still shadowed and cropped at the top edge; C08's wide upper fields and long run remain visually generic. |

All nine areas remain below 98. Staging is strongest. East turn is weakest because the floor improves route legibility but the surrounding wall and endpoint are still under-articulated.

## F3 targets: F4 result

| F3 target | Result | Pixel evidence |
|---|---|---|
| Floor/material hierarchy | **Improved** | The beige central tile lane with blue margins is visible in `C01`–`C08`, `C10`, `E01`–`E03` and the object close-ups. It separates travel and edge zones and adds material contrast. Keep this hierarchy deliberate; the same grout grid now repeats broadly. |
| Connected conditioning and extraction | **Improved** | `C02_PRIMARY_ROUTE` shows the wall unit linked upward into a duct and joined by a broad overhead header, so the assembly reads as a system rather than an isolated box. It is a strong specific improvement, while the surrounding wall remains open and plain. |
| PPE rack and clean-stock/cloth/log cluster | **Improved** | `C08_SERVICE_JUNCTION` shows a foreground stock rack with folded cloth and bottles, adding a practical clean-corridor story. In this wide view the rack is partly cropped by the frame and the clean destination label remains weak; the story is present but not yet fully readable from the route. |
| Freight closed-leaf inspection detail | **Improved, visible effect** | The closed diagnostic shows the leaf surfaces, raised bars, handles, perimeter construction and circular glazed apertures. Compared with F3, F4 gives the faces more light and the glazing/brushed rings stronger highlights. The portal-mounted inspection hood sits above the top crop in E03, so the diagnostic does not show the hood itself; its intended face-lighting effect is visible. The native open state continues to hide the leaf faces in their pockets, which is not treated as missing geometry. |
| Branch wayfinding | **Improved, incomplete** | Floor colors establish the direction of travel; `E01` has a readable waste destination at close range, and C10/E02 identify plant/clean. The dark-ink `CLEAN TRANSFER` text on warm enamel in C07 is small at route distance, while the white-on-dark `CLEAN / S02` header in E02 is cropped/shadowed. Route-distance reading is still weaker than spawn's signs. |

## Highest-impact remaining corrections

1. **Use a few major architectural silhouettes to break the wall repetition.** Preserve the footprint and clear corridor lane. In `C03_HERO`, give the large service wall around the staging cluster a deeper, stepped process bay or a larger connected service cassette; in `C05_EAST_TURN`, strengthen the turn with a distinct portal/header silhouette that leads the eye into the orange gate. Do not fill the remaining blank wall with small props. This addresses the dominant route-scale gap visible across `C01/C03/C05/C08`.

2. **Keep the useful tile hierarchy tied to area transitions.** The beige lane and blue margins work, and the spawn reference shows that a repeated central tile lane can be an effective organizing element. F4's refinement is to vary where that lane widens, changes border, or terminates at functional thresholds—especially C05's turn and C10's plant door—so every branch does not have the same floor cadence.

3. **Make the two clean-route labels readable from their actual approaches.** In `C07_BYPASS`, increase the size/weight of the dark-ink `CLEAN TRANSFER` lettering on the warm-enamel plate; its color contrast is visible, but the letters are small in the wide view. In `E02_CLEAN_APPROACH`, move the white-on-dark `CLEAN / S02` plate down or light it so it is not cropped and lost in shadow. Keep the wording count restrained; the issue is distance readability, not absent signage.

4. **Balance the freight task light and expose enough rail support.** `D05_GATE_MECHANISM` now has a readable illuminated drive. Preserve that local fixture, soften its hardest patch, lift the shadow detail on the adjoining running rail/mount, and reduce the visual weight of the broad lower guard/channel so the motor, supports and travel path read as one assembly.

5. **Extend the clean-use story without crowding the corridor.** The C08 stock rack is a good addition. Keep it wall-side and legible in the wide framing; add a single clear clean-preparation/return point at `E02` or C08, with visible attachment/support and a distinct material accent. The bypass and plant routes need one similarly specific functional cue each, integrated with their existing fixtures rather than a generic scatter of props.

## Concrete remaining gap by rubric category

- **Spatial composition/readability (92):** distinguish the C05 turn silhouette from the standard bay, give C03's work wall a deeper focal feature, keep C01's route markers and clipped board visible, and place the E02 header inside the frame.
- **Modeling/fabrication (92):** carry the connected-system quality of C02 into one or two large structural/service assemblies in C03/C05/C08. Existing carrier, rack, door and panel details are strengths; refine the large shell shapes around them.
- **Materials/surfacing (89):** preserve the tiled lane and blue border, but vary its termination or border at meaningful thresholds rather than copying the same floor cadence through each branch. Smooth painted walls are appropriate; distinguish large bays through purposeful color/value grouping, materials on functional fixtures, and threshold structure instead of adding surface noise.
- **Lighting (86):** D05's motor task light is useful but too hard against deep rail shadow. Add controlled local bounce in D01/D02/D06 and C08, while keeping route lighting directional enough to show bay hierarchy.
- **Storytelling/diversity (92):** retain the clean-stock rack; make its contents and role readable in C08's full view, and add one specific use cue at the bypass and plant thresholds. Avoid cluttering the lane.
- **Professional finish/support contacts (91):** keep the visible cart, rack and bench support construction; confirm hidden contacts separately. The pale C03 carrier parking-berth lines are real floor markings and are no longer treated as a defect; make them legible only if players need to understand the parking function.
- **Parity with spawn (89):** give the east turn, long north route and plant approach a stronger functional focal hierarchy. Spawn also has quiet painted fields and smooth doors, but it breaks them with bold portal frames, notice boards, lockers, warm rooms, PPE and distinct tile borders; F4's cream/blue wall rhythm is less purposeful across C05/C08/C10. Strengthen those specific area transitions and warm/cool lighting changes rather than adding detail to every quiet wall.

## Evidence and limits

All 19 F4 renders and the matching manifest were opened and checked. The 19 image hashes match the manifest; the manifest and native checkpoint SHA are `dabe7628ee596e93df007326373cf9ef05776a657e59ca77755b1dabee0d7278`. The closed-pose `E03_FREIGHT_LEAF.png` hash also matches its manifest. Archived F4 build/cold files are separate technical records and are not used to award visual points.

The closed-pose file is a rigid-carriage diagnostic; the native scene remains open. It lets the leaf faces be visually assessed, but it does not establish the runtime controller, collision or continuous sweep. Concealed open-state leaf surfaces are intentionally hidden and are not penalized. Render views cannot establish hidden support contacts, gameplay traversal or the appearance from unrendered locations.
