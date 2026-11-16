from pathlib import Path

import pandas as pd

from experiments.qualify_csi_bench import choose_join_key, parse_recording_path, summarize_metadata


def test_parse_recording_path_extracts_explicit_tokens():
    parsed = parse_recording_path(
        "Multitask/sub_Human_h5/user_U07/act_walk/env_E02/device_routerA/session_20250101T120000__freq5.h5"
    )
    assert parsed == {
        "identity": "user_U07",
        "activity": "act_walk",
        "environment": "env_E02",
        "device": "device_routerA",
        "session": "session_20250101T120000__freq5.h5",
    }


def test_parse_recording_path_does_not_invent_missing_session():
    parsed = parse_recording_path("user_U01/act_walk/env_E01/device_A/sample.h5")
    assert parsed["identity"] == "user_U01"
    assert parsed["session"] is None


def test_choose_join_key_prefers_sample_id():
    left = pd.DataFrame({"sample_id": ["a"], "file_path": ["x"]})
    right = pd.DataFrame({"sample_id": ["a"], "file_path": ["x"]})
    assert choose_join_key(left, right) == "sample_id"


def test_summarize_metadata_counts_session_groups(tmp_path: Path):
    metadata = pd.DataFrame({
        "label": ["u1", "u1", "u2"],
        "file_path": [
            "user_U01/act_walk/env_E01/device_A/session_1.h5",
            "user_U01/act_walk/env_E01/device_A/session_2.h5",
            "user_U02/act_walk/env_E01/device_A/session_1.h5",
        ],
    })
    path = tmp_path / "sample_metadata.csv"
    metadata.to_csv(path, index=False)
    result = summarize_metadata(path)
    assert result["rows"] == 3
    assert result["path_users_with_multiple_sessions"] == 1
    assert result["path_user_session_pairs"] == 3
