#!/usr/bin/env python
"""Extract a frame from the banner animation MP4 for use as the Open Graph preview image."""

from pathlib import Path

import imageio.v3 as iio

REPO_ROOT = Path(__file__).resolve().parent.parent
MP4_PATH = REPO_ROOT / "post" / "figures" / "banner_drc_animation.mp4"
OUT_PATH = REPO_ROOT / "post" / "assets" / "og-preview.png"


def main():
    frames = iio.imread(MP4_PATH, plugin="pyav")
    print(f"Total frames: {len(frames)}, shape: {frames[0].shape}")

    # Use the last frame (all curves fully drawn)
    frame = frames[-1]

    iio.imwrite(OUT_PATH, frame)
    print(f"Saved {OUT_PATH} ({OUT_PATH.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
