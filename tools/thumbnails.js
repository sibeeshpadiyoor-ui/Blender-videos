// Thumbnails in the Beyond the Obvious Physics style.
//   node tools/thumbnails.js            -> thumbnails/*.png
// Needs Playwright (npm i playwright) and the Inter / Liberation Serif fonts.
const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const WM = "file://" + path.join(ROOT, "assets/brand/watermark.png");
const INTER = "file:///usr/share/fonts/opentype/inter/Inter-Black.otf";
const SERIF = "file:///usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf";
const GOLD = "linear-gradient(135deg,#F4E2B0,#D9B26A 50%,#A8782E)";
const WORDS = [["Force", "#4CC9F0"], ["Energy", "#FF6B9D"],
               ["Momentum", "#FFB703"], ["Heat", "#5EE6A8"]];

function stars(w, h, n, seed = 4) {
  let s = seed;
  const rnd = () => ((s = (s * 16807) % 2147483647) / 2147483647);
  let out = "";
  for (let i = 0; i < n; i++) {
    const r = [0.8, 1.1, 1.5, 2][Math.floor(rnd() * 4)];
    out += `<circle cx="${(rnd() * w).toFixed(0)}" cy="${(rnd() * h).toFixed(0)}" r="${r}" fill="#fff" opacity="${(0.2 + rnd() * 0.6).toFixed(2)}"/>`;
  }
  return `<svg width="${w}" height="${h}" style="position:absolute;inset:0">${out}</svg>`;
}

const base = (w, h, body) => `<!doctype html><html><head><style>
@font-face{font-family:I;src:url("${INTER}")}
@font-face{font-family:S;src:url("${SERIF}");font-style:italic}
*{margin:0;box-sizing:border-box}
body{width:${w}px;height:${h}px;background:#02030A;position:relative;overflow:hidden;font-family:I,sans-serif;color:#fff}
.glow{position:absolute;inset:0;background:radial-gradient(ellipse 45% 55% at var(--gx,70%) 48%,#22306E 0%,rgba(2,3,10,0) 100%);opacity:.9}
.gold{background:${GOLD};-webkit-background-clip:text;color:transparent;font-family:S,serif;font-style:italic}
.foot{position:absolute;left:0;right:0;text-align:center;color:#D9B26A;letter-spacing:.34em;font-size:26px}
.pill{position:absolute;border:3px solid #D9B26A;border-radius:99px;color:#D9B26A;letter-spacing:.22em;padding:12px 30px;font-size:24px}
.wm{position:absolute}
.word{font-weight:900;line-height:1.05}
</style></head><body>
<div class="glow"></div>${stars(w, h, w > 1200 ? 140 : 200)}${body}</body></html>`;

const wide = base(1280, 720, `
<div class="pill" style="left:70px;top:56px">FUNDAMENTALS OF PHYSICS</div>
<img class="wm" src="${WM}" style="right:44px;top:34px;width:92px">
<div style="position:absolute;left:70px;top:150px;line-height:1">
  <div style="font-size:108px;letter-spacing:-2px">CAN YOU</div>
  <div style="font-size:108px;letter-spacing:-2px;margin-top:6px">EXPLAIN</div>
  <div class="gold" style="font-size:150px;margin-top:6px">them?</div>
</div>
<div style="position:absolute;left:715px;top:170px">
  ${WORDS.map(([t, c]) => `<div class="word" style="font-size:84px;color:${c}">${t}</div>`).join("")}
</div>
<div class="foot" style="bottom:34px">BEYOND THE OBVIOUS PHYSICS</div>`);

// Vertical cover: everything important sits in the middle 1080x1350, so the
// profile grid crop (4:5 or 1:1) keeps the message.
const tall = base(1080, 1920, `
<style>.glow{--gx:50%}</style>
<div class="pill" style="left:50%;transform:translateX(-50%);top:330px;white-space:nowrap">FUNDAMENTALS OF PHYSICS</div>
<img class="wm" src="${WM}" style="right:60px;top:60px;width:130px">
<div style="position:absolute;left:0;right:0;top:430px;text-align:center;line-height:1">
  <div style="font-size:104px;letter-spacing:-2px">CAN YOU EXPLAIN</div>
</div>
<div style="position:absolute;left:0;right:0;top:600px;text-align:center">
  ${WORDS.map(([t, c]) => `<div class="word" style="font-size:118px;color:${c}">${t}</div>`).join("")}
</div>
<div class="gold" style="position:absolute;left:0;right:0;top:1140px;text-align:center;font-size:150px">clearly?</div>
<div class="foot" style="bottom:300px;font-size:24px">BEYOND THE OBVIOUS PHYSICS</div>`);

(async () => {
  const out = path.join(ROOT, "thumbnails");
  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch({ args: ["--no-sandbox"] });
  for (const [name, html, w, h] of [
    ["trailer_youtube_1280x720", wide, 1280, 720],
    ["trailer_instagram_cover_1080x1920", tall, 1080, 1920]]) {
    const page = await browser.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: 1 });
    // Load from a real file: a page made with setContent() cannot read the
    // local fonts and logo.
    const tmp = path.join(out, "_page.html");
    fs.writeFileSync(tmp, html);
    await page.goto("file://" + tmp, { waitUntil: "load" });
    await page.evaluate(() => document.fonts.ready);
    await page.screenshot({ path: path.join(out, name + ".png") });
    console.log("wrote", name + ".png");
    fs.unlinkSync(tmp);
  }
  await browser.close();
})();
