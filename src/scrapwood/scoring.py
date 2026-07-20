"""Waste% and material-efficiency scoring."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from scrapwood.models import Board, PartSpec, Placement


@dataclass(frozen=True)
class Score:
    board_area: int
    defect_area: int
    usable_area: int
    placed_area: int
    placed_count: int
    waste_pct: float
    utilization_pct: float

    def as_dict(self) -> dict:
        return {
            "board_area": self.board_area,
            "defect_area": self.defect_area,
            "usable_area": self.usable_area,
            "placed_area": self.placed_area,
            "placed_count": self.placed_count,
            "waste_pct": self.waste_pct,
            "utilization_pct": self.utilization_pct,
        }


def score(
    board: Board,
    catalog: Sequence[PartSpec],
    placements: Sequence[Placement],
) -> Score:
    """
    waste_pct = 100 * (usable_area - placed_area) / usable_area

    Usable area excludes knot/defect AABBs. Lower waste% is better.
    """
    usable = board.usable_area()
    if usable <= 0:
        raise ValueError("board has no usable area")

    placed_area = 0
    for p in placements:
        placed_area += p.as_rect(catalog).area

    if placed_area > usable:
        # Should not happen with legal placements; clamp for display safety.
        placed_area = usable

    unused = usable - placed_area
    waste_pct = 100.0 * unused / usable
    util_pct = 100.0 * placed_area / usable
    return Score(
        board_area=board.area,
        defect_area=board.defect_area(),
        usable_area=usable,
        placed_area=placed_area,
        placed_count=len(placements),
        waste_pct=round(waste_pct, 4),
        utilization_pct=round(util_pct, 4),
    )
