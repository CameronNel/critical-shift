import './style.css';
import * as THREE from 'three';
import { createApp } from './core/app';

const canvas = document.getElementById('viewport') as HTMLCanvasElement | null;
const boot = document.getElementById('boot');

if (!canvas) throw new Error('Missing #viewport canvas');

const app = createApp(canvas);

// Temporary orientation aid until the facility builder lands.
const grid = new THREE.GridHelper(320, 32, 0x4a5866, 0x2e3843);
grid.position.set(0, 0.01, 0);
app.site.layers.ground.add(grid);

app.start();
boot?.classList.add('hidden');
