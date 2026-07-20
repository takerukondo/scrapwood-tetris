# PROVENANCE — scrapwood-tetris

**Artifact ID:** `scrapwood-tetris`  
**As of:** 2026-07-20  
**Lane:** Build Pod (local MVP)  
**State note:** Swarm control plane may still show `APPROVED_TO_BUILD: 0` / pending Human Plan Review; this worktree is an experimental local implementation under the remix card’s BUILD prior-art gate.

## One-sentence promise

On a knotty **synthetic** board, placements that intersect defects are illegal; human / solver / agent compete on live **waste%** under one scorer.

## Mechanism lineage

| Layer | ID / title | Role |
|---|---|---|
| Source | `construction-innovation-ai-and-robotic-fabrication` | Heterogeneous / lower-grade timber as constraint; waste reduction framing |
| Mechanism | `mech-heterogeneous-material-as-constraint` | Treat material defects/grade as hard optimization constraints |
| Mechanism | `mech-waste-to-resource-allocation` | Allocate around weakness to reduce waste |
| Mechanism | `mech-nn-layup-to-robotics` | Deferred — not implemented (no NN / robot demo) |
| Remix | `scrapwood-tetris` | Defect-aware packing contest + gym-shaped API |

Prefer `source_backed_summary` on the source card over interpretation. This MVP does **not** reproduce research panel photos, Are.na progress assets, or claimed CLT efficiency percentages.

## Prior art (differentiation)

Closest nesting engines (overlap acknowledged; not vendored):

- [SVGNest](https://github.com/Jack000/SVGnest) — irregular bin packing (NFP + GA)
- [libnest2d](https://github.com/tamasmeszaros/libnest2d) — C++ nesting (PrusaSlicer lineage)
- Sheet / cut planners (SheetSmart, EZNESTING, OptiNest) — commercial nesting

**Differentiation shipped here:** defects/knots as first-class hard constraints + human/solver/agent contest harness + waste% leaderboard on synthetic boards. Thin deterministic BLF placer — not a novel nesting engine and not mill-grade CAM.

## Inputs / outputs of this MVP

- **In:** `fixtures/boards/*.json`, `fixtures/parts/*.json` (synthetic)
- **Out:** contest waste% leaderboard, gym-shaped `reset`/`step`/`score`, CLI demo
- **Not in:** partner mill scans, research efficiency %, fabrication gallery re-exhibition, SVGNest runtime wrapper

## Attribution

See [ATTRIBUTION.md](./ATTRIBUTION.md) and [CITATION.cff](./CITATION.cff).

- **Listed authors (source card):** Casey Rehm, Masha Hupalo, Carolina Silva Garcia, Julia Pike  
- **takeru_role:** unknown  
- **permission_status:** confirmed_by_takeru (audit trail only)  
- **Official SCI-Arc?** No

## Evidence paths (swarm)

- `projects/sciarc-remix-swarm/source-cards/construction-innovation-ai-and-robotic-fabrication.yaml`
- `projects/sciarc-remix-swarm/remix-cards/scrapwood-tetris.yaml`
- `projects/sciarc-remix-swarm/prior-art/scrapwood-tetris.yaml`
- `projects/sciarc-remix-swarm/taste/scrapwood-tetris.yaml`
- `projects/sciarc-remix-swarm/build-plans/scrapwood-tetris.md`
