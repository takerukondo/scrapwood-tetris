"""Headless contest CLI — 10s demo."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

from scrapwood.agent import rotation_heuristic_place, solver_place
from scrapwood.constraints import check_placement, has_defect_constraints
from scrapwood.contest import leaderboard_lines, run_contest
from scrapwood.env import make_env
from scrapwood.load import (
    default_baseline_path,
    default_board_path,
    default_human_path,
    default_parts_path,
    load_baseline,
    load_board,
    load_catalog,
    load_placements,
)
from scrapwood.models import Placement
from scrapwood.scoring import score


def _print_board_ascii(board, catalog, placements) -> None:
    """Tiny ASCII occupancy map for the demo (optional clarity)."""
    grid = [["." for _ in range(board.width)] for _ in range(board.height)]
    for d in board.defect_rects():
        for y in range(d.y, d.y2):
            for x in range(d.x, d.x2):
                if 0 <= y < board.height and 0 <= x < board.width:
                    grid[y][x] = "#"
    symbols = "ABCDEFGHJKLMNPQRSTUVWXYZ"
    for i, p in enumerate(placements):
        ch = symbols[i % len(symbols)]
        r = p.as_rect(catalog)
        for y in range(r.y, r.y2):
            for x in range(r.x, r.x2):
                if grid[y][x] == ".":
                    grid[y][x] = ch
                else:
                    grid[y][x] = "!"
    print("board (.=free #=defect letter=part):")
    for row in grid:
        print("".join(row))


def cmd_demo(args: argparse.Namespace) -> int:
    board = load_board(args.board)
    catalog = load_catalog(args.parts)
    if not has_defect_constraints(board):
        print("FAIL: board has no defect constraints (kill gate)", file=sys.stderr)
        return 2

    human_path = Path(args.human) if args.human else default_human_path()
    human_script = load_placements(human_path) if human_path.exists() else None

    print("=== scrapwood-tetris — 10s contest demo ===")
    print(f"board: {board.board_id}  {board.width}x{board.height}")
    print(
        f"defects: {len(board.defects)}  "
        f"defect_area={board.defect_area()}  usable={board.usable_area()}"
    )
    print(f"parts: {len(catalog)}")
    print()

    # 1) Solver baseline
    solver_pl = solver_place(board, catalog)
    solver_sc = score(board, catalog, solver_pl)
    print(f"[solver] placed={solver_sc.placed_count}  waste%={solver_sc.waste_pct:.2f}")

    # 2) A deliberately different heuristic: rotations allowed, small first.
    rotation_pl = rotation_heuristic_place(board, catalog)
    rotation_sc = score(board, catalog, rotation_pl)
    print(
        f"[rotate] placed={rotation_sc.placed_count}  "
        f"waste%={rotation_sc.waste_pct:.2f}"
    )

    # 3) Human script (if present) + illegal demo
    if human_script is not None:
        results = run_contest(board, catalog, human_script)
        human = next(r for r in results if r.player == "human")
        print(
            f"[human ] placed={human.score.placed_count}  "
            f"waste%={human.score.waste_pct:.2f}  "
            f"rejected={len(human.rejected)}"
        )
    else:
        results = run_contest(board, catalog, None)
        print("[human ] (no script; skipped)")

    # Illegal knot overlap demo
    illegal = Placement("H", x=5, y=2, rotation=0)  # sits on knot
    reason = check_placement(board, catalog, illegal, [])
    print(f"[reject] placement on knot → {reason!r}")

    print()
    print("=== leaderboard (lower waste% wins) ===")
    for line in leaderboard_lines(results):
        print(line)

    if args.ascii:
        print()
        best = results[0]
        _print_board_ascii(board, catalog, best.placements)
        print(f"(showing best player: {best.player})")

    # Live env step sample
    if args.env_steps:
        print()
        print("=== step-by-step scorer (solver placements) ===")
        env = make_env(board, catalog)
        obs = env.reset(seed=board.seed)
        print(f"reset waste%={obs['waste_pct']:.2f}")
        for p in solver_pl[: args.env_steps]:
            obs, reward, done, info = env.step(p)
            flag = "ok" if info["accepted"] else info["reason"]
            print(
                f"step {p.part_id}@{p.x},{p.y} r{p.rotation} → "
                f"waste%={obs['waste_pct']:.2f} reward={reward:.2f} ({flag})"
            )
            if done:
                break

    return 0


def cmd_check_baseline(args: argparse.Namespace) -> int:
    board = load_board(args.board)
    catalog = load_catalog(args.parts)
    baseline = load_baseline(args.baseline)
    solver_pl = solver_place(board, catalog)
    sc = score(board, catalog, solver_pl)
    expected = float(baseline["solver_waste_pct"])
    eps = float(baseline.get("epsilon", 0.05))
    delta = abs(sc.waste_pct - expected)
    print(
        f"solver waste%={sc.waste_pct} expected={expected} eps={eps} delta={delta}"
    )
    if delta > eps:
        print("BASELINE DRIFT", file=sys.stderr)
        return 1
    print("baseline ok")
    return 0


def cmd_dump_solver(args: argparse.Namespace) -> int:
    board = load_board(args.board)
    catalog = load_catalog(args.parts)
    pl = solver_place(board, catalog)
    sc = score(board, catalog, pl)
    payload = {
        "placements": [
            {"part_id": p.part_id, "x": p.x, "y": p.y, "rotation": p.rotation}
            for p in pl
        ],
        "score": sc.as_dict(),
    }
    print(json.dumps(payload, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="scrapwood",
        description="Defect-aware scrapwood packing contest",
    )
    p.add_argument(
        "--board",
        default=str(default_board_path()),
        help="synthetic board JSON",
    )
    p.add_argument(
        "--parts",
        default=str(default_parts_path()),
        help="synthetic parts JSON",
    )
    sub = p.add_subparsers(dest="command")

    demo = sub.add_parser("demo", help="10s contest demo (default)")
    demo.add_argument("--human", default=None, help="human placement script JSON")
    demo.add_argument("--ascii", action="store_true", help="print ASCII board")
    demo.add_argument(
        "--env-steps",
        type=int,
        default=3,
        help="show N step-by-step placements (0 to skip)",
    )
    demo.set_defaults(func=cmd_demo)

    base = sub.add_parser("check-baseline", help="contest freeze vs golden waste%")
    base.add_argument(
        "--baseline",
        default=str(default_baseline_path()),
        help="baseline JSON",
    )
    base.set_defaults(func=cmd_check_baseline)

    dump = sub.add_parser("dump-solver", help="print solver placements + score")
    dump.set_defaults(func=cmd_dump_solver)

    return p


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "command", None):
        args.command = "demo"
        args.human = None
        args.ascii = True
        args.env_steps = 3
        args.func = cmd_demo
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
