import numpy as np
import pandas as pd
import pytest

from src.sequences import build_sequences, split_sessions_by_identity


def make_frame():
    rows = []
    for identity in ["p1", "p2"]:
        for session in ["s1", "s2"]:
            for t in range(6):
                rows.append({
                    "identity": identity,
                    "session": session,
                    "timestamp": t,
                    "activity": "walk" if t < 3 else "sit",
                    "f1": float(t),
                    "f2": float(t + (identity == "p2")),
                })
    return pd.DataFrame(rows)


def test_split_sessions_disjoint_and_identity_preserved():
    frame = make_frame()
    train, test = split_sessions_by_identity(frame, seed=7)
    train_groups = set(zip(frame.iloc[train].identity, frame.iloc[train].session))
    test_groups = set(zip(frame.iloc[test].identity, frame.iloc[test].session))
    assert train_groups.isdisjoint(test_groups)
    assert set(frame.iloc[train].identity) == set(frame.identity)
    assert set(frame.iloc[test].identity) == set(frame.identity)


def test_split_sessions_returns_positions_for_non_range_index():
    frame = make_frame()
    frame.index = np.arange(len(frame)) + 100
    train, test = split_sessions_by_identity(frame, seed=7)
    assert max(train.max(), test.max()) < len(frame)


def test_split_requires_two_sessions_per_identity():
    frame = make_frame()
    frame = frame[~((frame.identity == "p2") & (frame.session == "s2"))]
    with pytest.raises(ValueError, match="at least two distinct sessions"):
        split_sessions_by_identity(frame)


def test_sequences_are_ordered_and_never_cross_session():
    frame = make_frame().sample(frac=1, random_state=3).reset_index(drop=True)
    X, task, identity, session = build_sequences(frame, ["f1", "f2"], k=2)
    assert X.shape[1] == 2 * 2 + 3 * 2
    assert len(X) == len(task) == len(identity) == len(session)
    assert np.allclose(X[0][:4], [0.0, 0.0, 1.0, 1.0])


def test_mixed_task_sequence_purity_filter():
    frame = make_frame()
    X, task, identity, session = build_sequences(
        frame, ["f1", "f2"], k=4, min_task_purity=0.8
    )
    assert len(X) == 0


def test_sequence_builder_rejects_missing_session():
    frame = make_frame().drop(columns=["session"])
    with pytest.raises(ValueError, match="session"):
        build_sequences(frame, ["f1", "f2"], k=2)
