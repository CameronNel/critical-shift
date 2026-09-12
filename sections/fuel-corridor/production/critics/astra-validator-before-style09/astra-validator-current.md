# Current validator audit

**The requested failure behavior now works. One cartridge-role loophole remains, and these new cases are not yet covered by the validator's built-in self-tests.** P03's parked service-air recess is logically clear of the dressed bypass; full-stage and operating-state clearance remain unverified.

Independent audit by `/root/astra_reviewer`, with a separate source-only recess check by `/root/astra_reviewer/refinery_source_recheck`. Two fresh Blender 5.2.0 LTS factory/background CPU processes were run with two threads and a private profile. No production scene was opened/saved, no rendering/GPU work occurred, and no modeling or validator source was edited. Probe artifacts are confined to this critics directory.

Reviewed validator SHA256: `947af229ea54958c9fed633fac3ccd7705d3ca938da1fe443e10476d32a37b78`.

P03 interface SHA256: `df24e4b752e18b5140702bf1dbedb5a8e9bc921333e86fe09a00f10c46ee6a88`.

## Fresh test results

The existing `--self-test` suite passed **13/13**, exit code 0. It covers support gaps/penetration, fabricated anchors, missing support targets, disconnected members, an ordinary route barrier, cap-flag misuse and exact duplicates. It does **not** contain the newly requested hidden-barrier, mandatory-inventory or three-source-hash cases.

Independent probes called the actual `routes_audit()` and `main()` paths without altering their implementation. Positive controls preceded the negative cases.

| Probe | Actual result |
|---|---|
| Clear full route | PASS |
| 10 mm internal barrier with `hide_render=True` | FAIL; freight route records obstruction |
| Present carrier and three correct core parts | Their inventory/envelope gates PASS |
| Missing carrier / carrier with no evaluated children | Carrier gate FAIL |
| All core parts missing / body missing with two closures / one closure missing | Core gate FAIL |
| Matching build/detail/interface hashes | Provenance gate PASS |
| Independent byte changes to build, detail or interface file | Provenance gate FAIL in all three cases; failure enters `failed_gates` |
| No body-named object, but three closure-prefixed objects retaining the same combined bounds | **Core gate incorrectly PASS** |

The minimal `main()` fixtures deliberately fail unrelated camera/support/full-stage/cold-context gates. These tests establish the named gate's positive/negative behavior and failure propagation; they do not claim an entire production scene passed or certify a new cold reopen. The validator raised its expected failure exception after writing each failing report.

Evidence: `astra-validator-selftest-current.json`, `astra-validator-probe-summary.json`, `astra-validator-probe-evidence/`, and the reproducible `astra-validator-probes.py`. The probe script refuses to run against a different validator hash. **13/14 independent expectations matched; the last case above exposed a real weakness.**

## Remaining coverage issues

1. **Require component roles, not only total count.** `blender/validate.py:748–755` accepts any three names starting with either core prefix. It does not require exactly one body and two closures. The reproduced counterexample preserves matching bounds while eliminating the body role. Add role-specific counts, expected component dimensions and attachment/placement checks; aggregate bounds alone can also accept misplaced or inappropriate parts.
2. **Make the new regression cases durable.** Add hidden barriers, missing/empty carrier, each absent cartridge part, each independent hash mismatch, and the three-closure counterexample to the built-in suite. Include missing hash metadata/files and altered cartridge dimensions near the 2 mm threshold. These cases currently exist only in the independent probe evidence.
3. **Clarify envelope frame.** Carrier and core checks still compare world XYZ extents with length/width/height. The current axis-aligned setup is consistent, but rotated assemblies need an assembly-local measurement or an explicit orientation requirement.
4. **Keep route contract and test dimensions synchronized.** Bypass width 2.0 m and height 2.2 m are hardcoded at `validate.py:575`; the width currently agrees with P03, but a later interface change can diverge silently. Add a contract-consistency assertion and negative control.

The earlier hidden-render exemption is repaired: `routes_audit` now includes render-hidden geometry and excludes only the defined external cap members. Mandatory carrier failure and the three-way build/detail/interface hash comparison are also present and behave as intended. Explicit `--source-dir` and `--interface` inputs support frozen-source audits.

## P03 service-air recess

Source bounds in `interface.json:179–226` preserve a 2.40 m nominal bypass and add the lateral recess. The parked station's deepest handwheel remains approximately **110 mm behind the nominal corridor edge** and **310 mm outside the centered 2 m circulation strip**. Its mounting frame fits the recess length. No source contradiction was found for parked lateral clearance.

Qualification matters:

- Opposing ordinary wall bolt projections leave approximately **2.022 m**, only 22 mm above the dressed width requirement (`build.py:168–177`). This needs evaluated full-stage proof.
- The claim is **2.0 m wide × 2.2 m high**, not unrestricted width through the full 3 m height. A light hood projects farther inward above roughly Z2.465 (`valorant_details.py:230,376`).
- The station supply reaches Z2.46 while the niche ceiling starts at Z2.45; a **source-derived 10 mm overlap**, plus possible pipe/crossmember overlap, remains outside the route-width proof. Intended service penetration/continuity is not established by the current validator.
- The recess and station are omitted from the slice. Full-stage rays are finite samples, and floor support is tested along the centerline. Operator stance/reach, deployed hoses, supply continuity and comprehensive incidental intersections have no dedicated tests.

The station definition/call matched frozen style08 during this check, although the mutable detail file differed elsewhere. This audit does not certify later edits, adjacent passage, global assembly, runtime collision or art acceptance.
