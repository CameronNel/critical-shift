/**
 * Inline the built bundle into single HTML files.
 *
 * The prototype has to be openable on a phone that has no dev server, so the
 * whole thing collapses to one file with no external requests.
 *
 *   dist-single/critical-shift-greybox.html  full document, open it anywhere
 *   dist-single/artifact-body.html           body content only, for hosts that
 *                                            supply their own html/head wrapper
 */
import { mkdirSync, readFileSync, readdirSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

const root = new URL('..', import.meta.url).pathname;
const dist = join(root, 'dist-inline');
const out = join(root, 'dist-single');

const html = readFileSync(join(dist, 'index.html'), 'utf8');
const assets = readdirSync(join(dist, 'assets'));
const jsName = assets.find((f) => f.endsWith('.js'));
const cssName = assets.find((f) => f.endsWith('.css'));
if (!jsName || !cssName) throw new Error('Build output is missing a .js or .css asset');

const js = readFileSync(join(dist, 'assets', jsName), 'utf8').replace(
  /\/\/# sourceMappingURL=.*$/m,
  '',
);
const css = readFileSync(join(dist, 'assets', cssName), 'utf8');

// Escape only the sequence that could close the script element early.
const safeJs = js.replaceAll('</script', '<\\/script');

const bootMarkup = `<div id="app">
  <canvas id="viewport"></canvas>
  <div id="ui"></div>
  <div id="boot">Loading facility…</div>
</div>`;

// Hosts that own the <head> cannot be given a viewport meta tag, so set one at
// runtime; without it a phone lays the page out at desktop width.
const viewportShim = `(function () {
  var existing = document.querySelector('meta[name="viewport"]');
  var meta = existing || document.createElement('meta');
  meta.name = 'viewport';
  meta.content =
    'width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover';
  if (!existing) document.head.appendChild(meta);
  document.documentElement.style.colorScheme = 'dark';
})();`;

const body = `${bootMarkup}
<style>${css}</style>
<script>${viewportShim}</script>
<script type="module">${safeJs}</script>`;

// Replacement functions, not strings: the bundle contains $& and $` sequences
// that String.replace would otherwise interpret as substitution patterns.
const standalone = html
  .replace(/<link rel="stylesheet"[^>]*>/g, () => `<style>${css}</style>`)
  .replace(
    /<script type="module"[^>]*><\/script>/g,
    () => `<script type="module">${safeJs}</script>`,
  );

mkdirSync(out, { recursive: true });
writeFileSync(join(out, 'critical-shift-greybox.html'), standalone);
writeFileSync(join(out, 'artifact-body.html'), body);

const kb = (s) => `${Math.round(s / 1024)} KB`;
console.log(`standalone: ${kb(standalone.length)}`);
console.log(`artifact body: ${kb(body.length)}`);
