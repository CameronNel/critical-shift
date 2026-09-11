const path=require('path');
const sharp=require('C:/Users/Camer/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
sharp(path.join(__dirname,'floorplan.svg'),{density:120}).png().toFile(path.join(__dirname,'floorplan.png')).then(()=>console.log('PLAN_PNG_OK'));
