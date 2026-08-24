import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";

const EYE = 1.6;
const WALK = 4.2;
const SPRINT = 7.4;
const RADIUS = 0.4;
const SPAWN = { x: -15.2, y: EYE, z: 0 };
const YAW0 = -Math.PI / 2;

type Aabb = { minX: number; maxX: number; minZ: number; maxZ: number };

const COLLIDERS: Aabb[] = [
  // west wall, adit gap z -4.5..4.5
  { minX: -17.05, maxX: -16.55, minZ: 4.55, maxZ: 16.9 },
  { minX: -17.05, maxX: -16.55, minZ: -16.9, maxZ: -4.55 },
  // north wall, crusher gap ~3..10, worker ~12.4..16.4
  { minX: -16.9, maxX: 2.75, minZ: 16.55, maxZ: 17.05 },
  { minX: 10.15, maxX: 12.45, minZ: 16.55, maxZ: 17.05 },
  { minX: 16.35, maxX: 16.9, minZ: 16.55, maxZ: 17.05 },
  // east wall
  { minX: 16.55, maxX: 17.05, minZ: -16.9, maxZ: -10.35 },
  { minX: 16.55, maxX: 17.05, minZ: -6.45, maxZ: -2.35 },
  { minX: 16.55, maxX: 17.05, minZ: 4.75, maxZ: 16.9 },
  // south wall, door at x -2.2..2.2
  { minX: -16.9, maxX: -2.15, minZ: -17.05, maxZ: -16.55 },
  { minX: 2.15, maxX: 16.9, minZ: -17.05, maxZ: -16.55 },
  // winch
  { minX: -13.7, maxX: -10.3, minZ: 13.1, maxZ: 15.7 },
  // booth
  { minX: -2.2, maxX: 2.2, minZ: 12.9, maxZ: 16.0 },
  // carts
  { minX: -3.5, maxX: -1.3, minZ: 10.9, maxZ: 13.1 },
  { minX: 10.9, maxX: 13.1, minZ: -2.3, maxZ: 0.1 },
  { minX: -9.5, maxX: -7.3, minZ: -13.1, maxZ: -10.9 },
  // dump chute
  { minX: 5.3, maxX: 7.9, minZ: 15.5, maxZ: 16.9 },
  // tool crib / drums
  { minX: 13.3, maxX: 15.1, minZ: -15.2, maxZ: -12.8 },
  { minX: -15.5, maxX: -13.3, minZ: -15.2, maxZ: -13.9 },
  // deck legs (walk under the deck)
  { minX: -2.8, maxX: -2.4, minZ: 3.0, maxZ: 3.4 },
  { minX: 2.4, maxX: 2.8, minZ: 3.0, maxZ: 3.4 },
  { minX: -2.8, maxX: -2.4, minZ: -3.4, maxZ: -3.0 },
  { minX: 2.4, maxX: 2.8, minZ: -3.4, maxZ: -3.0 },
];

function collides(x: number, z: number) {
  for (const b of COLLIDERS) {
    if (x + RADIUS > b.minX && x - RADIUS < b.maxX && z + RADIUS > b.minZ && z - RADIUS < b.maxZ) return true;
  }
  return false;
}

export type WalkHandle = {
  stop: () => void;
  getPos: () => { x: number; y: number; z: number };
  getYaw: () => number;
  setHeld: (codes: string[]) => void;
  interact: () => void;
  getHud: () => { prompt: string; hint: string };
};

export function startHaulageWalk(canvas: HTMLCanvasElement): WalkHandle {
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(canvas.clientWidth || 1280, canvas.clientHeight || 800, false);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.15;
  renderer.setClearColor(0x0b1114, 1);

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x14110e);
  scene.fog = new THREE.Fog(0x14110e, 28, 70);
  const camera = new THREE.PerspectiveCamera(70, 1, 0.08, 120);
  camera.position.set(SPAWN.x, SPAWN.y, SPAWN.z);
  camera.rotation.order = "YXZ";

  scene.add(new THREE.HemisphereLight(0xc8d4dc, 0x1a1612, 1.05));
  const sun = new THREE.DirectionalLight(0xffe6c0, 1.15);
  sun.position.set(-8, 18, 10);
  scene.add(sun);
  for (const p of [
    [-12, 6.8, 12],
    [12, 6.8, 12],
    [-12, 6.8, -12],
    [12, 6.8, -12],
    [0, 6.5, 0],
    [6.6, 5.5, 14],
  ] as const) {
    const l = new THREE.PointLight(0xc9e8ee, 28, 16, 2);
    l.position.set(p[0], p[1], p[2]);
    scene.add(l);
  }

  new GLTFLoader().load("/models/haulage.glb", (gltf) => {
    gltf.scene.traverse((obj) => {
      const mesh = obj as THREE.Mesh;
      if (!mesh.isMesh) return;
      const mats = Array.isArray(mesh.material) ? mesh.material : [mesh.material];
      for (const mat of mats) {
        const std = mat as THREE.MeshStandardMaterial;
        if (mesh.name.includes("Glass")) {
          std.transparent = true;
          std.opacity = 0.2;
          std.depthWrite = false;
          std.emissive = new THREE.Color(0x3ad4e6);
          std.emissiveIntensity = 0.6;
        } else if (mesh.name.includes("Ore") || mesh.name.includes("load")) {
          std.emissive = new THREE.Color(0x88cc22);
          std.emissiveIntensity = 1.3;
        } else if (std.emissive && (std.emissive.r > 0.05 || std.emissive.g > 0.05)) {
          std.emissiveIntensity = 2.0;
        }
      }
    });
    scene.add(gltf.scene);
  });

  const keys = new Set<string>();
  const heldOverride = new Set<string>();
  let yaw = YAW0;
  let pitch = -0.04;
  let dragging = false;
  let last = performance.now();
  let raf = 0;
  let running = true;

  const syncCamera = () => {
    camera.rotation.order = "YXZ";
    camera.rotation.y = yaw;
    camera.rotation.x = pitch;
  };
  syncCamera();

  const pressed = (code: string) => keys.has(code) || heldOverride.has(code);
  const onKeyDown = (e: KeyboardEvent) => {
    keys.add(e.code);
    if (["KeyW", "KeyA", "KeyS", "KeyD", "KeyQ", "KeyE", "ShiftLeft", "ShiftRight"].includes(e.code)) e.preventDefault();
  };
  const onKeyUp = (e: KeyboardEvent) => keys.delete(e.code);
  const onPointerDown = (e: PointerEvent) => {
    dragging = true;
    canvas.setPointerCapture(e.pointerId);
    canvas.focus();
  };
  const onPointerUp = (e: PointerEvent) => {
    dragging = false;
    try {
      canvas.releasePointerCapture(e.pointerId);
    } catch {
      /* ignore */
    }
  };
  const onPointerMove = (e: PointerEvent) => {
    if (!dragging) return;
    yaw -= e.movementX * 0.0025;
    pitch = Math.max(-1.15, Math.min(1.15, pitch - e.movementY * 0.0025));
    syncCamera();
  };

  window.addEventListener("keydown", onKeyDown);
  window.addEventListener("keyup", onKeyUp);
  canvas.addEventListener("pointerdown", onPointerDown);
  canvas.addEventListener("pointerup", onPointerUp);
  canvas.addEventListener("pointercancel", onPointerUp);
  canvas.addEventListener("pointermove", onPointerMove);

  const tick = (now: number) => {
    if (!running) return;
    const dt = Math.min(0.05, (now - last) / 1000);
    last = now;
    if (pressed("KeyQ")) yaw += 1.7 * dt;
    if (pressed("KeyE")) yaw -= 1.7 * dt;
    syncCamera();
    const speed = pressed("ShiftLeft") || pressed("ShiftRight") ? SPRINT : WALK;
    let ax = 0;
    let az = 0;
    if (pressed("KeyW") || pressed("ArrowUp")) az += 1;
    if (pressed("KeyS") || pressed("ArrowDown")) az -= 1;
    if (pressed("KeyA") || pressed("ArrowLeft")) ax -= 1;
    if (pressed("KeyD") || pressed("ArrowRight")) ax += 1;
    const mag = Math.hypot(ax, az);
    if (mag > 0) {
      ax /= mag;
      az /= mag;
      const fx = -Math.sin(yaw);
      const fz = -Math.cos(yaw);
      const rx = Math.cos(yaw);
      const rz = -Math.sin(yaw);
      const nx = camera.position.x + (fx * az + rx * ax) * speed * dt;
      const nz = camera.position.z + (fz * az + rz * ax) * speed * dt;
      if (!collides(nx, camera.position.z)) camera.position.x = nx;
      if (!collides(camera.position.x, nz)) camera.position.z = nz;
    }
    const w = canvas.clientWidth;
    const h = canvas.clientHeight;
    if (w && h) {
      const ratio = w / h;
      if (Math.abs(camera.aspect - ratio) > 0.01) {
        camera.aspect = ratio;
        camera.updateProjectionMatrix();
      }
      renderer.setSize(w, h, false);
    }
    renderer.render(scene, camera);
    raf = requestAnimationFrame(tick);
  };
  raf = requestAnimationFrame(tick);

  const handle: WalkHandle = {
    stop() {
      running = false;
      cancelAnimationFrame(raf);
      window.removeEventListener("keydown", onKeyDown);
      window.removeEventListener("keyup", onKeyUp);
      canvas.removeEventListener("pointerdown", onPointerDown);
      canvas.removeEventListener("pointerup", onPointerUp);
      canvas.removeEventListener("pointercancel", onPointerUp);
      canvas.removeEventListener("pointermove", onPointerMove);
      renderer.dispose();
    },
    getPos: () => ({ x: camera.position.x, y: camera.position.y, z: camera.position.z }),
    getYaw: () => yaw,
    setHeld(codes) {
      heldOverride.clear();
      for (const c of codes) heldOverride.add(c);
    },
    interact() {},
    getHud: () => ({
      prompt: "Cross the loop between carts. North spur is the crusher. West door is the mine.",
      hint: "Haulage · 34 m hall · cart loop is live. Crossing the floor is a timing problem.",
    }),
  };
  (window as Window & { __controlsTest?: unknown }).__controlsTest = {
    setKeys: (codes: string[]) => handle.setHeld(codes),
    getHud: () => handle.getHud(),
  };
  return handle;
}
