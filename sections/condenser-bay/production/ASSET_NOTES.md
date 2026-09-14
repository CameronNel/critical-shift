# Condenser asset and dependency notes

The editable source is `blender/condenser_bay.blend`. R34 contains 2,724 objects and the 18 fixed room cameras. The room frame, major machinery layout and Grok R21 baseline are preserved. Interactive controls remain separate scene components; `interface.json` records intended hooks rather than implemented gameplay.

Paint, metal, rubber, glass, liquid, concrete, paper and cloth use authored procedural materials. The saved CPU dependency audit reports no missing external image paths or linked Blender libraries. Text is authored as Blender text objects through the retained construction helpers. Cold review must verify the visible labels and materials as well as geometry.

`production/checkpoints/R34/` freezes the authoring scripts and saved blend. Reproduction starts from the hash-checked immutable R21 baseline. Render controllers are also copied into each review pack's `renderer-source/` directory, with separate hashes in its manifest; these record the exact controller used even when it was refined after the authoring checkpoint. Do not substitute preview, benchmark or historical CPU images for final review images.

The current pipeline uses Blender 5.2, Cycles HIP hardware ray tracing on the RX 9070 XT, GPU OpenImageDenoise, persistent render data and the shared GPU gate. The user explicitly requested maximum rendering speed. No global driver or game configuration was changed. CPU-only diagnostic work and the former capped CPU mode remain distinct from the current GPU review.

The game engine owns export/import adaptation, collision, navigation, runtime lighting, optimization, animation, interaction, networking and whole-map validation. The local handoff supplies visual source and connection contracts; it does not claim a working facility cooling loop, removal of the turbine-owned U02 cap, or certified engineering ratings. Final local visual acceptance and outstanding integration actions are recorded in `FINAL_HANDOFF.md`. The earlier `INTEGRATION_PENDING.md` is retained as preparation history.
