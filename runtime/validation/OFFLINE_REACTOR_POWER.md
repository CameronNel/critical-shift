# OFFLINE-005: source integration and bounded reactor/power rules

Authorized by Cameron on 18 September 2026: reconcile the existing offline runtime with WP-01, rerun offline checks, then add a bounded reactor/power slice with scenarios. Do not launch Blender or Unity. Primary author: ChatGPT. Independent reviewer: unassigned; acceptance pending. No self-merge.

Base: WP-01 43a2e328802fa4b73de407cfeebb5a7058edf90a on main a82c7d9b80456153a0c65ca4897044a7f62c7d1c. Offline source imported exactly from PR #43 at 30129f7a44e8976b13a4fe3307e329420034e2ff, runtime/dotnet tree 3fdd46aaa237b9e8bca3bb28d7a4836c27ae8f8f. The current sections tree and map files must remain unchanged. Only runtime sources/tooling, its workflow and navigation/affected decision documentation are in scope.

This is explicitly authorized offline prework, not WP-01/WP-02/Gate 0 or Gate 1 acceptance. Unity compatibility, physics, network transport, UI, saves, art and human playtesting stay NotRun. No runtime third-party package is selected. The inherited automatic Unity workflow is omitted on this candidate so a push cannot launch/download an editor. Native runner source and historical WP-01 evidence are retained.

Plan before changes: reconcile the conflicting Application assembly without duplicating gameplay writers; preserve test identities; consume one canonical C# source or compiled library at the future Unity boundary. Reactor owns abstract operating mode, interlocks and fuel/cooling response; Power owns reserve and committed energy costs. Application coordinates actual production fuel transfer and commands through the existing epoch/sequence/access path. New domain dependencies are Application -> Reactor.Domain / Power.Domain, with no peer-domain or engine references. Numeric abstract units are reviewable test fixtures, not approved balance or real nuclear engineering.

Acceptance: rerun inherited tests/scenarios; add tests for stale/duplicate/invalid commands, finite fuel, startup interlocks, power spending without overspend, pause/deadline/reset and causal identities; inspect exact diff and preservation hashes; collect actual cross-platform build/test artifacts. S01-S05/S07-S08, A01-A09, H01-H07, CMD/TX/POWER-01/CAUSE/LIFE/SHIFT and offline ARCH/CI checks apply partially. No engine-dependent case is declared passed.

Migration ledger and final fixture details/results will be added after implementation. Initial status: integration in progress; no new checks claimed passed.
