// 渲染 figs/*.svg 到 PNG；依赖 sharp。用法：node render.cjs [figs 目录] [输出目录]。
const fs = require('node:fs');
const path = require('node:path');

async function main() {
    if (process.argv.includes('--help')) {
        console.log('Usage: node render.cjs [figs directory] [output directory]');
        console.log('Install sharp with npm install --no-save sharp, or set SHARP_MODULE to its module path.');
        return;
    }
    let sharp;
    try {
        sharp = require(process.env.SHARP_MODULE || 'sharp');
    } catch (error) {
        throw new Error('Cannot load sharp. Install it with npm install --no-save sharp, '
            + 'or set SHARP_MODULE to its module path. ' + error.message);
    }
    const figs = path.resolve(process.argv[2] || path.join(__dirname, '..', 'figs'));
    const preview = path.resolve(process.argv[3] || path.join(__dirname, 'preview'));
    const names = fs.readdirSync(figs).filter(name => name.endsWith('.svg')).sort();
    fs.mkdirSync(preview, {recursive: true});
    for (const name of names) {
        await sharp(path.join(figs, name)).png().toFile(path.join(preview, name.replace(/\.svg$/, '.png')));
    }
    console.log('Rendered', names.length, 'SVG files to', preview);
}

main().catch(error => {
    console.error(error.message);
    process.exitCode = 1;
});
