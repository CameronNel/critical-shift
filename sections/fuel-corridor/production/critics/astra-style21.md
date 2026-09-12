# Astra independent visual review — style21 slice

Date: 2026-09-10. **Decision: FAIL — lighting remains at 89.** Materials now reach 90 in the actual scene. The standalone texture-candidate approval was not used as evidence of scene quality.

## Evidence and scope

Inspected all five actual style21 PNGs: C03_HERO, C09_MATERIALS, D01_CARRIER_OPERATION, D02_WORKBENCH and D03_UTILITY. Compared them with the previously inspected approved A05/mine references and the C06 paintover, reopening C06's same-content preview for this review. The assessment concerns the slice's visible quality, not unseen full-stage geometry or matching reference room layouts.

Manifest: `style21`, `slice`, blend SHA-256 `39460ff343d0125a6a1221e0ded9ca985e55fa38ea0994356464788f96dcf3f7`. The supplied technical_style21 report identifies style21, records support and packed-material PASS, matching saved/source identity, and only `internal_routes` as NOT_RUN. I read this supplied result but did not replay its checks. P05's full-only corrections are outside this visual assessment and are not considered verified.

## Scores

| Category | Score / 100 | Visible evidence |
|---|---:|---|
| Scale / circulation | **91 — local slice** | Door, bench and carrier proportions remain coherent; the staging bay and local approaches read clearly. No full-route dimensional claim follows from these images. |
| Shape / art direction | **90** | Architecture, carrier restraint hardware, shaped tools, creased gloves and service regulator provide sufficiently specific industrial forms. The tool ends remain simplified, but the overall slice no longer reads as a generic primitive assembly. |
| Hierarchy | **92** | Service, freight, staging and maintenance functions remain readily distinguishable. The illuminated service sign and white cartridge against its dark backing establish useful priorities. The new ceiling patch is a minor competing highlight. |
| Materials | **90** | The gloves and wiping cloth now communicate textile surfaces. Concrete, exposed steel, enamel, rubber, brass and the transparent filter remain distinguishable. The glove weave is somewhat coarse and prominent, so the material treatment still has limited refinement, but the previous ambiguous rubber/sheet read is resolved sufficiently for this slice. |
| Lighting | **89** | Upper emission reveals ceiling panel seams and improves the fixture/ceiling relationship. It does not sufficiently recover the adjacent dark structural faces: the strong ceiling patch still sits beside almost black beam junctions. C06/A05 retain more controlled gradients and readable dark steel detail. |
| Color | **92** | Cool grey concrete, off-white panel/payload fields, gunmetal and restrained orange remain coherent with the approved direction. Warm practicals retain separation without washing out the overall palette. |
| Environmental storytelling | **90** | Inspection identifiers, restrained and staged payload, brake cues, labeled maintenance objects and readable air-service controls establish the work. Fabric identity adds credibility to the bench's human-use props. |
| Technical correctness | **Not independently scored** | The supplied slice-applicable checks pass, with full routes NOT_RUN. No independent geometric replay was performed in this visual task. |

## Remaining observed defects

1. **Moderate — lighting still loses the upper steel's material character (C03).** The brightest ceiling area above the central pendant is now conspicuous, and nearby panel joints can be read. However, the horizontal beam band below it and the upper-right beam junctions remain nearly featureless. The change raises the ceiling's brightness more than it improves the legibility of the dark structure. The approved references preserve subtle edge/face differences in those dark materials while keeping practical-light emphasis. This remains the only sub-90 category; the issue is the distribution of visible light and dark values, not whether an upward emitter exists in source.

2. **Minor — glove texture is stronger than the surrounding material treatment (D02).** The coarse, high-contrast weave draws attention away from some finger folds and competes with the leather patches. It now reads as textile, which is a real improvement, but the references use more restrained fine surface detail. This limits polish without keeping the material category below the slice threshold.

3. **Minor — worktop/pipe variation and small tool profiles remain less refined than the references (D02/D03).** Broad mottling is visible on the metal, while the tool heads retain blunt repeated profiles. These are residual finish observations; the overall equipment identity, glass depth and material separation remain accepted at the scores above.

## Changes accepted

- Wiping cloth and glove fabric identity are visible in D02; the material complaint from style20 is sufficiently addressed.
- Ceiling panels, seams and the pendant's upper illumination are clearer in C03. This improvement is credited even though the remaining dark-beam issue prevents a lighting pass.
- Carrier hardware remains clear and grounded in C09/D01, with no return of the earlier pale floor slivers.
- Filter interior, graduations, housing bolts and model plate remain legible in D03. No new material regression was observed there.

There is no additional deduction for unresolved full-stage engineering. This remains a narrow visual lighting rejection of the submitted slice. No full build, scene mutation, source edit or render was performed; only this report was written. A bounded second look at D02/C03 corroborated clearer fabric/ceiling readability and the remaining coarse-weave/dark-junction concerns; scores are Astra's independent judgment.

## Image identity

| Image | SHA-256 |
|---|---|
| C03_HERO.png | `aa0ee8c629c74084cfc123c7e1e3c905c35ff5f5099e1eb3e72459ac9b9c74b7` |
| C09_MATERIALS.png | `c7c08bc4f128a498277cdd1eb9938da1064fa9226a890fc14d771212a2b6c16f` |
| D01_CARRIER_OPERATION.png | `6e5c77225eb60e3c8070c7f62907665ad77193a71e16e6001badbb4a2269cb7a` |
| D02_WORKBENCH.png | `9bb8628da5f90ae55bcc0e5b907fc37d9b1608e987f6c037e80031c8dcb2ef9f` |
| D03_UTILITY.png | `d513f59804f20a3d8404c4bde78f1595921316c3039c364cbfca1f35f3d17e38` |
