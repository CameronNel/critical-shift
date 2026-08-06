import * as THREE from 'three';
import type { App } from '../core/app';

export type ReactorPreviewState =
  | 'normal'
  | 'high-output'
  | 'instability'
  | 'cooling-emergency'
  | 'scram'
  | 'meltdown';

export const REACTOR_PREVIEW_STATES: readonly ReactorPreviewState[] = [
  'normal',
  'high-output',
  'instability',
  'cooling-emergency',
  'scram',
  'meltdown',
] as const;

const BANK_MOVING_IDS = [
  'reactor.bank.a.moving.carriage',
  'reactor.bank.a.moving.upper-collar',
  'reactor.bank.a.moving.lower-collar',
  'reactor.bank.a.drive-column',
  'reactor.bank.b.moving.carriage',
  'reactor.bank.b.moving.upper-collar',
  'reactor.bank.b.moving.lower-collar',
  'reactor.bank.b.drive-column',
] as const;

const BANK_A_IDS = BANK_MOVING_IDS.filter((id) => id.includes('.bank.a.'));
const BANK_B_IDS = BANK_MOVING_IDS.filter((id) => id.includes('.bank.b.'));

const WATER_ID = 'reactor.pool.water.surface';
const CORE_LOW_ID = 'reactor.pool.core.glow.low';
const CORE_MID_ID = 'reactor.pool.core.glow.mid';
const MELTDOWN_ID = 'reactor.pool.core.glow.meltdown';
const ALARM_IDS = ['reactor.visual.light.alarm-a', 'reactor.visual.light.alarm-b'] as const;
const READY_IDS = ['reactor.bank.a.status.ready', 'reactor.bank.b.status.ready'] as const;
const WARN_IDS = ['reactor.bank.a.status.warn', 'reactor.bank.b.status.warn'] as const;

interface Targets {
  bankA: number;
  bankB: number;
  water: number;
  coreScale: number;
  meltdownScale: number;
  alarms: boolean;
  warning: boolean;
}

const TARGETS: Record<ReactorPreviewState, Targets> = {
  normal: {
    bankA: 0,
    bankB: 0,
    water: 0,
    coreScale: 1,
    meltdownScale: 0,
    alarms: false,
    warning: false,
  },
  'high-output': {
    bankA: 0.30,
    bankB: 0.18,
    water: 0,
    coreScale: 1.16,
    meltdownScale: 0,
    alarms: false,
    warning: false,
  },
  instability: {
    bankA: 0.12,
    bankB: -0.10,
    water: -0.06,
    coreScale: 1.22,
    meltdownScale: 0,
    alarms: true,
    warning: true,
  },
  'cooling-emergency': {
    bankA: -0.18,
    bankB: -0.28,
    water: -0.60,
    coreScale: 1.12,
    meltdownScale: 0.08,
    alarms: true,
    warning: true,
  },
  scram: {
    bankA: -1.80,
    bankB: -1.80,
    water: -0.10,
    coreScale: 0.82,
    meltdownScale: 0,
    alarms: true,
    warning: true,
  },
  meltdown: {
    bankA: -1.80,
    bankB: -1.80,
    water: -0.42,
    coreScale: 1.10,
    meltdownScale: 1.38,
    alarms: true,
    warning: true,
  },
};

/**
 * Visual-only reactor state controller for art/layout review. It never mutates
 * FacilityDoc coordinates. Instead it offsets the already-built, semantically
 * named Three.js entity roots. The exported facility JSON remains the neutral
 * source pose, while GLB keeps the individual named objects for Blender.
 */
export class ReactorPreview {
  private current: ReactorPreviewState = 'normal';
  private target: Targets = { ...TARGETS.normal };
  private bankA = 0;
  private bankB = 0;
  private water = 0;
  private coreScale = 1;
  private meltdownScale = 0;
  private startTime = performance.now();
  private running = false;
  private listeners = new Set<(state: ReactorPreviewState) => void>();

  constructor(private readonly app: App) {
    this.applyVisibility();
  }

  get state(): ReactorPreviewState {
    return this.current;
  }

  onChange(listener: (state: ReactorPreviewState) => void): () => void {
    this.listeners.add(listener);
    listener(this.current);
    return () => this.listeners.delete(listener);
  }

  setState(state: ReactorPreviewState): void {
    this.current = state;
    this.target = { ...TARGETS[state] };
    this.startTime = performance.now();
    this.applyVisibility();
    for (const listener of this.listeners) listener(state);
  }

  /** Re-apply state after a facility rebuild/reset without modifying the doc. */
  refresh(): void {
    this.applyVisibility();
    this.writeTransforms(performance.now());
  }

  start(): void {
    if (this.running) return;
    this.running = true;
    const frame = (now: number) => {
      if (!this.running) return;
      this.update(now);
      requestAnimationFrame(frame);
    };
    requestAnimationFrame(frame);
  }

  stop(): void {
    this.running = false;
  }

  private object(id: string): THREE.Object3D | undefined {
    return this.app.built.objects.get(id);
  }

  private setVisible(ids: readonly string[], visible: boolean): void {
    for (const id of ids) {
      const object = this.object(id);
      if (object) object.visible = visible;
    }
  }

  private applyVisibility(): void {
    this.setVisible(ALARM_IDS, this.target.alarms);
    this.setVisible(WARN_IDS, this.target.warning);
    this.setVisible(READY_IDS, !this.target.warning);
    // Keep the meltdown mesh as a real exportable asset but hide it from the
    // healthy browser state. Reactor GLB export explicitly forces tagged state
    // assets visible during export so Blender still receives it.
    const meltdown = this.object(MELTDOWN_ID);
    if (meltdown) meltdown.visible = this.target.meltdownScale > 0.001;
  }

  private ease(current: number, target: number, rate: number): number {
    return current + (target - current) * rate;
  }

  private update(now: number): void {
    const fast = this.current === 'scram' || this.current === 'meltdown';
    const easing = fast ? 0.18 : 0.075;
    this.bankA = this.ease(this.bankA, this.target.bankA, easing);
    this.bankB = this.ease(this.bankB, this.target.bankB, easing);
    this.water = this.ease(this.water, this.target.water, 0.055);
    this.coreScale = this.ease(this.coreScale, this.target.coreScale, 0.06);
    this.meltdownScale = this.ease(this.meltdownScale, this.target.meltdownScale, 0.08);

    this.writeTransforms(now);
  }

  private writeTransforms(now: number): void {
    let a = this.bankA;
    let b = this.bankB;
    let water = this.water;
    let coreScale = this.coreScale;

    const seconds = now / 1000;
    if (this.current === 'instability') {
      // Unequal hunting deliberately breaks symmetry before anything explodes.
      a += Math.sin(seconds * 4.7) * 0.13;
      b += Math.sin(seconds * 5.35 + 1.2) * 0.10;
      water += Math.sin(seconds * 3.1) * 0.035;
      coreScale *= 1 + Math.sin(seconds * 5.8) * 0.055;
    } else if (this.current === 'cooling-emergency') {
      water += Math.sin(seconds * 4.4) * 0.025;
      coreScale *= 1 + Math.sin(seconds * 3.8) * 0.035;
    } else if (this.current === 'meltdown') {
      water += Math.sin(seconds * 7.2) * 0.07 + Math.sin(seconds * 3.1) * 0.035;
      coreScale *= 1 + Math.sin(seconds * 6.5) * 0.10;
    } else if (this.current === 'high-output') {
      water += Math.sin(seconds * 2.6) * 0.012;
    } else if (this.current === 'scram') {
      // Brief damped rebound after the banks hit the emergency stop.
      const age = Math.max(0, (now - this.startTime) / 1000);
      const rebound = age < 1.4 ? Math.sin(age * 22) * Math.exp(-age * 4.5) * 0.07 : 0;
      a += rebound;
      b += rebound;
      water += age < 1.8 ? Math.sin(age * 14) * Math.exp(-age * 2.2) * 0.055 : 0;
    }

    for (const id of BANK_A_IDS) {
      const object = this.object(id);
      if (object) object.position.y = a;
    }
    for (const id of BANK_B_IDS) {
      const object = this.object(id);
      if (object) object.position.y = b;
    }

    const waterObject = this.object(WATER_ID);
    if (waterObject) {
      waterObject.position.y = water;
      const agitation = this.current === 'meltdown' ? 1.035 : this.current === 'instability' ? 1.012 : 1;
      waterObject.scale.set(agitation, 1, agitation);
    }

    const low = this.object(CORE_LOW_ID);
    const mid = this.object(CORE_MID_ID);
    if (low) low.scale.setScalar(coreScale);
    if (mid) mid.scale.setScalar(Math.max(0.72, coreScale * 0.96));

    const meltdown = this.object(MELTDOWN_ID);
    if (meltdown && this.target.meltdownScale > 0.001) {
      const pulse = this.current === 'meltdown' ? 1 + Math.sin(seconds * 8.2) * 0.10 : 1;
      const scale = Math.max(0.01, this.meltdownScale * pulse);
      meltdown.scale.setScalar(scale);
    }
  }
}
