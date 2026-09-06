#!/usr/bin/env python3
"""Build composition fixtures that match the two cardigan photos (layout only)."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
BUGS = ROOT / "bugs"
W, H = 640, 800


def leather(img: Image.Image) -> None:
    px = img.load()
    for y in range(H):
        for x in range(W):
            n = (x * 13 + y * 7) % 17
            v = 18 + n
            px[x, y] = (v, v - 2, v - 4)


def wood_strip(draw: ImageDraw.ImageDraw) -> None:
    y0 = int(H * 0.94)
    for y in range(y0, H):
        tone = 168 + (y % 5) * 4
        draw.line([(0, y), (W, y)], fill=(tone, tone - 32, tone - 72))


def gingham_collar(draw: ImageDraw.ImageDraw, cx: int, y0: int, y1: int, half: int) -> None:
    cell = 8
    for y in range(y0, y1):
        for x in range(cx - half, cx + half):
            if ((x // cell) + (y // cell)) % 2 == 0:
                draw.point((x, y), fill=(196, 28, 42))
            else:
                draw.point((x, y), fill=(248, 246, 242))


def cardigan_mask(x: int, y: int) -> bool:
    cx, cy = W // 2, int(H * 0.46)
    # torso + sleeves
    torso = abs(x - cx) < 168 and 150 < y < 690 and abs(x - cx) * 0.15 + (y - 160) * 0.02 < 190
    left = (x - (cx - 210)) ** 2 / 90**2 + (y - 310) ** 2 / 210**2 < 1 and x < cx - 40
    right = (x - (cx + 210)) ** 2 / 90**2 + (y - 310) ** 2 / 210**2 < 1 and x > cx + 40
    return bool(torso or left or right)


def hearts(draw: ImageDraw.ImageDraw, color: tuple[int, int, int]) -> None:
    cx = W // 2
    for i, y in enumerate((250, 320, 390, 460, 530)):
        draw.ellipse((cx - 7, y - 6, cx + 7, y + 7), fill=color)


def cream_cardigan() -> Image.Image:
    img = Image.new("RGB", (W, H))
    leather(img)
    draw = ImageDraw.Draw(img)
    wood_strip(draw)
    px = img.load()
    base = (237, 226, 204)
    shadow = (210, 192, 160)
    highlight = (247, 242, 230)
    for y in range(H):
        for x in range(W):
            if cardigan_mask(x, y):
                dx = abs(((x) % 28) - 14)
                dy = abs(((y) % 28) - 14)
                if dx + dy < 5:
                    px[x, y] = highlight
                elif dx + dy < 11:
                    px[x, y] = base
                else:
                    px[x, y] = shadow
    gingham_collar(draw, W // 2, 132, 210, 150)
    hearts(draw, (196, 28, 42))
    # tiny red embroidery
    draw.ellipse((W // 2 + 48, 240, W // 2 + 72, 258), fill=(200, 36, 48))
    draw.ellipse((W // 2 - 80, 236, W // 2 - 52, 260), fill=(200, 36, 48))
    return img


def red_cardigan() -> Image.Image:
    img = Image.new("RGB", (W, H))
    leather(img)
    draw = ImageDraw.Draw(img)
    wood_strip(draw)
    px = img.load()
    base = (196, 30, 46)
    shadow = (107, 16, 24)
    highlight = (220, 48, 62)
    for y in range(H):
        for x in range(W):
            if cardigan_mask(x, y):
                dx = abs((x % 22) - 11)
                dy = abs((y % 22) - 11)
                if dx + dy < 4:
                    px[x, y] = highlight
                elif dx + dy > 14:
                    px[x, y] = shadow
                else:
                    px[x, y] = base
    gingham_collar(draw, W // 2, 132, 210, 150)
    hearts(draw, (176, 24, 36))
    # white embroidery
    for ox, oy in ((-64, 242), (-48, 258), (56, 246), (72, 262), (48, 272)):
        draw.ellipse((W // 2 + ox, oy, W // 2 + ox + 10, oy + 8), fill=(248, 246, 242))
    return img


def main() -> None:
    BUGS.mkdir(parents=True, exist_ok=True)
    cream_cardigan().save(BUGS / "sample-cream-cardigan.png")
    red_cardigan().save(BUGS / "sample-red-cardigan.png")
    print(f"wrote {BUGS / 'sample-cream-cardigan.png'}")
    print(f"wrote {BUGS / 'sample-red-cardigan.png'}")


if __name__ == "__main__":
    main()
