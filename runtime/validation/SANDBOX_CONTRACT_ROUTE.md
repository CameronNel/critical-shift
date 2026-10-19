# Sandbox supply route,19 October2026

Task branch `codex/sandbox-contract-route-20261019`, primary author Codex; based
on medical checkpoint `2f247020`. Continuing authorized game development, with
one bounded responsibility: keep the sandbox's logical recipes, stock, reactor
and contract in one canonical fixture setup, and prove a complete legal supply
route against those exact values. This is not a balance or physics acceptance.

Baseline implementation: `SandboxFixture.BuildContainers/BuildMachines/BuildReactor`
and constructor registered gameplay inline; separate offline scenarios used
different, smaller fixture numbers. A passing small scenario therefore did not
establish that the actual twelve-minute sandbox could meet its contract.

The pure setup source remains in Sandbox Bootstrap and links exactly into the
offline test project. The Unity fixture uses that same registration once.
Application/Domain ownership and assembly edges remain unchanged; no package,
content art, network, UI/input or persistence framework is selected. Stable IDs
and authored parameters remain intact. S01/S05/S08, POWER-01, TX-01/02, SHIFT-01,
ARCH and verifier source-link checks apply. Existing serialized source identities
are retained; the new pure setup adds one new metadata identity.

Implemented evidence: a real ore→crusher→processor→fuel→reactor route through the
public local command port, demand windows and terminal accounting, across bounded
reload delays and a missed-window control. Tests use original quantities and
safe recipes without privileged completion or free power. Current models running in
the separate frozen medical endurance snapshot do not cover this extraction.

Unity remains unavailable/Blocked; native fixture import, loading clearance,
carrying time, human feel and actual solo/multiplayer success remain NotRun.
No merge or roadmap gate is claimed.

## Executed checks

- All six route cases passed on their first targeted run. Four reload budgets
  (0/10/20/21 seconds) can meet the contract;21.5-second reloads deliberately
  miss peak demand by four energy units. Coarse and partitioned advances agree.
- Full first verifier:818 executed/passed, zero failed/skipped,18 scripted
  scenarios each twice, with real failure/report-protection controls. Static
  source check passed182 GUIDs,21 asmdefs and111 C# files. The new canonical
  pure fixture is included in source-link validation and source hashes.
- The route processes34+11+11+11 fuel from four dry ore crates, adds12 initial
  fuel units, consumes the existing reserve startup cost for each load, and
  asserts exact window energy, no bypass/jam/trip, material conservation and
  terminal claim cleanup. Ten-second reloads deliver0/800/1040/1280 energy.
  Transport renewals run every second, using the configured three-second lease.
- Medical PR114 passed Ubuntu and Windows CI at2f247020; these route changes
  need their own exact-commit/CI evidence. Independent ultra source reviewer
  `review_domain` found no blocking findings and checked route arithmetic,
  registration order/values, physical mass and exact links. Their suggested
  broader terminal cleanup assertions were added. They ran no builds.
- Moving registration ahead of host composition also adds a disposal fallback
  that stops the pure world if setup fails before a host exists. Native execution
  of this lifecycle path remains NotRun.
- A fresh connected-device probe found the workstation offline. The cloud has
  no Unity editor and its official editor download is blocked; no account login
  or native success is claimed.
