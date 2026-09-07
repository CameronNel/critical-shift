# Archived Sol audit evidence

The Art08 reviewer script and JSON in `art-08/` were copied byte for byte from Sol's review worktree after its final audit execution. Their hashes match `SOL_ART_TECHNICAL_08.md`:

- Script SHA-256: `20ba36e57e531b886722106dbb304299281befba95347e472d4f8de977e75022`
- JSON SHA-256: `6ac4944738423fa68ea4d1267112bb1ecde1a0a2d0ec24948eb6e903d2ff0df0`

The report describes the files as untracked at its observed repository state, `14a5672`. The parent subsequently published the unchanged Art08 source/scene and the unfinished Art09a checkpoint in `8cf95b1`. This timing difference does not change the audit's source/blend hashes or its FAIL verdict.

The recorded command uses Sol's original absolute scratch paths. For reproduction, use these archived script bytes, pass the frozen Art08 scene/source as the documented inputs, and write new JSON into a separate scratch directory. Do not overwrite the preserved evidence. Art09a has not been independently cleared against these findings.
