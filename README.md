# scrapwood-tetris

**Experimental local MVP.** Defect-aware scrapwood packing contest: human / solver / agent compete on **waste%** when knots and cracks are hard constraints.

Independent personal remix — **not** an official SCI-Arc publication. Synthetic boards only.

**Source-page authors** (SCI-Arc Research “Construction Innovation: AI and Robotic Fabrication”): Casey Rehm, Masha Hupalo, Carolina Silva Garcia, Julia Pike. **takeru_role:** `unknown` (not sole authorship of the source research).

See [ATTRIBUTION.md](./ATTRIBUTION.md), [PROVENANCE.md](./PROVENANCE.md), [CITATION.cff](./CITATION.cff).

## Core promise

```text
knotty synthetic board  →  illegal if placement ∩ defect
human / solver / agent  →  same scorer  →  waste% leaderboard
```

**10s demo line:** 節だらけ合成板で人間 vs solver vs agent の waste% がライブ更新。

## One-command run

```bash
cd projects/sciarc-remix-swarm/worktrees/scrapwood-tetris
chmod +x scripts/run.sh scripts/ci-local.sh
./scripts/run.sh
```

Or manually:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
pytest -q
python -m scrapwood demo --ascii --env-steps 3
```

## Quick CLI

```bash
# Contest demo (solver + agent + human script)
python -m scrapwood demo --ascii

# Freeze check vs golden solver waste%
python -m scrapwood check-baseline

# Dump solver placements JSON
python -m scrapwood dump-solver
```

## Layout

| Path | Role |
|---|---|
| `fixtures/boards/knotty_board.json` | Synthetic board + knot/crack polygons |
| `fixtures/parts/catalog.json` | Oversized synthetic part set |
| `fixtures/parts/human_script.json` | Curated human placements (+ illegal knot hit) |
| `baselines/seeded_waste.json` | Contest-freeze golden waste% |
| `src/scrapwood/` | geometry, constraints, placer, scoring, env, contest, CLI |
| `tests/` | unit + contest freeze + Hypothesis property tests |

## Scoring

```text
usable_area = board_area - defect_aabb_area
waste%      = 100 * (usable_area - placed_area) / usable_area
```

Lower waste% wins. Defect overlap → placement rejected (not scored).

## Gym-shaped API

```python
from scrapwood.env import make_env
from scrapwood.load import load_contest_fixture
from scrapwood.models import Placement

board, catalog = load_contest_fixture()
env = make_env(board, catalog)
obs = env.reset(seed=42)
obs, reward, done, info = env.step(Placement("O", 0, 0, 0))
print(env.score().waste_pct)
```

## Limitations / non-goals / experimental

**This is experimental software.**

### Non-goals

- Not mill-grade CAM, CNC post, or kerf-accurate cut planning
- Not a full SVGNest / libnest2d / NFP+GA nesting engine
- Not a physics / robot fabrication demo video product
- Not a claim of SCI-Arc CLT research efficiency percentages
- No GitHub publish / deploy / PR from this worktree by default

### Limitations

- Axis-aligned rectangles; defect polygons use AABB hard constraints
- Thin deterministic bottom-left placer (not optimal packing)
- Solver baseline disables rotation; human/agent may rotate
- Agent is a heuristic stub, not a trained policy
- Synthetic fixtures only — no partner mill scans

### Kill conditions (do not ship as)

- Defect-free puzzle toy
- Physics demo video only
- SVGNest skin with no defect kernel

### Third-party

MVP uses **synthetic** boards/parts only. No fabrication-gallery re-exhibition. SVGNest/rectpack are conceptual prior art — code not vendored. See swarm `registry/third_party_risks.yaml` and [ATTRIBUTION.md](./ATTRIBUTION.md).

## License

MIT — see [LICENSE](./LICENSE).
