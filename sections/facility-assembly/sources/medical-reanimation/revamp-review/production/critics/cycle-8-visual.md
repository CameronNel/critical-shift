# Cycle 8 — independent full-room visual review

**FAIL — 76.9/90 visual points. Technical 10 points remain unscored.** All 24 labelled images were opened and inspected at their actual 1067 × 600 pixels, after the manifest reported `complete: true`. The four spawn calibration renders were also inspected. No prior critic reports, acceptance scores, implementation or source code were read; no scene/source edits were made.

The room preserves a coherent central route and achieves the bleak institutional mood. The single red bed practical, warm clinical workbench and restrained cool working-zone emphasis form a clear hierarchy. Where light reaches them, bed rails/lifts, linen, guarded controls, monitor housings and clinical tools show grounded stylized construction close to the spawn calibration. There is no dominant toy-plastic, generic primitive, repeated-bevel-box or texture-noise veto.

Acceptance is blocked by readability. The transfer-cart camera is essentially black; the reverse entry destination, OCRU side interfaces, reserve-power assembly and right cabinet leaf cannot be assessed or used clearly. These require a local light/occlusion diagnosis, not another whole-room asset replacement. Preserve the dark mood while restoring minimal form and material cues.

## Visual rubric

| Category | Score | Threshold (85%) | Gate |
| --- | ---: | ---: | --- |
| Layout / route readability | 18.2/20 | 17 | PASS |
| Art direction / silhouettes | 17.6/20 | 17 | PASS |
| Hero objects / focal clarity | 12.1/15 | 12.75 | FAIL |
| Materials / anti-plastic | 13.2/15 | 12.75 | PASS |
| Lighting / atmosphere | 7.0/10 | 8.5 | FAIL |
| Dressing / worldbuilding | 8.8/10 | 8.5 | PASS |

**Layout / route readability:** The preserved compact room reads as a central circulation strip between the OCRU bay and recovery/workbench wall. Entry and rescue-route views preserve functional grouping and open floor; the dark entry door limits reverse navigation clarity, without evidence of a changed room boundary.

**Art direction / silhouettes:** Authored bed rail, lift, layered monitor housing, guarded switch, cartridge dock, folded basin and clinical-prop forms meet the grounded stylized direction in the views where they are visible. No dominant repeated-bevel-box, low-poly toy, decorative sci-fi or texture-noise veto is present. The bag remains overly flat and rigid in its inspection view.

**Hero objects / focal clarity:** The red berth is the clear room focal point and the restart station is readable. The cart cannot be assessed from its nearly black required frame; OCRU side interfaces, reserve-power assembly and the right cabinet leaf lose sufficient form and material detail to block their hero gates.

**Materials / anti-plastic:** Visible clinical linen, dark gloves, paper, painted blue/red housings, steel rails, tiles and glass have distinct broad responses. Most major assets avoid generic gloss. Shadow suppresses separation in several functional assemblies; the hidden bag top and straight edge bands read rigid despite the visible zipper and handles.

**Lighting / atmosphere:** Single red bed practical, warm workbench light and restrained cool working-zone emphasis establish bleak hierarchy. Several required focal views exceed useful darkness: entry construction and side interfaces vanish, reserve power is displaced by adjacent brightness, and the transfer-cart frame is essentially unreadable. Darkness/possible occlusion is not evidence of acceptable asset fidelity.

**Dressing / worldbuilding:** The denied-release shift log, continuity graphic, sparse procedure signage, clinical working props and localized wash-area decline support institutional hopelessness without random clutter. The tiny note stays unobtrusive and a closed zipper/handles are confirmed under inspection fill. Bag fabric refinement would strengthen the concealed story object.

## Blocking defects and repair order

**V8-01 — critical.** HERO_CART; Entire image above the label. The required transfer-cart subject is essentially unavailable in the black render. Diagnose fixed-camera occlusion versus light reach in a disposable process; restore a minimal readable cart silhouette and material/construction read while preserving the established mood. Rerender the same fixed view. Limit: No visual judgment of cart fidelity or support is possible from this frame; this does not establish the technical cause.

**V8-02 — blocking.** REVERSE, WALL_SOUTH; Centre entry door/header; REVERSE x335–637/y178–414; WALL_SOUTH x325–638/y195–464. Door leaves, frame relationship and institutional identification disappear into black. Use restrained reflected/edge fill on the entry leaf and frame so destination and construction read; retain the red and warm practical hierarchy, without a global exposure increase. Limit: Rendered clarity is assessed; no route width or collision clearance is certified.

**V8-03 — blocking.** HERO_OCRU, WALL_WEST, HERO_RESERVE, HERO_CABINET; OCRU side interfaces; reserve assembly x212–727/y118–555; right cabinet leaf x468–780/y56–377. Functional hero construction and material families fall below a useful readable value. Control existing local spill/reflection to reveal each housing/shelf/glass edge and its working silhouette. Preserve black negative space around these objects and keep the bed the brightest red focal cue. Limit: The visible problem is readability. Construction hidden by darkness cannot be scored as either well-built or primitive.

**V8-04 — refinement.** HIDDEN_BAG; Bag top and edge bands, approximately x41–1027/y253–486. The zip and handles prove a closed bag, but the broad flat surface and straight bands resemble a rigid carrier pad/tray. Add restrained broad fabric slack/tension, softened corners and irregular thickness appropriate to a folded closed bag; keep it concealed and avoid a noisy grunge treatment. Limit: No corpse or filled-body silhouette is required by this review; the defect concerns bag material/construction read.

## Per-camera gates

| View | Gate | Actual-pixel finding |
| --- | --- | --- |
| 01 | FRONT LEFT / CUTAWAY (CORNER_SW.png) | PASS | Overall route, OCRU mass and clinical wall are organized with useful negative space. Cutaway presentation does not prove player-camera detail or physical support. |
| 02 | FRONT RIGHT / CUTAWAY (CORNER_SE.png) | PASS | Bed bay, recovery berth, console, cartridge bank and decon are functionally grouped. Unlit skin regions remain an issue in closer designated views. |
| 03 | REAR LEFT / CUTAWAY (CORNER_NW.png) | PASS | The fixed layout and central movement strip are visually coherent. Dark entrance detail is separately failed in the entry-wall and reverse views. |
| 04 | REAR RIGHT / CUTAWAY (CORNER_NE.png) | PASS | Opposing overview preserves functional grouping and floor route. Small asset/support details cannot be validated at this framing. |
| 05 | ENTRY WALL (WALL_SOUTH.png) | FAIL | Centre entry leaf and header, approximately x325–638/y195–464, are near black; sign, seal/leaf construction and useful material identity cannot be read. |
| 06 | OCRU WALL (WALL_WEST.png) | FAIL | Red berth and mechanical lifts read, but both side interaction housings and much of the structural frame lose secondary form into black. |
| 07 | RESTART / DECON WALL (WALL_NORTH.png) | PASS | Restart, cartridge rack and decon grouping remain readable with differentiated construction. Recovery edge stays subordinate. |
| 08 | RECOVERY / SUPPLIES WALL (WALL_EAST.png) | PASS | Recovery, wash and warm supply worktop remain distinct overall functions. Cabinet and underbench detail are dark; cabinet has its own failed hero gate. |
| 09 | OCRU REANIMATION UNIT (HERO_OCRU.png) | FAIL | Bed seams, rails and lifts are specific; INSERT/RELEASE left x45–202/y205–465 and SUIT right x844–988/y267–491 are near-black masses, impairing interaction and material read. |
| 10 | RESTART CONSOLE (HERO_RESTART.png) | PASS | Layered monitor bezels, guarded controls, drawer hardware, folded shelf trim and restrained color hierarchy are readable; interface is functional rather than emissive filler. |
| 11 | MEDICAL CARTRIDGE BANK (HERO_CARTRIDGES.png) | PASS | Docked cartridges, shelf divisions, frame fasteners and labels support purposeful manufacturing. Functional repetition does not become generic unrelated-box repetition. |
| 12 | RESERVE POWER (HERO_RESERVE.png) | FAIL | Hero region x212–727/y118–555 is mostly black while adjacent console is bright; battery casing, connections and shelf depth cannot be confidently read. |
| 13 | DECONTAMINATION ALCOVE (HERO_DECON.png) | PASS | Reel, sagging hose, wall-service termination, bin/pedal and slatted floor read as a practical narrow service alcove. |
| 14 | RECOVERY BERTH (HERO_RECOVERY.png) | PASS | Broad linen folds/thickness separate from tubular rails and frame; tiny note at foot stays barely visible. Dark lower structure limits microdetail but does not erase the berth. |
| 15 | TRANSFER CART (HERO_CART.png) | FAIL | Entire scene region above the review label is essentially black. Cart silhouette, construction, support and material response are unavailable from the actual pixels. Cause may be illumination or camera occlusion; this review does not infer it. |
| 16 | SUPPLY WORKBENCH (HERO_SUPPLIES.png) | PASS | Warm working surface and restrained prop cluster communicate clinical function. Lower storage/legs lose detail, a secondary concern rather than a missing whole focal subject. |
| 17 | HANDWASH STATION (HERO_WASH.png) | PASS | Folded basin/rim, tap, molded dispenser and local wall deterioration remain distinct from the bright adjacent worktop. Hidden waste/support geometry is not certified. |
| 18 | MEDICAL SUPPLIES CABINET (HERO_CABINET.png) | FAIL | Left glazing and supplies retain a partial read; right leaf/interior around x468–780/y56–377 falls into black, preventing a full cabinet material/construction assessment. |
| 19 | ENTRY / PLAYER HEIGHT (ENTRY.png) | PASS | Red OCRU, rear working station and right recovery silhouette establish the room at player height; central route remains readable. Local detail failures are real but do not erase the entry composition. |
| 20 | REVERSE / PLAYER HEIGHT (REVERSE.png) | FAIL | Entry door centre, approximately x335–637/y178–414, loses opening/leaf construction and material cues into black. Warm left and red right focal pools leave the destination too weak. |
| 21 | RESCUE ROUTE / PLAYER HEIGHT (PINCH.png) | PASS | Rear console, cartridges and decon entry retain clear hierarchy and usable negative floor space. Geometric clearance remains a separate numerical check. |
| 22 | OCRU CARRIAGE / DETAIL (DETAIL_OCRU.png) | PASS | Upholstery seams, shaped pillow, telescoped rail/sleeves, lift blocks, restrained bolts and chassis layers demonstrate authored construction and material separation. |
| 23 | CLINICAL WORK / DETAIL (DETAIL_SUPPLIES.png) | PASS | Specific tools, folded linen, bandages, gloves, bottle construction and denied-release log support tactile clinical work without noise or random clutter. |
| 24 | BAG / INSPECTION FILL (HIDDEN_BAG.png) | PASS | Closed zipper, teeth/pull and handles are visibly confirmed. The broad flat top, straight blue edge bands and crossing strips need softer bag-specific slack/tension; inspection fill is not gameplay lighting evidence. |

The mandatory player-height gate fails: ENTRY passes, REVERSE fails, PINCH passes. Across all 24 images, 17 pass and 7 fail. Passing overview/detail cameras do not override the failing hero and route evidence.

## Limits

- Only current cycle-8 pixels and approved spawn calibration were reviewed; no historical critic scores or implementation were read.
- Cutaways intentionally expose interiors and cannot establish physical support, room boundary measurements or player clearances.
- HIDDEN_BAG uses labelled inspection fill, so its material/shape evidence does not certify bag visibility under gameplay lighting.
- No calibrated luminance threshold was imposed; regions and coordinates describe qualitative visual failures in the supplied render.
- Final-two-cycle stability, cold-start, engine import and owner acceptance remain unreviewed.

Technical cleanliness, collision/clearance dimensions, support contact, cold start, reproducibility and runtime integration were not reviewed and receive no points here. This review makes no historical regression claim and does not certify the final-two-cycle condition. Visual acceptance requires repair and another complete fixed-camera review.
