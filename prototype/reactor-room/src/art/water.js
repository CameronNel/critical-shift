import * as THREE from 'three';
import { P } from './palette.js';
import { causticTexture, softDot } from './textures.js';

/**
 * The pool.
 *
 * This is the one asset in the room that is worth a custom shader, so it gets
 * five cooperating layers rather than a coloured plane:
 *
 *  1. **Surface** — scrolling ripple normals, Fresnel, a specular glint, and a
 *     Cherenkov term that rises out of the water as the core comes up.
 *  2. **Body** — an additive volume inside the pit, brightest at the lattice,
 *     so the water reads as *lit from within* rather than tinted.
 *  3. **Shafts** — one soft column per loaded assembly, flickering
 *     independently. This is what makes fuel count legible from the booth.
 *  4. **Caustics** — the same ridged noise projected onto the liner, the deck
 *     and the ceiling. Cheap, and it is what convinces the eye there is water.
 *  5. **Bubbles** — a slow riser stream, so a still pool is never truly still.
 *
 * Everything is driven by two numbers from the simulation: `glow` (0..1
 * reactivity) and `agitation` (0..1 coolant flow).
 */

const RIPPLE = /* glsl */`
  // Three scrolling samples of one ridged-noise map. Cheaper than any real
  // wave sum and, at this scale, indistinguishable from one.
  float rippleAt(sampler2D tex, vec2 uv, float t) {
    float a = texture2D(tex, uv * 1.6 + vec2(t * 0.021, t * 0.013)).r;
    float b = texture2D(tex, uv * 2.9 - vec2(t * 0.017, t * 0.026)).r;
    float c = texture2D(tex, uv * 5.3 + vec2(-t * 0.033, t * 0.011)).r;
    return a * 0.5 + b * 0.32 + c * 0.18;
  }
`;

export function createPool({
  half = 4.3,
  surfaceY = -0.55,
  floorY = -5.0,
  quality = { detail: 1 },
} = {}) {
  const group = new THREE.Group();
  const uniforms = {
    uTime: { value: 0 },
    uGlow: { value: 0 },
    uAgitation: { value: 0 },
    uRipple: { value: causticTexture() },
    uDeep: { value: new THREE.Color(P.poolDark) },
    uShallow: { value: new THREE.Color(P.cherenkovDeep) },
    uGlowColour: { value: new THREE.Color(P.cherenkov) },
    uHot: { value: new THREE.Color(P.cherenkovCore) },
    uSky: { value: new THREE.Color(P.lampSodium) },
    uHalf: { value: half },
  };

  /* ----------------------------------------------------------- 1. surface */
  const segments = quality.detail > 0.6 ? 96 : 40;
  const surface = new THREE.Mesh(
    new THREE.PlaneGeometry(half * 2, half * 2, segments, segments),
    new THREE.ShaderMaterial({
      uniforms,
      transparent: true,
      depthWrite: false,
      side: THREE.DoubleSide,
      vertexShader: /* glsl */`
        uniform float uTime;
        uniform float uAgitation;
        uniform sampler2D uRipple;
        varying vec2 vUv;
        varying vec3 vWorld;
        ${RIPPLE}
        void main() {
          vUv = uv;
          vec3 p = position;
          float h = rippleAt(uRipple, uv, uTime) - 0.5;
          p.z += h * (0.018 + uAgitation * 0.05);
          vec4 world = modelMatrix * vec4(p, 1.0);
          vWorld = world.xyz;
          gl_Position = projectionMatrix * viewMatrix * world;
        }
      `,
      fragmentShader: /* glsl */`
        uniform float uTime;
        uniform float uGlow;
        uniform float uAgitation;
        uniform sampler2D uRipple;
        uniform vec3 uDeep;
        uniform vec3 uShallow;
        uniform vec3 uGlowColour;
        uniform vec3 uHot;
        uniform vec3 uSky;
        varying vec2 vUv;
        varying vec3 vWorld;
        ${RIPPLE}

        void main() {
          float t = uTime * (1.0 + uAgitation * 1.8);
          float e = 0.0035;
          float h  = rippleAt(uRipple, vUv, t);
          float hx = rippleAt(uRipple, vUv + vec2(e, 0.0), t);
          float hy = rippleAt(uRipple, vUv + vec2(0.0, e), t);
          float relief = 0.6 + uAgitation * 1.6;
          vec3 n = normalize(vec3((h - hx) * relief / e * 0.004, 1.0, (h - hy) * relief / e * 0.004));

          vec3 view = normalize(cameraPosition - vWorld);
          float fres = pow(1.0 - clamp(dot(n, view), 0.0, 1.0), 3.2);

          // Radial falloff: the lattice sits at the middle, so the middle is
          // where the light comes from.
          float radial = 1.0 - clamp(length(vUv - 0.5) * 1.9, 0.0, 1.0);
          float core = pow(radial, 2.2);

          vec3 body = mix(uDeep, uShallow, core * 0.85 + 0.15);
          float shimmer = pow(clamp(h * 1.5 - 0.35, 0.0, 1.0), 2.0);

          vec3 cherenkov = mix(uGlowColour, uHot, shimmer * 0.8);
          vec3 emission = cherenkov * uGlow * (0.25 + core * 1.65) * (0.55 + shimmer * 1.5);
          body += emission;

          // Sodium worklights raking across the surface. Broken up by the ripple
          // so it reads as glints on moving water, not as one polished band.
          vec3 lightDir = normalize(vec3(-0.35, 0.9, 0.28));
          float spec = pow(max(dot(reflect(-lightDir, n), view), 0.0), 60.0);
          body += uSky * spec * (0.22 + uAgitation * 0.5) * (0.35 + shimmer * 1.3);
          body += uSky * fres * 0.12;

          // Thin enough to see the lattice through — that is the point of an
          // open pool — but not so thin that a cold pool reads as an empty pit
          // from across the deck. Alpha then follows the emission, because a
          // glowing patch of water has to reach the frame at full strength or it
          // just looks like tinted glass.
          float lit = dot(emission, vec3(0.33));
          float alpha = mix(0.42, 0.82, fres) + clamp(lit * 0.7, 0.0, 0.45);
          gl_FragColor = vec4(body, clamp(alpha, 0.0, 1.0));
        }
      `,
    }),
  );
  surface.rotation.x = -Math.PI / 2;
  surface.position.y = surfaceY;
  surface.renderOrder = 6;
  group.add(surface);

  /* -------------------------------------------------------------- 2. body */
  /**
   * The lit volume of water, as a stack of additive horizontal slices rather
   * than a box.
   *
   * A box only shows the viewer its far faces, and the far faces are exactly
   * what the core lattice hides — so the brightest part of the pool ended up
   * behind the thing that is supposed to be making the light. Slices sit *above*
   * the lattice, accumulate towards the surface, and cost one unlit quad each.
   */
  const depth = surfaceY - floorY;
  const sliceCount = quality.detail > 0.6 ? 14 : 7;
  for (let i = 0; i < sliceCount; i++) {
    const t = (i + 0.5) / sliceCount;
    const slice = new THREE.Mesh(
      new THREE.PlaneGeometry(half * 2 - 0.08, half * 2 - 0.08),
      new THREE.ShaderMaterial({
        uniforms: {
          uTime: uniforms.uTime,
          uGlow: uniforms.uGlow,
          uGlowColour: uniforms.uGlowColour,
          uHot: uniforms.uHot,
          uDepth: { value: t },
          uWeight: { value: 1.6 / sliceCount },
        },
        transparent: true,
        depthWrite: false,
        blending: THREE.AdditiveBlending,
        side: THREE.DoubleSide,
        vertexShader: /* glsl */`
          varying vec2 vUv;
          void main() {
            vUv = uv;
            gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
          }
        `,
        fragmentShader: /* glsl */`
          uniform float uTime; uniform float uGlow; uniform float uWeight; uniform float uDepth;
          uniform vec3 uGlowColour; uniform vec3 uHot;
          varying vec2 vUv;
          void main() {
            // Radial around the lattice, wider and softer the further the light
            // has travelled up through the water.
            float spread = 0.23 + uDepth * 0.25;
            float radial = 1.0 - clamp(length(vUv - 0.5) / spread, 0.0, 1.0);
            float shape = pow(radial, 1.5) * (1.0 - uDepth * 0.35);
            float pulse = 0.86 + 0.14 * sin(uTime * 1.7 + uDepth * 5.0) * sin(uTime * 0.63 + 1.3);
            float amount = shape * uGlow * uWeight * pulse * 2.2;
            // Kept firmly on the cyan side: pushed any whiter and the pool clips
            // to a flat white slab under bloom instead of reading as Cherenkov.
            vec3 colour = mix(uGlowColour, uHot, 0.22 - uDepth * 0.18);
            gl_FragColor = vec4(colour * amount * 1.25, amount);
          }
        `,
      }),
    );
    slice.rotation.x = -Math.PI / 2;
    slice.position.y = floorY + 1.15 + t * (depth - 1.35);
    slice.renderOrder = 4;
    group.add(slice);
  }

  /* ------------------------------------------------------------ 3. shafts */
  const shafts = [];
  const shaftMaterial = new THREE.ShaderMaterial({
    uniforms: { ...uniforms, uSeed: { value: 0 } },
    transparent: true,
    depthWrite: false,
    blending: THREE.AdditiveBlending,
    side: THREE.DoubleSide,
    vertexShader: /* glsl */`
      varying vec2 vUv;
      void main() {
        vUv = uv;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `,
    fragmentShader: /* glsl */`
      uniform float uTime;
      uniform float uGlow;
      uniform float uSeed;
      uniform vec3 uHot;
      varying vec2 vUv;
      void main() {
        float edge = sin(vUv.x * 3.14159);
        float rise = pow(clamp(vUv.y, 0.0, 1.0), 0.7);
        float flicker = 0.82 + 0.18 * sin(uTime * (5.1 + uSeed) + uSeed * 9.0);
        float a = pow(edge, 2.2) * (1.0 - rise * 0.66) * uGlow * flicker * 0.8;
        gl_FragColor = vec4(uHot * a * 2.0, a);
      }
    `,
  });

  function addShaft(x, z, height) {
    const material = shaftMaterial.clone();
    material.uniforms = { ...shaftMaterial.uniforms, uSeed: { value: Math.random() * 6.28 } };
    material.uniforms.uTime = uniforms.uTime;
    material.uniforms.uGlow = uniforms.uGlow;
    material.uniforms.uHot = uniforms.uHot;
    const mesh = new THREE.Mesh(new THREE.CylinderGeometry(0.42, 0.3, height, 12, 1, true), material);
    mesh.position.set(x, floorY + height / 2 + 0.2, z);
    mesh.renderOrder = 5;
    mesh.visible = false;
    group.add(mesh);
    shafts.push(mesh);
    return mesh;
  }

  /* ---------------------------------------------------------- 4. caustics */
  const causticUniforms = {
    uTime: uniforms.uTime,
    uGlow: uniforms.uGlow,
    uMap: { value: causticTexture() },
    uColour: { value: new THREE.Color(P.cherenkov) },
    uScale: { value: 1 },
    uStrength: { value: 1 },
  };
  function causticMaterial(strength, scale) {
    return new THREE.ShaderMaterial({
      uniforms: { ...causticUniforms, uStrength: { value: strength }, uScale: { value: scale } },
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
      side: THREE.DoubleSide,
      vertexShader: /* glsl */`
        varying vec2 vUv;
        void main() {
          vUv = uv;
          gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
        }
      `,
      fragmentShader: /* glsl */`
        uniform float uTime; uniform float uGlow; uniform sampler2D uMap;
        uniform vec3 uColour; uniform float uScale; uniform float uStrength;
        varying vec2 vUv;
        void main() {
          vec2 uv = vUv * uScale;
          // Two counter-scrolling layers multiplied: the interference is the
          // whole trick, and it costs two texture reads.
          float a = texture2D(uMap, uv + vec2(uTime * 0.014, uTime * 0.009)).r;
          float b = texture2D(uMap, uv * 1.31 - vec2(uTime * 0.011, uTime * 0.017)).r;
          float c = pow(clamp(a * b * 2.6, 0.0, 1.0), 1.5);
          float fade = smoothstep(0.0, 0.18, vUv.y) * smoothstep(0.0, 0.14, 1.0 - vUv.y);
          float amount = c * uGlow * uStrength * fade;
          gl_FragColor = vec4(uColour * amount, amount);
        }
      `,
    });
  }

  // Liner walls, just inside the concrete.
  for (let i = 0; i < 4; i++) {
    const wall = new THREE.Mesh(new THREE.PlaneGeometry(half * 2 - 0.1, depth), causticMaterial(1.5, 2.2));
    const angle = (i * Math.PI) / 2;
    wall.position.set(Math.sin(angle) * (half - 0.06), (surfaceY + floorY) / 2, Math.cos(angle) * (half - 0.06));
    wall.rotation.y = angle + Math.PI;
    wall.renderOrder = 3;
    group.add(wall);
  }
  // The deck around the pit, lit from the water.
  const deckCaustic = new THREE.Mesh(new THREE.PlaneGeometry(half * 4.4, half * 4.4), causticMaterial(0.5, 3.4));
  deckCaustic.rotation.x = -Math.PI / 2;
  deckCaustic.position.y = 0.02;
  deckCaustic.renderOrder = 2;
  group.add(deckCaustic);

  /** Ceiling caustics are added separately — they need the room's ceiling height. */
  function ceilingCaustics(y, width) {
    const mesh = new THREE.Mesh(new THREE.PlaneGeometry(width, width), causticMaterial(0.9, 2.0));
    mesh.rotation.x = Math.PI / 2;
    mesh.position.y = y;
    mesh.renderOrder = 2;
    return mesh;
  }

  /* ----------------------------------------------------------- 5. bubbles */
  const bubbleCount = quality.detail > 0.6 ? 90 : 36;
  const bubblePositions = new Float32Array(bubbleCount * 3);
  const bubbleSeeds = new Float32Array(bubbleCount);
  for (let i = 0; i < bubbleCount; i++) {
    bubblePositions[i * 3] = (Math.random() - 0.5) * half * 1.5;
    bubblePositions[i * 3 + 1] = floorY + Math.random() * depth;
    bubblePositions[i * 3 + 2] = (Math.random() - 0.5) * half * 1.5;
    bubbleSeeds[i] = 0.35 + Math.random() * 0.9;
  }
  const bubbleGeometry = new THREE.BufferGeometry();
  bubbleGeometry.setAttribute('position', new THREE.BufferAttribute(bubblePositions, 3));
  const bubbles = new THREE.Points(
    bubbleGeometry,
    new THREE.PointsMaterial({
      map: softDot(),
      color: new THREE.Color(P.cherenkovCore),
      size: 0.09,
      sizeAttenuation: true,
      transparent: true,
      opacity: 0,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
    }),
  );
  bubbles.renderOrder = 5;
  group.add(bubbles);

  /* --------------------------------------------------------------- lights */
  const fill = new THREE.PointLight(P.cherenkov, 0, 24, 1.7);
  fill.position.set(0, surfaceY - 0.6, 0);
  group.add(fill);
  const spill = new THREE.PointLight(P.cherenkov, 0, 16, 2);
  spill.position.set(0, surfaceY + 1.6, 0);
  group.add(spill);

  let elapsed = 0;
  function update(dt, { glow = 0, agitation = 0, activeShafts = 0 } = {}) {
    elapsed += dt;
    uniforms.uTime.value = elapsed;
    uniforms.uGlow.value = THREE.MathUtils.damp(uniforms.uGlow.value, glow, 2.2, dt);
    uniforms.uAgitation.value = THREE.MathUtils.damp(uniforms.uAgitation.value, agitation, 2.6, dt);
    const g = uniforms.uGlow.value;

    shafts.forEach((shaft, index) => { shaft.visible = index < activeShafts && g > 0.01; });

    const positions = bubbles.geometry.attributes.position;
    const speed = 0.18 + uniforms.uAgitation.value * 0.85;
    for (let i = 0; i < bubbleCount; i++) {
      let y = positions.getY(i) + speed * bubbleSeeds[i] * dt;
      if (y > surfaceY - 0.05) {
        y = floorY + 0.1;
        positions.setX(i, (Math.random() - 0.5) * half * 1.6);
        positions.setZ(i, (Math.random() - 0.5) * half * 1.6);
      }
      positions.setY(i, y);
    }
    positions.needsUpdate = true;
    bubbles.material.opacity = 0.1 + g * 0.55 + uniforms.uAgitation.value * 0.2;

    fill.intensity = 2 + g * 20;
    spill.intensity = 1 + g * 8;
  }

  return { group, update, addShaft, ceilingCaustics, uniforms, surface };
}
