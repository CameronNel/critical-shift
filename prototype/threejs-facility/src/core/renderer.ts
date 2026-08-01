import * as THREE from 'three';

export interface Viewport {
  renderer: THREE.WebGLRenderer;
  camera: THREE.PerspectiveCamera;
  canvas: HTMLCanvasElement;
  /** Call after any layout change. */
  resize(): void;
  dispose(): void;
}

/**
 * Renderer tuned for phones: capped pixel ratio, no post-processing, no
 * shadow maps. Legibility of the layout matters more than lighting quality.
 */
export function createViewport(canvas: HTMLCanvasElement): Viewport {
  const renderer = new THREE.WebGLRenderer({
    canvas,
    antialias: window.devicePixelRatio < 2,
    powerPreference: 'high-performance',
  });
  renderer.setClearColor(0x11151a, 1);

  const camera = new THREE.PerspectiveCamera(70, 1, 0.1, 2000);
  camera.position.set(-104, 1.7, 8);

  const resize = () => {
    const w = Math.max(1, canvas.clientWidth || window.innerWidth);
    const h = Math.max(1, canvas.clientHeight || window.innerHeight);
    // 1.75 keeps text sprites crisp without melting mid-range phones.
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.75));
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
  };

  window.addEventListener('resize', resize);
  window.addEventListener('orientationchange', resize);
  resize();

  return {
    renderer,
    camera,
    canvas,
    resize,
    dispose() {
      window.removeEventListener('resize', resize);
      window.removeEventListener('orientationchange', resize);
      renderer.dispose();
    },
  };
}
