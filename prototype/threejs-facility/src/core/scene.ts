import * as THREE from 'three';

/**
 * Extent the camera may occupy. Generous above the site so fly mode can get a
 * full overview; the walker is contained by the perimeter walls, not by this.
 */
export const SITE_BOUNDS = {
  min: new THREE.Vector3(-190, -40, -120),
  max: new THREE.Vector3(175, 240, 115),
};

/** Falling below this triggers a respawn. */
export const VOID_Y = -34;

export interface SceneLayers {
  /** Structure, machines, circulation. Always visible. */
  world: THREE.Group;
  /** Roofs and high ceilings, hidden by default so the plan reads from above. */
  roofs: THREE.Group;
  /** Surface grade slabs, hideable to inspect the underground level. */
  ground: THREE.Group;
  /** Zone signs and machine name plates. */
  labels: THREE.Group;
  /** Hazard / hiding / shortcut annotation gizmos. */
  markers: THREE.Group;
  /** Coloured circulation route ribbons. */
  routes: THREE.Group;
  /** Scale mannequins. */
  scaleRefs: THREE.Group;
}

export interface SiteScene {
  scene: THREE.Scene;
  layers: SceneLayers;
  boundary: THREE.Object3D;
}

export function createSiteScene(): SiteScene {
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x232a33);
  scene.fog = new THREE.Fog(0x232a33, 140, 900);

  // Interiors have no local lights, so the ambient floor has to keep ceilings
  // and undersides readable rather than black.
  scene.add(new THREE.AmbientLight(0xb6c3d0, 0.55));

  const hemi = new THREE.HemisphereLight(0xc9d8e8, 0x6a6358, 0.9);
  scene.add(hemi);

  const key = new THREE.DirectionalLight(0xfff0d8, 1.1);
  key.position.set(-0.55, 1, 0.35).multiplyScalar(120);
  scene.add(key);

  // Weak fill from the opposite side so north faces are not pure silhouette.
  const fill = new THREE.DirectionalLight(0x8fa8c0, 0.4);
  fill.position.set(0.6, 0.5, -0.6).multiplyScalar(120);
  scene.add(fill);

  const layers: SceneLayers = {
    world: new THREE.Group(),
    roofs: new THREE.Group(),
    ground: new THREE.Group(),
    labels: new THREE.Group(),
    markers: new THREE.Group(),
    routes: new THREE.Group(),
    scaleRefs: new THREE.Group(),
  };
  layers.world.name = 'world';
  layers.roofs.name = 'roofs';
  layers.ground.name = 'ground';
  layers.labels.name = 'labels';
  layers.markers.name = 'markers';
  layers.routes.name = 'routes';
  layers.scaleRefs.name = 'scaleRefs';
  for (const group of Object.values(layers)) scene.add(group);

  layers.roofs.visible = false;

  const boundary = createBoundary();
  scene.add(boundary);

  return { scene, layers, boundary };
}

function createBoundary(): THREE.Object3D {
  const size = new THREE.Vector3().subVectors(SITE_BOUNDS.max, SITE_BOUNDS.min);
  const centre = new THREE.Vector3()
    .addVectors(SITE_BOUNDS.min, SITE_BOUNDS.max)
    .multiplyScalar(0.5);
  const box = new THREE.Box3(SITE_BOUNDS.min, SITE_BOUNDS.max);
  const helper = new THREE.Box3Helper(box, new THREE.Color(0x3d4b5a));
  helper.name = 'site-boundary';
  (helper.material as THREE.LineBasicMaterial).transparent = true;
  (helper.material as THREE.LineBasicMaterial).opacity = 0.35;
  helper.userData.size = size;
  helper.userData.centre = centre;
  return helper;
}
