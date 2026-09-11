# Luna concept review — A01 overall

**Reviewer:** Luna, independent concept reviewer  
**Date:** 2026-09-11  
**Asset:** `sections/turbine-room/art/concepts/A01-overall.png`  
**Scope:** conceptual relevance and visual guidance only; no geometry edits and no saved-scene approval

## Disposition

**Concept guidance: useful with constraints.** A01 is a strong reference for the visual idea of a convincing industrial conversion hall: an aligned turbine-to-generator train, visibly supported assemblies, overhead material-handling logic, floor drainage, restrained hazard marking, and a no-teal ivory/charcoal/oxide-orange/yellow palette. It is not a measured plan, a camera match, or permission to alter the established room envelope and interfaces.

The image reads taller and more expansive than the documented hall. It includes upper catwalks, stairs, guard-railed platforms and mezzanine-like service levels. The architecture baseline explicitly has no mezzanine, stairs or raised thresholds on the main route. Those elements are image deviations and must be treated as non-authoritative inspiration unless a later architecture decision explicitly changes the design. A01 cannot enlarge the 14 × 24 × 7.2 m clear hall, add a second route, or move a portal, machine axis or utility marker.

## Component relevance scores

These are scores for how useful each visible concept component is as guidance for this room. They are not the eight final production-category scores and do not approve any Blender component.

| Concept component | Relevance /100 | Evidence and limit |
|---|---:|---|
| HP-to-LP turbine and generator silhouette | 95 | The image clearly presents a staged conversion train: smaller front casing, broader exhaust body, coupling transition and distinct rear generator. This is highly relevant to the designed train hierarchy. The image does not establish exact axial bounds, radius, support contacts or machine-contract names. |
| Grounded industrial construction | 93 | Split casing seams, bolted flanges, feet, soleplates, bearing supports, guards, concrete foundation and cable/pipe supports provide useful construction cues. Select and simplify these cues for the game’s stylized semi-realism; do not reproduce photoreal texture density. |
| No-teal palette / color blocking | 98 | Ivory and warm grey shells, charcoal/steel structure, oxide-orange couplings and restrained hazard yellow provide an excellent match for the takeover mandate and Cooling Plant calibration. No visible teal should be carried into the final room. |
| Overhead steam admission concept | 90 | A01 visibly brings a large pipe overhead and drops it into the front/HP region. This is compatible in principle with the documented U01 overhead steam route. The image does not prove the exact interface marker, support undersides, east-aisle headroom, removable final branch, or the lift reservation conflict. Preserve the existing U01 interface and verify those points in saved geometry. |
| Coupling and generator service logic | 89 | The orange coupling transition, guarded shaft region, generator end ventilation and side service clearance are useful cues for the planned coupling guard and generator/output region. The concept does not prove the removable guard sweep or output-bus adapter. |
| Controls / operator bay | 81 | Two consoles and chairs on the left suggest a west-side operating station with human scale. The image does not show the required coherent throttle, load, speed/output/demand readback and latched trip cluster clearly enough to establish interaction coverage. It must not become a closed control booth. |
| Maintenance and repair story | 67 | The plant feels operational, but A01 does not visibly establish the documented bearing-oil service point, repair bench, oil stand, spare-part staging or a specific live fault. Use the maintenance slice and machine design for those requirements. |
| Route and portal compatibility | 70 | Broad floor lanes and two visible door-like openings suggest circulation, but the concept is not aligned to the fixed cameras or documented 2.4 m central route. No pixel proportion can certify the main keep-clear volume, crossovers, portal pockets, or cart/rescue sweeps. |
| Lift / material-handling cue | 84 | The overhead crane and hook communicate realistic heavy-part handling and support the design’s conceptual lift reservation. A01’s crane beam and elevated platforms cannot be assumed to fit the 7.2 m shell or clear the train, utilities and route without geometry checks. |
| Upper catwalks, stairs and platforms | 35 | They are visually plausible industrial dressing, but they conflict with the current baseline’s no-mezzanine/no-stairs/no-raised-threshold design and are absent from the approved route evidence. Do not carry them into the room from this image. |
| Lighting and atmosphere | 91 | Strong daylight shafts, practical wall lights, controlled warm pools and contact shadows give useful hierarchy and depth cues. The final room should adapt the hierarchy to fixed gameplay cameras and an enclosed plant, without relying on unapproved windows or cinematic exposure. |
| Environmental specificity | 88 | Drains, guarded equipment, wall utilities, consoles, crane and service rails imply a working facility rather than a showroom. Signage, incident cues, repair traces and worker-use evidence remain under-described. |

The scores intentionally separate the excellent machine/palette guidance from the low-confidence layout and maintenance evidence. No aggregate score is asserted.

## Image-to-layout deviations

### Overhead inlet

A01’s steam inlet is visibly overhead, entering the front of the turbine through a large elbow and vertical drop. This is directionally consistent with U01’s documented overhead route toward the HP steam chest. It remains only concept evidence: the image does not bind the reactor portal, establish the exact local endpoint, confirm the minimum underside over the east aisle, or solve the removable branch required before lifting an upper casing. Keep the interface ID and recorded local frame unchanged while implementing and auditing the room.

### Catwalks, stairs and upper levels

The image shows multiple upper guard-railed runs, a foreground stair, rear platforms and what reads as a mezzanine/service deck. The current architecture has no mezzanine and no stairs or raised thresholds on the main route. These features would consume vertical and circulation envelope, create unrecorded collision/navigation obligations, and change the camera read. They are rejected as direct layout instructions. At most, their industrial language can inform isolated wall-mounted service hardware if it fits the existing shell and passes route/headroom checks.

### Windows and exterior daylight

A01 has tall windows and a bright exterior view. They are useful as a lighting reference but are not part of the documented portal/interface contract. Do not add wall openings or rely on exterior daylight to make the room readable without a separate architecture decision and a full clearance/lighting review. The complete room must remain legible in its fixed-camera, authored plant-lighting setup.

### Footprint, train placement and route

The concept perspective makes the hall feel wider and taller than the local design. It cannot change the 14 × 24 × 7.2 m clear envelope, the central D01-to-D02 route, the east aisle, the west control/maintenance bays, the foundation envelope, or the common train axis. It also cannot authorize an assembled train to leave through a personnel portal. Any useful A01 machine proportion must be re-expressed inside the existing bounds and proven in the saved-file measurements.

## Style guidance to carry forward

Use A01 for the hierarchy of a believable working power-conversion hall: a clear main train, visibly different casing stages, supported bearings, a guarded coupling, a distinct generator, overhead process routing, floor drainage, and purposeful hazard lines. Carry forward the no-teal palette and the disciplined ivory/charcoal/oxide-orange/yellow relationship. Keep surface variation selective and material-specific so the room remains stylized and readable at gameplay distance.

Do not copy A01’s photographic lighting, exterior view, broad high-ceiling impression, catwalk system, stairs, or unmeasured clearances. The approved room is judged from its fixed ten-camera contract and the saved authoritative scene, with the Cooling Plant finals as quality calibration and the local architecture/interface as layout authority.

## Review result

**A01 concept relevance: PASS WITH CONSTRAINTS.** Approve the concept only as visual guidance for the train silhouette, industrial construction, overhead utility idea, crane/service storytelling, lighting hierarchy and no-teal palette. Reject its upper catwalks, stairs, mezzanine-like levels, implied expanded height/width, and any inferred portal or utility relocation. No Blender geometry, interface, footprint, or camera was changed by this review.
