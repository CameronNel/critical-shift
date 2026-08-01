import * as THREE from 'three';
import { createViewport, type Viewport } from './renderer';
import { createSiteScene, VOID_Y, type SiteScene } from './scene';
import { InputState } from '../input/inputState';
import { createDesktopInput, type DesktopInput } from '../input/desktopInput';
import { FlyController } from '../nav/flyController';
import { MapController } from '../nav/mapController';
import { WalkController, EYE_HEIGHT } from '../nav/walkController';
import { applyToCamera, createNavState, type NavState } from '../nav/navState';
import { buildFacility, type FacilityBuild } from '../build/buildFacility';
import { defaultFacility } from '../facility/facility';
import type { FacilityDoc, SpawnEntity } from '../facility/schema';

export type NavMode = 'walk' | 'fly' | 'map' | 'edit';

export type LayerKey = 'roofs' | 'ground' | 'labels' | 'markers' | 'routes' | 'scaleRefs';

export interface AppStatus {
  mode: NavMode;
  fps: number;
  grounded: boolean;
  zone: string;
}

export class App {
  readonly viewport: Viewport;
  readonly site: SiteScene;
  readonly input = new InputState();
  readonly desktop: DesktopInput;
  readonly nav: NavState;

  private readonly fly = new FlyController();
  readonly map = new MapController();
  private readonly walk = new WalkController();
  private lastFrameTime = 0;
  private readonly listeners = new Set<(status: AppStatus) => void>();

  private doc: FacilityDoc;
  private build: FacilityBuild;
  private currentMode: NavMode = 'walk';
  /** Roof visibility outside map mode, restored when map mode is left. */
  private roofsBeforeMap = true;
  private running = false;
  private frames = 0;
  private fpsAccum = 0;
  private fps = 0;

  constructor(canvas: HTMLCanvasElement) {
    this.viewport = createViewport(canvas);
    this.site = createSiteScene();
    this.desktop = createDesktopInput(canvas, this.input);
    this.doc = defaultFacility();
    this.build = buildFacility(this.doc, this.site.layers);
    this.nav = createNavState(new THREE.Vector3(0, EYE_HEIGHT, 0));
    this.site.layers.roofs.visible = true;
    this.respawn();
  }

  get facility(): FacilityDoc {
    return this.doc;
  }

  get built(): FacilityBuild {
    return this.build;
  }

  get mode(): NavMode {
    return this.currentMode;
  }

  /** Replace the document and rebuild the scene in place. */
  setFacility(doc: FacilityDoc): void {
    this.doc = doc;
    this.build = buildFacility(this.doc, this.site.layers);
    this.emit();
  }

  rebuild(): void {
    this.build = buildFacility(this.doc, this.site.layers);
  }

  setMode(mode: NavMode): void {
    if (mode === this.currentMode) return;
    const previous = this.currentMode;
    this.currentMode = mode;

    if (mode === 'map') {
      // The plan is unreadable through the roofs, so drop them while mapping.
      this.roofsBeforeMap = this.site.layers.roofs.visible;
      this.site.layers.roofs.visible = false;
      this.map.target.set(this.nav.position.x, 0, this.nav.position.z);
      this.map.azimuth = this.nav.yaw;
    } else if (previous === 'map') {
      this.site.layers.roofs.visible = this.roofsBeforeMap;
      // Drop back in above the point being looked at rather than in orbit.
      this.nav.position.set(this.map.target.x, 30, this.map.target.z);
      this.nav.pitch = 0;
    }

    if (mode === 'walk') {
      this.walk.reset();
      this.snapToGround();
    }
    this.emit();
  }

  /** Centre map mode on the whole site. */
  frameSite(): void {
    this.map.frameSite(
      new THREE.Vector3(-142, 0, -78),
      new THREE.Vector3(126, 0, 66),
      this.viewport.camera,
    );
  }

  onStatus(listener: (status: AppStatus) => void): () => void {
    this.listeners.add(listener);
    listener(this.status());
    return () => this.listeners.delete(listener);
  }

  status(): AppStatus {
    return {
      mode: this.currentMode,
      fps: this.fps,
      grounded: this.walk.status.grounded,
      zone: this.zoneAt(this.nav.position),
    };
  }

  spawns(): SpawnEntity[] {
    return this.build.spawns;
  }

  teleport(position: THREE.Vector3 | [number, number, number], yawDegrees?: number): void {
    const target = Array.isArray(position) ? new THREE.Vector3(...position) : position;
    this.nav.position.set(target.x, target.y + EYE_HEIGHT, target.z);
    if (yawDegrees !== undefined) this.nav.yaw = THREE.MathUtils.degToRad(yawDegrees);
    this.nav.pitch = 0;
    this.walk.reset();
    if (this.currentMode === 'walk') this.snapToGround();
  }

  respawn(): void {
    const primary = this.build.spawns.find((s) => s.primary) ?? this.build.spawns[0];
    if (primary) {
      this.teleport(primary.position, primary.rotationY);
    } else {
      this.nav.position.set(0, 40, 0);
    }
  }

  setLayerVisible(layer: LayerKey, visible: boolean): void {
    this.site.layers[layer].visible = visible;
    if (layer === 'labels') {
      // Machine name plates live with their entity, not in the label group.
      this.site.scene.traverse((node) => {
        if (node.userData.isLabel) node.visible = visible;
      });
      this.site.layers.labels.visible = visible;
    }
  }

  isLayerVisible(layer: LayerKey): boolean {
    return this.site.layers[layer].visible;
  }

  zoneAt(position: THREE.Vector3): string {
    let best: string = '—';
    let bestArea = Infinity;
    for (const zone of this.doc.zones) {
      if (zone.id === 'yard') continue;
      const [x0, z0] = zone.bounds.min;
      const [x1, z1] = zone.bounds.max;
      if (position.x < x0 || position.x > x1 || position.z < z0 || position.z > z1) continue;
      const area = (x1 - x0) * (z1 - z0);
      if (area < bestArea) {
        bestArea = area;
        best = zone.name;
      }
    }
    return best === '—' ? 'YARD' : best;
  }

  private snapToGround(): void {
    const feet = this.nav.position.y - EYE_HEIGHT;
    const ground = this.build.collision.groundAt(
      this.nav.position.x,
      this.nav.position.z,
      feet + 2.5,
      feet - 60,
    );
    if (ground) this.nav.position.y = ground.y + EYE_HEIGHT;
  }

  private emit(): void {
    const status = this.status();
    for (const listener of this.listeners) listener(status);
  }

  start(): void {
    if (this.running) return;
    this.running = true;
    this.lastFrameTime = performance.now();
    const frame = () => {
      if (!this.running) return;
      requestAnimationFrame(frame);
      this.tick();
    };
    requestAnimationFrame(frame);
  }

  /** Hook for modes that draw themselves (map mode installs a renderer here). */
  renderOverride: ((dt: number) => boolean) | null = null;

  private tick(): void {
    const now = performance.now();
    const dt = Math.min((now - this.lastFrameTime) / 1000, 0.05);
    this.lastFrameTime = now;

    this.frames++;
    this.fpsAccum += dt;
    if (this.fpsAccum >= 0.5) {
      this.fps = Math.round(this.frames / this.fpsAccum);
      this.frames = 0;
      this.fpsAccum = 0;
      this.emit();
    }

    const handled = this.renderOverride?.(dt) ?? false;
    if (!handled) {
      if (this.currentMode === 'walk') {
        this.walk.update(dt, this.input, this.nav, this.build.collision);
        if (this.nav.position.y < VOID_Y) this.respawn();
      } else if (this.currentMode === 'map') {
        this.map.update(dt, this.input, this.nav);
      } else {
        // Edit mode flies: you need to get to a thing before you can move it.
        this.fly.update(dt, this.input, this.nav);
      }
      applyToCamera(this.nav, this.viewport.camera);
      this.build.labels.update(this.viewport.camera, this.site.layers.labels.visible);
      this.viewport.renderer.render(this.site.scene, this.viewport.camera);
    }

    this.input.clearFrame();
  }
}

export function createApp(canvas: HTMLCanvasElement): App {
  return new App(canvas);
}
