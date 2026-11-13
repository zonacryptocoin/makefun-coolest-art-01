"""make.fun bounty coolest-art-01: draw one cool image, deterministically.

Spec: Python 3.13, stdlib only, no network. Writes one PNG to
/output/entry.png, <=1 MiB, <=1024x1024 px. Run twice, same bytes.
Local test: ENTRY_OUTPUT env overrides the output path.

Art: a Mandelbrot set zoomed into the seahorse valley, smooth-colored
in a deep-space neon palette, with a gentle vignette. Pure stdlib PNG
encoder (zlib + CRC32), no image libraries.
"""
import binascii
import math
import os
import struct
import zlib

W, H = 1024, 1024
MAX_ITER = 200
# Seahorse valley: a classic detailed zoom of the Mandelbrot set.
CX, CY = -0.743643887037151, 0.131825904205330
SCALE = 0.0016  # half-width of the view, in complex-plane units
OUT = os.environ.get("ENTRY_OUTPUT", "/output/entry.png")

PALETTE_STOPS = [
    (0.00, (4, 2, 16)),
    (0.15, (24, 8, 64)),
    (0.35, (72, 16, 120)),
    (0.55, (150, 30, 110)),
    (0.75, (235, 90, 40)),
    (0.90, (255, 190, 90)),
    (1.00, (255, 240, 180)),
]

INSIDE = (3, 3, 14)  # points inside the set: near-black navy


def _palette(t):
    for i in range(len(PALETTE_STOPS) - 1):
        t0, c0 = PALETTE_STOPS[i]
        t1, c1 = PALETTE_STOPS[i + 1]
        if t0 <= t <= t1:
            f = 0.0 if t1 == t0 else (t - t0) / (t1 - t0)
            return (int(c0[0] + (c1[0] - c0[0]) * f),
                    int(c0[1] + (c1[1] - c0[1]) * f),
                    int(c0[2] + (c1[2] - c0[2]) * f))
    return PALETTE_STOPS[-1][1]


# 256-entry lookup table: smooth color per iteration band.
LUT = [bytes(_palette(i / 255.0)) for i in range(256)]
INSIDE_B = bytes(INSIDE)


def render():
    step = 2.0 * SCALE / W
    # Separable vignette factors, precomputed per row/column.
    fx = [1.0 - 0.25 * ((px - W / 2) / (W / 2)) ** 2 for px in range(W)]
    fy = [1.0 - 0.25 * ((py - H / 2) / (H / 2)) ** 2 for py in range(H)]
    rows = []
    max_iter = MAX_ITER
    for py in range(H):
        ci = CY + (py - H / 2) * step
        vy = fy[py]
        row = bytearray(b"\x00")  # PNG filter: none
        for px in range(W):
            cr = CX + (px - W / 2) * step
            zr = zi = 0.0
            n = 0
            while n < max_iter:
                zr2 = zr * zr
                zi2 = zi * zi
                if zr2 + zi2 > 4.0:
                    break
                zi = 2.0 * zr * zi + ci
                zr = zr2 - zi2 + cr
                n += 1
            if n == max_iter:
                row += INSIDE_B
            else:
                mod2 = zr * zr + zi * zi
                mu = n + 1.0 - math.log2(math.log2(mod2))
                idx = int(mu / max_iter * 255.0)
                if idx > 255:
                    idx = 255
                elif idx < 0:
                    idx = 0
                r, g, b = LUT[idx]
                v = fx[px] * vy
                row += bytes((int(r * v), int(g * v), int(b * v)))
        rows.append(bytes(row))
    return rows


def _chunk(typ, data):
    c = struct.pack(">I", len(data)) + typ + data
    return c + struct.pack(">I", binascii.crc32(typ + data) & 0xFFFFFFFF)


def write_png(path, rows, w, h):
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    idat = zlib.compress(b"".join(rows), 9)
    png = (b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr)
           + _chunk(b"IDAT", idat) + _chunk(b"IEND", b""))
    out_dir = os.path.dirname(path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(path, "wb") as f:
        f.write(png)


def main():
    write_png(OUT, render(), W, H)


if __name__ == "__main__":
    main()
