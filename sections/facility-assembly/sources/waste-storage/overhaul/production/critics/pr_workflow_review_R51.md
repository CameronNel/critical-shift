# Independent workflow-delta review — R51

## Scope

Reviewed only the current `README.md`, `blender/build_overhaul.py` and `blender/validate_overhaul.py` deltas against HEAD. No scene files, historical builders, or art scores were changed.

## Resolved finding — P2: fixture emission check read inactive nodes and omitted Emission shaders

The initial reviewed delta at `blender/validate_overhaul.py:42–54` built `energies` from every Principled node’s Emission Strength default, without checking whether that node contributed to the material output. The later exhaustive emissive audit recognized both Principled and `EMISSION` nodes, but did not require failed fixtures to have zero output.

That allowed two false passes: an inactive positive Principled default could satisfy a live fixture, and a positive connected `EMISSION` shader could evade the failed-fixture zero check. These were validation-boundary defects, not a finding that current R51 art was wrong.

The updated helper resolves these cases. It traverses only face-used lens material slots, requires an active `ALL`/`CYCLES` Material Output with a valid direct surface shader link, supports Principled/Emission constants, treats direct Transparent output as zero, and rejects unknown graphs or linked strength/color fields. For R51's dirty-glass color ramps, it bounds the RGB outputs over the supported RGB `LINEAR`, `EASE`, and `CONSTANT` interpolation modes while still requiring constant strength and finite nonnegative inputs. Live fixtures require a strictly positive lower emission bound; failed fixtures require an upper bound of zero. Unused nodes and slots cannot satisfy the fixture check.

## Accepted changes

- The cold replay preflight captures builder/full-room bytes, requires the archive files to exist and match before scene mutation, compiles the captured full-room bytes, and skips archive and active-alias writes for cold runs. The normal path still rejects occupied revision-owned outputs, and symlink/original-source output guards apply to both paths. Slice revisions intentionally have no full-room module.
- The README describes the selected-revision cold replay and distinguishes the unchanged historical archives from current canonical behavior.

The durable owner-run record `production/pr_workflow_checks_R51.json` reports PASS and names the exact validator SHA-256 `121b85ffb8418c23bef84e8c153d01100948973da85d42c6e9a02bac790f1b36`, matching the reviewed script. Hot and original-source cold R51 validation both pass with 26 fixtures (23 live, 3 failed), 589,943 triangles, and no issues. Actual-scene fault injections pass for zero live source energy, zero live lens emission, missing lens material, positive failed-source energy, positive failed-lens emission, disconnected positive Principled, connected positive Emission on a failed lens, linked strength with a positive default, black emission color, a ramp with zero minimum but positive maximum, and an unused positive slot paired with a dark face-used surface. Nine isolated archive-guard checks also pass, including missing/different builder/full-room rejection before mutation, exact archive cold replay, and no archive writes. The combined record says both scene files remained unsaved. The source and historical archive bytes were not rewritten.

No blocking defect remains in the reviewed code/doc delta. This review does not certify unrelated validation rules or runtime integration.
