// Render deterministik scene.html via headless Chromium (Playwright).
// node render.js stills out_dir t1,t2,...      -> PNG per t
// node render.js frames out_dir f0 f1 [fps]   -> JPEG frame f0..f1-1
const { chromium } = require('/opt/npm-tools/node_modules/playwright');
const fs = require('fs'), path = require('path');
const ROOT = __dirname;
const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json', '.ttf': 'font/ttf', '.png': 'image/png' };
(async () => {
  const [mode, outDir, a, b, fpsArg] = process.argv.slice(2);
  fs.mkdirSync(outDir, { recursive: true });
  let browser;
  try { browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] }); }
  catch (e) { console.error('launch gagal', e); process.exit(2); }
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  page.on('console', m => console.log('[page]', m.text()));
  page.on('pageerror', e => { console.error('[pageerror]', e.message); });
  await page.route('http://arn.local/**', r => { const f = path.join(ROOT, new URL(r.request().url()).pathname); if (!fs.existsSync(f)) return r.fulfill({ status: 404 }); r.fulfill({ status: 200, body: fs.readFileSync(f), contentType: MIME[path.extname(f)] || 'application/octet-stream' }); });
  await page.goto('http://arn.local/scene.html');
  await page.waitForFunction('window.READY === true', null, { timeout: 120000 });
  const grab = async (t, type) => page.evaluate(([t, type]) => { window.renderFrame(t); return document.getElementById('out').toDataURL(type, 0.93); }, [t, type]);
  const t0 = Date.now();
  if (mode === 'stills') {
    for (const ts of a.split(',')) { const t = parseFloat(ts); const d = await grab(t, 'image/png'); fs.writeFileSync(path.join(outDir, `still_${t.toFixed(2).padStart(6, '0')}.png`), Buffer.from(d.split(',')[1], 'base64')); }
  } else {
    const fps = parseFloat(fpsArg || '30'); const f0 = parseInt(a), f1 = parseInt(b);
    for (let f = f0; f < f1; f++) { const d = await grab(f / fps, 'image/jpeg'); fs.writeFileSync(path.join(outDir, `f_${String(f).padStart(5, '0')}.jpg`), Buffer.from(d.split(',')[1], 'base64')); if ((f - f0) % 60 === 0) console.log('frame', f, ((Date.now() - t0) / (f - f0 + 1)).toFixed(0), 'ms/frame'); }
  }
  console.log('selesai', ((Date.now() - t0) / 1000).toFixed(1), 's');
  await browser.close();
})();
