"""
Thin deterministic bottom-left placer.

Conceptually reuses the nesting idea of scanning candidate poses
(SVGNest / rectpack lineage) — not a GA/NFP engine. Defects are first-class
hard constraints checked at each candidate.
"""

from __future__ import annotations

from typing import Iterable, List, Optional, Sequence, Tuple

from scrapwood.constraints import check_placement
from scrapwood.models import Board, PartSpec, Placement


def candidate_rotations(part: PartSpec, allow_rotate: bool = True) -> Tuple[int, ...]:
    if not allow_rotate or part.w == part.h:
        return (0,)
    return (0, 90)


def iter_positions(board: Board, w: int, h: int) -> Iterable[Tuple[int, int]]:
    """Bottom-left scan: y ascending, then x ascending (deterministic)."""
    max_x = board.width - w
    max_y = board.height - h
    if max_x < 0 or max_y < 0:
        return
    for y in range(0, max_y + 1):
        for x in range(0, max_x + 1):
            yield x, y


def first_legal_pose(
    board: Board,
    catalog: Sequence[PartSpec],
    part: PartSpec,
    existing: Sequence[Placement],
    *,
    allow_rotate: bool = True,
) -> Optional[Placement]:
    for rot in candidate_rotations(part, allow_rotate=allow_rotate):
        pw, ph = part.size(rot)
        for x, y in iter_positions(board, pw, ph):
            cand = Placement(part.part_id, x, y, rot)
            if check_placement(board, catalog, cand, existing) is None:
                return cand
    return None


def greedy_place(
    board: Board,
    catalog: Sequence[PartSpec],
    *,
    order: str = "area_desc",
    allow_rotate: bool = True,
) -> List[Placement]:
    """
    Deterministic greedy baseline (thin BLF; not a GA/NFP nest engine).

    order:
      - area_desc: larger parts first (default solver)
      - area_asc: smaller first (alternate agent heuristic)
      - catalog: fixture order
    allow_rotate: if False, only axis-aligned as authored (weaker baseline)
    """
    parts = list(catalog)
    if order == "area_desc":
        parts.sort(key=lambda p: (-p.area, p.part_id))
    elif order == "area_asc":
        parts.sort(key=lambda p: (p.area, p.part_id))
    elif order == "catalog":
        pass
    else:
        raise ValueError(f"unknown order: {order}")

    placed: List[Placement] = []
    for part in parts:
        pose = first_legal_pose(
            board, catalog, part, placed, allow_rotate=allow_rotate
        )
        if pose is not None:
            placed.append(pose)
    return placed


def place_sequence(
    board: Board,
    catalog: Sequence[PartSpec],
    sequence: Sequence[Placement],
) -> Tuple[List[Placement], List[Tuple[Placement, str]]]:
    """Apply an explicit placement list; skip/reject illegals."""
    ok: List[Placement] = []
    rejected: List[Tuple[Placement, str]] = []
    for p in sequence:
        reason = check_placement(board, catalog, p, ok)
        if reason is None:
            ok.append(p)
        else:
            rejected.append((p, reason))
    return ok, rejected
