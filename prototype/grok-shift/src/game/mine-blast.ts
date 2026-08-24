export type HoleId = "low" | "mid" | "high";

export type BlastHud = {
  prompt: string;
  hint: string;
  mood: string;
  carried: number;
  placed: number;
  doorClosed: boolean;
  result: string;
  fuse: number;
  doorOpenAlert: boolean;
  oreHeld: number;
  cartCargo: number;
  cartMass: number;
  dumped: number;
  brakeOn: boolean;
  dose: number;
  grabbing: boolean;
};

export type Mood = {
  id: string;
  mul: number;
  title: string;
  hint: string;
};

const POLITE = 400;

export const MOODS: Mood[] = [
  {
    id: "hungover",
    mul: 0.6,
    title: "hungover",
    hint: "Rock called in sick. A polite cough (four sticks, toilets card) would be a war crime. One stick in the middle hole. Then apologise to the wall.",
  },
  {
    id: "sulk",
    mul: 0.9,
    title: "sulking",
    hint: "Rock is sulking. Yesterday it wanted a polite cough (four sticks). Today it wants a hair under that. Three in the polite hole. Four is 'we need to talk'.",
  },
  {
    id: "fine",
    mul: 1.0,
    title: "fine (lying)",
    hint: "Rock says it's fine. In this mine that is a lie, but it is the legal lie. Four sticks, middle hole, like the laminated card we stole from the toilets.",
  },
  {
    id: "peckish",
    mul: 1.3,
    title: "skipped breakfast",
    hint: "Rock skipped breakfast. A polite cough plus a nibble: five sticks in the polite hole. Six if you want it to text back. Not the ceiling. Never the ceiling.",
  },
  {
    id: "union",
    mul: 1.7,
    title: "unionized at 6am",
    hint: "The rock unionized at 6am. They want 70% more than a polite cough. That's seven sticks. I am also union. I will not do the maths for you.",
  },
  {
    id: "spicy",
    mul: 2.1,
    title: "found the energy drinks",
    hint: "Rock found the energy-drink crate. Double a polite cough, then one more for luck. That's eight. 'For luck' is how we lost shaft 3.",
  },
];

const HOLE_MULT: Record<HoleId, number> = { low: 0.55, mid: 1, high: 1.4 };

export function rollMood(seed = Date.now()): Mood {
  return MOODS[Math.abs(seed) % MOODS.length];
}

export function targetGrams(mood: Mood) {
  return Math.round(POLITE * mood.mul);
}

export function effectiveGrams(placed: Record<HoleId, number>) {
  return (Object.keys(placed) as HoleId[]).reduce((sum, h) => sum + placed[h] * 100 * HOLE_MULT[h], 0);
}

export type BlastOutcome = "under" | "good" | "over" | "tourist";

export function judge(
  effective: number,
  target: number,
  usedHigh: boolean,
  doorClosed: boolean,
  detonatedInside: boolean,
): { outcome: BlastOutcome; opening: number; line: string } {
  if (detonatedInside) {
    return {
      outcome: "tourist",
      opening: 0.4,
      line: "You punched the detonator while still in the hole. Compliance calls this 'a teachable moment'. The rock calls it breakfast.",
    };
  }
  if (!doorClosed) {
    return {
      outcome: "over",
      opening: 2.4,
      line: "Door was open. The blast waved at S1, stole a helmet, and brought the ceiling with it.",
    };
  }
  const ratio = effective / Math.max(1, target);
  if (usedHigh && ratio >= 0.8) {
    return {
      outcome: "over",
      opening: 2.6,
      line: `You stuffed the skylight. ${Math.round(effective)}g against a ${target}g mood. The roof has filed a complaint. With rubble.`,
    };
  }
  if (usedHigh) {
    return {
      outcome: "under",
      opening: 0.5,
      line: "You tickled the ceiling and it took it personally. Tiny bite of ore. Also a new drip. That's a feature.",
    };
  }
  if (ratio < 0.75) {
    return {
      outcome: "under",
      opening: 0.35 + ratio * 0.5,
      line: `Underblast. ${Math.round(effective)}g vs ${target}g. Less ore, more pick. The rock is laughing in grams.`,
    };
  }
  if (ratio > 1.28) {
    return {
      outcome: "over",
      opening: 2.2 + Math.min(1, ratio - 1.28),
      line: `Overblast. ${Math.round(effective)}g vs ${target}g. That's not a mine, that's a rumour of a mine.`,
    };
  }
  return {
    outcome: "good",
    opening: 1.1 + (ratio - 0.75) * 1.4,
    line: `Face opened. ${Math.round(effective)}g, target ${target}g. Quota might even notice.`,
  };
}

export const HOLES: { id: HoleId; label: string; x: number; y: number; z: number }[] = [
  { id: "low", label: "lazy pocket", x: -57.5, y: 0.85, z: -16.55 },
  { id: "mid", label: "polite hole", x: -57.5, y: 1.55, z: -18.7 },
  { id: "high", label: "union skylight", x: -57.5, y: 3.15, z: -20.85 },
];

export const CRATE = { x: -4.6, z: -15.4 };
export const DOOR = { x: -8.05, z: -18.7 };
export const CLOSE_BTN = { x: -7.22, z: -16.15 };
export const LEVER = { x: -7.2, z: -16.85 };
export const BOARD = { x: -6.4, z: -14.95 };
