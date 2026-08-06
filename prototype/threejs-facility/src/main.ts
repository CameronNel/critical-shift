import './style.css';
import { createApp } from './core/app';
import { Editor } from './editor/editor';
import { Hud } from './ui/hud';
import { buildEditorUi } from './ui/editorUi';
import { buildDataUi } from './ui/dataUi';
import { buildReactorUi } from './ui/reactorUi';
import { loadFacility, loadView, saveView } from './io/persistence';
import { EYE_HEIGHT } from './nav/walkController';
import type { NavMode } from './core/app';
import {
  REACTOR_PREVIEW_STATES,
  ReactorPreview,
  type ReactorPreviewState,
} from './reactor/reactorPreview';

const canvas = document.getElementById('viewport') as HTMLCanvasElement | null;
const ui = document.getElementById('ui');
const boot = document.getElementById('boot');
if (!canvas || !ui) throw new Error('Missing #viewport canvas or #ui container');

const params = new URLSearchParams(window.location.search);
const forceRepoDefault = params.get('repo') === '1';
const requestedSpawn = params.get('spawn');
const requestedReactorState = params.get('reactorState');

const app = createApp(canvas);
const hud = new Hud(app, ui);
const editor = new Editor(app);
const reactorPreview = new ReactorPreview(app);

hud.registerMode('edit', 'Edit');
buildEditorUi(hud, editor);
buildDataUi(hud, app);
buildReactorUi(hud, reactorPreview);

// A locally edited layout wins over the repository default unless a shareable
// preview URL explicitly asks for ?repo=1. That makes review links deterministic
// even on a phone/browser that has an old saved greybox in local storage.
if (!forceRepoDefault) {
  const stored = loadFacility();
  if (stored.error) hud.toast(stored.error.split('\n')[0], 'error');
  if (stored.doc) {
    app.setFacility(stored.doc);
    reactorPreview.refresh();
    hud.toast('Loaded your locally saved layout');
  }
}

function teleportFromQuery(): boolean {
  if (!requestedSpawn) return false;
  const normalized = requestedSpawn.trim().toLowerCase();
  const spawn = app.spawns().find((candidate) => {
    return (
      candidate.id.toLowerCase() === normalized ||
      candidate.id.toLowerCase().endsWith(`.${normalized}`) ||
      candidate.zone.toLowerCase() === normalized ||
      candidate.label.toLowerCase() === normalized
    );
  });
  if (!spawn) {
    hud.toast(`Unknown spawn '${requestedSpawn}'`, 'error');
    return false;
  }
  app.teleport(spawn.position, spawn.rotationY);
  hud.toast(`Preview: ${spawn.label}`);
  return true;
}

function stateFromQuery(): ReactorPreviewState | null {
  if (!requestedReactorState) return null;
  const normalized = requestedReactorState.trim().toLowerCase() as ReactorPreviewState;
  return REACTOR_PREVIEW_STATES.includes(normalized) ? normalized : null;
}

// Explicit ?spawn=... wins over persisted camera state. ?repo=1 also skips the
// old view so a shared reactor-review URL always opens where its author meant.
const usedQuerySpawn = teleportFromQuery();
if (!usedQuerySpawn && !forceRepoDefault) {
  const view = loadView();
  if (view) {
    app.setMode(view.mode as NavMode);
    app.nav.position.set(view.position[0], view.position[1], view.position[2]);
    app.nav.yaw = view.yaw;
    app.nav.pitch = view.pitch;
  } else {
    app.respawn();
  }
} else if (!usedQuerySpawn) {
  app.respawn();
}

const queryState = stateFromQuery();
if (queryState) reactorPreview.setState(queryState);
else if (requestedReactorState) hud.toast(`Unknown reactor state '${requestedReactorState}'`, 'error');
reactorPreview.start();

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

// Handy while iterating from a phone, MCP session or remote console.
Object.assign(window as unknown as Record<string, unknown>, {
  criticalShift: app,
  criticalShiftEditor: editor,
  criticalShiftReactor: reactorPreview,
  EYE_HEIGHT,
});
