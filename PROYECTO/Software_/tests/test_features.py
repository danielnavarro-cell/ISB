"""Pruebas de extract_beat_features: forma de la salida, bordes y casos raros."""
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from features import (FEATURE_COLUMNS, N_WINDOW, extract_beat_features)  # noqa: E402

FS = 360


def synthetic_ecg(r_peaks, n, qrs_sigma_s=0.012, amp=1.0):
    """Tren de 'QRS' gaussianos centrados en r_peaks."""
    t = np.arange(n)
    x = np.zeros(n)
    s = qrs_sigma_s * FS
    for r in r_peaks:
        x += amp * np.exp(-0.5 * ((t - r) / s) ** 2)
    return x


@pytest.fixture
def regular():
    r = np.arange(200, 360 * 20, 288)  # RR = 0.8 s
    return synthetic_ecg(r, 360 * 21), r


def test_output_shape_and_columns(regular):
    x, r = regular
    df = extract_beat_features(x, r, FS)
    assert df.shape == (len(r), len(FEATURE_COLUMNS))
    assert list(df.columns) == FEATURE_COLUMNS
    assert sum(c.startswith("w_") for c in df.columns) == N_WINDOW


def test_no_nan_and_edges_flagged(regular):
    x, r = regular
    df = extract_beat_features(x, r, FS)
    assert not df.isna().any().any()
    assert df["borde"].tolist() == [1] + [0] * (len(r) - 2) + [1]


def test_rr_values(regular):
    x, r = regular
    df = extract_beat_features(x, r, FS)
    assert np.allclose(df["rr_prev"], 0.8)
    assert np.allclose(df["rr_next"], 0.8)
    assert np.allclose(df["rr_local"], 0.8)
    assert np.allclose(df["rr_prev_ratio"], 1.0)


def test_premature_beat_ratio():
    r = np.array([200, 488, 776, 950, 1352, 1640, 1928])  # el 4.º llega antes
    x = synthetic_ecg(r, 2300)
    df = extract_beat_features(x, r, FS)
    assert df.loc[3, "rr_prev_ratio"] < 0.8 < df.loc[3, "rr_next_ratio"]


def test_r_amp(regular):
    x, r = regular
    df = extract_beat_features(2.5 * x, r, FS)
    assert np.allclose(df["r_amp"], 2.5, atol=1e-6)


def test_qrs_width_wider_for_wide_complex():
    r = np.array([400, 700])
    narrow = extract_beat_features(synthetic_ecg(r, 1100, 0.010), r, FS)["qrs_width"]
    wide = extract_beat_features(synthetic_ecg(r, 1100, 0.030), r, FS)["qrs_width"]
    assert (wide > narrow).all()
    assert ((narrow >= 0.04) & (wide <= 0.20)).all()


def test_window_at_signal_edges():
    r = np.array([5, 500, 995])  # ventanas que se salen por ambos lados
    df = extract_beat_features(synthetic_ecg(r, 1000), r, FS)
    assert df.shape == (3, len(FEATURE_COLUMNS))
    assert not df.isna().any().any()


def test_close_peaks_flagged():
    r = np.array([300, 588, 620, 900])  # 588 y 620 a 89 ms
    df = extract_beat_features(synthetic_ecg(r, 1300), r, FS)
    assert df["rr_corto"].tolist() == [0, 1, 1, 0]


def test_nan_in_signal_is_handled(regular):
    x, r = regular
    x = x.copy()
    x[r[3] + 50: r[3] + 60] = np.nan
    df = extract_beat_features(x, r, FS)
    assert not df.isna().any().any()


def test_empty_and_single_beat():
    assert extract_beat_features(np.zeros(1000), [], FS).shape == (0, len(FEATURE_COLUMNS))
    one = extract_beat_features(synthetic_ecg([500], 1000), [500], FS)
    assert one.shape == (1, len(FEATURE_COLUMNS))
    assert one["rr_prev"].isna().all()  # sin vecinos no hay RR


def test_unsorted_or_out_of_range_raise():
    with pytest.raises(ValueError):
        extract_beat_features(np.zeros(1000), [500, 300], FS)
    with pytest.raises(ValueError):
        extract_beat_features(np.zeros(1000), [500, 1000], FS)
