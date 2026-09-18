"""One-shot, exact-baseline source integration. Removed from candidate after application."""
from pathlib import Path
import json

ROOT = Path.cwd()
assert (ROOT / 'runtime/dotnet/src/CriticalShift.Application/InteractionContracts.cs').is_file()
def patch(path, old, new, count=1):
    p=ROOT/path; text=p.read_text(encoding='utf-8')
    assert text.count(old)==count, (path,old[:100],text.count(old),count)
    p.write_text(text.replace(old,new),encoding='utf-8')
def write(path, text):
    p=ROOT/path
    assert not p.exists(), path
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8')
A='runtime/dotnet/src/CriticalShift.Application/'
patch(A+'InteractionContracts.cs','Grab, Release, Renew, Production }','Grab, Release, Renew, Production, Reactor }')
patch(A+'InteractionContracts.cs','SlotEmpty, ProductionRejected','SlotEmpty, ProductionRejected, ReactorRejected')
patch(A+'InteractionContracts.cs','ProductionRequest? production = null)','ProductionRequest? production = null, ReactorRequest? reactor = null)')
patch(A+'InteractionContracts.cs','LeaseGeneration = leaseGeneration; Production = production;','LeaseGeneration = leaseGeneration; Production = production; Reactor = reactor;')
patch(A+'InteractionContracts.cs','public ProductionRequest? Production { get; }','public ProductionRequest? Production { get; }\n        public ReactorRequest? Reactor { get; }')
patch(A+'InteractionContracts.cs','(Kind == InteractionKind.Production ? Production != null && Production.IsWellFormed && ExpectedRevision == 0 && LeaseGeneration == 0 :\n             Production == null &&','(Kind == InteractionKind.Reactor ? Reactor != null && Reactor.IsWellFormed && Production == null && ExpectedRevision == 0 && LeaseGeneration == 0 :\n             Reactor == null && (Kind == InteractionKind.Production ? Production != null && Production.IsWellFormed && ExpectedRevision == 0 && LeaseGeneration == 0 :\n             Production == null &&')
patch(A+'InteractionContracts.cs','ExpectedRevision == 0 && LeaseGeneration > 0));','ExpectedRevision == 0 && LeaseGeneration > 0)));')
patch(A+'InteractionContracts.cs','Production.Same(other.Production));','Production.Same(other.Production)) &&\n            (Reactor == null ? other.Reactor == null : other.Reactor != null && Reactor.Same(other.Reactor));')
patch(A+'InteractionContracts.cs','ProductionReply? production = null)','ProductionReply? production = null, ReactorReply? reactor = null)')
patch(A+'InteractionContracts.cs','IsReplay = replay; Production = production;','IsReplay = replay; Production = production; Reactor = reactor;')
patch(A+'InteractionContracts.cs','public ProductionReply? Production { get; }','public ProductionReply? Production { get; }\n        public ReactorReply? Reactor { get; }')
patch(A+'InteractionContracts.cs','State, true, Production);','State, true, Production, Reactor);')
patch(A+'InteractionWorld.cs','private ProductionOperations? _production;','private ProductionOperations? _production;\n        private ReactorOperations? _reactor;')
patch(A+'InteractionWorld.cs','internal void BindProduction(ProductionOperations production) { RequireSetup(); _production = production; }','internal void BindProduction(ProductionOperations production) { RequireSetup(); _production = production; }\n        internal void BindReactor(ReactorOperations reactor) { RequireSetup(); _reactor = reactor; }')
patch(A+'InteractionWorld.cs','case InteractionKind.Production: return _production?', 'case InteractionKind.Reactor: return _reactor?.Apply(actorId, command.EntityId, command.Reactor!) ?? new InteractionReply(InteractionStatus.TargetUnavailable, true);\n                case InteractionKind.Production: return _production?')
patch(A+'WorldSession.cs','_interaction.BindProduction(Production);','_interaction.BindProduction(Production);\n            Reactor = new ReactorOperations(this, _interaction);\n            _interaction.BindReactor(Reactor);')
patch(A+'WorldSession.cs','public ProductionOperations Production { get; }','public ProductionOperations Production { get; }\n        public ReactorOperations Reactor { get; }')
patch(A+'WorldSession.cs','var productionChanges = Production.AdvanceTo(_timeline.ElapsedMilliseconds);','var productionChanges = Production.AdvanceTo(_timeline.ElapsedMilliseconds);\n                var reactorChanges = Reactor.AdvanceTo(_timeline.ElapsedMilliseconds);\n                if (reactorChanges.Count != 0)\n                {\n                    _revision = next;\n                    foreach (var change in reactorChanges)\n                        _diagnostics.Append(View, Epoch, SessionTraceKind.Reactor, entity: change.State.Id, changed: true, reactor: change);\n                }')
patch(A+'WorldSession.cs','productionChanges: productionChanges);','productionChanges: productionChanges, reactorChanges: reactorChanges);')
patch(A+'WorldSession.cs','false, workerChanges, productionChanges);','false, workerChanges, productionChanges, reactorChanges);')
patch(A+'WorldSession.cs','{ Production.Clear(); _timers.Stop();','{ Reactor.Clear(); Production.Clear(); _timers.Stop();')
patch(A+'WorldSession.cs','kind == InteractionKind.Grab || kind == InteractionKind.Production','kind == InteractionKind.Grab || kind == InteractionKind.Production || kind == InteractionKind.Reactor')
patch(A+'WorldSessionContracts.cs','IReadOnlyList<ProductionChange>? productionChanges = null)','IReadOnlyList<ProductionChange>? productionChanges = null, IReadOnlyList<ReactorChange>? reactorChanges = null)')
patch(A+'WorldSessionContracts.cs','ProductionChanges = productionChanges ?? Array.Empty<ProductionChange>();','ProductionChanges = productionChanges ?? Array.Empty<ProductionChange>();\n            ReactorChanges = reactorChanges ?? Array.Empty<ReactorChange>();')
patch(A+'WorldSessionContracts.cs','public IReadOnlyList<ProductionChange> ProductionChanges { get; }','public IReadOnlyList<ProductionChange> ProductionChanges { get; }\n        public IReadOnlyList<ReactorChange> ReactorChanges { get; }')
patch(A+'SessionDiagnostics.cs','Disconnected, Ended, Stopped, Faulted, Production','Disconnected, Ended, Stopped, Faulted, Production, Reactor')
patch(A+'SessionDiagnostics.cs','ProductionChange? production)','ProductionChange? production, ReactorChange? reactor)')
patch(A+'SessionDiagnostics.cs','ImpactSeverity = severity;','ImpactSeverity = severity;\n            ReactorChange = reactor ?? interaction?.Reactor?.Change;\n            ReactorEvent = changed ? ReactorChange?.Kind : null;\n            ReactorResult = interaction?.Reactor?.Status;')
patch(A+'SessionDiagnostics.cs','public ProductionStatus? ProductionResult { get; }','public ProductionStatus? ProductionResult { get; }\n        public ReactorChange? ReactorChange { get; }\n        public ReactorEvent? ReactorEvent { get; }\n        public ReactorStatus? ReactorResult { get; }')
patch(A+'SessionDiagnostics.cs','ProductionChange? production = null)','ProductionChange? production = null, ReactorChange? reactor = null)')
patch(A+'SessionDiagnostics.cs','severity, production);','severity, production, reactor);')
patch(A+'ProductionContracts.cs','Ore, CrushedOre, Fuel }','Ore, CrushedOre, Fuel, SpentFuel }')
patch('runtime/dotnet/src/CriticalShift.Features.Materials.Domain/BatchTypes.cs','Ore, CrushedOre, Fuel }','Ore, CrushedOre, Fuel, SpentFuel }')
for path,prefix in [(A+'CriticalShift.Application.csproj','../'),('runtime/dotnet/tests/CriticalShift.Offline.Tests/CriticalShift.Offline.Tests.csproj','../../src/')]:
    refs=''.join('    <ProjectReference Include="'+prefix+'CriticalShift.Features.'+n+'.Domain/CriticalShift.Features.'+n+'.Domain.csproj" />\n' for n in ['Reactor','Power'])
    patch(path,'  </ItemGroup>',refs+'  </ItemGroup>')
assets=ROOT/'runtime/unity/Assets/CriticalShift'
old=assets/'Application/CriticalShift.Application.asmdef'
for path in list(assets.rglob('*.asmdef')):
    text=path.read_text();path.write_text(text.replace('"CriticalShift.Application"','"CriticalShift.ProcessLifetime"'))
old.rename(old.with_name('CriticalShift.ProcessLifetime.asmdef'))
Path(str(old)+'.meta').rename(old.with_name('CriticalShift.ProcessLifetime.asmdef.meta'))
patch('runtime/tools/check_source.py','definitions["CriticalShift.Application"]','definitions["CriticalShift.ProcessLifetime"]')
patch('runtime/tools/api_compile.py','build("CriticalShift.Application",','build("CriticalShift.ProcessLifetime",')
write('runtime/dotnet/src/CriticalShift.ProcessLifetime/CriticalShift.ProcessLifetime.csproj','''<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>netstandard2.1</TargetFramework>
    <EnableDefaultCompileItems>false</EnableDefaultCompileItems>
  </PropertyGroup>
  <ItemGroup>
    <Compile Include="../../../unity/Assets/CriticalShift/Application/ProcessLifetime.cs" Link="ProcessLifetime.cs" />
  </ItemGroup>
</Project>
''')
patch('runtime/dotnet/tests/CriticalShift.Offline.Tests/CriticalShift.Offline.Tests.csproj','  </ItemGroup>','''    <ProjectReference Include="../../src/CriticalShift.ProcessLifetime/CriticalShift.ProcessLifetime.csproj" />
    <Compile Include="../../../unity/Assets/CriticalShift/Tests/EditMode/ProcessLifetimeTests.cs" Link="ProcessLifetimeTests.cs" />
  </ItemGroup>''')
for filename in ['Program.cs','PureTests.csproj','packages.lock.json']:
    p=ROOT/'runtime/tools/pure-tests'/filename;assert p.is_file();p.unlink()
B='runtime/dotnet/tests/CriticalShift.Offline.Tests/ModelAndBoundaryTests.cs'
patch(B,'using CriticalShift.Features.Production.Domain;','using CriticalShift.Features.Production.Domain;\nusing CriticalShift.Features.Reactor.Domain;\nusing CriticalShift.Features.Power.Domain;')
patch(B,'new[] { typeof(MaterialLedger).Assembly, typeof(MachineState).Assembly }','new[] { typeof(MaterialLedger).Assembly, typeof(MachineState).Assembly, typeof(ReactorCore).Assembly, typeof(PowerAccount).Assembly, typeof(ProcessLifetime).Assembly }')
patch(B,'"CriticalShift.Features.Production.Domain" }','"CriticalShift.Features.Production.Domain", "CriticalShift.Features.Reactor.Domain", "CriticalShift.Features.Power.Domain" }')
patch(B,'type.Assembly == typeof(MachineState).Assembly ||','type.Assembly == typeof(MachineState).Assembly || type.Assembly == typeof(ReactorCore).Assembly || type.Assembly == typeof(PowerAccount).Assembly ||')
patch(B,'typeof(MaterialLedger).Assembly, typeof(MachineState).Assembly })','typeof(MaterialLedger).Assembly, typeof(MachineState).Assembly, typeof(ReactorCore).Assembly, typeof(PowerAccount).Assembly, typeof(ProcessLifetime).Assembly })')
patch(B,'typeof(SessionTraceRecord), typeof(SessionTraceView) }','typeof(SessionTraceRecord), typeof(SessionTraceView), typeof(ReactorView), typeof(ReactorRequest), typeof(ReactorReply), typeof(ReactorChange), typeof(PowerView), typeof(ReactorDefinition) }')
S='runtime/dotnet/tools/CriticalShift.Scenarios/Program.cs'
patch(S,'_world?.Trace, _world?.Production.Summary);','_world?.Trace, _world?.Production.Summary, _world?.Reactor.PowerSummary);')
patch(S,'case "production": return ProductionScenarioSteps.Execute','case "reactor": return ReactorScenarioSteps.Execute(s, _world, epoch, Id(100 + actor));\n                case "production": return ProductionScenarioSteps.Execute')
patch(S,'if (!ProductionScenarioSteps.TryRead(a, assertions, _world, out var actual, out var expected))','if (!ProductionScenarioSteps.TryRead(a, assertions, _world, out var actual, out var expected) &&\n                            !ReactorScenarioSteps.TryRead(a, _world, out actual, out expected))')
patch(S,'ProductionScenarioSteps.Bind(_spec, world); world.Start();','ProductionScenarioSteps.Bind(_spec, world); ReactorScenarioSteps.Bind(_spec, world); world.Start();')
patch(S,'ProductionSummary? production)','ProductionSummary? production, PowerView? power)')
patch(S,'Trace = trace; Production = production;','Trace = trace; Production = production; Power = power;')
patch(S,'public ProductionSummary? Production { get; }','public ProductionSummary? Production { get; }\n        public PowerView? Power { get; }')
patch('runtime/dotnet/src/CriticalShift.Features.Power.Domain/PowerAccount.cs','checked(Spilled + reserve - stored)','checked(Spilled + (reserve - stored))')
patch('runtime/dotnet/src/CriticalShift.Features.Reactor.Domain/ReactorCore.cs','Mode == CoreMode.Loaded || Mode == CoreMode.Exhausted;','Mode == CoreMode.Loaded || (Mode == CoreMode.Exhausted && InstabilityMilliseconds <= _rules.ResetMilliseconds);')
V='runtime/dotnet/tools/verify.py'
patch(V,'summary = {"status": "Passed",','''for linked in [ROOT.parent / "unity/Assets/CriticalShift/Application/ProcessLifetime.cs",
                   ROOT.parent / "unity/Assets/CriticalShift/Tests/EditMode/ProcessLifetimeTests.cs"]:
        source_hashes["../" + linked.relative_to(ROOT.parent).as_posix()] = hashlib.sha256(linked.read_bytes()).hexdigest()
    summary = {"status": "Passed",''')
C='runtime/dotnet/tools/check_boundaries.py'
patch(C,'ALLOWED = {DOMAIN:', '''REACTOR = "src/CriticalShift.Features.Reactor.Domain/CriticalShift.Features.Reactor.Domain.csproj"
POWER = "src/CriticalShift.Features.Power.Domain/CriticalShift.Features.Power.Domain.csproj"
PROCESS = "src/CriticalShift.ProcessLifetime/CriticalShift.ProcessLifetime.csproj"
LINKS = {
    PROCESS: [{"Include": "../../../unity/Assets/CriticalShift/Application/ProcessLifetime.cs", "Link": "ProcessLifetime.cs"}],
    TESTS: [{"Include": "../../../unity/Assets/CriticalShift/Tests/EditMode/ProcessLifetimeTests.cs", "Link": "ProcessLifetimeTests.cs"}],
}
ALLOWED = {REACTOR: set(), POWER: set(), PROCESS: set(), DOMAIN:''')
patch(C,'APPLICATION: {DOMAIN, SESSION, WORKERS, MATERIALS, PRODUCTION},','APPLICATION: {DOMAIN, SESSION, WORKERS, MATERIALS, PRODUCTION, REACTOR, POWER},')
patch(C,'TESTS: {DOMAIN, SESSION, WORKERS, MATERIALS, PRODUCTION, APPLICATION}','TESTS: {DOMAIN, SESSION, WORKERS, MATERIALS, PRODUCTION, APPLICATION, REACTOR, POWER, PROCESS}')
patch(C,'for tag in ("Reference", "Compile", "Import", "Target", "EnableDefaultCompileItems", "TargetFrameworks"):', '''links = [element.attrib for element in xml.findall(".//Compile")]
        if links != LINKS.get(relative, []):
            problems.append(f"Unapproved external Compile link: {relative}")
        for link in links:
            if link in LINKS.get(relative, []) and not (project.parent / link["Include"]).is_file():
                problems.append(f"Missing canonical linked source: {relative}")
        defaults = xml.findall(".//EnableDefaultCompileItems")
        if (relative == PROCESS and (len(defaults) != 1 or defaults[0].text != "false" or defaults[0].attrib)) or (relative != PROCESS and defaults):
            problems.append(f"Unapproved default source discovery: {relative}")
        for tag in ("Reference", "Import", "Target", "TargetFrameworks"):''')
G='runtime/dotnet/tools/test_guards.py'
patch(G,'self.root = Path(self.temp.name)','self.root = Path(self.temp.name) / "dotnet"\n        self.root.mkdir()\n        for relative in ("Application/ProcessLifetime.cs", "Tests/EditMode/ProcessLifetimeTests.cs"):\n            source = ROOT.parent / "unity/Assets/CriticalShift" / relative\n            target = self.root.parent / "unity/Assets/CriticalShift" / relative\n            target.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(source, target)')
patch(G,'APPLICATION, MATERIALS, PRODUCTION','APPLICATION, MATERIALS, PRODUCTION, REACTOR, POWER, PROCESS, TESTS')
patch(G,'    def test_clean_graph(self):','''    def test_reactor_cannot_reference_power_peer(self):
        path = self.root / REACTOR; tree = ET.parse(path)
        ET.SubElement(ET.SubElement(tree.getroot(), "ItemGroup"), "ProjectReference",
                      Include="../CriticalShift.Features.Power.Domain/CriticalShift.Features.Power.Domain.csproj")
        tree.write(path)
        self.assertTrue(any("dependency" in x for x in check(self.root)))

    def test_power_cannot_reference_reactor_peer(self):
        path = self.root / POWER; tree = ET.parse(path)
        ET.SubElement(ET.SubElement(tree.getroot(), "ItemGroup"), "ProjectReference",
                      Include="../CriticalShift.Features.Reactor.Domain/CriticalShift.Features.Reactor.Domain.csproj")
        tree.write(path)
        self.assertTrue(any("dependency" in x for x in check(self.root)))

    def test_external_link_cannot_be_changed_or_duplicated(self):
        for mode in ("replace", "duplicate", "conditional"):
            with self.subTest(mode=mode):
                path = self.root / PROCESS; original = path.read_bytes(); tree = ET.parse(path)
                item = tree.find(".//Compile")
                if mode == "replace": item.set("Include", "../../../arbitrary.cs")
                elif mode == "conditional": item.set("Condition", "'$(Configuration)' == 'Release'")
                else: tree.find("ItemGroup").append(copy.deepcopy(item))
                tree.write(path)
                self.assertTrue(any("Compile" in x for x in check(self.root)))
                path.write_bytes(original)

    def test_external_source_must_exist(self):
        (self.root.parent / "unity/Assets/CriticalShift/Application/ProcessLifetime.cs").unlink()
        self.assertTrue(any("canonical linked source" in x for x in check(self.root)))

    def test_process_project_cannot_discover_duplicate_sources(self):
        path = self.root / PROCESS; tree = ET.parse(path)
        tree.find(".//EnableDefaultCompileItems").text = "true"; tree.write(path)
        self.assertTrue(any("source discovery" in x for x in check(self.root)))

    def test_tests_cannot_link_second_process_copy(self):
        path = self.root / TESTS; tree = ET.parse(path)
        ET.SubElement(tree.find("ItemGroup"), "Compile", Include="../../copy.cs")
        tree.write(path)
        self.assertTrue(any("Compile" in x for x in check(self.root)))

    def test_clean_graph(self):''')
# Explicit new test identities, never inferred from a passing result or used to remove inherited tests.
additional = '''CoreExhaustionPrecedesTripOnExactTie CoreRejectsBackwardsTimeWithoutMutation CoreCooldownRequiresExplicitTripResetAndRestart CoreDoesNotBurnBeforeStart InvalidReactorDefinitionsAreRejected PowerAccountConservesCreditsAndSpend PowerAccountRejectsInvalidAndUnfundedCosts ProcessAndGameplayAssembliesComposeWithoutCollision ProducedFuelReachesReactorAndBecomesSpentFuel BypassedProductionCarriesRiskToReactor FuelCycleCompletionCannotRunTwice StartupInterlocksPreserveReserveOnRejection MatchingRetryDoesNotChargeOrCreateAnotherEvent ChangedRetryPayloadAndForwardGapAreRejected OldEvictedCommandsDoNotSpendAgain CompetingConsumersCannotOverspend StaleRevisionCannotControlReactor InvalidMixedPayloadDoesNotConsumeSequence RestartRetainsNoCoreReserveOrClaims PauseStopsReactorWorkButNotReceiptProgress LostCoolingWarnsAndTripsWithStableCause SuspectFuelWarnsAtItsOwnBatchCause ShutdownAndRestartPreserveCycleAndFuelWork PartUsedFuelCannotBeEjectedToRecharge SpentFuelCannotBeReused IsolatedFuelCannotBeGrabbedByAnotherWorker DeniedAccessDoesNotControlReactor HistoryCapacityRejectsStartBeforeDebit FailedInsertDoesNotTakeInputFromOtherActor DuplicateRegistrationDoesNotDamageExistingSetup PowerSummaryIsDetachedAfterTerminalTeardown EmergencyCoolingChargesOnceAndDoesNotRestart FinalFuelEjectionRetainsOriginalCycleAttribution UnexpectedAccessFailureFaultsWorldAndPreservesAccounting NewProcessStartsCreated ReadyIsExplicit DuplicateReadyIsRejected StopBeforeReadyIsSafe StopAfterReadyIsSafe StopIsIdempotent StoppedProcessCannotBecomeReady RepeatedFreshProcessesDoNotShareState'''.split()
manifest=ROOT/'runtime/dotnet/tools/expected-tests.json'; expected=json.loads(manifest.read_text())
assert sum(expected.values())==525
for name in additional:
    assert name not in expected;expected[name]=1
for name,count in {'CoreSafeMatchesIndependentClockModel':100,'CoreTripTimingIndependentOfClockPartition':2,'DeadlineCountsOnlyEnergyUpToCutoff':3,'FuelValidationPreservesCustody':3}.items():
    assert name not in expected;expected[name]=count
assert sum(expected.values())==675
manifest.write_text(json.dumps(expected,indent=2)+'\n')
# Reuse the original production input in a NEW scenario; the inherited scenario is unchanged.
sc=json.loads((ROOT/'runtime/dotnet/scenarios/production-chain.json').read_text());assert len(sc['steps'])==16
sc.update(name='reactor-full-production-chain',reactor={'id':900},traceCapacity=128)
def r(seq,action,rev,expect='Applied',**kw):return dict(op='reactor',seq=seq,action=action,reactorRevision=rev,expect=expect,**kw)
sc['steps']=sc['steps'][:-1]+[
 dict(op='production',seq=11,action='Eject',machine=702,machineRevision=3,objectRevision=5,expect='Applied'),
 dict(op='grab',entity=600,seq=12,revision=6,expect='Applied'),
 r(13,'Insert',4,container=600,objectRevision=7,batchRevision=2,lease=3),r(14,'SetCooling',5,cooling=True),r(15,'Start',6),
 r(15,'Start',6,**{'assert':{'spentPower':3,'pendingCycles':1,'lastReactorEvent':None}}),
 dict(op='advance',time=16600,expect='Running',**{'assert':{'reactorMode':'Exhausted','reactorWork':6000,'generatedPower':300,'deliveredPower':240,'reserve':67,'batchKind':'SpentFuel','batchUnits':60,'wasteUnits':40,'completedCycles':3}}),
 r(16,'Eject',8,objectRevision=8),dict(op='grab',entity=600,seq=17,revision=9,expect='Applied'),
 r(18,'Insert',9,'WrongFuel',container=600,objectRevision=10,batchRevision=3,lease=4,**{'assert':{'reactorMode':'Empty','generatedPower':300,'claims':1}}),
 dict(op='restart',expect='Running',**{'assert':{'reactorMode':'Empty','reserve':10,'generatedPower':0,'batchKind':'Ore','batchUnits':100,'completedCycles':0}})]
write('runtime/dotnet/scenarios/reactor-full-production-chain.json',json.dumps(sc,indent=2)+'\n')
p=ROOT/'runtime/dotnet/tools/expected-scenarios.json';m=json.loads(p.read_text());assert len(m)==8
for name,steps,assertions in [('reactor-cooling-recovery',13,43),('reactor-reserve-contention',11,21),('reactor-deadline',7,22),('reactor-full-production-chain',26,63)]:
    assert name not in m;m[name]={'runs':2,'steps_per_run':steps,'assertions_per_run':assertions}
p.write_text(json.dumps(m,indent=2)+'\n')
print('Applied bounded integration, preserved old tests, and declared 675 offline cases plus 12 scenarios. No editor invoked.')
