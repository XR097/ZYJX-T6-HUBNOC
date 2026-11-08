// 渲染 figs/*.svg 到 PNG。用法：node render.cjs <figs 目录> <输出目录>。Owner: WangYizhao
const fs=require('fs'),path=require('path');
const sharp=require('C:/Users/18698/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
const figs=path.resolve(process.argv[2]||path.join(__dirname,'..','figs')),preview=path.resolve(process.argv[3]||path.join(__dirname,'preview'));
fs.mkdirSync(preview,{recursive:true});
(async()=>{
 const names=fs.readdirSync(figs).filter(x=>x.endsWith('.svg'));
 for(const name of names) await sharp(path.join(figs,name)).png().toFile(path.join(preview,name.replace('.svg','.png')));
 console.log('Rendered',names.length,'SVG files to',preview);
})().catch(e=>{console.error(e);process.exit(1)});
