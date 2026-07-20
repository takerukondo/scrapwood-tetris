"""Agent stub: alternate greedy heuristic under the same scorer."""

from __future__ import annotations

from typing import List, Sequence

from scrapwood.models import Board, PartSpec, Placement
from scrapwood.placer import greedy_place


def agent_place(board: Board, catalog: Sequence[PartSpec]) -> List[Placement]:
    """
    Stub agent: smallest-first bottom-left with rotations.

    Same constraint checker and scorer as the solver baseline; order and
    rotation policy differ. Not a trained policy.
    """
    return greedy_place(board, catalog, order="area_asc", allow_rotate=True)


def solver_place(board: Board, catalog: Sequence[PartSpec]) -> List[Placement]:
    """
    Deterministic greedy baseline: largest-first BLF, no rotation.

    Intentionally thin — rotation-aware packing is left to human/agent
    contestants so waste% can diverge under the same scorer.
    """
    return greedy_place(board, catalog, order="area_desc", allow_rotate=False)
