"""Hard constraints: defects, bounds, pairwise overlap."""

from __future__ import annotations

from typing import List, Optional, Sequence, Tuple

from scrapwood.geometry import Rect
from scrapwood.models import Board, PartSpec, Placement, find_part


class ConstraintError(ValueError):
    """Raised when a placement violates a hard constraint."""


def check_placement(
    board: Board,
    catalog: Sequence[PartSpec],
    placement: Placement,
    existing: Sequence[Placement],
) -> Optional[str]:
    """Return None if legal, else a short reason string."""
    spec = find_part(catalog, placement.part_id)
    if spec is None:
        return f"unknown_part:{placement.part_id}"
    if placement.part_id in {p.part_id for p in existing}:
        return f"duplicate_part:{placement.part_id}"
    if placement.rotation % 90 != 0:
        return f"bad_rotation:{placement.rotation}"

    try:
        rect = placement.as_rect(catalog)
    except ValueError as exc:
        return str(exc)

    if not rect.within(board.bounds):
        return "out_of_bounds"

    for defect in board.defect_rects():
        if rect.intersects(defect):
            return "defect_overlap"

    for other in existing:
        if rect.intersects(other.as_rect(catalog)):
            return f"part_overlap:{other.part_id}"

    return None


def assert_legal(
    board: Board,
    catalog: Sequence[PartSpec],
    placement: Placement,
    existing: Sequence[Placement],
) -> Rect:
    reason = check_placement(board, catalog, placement, existing)
    if reason is not None:
        raise ConstraintError(reason)
    return placement.as_rect(catalog)


def has_defect_constraints(board: Board) -> bool:
    """Kill-gate helper: boards without defects are not valid contest stock."""
    return len(board.defects) > 0 and board.defect_area() > 0


def all_placed_rects(
    catalog: Sequence[PartSpec], placements: Sequence[Placement]
) -> List[Rect]:
    return [p.as_rect(catalog) for p in placements]


def validate_state(
    board: Board, catalog: Sequence[PartSpec], placements: Sequence[Placement]
) -> List[Tuple[Placement, str]]:
    """Re-check placements in order; return illegal ones with reasons."""
    ok: List[Placement] = []
    bad: List[Tuple[Placement, str]] = []
    for p in placements:
        reason = check_placement(board, catalog, p, ok)
        if reason is None:
            ok.append(p)
        else:
            bad.append((p, reason))
    return bad
