# Independent technical audit — R23 power redistribution

**Artifact inspected:** `production/checkpoints/R23.blend`.\
**Revision:** R23; checkpoint, build, and validation source hash `28c9262e7f0514e61223da26e5d0584021236c563277ee6795c5feab082b8499`.\
**Formal validation:** PASS; 29 protected interfaces unchanged, world strength 0, 21 light checks, no reported issues. This is a read-only lighting-constraint review; it does not score the render or certify runtime behavior.

## Fixture pairing and outages

The evaluated scene contains 21 light objects with 21 distinct, existing physical fixture lenses; there are no missing or duplicate lens targets. Each lens material's electrical state and emission strength agree with its source. World strength is zero.

All six failed fixtures have both source energy and lens emission at zero: PV hood 1; ceiling pendants 3 and 5; and wall service lamps 0, 1, and 2. The receiving-bay ceiling pendant 0 is active at 50 W with its paired lens at emission strength 0.30. The other 14 active source/lens pairs also have emission strength 0.30. No external light source was added.

## Power changes and preserved poses

Compared R22 against R23, all 11 camera and 21 light world matrices are identical at `1e−9` tolerance; object names and types also match. The R23 revision script changes only existing source energies and the corresponding fixture-lens electrical state/color/emission values:

- Ceiling pendant 0: 0 → 50 W (revived).
- Wall service lamp 1: 14 → 0 W (now failed).
- Press task bar: 38 → 60 W.
- Mine threshold practical: 45 → 60 W.
- Personnel threshold practical: 22 → 28 W.

The six-failure count remains unchanged. The R22 and R23 build manifests also report the same 3,043-object count and 1,229 new objects. No geometry or room-residue shader operation appears in `revision_R23.py`; changes are confined to the existing fixture electrical properties. The 29 protected-interface check passes with no changes.

## Inherited geometry evidence and limits

The previously completed R22 independent audit remains the geometry provenance for the unchanged scene: all eight glove fingers had closed, positive-volume palm intersections; all printed pump marks were 20.027 µm off the paper face with +Y winding; and residue material users were restricted to indoor surfaces. I did not repeat those geometry checks for this power-only revision.

The cold rebuild and full R23 render batch were still running at audit time. This report makes no visual-quality, cold-rebuild, or runtime claim.
