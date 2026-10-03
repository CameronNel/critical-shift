import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';

/**
 * Post chain: bloom, then a grade.
 *
 * Bloom is not decoration here — it is the only reason a "glowing" pool reads as
 * emitting light rather than as a bright blue rectangle. The grade pass that
 * follows keeps it from turning the whole room milky: it pulls a warm/cool split
 * tone across the image, adds a vignette, and lifts the shadows just enough that
 * the deck never crushes to black the way the greybox did.
 */

const GradeShader = {
  uniforms: {
    tDiffuse: { value: null },
    uTime: { value: 0 },
    uWarm: { value: new THREE.Color('#ffe3c4') },
    uCool: { value: new THREE.Color('#b3cbd6') },
    uLift: { value: new THREE.Color('#182028') },
    uVignette: { value: 0.6 },
    uSaturation: { value: 1.06 },
    uAlarm: { value: 0 },
  },
  vertexShader: /* glsl */`
    varying vec2 vUv;
    void main() {
      vUv = uv;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: /* glsl */`
    uniform sampler2D tDiffuse;
    uniform float uTime;
    uniform vec3 uWarm;
    uniform vec3 uCool;
    uniform vec3 uLift;
    uniform float uVignette;
    uniform float uSaturation;
    uniform float uAlarm;
    varying vec2 vUv;

    void main() {
      vec4 texel = texture2D(tDiffuse, vUv);
      vec3 c = texel.rgb;
      float luma = dot(c, vec3(0.2126, 0.7152, 0.0722));

      // Split tone: sodium in the highlights, pool-cyan in the shadows. The
      // whole look of the room lives in these two lines.
      c *= mix(uCool, uWarm, smoothstep(0.18, 0.78, luma));
      c += uLift * (1.0 - smoothstep(0.0, 0.42, luma)) * 0.5;
      // Pull saturation out of the brightest *warm* values, so sodium lamps and
      // painted signs bloom to white instead of to orange. Deliberately excludes
      // cool highlights: the pool has to stay cyan however hot it gets.
      float warm = clamp((c.r - c.b) * 2.2, 0.0, 1.0);
      c = mix(c, vec3(luma), smoothstep(0.85, 1.7, luma) * 0.6 * warm);

      c = mix(vec3(luma), c, uSaturation);

      float d = distance(vUv, vec2(0.5));
      c *= mix(1.0, 1.0 - uVignette, smoothstep(0.34, 0.82, d));

      // Alarm wash, applied after the vignette so it reaches the corners.
      c = mix(c, c * vec3(1.6, 0.52, 0.44), uAlarm * 0.5);

      gl_FragColor = vec4(c, texel.a);
    }
  `,
};

export function createPostChain(renderer, scene, camera, quality) {
  const size = renderer.getSize(new THREE.Vector2());
  const composer = new EffectComposer(renderer);
  composer.setPixelRatio(renderer.getPixelRatio());
  composer.setSize(size.x, size.y);
  composer.addPass(new RenderPass(scene, camera));

  const bloom = new UnrealBloomPass(
    new THREE.Vector2(size.x, size.y),
    quality.bloomStrength,
    quality.bloomRadius,
    quality.bloomThreshold,
  );
  composer.addPass(bloom);

  const grade = new ShaderPass(GradeShader);
  composer.addPass(grade);
  composer.addPass(new OutputPass());

  let elapsed = 0;
  return {
    composer,
    bloom,
    grade,
    setSize(width, height) {
      composer.setPixelRatio(renderer.getPixelRatio());
      composer.setSize(width, height);
      bloom.setSize(width, height);
    },
    update(dt, { alarm = 0, glow = 0 } = {}) {
      elapsed += dt;
      grade.uniforms.uTime.value = elapsed;
      grade.uniforms.uAlarm.value = alarm;
      // A hot core pushes bloom slightly, so bringing the reactor up is
      // something you feel in the whole image, not only in the pool.
      bloom.strength = quality.bloomStrength * (1 + glow * 0.45);
    },
    render() {
      composer.render();
    },
  };
}
