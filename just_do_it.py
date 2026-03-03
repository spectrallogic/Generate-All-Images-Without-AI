#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║          EVERY POSSIBLE IMAGE GENERATOR™                     ║
║   "Your next masterpiece is already in my output folder."    ║
╚══════════════════════════════════════════════════════════════╝

Generates every possible image that can exist within a given
resolution and color palette. A mathematical proof that the
artist vs. AI debate is missing the point — the output space
was always finite, and every image was always in it.
"""

import os
import sys
import shutil
import itertools
import math
import time
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("Pillow is required. Install it with:")
    print("  pip install Pillow")
    sys.exit(1)


def format_number(n):
    """Make enormous numbers human-readable."""
    if n < 10_000:
        return f"{n:,}"

    suffixes = [
        (10 ** 303, "centillion"), (10 ** 100, "googol"),
        (10 ** 63, "vigintillion"), (10 ** 33, "decillion"),
        (10 ** 30, "nonillion"), (10 ** 27, "octillion"),
        (10 ** 24, "septillion"), (10 ** 21, "sextillion"),
        (10 ** 18, "quintillion"), (10 ** 15, "quadrillion"),
        (10 ** 12, "trillion"), (10 ** 9, "billion"),
        (10 ** 6, "million"), (10 ** 3, "thousand"),
    ]
    for threshold, name in suffixes:
        if n >= threshold:
            value = n / threshold
            return f"~{value:.2f} {name} ({n:.2e})"
    return f"{n:,}"


def fun_comparisons(n):
    """Put absurd numbers in perspective."""
    comparisons = []
    if n > 7.5e18:
        comparisons.append(f"  🌍 Grains of sand on Earth:        ~7.5 × 10¹⁸")
    if n > 10 ** 80:
        comparisons.append(f"  ⚛️  Atoms in observable universe:   ~10⁸⁰")
    if n > 200e9:
        comparisons.append(f"  ⭐ Stars in the Milky Way:          ~200 billion")
    if n > 8e9:
        comparisons.append(f"  👤 Humans alive right now:          ~8 billion")
    if n > 31_536_000:
        comparisons.append(f"  ⏱️  Seconds in a year:              ~31.5 million")

    if comparisons:
        print("\n  Your image count DWARFS:")
        for c in comparisons:
            print(c)


def get_user_input():
    """Gather all parameters from the user."""
    print("\n" + "=" * 60)
    print("  🎨  EVERY POSSIBLE IMAGE GENERATOR")
    print("  Generating literally every image that can exist.")
    print("=" * 60)

    # --- Color Mode ---
    print("\n📺 IMAGE MODE")
    print("  1) Black & White (grayscale shades)")
    print("  2) Full Color (RGB)")
    while True:
        choice = input("\n  Choose mode [1/2]: ").strip()
        if choice in ("1", "2"):
            mode = "bw" if choice == "1" else "color"
            break
        print("  Please enter 1 or 2.")

    # --- Number of Colors ---
    if mode == "bw":
        max_colors = 256
        print(f"\n🎨 NUMBER OF SHADES (grayscale)")
        print(f"  Range: 2 (pure black & white) to {max_colors} (full 8-bit grayscale)")
        print(f"  Examples:")
        print(f"    2  = just black and white")
        print(f"    4  = black, dark gray, light gray, white")
        print(f"    16 = nice gradient of grays")
        print(f"    256 = full grayscale spectrum")
    else:
        print(f"\n🎨 NUMBER OF VALUES PER COLOR CHANNEL (R, G, B)")
        print(f"  Range: 2 to 256 values per channel")
        print(f"  Examples:")
        print(f"    2  = each channel is 0 or 255 → 2³ = 8 total colors")
        print(f"    4  = 4 levels per channel    → 4³ = 64 total colors")
        print(f"    6  = 6 levels per channel    → 6³ = 216 total colors (web-safe)")
        print(f"    16 = 16 levels per channel   → 16³ = 4,096 total colors")
        print(f"    256 = full 24-bit color      → 16.7 million total colors")
        max_colors = 256

    while True:
        try:
            num_colors = int(input(
                f"\n  Enter number {'of shades' if mode == 'bw' else 'of values per channel'} [2-{max_colors}]: "))
            if 2 <= num_colors <= max_colors:
                break
            print(f"  Please enter a number between 2 and {max_colors}.")
        except ValueError:
            print("  Please enter a valid number.")

    if mode == "color":
        total_colors = num_colors ** 3
        print(f"  → {num_colors}³ = {total_colors:,} total unique colors")
    else:
        total_colors = num_colors
        print(f"  → {total_colors} unique shades of gray")

    # --- Resolution ---
    print(f"\n📐 IMAGE RESOLUTION")
    print(f"  Keep it TINY unless you want to wait until the heat death of the universe.")
    print(f"  Recommended: 1×1 to 4×4 (with few colors)")
    print(f"  Maximum allowed: 8×8 (but you've been warned)")

    while True:
        try:
            width = int(input("\n  Width in pixels  [1-8]: "))
            height = int(input("  Height in pixels [1-8]: "))
            if 1 <= width <= 8 and 1 <= height <= 8:
                break
            print("  Please keep dimensions between 1 and 8.")
        except ValueError:
            print("  Please enter valid numbers.")

    return mode, num_colors, total_colors, width, height


def preview_generation(mode, num_colors, total_colors, width, height):
    """Show the user what they're about to unleash."""
    num_pixels = width * height
    colors_per_pixel = total_colors
    total_images = colors_per_pixel ** num_pixels

    print("\n" + "=" * 60)
    print("  📊  GENERATION PREVIEW")
    print("=" * 60)
    print(f"  Resolution:        {width}×{height} = {num_pixels} pixels")
    print(f"  Colors per pixel:  {total_colors:,}")
    print(f"  Total images:      {total_colors}^{num_pixels} = {format_number(total_images)}")

    fun_comparisons(total_images)

    # Time estimate (assume ~5000 images/sec for small images)
    rate = 5000
    seconds = total_images / rate
    if seconds < 60:
        time_str = f"{seconds:.1f} seconds"
    elif seconds < 3600:
        time_str = f"{seconds / 60:.1f} minutes"
    elif seconds < 86400:
        time_str = f"{seconds / 3600:.1f} hours"
    elif seconds < 31536000:
        time_str = f"{seconds / 86400:.1f} days"
    elif seconds < 31536000 * 1000:
        time_str = f"{seconds / 31536000:.1f} years"
    else:
        time_str = f"{seconds / 31536000:.2e} years (age of universe: ~1.38 × 10¹⁰ years)"

    print(f"\n  ⏱️  Estimated time:   {time_str} (at ~{rate:,} images/sec)")

    # Check available disk space
    output_dir = Path("generated_images")
    output_dir.mkdir(exist_ok=True)
    disk_usage = shutil.disk_usage(output_dir.resolve())
    available_bytes = disk_usage.free

    # Estimate bytes per image (rough PNG estimate for tiny images)
    bytes_per_pixel = 3 if mode == "color" else 1
    raw_size = width * height * bytes_per_pixel
    est_per_image = max(raw_size + 100, 150)  # PNG overhead
    needed_bytes = total_images * est_per_image

    # Format storage sizes nicely
    def fmt_bytes(b):
        for name, div in [("YB", 1024 ** 8), ("ZB", 1024 ** 7), ("EB", 1024 ** 6),
                          ("PB", 1024 ** 5), ("TB", 1024 ** 4), ("GB", 1024 ** 3),
                          ("MB", 1024 ** 2), ("KB", 1024)]:
            if b >= div:
                return f"{b / div:.2f} {name}"
        return f"{b} bytes"

    print(f"\n  💾  DISK SPACE CHECK")
    print(f"     Available on disk:    {fmt_bytes(available_bytes)}")
    print(f"     Estimated needed:     {fmt_bytes(needed_bytes)}")
    print(f"     (at ~{est_per_image} bytes per image)")

    if needed_bytes > available_bytes:
        shortfall = needed_bytes - available_bytes
        max_possible = available_bytes // est_per_image
        pct_of_total = (max_possible / total_images) * 100 if total_images > 0 else 0

        print(f"\n  🚫 NOT ENOUGH DISK SPACE!")
        print(f"     You're short by:      {fmt_bytes(shortfall)}")
        print(f"     You could fit:        {max_possible:,} images ({pct_of_total:.6f}% of total)")
        print(f"     You would need:       {fmt_bytes(needed_bytes)} of free space")

        if needed_bytes > 1024 ** 5:  # Petabyte+
            print(f"\n     📦 For perspective, you'd need roughly:")
            if needed_bytes > 1024 ** 8:
                print(f"        {needed_bytes / 1024 ** 8:.2e} yottabytes — this exceeds all")
                print(f"        data storage ever manufactured by humanity. Combined. Many times over.")
            elif needed_bytes > 1024 ** 7:
                print(f"        {needed_bytes / 1024 ** 7:.2e} zettabytes — all data on Earth is ~120 ZB.")
            elif needed_bytes > 1024 ** 6:
                print(f"        {needed_bytes / 1024 ** 6:.2e} exabytes — that's entire-internet territory.")
            elif needed_bytes > 1024 ** 5:
                print(f"        {needed_bytes / 1024 ** 5:.2e} petabytes — a few large data centers worth.")

        print(f"\n     But hey — you've already proven the point! 😄")
        print(f"     Even at this tiny resolution, every possible image won't")
        print(f"     fit on your hard drive. And people are arguing about who")
        print(f"     'owns' individual pixel arrangements from this space...")
        return total_images, False

    # It fits, but warn if it's a lot
    if needed_bytes > available_bytes * 0.5:
        print(f"\n  ⚠️  WARNING: This will use over 50% of your remaining disk space!")
    elif needed_bytes > available_bytes * 0.1:
        print(f"\n  ⚠️  Heads up: This will use a noticeable chunk of disk space.")

    return total_images, True


def generate_palette(mode, num_colors):
    """Generate the color palette."""
    if mode == "bw":
        # Evenly spaced grayscale values
        if num_colors == 2:
            values = [0, 255]
        else:
            values = [round(i * 255 / (num_colors - 1)) for i in range(num_colors)]
        # Each "color" is a single grayscale value
        return values, "L"
    else:
        # RGB: generate all combinations of channel values
        if num_colors == 2:
            channel_values = [0, 255]
        else:
            channel_values = [round(i * 255 / (num_colors - 1)) for i in range(num_colors)]
        # All RGB combinations
        colors = list(itertools.product(channel_values, repeat=3))
        return colors, "RGB"


def generate_images(mode, num_colors, total_colors, width, height, total_images):
    """Generate all possible images."""
    output_dir = Path("generated_images")
    output_dir.mkdir(exist_ok=True)

    palette, pil_mode = generate_palette(mode, num_colors)
    num_pixels = width * height

    print(f"\n  🚀 Generating {format_number(total_images)} images into '{output_dir}/'...")
    print(
        f"     Palette: {len(palette) if mode == 'bw' else len(palette)} unique {'shades' if mode == 'bw' else 'colors'}")
    print()

    start_time = time.time()
    count = 0
    report_interval = max(1, min(total_images // 20, 50000))

    # Generate every combination of colors for every pixel
    for combo in itertools.product(range(len(palette)), repeat=num_pixels):
        img = Image.new(pil_mode, (width, height))
        pixels = img.load()

        for idx, color_idx in enumerate(combo):
            x = idx % width
            y = idx // width
            pixels[x, y] = palette[color_idx]

        # Save with a numbered filename
        img.save(output_dir / f"img_{count:08d}.png")
        count += 1

        if count % report_interval == 0:
            elapsed = time.time() - start_time
            rate = count / elapsed if elapsed > 0 else 0
            pct = (count / total_images) * 100
            remaining = (total_images - count) / rate if rate > 0 else 0
            print(f"     [{pct:5.1f}%] {count:,} / {total_images:,} images "
                  f"| {rate:.0f} img/sec | ~{remaining:.0f}s remaining")

    elapsed = time.time() - start_time
    print(f"\n  ✅ DONE! Generated {count:,} images in {elapsed:.1f} seconds")
    print(f"     Output directory: {output_dir.resolve()}")
    print(f"     Average rate: {count / elapsed:.0f} images/second")

    return count


def print_copyright_rant(total_images):
    """The whole point of this project."""
    print("\n" + "=" * 60)
    print("  ⚖️  SO... ABOUT THAT CREATIVITY DEBATE")
    print("=" * 60)
    print(f"""
  You just explored a space of {format_number(total_images)} images.

  Among them — in tiny, pixelated form — is every painting 
  that will ever be painted. Every AI-generated image that 
  Midjourney, DALL-E, and Stable Diffusion will ever produce.
  Every photograph that hasn't been taken yet. Every album 
  cover for songs that don't exist. All of them. Generated 
  by a for loop.

  Traditional artists act like creativity is sacred — like 
  they're pulling images from some mystical dimension that 
  only humans can access. But they're not. They're picking 
  one pixel arrangement from a finite set of possibilities. 
  A breathtakingly large set, but a set with hard edges.

  AI artists aren't doing anything different. Same pool of 
  possible images. Different method of picking one. Statistics 
  instead of a brush. The output space doesn't care HOW you 
  arrived at a particular arrangement of pixels.

  And yet people are at war over who "really" creates art.

  This script proves the whole argument is about process, 
  not output. The outputs were always there — every single 
  one of them — locked inside the math, waiting for someone 
  (or something) to stumble onto them.

  Nobody invents an image. You just find one that was always 
  possible.

  So maybe we can stop fighting about it.

  ─────────────────────────────────────────────────────
  "Creativity is not generating something from nothing.
   It's choosing one possibility from a space that 
   already contains everything."
  ─────────────────────────────────────────────────────
  """)


def main():
    mode, num_colors, total_colors, width, height = get_user_input()
    total_images, can_generate = preview_generation(mode, num_colors, total_colors, width, height)

    if not can_generate:
        print_copyright_rant(total_images)
        return

    print("\n" + "-" * 60)
    confirm = input("  Proceed with generation? [y/N]: ").strip().lower()
    if confirm not in ("y", "yes"):
        print("\n  Generation cancelled. Smart choice, probably. 😄")
        print_copyright_rant(total_images)
        return

    count = generate_images(mode, num_colors, total_colors, width, height, total_images)
    print_copyright_rant(count)


if __name__ == "__main__":
    main()