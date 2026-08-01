import * as THREE from 'three';
import { createViewport, type Viewport } from './renderer';
import { createSiteScene, type SiteScene } from './scene';
import { InputState } from '../input/inputState';
import { createDesktopInput, type DesktopInput } from '../input/desktopInput';
import { FlyController } from '../nav/flyController';
import { applyToCamera, createNavState, type NavState } from '../nav/navState';

export type NavMode = 'walk' | 'fly' | 'map';

export interface App {
  viewport: Viewport;
  site: SiteScene;
  input: InputState;
  desktop: DesktopInput;
  nav: NavState;
  mode: NavMode;
  start(): void;
}

export function createApp(canvas: HTMLCanvasElement): App {
  const viewport = createViewport(canvas);
  const site = createSiteScene();
  const input = new InputState();
  const desktop = createDesktopInput(canvas, input);
  const nav = createNavState(new THREE.Vector3(-104, 1.7, 10), Math.PI);
  const fly = new FlyController();

  canvas.addEventListener('click', () => desktop.requestLook());

  const clock = new THREE.Clock();
  let running = false;

  const frame = () => {
    if (!running) return;
    requestAnimationFrame(frame);
    const dt = Math.min(clock.getDelta(), 0.05);
    fly.update(dt, input, nav);
    applyToCamera(nav, viewport.camera);
    input.clearFrame();
    viewport.renderer.render(site.scene, viewport.camera);
  };

  return {
    viewport,
    site,
    input,
    desktop,
    nav,
    mode: 'fly',
    start() {
      if (running) return;
      running = true;
      clock.start();
      requestAnimationFrame(frame);
    },
  };
}
