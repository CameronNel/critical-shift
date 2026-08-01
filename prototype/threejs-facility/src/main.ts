import './style.css';
import { createApp } from './core/app';
import { Hud } from './ui/hud';

const canvas = document.getElementById('viewport') as HTMLCanvasElement | null;
const ui = document.getElementById('ui');
const boot = document.getElementById('boot');
if (!canvas || !ui) throw new Error('Missing #viewport canvas or #ui container');

const app = createApp(canvas);
const hud = new Hud(app, ui);

app.desktop.onShortcut((code) => {
  if (code === 'keyf') app.setMode(app.mode === 'fly' ? 'walk' : 'fly');
  if (code === 'keyr') {
    app.respawn();
    hud.toast('Respawned at the shift entrance');
  }
  if (code === 'escape') hud.togglePanel(false);
});

app.start();
boot?.classList.add('hidden');

// Handy while iterating from a phone or a remote console.
(window as unknown as Record<string, unknown>).criticalShift = app;
