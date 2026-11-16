"""Session-aware chronological sequence construction for RF/ISAC privacy evaluation."""
from __future__ import annotations

import numpy as np
import pandas as pd


def split_sessions_by_identity(
    frame: pd.DataFrame,
    identity_col: str = "identity",
    session_col: str = "session",
    test_fraction: float = 0.25,
    seed: int = 42,
) -> tuple[np.ndarray, np.ndarray]:
    """Return positional train/test row indices with disjoint sessions per identity.

    Each identity must occur in at least two sessions. Identities are retained in
    both partitions (closed-set re-identification across sessions); sessions are
    never shared between train and test.
    """
    if not 0.0 < test_fraction < 1.0:
        raise ValueError("test_fraction must be between 0 and 1")
    missing = {identity_col, session_col} - set(frame.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    frame = frame.reset_index(drop=True)
    if frame[[identity_col, session_col]].isna().any().any():
        raise ValueError("Identity and session labels must not be missing")

    rng = np.random.default_rng(seed)
    train_positions: list[int] = []
    test_positions: list[int] = []

    for _, group in frame.groupby(identity_col, sort=True):
        sessions = pd.unique(group[session_col])
        if len(sessions) < 2:
            raise ValueError(
                "Each identity needs at least two distinct sessions for "
                "session-disjoint known-identity evaluation."
            )
        shuffled = rng.permutation(sessions)
        n_test = min(max(1, int(round(len(sessions) * test_fraction))), len(sessions) - 1)
        held_out = set(shuffled[:n_test].tolist())
        positions = group.index.to_numpy()
        session_values = group[session_col].to_numpy()
        for pos, session in zip(positions, session_values):
            (test_positions if session in held_out else train_positions).append(int(pos))

    return np.asarray(sorted(train_positions)), np.asarray(sorted(test_positions))


def build_sequences(
    frame: pd.DataFrame,
    feature_cols: list[str],
    k: int,
    identity_col: str = "identity",
    task_col: str = "activity",
    session_col: str = "session",
    timestamp_col: str = "timestamp",
    stride: int | None = None,
    min_task_purity: float = 0.8,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Create ordered, within-session sequence vectors and labels.

    Each vector concatenates K chronological feature rows and appends per-feature
    mean, standard deviation and linear trend. Sequences never cross identity or
    session boundaries. Mixed-task sequences below min_task_purity are discarded.
    Returns X_sequence, task_labels, identity_labels, session_labels.
    """
    if k < 1:
        raise ValueError("k must be >= 1")
    if not 0.0 < min_task_purity <= 1.0:
        raise ValueError("min_task_purity must be in (0, 1]")
    if not feature_cols:
        raise ValueError("feature_cols cannot be empty")
    required = {identity_col, task_col, session_col, *feature_cols}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    if frame[list(required)].isna().any().any():
        raise ValueError("Labels and selected features must not contain missing values")

    step = k if stride is None else stride
    if step < 1:
        raise ValueError("stride must be >= 1")

    xs: list[np.ndarray] = []
    tasks: list[object] = []
    identities: list[object] = []
    sessions: list[object] = []
    ordered = frame.copy()

    for (identity, session), group in ordered.groupby([identity_col, session_col], sort=True):
        if timestamp_col in group.columns:
            group = group.sort_values(timestamp_col, kind="mergesort")
        values = group[feature_cols].to_numpy(dtype=float)
        task_values = group[task_col].to_numpy()
        for start in range(0, len(group) - k + 1, step):
            stop = start + k
            labels, counts = np.unique(task_values[start:stop], return_counts=True)
            best = int(np.argmax(counts))
            purity = float(counts[best] / k)
            if purity < min_task_purity:
                continue
            window = values[start:stop]
            mean = window.mean(axis=0)
            std = window.std(axis=0)
            if k == 1:
                trend = np.zeros(window.shape[1], dtype=float)
            else:
                time_axis = np.arange(k, dtype=float)
                time_axis -= time_axis.mean()
                denom = float(np.dot(time_axis, time_axis))
                centered = window - mean
                trend = (time_axis[:, None] * centered).sum(axis=0) / denom
            xs.append(np.concatenate([window.reshape(-1), mean, std, trend]))
            tasks.append(labels[best])
            identities.append(identity)
            sessions.append(session)

    width = k * len(feature_cols) + 3 * len(feature_cols)
    if not xs:
        return (
            np.empty((0, width), dtype=float),
            np.asarray([]),
            np.asarray([]),
            np.asarray([]),
        )
    return np.vstack(xs), np.asarray(tasks), np.asarray(identities), np.asarray(sessions)
