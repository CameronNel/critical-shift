# Reactor Room Checkpoints

<!-- ART_DIRECTION_RESET_2026_09 -->
> [!IMPORTANT]
> **Art-direction canon:** Critical Shift uses **grounded stylized semi-realism**. Valorant-style environment principles are the primary rendering influence; PEAK contributes readability and restraint only. The target is believable, tactile and simplified, **not** generic low-poly, toy-like, Three.js-looking, glossy sci-fi, or modern AAA photorealism. [ART_DIRECTION](/design/ART_DIRECTION.md) and [ART_REFERENCE_INDEX](/design/ART_REFERENCE_INDEX.md) override conflicting legacy style wording in this file.


Store meaningful rollback checkpoints or checkpoint manifests here.

Checkpoint before structural, hero-machinery, material-system or lighting-system changes that could cause broad regressions.


## Style checkpoint rule

Create a named checkpoint immediately after the reactor validation slice passes. That checkpoint becomes the visual baseline for later regressions. Do not checkpoint a failed style and then treat its existence as approval.
