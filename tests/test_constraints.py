"""Defect / bounds / overlap constraints."""

from scrapwood.constraints import check_placement, has_defect_constraints
from scrapwood.load import load_contest_fixture
from scrapwood.models import Board, Placement
from scrapwood.geometry import Polygon


def test_board_has_defect_constraints_kill_gate():
    board, _ = load_contest_fixture()
    assert has_defect_constraints(board)


def test_defect_free_board_fails_kill_gate():
    empty = Board(board_id="empty", width=10, height=10, defects=[])
    assert not has_defect_constraints(empty)


def test_knot_overlap_is_illegal():
    board, catalog = load_contest_fixture()
    # First knot AABB is (5,2)-(8,4)
    bad = Placement("O", x=5, y=2, rotation=0)
    assert check_placement(board, catalog, bad, []) == "defect_overlap"


def test_legal_placement_away_from_knots():
    board, catalog = load_contest_fixture()
    ok = Placement("O", x=0, y=0, rotation=0)
    assert check_placement(board, catalog, ok, []) is None


def test_out_of_bounds_illegal():
    board, catalog = load_contest_fixture()
    bad = Placement("A", x=15, y=0, rotation=0)  # 10x6 → x2=25 > 20
    assert check_placement(board, catalog, bad, []) == "out_of_bounds"


def test_part_overlap_illegal():
    board, catalog = load_contest_fixture()
    first = Placement("O", x=0, y=0, rotation=0)
    second = Placement("N", x=1, y=0, rotation=0)
    assert check_placement(board, catalog, first, []) is None
    assert check_placement(board, catalog, second, [first]) == "part_overlap:O"


def test_polygon_defect_aabb_used():
    board = Board(
        board_id="poly",
        width=10,
        height=10,
        defects=[
            Polygon(vertices=((2, 2), (4, 2), (4, 4), (2, 4)), kind="knot")
        ],
    )
    from scrapwood.models import PartSpec

    catalog = [PartSpec("P", 2, 2)]
    assert check_placement(board, catalog, Placement("P", 2, 2, 0), []) == (
        "defect_overlap"
    )
