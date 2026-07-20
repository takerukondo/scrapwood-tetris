"""Gymnasium-shaped thin env: reset / step / score (no full RL stack)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple

from scrapwood.constraints import ConstraintError, assert_legal, has_defect_constraints
from scrapwood.models import Board, ContestState, PartSpec, Placement
from scrapwood.scoring import Score, score


@dataclass
class ScrapwoodEnv:
    """
    Minimal contest env.

    observation = remaining part ids + current waste%
    action = Placement
    """

    board: Board
    catalog: List[PartSpec]
    _state: ContestState = field(init=False)
    _done: bool = False

    def __post_init__(self) -> None:
        if not has_defect_constraints(self.board):
            raise ValueError(
                "kill_gate: board must include defect/knot constraints"
            )
        self.reset()

    def reset(self, seed: Optional[int] = None) -> Dict[str, Any]:
        if seed is not None:
            # Seed reserved for future stochastic boards; fixtures are fixed.
            self.board.seed = seed
        self._state = ContestState(
            board=self.board,
            catalog=list(self.catalog),
            placements=[],
            rejected=[],
        )
        self._done = False
        return self._observe()

    def step(
        self, action: Placement
    ) -> Tuple[Dict[str, Any], float, bool, Dict[str, Any]]:
        if self._done:
            raise RuntimeError("episode already done; call reset()")

        info: Dict[str, Any] = {"action": action}
        try:
            assert_legal(
                self._state.board,
                self._state.catalog,
                action,
                self._state.placements,
            )
            self._state.placements.append(action)
            info["accepted"] = True
            info["reason"] = None
        except ConstraintError as exc:
            self._state.rejected.append((action, str(exc)))
            info["accepted"] = False
            info["reason"] = str(exc)

        sc = self.score()
        # Reward = negative waste (lower waste → higher reward)
        reward = -sc.waste_pct
        remaining = self._state.remaining_parts()
        if not remaining:
            self._done = True
        obs = self._observe()
        return obs, reward, self._done, info

    def score(self) -> Score:
        return score(self._state.board, self._state.catalog, self._state.placements)

    @property
    def state(self) -> ContestState:
        return self._state

    def _observe(self) -> Dict[str, Any]:
        sc = self.score()
        return {
            "board_id": self.board.board_id,
            "remaining": [p.part_id for p in self._state.remaining_parts()],
            "placed": [p.part_id for p in self._state.placements],
            "waste_pct": sc.waste_pct,
            "utilization_pct": sc.utilization_pct,
            "defect_count": len(self.board.defects),
        }


def make_env(board: Board, catalog: Sequence[PartSpec]) -> ScrapwoodEnv:
    return ScrapwoodEnv(board=board, catalog=list(catalog))
