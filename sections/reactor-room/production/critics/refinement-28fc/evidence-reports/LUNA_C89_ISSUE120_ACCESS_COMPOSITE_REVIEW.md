# C89 issue 120: gantry ladder, landing, and gate

Candidate C89 SHA-256: `099be8168f948915436e200c57939c134dd2c44baec6c68bcc23528425bb420a`.

The complete route is supported by three exact-C89 full-quality images:

| View | Image SHA-256 | Manifest SHA-256 | What it resolves |
|---|---|---|---|
| 16, gantry access | `f2fb1eba39d42007ffec874bf6db24b8569a98749b66b48c83cd0e3b293bdcfa` | `ac2987a9e537aa15c1415a3368e0a24b5b82ac96ac616d954776b10846ebbb9b` | Landing deck, yellow portal/gate, ladder head and top transfer |
| 24, gantry middle | `6372b9e6db4b282871f5bc641e712289c5be6ade78fc045e6c25d9fc5234abcf` | `37f00d885b0d9e9ba3599f3434deabf734474675be5b95c59b6c3baaac887716` | Mid-run rungs, side guides and attachments |
| 25, gantry overview | `edc16b5b1eaa5d0dadfde5ce9630fe49a23e7584174698f527c121cfbb5b33ae` | `ecd8f92c0fdfe36b5cfdb3facd6e7824c153096612c93361f5b2ec3ccf0be672` | Whole ladder route in the room and its approach to the floor |

Each manifest records 1280×720, Cycles 96 maximum/32 minimum samples, OIDN, 16-bit color and path guiding. No image is a preview.

## Physical corroboration and scope

The exact-C89 saved audit records floor seats for both ladder feet at `(7.17, 0.88, 0)` and `(7.17, 1.26, 0)`, head ties to the pool platform at `z=13.82`, and the top-step/landing seam. The audit contains 3,449 finite support records with zero recorded failures; this is sampled support evidence, not exhaustive collision analysis. The exact-source `gantry-guard.json` records 120 fixed-rail/opening samples with zero failures. Its stated scope excludes the separate movable gate’s animation and global collision testing.

The images complement one another: view25 makes the end-to-end route apparent but the feet are small; view16 resolves the gate and upper transfer; view24 resolves the middle attachments. The saved foot, head-tie and landing contacts corroborate the small endpoints. Together they are sufficient for issue 120’s access-route readability and support scope. No new view23 is needed for this criterion. This disposition does not claim a dynamic-gate sweep or an exhaustive human-clearance envelope.

## Disposition

Accept issue 120 as a scoped composite for C89 from views16/24/25 plus the finite saved contact and fixed-opening checks. The lower ladder endpoint is visible in the wide view at small scale but is independently anchored to the floor in the saved support record. No concrete visual or support defect was found in this scope.
