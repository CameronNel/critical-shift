import type { App, LayerKey, NavMode } from '../core/app';
import { bindHoldButton, createTouchInput } from '../input/touchInput';

const LAYERS: { key: LayerKey; label: string }[] = [
  { key: 'roofs', label: 'Roofs' },
  { key: 'ground', label: 'Ground' },
  { key: 'labels', label: 'Labels' },
  { key: 'markers', label: 'Markers' },
  { key: 'routes', label: 'Routes' },
  { key: 'scaleRefs', label: 'Scale figures' },
];

function el<K extends keyof HTMLElementTagNameMap>(
  tag: K,
  className?: string,
  text?: string,
): HTMLElementTagNameMap[K] {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function button(label: string, className = 'btn'): HTMLButtonElement {
  const node = el('button', className, label);
  node.type = 'button';
  node.dataset.hud = 'button';
  return node;
}

/**
 * Single on-screen interface for desktop and phone. Every control is a real
 * button with a phone-sized target: nothing here requires a keyboard.
 */
export class Hud {
  readonly root: HTMLElement;
  private readonly modeBar: HTMLElement;
  private readonly actions: HTMLElement;
  private readonly panel: HTMLElement;
  private readonly panelBody: HTMLElement;
  private readonly statusChip: HTMLElement;
  private readonly crosshair: HTMLElement;
  private readonly toastHost: HTMLElement;
  private readonly modeButtons = new Map<NavMode, HTMLButtonElement>();
  private readonly flyOnly: HTMLElement[] = [];

  constructor(private readonly app: App, container: HTMLElement) {
    this.root = el('div', 'hud');

    const touch = createTouchInput(app.input);
    this.root.appendChild(touch.root);

    this.crosshair = el('div', 'crosshair');
    this.root.appendChild(this.crosshair);

    this.modeBar = el('div', 'hud-modes');
    this.root.appendChild(this.modeBar);

    const topRight = el('div', 'hud-top-right');
    this.statusChip = el('div', 'chip', '—');
    const menuButton = button('☰', 'btn btn-icon');
    menuButton.setAttribute('aria-label', 'Menu');
    menuButton.addEventListener('click', () => this.togglePanel());
    topRight.append(this.statusChip, menuButton);
    this.root.appendChild(topRight);

    this.actions = el('div', 'hud-actions');
    this.root.appendChild(this.actions);

    this.panel = el('aside', 'panel');
    const panelHead = el('div', 'panel-head');
    panelHead.appendChild(el('strong', undefined, 'Critical Shift — Greybox'));
    const close = button('✕', 'btn btn-icon');
    close.addEventListener('click', () => this.togglePanel(false));
    panelHead.appendChild(close);
    this.panelBody = el('div', 'panel-body');
    this.panel.append(panelHead, this.panelBody);
    this.root.appendChild(this.panel);

    this.toastHost = el('div', 'toasts');
    this.root.appendChild(this.toastHost);

    container.appendChild(this.root);

    this.registerMode('walk', 'Walk');
    this.registerMode('fly', 'Fly');
    this.buildActions();
    this.buildLayerSection();
    this.buildTeleportSection();
    this.buildHelpSection();

    app.onStatus((status) => this.render(status.mode, status.zone, status.fps));
    touch.onFirstTouch(() => this.root.classList.add('touch'));
  }

  registerMode(mode: NavMode, label: string): void {
    if (this.modeButtons.has(mode)) return;
    const node = button(label, 'btn btn-mode');
    node.addEventListener('click', () => this.app.setMode(mode));
    this.modeBar.appendChild(node);
    this.modeButtons.set(mode, node);
    this.render(this.app.mode, '', 0);
  }

  addAction(label: string, onClick: () => void, options: { flyOnly?: boolean } = {}): HTMLButtonElement {
    const node = button(label, 'btn btn-action');
    node.addEventListener('click', onClick);
    this.actions.appendChild(node);
    if (options.flyOnly) this.flyOnly.push(node);
    return node;
  }

  addHoldAction(label: string, onChange: (held: boolean) => void, flyOnly = false): HTMLElement {
    const node = button(label, 'btn btn-action');
    bindHoldButton(node, onChange);
    this.actions.appendChild(node);
    if (flyOnly) this.flyOnly.push(node);
    return node;
  }

  addPanelSection(title: string, build: (body: HTMLElement) => void): HTMLElement {
    const section = el('section', 'panel-section');
    section.appendChild(el('h3', undefined, title));
    const body = el('div', 'panel-section-body');
    section.appendChild(body);
    this.panelBody.appendChild(section);
    build(body);
    return section;
  }

  togglePanel(force?: boolean): void {
    const open = force ?? !this.panel.classList.contains('open');
    this.panel.classList.toggle('open', open);
    if (open) this.app.desktop.releaseLook();
  }

  toast(message: string, kind: 'info' | 'error' = 'info'): void {
    const node = el('div', `toast toast-${kind}`, message);
    this.toastHost.appendChild(node);
    setTimeout(() => node.classList.add('out'), 2600);
    setTimeout(() => node.remove(), 3200);
  }

  private render(mode: NavMode, zone: string, fps: number): void {
    for (const [key, node] of this.modeButtons) node.classList.toggle('on', key === mode);
    for (const node of this.flyOnly) node.classList.toggle('hidden', mode !== 'fly');
    this.crosshair.classList.toggle('hidden', mode === 'map');
    const p = this.app.nav.position;
    this.statusChip.textContent = `${zone}  ·  ${p.x.toFixed(0)} ${(p.y - 1.62).toFixed(
      0,
    )} ${p.z.toFixed(0)}  ·  ${fps} fps`;
  }

  private buildActions(): void {
    this.addAction('Reset', () => {
      this.app.respawn();
      this.toast('Respawned at the shift entrance');
    });
    this.addHoldAction('▲', (held) => {
      this.app.input.vertical = held ? 1 : 0;
    }, true);
    this.addHoldAction('▼', (held) => {
      this.app.input.vertical = held ? -1 : 0;
    }, true);
    const sprint = this.addAction('Sprint', () => {
      const on = !this.app.input.sprint;
      this.app.input.sprint = on;
      sprint.classList.toggle('on', on);
    });
  }

  private buildLayerSection(): void {
    this.addPanelSection('Layers', (body) => {
      const grid = el('div', 'toggle-grid');
      for (const { key, label } of LAYERS) {
        const node = button(label, 'btn btn-toggle');
        node.classList.toggle('on', this.app.isLayerVisible(key));
        node.addEventListener('click', () => {
          const next = !this.app.isLayerVisible(key);
          this.app.setLayerVisible(key, next);
          node.classList.toggle('on', next);
        });
        grid.appendChild(node);
      }
      body.appendChild(grid);
      body.appendChild(
        el(
          'p',
          'hint',
          'Hide Roofs to read the plan from above. Hide Ground to inspect the mine, ' +
            'the crusher pit and the maintenance spine.',
        ),
      );
    });
  }

  private buildTeleportSection(): void {
    this.addPanelSection('Go to', (body) => {
      const grid = el('div', 'toggle-grid');
      for (const spawn of this.app.spawns()) {
        const node = button(spawn.label, 'btn btn-toggle');
        node.addEventListener('click', () => {
          this.app.teleport(spawn.position, spawn.rotationY);
          this.togglePanel(false);
          this.toast(`Moved to ${spawn.label}`);
        });
        grid.appendChild(node);
      }
      body.appendChild(grid);
    });
  }

  private buildHelpSection(): void {
    this.addPanelSection('Controls', (body) => {
      const list = el('dl', 'help');
      const rows: [string, string][] = [
        ['Phone', 'Left thumb: move. Right thumb: look. Buttons for mode, height and reset.'],
        ['Desktop', 'WASD to move, mouse to look (click to lock), Ctrl or Shift to sprint.'],
        ['Fly', 'Space / Shift or the ▲ ▼ buttons for height. F toggles fly.'],
        ['Reset', 'R, or the Reset button, returns you to the shift entrance.'],
      ];
      for (const [term, description] of rows) {
        list.appendChild(el('dt', undefined, term));
        list.appendChild(el('dd', undefined, description));
      }
      body.appendChild(list);
    });
  }
}
