"""Gymnasium-shaped env."""

import pytest

from scrapwood.env import ScrapwoodEnv, make_env
from scrapwood.load import load_contest_fixture
from scrapwood.models import Board, Placement
from scrapwood.agent import solver_place


def test_env_rejects_defect_free_board():
    board = Board(board_id="x", width=5, height=5, defects=[])
    with pytest.raises(ValueError, match="kill_gate"):
        ScrapwoodEnv(board=board, catalog=[])


def test_reset_step_score():
    board, catalog = load_contest_fixture()
    env = make_env(board, catalog)
    obs = env.reset(seed=42)
    assert obs["waste_pct"] == 100.0
    assert obs["defect_count"] >= 1

    pose = solver_place(board, catalog)[0]
    obs2, reward, done, info = env.step(pose)
    assert info["accepted"] is True
    assert obs2["waste_pct"] < 100.0
    assert reward == -obs2["waste_pct"]
    assert env.score().waste_pct == obs2["waste_pct"]


def test_env_rejects_illegal_step():
    board, catalog = load_contest_fixture()
    env = make_env(board, catalog)
    env.reset()
    obs, reward, done, info = env.step(Placement("O", 5, 2, 0))
    assert info["accepted"] is False
    assert info["reason"] == "defect_overlap"
    assert obs["waste_pct"] == 100.0
