const path = require('path');
const sharp = require('C:/Users/Camer/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
const root=path.resolve(__dirname,'..');
sharp(path.join(root,'architecture/A101-plan.svg')).png().toFile(path.join(root,'architecture/A101-plan-preview.png')).then(()=>console.log('Dimensioned plan rendered'));
