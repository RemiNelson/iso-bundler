"""Generates a cute CD-disc icon for the app bundle (packaging/icon.icns).

Not a runtime dependency of the app -- only needed to regenerate the icon.
Requires Pillow (`pip install pillow`) and macOS's `iconutil`.

Usage: python packaging/make_icon.py
"""

import math
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw

SIZE = 1024
OUT_DIR = Path(__file__).parent
ICONSET_DIR = OUT_DIR / "icon.iconset"
ICNS_PATH = OUT_DIR / "icon.icns"

# macOS iconset requires exactly these files.
ICONSET_SIZES = [
    ("icon_16x16.png", 16),
    ("icon_16x16@2x.png", 32),
    ("icon_32x32.png", 32),
    ("icon_32x32@2x.png", 64),
    ("icon_128x128.png", 128),
    ("icon_128x128@2x.png", 256),
    ("icon_256x256.png", 256),
    ("icon_256x256@2x.png", 512),
    ("icon_512x512.png", 512),
    ("icon_512x512@2x.png", 1024),
]


def draw_icon(size):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    center = size / 2
    disc_radius = size * 0.42

    def bbox(radius):
        return (center - radius, center - radius, center + radius, center + radius)

    # Soft drop shadow.
    shadow_offset = size * 0.015
    draw.ellipse(
        [c + shadow_offset for c in bbox(disc_radius)],
        fill=(0, 0, 0, 60),
    )

    # Disc body: silver gradient via concentric rings, light at the edge,
    # slightly darker toward the center.
    rings = 60
    for i in range(rings, 0, -1):
        t = i / rings
        r = disc_radius * t
        shade = int(214 + 30 * (1 - t))
        draw.ellipse(bbox(r), fill=(shade, shade, shade + 6, 255))

    # Rainbow reflection arc across the upper-left of the disc.
    rainbow = [
        (255, 99, 132),
        (255, 178, 102),
        (255, 245, 130),
        (140, 230, 160),
        (120, 190, 255),
        (180, 140, 255),
    ]
    band_outer = disc_radius * 0.98
    band_inner = disc_radius * 0.55
    n = len(rainbow)
    start_angle, end_angle = 200, 340
    step = (end_angle - start_angle) / n
    for i, color in enumerate(rainbow):
        a0 = start_angle + i * step
        a1 = a0 + step + 0.5
        draw.pieslice(bbox(band_outer), a0, a1, fill=color + (150,))
    # Punch the inner radius back out to transparent-over-disc (redraw disc
    # shade underneath the band's inner edge for a crescent look).
    inner_shade = 232
    draw.ellipse(bbox(band_inner), fill=(inner_shade, inner_shade, 238, 255))

    # Center hole.
    hole_r = disc_radius * 0.16
    draw.ellipse(bbox(hole_r + size * 0.01), fill=(150, 150, 158, 255))
    draw.ellipse(bbox(hole_r), fill=(20, 20, 24, 255))

    # Cute face, sitting on the lower half of the disc.
    eye_y = center + disc_radius * 0.32
    eye_dx = disc_radius * 0.24
    eye_r = disc_radius * 0.07
    for dx in (-eye_dx, eye_dx):
        ex, ey = center + dx, eye_y
        draw.ellipse([ex - eye_r, ey - eye_r, ex + eye_r, ey + eye_r], fill=(40, 40, 45, 255))
        hl_r = eye_r * 0.35
        draw.ellipse(
            [ex - hl_r * 1.6, ey - hl_r * 2.2, ex + hl_r * 0.4, ey - hl_r * 0.2],
            fill=(255, 255, 255, 230),
        )

    # Blush.
    blush_r = disc_radius * 0.09
    blush_y = eye_y + disc_radius * 0.16
    for dx in (-eye_dx * 1.55, eye_dx * 1.55):
        bx = center + dx
        draw.ellipse(
            [bx - blush_r, blush_y - blush_r * 0.6, bx + blush_r, blush_y + blush_r * 0.6],
            fill=(255, 140, 150, 110),
        )

    # Smile.
    smile_r = disc_radius * 0.22
    smile_y = eye_y + disc_radius * 0.05
    draw.arc(
        [center - smile_r, smile_y - smile_r, center + smile_r, smile_y + smile_r],
        start=20,
        end=160,
        fill=(60, 45, 50, 255),
        width=max(2, int(size * 0.012)),
    )

    # Thin outline around the whole disc.
    draw.ellipse(bbox(disc_radius), outline=(120, 120, 130, 200), width=max(1, int(size * 0.004)))

    return img


def main():
    master = draw_icon(SIZE)

    if ICONSET_DIR.exists():
        shutil.rmtree(ICONSET_DIR)
    ICONSET_DIR.mkdir()

    for filename, px in ICONSET_SIZES:
        resized = master.resize((px, px), Image.LANCZOS)
        resized.save(ICONSET_DIR / filename)

    subprocess.run(
        ["iconutil", "-c", "icns", str(ICONSET_DIR), "-o", str(ICNS_PATH)],
        check=True,
    )
    shutil.rmtree(ICONSET_DIR)
    print(f"Wrote {ICNS_PATH}")


if __name__ == "__main__":
    main()
