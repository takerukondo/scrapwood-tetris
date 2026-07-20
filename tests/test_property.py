"""Property: random legal placements never overlap defects."""

from hypothesis import given, settings, strategies as st

from scrapwood.constraints import check_placement
from scrapwood.load import load_contest_fixture
from scrapwood.models import Placement


@settings(max_examples=80, deadline=None)
@given(
    part_idx=st.integers(min_value=0, max_value=14),
    x=st.integers(min_value=-2, max_value=22),
    y=st.integers(min_value=-2, max_value=14),
    rot=st.sampled_from([0, 90]),
)
def test_accepted_placements_never_hit_defects(part_idx, x, y, rot):
    board, catalog = load_contest_fixture()
    part = catalog[part_idx % len(catalog)]
    cand = Placement(part.part_id, x, y, rot)
    reason = check_placement(board, catalog, cand, [])
    if reason is None:
        rect = cand.as_rect(catalog)
        for defect in board.defect_rects():
            assert not rect.intersects(defect)
        assert rect.within(board.bounds)
    else:
        # If it intersects a defect, reason must say so (when that is the cause).
        rect_ok = True
        try:
            rect = cand.as_rect(catalog)
            rect_ok = rect.within(board.bounds)
        except ValueError:
            return
        if rect_ok and any(rect.intersects(d) for d in board.defect_rects()):
            assert reason == "defect_overlap"
