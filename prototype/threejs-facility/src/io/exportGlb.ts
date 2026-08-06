import * as THREE from 'three';
import type { SceneLayers } from '../core/scene';
import { downloadBlob } from './facilityIo';

interface ExportOptions {
  filename: string;
  rootName: string;
  include?: (object: THREE.Object3D) => boolean;
}

/**
 * Export built facility geometry as GLB. JSON remains the authoritative layout,
 * while object names and facility userData are preserved as GLTF node names /
 * extras so Blender and MCP tooling can still identify individual assets.
 */
async function exportLayersGlb(layers: SceneLayers, options: ExportOptions): Promise<number> {
  const { GLTFExporter } = await import('three/examples/jsm/exporters/GLTFExporter.js');

  const root = new THREE.Group();
  root.name = options.rootName;
  const restore: { object: THREE.Object3D; parent: THREE.Object3D }[] = [];

  // Re-parent rather than clone: merged geometry is large and cloning it all
  // would spike memory on a phone.
  for (const key of ['world', 'roofs', 'ground'] as const) {
    const group = layers[key];
    const holder = new THREE.Group();
    holder.name = key;
    for (const child of [...group.children]) {
      if (child instanceof THREE.Sprite) continue;
      if (options.include && !options.include(child)) continue;
      restore.push({ object: child, parent: group });
      holder.add(child);
    }
    root.add(holder);
  }

  // Sprites nested inside entity groups cannot be exported; hide them instead.
  const hiddenSprites: THREE.Sprite[] = [];
  root.traverse((node) => {
    if (node instanceof THREE.Sprite && node.visible) {
      node.visible = false;
      hiddenSprites.push(node);
    }
  });

  try {
    const exporter = new GLTFExporter();
    const result = await exporter.parseAsync(root, {
      binary: true,
      onlyVisible: true,
      truncateDrawRange: false,
    });
    const blob = new Blob([result as ArrayBuffer], { type: 'model/gltf-binary' });
    downloadBlob(blob, options.filename);
    return blob.size;
  } finally {
    for (const sprite of hiddenSprites) sprite.visible = true;
    for (const { object, parent } of restore) parent.add(object);
    root.clear();
  }
}

/** Whole-site blockout handoff. */
export function exportGreyboxGlb(layers: SceneLayers): Promise<number> {
  return exportLayersGlb(layers, {
    filename: 'critical-shift-greybox.glb',
    rootName: 'CriticalShiftGreybox',
  });
}

/**
 * Reactor/control-only handoff for Blender. Every top-level entity carries its
 * stable facility id, semantic label, tags and notes in userData, which GLTF
 * writes as node extras where supported.
 */
export function exportReactorGlb(layers: SceneLayers): Promise<number> {
  return exportLayersGlb(layers, {
    filename: 'critical-shift-reactor-room.glb',
    rootName: 'CriticalShiftReactorRoom',
    include: (object) => object.userData.zone === 'reactor' || object.userData.zone === 'control',
  });
}
