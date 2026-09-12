// Raster preview of the original editable architectural vector drawing.
const path = require('node:path');
const sharp = require('sharp');
sharp(path.join(__dirname, 'A101-plan.svg'))
  .png().toFile(path.join(__dirname, 'A101-plan-preview.png'))
  .then(info => process.stdout.write(JSON.stringify(info)))
  .catch(error => { process.stderr.write(String(error)); process.exitCode = 1; });
