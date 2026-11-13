# Coolest Art — make.fun bounty `coolest-art-01`

A tiny deterministic program that draws one cool image: a Mandelbrot
set zoomed into the seahorse valley, smooth-colored in a deep-space
neon palette, with a gentle vignette.

## Run it

Requires Python 3.13 (stdlib only, no network, no dependencies):

```sh
python3 main.py
```

It writes the image to `/output/entry.png` (override with the
`ENTRY_OUTPUT` environment variable). 1024x1024 PNG, about 600 KB.
Run it twice and the output is byte-identical (~13 s per run).

## Files

- `main.py` — the program (stdlib only; own PNG encoder via zlib)
- `LICENSE` — MIT
