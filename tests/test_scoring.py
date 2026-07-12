"""Unit tests for the relocation-decision-model scoring engine.

Pins the pure scoring functions to independently known answers and runs the
bundled example config end-to-end through the config/score loaders, so the
weighting, normalization, tie-breaking and parsing paths can't silently regress.
Runs offline with no network and no credentials: `pytest -q`.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import score  # noqa: E402

EXAMPLE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "examples",
    "eu-relocation-couple",
)


# --------------------------------------------------------------------------- #
# weighted_score
# --------------------------------------------------------------------------- #
def test_weighted_score_is_a_normalized_weighted_average():
    vals = {"a": 8.0, "b": 4.0}
    weights = {"a": 30.0, "b": 10.0}
    # (8*30 + 4*10) / 40 = 280 / 40 = 7.0
    assert score.weighted_score(vals, weights, ["a", "b"]) == pytest.approx(7.0)


def test_weighted_score_normalizes_by_weight_sum_not_100():
    vals = {"a": 10.0, "b": 2.0}
    # weights sum to 3, not 100 — engine divides by the sum regardless.
    weights = {"a": 2.0, "b": 1.0}
    # (10*2 + 2*1) / 3 = 22 / 3
    assert score.weighted_score(vals, weights, ["a", "b"]) == pytest.approx(22.0 / 3.0)


def test_weighted_score_zero_total_weight_returns_zero():
    vals = {"a": 9.0, "b": 9.0}
    weights = {"a": 0.0, "b": 0.0}
    assert score.weighted_score(vals, weights, ["a", "b"]) == 0.0


def test_weighted_score_respects_the_cids_subset():
    vals = {"a": 10.0, "b": 1.0, "c": 5.0}
    weights = {"a": 1.0, "b": 1.0, "c": 1.0}
    # only 'a' and 'b' considered → (10 + 1) / 2 = 5.5
    assert score.weighted_score(vals, weights, ["a", "b"]) == pytest.approx(5.5)


# --------------------------------------------------------------------------- #
# rank_scenario
# --------------------------------------------------------------------------- #
def test_rank_scenario_orders_by_score_descending():
    scores = {
        "Low": {"a": 2.0},
        "High": {"a": 9.0},
        "Mid": {"a": 5.0},
    }
    weights = {"a": 100.0}
    _, rank_map, ordered = score.rank_scenario(scores, weights, ["a"])
    assert [name for name, _ in ordered] == ["High", "Mid", "Low"]
    assert rank_map == {"High": 1, "Mid": 2, "Low": 3}


def test_rank_scenario_breaks_ties_alphabetically():
    scores = {
        "Zeta": {"a": 5.0},
        "Alpha": {"a": 5.0},
    }
    weights = {"a": 100.0}
    _, rank_map, ordered = score.rank_scenario(scores, weights, ["a"])
    # equal scores → alphabetical, so Alpha ranks ahead of Zeta.
    assert [name for name, _ in ordered] == ["Alpha", "Zeta"]
    assert rank_map == {"Alpha": 1, "Zeta": 2}


def test_rank_scenario_rounds_scores_to_two_decimals():
    scores = {"X": {"a": 1.0, "b": 2.0}}
    weights = {"a": 1.0, "b": 2.0}  # (1 + 4) / 3 = 1.666...
    score_map, _, _ = score.rank_scenario(scores, weights, ["a", "b"])
    assert score_map["X"] == 1.67


# --------------------------------------------------------------------------- #
# Integration: the bundled example config parses and ranks end-to-end
# --------------------------------------------------------------------------- #
def test_example_config_loads_and_ranks():
    cfg = score.load_config(os.path.join(EXAMPLE_DIR, "criteria.yaml"))
    assert cfg.criteria, "example config should declare criteria"

    cids = [c.cid for c in cfg.criteria]
    weights = {c.cid: c.weight for c in cfg.criteria}
    scores, regions = score.load_scores(os.path.join(EXAMPLE_DIR, "scores.csv"), cfg.criteria)
    assert scores, "example scores.csv should contain candidates"

    _, rank_map, ordered = score.rank_scenario(scores, weights, cids)

    # Ranks are a contiguous 1..N permutation and the order is score-descending.
    assert sorted(rank_map.values()) == list(range(1, len(scores) + 1))
    prev = None
    for _, sc in ordered:
        assert 0.0 <= sc <= 10.0
        if prev is not None:
            assert sc <= prev
        prev = sc
