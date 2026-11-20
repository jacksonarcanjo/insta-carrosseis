// uso: node tools/render.js <carrossel.html> <pasta_saida> <n_slides>
const { chromium } = require('playwright');
(async () => {
  const [html, out, n] = process.argv.slice(2);
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1200, height: 1500 }, deviceScaleFactor: 2 });
  await p.goto('file://' + html);
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(500);
  await p.waitForFunction(() => document.body.dataset.ready === '1' || !document.querySelector('.fg'), null, {timeout: 10000}).catch(() => {});
  for (let i = 1; i <= Number(n); i++) {
    await p.locator('#s' + i).screenshot({ path: `${out}/raw_${i}.png` });
  }
  await b.close();
})();
