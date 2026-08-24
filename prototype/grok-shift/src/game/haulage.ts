/** One cart, pushed by hand. Ore in your hands is a dose. Cart is the shield. */

export const ORE_QUOTA = 3;
export const RATED_MASS = 12;
export const DRY_MASS = 0.85;
export const WET_MASS = 1.35;
export const HAND_RAD = 9;
export const WET_RAD = 14;
export const CART_SPEED = 3.4;
export const HAND_SPEED = 2.3;

function bend(radius = 3, steps = 12): { x: number; z: number }[] {
  const cx = -4.75;
  const cz = -21.7;
  const pts: { x: number; z: number }[] = [];
  for (let i = 0; i <= steps; i++) {
    const th = (Math.PI / 2) * (i / steps);
    pts.push({ x: cx + radius * Math.sin(th), z: cz + radius * Math.cos(th) });
  }
  return pts;
}

export const PATH: { x: number; z: number }[] = [
  { x: -52.0, z: -18.7 },
  ...bend(),
  { x: -1.75, z: -52.6 },
];

export const STATIONS = {
  pile: { x: -54.2, z: -17.2, label: "ore pile" },
  weigh: { x: -3.5, z: -33.2, label: "weighbridge" },
  winch: { x: -6.6, z: -30.0, label: "haul winch" },
  marshal: { x: 6.3, z: -36.0, label: "marshalling control" },
  intake: { x: -1.75, z: -52.6, label: "crusher intake" },
  spares: { x: -7.2, z: -27.6, label: "spares" },
  access: { x: 8.5, z: -40.0, label: "main access" },
} as const;

export type Chunk = { mass: number; wet: boolean };

export type Haulage = {
  held: Chunk | null;
  stock: number;
  cargo: Chunk[];
  s: number;
  grabbing: boolean;
  dumped: number;
  dose: number;
  stunned: number;
  line: string;
};

export function createHaulage(): Haulage {
  return {
    held: null,
    stock: 6,
    cargo: [],
    s: 0,
    grabbing: false,
    dumped: 0,
    dose: 0,
    stunned: 0,
    line: "",
  };
}

export function pathLength() {
  let n = 0;
  for (let i = 1; i < PATH.length; i++) n += Math.hypot(PATH[i].x - PATH[i - 1].x, PATH[i].z - PATH[i - 1].z);
  return n;
}

const LEN = pathLength();

export function pointOnPath(s: number) {
  const t = Math.max(0, Math.min(LEN, s));
  let acc = 0;
  for (let i = 1; i < PATH.length; i++) {
    const dx = PATH[i].x - PATH[i - 1].x;
    const dz = PATH[i].z - PATH[i - 1].z;
    const seg = Math.hypot(dx, dz);
    if (acc + seg >= t || i === PATH.length - 1) {
      const u = seg < 1e-4 ? 0 : (t - acc) / seg;
      return { x: PATH[i - 1].x + dx * u, z: PATH[i - 1].z + dz * u, yaw: Math.atan2(dx, dz) };
    }
    acc += seg;
  }
  return { x: PATH[0].x, z: PATH[0].z, yaw: 0 };
}

export function massOf(h: Haulage) {
  return h.cargo.reduce((sum, c) => sum + c.mass, 0);
}

export function overloaded(h: Haulage) {
  return massOf(h) > RATED_MASS;
}

export function cartPos(h: Haulage) {
  return pointOnPath(h.s);
}

export function nearCart(h: Haulage, x: number, z: number, reach = 2.2) {
  const p = cartPos(h);
  return Math.hypot(x - p.x, z - p.z) < reach;
}

export function atIntake(h: Haulage) {
  return h.s > LEN - 3.5;
}

export function takeOre(h: Haulage, wet: boolean) {
  if (h.held) {
    h.line = "Hands full. Put it in the cart — that's what the lead lining is for.";
    return false;
  }
  if (h.stock <= 0) {
    h.line = "Pile empty. Blast the face.";
    return false;
  }
  h.stock -= 1;
  h.held = { mass: wet ? WET_MASS : DRY_MASS, wet };
  h.dose += wet ? 4 : 2;
  h.line = h.held.wet
    ? `Wet ore ${WET_MASS}t in your hands. Dose climbing. Get it in the cart.`
    : `Ore ${DRY_MASS}t in your hands. It's hot. Cart is 50 m that way.`;
  return true;
}

export function loadCart(h: Haulage) {
  if (!h.held) {
    h.line = h.grabbing ? "Grabbed the cart. Push it. F again to let go." : "Grab ore, or F to push the cart.";
    return false;
  }
  if (h.cargo.length >= 4) {
    h.line = "Bed full.";
    return false;
  }
  h.cargo.push(h.held);
  h.held = null;
  const m = massOf(h);
  h.line = overloaded(h)
    ? `OVERLOAD ${m.toFixed(1)}/${RATED_MASS}t. Push anyway if you like pain.`
    : `In the cart. ${h.cargo.length}/${ORE_QUOTA}  ${m.toFixed(2)}t. Dose stops climbing.`;
  return true;
}

export function grabCart(h: Haulage) {
  if (h.held) return loadCart(h);
  if (atIntake(h) && h.cargo.length) return dumpCart(h);
  h.grabbing = !h.grabbing;
  h.line = h.grabbing
    ? "On the handle. Walk. The cart stays on the rails."
    : "Let go. Cart stays put.";
  return true;
}

export function dumpCart(h: Haulage) {
  if (!atIntake(h)) {
    h.line = "Intake is the far end of haulage.";
    return false;
  }
  if (!h.cargo.length) {
    h.line = "Empty cart. Go back for ore.";
    return false;
  }
  const n = h.cargo.length;
  h.dumped += n;
  h.cargo = [];
  h.grabbing = false;
  h.line = `${n} chunks tipped. Batch merged. Push the empty back to the face.`;
  return true;
}

export function pushCart(h: Haulage, moveX: number, moveZ: number, dt: number) {
  if (!h.grabbing || h.stunned > 0) return 0;
  const p = pointOnPath(h.s);
  const tangentX = Math.sin(p.yaw);
  const tangentZ = Math.cos(p.yaw);
  const along = moveX * tangentX + moveZ * tangentZ;
  if (Math.abs(along) < 1e-4) return 0;
  const over = overloaded(h);
  const speed = CART_SPEED * (over ? 0.62 : 1) * (h.cargo.length >= 3 ? 0.9 : 1);
  const ds = along * speed * dt;
  h.s = Math.max(0, Math.min(LEN, h.s + ds));
  return ds;
}

export function tickDose(h: Haulage, dt: number) {
  if (h.stunned > 0) h.stunned = Math.max(0, h.stunned - dt);
  if (h.held) {
    h.dose = Math.min(100, h.dose + (h.held.wet ? WET_RAD : HAND_RAD) * dt);
  } else {
    h.dose = Math.max(0, h.dose - 1.6 * dt);
  }
  if (h.dose >= 100 && h.stunned <= 0) {
    h.stunned = 2.2;
    h.dose = 82;
    h.grabbing = false;
    h.line = "DOSE. You carried it by hand too long. That's why the cart exists.";
  }
}

export function promptHaul(h: Haulage, id: string) {
  if (id === "pile") {
    if (h.held) return "Hands full. Dose climbing. Cart. Now.";
    if (h.stock <= 0) return "Pile empty.";
    return `F — pick ore (${h.stock} left). Hands = radiation. Cart = shield.`;
  }
  if (id === "cart") {
    if (h.held) return `F — drop chunk in cart (${h.cargo.length}/${ORE_QUOTA})`;
    if (atIntake(h) && h.cargo.length) return "F — tip the cart into intake";
    return h.grabbing ? "F — let go of the cart" : "F — grab the handle and push";
  }
  if (id === "weigh") return `Weighbridge ${massOf(h).toFixed(2)}/${RATED_MASS}t`;
  if (id === "winch") return "Haul winch. For when someone walks it off the rail.";
  if (id === "marshal") return "One cart. You push it. Line is not live.";
  if (id === "intake") return h.cargo.length ? "Bring the cart onto the grate, then F." : `Intake. Batches: ${h.dumped}.`;
  if (id === "spares") return "Spares. Wheels, a brake shoe, a dosimeter nobody reset.";
  if (id === "access") return "MAIN ACCESS. Worker door. Carts don't go this way.";
  return "";
}
