#!/usr/bin/env python3
"""Rebuild non-cat pet GIFs with characteristic loops (not mouth-pop).

Cat stays Pop Cat (há miệng). Others get species-specific motion:
  dog     – pant / stick tongue out + wink
  bird    – blink + soft head bob
  rabbit  – nose twitch + ear wiggle + blink
  hamster – cheek puff + blink + nose twitch

Usage:
  python scripts/make_characteristic_gifs.py
"""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

PETS = ['dog', 'bird', 'rabbit', 'hamster']
ROOT = Path(__file__).resolve().parents[1] / 'assets' / 'animations'
MASTERS = Path(__file__).resolve().parent / 'masters'  # clean closed faces
N_FRAMES = 5
DURATION_MS = 120

# Landmarks on the closed-mouth face (128x128).
LANDMARKS = {
    'dog': {
        # Near eye sits high (dog looks up-right); far eye is the large dark blob.
        'eyes': [(64.0, 36.0, 8.0), (105.0, 51.0, 8.5)],
        'mouth': (90, 88),
        'tongue': {'w': 22, 'h': 28, 'color': (232, 105, 130, 255)},
    },
    'bird': {
        'eyes': [(59.4, 37.2, 7.5)],
    },
    'rabbit': {
        'eyes': [(64.2, 65.3, 7.0), (103.7, 62.0, 5.5)],
        'nose': (82, 78, 11),
        'ears': [(42, 6, 32, 52), (86, 2, 30, 48)],
    },
    'hamster': {
        'eyes': [(62.2, 46.8, 9.0), (98.3, 39.0, 6.0)],
        'nose': (76, 70, 9),
        'cheeks': [(42, 54, 26, 32), (88, 48, 26, 32)],
    },
}


def load_all(path: Path) -> list[Image.Image]:
    im = Image.open(path)
    frames = []
    for i in range(im.n_frames):
        im.seek(i)
        frames.append(im.convert('RGBA'))
    return frames


def pick_closed(frames: list[Image.Image]) -> Image.Image:
    scores = []
    for f in frames:
        px = f.load()
        w, h = f.size
        dark = 0
        for y in range(int(h * 0.4), h):
            for x in range(int(w * 0.2), int(w * 0.8)):
                r, g, b, a = px[x, y]
                if a > 200 and (r + g + b) < 90:
                    dark += 1
        scores.append(dark)
    return frames[min(range(len(scores)), key=lambda i: scores[i])].copy()


def get_closed(pet: str) -> Image.Image:
    master = MASTERS / f'{pet}.png'
    if master.exists():
        return Image.open(master).convert('RGBA')
    source = ROOT / pet / 'idle_1.gif'
    return pick_closed(load_all(source))


def sample_fur(img: Image.Image, cx: float, cy: float, r: float = 12) -> tuple[int, int, int, int]:
    px = img.load()
    w, h = img.size
    samples = []
    for ang in range(0, 360, 25):
        for dist in (r, r + 3, r + 6, r + 9):
            x = int(cx + math.cos(math.radians(ang)) * dist)
            y = int(cy + math.sin(math.radians(ang)) * dist)
            if 0 <= x < w and 0 <= y < h:
                p = px[x, y]
                if p[3] > 200 and (p[0] + p[1] + p[2]) > 140:
                    samples.append(p)
    if not samples:
        return (200, 180, 150, 255)
    n = len(samples)
    return (
        sum(s[0] for s in samples) // n,
        sum(s[1] for s in samples) // n,
        sum(s[2] for s in samples) // n,
        255,
    )


def blink_simple(base: Image.Image, eyes: list[tuple[float, float, float]], amount: float) -> Image.Image:
    """Paint fur eyelid over eyes. amount 0=open, 1=closed."""
    if amount <= 0.04:
        return base.copy()
    out = base.copy()
    px = out.load()
    src = base.load()
    w, h = out.size
    for cx, cy, rad in eyes:
        fur = sample_fur(base, cx, cy, rad + 3)
        r2 = (rad + 1.8) ** 2
        cover = min(1.0, amount)
        lid_y = cy - rad + (2 * rad) * cover
        for y in range(max(0, int(cy - rad - 3)), min(h, int(cy + rad + 4))):
            for x in range(max(0, int(cx - rad - 3)), min(w, int(cx + rad + 4))):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r2:
                    if y <= lid_y or cover >= 0.92:
                        t = 1.0 if cover >= 0.92 or y < lid_y - 1 else 0.9
                        r0, g0, b0, a0 = src[x, y]
                        if a0 < 30:
                            continue
                        px[x, y] = (
                            int(r0 * (1 - t) + fur[0] * t),
                            int(g0 * (1 - t) + fur[1] * t),
                            int(b0 * (1 - t) + fur[2] * t),
                            a0,
                        )
        if cover > 0.65:
            draw = ImageDraw.Draw(out)
            yline = cy + rad * 0.1
            shade = (max(0, fur[0] - 55), max(0, fur[1] - 55), max(0, fur[2] - 55), 230)
            draw.arc(
                [cx - rad * 0.95, yline - 2, cx + rad * 0.95, yline + rad * 0.75],
                200, 340, fill=shade, width=1,
            )
    return out


def draw_tongue(base: Image.Image, mouth_xy: tuple[int, int], scale: float, cfg: dict) -> Image.Image:
    if scale <= 0.05:
        return base.copy()
    out = base.copy()
    mx, my = mouth_xy
    tw = cfg['w'] * (0.5 + 0.5 * scale)
    th = cfg['h'] * scale
    color = cfg['color']
    shade = (max(0, color[0] - 40), max(0, color[1] - 50), max(0, color[2] - 30), 255)
    highlight = (min(255, color[0] + 30), min(255, color[1] + 45), min(255, color[2] + 40), 220)

    layer = Image.new('RGBA', out.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x0, y0 = mx - tw / 2, my - 1
    x1, y1 = mx + tw / 2, my + th
    d.ellipse([x0, y0, x1, y1], fill=color)
    d.ellipse([x0 + tw * 0.08, y1 - th * 0.5, x1 - tw * 0.08, y1 + 3], fill=color)
    # slight mouth opening so tongue reads as coming from inside
    d.ellipse([mx - tw * 0.35, my - 4, mx + tw * 0.35, my + 3], fill=(40, 20, 20, 200))
    d.ellipse([x0, y0, x1, y1], fill=color)
    d.line([(mx, my + 3), (mx, my + th * 0.8)], fill=shade, width=1)
    d.ellipse([x0 + tw * 0.18, y0 + th * 0.12, x0 + tw * 0.42, y0 + th * 0.4], fill=highlight)
    layer = layer.filter(ImageFilter.GaussianBlur(radius=0.55))
    return Image.alpha_composite(out, layer)


def shift_region(base: Image.Image, cx: float, cy: float, rad: float, dx: float, dy: float) -> Image.Image:
    out = base.copy()
    src = base.load()
    dst = out.load()
    w, h = base.size
    r2 = (rad + 1) ** 2
    for y in range(max(0, int(cy - rad - 2)), min(h, int(cy + rad + 3))):
        for x in range(max(0, int(cx - rad - 2)), min(w, int(cx + rad + 3))):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r2:
                sx, sy = int(x - dx), int(y - dy)
                if 0 <= sx < w and 0 <= sy < h and src[sx, sy][3] > 20:
                    dst[x, y] = src[sx, sy]
    return out


def wiggle_ear(base: Image.Image, box: tuple[int, int, int, int], angle_deg: float) -> Image.Image:
    if abs(angle_deg) < 0.4:
        return base
    x, y, bw, bh = box
    ear = base.crop((x, y, x + bw, y + bh))
    pivoted = ear.rotate(angle_deg, resample=Image.BICUBIC, expand=True, fillcolor=(0, 0, 0, 0))
    out = base.copy()
    mask = Image.new('L', (bw, bh), 0)
    md = ImageDraw.Draw(mask)
    md.ellipse([1, 1, bw - 2, bh - 2], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(1.2))
    clear = Image.new('RGBA', (bw, bh), (0, 0, 0, 0))
    region = Image.composite(clear, out.crop((x, y, x + bw, y + bh)), mask)
    out.paste(region, (x, y))
    px = x + (bw - pivoted.size[0]) // 2
    py = y + (bh - pivoted.size[1]) // 2
    out.alpha_composite(pivoted, (max(0, px), max(0, py)))
    return out


def puff_cheeks(base: Image.Image, cheeks: list[tuple[int, int, int, int]], amount: float) -> Image.Image:
    if amount <= 0.05:
        return base.copy()
    out = base.copy()
    for x, y, bw, bh in cheeks:
        patch = base.crop((x, y, x + bw, y + bh))
        new_w = max(bw + 1, int(bw * (1 + 0.22 * amount)))
        scaled = patch.resize((new_w, bh), Image.BICUBIC)
        px = x - (new_w - bw) // 2
        mask = Image.new('L', scaled.size, 0)
        md = ImageDraw.Draw(mask)
        md.ellipse([0, 0, scaled.size[0] - 1, scaled.size[1] - 1], fill=int(220 * min(1.0, 0.5 + 0.5 * amount)))
        mask = mask.filter(ImageFilter.GaussianBlur(2))
        layer = Image.new('RGBA', out.size, (0, 0, 0, 0))
        layer.paste(scaled, (px, y), mask)
        out = Image.alpha_composite(out, layer)
    return out


def head_bob(base: Image.Image, dy: float, dx: float = 0) -> Image.Image:
    if abs(dy) < 0.2 and abs(dx) < 0.2:
        return base.copy()
    out = Image.new('RGBA', base.size, (0, 0, 0, 0))
    out.paste(base, (int(round(dx)), int(round(dy))))
    return out


def make_dog_frames(closed: Image.Image) -> list[Image.Image]:
    lm = LANDMARKS['dog']
    # rest → tongue → full pant → wink+tongue → almost rest
    scales = [0.0, 0.65, 1.0, 0.85, 0.2]
    blinks = [0.0, 0.0, 0.1, 0.95, 0.0]  # wink-ish on peak
    # wink mainly left eye
    frames = []
    for s, b in zip(scales, blinks):
        f = draw_tongue(closed, lm['mouth'], s, lm['tongue'])
        if b > 0:
            # wink: close first eye harder
            eyes = [(lm['eyes'][0][0], lm['eyes'][0][1], lm['eyes'][0][2]),
                    (lm['eyes'][1][0], lm['eyes'][1][1], lm['eyes'][1][2] * 0.35)]
            f = blink_simple(f, eyes if b > 0.5 else lm['eyes'], b)
        frames.append(f)
    return frames


def make_bird_frames(closed: Image.Image) -> list[Image.Image]:
    lm = LANDMARKS['bird']
    blinks = [0.0, 0.55, 1.0, 0.4, 0.0]
    bobs = [(0, 0), (0, -1), (1, 0), (0, 1), (0, 0)]
    frames = []
    for b, (dx, dy) in zip(blinks, bobs):
        f = blink_simple(closed, lm['eyes'], b)
        f = head_bob(f, dy, dx)
        frames.append(f)
    return frames


def make_rabbit_frames(closed: Image.Image) -> list[Image.Image]:
    lm = LANDMARKS['rabbit']
    nose_shifts = [(0, 0), (-3, 0), (3, 1), (-2, 0), (0, 0)]
    ear_angles = [0, 4, -5, 3, 0]
    blinks = [0.0, 0.0, 0.15, 0.9, 0.0]
    frames = []
    nx, ny, nr = lm['nose']
    for (dx, dy), ang, b in zip(nose_shifts, ear_angles, blinks):
        f = closed.copy()
        if dx or dy:
            f = shift_region(f, nx, ny, nr, dx, dy)
            # whisker hint: tiny dark ticks near nose
            d = ImageDraw.Draw(f)
            tip = (max(0, 40), max(0, 30), max(0, 25), 180)
            d.line([(nx - 14, ny + 2), (nx - 22, ny + dy)], fill=tip, width=1)
            d.line([(nx + 10, ny + 1), (nx + 18, ny - 1 + dy)], fill=tip, width=1)
        if abs(ang) > 0.5:
            for ear in lm['ears']:
                f = wiggle_ear(f, ear, ang)
        if b > 0:
            f = blink_simple(f, lm['eyes'], b)
        frames.append(f)
    return frames


def make_hamster_frames(closed: Image.Image) -> list[Image.Image]:
    lm = LANDMARKS['hamster']
    puffs = [0.0, 0.5, 1.0, 0.6, 0.15]
    blinks = [0.0, 0.0, 0.25, 1.0, 0.0]
    nose_dx = [0, 2, 0, -2, 0]
    frames = []
    nx, ny, nr = lm['nose']
    for puff, b, dx in zip(puffs, blinks, nose_dx):
        f = puff_cheeks(closed, lm['cheeks'], puff)
        if dx:
            f = shift_region(f, nx, ny, nr, dx, 0)
        if b > 0:
            f = blink_simple(f, lm['eyes'], b)
        frames.append(f)
    return frames


MAKERS = {
    'dog': make_dog_frames,
    'bird': make_bird_frames,
    'rabbit': make_rabbit_frames,
    'hamster': make_hamster_frames,
}


def save_gif(frames: list[Image.Image], path: Path) -> None:
    frames[0].save(
        path,
        save_all=True,
        append_images=frames[1:],
        duration=DURATION_MS,
        loop=0,
        disposal=2,
        optimize=False,
    )


def main() -> None:
    for pet in PETS:
        pet_dir = ROOT / pet
        gifs = sorted(pet_dir.glob('*.gif'))
        if not gifs:
            print(f'skip {pet}: no gifs')
            continue
        closed = get_closed(pet)
        frames = MAKERS[pet](closed)
        assert len(frames) == N_FRAMES
        for gif_path in gifs:
            save_gif(frames, gif_path)
            print(f'wrote {gif_path.relative_to(ROOT)} ({N_FRAMES} frames, {pet})')


if __name__ == '__main__':
    main()
