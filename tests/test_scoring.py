"""Waste% golden formula."""

from scrapwood.load import load_contest_fixture
from scrapwood.models import Placement
from scrapwood.scoring import score


def test_empty_board_is_100_percent_waste():
    board, catalog = load_contest_fixture()
    sc = score(board, catalog, [])
    assert sc.waste_pct == 100.0
    assert sc.placed_area == 0
    assert sc.usable_area == board.area - board.defect_area()


def test_waste_formula_golden():
    board, catalog = load_contest_fixture()
    # Place a single 2x2 at origin → placed_area=4
    pl = [Placement("O", 0, 0, 0)]
    sc = score(board, catalog, pl)
    usable = board.usable_area()
    expected = round(100.0 * (usable - 4) / usable, 4)
    assert sc.waste_pct == expected
    assert sc.utilization_pct == round(100.0 * 4 / usable, 4)


def test_more_placed_area_lowers_waste():
    board, catalog = load_contest_fixture()
    one = [Placement("O", 0, 0, 0)]
    two = [
        Placement("O", 0, 0, 0),
        Placement("N", 2, 0, 0),
    ]
    assert score(board, catalog, two).waste_pct < score(board, catalog, one).waste_pct
