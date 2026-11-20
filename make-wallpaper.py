"""Generate original wallpapers for the Omarchy "miku" theme.

Teal equalizer bars under stage lighting on a teal-black background,
with a single hot-pink bar as the "01" accent. Needs Pillow.

    python make-wallpaper.py [output_dir] [width] [height]
"""
import math
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

BG_TOP = (14, 22, 24)      # #0e1618
BG_BOTTOM = (8, 14, 16)
TEAL = (57, 197, 187)      # #39c5bb
DEEP = (19, 122, 127)      # #137a7f
PINK = (232, 52, 142)      # #e8348e
LIGHT = (130, 230, 222)    # #82e6de


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def background(w, h):
    img = Image.new("RGB", (w, h))
    px = ImageDraw.Draw(img)
    for y in range(h):
        px.line([(0, y), (w, y)], fill=lerp(BG_TOP, BG_BOTTOM, y / h))
    # soft teal spotlight from above the stage
    spot = Image.new("L", (w, h), 0)
    ImageDraw.Draw(spot).ellipse(
        [w * 0.18, -h * 0.55, w * 0.82, h * 0.55], fill=60
    )
    spot = spot.filter(ImageFilter.GaussianBlur(w // 10))
    img = Image.composite(Image.new("RGB", (w, h), DEEP), img, spot)
    return img


def heights(n, rng):
    phase = [rng.uniform(0, math.tau) for _ in range(3)]
    out = []
    for i in range(n):
        x = i / (n - 1)
        env = math.sin(math.pi * x) ** 0.8  # taller in the middle
        wave = (
            0.55
            + 0.25 * math.sin(x * 9 + phase[0])
            + 0.15 * math.sin(x * 23 + phase[1])
            + 0.05 * math.sin(x * 51 + phase[2])
        )
        out.append(max(0.04, env * wave * rng.uniform(0.85, 1.0)))
    return out


def equalizer(w, h, seed, pink_index_frac):
    rng = random.Random(seed)
    img = background(w, h)
    bars = Image.new("RGB", (w, h), (0, 0, 0))
    mask = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(bars)
    m = ImageDraw.Draw(mask)

    n = 64
    left, right = w * 0.12, w * 0.88
    slot = (right - left) / n
    bar_w = slot * 0.58
    base = h * 0.72
    max_h = h * 0.42
    pink_i = int(n * pink_index_frac)

    for i, t in enumerate(heights(n, rng)):
        x0 = left + i * slot + (slot - bar_w) / 2
        x1 = x0 + bar_w
        top = base - t * max_h
        segs = max(1, int((base - top) / (bar_w * 0.55)))
        seg_h = (base - top) / segs
        for s in range(segs):
            y1 = base - s * seg_h
            y0 = y1 - seg_h * 0.78
            k = s / max(1, segs - 1)
            col = lerp(PINK, (242, 92, 166), k) if i == pink_i else lerp(DEEP, LIGHT, k ** 1.4)
            d.rectangle([x0, y0, x1, y1], fill=col)
            m.rectangle([x0, y0, x1, y1], fill=235)
        # faint reflection on the stage floor
        ry1 = base + (base - top) * 0.35
        refl = PINK if i == pink_i else DEEP
        d.rectangle([x0, base + seg_h * 0.3, x1, ry1], fill=refl)
        m.rectangle([x0, base + seg_h * 0.3, x1, ry1], fill=38)

    # glow: blurred copy of the bars underneath
    glow = bars.filter(ImageFilter.GaussianBlur(w // 120))
    glow_mask = mask.filter(ImageFilter.GaussianBlur(w // 120)).point(lambda v: int(v * 0.55))
    img = Image.composite(glow, img, glow_mask)
    img = Image.composite(bars, img, mask)

    # thin floor line
    ImageDraw.Draw(img).line(
        [(left, base + 2), (right, base + 2)], fill=lerp(DEEP, BG_TOP, 0.4), width=max(1, h // 720)
    )
    return img


def main():
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "backgrounds")
    w = int(sys.argv[2]) if len(sys.argv) > 2 else 3840
    h = int(sys.argv[3]) if len(sys.argv) > 3 else 2160
    out.mkdir(parents=True, exist_ok=True)
    equalizer(w, h, seed=39, pink_index_frac=0.39).save(out / "1-miku-equalizer.png", optimize=True)
    equalizer(w, h, seed=1, pink_index_frac=0.01 + 0.62).save(out / "2-miku-encore.png", optimize=True)
    print("wrote", *sorted(p.name for p in out.glob("*.png")))


if __name__ == "__main__":
    main()
