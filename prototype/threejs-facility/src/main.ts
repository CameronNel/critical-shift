import './style.css';
import { createApp } from './core/app';
import { Editor } from './editor/editor';
import { Hud } from './ui/hud';
import { buildEditorUi } from './ui/editorUi';
import { buildDataUi } from './ui/dataUi';
import { loadFacility, loadView, saveView } from './io/persistence';
import { EYE_HEIGHT } from './nav/walkController';
import type { NavMode } from './core/app';

const canvas = document.getElementById('viewport') as HTMLCanvasElement | null;
const ui = document.getElementById('ui');
const boot = document.getElementById('boot');
if (!canvas || !ui) throw new Error('Missing #viewport canvas or #ui container');

const app = createApp(canvas);
const hud = new Hud(app, ui);
const editor = new Editor(app);

hud.registerMode('edit', 'Edit');
buildEditorUi(hud, editor);
buildDataUi(hud, app);

// A locally edited layout wins over the repository default, but only if it
// still validates; otherwise say so rather than starting from a broken map.
const stored = loadFacility();
if (stored.error) hud.toast(stored.error.split('\n')[0], 'error');
if (stored.doc) {
  app.setFacility(stored.doc);
  hud.toast('Loaded your locally saved layout');
}

const view = loadView();
if (view) {
  app.setMode(view.mode as NavMode);
  app.nav.position.set(view.position[0], view.position[1], view.position[2]);
  app.nav.yaw = view.yaw;
  app.nav.pitch = view.pitch;
} else {
  app.respawn();
}

// Remember where you were, so reloading on a phone does not restart the tour.
setInterval(() => {
  saveView({
    mode: app.mode,
    position: [app.nav.position.x, app.nav.position.y, app.nav.position.z],
    yaw: app.nav.yaw,
    pitch: app.nav.pitch,
  });
}, 4000);

// Wheel zoom in map mode; the touch ▲/▼ buttons do the same job on a phone.
canvas.addEventListener(
  'wheel',
  (event) => {
    if (app.mode !== 'map') return;
    event.preventDefault();
    app.map.zoomBy(Math.exp(event.deltaY * 0.0012));
  },
  { passive: false },
);

app.desktop.onShortcut((code) => {
  if (code === 'keyf') app.setMode(app.mode === 'fly' ? 'walk' : 'fly');
  if (code === 'keym') app.setMode(app.mode === 'map' ? 'walk' : 'map');
  if (code === 'keye') app.setMode(app.mode === 'edit' ? 'walk' : 'edit');
  if (code === 'keyr') {
    app.respawn();
    hud.toast('Respawned at the shift entrance');
  }
  if (code === 'escape') {
    hud.togglePanel(false);
    editor.select(null);
  }
});

app.start();
boot?.classList.add('hidden');

// Handy while iterating from a phone or a remote console.
Object.assign(window as unknown as Record<string, unknown>, {
  criticalShift: app,
  criticalShiftEditor: editor,
  EYE_HEIGHT,
});
