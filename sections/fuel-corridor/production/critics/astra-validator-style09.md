# Style09 validator replay

**PASS for the requested correction and regression probes: 14/14 expectations matched.** The three-closure/no-body counterexample now fails the cartridge gate and propagates to `failed_gates`. The valid one-body/two-closure positive control still passes.

Inspected validator SHA256: `f18ced2168b84aa6588bae4d6e822218c508776fdbd5723dbce6ede3a1ffcdfa`. Current and retained validator-copy hashes matched after the run. Interface SHA256 remained `df24e4b752e18b5140702bf1dbedb5a8e9bc921333e86fe09a00f10c46ee6a88`.

`blender/validate.py:751–753` now requires exactly one exact/dotted-prefix body, two exact/dotted-prefix closures and three combined core geometries before testing dimensions. Independent source review and fresh CPU execution agree that this closes the reported cardinality loophole.

The same 14 probes were replayed in a new Blender 5.2.0 LTS factory/background process with two threads, exit code 0. Clear-route and valid inventory/hash controls passed. Render-hidden internal barriers, missing/empty carrier, absent body/closures, and independent build/detail/interface byte mismatches continued to fail their relevant gates.

Evidence:

- `astra-validator-probe-summary-style09.json`
- `astra-validator-probe-evidence-style09/`
- `astra-validator-probes-style09.py`
- `astra-validator-source-style09.py`

Earlier evidence is preserved in `astra-validator-before-style09/`; all **16 archived files** were checked byte-for-byte by SHA256. Original report paths remain intact. No modeling or validator source was edited.

This is targeted validator behavior, not scene acceptance: disposable `main()` fixtures intentionally fail unrelated camera/support/full-stage/cold-context gates. No production scene was opened/saved and no render/GPU work occurred. Packed floor-texture provenance is outside this replay and remains a separate review.

Remaining scope limit: the gate still identifies roles by names across scene geometry and checks combined world-axis bounds. Carrier membership, individual component shape/dimensions and opposite-end placement are not established by these 14 probes. The broader follow-up tests identified in the prior report remain useful; the specific three-closure bug is resolved.
