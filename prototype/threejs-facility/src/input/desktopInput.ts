import type { InputState } from './inputState';

const LOOK_SPEED = 0.0022;

export interface DesktopInput {
  /** Ask the browser for pointer lock so the mouse can drive the camera. */
  requestLook(): void;
  releaseLook(): void;
  readonly locked: boolean;
  /** Register a handler for single-press shortcut keys (already lower-cased). */
  onShortcut(handler: (key: string, event: KeyboardEvent) => void): void;
  dispose(): void;
}

/**
 * Keyboard + pointer-lock mouse. Falls back to drag-to-look when pointer lock
 * is refused, which is what happens inside some embedded preview frames.
 */
export function createDesktopInput(
  canvas: HTMLCanvasElement,
  input: InputState,
  /** Suppress mouse-look, e.g. while an editor gizmo owns the pointer. */
  blocked: () => boolean = () => false,
): DesktopInput {
  const held = new Set<string>();
  const shortcutHandlers: ((key: string, event: KeyboardEvent) => void)[] = [];
  let dragging = false;
  let locked = false;

  const isTypingTarget = (target: EventTarget | null) =>
    target instanceof HTMLElement &&
    (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable);

  const applyMovement = () => {
    let x = 0;
    let y = 0;
    if (held.has('keyw') || held.has('arrowup')) y += 1;
    if (held.has('keys') || held.has('arrowdown')) y -= 1;
    if (held.has('keyd') || held.has('arrowright')) x += 1;
    if (held.has('keya') || held.has('arrowleft')) x -= 1;
    input.move.set(x, y);
    if (input.move.lengthSq() > 1) input.move.normalize();

    let v = 0;
    if (held.has('space')) v += 1;
    if (held.has('shiftleft') || held.has('shiftright')) v -= 1;
    input.vertical = v;
    input.sprint = held.has('controlleft') || held.has('controlright') || held.has('keyq');
  };

  const onKeyDown = (event: KeyboardEvent) => {
    if (isTypingTarget(event.target)) return;
    const code = event.code.toLowerCase();
    if (code === 'space') event.preventDefault();
    if (!held.has(code)) {
      if (code === 'space') input.jump = true;
      for (const handler of shortcutHandlers) handler(code, event);
    }
    held.add(code);
    applyMovement();
  };

  const onKeyUp = (event: KeyboardEvent) => {
    held.delete(event.code.toLowerCase());
    applyMovement();
  };

  const onBlur = () => {
    held.clear();
    applyMovement();
    dragging = false;
    input.looking = false;
  };

  const onMouseMove = (event: MouseEvent) => {
    if (!locked && !dragging) return;
    input.look.x -= event.movementX * LOOK_SPEED;
    input.look.y -= event.movementY * LOOK_SPEED;
  };

  // The HUD overlays the canvas, so mouse-look listens on the window and
  // ignores presses that land on interface elements.
  const onInterface = (target: EventTarget | null) =>
    target instanceof Element &&
    target.closest(
      '[data-hud="button"], [data-hud="legend"], .panel, .legend, input, select, textarea, label',
    ) !== null;

  const onMouseDown = (event: MouseEvent) => {
    if (event.button !== 0) return;
    if (onInterface(event.target)) return;
    if (blocked()) return;
    if (!locked) {
      dragging = true;
      input.looking = true;
    }
    requestLook();
  };

  const onMouseUp = () => {
    dragging = false;
    input.looking = locked;
  };

  const onLockChange = () => {
    locked = document.pointerLockElement === canvas;
    input.looking = locked;
    if (!locked) {
      held.clear();
      applyMovement();
    }
  };

  window.addEventListener('keydown', onKeyDown);
  window.addEventListener('keyup', onKeyUp);
  window.addEventListener('blur', onBlur);
  window.addEventListener('mousemove', onMouseMove);
  window.addEventListener('mousedown', onMouseDown);
  window.addEventListener('mouseup', onMouseUp);
  document.addEventListener('pointerlockchange', onLockChange);

  function requestLook(): void {
    if (document.pointerLockElement !== canvas) {
      const request = canvas.requestPointerLock?.bind(canvas);
      try {
        const result = request?.() as unknown;
        if (result instanceof Promise) result.catch(() => undefined);
      } catch {
        /* Pointer lock is unavailable; drag-to-look still works. */
      }
    }
  }

  return {
    get locked() {
      return locked;
    },
    requestLook,
    releaseLook() {
      if (document.pointerLockElement === canvas) document.exitPointerLock();
    },
    onShortcut(handler) {
      shortcutHandlers.push(handler);
    },
    dispose() {
      window.removeEventListener('keydown', onKeyDown);
      window.removeEventListener('keyup', onKeyUp);
      window.removeEventListener('blur', onBlur);
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('mousedown', onMouseDown);
      window.removeEventListener('mouseup', onMouseUp);
      document.removeEventListener('pointerlockchange', onLockChange);
    },
  };
}
