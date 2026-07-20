"""Deterministic placer."""

from scrapwood.agent import agent_place, solver_place
from scrapwood.constraints import check_placement, validate_state
from scrapwood.load import load_contest_fixture
from scrapwood.placer import greedy_place
from scrapwood.scoring import score


def test_solver_is_deterministic():
    board, catalog = load_contest_fixture()
    a = solver_place(board, catalog)
    b = solver_place(board, catalog)
    assert a == b


def test_solver_placements_are_all_legal():
    board, catalog = load_contest_fixture()
    placed = solver_place(board, catalog)
    assert validate_state(board, catalog, placed) == []


def test_greedy_never_overlaps_defects():
    board, catalog = load_contest_fixture()
    for order in ("area_desc", "area_asc", "catalog"):
        placed = greedy_place(board, catalog, order=order, allow_rotate=True)
        for i, p in enumerate(placed):
            assert check_placement(board, catalog, p, placed[:i]) is None


def test_agent_and_solver_differ():
    board, catalog = load_contest_fixture()
    assert solver_place(board, catalog) != agent_place(board, catalog)


def test_rotation_improves_or_matches_no_rotate():
    board, catalog = load_contest_fixture()
    no_rot = greedy_place(board, catalog, order="area_desc", allow_rotate=False)
    with_rot = greedy_place(board, catalog, order="area_desc", allow_rotate=True)
    assert score(board, catalog, with_rot).waste_pct <= score(
        board, catalog, no_rot
    ).waste_pct
