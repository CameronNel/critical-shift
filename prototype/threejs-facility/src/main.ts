import './style.css';
import { createApp } from './core/app';

const canvas = document.getElementById('viewport') as HTMLCanvasElement | null;
const boot = document.getElementById('boot');
if (!canvas) throw new Error('Missing #viewport canvas');

const app = createApp(canvas);

app.desktop.onShortcut((code) => {
  if (code === 'keyf') app.setMode(app.mode === 'fly' ? 'walk' : 'fly');
  if (code === 'keyr') app.respawn();
});

app.start();
boot?.classList.add('hidden');

// Handy while iterating from a phone or a remote console.
(window as unknown as Record<string, unknown>).criticalShift = app;
