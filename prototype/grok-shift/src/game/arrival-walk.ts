import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import {
  BOARD,
  CLOSE_BTN,
  CRATE,
  LEVER,
  HOLES,
  type BlastHud,
  type HoleId,
  effectiveGrams,
  judge,
  rollMood,
  targetGrams,
} from "@/game/mine-blast";
import {
  STATIONS,
  createHaulage,
  takeOre,
  grabCart,
  promptHaul,
  massOf,
  cartPos,
  tickDose,
  pushCart,
  HAND_SPEED,
} from "@/game/haulage";

const EYE = 1.6;
const WALK = 4.2;
const SPRINT = 7.4;
const RADIUS = 0.34;
const SPAWN = { x: 0, y: EYE, z: -1.8 };
const GAME_KEYS = new Set([
  "KeyW",
  "KeyA",
  "KeyS",
  "KeyD",
  "ArrowUp",
  "ArrowLeft",
  "ArrowDown",
  "ArrowRight",
  "KeyQ",
  "KeyE",
  "ShiftLeft",
  "ShiftRight",
  "Space",
  "KeyF",
]);

type Aabb = { minX: number; maxX: number; minZ: number; maxZ: number };

const T = 0.28;
const COLLIDERS: Aabb[] = [
  // hall back / front
  { minX: -2.7, maxX: 2.7, minZ: -0.25, maxZ: 0.2 },
  // hall end posts (door is open)
  { minX: -2.7, maxX: -1.05, minZ: -14.15, maxZ: -13.65 },
  { minX: 1.05, maxX: 2.7, minZ: -14.15, maxZ: -13.65 },
  // hall left, gap z -5.2..-11.2
  { minX: -2.5 - T, maxX: -2.5 + T, minZ: -5.2, maxZ: 0.1 },
  { minX: -2.5 - T, maxX: -2.5 + T, minZ: -14.1, maxZ: -11.2 },
  // hall right, same gap
  { minX: 2.5 - T, maxX: 2.5 + T, minZ: -5.2, maxZ: 0.1 },
  { minX: 2.5 - T, maxX: 2.5 + T, minZ: -14.1, maxZ: -11.2 },
  // briefing room (left)
  { minX: -11.7, maxX: -11.3, minZ: -12.4, maxZ: -4.0 },
  { minX: -11.7, maxX: -2.4, minZ: -4.4, maxZ: -4.0 },
  { minX: -11.7, maxX: -2.4, minZ: -12.45, maxZ: -12.05 },
  { minX: -7.4, maxX: -3.4, minZ: -9.3, maxZ: -7.1 }, // table
  // locker room (right)
  { minX: 10.3, maxX: 10.75, minZ: -12.4, maxZ: -4.0 },
  { minX: 2.4, maxX: 10.7, minZ: -4.4, maxZ: -4.0 },
  { minX: 2.4, maxX: 10.7, minZ: -12.45, maxZ: -12.05 },
  { minX: 9.2, maxX: 10.5, minZ: -10.4, maxZ: -6.1 }, // suit locker
  // integrity tube base (walk into the glass)
  { minX: 6.9, maxX: 7.7, minZ: -8.4, maxZ: -7.7 }, // pedestal
  // dosimeter cabinet at exit
  { minX: -1.85, maxX: -1.25, minZ: -13.55, maxZ: -13.1 },
  // S1 corridor — left mine, right solid, straight haulage
  { minX: -2.75, maxX: -2.3, minZ: -16.2, maxZ: -13.9 },
  { minX: -2.75, maxX: -2.3, minZ: -22.2, maxZ: -21.2 },
  { minX: 2.3, maxX: 2.75, minZ: -22.2, maxZ: -13.9 },
  // staging bay (open off S1)
  { minX: -8.2, maxX: -2.4, minZ: -15.0, maxZ: -14.45 },
  { minX: -8.2, maxX: -2.4, minZ: -22.95, maxZ: -22.45 },
  { minX: -5.25, maxX: -3.95, minZ: -15.85, maxZ: -15.0 }, // tnt crate
  { minX: -6.9, maxX: -4.7, minZ: -22.6, maxZ: -21.9 }, // picks
  // blast door jambs (opening is z -21.2..-16.2)
  { minX: -8.25, maxX: -7.85, minZ: -16.2, maxZ: -14.5 },
  { minX: -8.25, maxX: -7.85, minZ: -22.9, maxZ: -21.2 },
  // drift 50 m
  { minX: -48.2, maxX: -8.0, minZ: -16.45, maxZ: -15.95 },
  { minX: -48.2, maxX: -8.0, minZ: -21.45, maxZ: -20.95 },
  // working chamber
  { minX: -58.5, maxX: -57.8, minZ: -22.9, maxZ: -14.5 },
  { minX: -58.2, maxX: -48.0, minZ: -15.0, maxZ: -14.45 },
  { minX: -58.2, maxX: -48.0, minZ: -22.95, maxZ: -22.45 },
  { minX: -48.25, maxX: -47.75, minZ: -16.2, maxZ: -14.5 },
  { minX: -48.25, maxX: -47.75, minZ: -22.9, maxZ: -21.2 },
  { minX: -56.4, maxX: -54.4, minZ: -21.2, maxZ: -19.6 }, // drill
  // haulage hall
  { minX: -9.25, maxX: -8.75, minZ: -46.0, maxZ: -22.1 },
  { minX: -9.25, maxX: -8.75, minZ: -56.6, maxZ: -50.0 },
  { minX: 8.75, maxX: 9.25, minZ: -36.0, maxZ: -22.1 },
  { minX: 8.75, maxX: 9.25, minZ: -56.6, maxZ: -44.0 },
  { minX: -9.1, maxX: -2.4, minZ: -22.35, maxZ: -21.85 },
  { minX: 2.4, maxX: 9.1, minZ: -22.35, maxZ: -21.85 },
  { minX: -9.1, maxX: -2.3, minZ: -56.75, maxZ: -56.25 },
  { minX: 2.3, maxX: 9.1, minZ: -56.75, maxZ: -56.25 },
  { minX: -8.2, maxX: -5.1, minZ: -31.3, maxZ: -28.7 }, // winch
  { minX: 6.1, maxX: 8.7, minZ: -37.5, maxZ: -34.5 }, // booth
  { minX: -2.2, maxX: 2.2, minZ: -55.9, maxZ: -53.2 }, // dump / intake
  { minX: 6.5, maxX: 8.3, minZ: -27.5, maxZ: -25.3 }, // tool crib
  { minX: -8.5, maxX: -5.9, minZ: -29.2, maxZ: -26.0 }, // spares
  { minX: -7.1, maxX: -3.7, minZ: -25.7, maxZ: -23.1 }, // load deck
];

const extraColliders: Aabb[] = [];
const cartColliders: Aabb[] = [];
const DOOR_BOX: Aabb = { minX: -8.3, maxX: -7.8, minZ: -21.2, maxZ: -16.2 };
const RUBBLE_BOX: Aabb = { minX: -10.2, maxX: -7.6, minZ: -21.0, maxZ: -16.4 };

function collides(x: number, z: number) {
  for (const list of [COLLIDERS, extraColliders, cartColliders]) {
    for (const b of list) {
      if (x + RADIUS > b.minX && x - RADIUS < b.maxX && z + RADIUS > b.minZ && z - RADIUS < b.maxZ) {
        return true;
      }
    }
  }
  return false;
}

export type WalkHandle = {
  stop: () => void;
  getPos: () => { x: number; y: number; z: number };
  getYaw: () => number;
  setHeld: (codes: string[]) => void;
  interact: () => void;
  getHud: () => BlastHud;
};

export function startArrivalWalk(canvas: HTMLCanvasElement): WalkHandle {
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(canvas.clientWidth || 1280, canvas.clientHeight || 800, false);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.25;
  renderer.setClearColor(0x0b1114, 1);

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x12181c);
  scene.fog = new THREE.Fog(0x12181c, 18, 90);
  const camera = new THREE.PerspectiveCamera(72, 1, 0.08, 180);
  camera.position.set(SPAWN.x, SPAWN.y, SPAWN.z);
  camera.rotation.order = "YXZ";
  camera.rotation.set(-0.04, 0, 0);

  scene.add(new THREE.HemisphereLight(0xd0e4ee, 0x1b1814, 1.2));
  const sun = new THREE.DirectionalLight(0xfff3d8, 1.7);
  sun.position.set(18, 16, -8);
  scene.add(sun);
  const fill = new THREE.DirectionalLight(0x7fcae0, 0.55);
  fill.position.set(8, 5, -8);
  scene.add(fill);
  let blastDoor: THREE.Object3D | null = null;
  const faceMeshes: THREE.Object3D[] = [];
  const cartRoot = new THREE.Group();
  scene.add(cartRoot);
  const workCart: THREE.Object3D[] = [];
  for (const p of [
    [0, 3.4, -3],
    [0, 3.4, -8],
    [-5.4, 3.3, -8.2],
    [0, 3.2, -18],
    [-5, 3.0, -18.7],
    [-12, 2.4, -18.7],
    [-20, 2.2, -18.7],
    [-28, 2.2, -18.7],
    [-36, 2.2, -18.7],
    [-44, 2.2, -18.7],
    [-52, 2.4, -18.7],
    [0, 3.6, -28],
    [0, 5.5, -36],
    [0, 5.5, -44],
    [0, 5.5, -52],
  ] as const) {
    const l = new THREE.PointLight(0xb8f0f4, 22, 10, 2);
    l.position.set(p[0], p[1], p[2]);
    scene.add(l);
  }

  new GLTFLoader().load("/models/arrival.glb", (gltf) => {
    gltf.scene.traverse((obj) => {
      const mesh = obj as THREE.Mesh;
      if (!mesh.isMesh) return;
      if (mesh.name.includes("BlastDoor") && !mesh.name.includes("Haz")) blastDoor = mesh;
      if (mesh.name.includes("MineFace") || mesh.name.includes("FaceBump") || mesh.name.startsWith("Vein")) {
        faceMeshes.push(mesh);
      }
      if (mesh.name.startsWith("WorkCart")) workCart.push(mesh);
      const mats = Array.isArray(mesh.material) ? mesh.material : [mesh.material];
      for (const mat of mats) {
        const std = mat as THREE.MeshStandardMaterial;
        if (mesh.name.includes("Glass")) {
          std.transparent = true;
          std.opacity = 0.18;
          std.depthWrite = false;
          std.emissive = new THREE.Color(0x3ad4e6);
          std.emissiveIntensity = 0.7;
          std.roughness = 0.08;
          std.metalness = 0.05;
        } else if (mesh.name.includes("Vein") || mesh.name.includes("Ore") || mesh.name.includes("CartLoad")) {
          std.emissive = new THREE.Color(0x88cc22);
          std.emissiveIntensity = 1.6;
        } else if (mesh.name.includes("Core") || mesh.name.includes("FuelSlot") || mesh.name.includes("DrySteam")) {
          std.emissive = new THREE.Color(mesh.name.includes("Fuel") ? 0xe0a020 : 0x3ee6a0);
          std.emissiveIntensity = 1.8;
        } else if (std.emissive && (std.emissive.r > 0.05 || std.emissive.g > 0.05)) {
          std.emissiveIntensity = 2.2;
        }
      }
    });
    scene.add(gltf.scene);
    for (const m of workCart) {
      const w = new THREE.Vector3();
      m.getWorldPosition(w);
      m.parent?.remove(m);
      cartRoot.add(m);
      m.position.set(w.x + 52, w.y, w.z + 18.7);
    }
    cartRoot.position.set(-52, 0, -18.7);
  });

  const mood = rollMood();
  const target = targetGrams(mood);
  let carried = 0;
  const placed: Record<HoleId, number> = { low: 0, mid: 0, high: 0 };
  let doorClosed = false;
  let blasted = false;
  let fuseLive = false;
  let fuseLeft = 0;
  const haul = createHaulage();
  let result = "";
  let readBoard = false;
  let fWas = false;
  const stickGroup = new THREE.Group();
  scene.add(stickGroup);
  const rubbleGroup = new THREE.Group();
  scene.add(rubbleGroup);

  const dist = (ax: number, az: number, bx: number, bz: number) => Math.hypot(ax - bx, az - bz);

  const nearest = (pos: THREE.Vector3) => {
    type Hit = { id: string; d: number; label: string };
    const hits: Hit[] = [
      { id: "crate", d: dist(pos.x, pos.z, CRATE.x, CRATE.z), label: "tnt crate" },
      { id: "board", d: dist(pos.x, pos.z, BOARD.x, BOARD.z), label: "form 7-B" },
    ];
    if (pos.x > -7.85) {
      hits.push({ id: "close", d: dist(pos.x, pos.z, CLOSE_BTN.x, CLOSE_BTN.z), label: "close" });
      hits.push({ id: "lever", d: dist(pos.x, pos.z, LEVER.x, LEVER.z), label: "lever" });
    }
    for (const [id, s] of Object.entries(STATIONS)) {
      hits.push({ id, d: dist(pos.x, pos.z, s.x, s.z), label: s.label });
    }
    {
      const p = cartPos(haul);
      hits.push({ id: "cart", d: dist(pos.x, pos.z, p.x, p.z), label: "mine cart" });
    }
    for (const h of HOLES) {
      const reach = h.id === "high" ? 2.6 : 1.7;
      const d = dist(pos.x, pos.z, h.x, h.z);
      if (d < reach + 0.4) hits.push({ id: `hole:${h.id}`, d, label: h.label });
    }
    hits.sort((a, b) => a.d - b.d);
    return hits[0] && hits[0].d < 2.4 ? hits[0] : null;
  };

  const inMine = (pos: THREE.Vector3) => pos.x < -8.1;

  const promptFor = (pos: THREE.Vector3) => {
    if (fuseLive) {
      const n = nearest(pos);
      const fuse = `FUSE ${Math.ceil(fuseLeft)}s` + (doorClosed ? " — door shut." : " — BLAST DOOR OPEN. CONSEQUENCES MAY FOLLOW.");
      if (n?.id === "close") return (doorClosed ? "F — open the blast door. " : "F — close the blast door. ") + fuse;
      return fuse;
    }
    const n = nearest(pos);
    if (n && (n.id in STATIONS || n.id === "cart")) return promptHaul(haul, n.id);
    if (blasted) return result;
    if (!n) return haul.line || (readBoard ? mood.hint : "Hold W. Left mine. Straight haulage: pick ore, load, release brake, follow to intake.");
    if (n.id === "board") return "F — steal the toilets card (today's rock mood)";
    if (n.id === "crate") return carried >= 8 ? "Pockets full. Compliance is already weeping." : `F — take a stick (100g, 'or 87g if the rain got in'). Holding ${carried}`;
    if (n.id.startsWith("hole:")) {
      const id = n.id.slice(5) as HoleId;
      if (carried <= 0) return `The ${n.label} is empty of you. Grab TNT first.`;
      return `F — stuff a stick in the ${n.label} (${placed[id]} in)`;
    }
    if (n.id === "close") {
      if (pos.x <= -7.85) return "Button is on the staging side of the door.";
      return doorClosed ? "F — open the blast door" : "F — close the blast door";
    }
    if (n.id === "lever") {
      if (blasted) return result || "Already fired.";
      const grams = effectiveGrams(placed);
      if (grams <= 0) return "Lever is decorative until there is TNT in a hole.";
      return `F — pull the blast lever (${Math.round(grams)}g). 5s fuse. Door may be open.`;
    }
    return haul.line || "";
  };

  const addStickMesh = (hole: HoleId, count: number) => {
    const spec = HOLES.find((h) => h.id === hole)!;
    const m = new THREE.Mesh(
      new THREE.BoxGeometry(0.1, 0.1, 0.35),
      new THREE.MeshStandardMaterial({ color: 0xc41e12, emissive: 0x4a0808, roughness: 0.5 }),
    );
    m.position.set(spec.x + 0.15, spec.y - 0.05 + count * 0.08, spec.z);
    stickGroup.add(m);
  };

  const setDoor = (closed: boolean) => {
    doorClosed = closed;
    extraColliders.length = 0;
    if (closed) extraColliders.push(DOOR_BOX);
    if (blastDoor) blastDoor.position.y = closed ? 1.75 : 5.35;
  };

  const spawnOre = (count: number, spread: number) => {
    const mat = new THREE.MeshStandardMaterial({ color: 0x8ccc28, emissive: 0x446611, emissiveIntensity: 1.2 });
    for (let i = 0; i < count; i++) {
      const m = new THREE.Mesh(new THREE.BoxGeometry(0.35 + Math.random() * 0.4, 0.25 + Math.random() * 0.3, 0.3), mat);
      m.position.set(-54.2 + (Math.random() - 0.5) * spread, 0.22 + Math.random() * 0.25, -18.7 + (Math.random() - 0.5) * 2);
      rubbleGroup.add(m);
    }
  };

  const spawnRubble = () => {
    const mat = new THREE.MeshStandardMaterial({ color: 0x3a342c, roughness: 0.9 });
    for (let i = 0; i < 14; i++) {
      const m = new THREE.Mesh(
        new THREE.BoxGeometry(0.5 + Math.random(), 0.4 + Math.random() * 0.8, 0.5 + Math.random()),
        mat,
      );
      m.position.set(-8.8 - Math.random() * 2.2, 0.35 + Math.random() * 0.6, -16.6 - Math.random() * 4.4);
      m.rotation.y = Math.random() * 2;
      rubbleGroup.add(m);
    }
    extraColliders.push(RUBBLE_BOX);
  };

  const detonate = (pos: THREE.Vector3) => {
    if (blasted) return;
    const grams = effectiveGrams(placed);
    if (grams <= 0) {
      result = "You mashed the plunger. Nothing. The rock yawned.";
      return;
    }
    blasted = true;
    const verdict = judge(grams, target, placed.high > 0, doorClosed, inMine(pos));
    result = verdict.line;
    for (const mesh of faceMeshes) mesh.position.x -= verdict.opening;
    if (verdict.outcome === "under") {
      spawnOre(2, 0.8);
      haul.stock += 2;
    }
    if (verdict.outcome === "good") {
      spawnOre(7, 1.6);
      haul.stock += 5;
    }
    if (verdict.outcome === "over" || verdict.outcome === "tourist") {
      spawnOre(2, 1.2);
      spawnRubble();
      haul.stock += 1;
    }
  };

  const interact = () => {
    const pos = camera.position;
    const n = nearest(pos);
    if (!n) return;
    if (n.id === "close") {
      setDoor(!doorClosed);
      return;
    }
    if (blasted) return;
    if (n.id === "board") {
      readBoard = true;
      result = `Today the rock is ${mood.title}.`;
      return;
    }
    if (n.id === "crate") {
      if (carried < 8) carried += 1;
      return;
    }
    if (n.id.startsWith("hole:")) {
      if (carried <= 0) return;
      const id = n.id.slice(5) as HoleId;
      carried -= 1;
      placed[id] += 1;
      addStickMesh(id, placed[id]);
      return;
    }
    if (n.id === "lever") {
      if (!fuseLive && !blasted) {
        const grams = effectiveGrams(placed);
        if (grams <= 0) {
          result = "Put TNT in a hole first.";
          return;
        }
        fuseLive = true;
        fuseLeft = 5;
        result = doorClosed
          ? "FUSE LIT — 5s. Door is shut."
          : "FUSE LIT — 5s. BLAST DOOR IS OPEN. CONSEQUENCES MAY FOLLOW.";
      }
      return;
    }
    if (n.id === "pile") {
      takeOre(haul, blasted && placed.high > 0);
      result = haul.line;
      return;
    }
    if (n.id === "cart" || n.id === "intake") {
      grabCart(haul);
      result = haul.line;
      return;
    }
    if (n.id === "weigh" || n.id === "winch" || n.id === "marshal" || n.id === "spares" || n.id === "access") {
      result = promptHaul(haul, n.id);
    }
  };

  const getHud = (): BlastHud => ({
    prompt: promptFor(camera.position),
    hint: haul.held
      ? "ORE IN HANDS. Dose climbing. Put it in the cart."
      : haul.grabbing
        ? "Pushing the cart. Walk. Rails only."
        : "Deep face. Ore burns. One cart. Push it to intake.",
    mood: mood.title,
    carried,
    placed: placed.low + placed.mid + placed.high,
    doorClosed,
    result,
    fuse: fuseLive ? fuseLeft : 0,
    doorOpenAlert: fuseLive && !doorClosed,
    oreHeld: haul.held ? 1 : 0,
    cartCargo: haul.cargo.length,
    cartMass: massOf(haul),
    dumped: haul.dumped,
    brakeOn: !haul.grabbing,
    dose: haul.dose,
    grabbing: haul.grabbing,
  });


  const keys = new Set<string>();
  const heldOverride = new Set<string>();
  let yaw = 0;
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

  const applyLook = (dx: number, dy: number) => {
    yaw -= dx * 0.0025;
    pitch -= dy * 0.0025;
    pitch = Math.max(-1.15, Math.min(1.15, pitch));
    syncCamera();
  };

  const pressed = (code: string) => keys.has(code) || heldOverride.has(code);
  const onKeyDown = (e: KeyboardEvent) => {
    keys.add(e.code);
    if (GAME_KEYS.has(e.code)) e.preventDefault();
  };
  const onKeyUp = (e: KeyboardEvent) => keys.delete(e.code);
  const clearKeys = () => keys.clear();
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
    if (dragging) applyLook(e.movementX, e.movementY);
  };

  window.addEventListener("keydown", onKeyDown);
  window.addEventListener("keyup", onKeyUp);
  window.addEventListener("blur", clearKeys);
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
    const fNow = pressed("KeyF") || pressed("Space");
    if (fNow && !fWas) interact();
    fWas = fNow;
    if (fuseLive) {
      fuseLeft -= dt;
      if (fuseLeft <= 0) {
        fuseLive = false;
        fuseLeft = 0;
        detonate(camera.position);
      }
    }
    tickDose(haul, dt);
    if (haul.line) result = haul.line;
    const p = cartPos(haul);
    cartRoot.position.set(p.x, 0, p.z);
    cartRoot.rotation.y = p.yaw - Math.PI / 2;
    cartColliders.length = 0;
    if (!haul.grabbing) {
      cartColliders.push({ minX: p.x - 1.2, maxX: p.x + 1.2, minZ: p.z - 0.85, maxZ: p.z + 0.85 });
    }
    syncCamera();

    if (haul.stunned > 0) {
      renderer.render(scene, camera);
      raf = requestAnimationFrame(tick);
      return;
    }

    const carrying = !!haul.held;
    const radSlow = haul.dose > 70 ? 0.65 : haul.dose > 40 ? 0.85 : 1;
    const speed = carrying
      ? HAND_SPEED * radSlow
      : (pressed("ShiftLeft") || pressed("ShiftRight") ? SPRINT : WALK) * radSlow;
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
      const mx = fx * az + rx * ax;
      const mz = fz * az + rz * ax;
      if (haul.grabbing) {
        pushCart(haul, mx, mz, dt);
        const np = cartPos(haul);
        camera.position.x = np.x - Math.sin(np.yaw) * 1.4;
        camera.position.z = np.z - Math.cos(np.yaw) * 1.4;
        camera.position.y = EYE;
        cartRoot.position.set(np.x, 0, np.z);
        cartRoot.rotation.y = np.yaw - Math.PI / 2;
      } else {
        const nx = camera.position.x + mx * speed * dt;
        const nz = camera.position.z + mz * speed * dt;
        if (!collides(nx, camera.position.z)) camera.position.x = nx;
        if (!collides(camera.position.x, nz)) camera.position.z = nz;
        camera.position.y = EYE;
      }
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
      window.removeEventListener("blur", clearKeys);
      canvas.removeEventListener("pointerdown", onPointerDown);
      canvas.removeEventListener("pointerup", onPointerUp);
      canvas.removeEventListener("pointercancel", onPointerUp);
      canvas.removeEventListener("pointermove", onPointerMove);
      renderer.dispose();
    },
    getPos: () => ({ x: camera.position.x, y: camera.position.y, z: camera.position.z }),
    getYaw: () => yaw,
    setHeld(codes: string[]) {
      heldOverride.clear();
      for (const c of codes) heldOverride.add(c);
    },
    interact,
    getHud,
  };

  (window as Window & { __controlsTest?: unknown }).__controlsTest = {
    getYaw: () => yaw,
    getSpeed: () => (pressed("KeyW") ? WALK : 0),
    setKeys: (codes: string[]) => handle.setHeld(codes),
    interact: () => handle.interact(),
    getHud: () => handle.getHud(),
  };

  return handle;
}
