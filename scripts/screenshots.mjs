import { spawn } from 'node:child_process';
import { mkdirSync, writeFileSync } from 'node:fs';
import { setTimeout as sleep } from 'node:timers/promises';

const BASE = process.env.BASE_URL || 'http://127.0.0.1:9002/word-chart-app/';
const OUT = process.env.OUT_DIR || new URL('../screenshots/', import.meta.url).pathname;
const CHROME = process.env.CHROME || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const PORT = 9333;

const shots = [
  { name: '1-landing', path: '', width: 1280, height: 760 },
  { name: '2-word-counts', path: 'word-counts.html', width: 1280, height: 1200, wait: 2500 },
  {
    name: '3-unique-comparison', path: 'unique.html', width: 1280, height: 1250, wait: 3000,
    run: `(async () => {
      await new Promise(r => setTimeout(r, 800));
      document.getElementById('book1').value = 'Pride_and_Prejudice';
      document.getElementById('book2').value = 'Tarzan_of_the_Apes';
      document.getElementById('compareForm').requestSubmit();
    })()`,
  },
  {
    name: '4-word-chart', path: 'chart.html', width: 1280, height: 1150, wait: 2500,
    run: `(async () => {
      await new Promise(r => setTimeout(r, 800));
      document.getElementById('book').value = 'War_and_Peace';
      document.getElementById('topN').value = 20;
      document.getElementById('filterLevel').value = 'literary';
      document.getElementById('chartForm').requestSubmit();
    })()`,
  },
];

mkdirSync(OUT, { recursive: true });
const chrome = spawn(CHROME, ['--headless=new', `--remote-debugging-port=${PORT}`, '--hide-scrollbars',
  '--user-data-dir=/tmp/wc-chrome', '--force-color-profile=srgb', 'about:blank'], { stdio: 'ignore' });

try {
  let target;
  for (let i = 0; i < 50 && !target; i += 1) {
    try { target = await (await fetch(`http://127.0.0.1:${PORT}/json/new?about:blank`, { method: 'PUT' })).json(); }
    catch { await sleep(200); }
  }
  const ws = new WebSocket(target.webSocketDebuggerUrl);
  await new Promise((resolve) => ws.addEventListener('open', resolve, { once: true }));
  let id = 0;
  const pending = new Map();
  ws.addEventListener('message', (event) => {
    const msg = JSON.parse(event.data);
    if (msg.id && pending.has(msg.id)) { pending.get(msg.id)(msg); pending.delete(msg.id); }
  });
  const send = (method, params = {}) => new Promise((resolve) => {
    id += 1; pending.set(id, resolve); ws.send(JSON.stringify({ id, method, params }));
  });

  await send('Page.enable');
  for (const shot of shots) {
    await send('Emulation.setDeviceMetricsOverride', { width: shot.width, height: shot.height, deviceScaleFactor: 1, mobile: false });
    await send('Page.navigate', { url: BASE + shot.path });
    await sleep(1500);
    if (shot.run) await send('Runtime.evaluate', { expression: shot.run, awaitPromise: true });
    await sleep(shot.wait || 800);
    const { result } = await send('Page.captureScreenshot', { format: 'png' });
    writeFileSync(`${OUT}${shot.name}.png`, Buffer.from(result.data, 'base64'));
    console.log(`${OUT}${shot.name}.png`);
  }
  ws.close();
} finally {
  chrome.kill();
}
