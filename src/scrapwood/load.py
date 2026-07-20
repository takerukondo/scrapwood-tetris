"""Load synthetic board / part fixtures (JSON)."""

from __future__ import annotations

import json
from importlib.resources import files
from pathlib import Path
from typing import Any, List, Optional, Tuple, Union

from scrapwood.geometry import Polygon, Rect
from scrapwood.models import Board, PartSpec, Placement

PathLike = Union[str, Path]


def _data_path(*parts: str) -> Path:
    """Return a packaged demo-data path (works from an installed wheel)."""
    return Path(str(files("scrapwood").joinpath("data", *parts)))


def default_board_path() -> Path:
    return _data_path("knotty_board.json")


def default_parts_path() -> Path:
    return _data_path("catalog.json")


def default_baseline_path() -> Path:
    return _data_path("seeded_waste.json")


def default_human_path() -> Path:
    return _data_path("human_script.json")


def _read_json(path: PathLike) -> Any:
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"JSON not found: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path}: {exc.msg}") from exc


def _require_mapping(data: Any, path: Path, kind: str) -> dict:
    if not isinstance(data, dict):
        raise ValueError(
            f"{kind} JSON must be a mapping, got {type(data).__name__}: {path}"
        )
    return data


def _require_keys(data: dict, keys: Tuple[str, ...], path: Path, kind: str) -> None:
    missing = [k for k in keys if k not in data]
    if missing:
        raise ValueError(
            f"{kind} JSON missing required key(s) {missing}: {path}"
        )


def _positive_int(value: Any, field: str, path: Path) -> int:
    try:
        n = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be an integer in {path}") from exc
    if n <= 0:
        raise ValueError(f"{field} must be positive in {path}, got {n}")
    return n


def _nonneg_int(value: Any, field: str, path: Path) -> int:
    try:
        n = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be an integer in {path}") from exc
    if n < 0:
        raise ValueError(f"{field} must be >= 0 in {path}, got {n}")
    return n


def _parse_defect(raw: Any, path: Path, index: int) -> Polygon:
    if not isinstance(raw, dict):
        raise ValueError(
            f"defect[{index}] must be a mapping in {path}, got {type(raw).__name__}"
        )
    kind = str(raw.get("kind", "knot"))
    if "vertices" in raw:
        verts_raw = raw["vertices"]
        if not isinstance(verts_raw, list) or len(verts_raw) < 3:
            raise ValueError(
                f"defect[{index}].vertices needs >= 3 points in {path}"
            )
        try:
            verts = tuple((int(x), int(y)) for x, y in verts_raw)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"defect[{index}].vertices must be [x,y] integer pairs in {path}"
            ) from exc
        try:
            return Polygon(vertices=verts, kind=kind)
        except ValueError as exc:
            raise ValueError(f"defect[{index}] invalid polygon in {path}: {exc}") from exc

    for key in ("x", "y", "w", "h"):
        if key not in raw:
            raise ValueError(
                f"defect[{index}] missing '{key}' (or 'vertices') in {path}"
            )
    try:
        rect = Rect(
            _nonneg_int(raw["x"], f"defect[{index}].x", path),
            _nonneg_int(raw["y"], f"defect[{index}].y", path),
            _positive_int(raw["w"], f"defect[{index}].w", path),
            _positive_int(raw["h"], f"defect[{index}].h", path),
        )
    except ValueError as exc:
        raise ValueError(f"defect[{index}] invalid rect in {path}: {exc}") from exc
    return Polygon.from_rect(rect, kind=kind)


def load_board(path: PathLike) -> Board:
    path = Path(path)
    data = _require_mapping(_read_json(path), path, "board")
    _require_keys(data, ("board_id", "width", "height"), path, "board")

    width = _positive_int(data["width"], "width", path)
    height = _positive_int(data["height"], "height", path)

    raw_defects = data.get("defects", [])
    if raw_defects is None:
        raw_defects = []
    if not isinstance(raw_defects, list):
        raise ValueError(f"board 'defects' must be a list in {path}")

    defects: List[Polygon] = []
    for i, d in enumerate(raw_defects):
        defects.append(_parse_defect(d, path, i))

    try:
        seed = int(data.get("seed", 0))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"seed must be an integer in {path}") from exc

    board = Board(
        board_id=str(data["board_id"]),
        width=width,
        height=height,
        defects=defects,
        seed=seed,
    )
    if board.usable_area() <= 0:
        raise ValueError(
            f"board has no usable area after defects in {path} "
            f"(area={board.area}, defect_area={board.defect_area()})"
        )
    return board


def load_catalog(path: PathLike) -> List[PartSpec]:
    path = Path(path)
    data = _read_json(path)
    if isinstance(data, dict):
        if "parts" not in data:
            raise ValueError(f"catalog JSON missing required key 'parts': {path}")
        parts = data["parts"]
    else:
        parts = data
    if not isinstance(parts, list):
        raise ValueError(
            f"catalog 'parts' must be a list, got {type(parts).__name__}: {path}"
        )
    out: List[PartSpec] = []
    for i, p in enumerate(parts):
        if not isinstance(p, dict):
            raise ValueError(
                f"parts[{i}] must be a mapping in {path}, got {type(p).__name__}"
            )
        for key in ("part_id", "w", "h"):
            if key not in p:
                raise ValueError(f"parts[{i}] missing '{key}' in {path}")
        out.append(
            PartSpec(
                part_id=str(p["part_id"]),
                w=_positive_int(p["w"], f"parts[{i}].w", path),
                h=_positive_int(p["h"], f"parts[{i}].h", path),
            )
        )
    return out


def load_placements(path: PathLike) -> List[Placement]:
    path = Path(path)
    data = _read_json(path)
    if isinstance(data, dict):
        if "placements" not in data:
            raise ValueError(
                f"placements JSON missing required key 'placements': {path}"
            )
        items = data["placements"]
    else:
        items = data
    if not isinstance(items, list):
        raise ValueError(
            f"placements must be a list, got {type(items).__name__}: {path}"
        )
    out: List[Placement] = []
    for i, p in enumerate(items):
        if not isinstance(p, dict):
            raise ValueError(
                f"placements[{i}] must be a mapping in {path}, "
                f"got {type(p).__name__}"
            )
        for key in ("part_id", "x", "y"):
            if key not in p:
                raise ValueError(f"placements[{i}] missing '{key}' in {path}")
        try:
            rot = int(p.get("rotation", 0))
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"placements[{i}].rotation must be an integer in {path}"
            ) from exc
        out.append(
            Placement(
                part_id=str(p["part_id"]),
                x=_nonneg_int(p["x"], f"placements[{i}].x", path),
                y=_nonneg_int(p["y"], f"placements[{i}].y", path),
                rotation=rot,
            )
        )
    return out


def load_baseline(path: PathLike) -> dict:
    path = Path(path)
    data = _require_mapping(_read_json(path), path, "baseline")
    _require_keys(data, ("solver_waste_pct",), path, "baseline")
    return data


def load_contest_fixture(
    board_path: Optional[PathLike] = None,
    parts_path: Optional[PathLike] = None,
) -> Tuple[Board, List[PartSpec]]:
    board = load_board(board_path or default_board_path())
    catalog = load_catalog(parts_path or default_parts_path())
    return board, catalog
