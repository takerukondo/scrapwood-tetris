"""Malformed / empty fixture hardening."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scrapwood.load import load_board, load_catalog, load_placements


def _write(tmp_path: Path, name: str, payload) -> Path:
    path = tmp_path / name
    if isinstance(payload, str):
        path.write_text(payload, encoding="utf-8")
    else:
        path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_empty_board_mapping_raises_value_error(tmp_path: Path):
    path = _write(tmp_path, "empty.json", {})
    with pytest.raises(ValueError, match="missing required key"):
        load_board(path)


def test_board_list_top_level_raises_value_error(tmp_path: Path):
    path = _write(tmp_path, "list.json", [])
    with pytest.raises(ValueError, match="must be a mapping"):
        load_board(path)


def test_invalid_json_raises_value_error(tmp_path: Path):
    path = _write(tmp_path, "bad.json", "{not json")
    with pytest.raises(ValueError, match="invalid JSON"):
        load_board(path)


def test_negative_board_size_rejected(tmp_path: Path):
    path = _write(
        tmp_path,
        "neg.json",
        {"board_id": "x", "width": -1, "height": 10, "defects": []},
    )
    with pytest.raises(ValueError, match="width must be positive"):
        load_board(path)


def test_zero_board_size_rejected(tmp_path: Path):
    path = _write(
        tmp_path,
        "zero.json",
        {"board_id": "x", "width": 0, "height": 0, "defects": []},
    )
    with pytest.raises(ValueError, match="width must be positive"):
        load_board(path)


def test_full_defect_board_rejected(tmp_path: Path):
    path = _write(
        tmp_path,
        "full.json",
        {
            "board_id": "x",
            "width": 2,
            "height": 2,
            "defects": [{"x": 0, "y": 0, "w": 2, "h": 2}],
        },
    )
    with pytest.raises(ValueError, match="no usable area"):
        load_board(path)


def test_defect_missing_rect_keys_raises_value_error(tmp_path: Path):
    path = _write(
        tmp_path,
        "defect.json",
        {
            "board_id": "x",
            "width": 10,
            "height": 10,
            "defects": [{"kind": "knot"}],
        },
    )
    with pytest.raises(ValueError, match="missing 'x'"):
        load_board(path)


def test_catalog_missing_parts_raises_value_error(tmp_path: Path):
    path = _write(tmp_path, "cat.json", {})
    with pytest.raises(ValueError, match="missing required key 'parts'"):
        load_catalog(path)


def test_catalog_null_parts_raises_value_error(tmp_path: Path):
    path = _write(tmp_path, "cat.json", {"parts": None})
    with pytest.raises(ValueError, match="must be a list"):
        load_catalog(path)


def test_placement_missing_keys_raises_value_error(tmp_path: Path):
    path = _write(tmp_path, "pl.json", {"placements": [{"part_id": "A"}]})
    with pytest.raises(ValueError, match="missing 'x'"):
        load_placements(path)
