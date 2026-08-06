import type { App } from '../core/app';
import { defaultFacility } from '../facility/facility';
import {
  copyFacilityJson,
  exportFacilityJson,
  parseFacilityJson,
  pickJsonFile,
} from '../io/facilityIo';
import { exportGreyboxGlb, exportReactorGlb } from '../io/exportGlb';
import { clearFacility, saveFacility } from '../io/persistence';
import type { Hud } from './hud';

function el<K extends keyof HTMLElementTagNameMap>(
  tag: K,
  className?: string,
  text?: string,
): HTMLElementTagNameMap[K] {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function button(label: string): HTMLButtonElement {
  const node = el('button', 'btn btn-toggle', label);
  node.type = 'button';
  node.dataset.hud = 'button';
  return node;
}

/** Save, restore, import, export. Errors are shown, never swallowed. */
export function buildDataUi(hud: Hud, app: App): void {
  hud.addPanelSection('Layout', (body) => {
    const grid = el('div', 'toggle-grid');

    const save = button('Save locally');
    save.addEventListener('click', () => {
      if (saveFacility(app.facility)) hud.toast('Layout saved in this browser');
      else hud.toast('This browser refused local storage', 'error');
    });

    const reset = button('Reset to repo default');
    reset.addEventListener('click', () => {
      clearFacility();
      app.setFacility(defaultFacility());
      app.respawn();
      hud.toast('Reset to the layout committed in the repository');
    });

    const exportJson = button('Export JSON');
    exportJson.addEventListener('click', () => {
      exportFacilityJson(app.facility);
      hud.toast('Exported facility JSON');
    });

    const copyJson = button('Copy JSON');
    copyJson.addEventListener('click', () => {
      copyFacilityJson(app.facility)
        .then(() => hud.toast('Facility JSON copied to the clipboard'))
        .catch((error: Error) => hud.toast(error.message, 'error'));
    });

    const importJson = button('Import JSON');
    importJson.addEventListener('click', () => {
      pickJsonFile()
        .then((text) => {
          if (text === null) return;
          try {
            const doc = parseFacilityJson(text);
            app.setFacility(doc);
            app.respawn();
            hud.toast(`Imported ${doc.entities.length} entities`);
          } catch (error) {
            hud.toast((error as Error).message, 'error');
          }
        })
        .catch((error: Error) => hud.toast(error.message, 'error'));
    });

    const exportGlb = button('Export GLB');
    exportGlb.addEventListener('click', () => {
      exportGlb.disabled = true;
      exportGlb.textContent = 'Exporting…';
      exportGreyboxGlb(app.site.layers)
        .then((bytes) => hud.toast(`Exported greybox GLB (${Math.round(bytes / 1024)} KB)`))
        .catch((error: Error) => hud.toast(`GLB export failed: ${error.message}`, 'error'))
        .finally(() => {
          exportGlb.disabled = false;
          exportGlb.textContent = 'Export GLB';
        });
    });

    const exportReactor = button('Export Reactor GLB');
    exportReactor.addEventListener('click', () => {
      exportReactor.disabled = true;
      exportReactor.textContent = 'Exporting reactor…';
      exportReactorGlb(app.site.layers)
        .then((bytes) => hud.toast(`Exported reactor-room GLB (${Math.round(bytes / 1024)} KB)`))
        .catch((error: Error) => hud.toast(`Reactor GLB export failed: ${error.message}`, 'error'))
        .finally(() => {
          exportReactor.disabled = false;
          exportReactor.textContent = 'Export Reactor GLB';
        });
    });

    grid.append(save, reset, exportJson, copyJson, importJson, exportGlb, exportReactor);
    body.appendChild(grid);
    body.appendChild(
      el(
        'p',
        'hint',
        'JSON is the authoritative layout. GLB is a one-way visual handoff; the reactor-only ' +
          'export preserves semantic object names/tags for Blender inspection.',
      ),
    );

    const stats = el('p', 'hint');
    const refresh = () => {
      const { meshes } = app.built.stats;
      stats.textContent =
        `${app.facility.entities.length} entities · ${meshes} meshes · ` +
        `${app.built.collision.count} colliders`;
    };
    app.onStatus(refresh);
    refresh();
    body.appendChild(stats);
  });
}
