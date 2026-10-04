# Read-only delivery-helper review — Waste Storage

I inspected the Waste package builder, transport preparer, remote-body verifier, and the reused refinery delivery/publish/workflow templates as text only. I did not execute publication code, contact external services, or modify assets.

## Findings

**One concrete guard gap:** `build_package.py` takes the manifest `head` from the current checkout's `HEAD`, but creates `delivery.bundle` from the separately named `codex/waste-storage-overhaul-20261003` ref. It does not assert that those two commits are equal before computing the manifest and archive. The generated delivery worker later fetches the branch from the bundle and asserts the imported tip equals the manifest `HEAD`, so a mismatch should fail closed before LFS upload or target-branch push. Still, an early equality assertion is needed to ensure the package is built from the exact reviewed task-branch commit and to avoid producing an internally inconsistent package.

At this inspection, both the checkout `HEAD` and target branch ref resolve to the pinned base `b129600899e710fa8912d82ab5cfd2873851174c`, with no diff from that base. The owner has said the final Waste helper outputs will be generated only after the final earned commit; therefore this is a staged helper review, not proof that a finished package currently exists. Recheck that `HEAD` and the target branch tip match and that the final diff is nonempty/in-scope before package generation.

The path allowlist is bounded to the Waste Storage subtree, two module blend paths, and a top-level `AGENTS.md`. The parent independently confirmed the `AGENTS.md` exception is limited to a Waste-specific row, so the exception remains within reviewed Waste scope. The allowlist otherwise rejects paths outside `sections/facility-assembly/sources/waste-storage/`.

**Remediation verified:** the builder now asserts `HEAD == refs/heads/codex/waste-storage-overhaul-20261003` before path scanning and bundle creation. This closes the early exact-commit guard gap. The final commit still needs the planned HEAD/branch-tip check when the earned commit is ready; this read-only review does not claim a final Waste package has been generated.

## Verified safeguards

- The base SHA and target branch are pinned in the builder. The worker compares the package manifest's repository, base, head and target branch; validates the bundle ref resolves to the expected `HEAD`; compares changed paths against the manifest and Waste path allowlist; checks the protected original-source pointer remains identical; and uses a normal, non-force push to publish only the reviewed task branch. It verifies the remote ref equals the exact `HEAD` after push. There is no merge to `main`.
- Local LFS inventory verifies every included object's byte count and SHA-256 against its pointer OID, including the existing replay-source dependency. The tar manifest records the verified object list. The worker rechecks archive/chunk Git blob hashes, archive SHA-256, LFS object count/size/SHA-256 while extracting, and the exact object set before upload.
- After LFS upload, the worker requests download actions for every OID and independently streams every remote body, checking both byte count and SHA-256. Evidence stores OIDs, counts and hashes, not action URLs or credentials.
- The worker obtains `GH_TOKEN` from the Actions environment and uses it in Authorization headers only; the token is not embedded in URLs or printed. The reused publisher similarly keeps `GH_TOKEN` in request headers and stores only blob hashes and refs. The remote verifier suppresses HTTP error detail and records no signed URL/header material.
- The temporary delivery workflow and `.delivery/waste` files are placed on a short-lived transfer branch based on current `main`. The helper does not update `main`; the workflow is branch-filtered to that transfer branch and the `READY` path, and the worker deletes the temporary branch after successful publication. Thus the helper does not merge a global workflow change. The checkout action is pinned to a commit SHA and has only `contents: write` permission for the delivery job.

The reviewed templates still require successful runtime credentials and GitHub LFS behavior; this static review does not claim those external operations have succeeded. No R50 review score is assigned here.
