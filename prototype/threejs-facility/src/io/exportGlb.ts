import * as THREE from 'three';
import type { SceneLayers } from '../core/scene';
import { downloadBlob } from './facilityIo';

/**
 * Greybox geometry as a .glb, for dropping into Unity or Godot as a sizing and
 * blockout reference. JSON stays the authoritative layout format — this is a
 * convenience, so sprites, gizmos and route ribbons are deliberately excluded.
 *
 * The exporter is loaded on demand to keep the initial phone download small.
 */
export async function exportGreyboxGlb(layers: SceneLayers): Promise<number> {
  const { GLTFExporter } = await import('three/examples/jsm/exporters/GLTFExporter.js');

  const root = new THREE.Group();
  root.name = 'CriticalShiftGreybox';
  const restore: { object: THREE.Object3D; parent: THREE.Object3D }[] = [];

  // Re-parent rather than clone: merged geometry is large and cloning it all
  // would spike memory on a phone.
  for (const key of ['world', 'roofs', 'ground'] as const) {
    const group = layers[key];
    const holder = new THREE.Group();
    holder.name = key;
    for (const child of [...group.children]) {
      if (child instanceof THREE.Sprite) continue;
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
    downloadBlob(blob, 'critical-shift-greybox.glb');
    return blob.size;
  } finally {
    for (const sprite of hiddenSprites) sprite.visible = true;
    for (const { object, parent } of restore) parent.add(object);
    root.clear();
  }
}
