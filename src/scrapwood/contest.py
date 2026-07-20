"""Human / solver / agent contest harness under one scorer."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence

from scrapwood.agent import rotation_heuristic_place, solver_place
from scrapwood.constraints import has_defect_constraints
from scrapwood.models import Board, PartSpec, Placement
from scrapwood.placer import place_sequence
from scrapwood.scoring import Score, score


@dataclass(frozen=True)
class ContestResult:
    player: str
    placements: List[Placement]
    rejected: List[tuple]
    score: Score

    def row(self) -> Dict:
        return {
            "player": self.player,
            "placed": self.score.placed_count,
            "waste_pct": self.score.waste_pct,
            "utilization_pct": self.score.utilization_pct,
            "rejected": len(self.rejected),
        }


def run_player(
    player: str,
    board: Board,
    catalog: Sequence[PartSpec],
    placements: Sequence[Placement],
    rejected: Optional[Sequence[tuple]] = None,
) -> ContestResult:
    sc = score(board, catalog, placements)
    return ContestResult(
        player=player,
        placements=list(placements),
        rejected=list(rejected or []),
        score=sc,
    )


def run_contest(
    board: Board,
    catalog: Sequence[PartSpec],
    human_script: Optional[Sequence[Placement]] = None,
) -> List[ContestResult]:
    if not has_defect_constraints(board):
        raise ValueError("kill_gate: contest requires defect constraints")

    results: List[ContestResult] = []

    solver_pl = solver_place(board, catalog)
    results.append(run_player("solver", board, catalog, solver_pl))

    rotation_pl = rotation_heuristic_place(board, catalog)
    results.append(run_player("rotate", board, catalog, rotation_pl))

    if human_script is not None:
        ok, rejected = place_sequence(board, catalog, human_script)
        results.append(run_player("human", board, catalog, ok, rejected))

    results.sort(key=lambda r: (r.score.waste_pct, r.player))
    return results


def leaderboard_lines(results: Sequence[ContestResult]) -> List[str]:
    lines = ["rank  player   waste%    util%   placed  rejected"]
    for i, r in enumerate(results, start=1):
        lines.append(
            f"{i:<5} {r.player:<8} {r.score.waste_pct:>7.2f}  "
            f"{r.score.utilization_pct:>6.2f}  {r.score.placed_count:>6}  "
            f"{len(r.rejected):>8}"
        )
    return lines
