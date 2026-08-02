import * as THREE from 'three';
import type { App } from '../core/app';
import { rebuildEntity, removeBuiltEntity } from '../build/buildFacility';
import type { Entity } from '../facility/schema';
import {
  duplicateId,
  editableFields,
  entityAnchor,
  rotateEntity,
  scaleEntity,
  setField,
  translateEntity,
} from './transforms';

const TAP_MS = 260;
const TAP_PX = 9;

export type EditorListener = (selected: Entity | null) => void;

/**
 * Lightweight structural editor. It exists to answer "move that wall two
 * metres and look again", not to replace an engine editor.
 *
 * Selection is a tap or click; a press-and-drag is still a look, so editing
 * never costs you the ability to move around. Edits mutate the facility
 * document and rebuild only the affected entity.
 */
export class Editor {
  private selectedId: string | null = null;
  private readonly raycaster = new THREE.Raycaster();
  private readonly pointer = new THREE.Vector2();
  private readonly outline: THREE.Box3Helper;
  private readonly outlineBox = new THREE.Box3();
  private readonly listeners = new Set<EditorListener>();
  private pressAt = { x: 0, y: 0, time: 0, valid: false };

  /** Metres per nudge. */
  step = 1;

  constructor(private readonly app: App) {
    this.outline = new THREE.Box3Helper(this.outlineBox, new THREE.Color(0xffc040));
    this.outline.visible = false;
    this.outline.userData.persistent = true;
    this.app.site.scene.add(this.outline);

    window.addEventListener('pointerdown', this.onPointerDown, true);
    window.addEventListener('pointerup', this.onPointerUp, true);
  }

  onChange(listener: EditorListener): () => void {
    this.listeners.add(listener);
    listener(this.selected);
    return () => this.listeners.delete(listener);
  }

  get selected(): Entity | null {
    if (!this.selectedId) return null;
    return this.app.facility.entities.find((e) => e.id === this.selectedId) ?? null;
  }

  select(id: string | null): void {
    this.selectedId = id;
    this.refreshOutline();
    this.emit();
  }

  private emit(): void {
    const selected = this.selected;
    for (const listener of this.listeners) listener(selected);
  }

  private onInterface(target: EventTarget | null): boolean {
    return (
      target instanceof Element &&
      target.closest('[data-hud="button"], [data-hud="legend"], .panel, .legend') !== null
    );
  }

  private onPointerDown = (event: PointerEvent): void => {
    if (this.app.mode !== 'edit') return;
    if (this.onInterface(event.target)) return;
    this.pressAt = { x: event.clientX, y: event.clientY, time: performance.now(), valid: true };
  };

  private onPointerUp = (event: PointerEvent): void => {
    if (!this.pressAt.valid) return;
    this.pressAt.valid = false;
    if (this.app.mode !== 'edit') return;
    if (performance.now() - this.pressAt.time > TAP_MS) return;
    if (Math.hypot(event.clientX - this.pressAt.x, event.clientY - this.pressAt.y) > TAP_PX) return;
    this.pickAt(event.clientX, event.clientY);
  };

  private pickAt(clientX: number, clientY: number): void {
    const rect = this.app.viewport.canvas.getBoundingClientRect();
    this.pointer.set(
      ((clientX - rect.left) / rect.width) * 2 - 1,
      -((clientY - rect.top) / rect.height) * 2 + 1,
    );
    this.raycaster.setFromCamera(this.pointer, this.app.viewport.camera);
    const targets = [
      this.app.site.layers.world,
      this.app.site.layers.roofs,
      this.app.site.layers.ground,
    ];
    const hits = this.raycaster.intersectObjects(targets, true);
    for (const hit of hits) {
      if (hit.object instanceof THREE.Sprite) continue;
      const id = hit.object.userData.entityId as string | undefined;
      if (id) {
        this.select(id);
        return;
      }
    }
    this.select(null);
  }

  private refreshOutline(): void {
    const object = this.selectedId ? this.app.built.objects.get(this.selectedId) : undefined;
    if (!object) {
      this.outline.visible = false;
      return;
    }
    this.outlineBox.setFromObject(object, true);
    if (this.outlineBox.isEmpty()) {
      this.outline.visible = false;
      return;
    }
    this.outlineBox.expandByScalar(0.15);
    this.outline.box = this.outlineBox;
    this.outline.visible = true;
    this.outline.updateMatrixWorld(true);
  }

  /** Replace the selected entity with an edited copy and rebuild it. */
  private commit(next: Entity): void {
    const doc = this.app.facility;
    const index = doc.entities.findIndex((e) => e.id === this.selectedId);
    if (index < 0) return;
    doc.entities[index] = next;
    this.selectedId = next.id;
    rebuildEntity(this.app.built, this.app.site.layers, next);
    this.refreshOutline();
    this.emit();
  }

  nudge(axis: 0 | 1 | 2, direction: 1 | -1): void {
    const entity = this.selected;
    if (!entity) return;
    const delta: [number, number, number] = [0, 0, 0];
    delta[axis] = this.step * direction;
    this.commit(translateEntity(entity, delta));
  }

  rotate(degrees: number): void {
    const entity = this.selected;
    if (entity) this.commit(rotateEntity(entity, degrees));
  }

  scale(factor: number): void {
    const entity = this.selected;
    if (entity) this.commit(scaleEntity(entity, factor));
  }

  setNumber(key: string, index: number, value: number): void {
    const entity = this.selected;
    if (entity && Number.isFinite(value)) this.commit(setField(entity, key, index, value));
  }

  setText(key: 'label' | 'notes', value: string): void {
    const entity = this.selected;
    if (!entity) return;
    const next = structuredClone(entity) as Entity & Record<string, unknown>;
    if (value.trim() === '') delete next[key];
    else next[key] = value;
    this.commit(next);
  }

  toggleHidden(): void {
    const entity = this.selected;
    if (!entity) return;
    const next = structuredClone(entity);
    next.hidden = !next.hidden;
    this.commit(next);
  }

  duplicate(): void {
    const entity = this.selected;
    if (!entity) return;
    const doc = this.app.facility;
    const taken = (candidate: string) => doc.entities.some((e) => e.id === candidate);
    const copy = structuredClone(entity);
    copy.id = duplicateId(entity.id, taken);
    // Offset so the copy is visible rather than z-fighting with the original.
    const moved = translateEntity(copy, [this.step * 2, 0, 0]);
    doc.entities.push(moved);
    rebuildEntity(this.app.built, this.app.site.layers, moved);
    this.select(moved.id);
  }

  remove(): void {
    const entity = this.selected;
    if (!entity) return;
    const doc = this.app.facility;
    doc.entities = doc.entities.filter((e) => e.id !== entity.id);
    removeBuiltEntity(this.app.built, entity.id);
    this.select(null);
  }

  /** Move the camera to look at the selection. */
  focus(): void {
    const entity = this.selected;
    if (!entity) return;
    const anchor = entityAnchor(entity);
    const object = this.app.built.objects.get(entity.id);
    let radius = 8;
    if (object) {
      const box = new THREE.Box3().setFromObject(object, true);
      if (!box.isEmpty()) radius = Math.max(6, box.getSize(new THREE.Vector3()).length() * 0.7);
    }
    this.app.nav.position.set(anchor[0], anchor[1] + radius * 0.5, anchor[2] + radius);
    this.app.nav.yaw = 0;
    this.app.nav.pitch = -0.4;
  }

  fields() {
    const entity = this.selected;
    return entity ? editableFields(entity) : [];
  }

  dispose(): void {
    window.removeEventListener('pointerdown', this.onPointerDown, true);
    window.removeEventListener('pointerup', this.onPointerUp, true);
    this.app.site.scene.remove(this.outline);
  }
}
