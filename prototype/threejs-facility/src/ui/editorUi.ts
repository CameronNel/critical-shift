import type { Editor } from '../editor/editor';
import type { Hud } from './hud';

const STEPS = [0.25, 0.5, 1, 2, 5];

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

function button(label: string, className = 'btn btn-toggle'): HTMLButtonElement {
  const node = el('button', className, label);
  node.type = 'button';
  node.dataset.hud = 'button';
  return node;
}

/**
 * Editor panel. Transforms are nudge buttons and typed numbers rather than a
 * 3D gizmo: on a phone a gizmo is unusable, and for a greybox "move this wall
 * two metres east" is what you actually want to say.
 */
export function buildEditorUi(hud: Hud, editor: Editor): void {
  let body: HTMLElement;
  hud.addPanelSection('Edit', (host) => {
    body = host;
  });

  const empty = el(
    'p',
    'hint',
    'Switch to Edit, then tap an object to select it. Press and drag still looks around.',
  );
  const content = el('div', 'editor');

  const heading = el('div', 'editor-heading');
  const idLine = el('strong');
  const typeLine = el('span', 'hint');
  heading.append(idLine, typeLine);

  const stepRow = el('div', 'chip-row');
  stepRow.appendChild(el('span', 'field-label', 'Step'));
  const stepButtons = STEPS.map((value) => {
    const node = button(`${value} m`, 'btn btn-toggle btn-compact');
    node.addEventListener('click', () => {
      editor.step = value;
      for (const other of stepButtons) other.classList.toggle('on', other === node);
    });
    stepRow.appendChild(node);
    return node;
  });
  stepButtons[2].classList.add('on');

  const moveGrid = el('div', 'nudge-grid');
  const axes: [string, 0 | 1 | 2][] = [
    ['X', 0],
    ['Y', 1],
    ['Z', 2],
  ];
  for (const [name, axis] of axes) {
    const minus = button(`−${name}`, 'btn btn-toggle');
    minus.addEventListener('click', () => editor.nudge(axis, -1));
    const plus = button(`+${name}`, 'btn btn-toggle');
    plus.addEventListener('click', () => editor.nudge(axis, 1));
    moveGrid.append(minus, plus);
  }

  const rotateRow = el('div', 'chip-row');
  rotateRow.appendChild(el('span', 'field-label', 'Rotate'));
  for (const degrees of [-90, -15, 15, 90]) {
    const node = button(`${degrees > 0 ? '+' : ''}${degrees}°`, 'btn btn-toggle btn-compact');
    node.addEventListener('click', () => editor.rotate(degrees));
    rotateRow.appendChild(node);
  }

  const scaleRow = el('div', 'chip-row');
  scaleRow.appendChild(el('span', 'field-label', 'Scale'));
  for (const [label, factor] of [
    ['−10%', 1 / 1.1],
    ['+10%', 1.1],
    ['−50%', 0.5],
    ['×2', 2],
  ] as const) {
    const node = button(label, 'btn btn-toggle btn-compact');
    node.addEventListener('click', () => editor.scale(factor));
    scaleRow.appendChild(node);
  }

  const textRows = el('div', 'field-list');
  const labelInput = el('input', 'text-input') as HTMLInputElement;
  labelInput.placeholder = 'Label';
  labelInput.addEventListener('change', () => editor.setText('label', labelInput.value));
  const notesInput = el('input', 'text-input') as HTMLInputElement;
  notesInput.placeholder = 'Design note';
  notesInput.addEventListener('change', () => editor.setText('notes', notesInput.value));
  textRows.append(labelInput, notesInput);

  const numberRows = el('div', 'field-list');

  const actions = el('div', 'chip-row');
  const focusButton = button('Focus');
  focusButton.addEventListener('click', () => editor.focus());
  const duplicateButton = button('Duplicate');
  duplicateButton.addEventListener('click', () => {
    editor.duplicate();
    hud.toast('Duplicated');
  });
  const hideButton = button('Hide');
  hideButton.addEventListener('click', () => editor.toggleHidden());
  const deleteButton = button('Delete', 'btn btn-toggle btn-danger');
  deleteButton.addEventListener('click', () => {
    editor.remove();
    hud.toast('Deleted');
  });
  const deselectButton = button('Deselect');
  deselectButton.addEventListener('click', () => editor.select(null));
  actions.append(focusButton, duplicateButton, hideButton, deselectButton, deleteButton);

  content.append(heading, stepRow, moveGrid, rotateRow, scaleRow, textRows, numberRows, actions);

  editor.onChange((selected) => {
    body.replaceChildren(selected ? content : empty);
    if (!selected) return;
    idLine.textContent = selected.id;
    typeLine.textContent = `${selected.type} · ${selected.zone}${selected.hidden ? ' · hidden' : ''}`;
    labelInput.value = selected.label ?? '';
    notesInput.value = selected.notes ?? '';
    hideButton.textContent = selected.hidden ? 'Show' : 'Hide';

    numberRows.replaceChildren();
    for (const field of editor.fields()) {
      const row = el('div', 'field-row');
      row.appendChild(el('span', 'field-label', field.label));
      field.values.forEach((value, index) => {
        const input = el('input', 'num-input') as HTMLInputElement;
        input.type = 'number';
        input.step = '0.1';
        input.value = String(Math.round(value * 1000) / 1000);
        input.title = `${field.label} ${field.parts[index] ?? ''}`.trim();
        input.addEventListener('change', () => {
          editor.setNumber(field.key, index, Number(input.value));
        });
        row.appendChild(input);
      });
      numberRows.appendChild(row);
    }
  });
}
