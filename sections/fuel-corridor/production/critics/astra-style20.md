# Astra independent visual review — style20 slice

Date: 2026-09-10. **Decision: FAIL — materials and lighting remain below 90.** Shape/art direction and storytelling now meet this slice's visual threshold. This decision is independent of the separate full-stage source preflight defects.

## Evidence and limits

Directly inspected the actual style20 C03_HERO, C09_MATERIALS, D01_CARRIER_OPERATION, D02_WORKBENCH and D03_UTILITY PNGs. Compared them with the approved reactor A05, mine entry/heading/sump and C06 paintover images through the supplied same-content viewing copies in `production/evidence/reference-previews`; A05 and C06 were reopened for this review. The references govern finish and visual language, not a requirement to copy room layouts or add mine wetness/rock to the corridor.

The manifest identifies `style20`, stage `slice`, blend SHA-256 `2cffe4448ff846aba036c79be587af39d03032f4ee190e6fad0499bff01d45ac`. The supplied `technical_style20.json` identifies the same revision, reports support PASS and matching saved/source identity, and lists only `internal_routes` as failed because that gate is NOT_RUN for the slice. I read that supplied result; I did not independently replay technical validation. No full-route or overall technical acceptance is implied.

## Scores

| Category | Score / 100 | Observed basis |
|---|---:|---|
| Scale / circulation | **91 — local slice** | C03 retains coherent door, bench and cart proportions, readable staging and open local approaches. Remote routes and measured clearance remain outside these pixels. |
| Shape / art direction | **90** | Contoured spanner shanks, creased gloves, the filter's visible internal assembly and housing fittings now provide enough object-specific construction for the slice. The architecture and carrier already establish the intended industrial language. Tool ends and some small props remain simplified, but no longer dominate the whole slice as generic primitives. |
| Hierarchy | **92** | The service sign, its light and directional chevrons establish a clearer destination. Staging, freight and maintenance functions remain distinct; the white payload separates well from its dark backing. |
| Materials | **89** | Cool concrete, reflective exposed steel, painted cartridge, orange controls, dark rubber and the filter's transparent enclosure are now distinguishable. D02's cloth remains a very smooth folded sheet, while the gloves still have a relatively uniform rubbery surface read. Broad mottling on steel is less specific than the references' controlled surface variation. |
| Lighting | **89** | The new service-light pool improves focus, and the cooler floor separates better from warm practicals. However, C03 still loses upper structural detail in nearly black beam bands while broad pale wall fields dominate the midtones. The references maintain more tactile dark steel and more deliberately shaped light/shadow transitions. |
| Color | **92** | The cooler grey floor, off-white wall/cartridge fields, gunmetal and restrained orange form a coherent match to the current palette. Local warm lighting does not overwhelm it. |
| Environmental storytelling | **90** | Inspection/checked identifiers, the staged restrained cartridge, brake cues, air-service hardware and individually identifiable maintenance objects communicate the intended work. The more natural glove shapes and visible filter core support this reading. The very tidy bench remains a minor limitation, not a missing story. |
| Technical correctness | **Not independently scored** | The supplied audit passes the slice-applicable gates; full internal routes are NOT_RUN. This visual review did not perform the independent geometric verification needed for a numeric technical score. |

## Remaining visible defects

1. **Moderate — soft-goods material character remains weak in D02.** The blue-grey cloth has a broad fold but very little readable fabric character; it can still be mistaken for a thin smooth sheet. The gloves have better creases and less rigid silhouettes, yet their palms/fingers share a uniform, softly highlighted surface. The reference bench communicates fabric and layered soft materials more distinctly. This is about their appearance in the close view, not an assertion that a shader or fold is absent from source.

2. **Moderate — dark structure still loses too much definition in C03.** The upper horizontal framing and right ceiling beams become nearly featureless black strips. The service light improves the sign, but much of the architecture still alternates between broad bright wall fields and blocked dark bands. C06/A05 retain clearer material response and construction detail through their darker values. The current image is easy to read, but the light/material balance has not quite reached that reference finish.

3. **Minor — material variation does not always explain use (D02/D03).** The worktop and pipes show broad cloudy variation, while the nearby containers and handled parts remain very clean. Small wheel chips are visible and should be credited; the remaining issue is the consistency of the overall wear language, not a need for dirt everywhere.

4. **Minor — close tool profiles remain blunt (D02).** The shaped shanks improve the tools considerably, but their similar circular box ends and square-looking open jaws still feel less refined than the paintover's tool set. This is a residual finish limitation, not a new requirement for replacement geometry.

## Improvements accepted from the pixels

- D03's filter core, enclosure depth and graduation marks are visible. The old predominantly opaque-bowl complaint is resolved sufficiently for this slice.
- Housing lugs, bolts and the model plate give the air station a more specific manufactured identity.
- D02's gloves have visible creases and cuff/finger variation; the former flat padded-extrusion silhouette complaint is substantially resolved. Material character remains the narrower concern above.
- The cooler floor and service-header light improve color separation and local hierarchy. The removed floor slivers remain absent in D01.
- Carrier rings, lifting eyes, latches and brakes remain readable and consistently separated from the payload paint and rubber.

No additional full-stage defect has been deducted from these visual scores. The two sub-90 categories are grounded in the submitted slice's actual pixels. The next acceptance evidence must demonstrate those visible gaps are resolved; a passing slice technical report alone does not settle them.

## Image identity

| Image | SHA-256 |
|---|---|
| C03_HERO.png | `cf2dfb4dec1c7bfaa87a75a93c984203801020fa91a322b6fa020b77a4a0ee36` |
| C09_MATERIALS.png | `edab5467bd12780476dc6a9794df4857c91ea4e06f2cd36e9a46482b90a028b8` |
| D01_CARRIER_OPERATION.png | `3f2cacb03f8fdf233475576012e16c5652e8def815ff90ca7a6a9c1ffef6a9a9` |
| D02_WORKBENCH.png | `32f0b87c3409e5fcb372604bde5a82563e1aee2d9a2bec035ac644ecba623fe6` |
| D03_UTILITY.png | `c981f66dbfc1d33c1a1303ed2eba1decb4bc66e63917eba24aee16de35d3b792` |

A bounded independent D02/D03 crosscheck corroborated the stronger filter/prop identity and the remaining cloth/wear concerns. Scores and gate decision are Astra's judgment. Only this report was written; no scenes, geometry, shaders, source or neighbor files were changed and no render was run.
