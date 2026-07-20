"""Domain models: board, parts, placements."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Sequence, Tuple

from scrapwood.geometry import Polygon, Rect


@dataclass(frozen=True)
class PartSpec:
    part_id: str
    w: int
    h: int

    @property
    def area(self) -> int:
        return self.w * self.h

    def size(self, rotation: int) -> Tuple[int, int]:
        if rotation % 180 == 0:
            return self.w, self.h
        if rotation % 180 == 90:
            return self.h, self.w
        raise ValueError(f"unsupported rotation: {rotation}")


@dataclass(frozen=True)
class Placement:
    part_id: str
    x: int
    y: int
    rotation: int = 0  # 0 or 90

    def as_rect(self, catalog: Sequence[PartSpec]) -> Rect:
        spec = _lookup(catalog, self.part_id)
        w, h = spec.size(self.rotation)
        return Rect(self.x, self.y, w, h)


@dataclass
class Board:
    board_id: str
    width: int
    height: int
    defects: List[Polygon] = field(default_factory=list)
    seed: int = 0

    @property
    def bounds(self) -> Rect:
        return Rect(0, 0, self.width, self.height)

    @property
    def area(self) -> int:
        return self.width * self.height

    def defect_rects(self) -> List[Rect]:
        return [d.aabb() for d in self.defects]

    def defect_area(self) -> int:
        # Synthetic AABB defects are non-overlapping in fixtures.
        return sum(r.area for r in self.defect_rects())

    def usable_area(self) -> int:
        return self.area - self.defect_area()


@dataclass
class ContestState:
    board: Board
    catalog: List[PartSpec]
    placements: List[Placement] = field(default_factory=list)
    rejected: List[Tuple[Placement, str]] = field(default_factory=list)

    def placed_part_ids(self) -> set:
        return {p.part_id for p in self.placements}

    def remaining_parts(self) -> List[PartSpec]:
        used = self.placed_part_ids()
        return [p for p in self.catalog if p.part_id not in used]


def _lookup(catalog: Sequence[PartSpec], part_id: str) -> PartSpec:
    for p in catalog:
        if p.part_id == part_id:
            return p
    raise KeyError(f"unknown part_id: {part_id}")


def find_part(catalog: Sequence[PartSpec], part_id: str) -> Optional[PartSpec]:
    for p in catalog:
        if p.part_id == part_id:
            return p
    return None
