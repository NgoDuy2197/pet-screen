#!/usr/bin/env python3
"""Expand non-cat pet GIFs to smooth 5-frame open/close mouth loops."""
from PIL import Image, ImageDraw, ImageFilter
import math
from pathlib import Path

PETS = ['dog', 'bird', 'rabbit', 'hamster']
ROOT = Path(__file__).resolve().parents[1] / 'assets' / 'animations'
SCALES = [0.0, 0.35, 1.0, 0.45, 0.08]
DURATION_MS = 80


def load_all(path):
    im = Image.open(path)
    frames = []
    for i in range(im.n_frames):
        im.seek(i)
        frames.append(im.convert('RGBA'))
    return frames


def pick_closed_open(frames):
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
    open_i = max(range(len(scores)), key=lambda i: scores[i])
    closed_i = min(range(len(scores)), key=lambda i: scores[i])
    return frames[closed_i].copy(), frames[open_i].copy()


def mouth_diff_info(closed, open_img):
    cp = closed.load()
    op = open_img.load()
    w, h = closed.size
    pts = []
    for y in range(h):
        for x in range(w):
            r2, g2, b2, a2 = op[x, y]
            r1, g1, b1, a1 = cp[x, y]
            open_dark = a2 > 200 and (r2 + g2 + b2) < 100
            closed_dark = a1 > 200 and (r1 + g1 + b1) < 100
            if open_dark and not closed_dark:
                pts.append((x, y))
            elif open_dark and closed_dark and (r1 + g1 + b1) - (r2 + g2 + b2) > 40:
                pts.append((x, y))
    if len(pts) < 20:
        for y in range(int(h * 0.45), h):
            for x in range(int(w * 0.25), int(w * 0.75)):
                r2, g2, b2, a2 = op[x, y]
                if a2 > 200 and (r2 + g2 + b2) < 90:
                    pts.append((x, y))
    if not pts:
        return w / 2, h * 0.72, min(w, h) * 0.2
    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)
    dists = sorted(math.hypot(x - cx, y - cy) for x, y in pts)
    rad = dists[int(len(dists) * 0.92)] * 1.12
    return cx, cy, max(rad, 8)


def make_frame(closed, open_img, scale, cx, cy, max_r):
    if scale <= 0.05:
        return closed.copy()
    if scale >= 0.97:
        return open_img.copy()
    out = closed.copy()
    r = max(2.0, max_r * scale)
    mask = Image.new('L', closed.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(radius=1.2))
    out.paste(open_img, (0, 0), mask)
    return out


def save_gif(frames, path):
    frames[0].save(
        path,
        save_all=True,
        append_images=frames[1:],
        duration=DURATION_MS,
        loop=0,
        disposal=2,
        optimize=False,
    )


def main():
    for pet in PETS:
        for gif_path in sorted((ROOT / pet).glob('*.gif')):
            frames = load_all(gif_path)
            closed, open_img = pick_closed_open(frames)
            cx, cy, max_r = mouth_diff_info(closed, open_img)
            new_frames = [make_frame(closed, open_img, s, cx, cy, max_r) for s in SCALES]
            save_gif(new_frames, gif_path)
            print(f'wrote {gif_path.relative_to(ROOT)} ({Image.open(gif_path).n_frames} frames)')


if __name__ == '__main__':
    main()
