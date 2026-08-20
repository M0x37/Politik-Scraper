const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

async function main() {
  const [, , inputPath, outputPath, port = '3000'] = process.argv;
  if (!inputPath || !outputPath) {
    throw new Error('Usage: node render_sheet.cjs <input.txt> <output.png> [port]');
  }

  const text = fs.readFileSync(path.resolve(inputPath), 'utf8');
  const browser = await chromium.launch({ headless: true });

  try {
    const page = await browser.newPage({
      viewport: { width: 1000, height: 1100 },
      deviceScaleFactor: 2,
    });

    const url = `http://127.0.0.1:${port}/?text=${encodeURIComponent(text)}`;
    await page.goto(url, { waitUntil: 'networkidle', timeout: 60_000 });
    await page.waitForSelector('#paper', { timeout: 30_000 });
    await page.waitForTimeout(1_500);

    const pngBase64 = await page.locator('#paper').evaluate((canvas) => {
      if (!canvas || canvas.width === 0 || canvas.height === 0) {
        throw new Error('Canvas wurde nicht korrekt gerendert.');
      }
      return canvas.toDataURL('image/png').split(',')[1];
    });

    fs.mkdirSync(path.dirname(path.resolve(outputPath)), { recursive: true });
    fs.writeFileSync(path.resolve(outputPath), Buffer.from(pngBase64, 'base64'));
    console.log(`PNG erstellt: ${outputPath}`);
  } finally {
    await browser.close();
  }
}

main().catch((error) => {
  console.error(error.stack || error.message || error);
  process.exit(1);
});
