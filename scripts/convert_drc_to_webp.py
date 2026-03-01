"""Convert DRC plot PNGs to WebP format.

Usage:
    python scripts/convert_drc_to_webp.py [--quality 80] [--src data/inhibition_drc-plots] [--dst data/inhibition_drc-plots-webp]
"""

import argparse
from pathlib import Path
from PIL import Image


def main():
    parser = argparse.ArgumentParser(description="Convert DRC plot PNGs to WebP")
    parser.add_argument("--quality", type=int, default=80)
    parser.add_argument("--src", type=Path, default=Path("data/inhibition_drc-plots"))
    parser.add_argument("--dst", type=Path, default=Path("data/inhibition_drc-plots-webp"))
    args = parser.parse_args()

    args.dst.mkdir(parents=True, exist_ok=True)
    pngs = sorted(args.src.glob("*.png"))
    print(f"Converting {len(pngs)} PNGs to WebP (quality={args.quality})")

    for p in pngs:
        img = Image.open(p)
        img.save(args.dst / (p.stem + ".webp"), format="webp", quality=args.quality)

    total_png = sum(p.stat().st_size for p in pngs)
    webps = list(args.dst.glob("*.webp"))
    total_webp = sum(p.stat().st_size for p in webps)
    print(f"Done: {len(webps)} files")
    print(f"PNG:  {total_png / 1e6:.1f} MB")
    print(f"WebP: {total_webp / 1e6:.1f} MB")
    print(f"Saved: {(total_png - total_webp) / 1e6:.1f} MB ({(1 - total_webp / total_png) * 100:.0f}%)")


if __name__ == "__main__":
    main()
