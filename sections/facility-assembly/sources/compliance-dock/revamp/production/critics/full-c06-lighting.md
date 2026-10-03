# Independent cycle06 lighting review

Category 5: **96/100**. Strict >93 gate: **PASS**. Critical defects: **0**. No lighting visual veto.

All 27 beauty, four UV-standard, four neutral and four approved spawn images were individually opened with `view_image` at original size. Complete manifests, frozen source/renderer SHA-256, every current PNG hash/dimension and every spawn PNG hash were independently verified. Native and renderer were hash-only; no code, graphs, old reports or scores were read.

The scanner has a clear cool key zone against a darker gate and roof. Warm hatch/office pools and a separate trolley pool establish depth; cargo strip light visibly lights curtain, lid and rollers. Contacts remain grounded, functional geometry remains readable, and emissives are restrained. Corner and wall views confirm this hierarchy throughout the room.

Deductions total four points:

- **L06-01 (-2)**: Dark vertical conduits and mounts compress against the black backing; the neutral render separates their routing and construction distinctly. Main boxes and upper pipe bends remain readable. Evidence: `full-cycle-06/HERO_UTILITIES.png`, `full-cycle-06/PLAYER_PINCH.png`, `full-cycle-06-neutral/HERO_UTILITIES.png`. Introduce restrained local reflected or edge light on the dark conduit runs while retaining the dim service-wall hierarchy.
- **L06-02 (-1.5)**: Lower conveyor supports and portions of the front/side frame merge in near-black values. Neutral reveals more construction. The curtain, crate, rollers and primary silhouette remain readable. Evidence: `full-cycle-06/C05_CONVEYOR_LEAD_TUNNEL.png`, `full-cycle-06/HERO_CARGO.png`, `full-cycle-06-neutral/C05_CONVEYOR_LEAD_TUNNEL.png`. Separate adjacent dark frame/rail planes with a small amount of controlled fill rather than raising whole-room exposure.
- **L06-03 (-0.5)**: Cabinet outer surrounds, the small office wall cabinet and far trolley support retain limited tonal separation. The readable doors and main supported forms prevent this from becoming a geometry-hiding veto. Evidence: `full-cycle-06/HERO_EVIDENCE.png`, `full-cycle-06/C07_OFFICE_INTERIOR.png`, `full-cycle-06/HERO_TROLLEY.png`, `full-cycle-06-neutral/HERO_TROLLEY.png`. Preserve low secondary values while adding just enough local plane separation to retain support and reveal detail.

Category 5 earns 96/100 and passes the strict >93 and zero-critical category gates. It does not earn 99: localized shadow compression still suppresses specific construction details. This review does not certify overall acceptance, native technical checks, regression stability or runtime lighting.

Frozen source: `73b85e9a84b577d2059a07371abd366666536800eb45c9e56a7d7788a21b77a3`. Renderer: `9993f999e0eddef5d3c106591728c665647cc49364e44199253780cb9bc89c57`. The spawn source hash is recorded by reference provenance; its native file was outside this pixel review and was not independently inspected.

All image and filesystem handles used by this critic are released; no background process or native scene handle was opened. Only this critic’s three report files were written.
