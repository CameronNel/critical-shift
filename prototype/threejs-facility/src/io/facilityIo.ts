import type { FacilityDoc } from '../facility/schema';
import { formatIssues, hasErrors, validateFacility } from '../facility/validate';

function timestamp(): string {
  return new Date().toISOString().slice(0, 16).replace(/[:T]/g, '-');
}

export function downloadBlob(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  // Revoke late; Safari on iOS needs the URL alive past the click.
  setTimeout(() => URL.revokeObjectURL(url), 10_000);
}

export function exportFacilityJson(doc: FacilityDoc): string {
  const json = JSON.stringify(doc, null, 2);
  downloadBlob(
    new Blob([json], { type: 'application/json' }),
    `critical-shift-facility-${timestamp()}.json`,
  );
  return json;
}

export async function copyFacilityJson(doc: FacilityDoc): Promise<void> {
  const json = JSON.stringify(doc, null, 2);
  if (!navigator.clipboard?.writeText) throw new Error('Clipboard is unavailable in this browser');
  await navigator.clipboard.writeText(json);
}

/**
 * Parse and validate an imported document. Errors are readable on purpose:
 * the likely author of a broken file is a person hand-editing JSON, or another
 * AI agent generating a layout from the schema.
 */
export function parseFacilityJson(text: string): FacilityDoc {
  let parsed: unknown;
  try {
    parsed = JSON.parse(text);
  } catch (error) {
    throw new Error(`Not valid JSON: ${(error as Error).message}`);
  }
  const issues = validateFacility(parsed);
  if (hasErrors(issues)) {
    const errors = issues.filter((i) => i.level === 'error').slice(0, 8);
    throw new Error(
      `Facility JSON is not usable:\n${formatIssues(errors)}` +
        (issues.length > errors.length ? `\n…and ${issues.length - errors.length} more` : ''),
    );
  }
  return parsed as FacilityDoc;
}

/** Open a file picker and resolve with the chosen file's text. */
export function pickJsonFile(): Promise<string | null> {
  return new Promise((resolve) => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'application/json,.json';
    input.style.display = 'none';
    document.body.appendChild(input);
    input.addEventListener('change', () => {
      const file = input.files?.[0];
      input.remove();
      if (!file) {
        resolve(null);
        return;
      }
      file
        .text()
        .then(resolve)
        .catch(() => resolve(null));
    });
    input.addEventListener('cancel', () => {
      input.remove();
      resolve(null);
    });
    input.click();
  });
}
