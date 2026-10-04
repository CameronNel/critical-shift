# Critic A — whole-room cycle R04c

## Scope and evidence

I inspected all 21 R04c fixed-camera images individually and compared each against its R03 counterpart. The render manifest is complete, and its blend hash matches `validation_R04c.json`. Portal views follow the isolated-module contract: black beyond an opening is expected; I assessed the authored frame, jambs, threshold and approach. These scores cover editable Blender source only. They do not claim Unity runtime performance, collision or navmesh validation. Scores are normalized 0–100 per category, with rubric weights used for the weighted total. The final requirement remains at least 99 in every category with no vetoes.

## Category scores

| Category | Score / 100 | Weight | Basis |
|---|---:|---:|---|
| Layout, scale and route readability | 79 | 20% | The central route, bay boundaries, portals and loaded transfer cart remain readable. No sampled route obstruction is reported. The repeated bay rhythm still flattens zone hierarchy, and C08 does not clarify circulation around the extraction task. |
| Art direction, architecture and silhouettes | 65 | 20% | Formed cask covers and east-bay channel/corrugated construction improve the silhouettes. The east-bay panels read inconsistently as metal versus wood in different views, and broad walls/floor still feel clean and generic for the requested neglected mood. |
| Waste-process hero equipment and functional clarity | 70 | 15% | The casks, loaded cart and storage covers read more specifically. The quarantine filter is only partly visible above the lip, and the extractor's source-to-destination relationship remains unclear in C08. |
| Materials and anti-plastic quality | 72 | 15% | Corrosion is much more restrained than R02b/R03 and follows many rims and contact areas. Painted steel, metal hardware, plywood, rubber and paper have distinct responses. Some stains remain broad, and east-bay skin values/color make metal surfaces look timber-like in W07/C03. |
| Fixture-only lighting and gloomy atmosphere | 72 | 10% | The established practical-light pools retain useful contrast in the functional views; dark openings beyond module interfaces are expected. The mood is gloomy, but much of the surrounding wall and floor still reads maintained and evenly clean. |
| Purposeful dressing and human storytelling | 55 | 10% | A closed load on the cart, filter crown, repair gloves and overdue note add process/human evidence. Much of the room remains sparse; the filter's purpose is not obvious, the loaded cart has no visible restraint, and wall/floor wear does not yet convey long-term neglect. |
| Technical cleanliness, contacts and reproducibility | 88 | 10% | The 21-view manifest matches the validated R04c blend. Validation reports 474,128 evaluated triangles, 24 physical fixture pairs/21 active emissive surfaces, 310 new and 57 inherited contacts, six hollow-plenum cavity rays, 247 protected transforms unchanged, world 0, and no reported support/route/mesh issues. Cold-start remains pending. |

**Weighted total: 72/100** (71.6 before rounding). This candidate improves on R03 but is not close to the 99-point bar in any visual category. It is not accepted.

## Camera-by-camera comparison

| Camera | R03 → R04c pixel result |
|---|---|
| `C01_Entry` | The aisle is unchanged and clear. The right-hand storage fronts now show vertical channels and more specific folded panels; localized wear is quieter. Wall/floor paint and lane lines still look relatively fresh. |
| `C02_Casks` | Cask bodies are less broadly mottled and cover rims read more formed. Remaining lower-body/contact wear is plausible; large vessels still feel similar in shape and small identifiers recede. |
| `C03_Reverse` | Corrugated/channel east-bay construction is visible, but its warm brown horizontal faces can read as timber slats against the adjacent painted metal. Route layout and light are stable. |
| `C04_Route` | Route remains open and readable. The added side skin/channel details give the right-hand bay more structure, though the large faces still compete with repeated box silhouettes and clean yellow lane lines. |
| `C05_Transfer` | The cart now carries a closed canister, making its purpose and scale much clearer. It sits on the bed, but no clear strap or locking restraint reads from this view. The adjacent corrugated bin improves the backdrop while its brown/blue material relationship remains uncertain. |
| `C06_Dry` | The cap geometry is more specific and wear is reduced to the edge. The side bay panel now shows more structure, but the broad cover faces remain quiet slabs from this angle and the lower aisle-side area falls dark. |
| `C07_Quarantine` | The cover's formed return and edge damage read well. The filter crown now peeks above the bin wall, but almost all of its body remains hidden; this still reads as a small cap in a dark cavity, not clearly as a quarantined spent filter. |
| `C08_Extraction` | The access doors have more visible narrow inspection/detail elements and wear is reduced. The tall assembly still fills the frame without a clear source, extraction step and receiving path. |
| `C09_Inventory` | Inventory screen and desk are essentially unchanged and readable. The wider room context remains sparse and less worn than the task note implies. |
| `C10_Workbench` | The repair corner remains legible and locally lit. A small additional work item appears on the far-right bench, but the tool board and tabletop still feel neat and staged. |
| `W01_Personnel` | No meaningful change. Authored jambs and the approach remain visible; black beyond the opening is expected. |
| `W02_ReceivingReturn` | No meaningful change. The frame, threshold, floor approach and scan booth are readable; expected black beyond the module is not a defect. |
| `W03_Dispatch` | No meaningful change. The lintel/jamb frame and approach remain legible; the isolated black beyond the aperture is expected. |
| `W04_CellService` | Cask construction and service gauge remain readable. Wear is restrained to the lower/contact region, a clear improvement over the broad R02b pattern. |
| `W05_ReceivingExterior` | Receiving and the route are clear. The new side skins/channels give the bins stronger construction, though nearby panels switch between blue-green painted metal and brown horizontal faces that look wood-like. The closed cart load is visible. |
| `W06_PersonnelExterior` | The previously visible empty cart now carries a seated canister. The added load strengthens the process read; its hold-down/retention remains hard to identify at this distance. No change to the route or personnel frame. |
| `W07_DispatchExterior` | The route and isolated portal approach remain clear. The left-side bay's brown, strongly banded face looks like horizontal boards rather than folded steel, and the lane paint still feels new. |
| `W08_BoothDoor` | The inventory booth is unchanged and clear. Fine wall marks at far left are slight; broad wall surfaces still lack a convincing neglected surface history. |
| `W09_DrySouth` | Container lids retain their formed edges and more controlled rim wear. The wide lid faces remain pale and comparatively clean; the new side skin visible at left reads blue steel and is more convincing than the warmer faces in other views. |
| `W10_ResidueService` | Residue vessels are cleaner and corrosion is concentrated nearer rims and lower contact areas. Construction is legible, but repeated vessel forms still dominate over a residue-handling story. |
| `D01_SealRepair` | The gloves are fuller, with readable fingers and palm shapes, and the softened ring stain is less distracting. The repair materials are still neatly arrayed, but glove construction is a real improvement over R03. |

## Highest-impact corrections for R05

1. **Make the spent filter unmistakable in C07 while preserving closure clearance.** Raise or enlarge its visible body within the original envelope so the fixed camera sees a used filter form, not only a perforated crown. Keep it physically inside the bin and below the lid's closure sweep.
2. **Unify the east-bay material read.** The new ribs and channel frames improve construction, but C03/W07's warm horizontal bands look like timber beside blue-green sheet metal in C01/C05/W05/W09. Establish one believable folded/corrugated steel family with consistent color, edge response and visible returns, while preserving the existing room envelope and route reservations.
3. **Show how the transfer load is held.** The cart load is now visible in C05/W05/W06. Add a clearly readable cradle, chock or strap that explains its restraint and contact from those fixed views without crossing the lane.
4. **Clarify the extraction sequence in C08.** Make the incoming source, extractor mechanism, inspection state and receiving/containment connection read as one operation at this camera. Preserve the functional root positions and existing routes.
5. **Carry neglect across the architecture.** The casks and bins now have more restrained localized wear, but broad walls and lane paint remain clean. Add authored wall spalls, lower-wall deterioration and seepage, plus faded route marks and plausible wheel rubs. Keep the marks localized and readable; avoid returning to blanket noise.

## Bounded technical evidence

The R04c manifest is complete for all 21 fixed views and its source SHA matches the validation blend hash. The validation PASS reports the stated source-side transform, fixture, support, route, mesh and hollow-plenum checks. Those checks do not establish cold-start behavior or Unity runtime performance, collision or navmesh. The validator explicitly limits its anchor and lane rays to samples, not exhaustive collision certification.
