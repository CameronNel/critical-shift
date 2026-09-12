# Astra independent visual review — style16 slice

Date: 2026-09-10. **Decision: FAIL — visual slice gate remains closed.** Four visual categories remain below the required 90. The known support-contact failure is a separate technical issue and is not the reason for these visual scores.

## Evidence

Directly viewed the actual style16 `C03_HERO.png`, `C09_MATERIALS.png`, `D01_CARRIER_OPERATION.png`, `D02_WORKBENCH.png`, and `D03_UTILITY.png`. Directly viewed reactor A05, mine entry/heading/sump and C06-style05-paintover-r01 through the supplied same-content JPEG viewing copies in `production/evidence/reference-previews`. The current white/gunmetal/orange authority governs this review. The comparison concerns art language, finish and light/material behavior; the corridor does not need the reactor's room layout or the mine's rock/wet surfaces.

Manifest: revision `style16`, stage `slice`, blend SHA-256 `7ab8e43224e7d6d906586df4ef03432b034e33c1fdd2e740a1fe880a2d5ea8ef`. I did not reopen the blend or render anything. The supplied technical report was read only far enough to confirm that it identifies style16 and reports `support_contact: FAIL`; I did not independently replay that test. Full-route geometry is absent and is outside this slice's visual assessment.

## Scores

| Category | Score / 100 | Evidence |
|---|---:|---|
| Scale / circulation | **91 — local slice only** | C03 shows coherent doorway, workbench and carrier proportions, a clearly marked staging bay, and open local approaches. No conclusion about remote turns, measured clearances or continuous full-route circulation is supported by these five images. |
| Shape / art direction | **88** | The architecture fits the reference language. Toolbox clasps, flashlight divisions/switch and flask-cap detail read as purposeful construction. The tool set, cloth and gloves remain conspicuously simplified in D02, and the utility close-up still lacks the references' level of distinct manufactured detail. |
| Hierarchy | **91** | Service, freight, staging and maintenance functions are readily distinguishable. The darker backing improves the white cartridge's separation in C09/D01. C03 retains a weaker service-sign contrast and broader empty bright wall fields than C06, but local wayfinding and functional priorities are clear. |
| Materials | **88** | Exposed pipe, cask hardware, tool shafts and worktop now read more clearly as metal, with reflective variation distinct from the matte housings and rubber. The cloth/gloves and filter bowl remain weak; some metal variation reads as broad mottling rather than convincing material-specific use. |
| Lighting | **87** | Exposure and cast shadows make the scene readable. C03 still relies on broad bright wall fill, with little of C06's concentrated warm practical pools and tactile dark structural edges. Dark ceiling bands and broadly illuminated walls flatten the intended depth. |
| Color | **92** | Off-white, dark steel and orange consistently match the current palette. Orange concentrates on controls, travel cues and handling elements, and the new dark backing supports the payload. |
| Environmental storytelling | **89** | Labeled grease, identified toolboxes, working-looking clasps and flashlight controls add specificity. Carrier brakes, restraint hardware, checked tag and air-service equipment establish the work. The uniformly tidy gloves/cloth and very clean prop condition still make the bench feel arranged for display rather than convincingly used. |
| Technical correctness | **Not scored** | The supplied style16 audit reports support-contact failure; its diagnosis and repair remain separate. These pixels and that limited report read do not constitute a fresh independent technical audit or support a numeric technical score. |

## Strongest remaining visible defects

1. **Major — D02's soft goods and tools remain below the approved finish.** The pale cloth presents a nearly smooth sheet with minimal fabric behavior. The paired gloves look like flat molded pads with neat repeated fingers, despite the visible seam marks. The four wrenches share long straight shafts and blunt end profiles that remain generic at this close scale. Additional labels and clasp details elsewhere do not resolve these prominent shape/material weaknesses.

2. **Moderate — D03's filter bowl does not communicate its material convincingly.** It reads predominantly as an opaque ribbed olive component, with little visible transmission or interior depth. The matte regulator housing, large backplate and orange wheel still have a soft, very pristine finish. The exposed metal is improved, but the assembly as a whole has weaker material separation and manufactured character than the reference equipment.

3. **Moderate — C03's illumination remains flatter than C06/A05.** Bright wall fields receive similar broad coverage; several ceiling members collapse into near-black bands, and the service sign blends into its surrounding value range. C06 preserves more focused task-light emphasis, richer dark steel detail and greater separation between functional zones. The current image is readable, but this is still an obvious reference-match gap.

4. **Moderate — wear and use remain unevenly authored.** D02/D03 metal carries broad cloudy variation, while orange paint, toolbox faces, gloves and cloth remain unusually pristine. The cask's remaining small grey scuffs are less repetitive than style12 but still read as a few discrete graphic marks. The references maintain stronger relationships between material, exposed edges, joints and handling areas. This is not a request to apply uniform dirt or to match the mine's dampness.

## Visible improvements accepted

- The pale angular floor slivers previously identified in D01 are absent from the current D01 image; that specific visible distraction is resolved.
- C09/D01 silver rings, latches and lifting eyes separate more clearly from paint and rubber. The backing strengthens the payload silhouette.
- D02 now provides legible clasp mechanisms, container identification, grease-can construction, flashlight controls and flask-cap detail. These are visible improvements in specificity, not merely source-level additions.

The remaining shortfall is concentrated in close-up asset character and scene lighting. The architectural palette and route readability already meet this slice's visual standard. A visual pass is still not justified by the submitted images, irrespective of the separate support-contact investigation.

## Image identity

| Image | SHA-256 |
|---|---|
| C03_HERO.png | `92d040fb889a112b4b582a85314c30effee56adb75e1840bd73cce6da0b91b95` |
| C09_MATERIALS.png | `63955e0f2929da80259f6b2ec2194cf3ddf523d0dfb9d45b7136ed5635c9c047` |
| D01_CARRIER_OPERATION.png | `14a7be2b9ef6020427bb74358c951695f5ddd4be5923e00bd483efa7670a752d` |
| D02_WORKBENCH.png | `c61a7bde129597daa5844481aeabc50af36d2957399fba157f957eef74a94702` |
| D03_UTILITY.png | `ec9ec90a66903713a9cdae721d4e826aa93549f9a17ce8931793dd3b02d4d44a` |

A bounded independent second look at D02/D03 corroborated the improved metal/prop specificity and remaining cloth/glass issues. Scores and the gate decision are Astra's judgment. Only this report was written; no geometry, shaders, source, scene or neighbor files were changed.
