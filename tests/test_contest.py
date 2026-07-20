"""Contest harness + baseline freeze."""

from scrapwood.contest import run_contest
from scrapwood.load import (
    default_baseline_path,
    default_human_path,
    load_baseline,
    load_contest_fixture,
    load_placements,
)
from scrapwood.agent import solver_place
from scrapwood.scoring import score


def test_contest_leaderboard_human_beats_solver():
    board, catalog = load_contest_fixture()
    human = load_placements(default_human_path())
    results = run_contest(board, catalog, human)
    by = {r.player: r for r in results}
    assert by["human"].score.waste_pct < by["solver"].score.waste_pct
    assert by["solver"].score.waste_pct < by["rotate"].score.waste_pct


def test_human_script_rejects_knot_hit():
    board, catalog = load_contest_fixture()
    human = load_placements(default_human_path())
    results = run_contest(board, catalog, human)
    human_r = next(r for r in results if r.player == "human")
    assert any(reason == "defect_overlap" for _, reason in human_r.rejected)


def test_contest_freeze_solver_waste_within_epsilon():
    board, catalog = load_contest_fixture()
    baseline = load_baseline(default_baseline_path())
    sc = score(board, catalog, solver_place(board, catalog))
    eps = float(baseline["epsilon"])
    assert abs(sc.waste_pct - float(baseline["solver_waste_pct"])) <= eps
    assert sc.placed_count == int(baseline["solver_placed_count"])
