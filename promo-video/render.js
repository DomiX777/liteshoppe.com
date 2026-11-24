// Usage: node render.js            -> full render to out/promo_silent.mp4
//        node render.js --stills DIR t1 t2 ...  -> PNG stills
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path'); const fs = require('fs');
(async () => {
  const args = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  page.on('pageerror', e => console.error('PAGE ERROR', e.message));
  await page.goto('file://' + path.resolve(__dirname, 'ad.html'));
  await page.waitForFunction(() => window.READY);
  if (args[0] === '--stills') {
    const dir = args[1];
    for (const t of args.slice(2)) { await page.evaluate(t => seek(+t, Math.round(t * 30)), t); await page.screenshot({ path: `${dir}/t${t}.png` }); }
    await browser.close(); return;
  }
  const FPS = 30, DUR = await page.evaluate(() => window.DUR), N = Math.round(DUR * FPS);
  fs.mkdirSync(path.join(__dirname, 'out'), { recursive: true });
  const ff = spawn('ffmpeg', ['-y', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', path.join(__dirname, 'out/promo_silent.mp4')], { stdio: ['pipe', 'ignore', 'inherit'] });
  for (let f = 0; f < N; f++) {
    await page.evaluate(f => seek(f / 30, f), f);
    const buf = await page.screenshot({ type: 'jpeg', quality: 95 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (f % 60 === 0) console.log(`frame ${f}/${N}`);
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r));
  await browser.close();
  fs.writeFileSync(path.join(__dirname, 'out/cuts.json'), JSON.stringify(await Promise.resolve([4.5, 10, 15.5, 21, 26.5, 31])));
})();
