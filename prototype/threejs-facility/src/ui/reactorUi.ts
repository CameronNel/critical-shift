import type { Hud } from './hud';
import { REACTOR_PREVIEW_STATES, type ReactorPreview, type ReactorPreviewState } from '../reactor/reactorPreview';

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

function button(label: string): HTMLButtonElement {
  const node = el('button', 'btn btn-toggle', label);
  node.type = 'button';
  node.dataset.hud = 'button';
  return node;
}

const LABELS: Record<ReactorPreviewState, string> = {
  normal: 'Normal',
  'high-output': 'High Output',
  instability: 'Instability',
  'cooling-emergency': 'Cooling Emergency',
  scram: 'SCRAM',
  meltdown: 'Meltdown',
};

/** Art-direction controls for the finished reactor-room visual states. */
export function buildReactorUi(hud: Hud, reactor: ReactorPreview): void {
  hud.addPanelSection('Reactor visual state', (body) => {
    const grid = el('div', 'toggle-grid');
    const buttons = new Map<ReactorPreviewState, HTMLButtonElement>();

    for (const state of REACTOR_PREVIEW_STATES) {
      const node = button(LABELS[state]);
      node.addEventListener('click', () => {
        reactor.setState(state);
        hud.toast(`Reactor preview: ${LABELS[state]}`);
      });
      buttons.set(state, node);
      grid.appendChild(node);
    }

    const hint = el(
      'p',
      'hint',
      'Visual review only. The buttons move the separately-authored Control Bank A/B parts, ' +
        'change pool level/agitation and expose emergency assets without mutating the facility JSON.',
    );
    body.append(grid, hint);

    reactor.onChange((state) => {
      for (const [key, node] of buttons) node.classList.toggle('on', key === state);
    });
  });
}
