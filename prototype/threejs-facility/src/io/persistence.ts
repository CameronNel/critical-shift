import type { FacilityDoc } from '../facility/schema';
import { formatIssues, hasErrors, validateFacility } from '../facility/validate';

const FACILITY_KEY = 'critical-shift.facility.v1';
const VIEW_KEY = 'critical-shift.view.v1';

export interface StoredView {
  mode: string;
  position: [number, number, number];
  yaw: number;
  pitch: number;
}

function storage(): Storage | null {
  try {
    return window.localStorage;
  } catch {
    // Private browsing and some embedded webviews throw on access.
    return null;
  }
}

export function saveFacility(doc: FacilityDoc): boolean {
  const store = storage();
  if (!store) return false;
  try {
    store.setItem(FACILITY_KEY, JSON.stringify(doc));
    return true;
  } catch {
    return false;
  }
}

/**
 * Load the locally edited layout. Anything invalid is discarded rather than
 * half-applied, so a bad edit can never leave the prototype unopenable.
 */
export function loadFacility(): { doc: FacilityDoc | null; error: string | null } {
  const store = storage();
  if (!store) return { doc: null, error: null };
  const raw = store.getItem(FACILITY_KEY);
  if (!raw) return { doc: null, error: null };
  let parsed: unknown;
  try {
    parsed = JSON.parse(raw);
  } catch {
    return { doc: null, error: 'Saved layout is not valid JSON; using the repository default.' };
  }
  const issues = validateFacility(parsed);
  if (hasErrors(issues)) {
    return {
      doc: null,
      error: `Saved layout failed validation; using the repository default.\n${formatIssues(issues)}`,
    };
  }
  return { doc: parsed as FacilityDoc, error: null };
}

export function hasSavedFacility(): boolean {
  return storage()?.getItem(FACILITY_KEY) !== null && storage()?.getItem(FACILITY_KEY) !== undefined;
}

export function clearFacility(): void {
  storage()?.removeItem(FACILITY_KEY);
}

export function saveView(view: StoredView): void {
  try {
    storage()?.setItem(VIEW_KEY, JSON.stringify(view));
  } catch {
    /* Not important enough to surface. */
  }
}

export function loadView(): StoredView | null {
  const raw = storage()?.getItem(VIEW_KEY);
  if (!raw) return null;
  try {
    const parsed = JSON.parse(raw) as StoredView;
    if (!Array.isArray(parsed.position) || parsed.position.length !== 3) return null;
    if (!parsed.position.every((n) => Number.isFinite(n))) return null;
    return parsed;
  } catch {
    return null;
  }
}
