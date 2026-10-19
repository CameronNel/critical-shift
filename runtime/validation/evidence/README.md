# Overnight runtime evidence, 19 October 2026

These files support the [overnight handoff](../OVERNIGHT_RUNTIME_20261019.md).
They preserve offline execution and source provenance. Current native Unity,
physics, rendered UI, Player, performance and multiplayer remain NotRun.

| File | Meaning |
|---|---|
| [Duration index](overnight-logical-20261019.json) | Per-build closure, accepted chunks and completed seconds |
| [Duration records](overnight-logical-20261019.jsonl.gz) | Raw Running/Passed reports and recorded observed zero-exit receipts; source/closure audits and final checkpoints |
| [Final execution index](overnight-final-tests-20261019.json) | Separate latest source, counts, hash and expected baseline failures |
| [Final execution records](overnight-final-tests-20261019.json.gz) | Raw positive/negative TRX, 13 logical controls, 28 scenarios, frozen 10,000-case run, and pre-fix regression TRX/test source |
| [PR checkpoint](pr-checkpoint-20261019.json) | GitHub states, exact heads/bases and Windows/Ubuntu CI at the recorded time |
| [PR inventories](pr-inventory-20261019.json) | Source inventory counts and runtime ancestry reconciled with those successful head checks |
| [Virtual merge](merged-source-20261019.json) | Conflict-free merge tree and static exported-source checks against main; native NotRun |
| [Package check](packaged-runner-20261019.json) | Actual workflow script, local frozen binaries, fresh extraction and CLI smoke; CI artifact download was blocked403 |
| [Premature archive guard](archive-premature-guard-20261019.json) | Archive writer refused to emit duration evidence before target completion |
| [Final handoff check](final-handoff-check-20261019.json) | Re-read archive hashes, totals, source inputs, UTC intervals and handoff links |
| [Native availability](native-availability-20261019.json) | Local editor unavailable and configured remote offline at the checkpoint |

Duration is the sum of sequential successful45-second logical probes across the
listed builds. It is not one continuous process or one unchanged build. Earlier
hours belong to their own source and binary closures. The latest test execution
is separate. Failed controls and the interrupted/unacknowledged children are
excluded. Case/checked-step counts include selected operations and model
observations, not distinct assertions or committed player actions. The archive
alone is not a measurement of authoring time.

Final execution source: `5d2c39733659ee0fa5a05a05a71ad3c5bc8366c7`.
Positive result:1,219 passed, zero failed/skipped;28 scenarios each twice.
One intentionally failing NUnit case,13 intentionally failing logical controls,
eight pre-fix owner regressions and two pre-fix lease regressions are preserved
as expected failures. Do not classify them as positive test failures. Baseline
source omits only the declared new typed-production assertion; behavioral
expectations remain. Raw negative-scenario/report-safety outputs and every
smoke/replay artifact are not included in this compressed execution record.
The full verifier's summary records those checks.

These archives contain reports and hashes. They do not embed the runnable
binaries, every source file or a native build. Source is referenced by immutable
Git commit; CI retains its own runner/source artifacts under its retention policy.
The separately recorded local package check executed first-party frozen binaries
and verified report bytes remained unchanged on overwrite rejection. It did not
execute a downloaded CI artifact.

Both gzip payloads use deterministic compression timestamps. Their indexes
record byte counts and SHA-256. This standard-library check verifies the payloads
before reading records, without modifying any evidence:

```sh
python - <<'PY'
from pathlib import Path
import gzip, hashlib, json
folder = Path('runtime/validation/evidence')
for name in ('overnight-logical-20261019', 'overnight-final-tests-20261019'):
    index = json.loads((folder / (name + '.json')).read_text())
    raw = (folder / index['archive']).read_bytes()
    expected = index.get('archive_sha256', index.get('sha256'))
    assert hashlib.sha256(raw).hexdigest() == expected
    assert len(raw) == index.get('archive_bytes', index.get('bytes'))
    data = gzip.decompress(raw).decode('utf-8')
    print(name, len(raw), 'verified bytes')
    if name.startswith('overnight-logical'):
        records = [json.loads(line) for line in data.splitlines()]
        chunks = [r['accepted_exit'] for r in records if r['kind'] == 'chunk']
        assert sum(r['seconds'] for r in chunks) >= 28800
        assert all(r['exit_code'] == 0 for r in chunks)
        print(len(chunks), 'accepted chunks', sum(r['seconds'] for r in chunks), 'seconds')
    else:
        record = json.loads(data)
        print(record['source_commit'], record['summary']['tests'])
PY
```

For each duration snapshot, the builder also checked all recorded source hashes
against its Git tree and all nine gameplay DLL hashes against its frozen closure.
Each raw chunk identifies that closure, its outer seed, duration and final case
counts. Accepted UTC intervals were checked for overlap. Seeds can repeat across
builds; totals do not claim unique cases or seeds. The final latest-source audit
is recorded separately from probe-duration attribution.
