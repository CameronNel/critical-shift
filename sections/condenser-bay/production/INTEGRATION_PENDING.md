> Superseded by [FINAL_HANDOFF.md](FINAL_HANDOFF.md): two independent passing rounds are complete. This earlier preparation record is retained as history; its integration actions remain applicable.

# Local integration preparation — acceptance pending

This is a working integration record, not FINAL_HANDOFF or a claim of acceptance. R34 is saved and passes its disclosed local geometry audit. Full independent visual acceptance, two stable accepted rounds, and complete cold evidence remain outstanding.

## Asset and coordinate contract

- Asset: `blender/condenser_bay.blend`, R34, 2724 objects; source checkpoint in `production/checkpoints/R34/`.
- Saved SHA256: `26edf558d2e03b16b841940d20973b74017a52e9f8c0c320d5ff5487c9d9ea3b`.
- Room: 11.40 × 9.40 × 6.00 m. Local D01 threshold is (0,0,0), +Y inward, +Z up.
- Placement in turbine coordinates: add (1.6,7.4,-6.0). This is a local transform contract; whole-facility assembly is unverified.
- Original Grok R21 baseline and failed review history are retained. No neighboring section was edited.

## Work left for the integrator

| Connection or system | Local state | Integration action |
|---|---|---|
| U04 exhaust | Open rectangular 2.5 × 1.5 m receive at local (3,4.05,6); maps to turbine (4.6,11.45,0) | Reconcile both saved assets at the documented transform and verify the slab/header/chest joint in assembly. |
| U02 condensate | Local 0.2 m stub at (7.9,0,5.42), facing −Y | Route continuation to turbine U02 at (9.5,0,0.45) in turbine coordinates. The turbine-owned blind cap remains untouched; its owner/integrator must coordinate the cap action. |
| Cooling water | Local capped 0.3 m supply/return sockets at (9.6,3.2,3.15) and (9.6,4.9,3.15) | Design and bind the external loop. Cooling Plant's proposed 0.2 m sockets are not a reciprocal match or a proven connection. |
| D01 | Open 2.0 × 2.4 m local portal; deliberate unbound receiving connector | Supply and align the remote corridor and verify travel. |
| Drain / vent | Unbound endpoints listed in interface.json | Bind external destinations and inspect wall penetrations in assembly. |
| Movement and interactions | Saved markers/hooks, static route/cart/stair tests | Implement collision, navmesh, interaction logic, opening/removal animations, and whole-map travel. Static ray samples are not an engine movement test. |
| Major maintenance | Accessible stairs/gallery, lifting equipment and east service staging | Validate the carried bundle/removal sequence and equipment envelopes in engine; a full extraction sweep is not certified here. |

No MW, RPM or pressure rating is claimed. This is scenic game geometry, not a thermodynamic simulation or engineering certification.

## Reproduction and resource constraint

To reproduce in a separate isolated section copy, restore the frozen `production/checkpoints/R34/*.py` files into that copy's `blender/` directory, retain the immutable `production/checkpoints/R21/grok-baseline.blend`, and invoke the restored `astra_continue.py` under the resource guard and shared GPU gate with a new revision name such as `R34-replay`. Do not execute the checkpoint copy of that script in place: its directory-relative paths expect `blender/`. Never overwrite a completed revision. The baseline hash is checked by the continuation script. Current `build_condenser.py` retains the full factory-source alternative; source and continuation paths must be compared before claiming identical factory replay pixels.

The user subsequently reauthorized GPU use and requested maximum speed. Current wrappers use HIP hardware ray tracing on RX 9070 XT, GPU denoising, persistent data, all 16 logical processors and normal priority. Invoke GPU build/render jobs through the shared gpu_gate.py with owner astra-condenser-bay. Keep one worker and do not delete gpu.lock. Explicit ASTRA_RENDER_MODE=CPU remains available for capped CPU-only direct work; old CPU scores are not transferred to GPU images.

Current `astra_full_round.ps1 -Revision R34 -Samples 32` produces retained 18-camera and labelled supplemental 7-camera warm/cold packs, then checks hashes, completeness, render settings and separate process IDs. Its completion does not award art acceptance; independent Luna scores govern that gate.


R32 introduced saved exhaust-plenum continuity and chest-to-shell contact reports; R34 retains the corrected geometry and reruns those checks. The original capped inlet failed nine path probes in R31; R34 passes all nine into the vessel volume. These local tests supplement the slab aperture audit and do not claim a thermodynamic simulation.
