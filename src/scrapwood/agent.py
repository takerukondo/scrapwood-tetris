"""Two deliberately small packing heuristics under the same scorer."""

from __future__ import annotations

from typing import List, Sequence

from scrapwood.models import Board, PartSpec, Placement
from scrapwood.placer import greedy_place


def rotation_heuristic_place(
    board: Board, catalog: Sequence[PartSpec]
) -> List[Placement]:
    """
    Smallest-first bottom-left heuristic with rotations.

    Same constraint checker and scorer as the baseline; only ordering and
    rotation policy differ. This is not an AI agent or a trained policy.
    """
    return greedy_place(board, catalog, order="area_asc", allow_rotate=True)


def solver_place(board: Board, catalog: Sequence[PartSpec]) -> List[Placement]:
    """
    Deterministic greedy baseline: largest-first BLF, no rotation.

    Intentionally thin — rotation-aware packing is left to human/agent
    contestants so waste% can diverge under the same scorer.
    """
    return greedy_place(board, catalog, order="area_desc", allow_rotate=False)
