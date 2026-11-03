import { mkdir, writeFile } from "node:fs/promises";
import { spawn } from "node:child_process";
import path from "node:path";
import puppeteer from "puppeteer-core";

const ORIGIN = process.env.SHOP_ORIGIN || "http://127.0.0.1:43147";
const ARTIFACTS = "/opt/cursor/artifacts";
const PREVIEW = "/workspace/public/preview";
const CHROME = process.env.CHROME_PATH || "/usr/bin/google-chrome";

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function run(cmd, args) {
  return new Promise((resolve, reject) => {
    const child = spawn(cmd, args, { stdio: "inherit" });
    child.on("exit", (code) => {
      if (code === 0) {
        resolve();
      } else {
        reject(new Error(`${cmd} exited ${code}`));
      }
    });
  });
}

async function framesToMp4(dir, pattern, dest, fps = 20) {
  await run("ffmpeg", [
    "-y",
    "-framerate",
    String(fps),
    "-i",
    path.join(dir, pattern),
    "-c:v",
    "libx264",
    "-pix_fmt",
    "yuv420p",
    "-movflags",
    "+faststart",
    "-vf",
    "scale=trunc(iw/2)*2:trunc(ih/2)*2",
    dest,
  ]);
}

async function waitVisible(page, selector) {
  await page.waitForFunction(
    (sel) => {
      const el = document.querySelector(sel);
      if (!el) {
        return false;
      }
      const box = el.getBoundingClientRect();
      return box.width > 40 && box.top >= 0 && box.top < window.innerHeight - 80;
    },
    { timeout: 15000 },
    selector,
  );
}

async function main() {
  await mkdir(ARTIFACTS, { recursive: true });
  await mkdir(PREVIEW, { recursive: true });
  await mkdir("/tmp/glass-tab", { recursive: true });
  await mkdir("/tmp/glass-color", { recursive: true });

  const browser = await puppeteer.launch({
    executablePath: CHROME,
    headless: "new",
    args: [
      "--no-sandbox",
      "--disable-dev-shm-usage",
      "--window-size=1440,3200",
      "--force-device-scale-factor=1",
      "--hide-scrollbars",
    ],
    defaultViewport: { width: 1440, height: 2800, deviceScaleFactor: 1 },
  });
  const page = await browser.newPage();
  await page.emulateMediaFeatures([{ name: "prefers-reduced-motion", value: "no-preference" }]);
  const client = await page.createCDPSession();
  await client.send("Animation.enable");
  await client.send("Animation.setPlaybackRate", { playbackRate: 0.18 });

  await page.goto(`${ORIGIN}/`, { waitUntil: "networkidle0", timeout: 60000 });
  await page.waitForSelector("#featured-collection");
  await page.waitForSelector("#featured-collection a[href='/m/A01'] img");
  await sleep(400);

  const featured = await page.$("#featured-collection");
  if (!featured) {
    throw new Error("Featured collection missing");
  }

  async function grabTab() {
    return featured.screenshot({ type: "jpeg", quality: 82 });
  }

  async function clickTab(label) {
    await page.evaluate((name) => {
      const tab = [...document.querySelectorAll('[data-testid="featured-filter-tab"]')].find((el) =>
        el.textContent?.includes(name),
      );
      if (!tab || !(tab instanceof HTMLElement)) {
        throw new Error(`Missing tab ${name}`);
      }
      tab.click();
    }, label);
  }

  const tabShots = [];
  tabShots.push(await grabTab());
  await clickTab("Tops");
  for (let i = 0; i < 14; i += 1) {
    tabShots.push(await grabTab());
    await sleep(50);
  }
  await sleep(250);
  await clickTab("All");
  for (let i = 0; i < 14; i += 1) {
    tabShots.push(await grabTab());
    await sleep(50);
  }

  for (const [i, shot] of tabShots.entries()) {
    await writeFile(`/tmp/glass-tab/frame-${String(i).padStart(3, "0")}.jpg`, shot);
  }

  const a01Card = await page.$("#featured-collection li:has(a[href='/m/A01'])");
  if (!a01Card) {
    throw new Error("A01 card missing");
  }

  async function grabColor() {
    return a01Card.screenshot({ type: "jpeg", quality: 82 });
  }

  async function clickColor(id) {
    await page.evaluate((colorId) => {
      const chip = document.querySelector(
        `#featured-collection li:has(a[href="/m/A01"]) [data-color-id="${colorId}"]`,
      );
      if (!chip || !(chip instanceof HTMLElement)) {
        throw new Error(`Missing A01 ${colorId}`);
      }
      chip.click();
    }, id);
  }

  const colorShots = [];
  colorShots.push(await grabColor());
  await clickColor("xanh");
  for (let i = 0; i < 12; i += 1) {
    colorShots.push(await grabColor());
    await sleep(40);
  }
  await sleep(220);
  await clickColor("kem");
  for (let i = 0; i < 12; i += 1) {
    colorShots.push(await grabColor());
    await sleep(40);
  }

  for (const [i, shot] of colorShots.entries()) {
    await writeFile(`/tmp/glass-color/frame-${String(i).padStart(3, "0")}.jpg`, shot);
  }

  await featured.screenshot({
    path: path.join(ARTIFACTS, "glass_featured_rest.jpg"),
    type: "jpeg",
    quality: 84,
  });

  await browser.close();

  const midTab = tabShots[4] ?? tabShots[2];
  const midColor = colorShots[3] ?? colorShots[2];
  if (!midTab || !midColor) {
    throw new Error("Mid-transition frames missing");
  }
  await writeFile(path.join(ARTIFACTS, "glass_tab_mid.jpg"), midTab);
  await writeFile(path.join(ARTIFACTS, "glass_color_mid.jpg"), midColor);

  await framesToMp4("/tmp/glass-tab", "frame-%03d.jpg", path.join(ARTIFACTS, "glass_tab_demo.mp4"));
  await framesToMp4("/tmp/glass-color", "frame-%03d.jpg", path.join(ARTIFACTS, "glass_color_demo.mp4"));
  await run("ffmpeg", ["-y", "-i", path.join(ARTIFACTS, "glass_tab_mid.jpg"), path.join(ARTIFACTS, "glass_tab_mid.webp")]);
  await run("ffmpeg", ["-y", "-i", path.join(ARTIFACTS, "glass_color_mid.jpg"), path.join(ARTIFACTS, "glass_color_mid.webp")]);

  for (const name of [
    "glass_tab_demo.mp4",
    "glass_color_demo.mp4",
    "glass_tab_mid.webp",
    "glass_color_mid.webp",
  ]) {
    await run("cp", [path.join(ARTIFACTS, name), path.join(PREVIEW, name)]);
  }
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
