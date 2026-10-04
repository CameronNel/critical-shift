# Critic A — whole-room cycle R02b

## Scope and evidence

I inspected all 21 individual R02b images and compared each to its R01a camera: C01–C10, W01–W10, and D01. The render manifest is complete and its source hash matches `validation_R02b.json`. For portal views I follow the clarified isolated-module scope: black beyond a contract opening is expected; I judge the authored jambs, threshold and approach. Category scores are normalized 0–100; the rubric weights apply to the weighted total. The final requirement remains at least 99 in every category with no vetoes.

## Category scores

| Category | Score / 100 | Weight | Basis |
|---|---:|---:|---|
| Layout, scale and route readability | 78 | 20% | The central lane remains clear and the portal approaches and jambs are now more visible. Transfer and storage equipment are easier to read. The isolated black beyond openings is not penalized; some close service views still hide useful details and the space is visually repetitive. |
| Art direction, architecture and silhouettes | 58 | 20% | Casks, the crane, cells and transfer cart have strong industrial silhouettes. Broad flat container lids and repeated module shapes remain, and blanket speckled corrosion overwhelms the authored forms. |
| Waste-process hero equipment and functional clarity | 66 | 15% | Cask identity, inventory station, transfer cart and quarantine container are clearer. Extraction still reads as a stack of machinery without an obvious material path, and the quarantine payload is not clearly visible. |
| Materials and anti-plastic quality | 49 | 15% | Local lighting reveals metal, painted surfaces, rubber, paper and wood more clearly, but the new orange-white speckling blankets large surfaces. It reads as procedural noise rather than localized corrosion and makes the lids/collars and cask bodies less believable. |
| Fixture-only lighting and gloomy atmosphere | 75 | 10% | The real bay fixtures improve local contrast across the room while retaining a dark mood. Functional surfaces, route edges and portal thresholds are substantially more legible than R01a. Some corners remain very dark and fixture pools still feel broad/flat in close service views. |
| Purposeful dressing and human storytelling | 47 | 10% | The repair bench, overdue note, gloves and inventory papers tell useful stories. Other zones remain sparse and orderly; the quarantine view has no clearly readable spent payload, and the repair gloves still read as flat silhouettes. |
| Technical cleanliness, contacts and reproducibility | 86 | 10% | The complete 21-view manifest matches the validation blend hash. Validation reports world 0, 247 protected transforms unchanged, 24 fixture/lens pairs passing, 276 new and 57 inherited contacts passing, zero unregistered supports/route obstructions/issues, and 152 closed-mesh checks passing. Cold-start behavior remains unverified. |

**Weighted total: 65/100** (65.25 before rounding). Every category remains well below 99; this is not visual acceptance.

## Camera-by-camera comparison

| Camera | R01a → R02b pixel result |
|---|---|
| `C01_Entry` | Additional practical pools lift the bays and make storage details more legible; the clear aisle remains. The right open lid and several adjacent broad surfaces now carry distracting orange-white speckle. The black beyond the far dispatch opening is expected for this isolated module. |
| `C02_Casks` | Cask hardware and surfaces are better lit, but rust speckle now blankets the vessel bodies, collars and plinths. This is the clearest example of damage overwhelming the hero silhouette and reading as a texture overlay. |
| `C03_Reverse` | The added side lighting opens the formerly murky reverse view and reveals the room's bay rhythm. Cask/cell surfaces at the edges show the same broad mottling; route and threshold remain clear. |
| `C04_Route` | The aisle and side equipment read better under the relighting, with no apparent lane obstruction. The right open lid's speckling pulls attention out of the route hierarchy. The far isolated opening's black interior is not scored as a missing neighbor. |
| `C05_Transfer` | The cart is now visible as a transfer unit, including its platform, rails, wheels and front label; this is a strong improvement over R01a. The large equipment bay behind it is still visually quiet, so the transfer relationship to the containers could be clearer. |
| `C06_Dry` | Added illumination makes the bin fronts, rails and wall readable. Broad speckling across all large lids and front panels is much too uniform and high-contrast; flat lid construction remains obvious. |
| `C07_Quarantine` | The open lid and container are easier to read, but the lid and box are heavily mottled. The interior is dark and no quarantined item reads clearly in this image, so containment purpose depends on the label rather than visible contents. |
| `C08_Extraction` | Little visible change from R01a. The side view remains dimmer and less legible than the improved storage views; vertical machinery, housing and controls do not explain the extraction or material path at a glance. |
| `C09_Inventory` | The workstation/list screen is brighter and more readable; the dose meter and shift log remain clear. This is a useful improvement with no major new visual regression. |
| `C10_Workbench` | The workbench retains a clear local task-light pool and readable seal-service tools. It is largely unchanged; the tabletop and tool arrangement still feel clean and staged relative to the rest of the run-down room. |
| `W01_Personnel` | The relit portal face, jambs and threshold are now distinct. Black beyond the opening is expected at this module boundary; the authored approach reads. |
| `W02_ReceivingReturn` | The receiving frame, jambs, threshold marks and adjacent scan booth are much clearer. The black beyond the contract opening is expected and is not scored as missing content. |
| `W03_Dispatch` | A new local pool reveals the surrounding wall and door jambs; the approach is clearer. The opening remains black beyond the module, as expected. The large simple bulkhead/frame still lacks specific hardware detail. |
| `W04_CellService` | Gauge and seal details are easier to read, but the cask body and collar are covered in speckled corrosion. The main body surfaces now look noisier and less materially controlled than R01a. |
| `W05_ReceivingExterior` | The receiving scanner, open approach and central route are better lit, and the cart is visible on the right. The far opening remains an expected isolated-module black. Open lids and broad rust speckle remain visually loud. |
| `W06_PersonnelExterior` | Added practicals improve door and room legibility; the booth and waste bays are easier to distinguish. The cart/table cluster still crowds the lower-right composition, though it does not visibly block the main approach. |
| `W07_DispatchExterior` | The route lines and door approach are brighter and clear, while the far isolated opening stays black. The opened lid at left and cask collars at right are overrun by the same orange-white pattern. |
| `W08_BoothDoor` | The inventory station and glass booth read better under increased local light. A bright wall hotspot at upper right is slightly attention-grabbing, but smaller than the corrosion and process-readability issues elsewhere. |
| `W09_DrySouth` | Increased light reveals container fronts and rails, correcting R01a's lost detail. Speckle covers nearly every lid and side panel and is the dominant read; the formed-lid construction still appears like a flat slab on a box. |
| `W10_ResidueService` | The residue vessels remain recognizable and now show mottling across bodies, collars and support plates. Damage is not confined to exposed rims/joints, so the surfaces read uniformly neglected rather than plausibly corroded. |
| `D01_SealRepair` | Essentially unchanged from R01a: the seal task is clear, but the work gloves still have flat, stiff silhouettes without convincing hand volume or finger folds. The bench cluster remains neat and the table grain regular. |

## Highest-impact corrections for R03

1. **Confine corrosion to physically plausible rims and joints.** Remove broad, repeated speckling from cask bodies, large lids and support plates. Keep corrosion at exposed seams, damaged paint edges, fastener pockets and leak/contact points, with scale and color variation that follows the construction. This is currently the largest art-direction regression.
2. **Give dry/quarantine lids folded construction.** Their broad, flat slabs dominate C06, C07 and W09. Form a believable sheet-metal lid with returns, stiffening, hinge/seal details and localized wear so the silhouette works even without a texture. Make the quarantine opening reveal its actual held filter or waste item clearly below the lid clearance.
3. **Clarify extraction and material movement in C08.** The added room lighting has not solved this camera's functional hierarchy. Make the connection from source vessel through extraction equipment and onward to containment visually traceable; keep controls and key junctions in readable local light.
4. **Give PPE and repair evidence believable volume.** D01's gloves still read as flat shapes at close range. Add palm/finger volume and broad fabric folds, with a contact shadow and wear that match the task. Disturb the staged bench contents only enough to suggest actual use.
5. **Keep the R02 local-light gains without flattening the mood.** The portal and work/service views now hold much more useful detail. Preserve this fixture-only hierarchy, then check low-value areas and wall hotspots camera by camera. Do not solve dark material loss with world fill or broad invisible sources.

## Bounded technical evidence

`validation_R02b.json` reports PASS and identifies the R02b checkpoint. It records 24 passing fixture/lens pairs, 276 passing new contacts and 57 inherited contacts, no unregistered new supports, route obstructions or issues, and 152 passing closed-mesh checks. The report also records zero world strength and the 247 protected transforms unchanged. The R02b render manifest is complete for all 21 required cameras, and its source hash equals the validation blend hash. These results support technical reproducibility for the stated checkpoint, not cold-start or runtime certification. The validator notes that registered anchor and lane rays are samples, not exhaustive collision certification.
