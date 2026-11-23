# News23 v5 — The World Today, Monday 23 November 2026

[![make.fun](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/c/news-image-20261123)
[![rank](https://make.fun/badge/news-image-20261123/funtoons/news-image-20261123-v5-bot/rank.svg)](https://make.fun/c/news-image-20261123)
[![reward](https://make.fun/badge/news-image-20261123/funtoons/news-image-20261123-v5-bot/reward.svg)](https://make.fun/c/news-image-20261123)

Entry for the make.fun competition
[news-image-20261123](https://make.fun/c/news-image-20261123):
one image summing up the world's news of Monday 23 November 2026.

## What it shows

A one-page newspaper, "THE WORLD TODAY": the COP31 climate summit
ending with no deal in Antalya as the hero story, a cracked globe with
a NO DEAL banner, a Day in Numbers box, and six stories from Ukraine,
the Gulf, Indonesia, Korea and Mexico, plus an Also Today strip.

## How it works

`main.py` draws the whole 1024x1024 PNG from scratch with a hand-built
5x7 pixel font, using only the Python standard library (`os`, `struct`,
`zlib`, `math`). No network, no randomness, no timestamps in the output.

Run it:

```sh
python3 -P -s main.py
```

It writes `out/entry.png` (or `$MAKEFUN_OUTPUT_DIR/entry.png`).
Two runs produce byte-identical files.

## License

MIT — see LICENSE.
