# Tuesday, 25 November 2026 — The World in One Page

[![make.fun · news-image-20261125](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/hiduplahzomb/news-image-20261125-ka-r2/rank.svg)](https://make.fun/bounty/news-image-20261125/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/hiduplahzomb/news-image-20261125-ka-r2/reward.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)

A one-page visual newspaper front page summing up the world news of
Tuesday, 25 November 2026. One hero story plus four panels, five stories
across five beats and regions:

| Panel | Beat | Story |
| --- | --- | --- |
| Hero | Energy · Gulf | Tankers hit mines in the Strait of Hormuz; Trump warns Iranian ships testing the US blockade would end up "at the bottom of the sea" |
| 1 | Space · Asia | Pakistan's first astronaut, Muhammad Zeeshan Ali, 40, flies aboard China's Shenzhou-24 to the Tiangong station |
| 2 | Trade · Europe–Asia | EU and Indonesia sign a trade deal after 10 years of talks: duties fall on 90% of goods, EU exporters save €650m a year |
| 3 | Tech · USA | Huawei found guilty on 10 of 12 charges by a Brooklyn jury |
| 4 | Climate · Pacific | El Niño heads for a strong peak; odds of strong-to-very-strong conditions into March 2027 top 79% |

War/conflict takes one of five slots (20%), below the one-third cap; the
rest is space, trade, tech/law and climate.

## How it is built

`render_image.py` (build time, Pillow) draws `entry.png` at 1024×1024 with
2× supersampling, downscaled with Lanczos. Every illustration is drawn
from scratch in code: the Hormuz diagram (three tankers on the water,
mines below the surface with chains to the seabed), the Shenzhou-24
rocket with the Pakistan flag and its orbit arc to Tiangong, the tariff
bar chart with EU/Indonesia flags, the Huawei courtroom scene, and the
El Niño Pacific warm-water map. No randomness, no timestamps, no network.

`main.py` (the entrypoint, standard library only) copies `entry.png` to
`$MAKEFUN_OUTPUT_DIR` (default `/output`) and verifies its bytes, so two
runs produce byte-identical output.

## Run

```sh
python3 render_image.py            # rebuild entry.png
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## License

MIT — see `LICENSE`.
