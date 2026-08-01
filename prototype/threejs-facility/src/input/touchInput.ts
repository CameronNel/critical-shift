import type { InputState } from './inputState';

const LOOK_SPEED = 0.0032;
const STICK_RADIUS = 62;
const DEAD_ZONE = 0.12;

export interface TouchInput {
  root: HTMLElement;
  /** True once a real touch has been seen; the layer stays inert before that. */
  readonly active: boolean;
  onFirstTouch(handler: () => void): void;
  dispose(): void;
}

/**
 * Landscape phone controls: a dynamic joystick wherever the left thumb lands,
 * drag-to-look on the right. The stick base follows the first touch instead of
 * being fixed, so the layout works on any phone size and any grip.
 */
export function createTouchInput(input: InputState): TouchInput {
  const root = document.createElement('div');
  root.className = 'touch-layer';
  root.dataset.hud = 'touch';

  const stick = document.createElement('div');
  stick.className = 'stick';
  const knob = document.createElement('div');
  knob.className = 'stick-knob';
  stick.appendChild(knob);
  root.appendChild(stick);

  let movePointer: number | null = null;
  let lookPointer: number | null = null;
  let originX = 0;
  let originY = 0;
  let lastX = 0;
  let lastY = 0;
  let active = false;
  const firstTouchHandlers: (() => void)[] = [];

  const showStick = (x: number, y: number) => {
    stick.style.left = `${x}px`;
    stick.style.top = `${y}px`;
    stick.classList.add('visible');
  };

  const setKnob = (dx: number, dy: number) => {
    knob.style.transform = `translate(calc(-50% + ${dx}px), calc(-50% + ${dy}px))`;
  };

  const clearStick = () => {
    stick.classList.remove('visible');
    setKnob(0, 0);
    input.move.set(0, 0);
  };

  const onPointerDown = (event: PointerEvent) => {
    if (event.pointerType === 'mouse') return;
    if (!active) {
      active = true;
      root.classList.add('active');
      for (const handler of firstTouchHandlers) handler();
    }
    const leftHalf = event.clientX < window.innerWidth * 0.45;
    if (leftHalf && movePointer === null) {
      movePointer = event.pointerId;
      originX = event.clientX;
      originY = event.clientY;
      showStick(originX, originY);
      setKnob(0, 0);
      root.setPointerCapture(event.pointerId);
      event.preventDefault();
    } else if (!leftHalf && lookPointer === null) {
      lookPointer = event.pointerId;
      lastX = event.clientX;
      lastY = event.clientY;
      input.looking = true;
      root.setPointerCapture(event.pointerId);
      event.preventDefault();
    }
  };

  const onPointerMove = (event: PointerEvent) => {
    if (event.pointerId === movePointer) {
      let dx = event.clientX - originX;
      let dy = event.clientY - originY;
      const distance = Math.hypot(dx, dy);
      if (distance > STICK_RADIUS) {
        dx = (dx / distance) * STICK_RADIUS;
        dy = (dy / distance) * STICK_RADIUS;
      }
      setKnob(dx, dy);
      const nx = dx / STICK_RADIUS;
      const ny = -dy / STICK_RADIUS;
      const magnitude = Math.hypot(nx, ny);
      if (magnitude < DEAD_ZONE) {
        input.move.set(0, 0);
      } else {
        // Rescale past the dead zone so slow walking is still possible.
        const scaled = (magnitude - DEAD_ZONE) / (1 - DEAD_ZONE) / magnitude;
        input.move.set(nx * scaled, ny * scaled);
      }
      event.preventDefault();
    } else if (event.pointerId === lookPointer) {
      input.look.x -= (event.clientX - lastX) * LOOK_SPEED;
      input.look.y -= (event.clientY - lastY) * LOOK_SPEED;
      lastX = event.clientX;
      lastY = event.clientY;
      event.preventDefault();
    }
  };

  const onPointerUp = (event: PointerEvent) => {
    if (event.pointerId === movePointer) {
      movePointer = null;
      clearStick();
    } else if (event.pointerId === lookPointer) {
      lookPointer = null;
      input.looking = false;
    }
  };

  root.addEventListener('pointerdown', onPointerDown);
  root.addEventListener('pointermove', onPointerMove);
  root.addEventListener('pointerup', onPointerUp);
  root.addEventListener('pointercancel', onPointerUp);
  root.addEventListener('contextmenu', (event) => event.preventDefault());

  return {
    root,
    get active() {
      return active;
    },
    onFirstTouch(handler) {
      firstTouchHandlers.push(handler);
    },
    dispose() {
      root.remove();
    },
  };
}

/** A held button that drives a value while pressed. Used for fly up/down. */
export function bindHoldButton(
  element: HTMLElement,
  onChange: (held: boolean) => void,
): () => void {
  const down = (event: PointerEvent) => {
    element.setPointerCapture(event.pointerId);
    element.classList.add('held');
    onChange(true);
    event.preventDefault();
    event.stopPropagation();
  };
  const up = (event: PointerEvent) => {
    element.classList.remove('held');
    onChange(false);
    event.stopPropagation();
  };
  element.addEventListener('pointerdown', down);
  element.addEventListener('pointerup', up);
  element.addEventListener('pointercancel', up);
  element.addEventListener('pointerleave', up);
  return () => {
    element.removeEventListener('pointerdown', down);
    element.removeEventListener('pointerup', up);
    element.removeEventListener('pointercancel', up);
    element.removeEventListener('pointerleave', up);
  };
}
