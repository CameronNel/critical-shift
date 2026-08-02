/**
 * Headless check of the repository-default facility.
 * Bundled for Node by `vite.validate.config.ts` and run by `npm run validate`.
 */
import { DEFAULT_FACILITY } from '../facility/facility';
import { formatIssues, hasErrors, validateFacility } from '../facility/validate';

// Node-only entry; @types/node is not worth adding for one symbol.
declare const process: { exit(code: number): never };

const issues = validateFacility(DEFAULT_FACILITY);
const byType = new Map<string, number>();
const byZone = new Map<string, number>();
for (const entity of DEFAULT_FACILITY.entities) {
  byType.set(entity.type, (byType.get(entity.type) ?? 0) + 1);
  byZone.set(entity.zone, (byZone.get(entity.zone) ?? 0) + 1);
}

const line = (label: string, map: Map<string, number>) =>
  `${label}: ` +
  [...map.entries()]
    .sort((a, b) => b[1] - a[1])
    .map(([k, v]) => `${k}=${v}`)
    .join(' ');

console.log(`facility: ${DEFAULT_FACILITY.name}`);
console.log(`zones: ${DEFAULT_FACILITY.zones.length}`);
console.log(`entities: ${DEFAULT_FACILITY.entities.length}`);
console.log(`routes: ${DEFAULT_FACILITY.routes.length}`);
console.log(line('by type', byType));
console.log(line('by zone', byZone));

if (issues.length > 0) {
  console.log('');
  console.log(formatIssues(issues));
}

if (hasErrors(issues)) {
  console.error('\nFAILED: facility document has errors');
  process.exit(1);
}
console.log('\nOK');
