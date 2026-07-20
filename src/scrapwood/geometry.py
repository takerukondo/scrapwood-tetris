"""Axis-aligned geometry helpers (synthetic board units)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence, Tuple

Point = Tuple[int, int]


@dataclass(frozen=True)
class Rect:
    x: int
    y: int
    w: int
    h: int

    def __post_init__(self) -> None:
        if self.w <= 0 or self.h <= 0:
            raise ValueError("Rect width/height must be positive")

    @property
    def x2(self) -> int:
        return self.x + self.w

    @property
    def y2(self) -> int:
        return self.y + self.h

    @property
    def area(self) -> int:
        return self.w * self.h

    def contains_point(self, px: int, py: int) -> bool:
        return self.x <= px < self.x2 and self.y <= py < self.y2

    def intersects(self, other: "Rect") -> bool:
        return not (
            self.x2 <= other.x
            or other.x2 <= self.x
            or self.y2 <= other.y
            or other.y2 <= self.y
        )

    def within(self, bounds: "Rect") -> bool:
        return (
            self.x >= bounds.x
            and self.y >= bounds.y
            and self.x2 <= bounds.x2
            and self.y2 <= bounds.y2
        )

    def rotated_90(self) -> "Rect":
        return Rect(self.x, self.y, self.h, self.w)


@dataclass(frozen=True)
class Polygon:
    """Simple polygon; MVP treats AABB as the hard constraint footprint."""

    vertices: Tuple[Point, ...]
    kind: str = "knot"

    def __post_init__(self) -> None:
        if len(self.vertices) < 3:
            raise ValueError("Polygon needs >= 3 vertices")

    def aabb(self) -> Rect:
        xs = [p[0] for p in self.vertices]
        ys = [p[1] for p in self.vertices]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        return Rect(min_x, min_y, max_x - min_x, max_y - min_y)

    @classmethod
    def from_rect(cls, rect: Rect, kind: str = "knot") -> "Polygon":
        return cls(
            vertices=(
                (rect.x, rect.y),
                (rect.x2, rect.y),
                (rect.x2, rect.y2),
                (rect.x, rect.y2),
            ),
            kind=kind,
        )


def any_intersect(rect: Rect, others: Iterable[Rect]) -> bool:
    return any(rect.intersects(o) for o in others)


def total_area(rects: Sequence[Rect]) -> int:
    return sum(r.area for r in rects)
