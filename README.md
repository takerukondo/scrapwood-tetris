# scrapwood-tetris

A clean rectangle is easy. A board with knots and cracks is where the argument starts.

`scrapwood-tetris` is a small packing contest in which defects are hard constraints and every player is judged by the same waste calculation. The included match is intentionally uneven: a largest-first heuristic, a rotation-happy heuristic, and one hand-arranged layout compete on a synthetic 20×12 board.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"

scrapwood demo --ascii
```

The output includes a leaderboard, a rejected placement that lands on a knot, and the winning board:

```text
rank  player   waste%    util%   placed  rejected
1     human       4.02   95.98      12         1
2     solver      7.59   92.41      11         0
3     rotate     36.61   63.39      11         0
```

The “human” row is a curated placement script, not a user study. The heuristics are a deliberately weak pair, not AI agents. Their job is to make ordering and rotation choices inspectable under one scorer.

## Useful commands

```bash
scrapwood check-baseline   # detect scorer or fixture drift
scrapwood dump-solver      # placements and score as JSON
pytest -q
```

## Rules of this tiny board

- Parts are axis-aligned rectangles and may not overlap.
- Defects are polygons but use their bounding boxes for collision checks.
- Waste is unoccupied usable area; rejected pieces do not count.
- The catalog is oversized, so ordering changes the result.

The surprising result in the fixture—that the hand arrangement beats the largest-first heuristic—is not evidence that humans generally pack better. It is a prompt to implement a real search method and compare it without changing the rules.

## Research lineage

I worked as a research assistant at SCI-Arc Research from May 2024 to January 2025. This is an independent implementation inspired by [Construction Innovation: AI and Robotic Fabrication](http://research.sciarc.edu/projects/10-construction-innovation-ai-and-robotic-fabrication), credited to Casey Rehm, Masha Hupalo, Carolina Silva Garcia, and Julia Pike. No research imagery, structural data, mill scans, or robot instructions are included. See [ATTRIBUTION.md](ATTRIBUTION.md) and [PROVENANCE.md](PROVENANCE.md).

This is a packing experiment, not structural or fabrication advice.

MIT — see [LICENSE](LICENSE).
