#!/usr/bin/env python
"""Generate optimised web images (WebP + JPEG) at 400/800/1600 widths from
originals in images/originals/. Never upscales past a photo's native width.

Run:  py build_images.py
Add a new photo: drop it in images/originals/, add a (slug, filename) line to
GALLERY below (with alt text in the site's HTML), then re-run this script.
"""
import os
from PIL import Image, ImageOps

SRC = os.path.join("images", "originals")
OUT = "images"
WIDTHS = [400, 800, 1600]
JPEG_Q = 82
WEBP_Q = 80

# slug -> original filename. Curated: finished thatch work + before/after +
# a few build-process shots. Tile-roof and phone-watermarked shots excluded.
IMAGES = {
    # hero
    "hero-house-pool":   "WhatsApp Image 2026-07-17 at 17.06.12.jpeg",
    # team
    "team":              "WhatsApp Image 2026-07-17 at 17.06.04 (1).jpeg",
    # gallery
    "lapa-after":        "WhatsApp Image 2026-07-17 at 17.06.05 (2).jpeg",
    "gazebo-after":      "WhatsApp Image 2026-07-17 at 17.06.05.jpeg",
    "lapa-before":       "WhatsApp Image 2026-07-17 at 17.06.02.jpeg",
    "braai-before":      "WhatsApp Image 2026-07-17 at 17.06.07.jpeg",
    "house-dawn":        "WhatsApp Image 2026-07-17 at 17.06.00 (1).jpeg",
    "large-lapa":        "WhatsApp Image 2026-07-17 at 17.06.06 (1).jpeg",
    "rondavel-dusk":     "WhatsApp Image 2026-07-17 at 17.06.02 (1).jpeg",
    "rounded-lapa":      "WhatsApp Image 2026-07-17 at 17.06.03.jpeg",
    "house-palm":        "WhatsApp Image 2026-07-17 at 17.06.11 (1).jpeg",
    "house-pool-2":      "WhatsApp Image 2026-07-17 at 17.06.11.jpeg",
    "house-yellow":      "WhatsApp Image 2026-07-17 at 17.06.00.jpeg",
    "chimney-detail":    "WhatsApp Image 2026-07-17 at 17.06.10.jpeg",
    "house-grand":       "WhatsApp Image 2026-07-17 at 17.06.04.jpeg",
    # process / build-in-progress
    "workers-thatching": "WhatsApp Image 2026-07-17 at 17.06.01 (1).jpeg",
    "roof-structure":    "WhatsApp Image 2026-07-17 at 17.06.01.jpeg",
    "roof-frame":        "WhatsApp Image 2026-07-17 at 17.06.09 (1).jpeg",
}


def main():
    os.makedirs(OUT, exist_ok=True)
    for slug, fname in IMAGES.items():
        path = os.path.join(SRC, fname)
        if not os.path.exists(path):
            print(f"  MISSING {fname}")
            continue
        im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
        native = im.width
        targets = sorted({w for w in WIDTHS if w <= native} | {min(native, max(WIDTHS))})
        for w in targets:
            if w >= native:
                r = im.copy()
                w = native
            else:
                h = round(im.height * w / native)
                r = im.resize((w, h), Image.LANCZOS)
            r.save(os.path.join(OUT, f"{slug}-{w}.webp"), "WEBP", quality=WEBP_Q, method=6)
            r.save(os.path.join(OUT, f"{slug}-{w}.jpg"), "JPEG", quality=JPEG_Q,
                   optimize=True, progressive=True)
        print(f"  {slug:18s} native={native}w  -> {sorted(set(targets))}")
    print("done")


if __name__ == "__main__":
    main()
